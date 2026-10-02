#!/usr/bin/env python3
"""Offline CPC reference adapter. Validates records; never executes project actions.

This is a cooperative single-writer local-file utility, NOT a permission system,
scientific validator, scheduler, model client, distributed lock or task engine.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ImportError as exc:
    raise SystemExit("Optional tools require jsonschema>=4.23,<5. Install the bundled requirements.txt.") from exc

ASSETS = Path(__file__).resolve().parents[1] / "assets"
MAX_RECORD_BYTES = 8 * 1024 * 1024
MAX_ARTIFACT_BYTES = 128 * 1024 * 1024
SAFE_CLASSES = frozenset({"inspect", "local_edit", "local_compute"})
PROTECTED_CLASSES = frozenset({"objective_change", "publish", "external_write", "delete_data",
                               "physical_actuation", "accept_risk", "permissions_change"})
ACTIVE_MODES = frozenset({"observe", "act"})


class CPCError(ValueError):
    """A malformed record, conflict or unsupported operation."""


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CPCError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise CPCError(f"Non-finite JSON number is not allowed: {value}")


def load_json(path: Path) -> dict[str, Any]:
    """Load bounded UTF-8 JSON without duplicate keys or non-finite values."""
    if path.is_symlink():
        raise CPCError(f"Refusing symlink record: {path}")
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_RECORD_BYTES + 1)
        if len(raw) > MAX_RECORD_BYTES:
            raise CPCError(f"JSON exceeds {MAX_RECORD_BYTES} bytes")
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicates,
                            parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise CPCError(f"Cannot load JSON {path}: {exc}") from exc
    if not isinstance(result, dict):
        raise CPCError("Top-level JSON value must be an object")
    return result


def canonical_bytes(value: dict[str, Any]) -> bytes:
    try:
        return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    except (ValueError, TypeError, RecursionError) as exc:
        raise CPCError(f"Cannot serialize JSON: {exc}") from exc


def digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def timestamp(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise CPCError(f"Invalid timestamp: {value!r}") from exc
    if dt.tzinfo is None:
        raise CPCError("Timestamps must include a UTC offset")
    return dt.astimezone(timezone.utc)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def schema_validate(record: dict[str, Any], kind: str) -> None:
    schemas = [load_json(ASSETS / f"{k}.schema.json") for k in ("state", "turn")]
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas)
    schema = schemas[0 if kind == "state" else 1]
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(record), key=lambda e: str(list(e.absolute_path)))
    if errors:
        details = "; ".join(f"{'/'.join(map(str,e.absolute_path)) or '<root>'}: {e.message}"
                            for e in errors[:8])
        raise CPCError(f"{kind} schema error: {details}")


def safe_relative(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    """Reject traversal and symlinks, even symlinks targeting inside the root.

    A cooperative filesystem is assumed. This does not defeat an adversarial
    local process racing directory entries between verification and use.
    """
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise CPCError(f"Invalid relative path: {relative!r}")
    p = PurePosixPath(relative)
    if p.is_absolute() or any(part in (".", "..", "") for part in relative.split("/")):
        raise CPCError(f"Unsafe relative path: {relative}")
    if ":" in p.parts[0]:
        raise CPCError(f"Drive or URI path is not a local artifact: {relative}")
    root = root.resolve()
    candidate = root
    for part in p.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise CPCError(f"Symlink is not accepted: {relative}")
    if not candidate.resolve().is_relative_to(root):
        raise CPCError(f"Path escapes project: {relative}")
    if must_exist and not candidate.is_file():
        raise CPCError(f"Artifact is missing or not a file: {relative}")
    return candidate


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    count = 0
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                count += len(chunk)
                if count > MAX_ARTIFACT_BYTES:
                    raise CPCError(f"Artifact exceeds {MAX_ARTIFACT_BYTES} bytes: {path}")
                h.update(chunk)
    except OSError as exc:
        raise CPCError(f"Cannot read artifact {path}: {exc}") from exc
    return h.hexdigest()


def _index(items: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if item["id"] in result:
            raise CPCError(f"Duplicate {label} id: {item['id']}")
        result[item["id"]] = item
    return result


def _require_refs(refs: list[str], known: dict[str, Any] | set[str], label: str) -> None:
    missing = [x for x in refs if x not in known]
    if missing:
        raise CPCError(f"Unknown {label} references: {missing}")


def _check_receipt(root: Path, entry: dict[str, Any], project_id: str) -> None:
    """Verify the accepted receipt against its summary; labels are not signatures."""
    expected_path = f".project-control/receipts/{entry['id']}.json"
    if entry["receipt_path"] != expected_path:
        raise CPCError("Noncanonical receipt path")
    receipt = load_json(safe_relative(root, expected_path, must_exist=True))
    schema_validate(receipt, "turn")
    expected = {"id": entry["id"], "project_id": project_id,
                "base_revision": entry["base_revision"], "mode": entry["mode"],
                "actor": entry["actor"], "created_at": entry["at"]}
    if digest(receipt) != entry["sha256"] or any(receipt[k] != v for k, v in expected.items()):
        raise CPCError("Receipt identity, metadata or digest mismatch")
    if receipt["result"]["summary"] != entry["summary"]:
        raise CPCError("Receipt summary mismatch")


def validate_state(state: dict[str, Any], root: Path | None = None,
                   *, verify_artifacts: bool = False) -> list[str]:
    schema_validate(state, "state")
    criteria = _index(state["criteria"], "criterion")
    questions = _index(state["questions"], "question")
    evidence = _index(state["evidence"], "evidence")
    decisions = _index(state["decisions"], "decision")
    _index(state["pending_effects"], "pending effect")
    _index(state["history"], "turn")
    targets = set(criteria) | set(questions)
    as_of = timestamp(state["as_of"])
    warnings: list[str] = []
    if verify_artifacts and root is None:
        raise CPCError("Artifact verification requires a project root")
    root = (root or Path.cwd()).resolve()
    for e in evidence.values():
        _require_refs(e["targets"], targets, "evidence target")
        _require_refs(e["depends_on"], evidence, "evidence dependency")
        if timestamp(e["observed_at"]) > as_of:
            raise CPCError(f"Evidence observed after state as_of: {e['id']}")
        if e["validity"] == "current" and e["objective_version"] != state["objective"]["version"]:
            raise CPCError(f"Current evidence has stale objective version: {e['id']}")
        if e["validity"] != "current" and not e["validity_reason"]:
            raise CPCError(f"Invalidated evidence needs a reason: {e['id']}")
        if e["review_status"] == "reviewed" and not e["reviewer"]:
            raise CPCError(f"Reviewed evidence needs a reviewer label: {e['id']}")
        if e["validity"] == "current" and any(evidence[d]["validity"] != "current" for d in e["depends_on"]):
            raise CPCError(f"Current evidence depends on invalidated evidence: {e['id']}")
        for a in e["artifacts"]:
            path = safe_relative(root, a["path"])
            if verify_artifacts and e["validity"] == "current" and e["review_status"] == "reviewed":
                safe_relative(root, a["path"], must_exist=True)
                if hash_file(path) != a["sha256"]:
                    raise CPCError(f"Artifact hash mismatch: {a['path']}")
        if e["review_status"] == "unreviewed":
            warnings.append(f"Unreviewed evidence cannot establish a resolved claim: {e['id']}")
    active: set[str] = set()
    finished: set[str] = set()
    def visit(key: str) -> None:
        if key in active:
            raise CPCError(f"Evidence dependency cycle at {key}")
        if key in finished:
            return
        active.add(key)
        for dep in evidence[key]["depends_on"]:
            visit(dep)
        active.remove(key)
        finished.add(key)
    try:
        for key in evidence:
            visit(key)
    except RecursionError as exc:
        raise CPCError("Evidence graph too deep for this reference adapter") from exc

    def reviewed_refs(item: dict[str, Any]) -> None:
        if not item["evidence_ids"]:
            raise CPCError(f"Resolved status needs evidence: {item['id']}")
        for key in item["evidence_ids"]:
            e = evidence[key]
            if e["validity"] != "current" or e["review_status"] != "reviewed":
                raise CPCError(f"Resolved status cites stale/unreviewed evidence: {item['id']} -> {key}")
            if item["id"] not in e["targets"]:
                raise CPCError(f"Evidence does not target claim: {item['id']} -> {key}")
    for c in criteria.values():
        _require_refs(c["evidence_ids"], evidence, "criterion evidence")
        if c["status"] != "unknown":
            reviewed_refs(c)
            expected = "supports" if c["status"] == "supported" else "contradicts"
            if not any(evidence[x]["relation"] == expected for x in c["evidence_ids"]):
                raise CPCError(f"Evidence relation does not justify {c['status']}: {c['id']}")
            contrary = "contradicts" if expected == "supports" else "supports"
            if any(c["id"] in e["targets"] and e["validity"] == "current"
                   and e["review_status"] == "reviewed" and e["relation"] == contrary
                   for e in evidence.values()):
                raise CPCError(f"Unresolved contrary evidence; retain unknown or adjudicate scope: {c['id']}")
    for q in questions.values():
        _require_refs(q["blocks"], criteria, "blocked criterion")
        _require_refs(q["evidence_ids"], evidence, "question evidence")
        if q["status"] == "resolved":
            reviewed_refs(q)
            if not any(evidence[x]["relation"] != "inconclusive" for x in q["evidence_ids"]):
                raise CPCError(f"Inconclusive evidence alone cannot resolve {q['id']}")
    preceding_decisions: set[str] = set()
    for d in decisions.values():
        _require_refs(d["evidence_ids"], evidence, "decision evidence")
        if d["supersedes"] is not None and d["supersedes"] not in preceding_decisions:
            raise CPCError(f"A decision can supersede only an earlier decision: {d['id']}")
        preceding_decisions.add(d["id"])
    for p in state["pending_effects"]:
        if timestamp(p["expected_at"]) > timestamp(p["timeout_at"]):
            raise CPCError(f"Feedback timeout precedes expected time: {p['id']}")
    if state["revision"] != len(state["history"]):
        raise CPCError("Reference adapter requires revision == number of accepted receipts")
    previous_at: datetime | None = None
    for i, h in enumerate(state["history"]):
        if h["base_revision"] != i or h["new_revision"] != i+1:
            raise CPCError("History revision chain is broken")
        at = timestamp(h["at"])
        if at > as_of or (previous_at is not None and at < previous_at):
            raise CPCError("History timestamps must be monotonic and not exceed as_of")
        previous_at = at
        safe_relative(root, h["receipt_path"])
        if h["receipt_path"] != f".project-control/receipts/{h['id']}.json":
            raise CPCError("Noncanonical receipt path")
        if verify_artifacts:
            _check_receipt(root, h, state["project_id"])
    used = sum(h["mode"] in ACTIVE_MODES for h in state["history"])
    if state["control"]["actions_used"] != used:
        raise CPCError("actions_used does not match accepted active turns")
    if used > state["control"]["max_actions"]:
        raise CPCError("Recorded actions exceed the approved reference budget")
    return warnings


def _invalidate(state: dict[str, Any], changes: list[dict[str, str]]) -> None:
    ev = _index(state["evidence"], "evidence")
    for change in changes:
        if change["id"] not in ev:
            raise CPCError(f"Cannot invalidate unknown evidence: {change['id']}")
        e = ev[change["id"]]
        if e["validity"] == "retracted":
            raise CPCError(f"Evidence already retracted: {e['id']}")
        e["validity"] = "retracted"
        e["validity_reason"] = change["reason"]
    changed = True
    while changed:
        changed = False
        for e in ev.values():
            bad = [d for d in e["depends_on"] if ev[d]["validity"] != "current"]
            if bad and e["validity"] == "current":
                e["validity"] = "stale"
                e["validity_reason"] = "Invalid upstream evidence: " + ", ".join(bad)
                changed = True
    for c in state["criteria"]:
        if any(ev[x]["validity"] != "current" for x in c["evidence_ids"]):
            c["status"] = "unknown"
    for q in state["questions"]:
        if any(ev[x]["validity"] != "current" for x in q["evidence_ids"]):
            q["status"] = "open"


def transition(state: dict[str, Any], turn: dict[str, Any], root: Path,
               *, verify_artifacts: bool = False) -> dict[str, Any]:
    """Pure proposal validation and merge; does not write or execute work."""
    validate_state(state, root, verify_artifacts=False)
    schema_validate(turn, "turn")
    if turn["project_id"] != state["project_id"]:
        raise CPCError("Wrong project_id")
    if turn["base_revision"] != state["revision"]:
        raise CPCError("Stale base_revision; re-read and reconcile before proposing again")
    if turn["objective_version"] != state["objective"]["version"]:
        raise CPCError("Objective version changed")
    if turn["actor"] != state["control"]["controller_id"]:
        raise CPCError("Only the designated controller label can accept a turn (not authentication)")
    if turn["id"] in {h["id"] for h in state["history"]}:
        raise CPCError("Turn id already accepted")
    if timestamp(turn["created_at"]) < timestamp(state["as_of"]):
        raise CPCError("Turn predates the current state")
    mode, cls = turn["mode"], turn["action_class"]
    if mode == "observe" and cls != "inspect":
        raise CPCError("observe mode requires inspect action_class")
    if mode == "act" and cls not in {"local_edit", "local_compute"}:
        raise CPCError("Reference adapter cannot accept protected or nonlocal execution")
    if mode in {"wait", "stop"} and cls != "none":
        raise CPCError("wait/stop cannot carry an execution action_class")
    if mode == "escalate" and cls not in PROTECTED_CLASSES | {"none"}:
        raise CPCError("escalate records a gate request, not an executed local action")
    if mode in ACTIVE_MODES:
        if cls not in state["control"]["allowed_action_classes"]:
            raise CPCError("Action class is outside the recorded scope")
        if state["control"]["actions_used"] >= state["control"]["max_actions"]:
            raise CPCError("Action budget exhausted; stop or escalate")
        if turn["result"]["status"] == "not_run":
            raise CPCError("Unexecuted plan cannot be accepted as an active turn")
    elif turn["result"]["status"] != "not_run":
        raise CPCError("wait/escalate/stop record no newly executed action")
    if mode == "act" and state["control"]["mode"] != "bounded":
        raise CPCError("Advisory mode does not authorize local changes/computation")
    if mode not in ACTIVE_MODES and any(turn[k] for k in ("add_evidence", "invalidate_evidence", "criterion_updates", "question_updates", "pending_updates")):
        raise CPCError("Non-active turn cannot silently perform evidence/state work; use observe")
    for k in ("add_evidence", "invalidate_evidence", "criterion_updates", "question_updates", "pending_updates", "add_decisions"):
        _index(turn[k], k)
    candidate = copy.deepcopy(state)
    for kind, key in (("evidence", "add_evidence"), ("decisions", "add_decisions")):
        known = {e["id"] for e in candidate[kind]}
        if any(e["id"] in known for e in turn[key]):
            raise CPCError(f"Cannot replace existing {kind}; append a new id instead")
        candidate[kind].extend(copy.deepcopy(turn[key]))
    all_evidence = _index(candidate["evidence"], "evidence")
    _require_refs(turn["diagnosis"]["evidence_ids"], all_evidence, "diagnosis evidence")
    _require_refs(turn["result"]["evidence_ids"], all_evidence, "result evidence")
    _require_refs(turn["target_questions"], _index(state["questions"], "question"), "target question")
    for e in all_evidence.values():
        _require_refs(e["depends_on"], all_evidence, "evidence dependency")
    _invalidate(candidate, turn["invalidate_evidence"])
    if turn["result"]["status"] == "checked":
        refs = turn["result"]["evidence_ids"]
        if not refs or any(all_evidence[x]["review_status"] != "reviewed"
                           or all_evidence[x]["validity"] != "current" for x in refs):
            raise CPCError("Checked result requires current reviewed evidence for every result reference")
    for kind, key in (("criteria", "criterion_updates"), ("questions", "question_updates")):
        index = _index(candidate[kind], kind)
        for update in turn[key]:
            if update["id"] not in index:
                raise CPCError(f"Cannot update unknown {kind}: {update['id']}")
            index[update["id"]].update(copy.deepcopy(update))
    pending = _index(candidate["pending_effects"], "pending effect")
    for p in turn["pending_updates"]:
        if p["id"] in pending:
            old = pending[p["id"]]
            if p["task_ref"] != old["task_ref"]:
                raise CPCError("Cannot reuse a pending id for a different remote task")
            if old["status"] != "waiting" and p["status"] == "waiting":
                raise CPCError("Cannot reopen a finished pending effect under the same id")
            old.update(copy.deepcopy(p))
        else:
            candidate["pending_effects"].append(copy.deepcopy(p))
    candidate["revision"] += 1
    candidate["as_of"] = turn["created_at"]
    candidate["control"]["actions_used"] += int(mode in ACTIVE_MODES)
    candidate["handoff"] = copy.deepcopy(turn["handoff"])
    candidate["history"].append({"id":turn["id"],"base_revision":state["revision"],
        "new_revision":candidate["revision"],"mode":mode,"actor":turn["actor"],
        "at":turn["created_at"],"receipt_path":f".project-control/receipts/{turn['id']}.json",
        "sha256":digest(turn),"summary":turn["result"]["summary"]})
    validate_state(candidate, root, verify_artifacts=False)
    if verify_artifacts:
        for e in candidate["evidence"]:
            if e["validity"] == "current" and e["review_status"] == "reviewed":
                for a in e["artifacts"]:
                    path = safe_relative(root, a["path"], must_exist=True)
                    if hash_file(path) != a["sha256"]:
                        raise CPCError(f"Artifact hash mismatch: {a['path']}")
        for h in state["history"]:
            _check_receipt(root, h, state["project_id"])
    return candidate


def _fsync_dir(path: Path) -> None:
    if os.name != "posix":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(path: Path, payload: bytes) -> None:
    """Atomic replace in the same directory. Caller must hold the project lock."""
    if path.is_symlink():
        raise CPCError("Refusing to overwrite a symlink")
    if len(payload) > MAX_RECORD_BYTES:
        raise CPCError("State exceeds the reference adapter limit; migrate, do not truncate")
    fd, temp = tempfile.mkstemp(prefix=".cpc-tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        _fsync_dir(path.parent)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


@contextmanager
def project_lock(root: Path) -> Iterator[None]:
    lock = safe_relative(root,".project-control/.write.lock")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise CPCError("Project is locked. Do not auto-steal the lock; verify whether a writer is active.") from exc
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as stream:
            stream.write(json.dumps({"pid":os.getpid(),"created_at":utc_now()}))
            stream.flush();os.fsync(stream.fileno())
        yield
    finally:
        lock.unlink(missing_ok=True)


def read_project(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise CPCError("Project directory does not exist")
    return load_json(safe_relative(root,".project-control/state.json",must_exist=True))


def init_project(root: Path, project_id: str, objective: str, criterion: str,
                 controller: str, *, now: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise CPCError("Create the intended project directory first")
    for marker in (".project-control", ".loopx", ".apm", ".project", "PROJECT_STATE.md", "PROJECT_STATUS.md", "_knowledge"):
        path = root / marker
        if path.exists() or path.is_symlink():
            raise CPCError(f"Existing state marker {marker}; reuse/reconcile instead of creating a second state")
    state = load_json(ASSETS/"state.template.json")
    state.update(project_id=project_id,as_of=now or utc_now())
    state["objective"]["statement"] = objective
    state["criteria"][0]["description"] = criterion
    state["control"]["controller_id"] = controller
    state["handoff"]={"summary":"Initialized from user-provided goal; project evidence has not been inspected.",
        "next_action":"Read current materials and propose a bounded action in advisory mode.",
        "open_risks":["No initial evidence has been checked."],"do_not_repeat":[]}
    validate_state(state,root)
    directory = root/".project-control"
    try:
        directory.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise CPCError("Another initializer created project state; inspect before retrying") from exc
    (directory/"receipts").mkdir(mode=0o700)
    atomic_write(directory/"state.json",canonical_bytes(state))
    return state


def apply_turn(root: Path, turn: dict[str, Any], expected_revision: int) -> dict[str, Any]:
    """Commit a validated record, not the project action it describes."""
    root=root.resolve()
    schema_validate(turn,"turn")
    with project_lock(root):
        state=read_project(root)
        validate_state(state,root,verify_artifacts=False)
        prior=next((h for h in state["history"] if h["id"] == turn["id"]),None)
        if prior:
            if prior["sha256"] != digest(turn):
                raise CPCError("Idempotency conflict: same turn id, different content")
            _check_receipt(root, prior, state["project_id"])
            return {"status":"already_applied","revision":state["revision"],"turn_id":turn["id"]}
        if expected_revision != state["revision"]:
            raise CPCError(f"Revision conflict: expected {expected_revision}, actual {state['revision']}")
        candidate=transition(state,turn,root,verify_artifacts=True)
        receipt_path=safe_relative(root,f".project-control/receipts/{turn['id']}.json")
        if not receipt_path.parent.is_dir():
            raise CPCError("Missing receipts directory; inspect reference state integrity")
        if receipt_path.exists():
            if digest(load_json(receipt_path)) != digest(turn):
                raise CPCError("Conflicting orphan receipt; inspect before retrying")
        else:
            atomic_write(receipt_path,canonical_bytes(turn))
        atomic_write(safe_relative(root,".project-control/state.json"),canonical_bytes(candidate))
        return {"status":"applied","revision":candidate["revision"],"turn_id":turn["id"],
                "limits":"Record consistency and bytes checked; no action executed or scientific claim certified."}


def snapshot(state: dict[str,Any]) -> dict[str,Any]:
    return {"project_id":state["project_id"],"revision":state["revision"],"as_of":state["as_of"],
        "objective":state["objective"],"criteria":state["criteria"],"open_questions":[q for q in state["questions"] if q["status"] == "open"],
        "waiting_effects":[p for p in state["pending_effects"] if p["status"] == "waiting"],
        "control":state["control"],"recent_decisions":state["decisions"][-3:],"handoff":state["handoff"],
        "limits":"Recorded snapshot only; actual workspace and relevant evidence must still be inspected."}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    init=sub.add_parser("init",help="Initialize optional advisory file state, never overwrite existing state")
    init.add_argument("project",type=Path)
    for flag in ("project-id","objective","criterion","controller"):
        init.add_argument("--"+flag,required=True)
    for name in ("validate","snapshot"):
        p=sub.add_parser(name)
        p.add_argument("project",type=Path)
        p.add_argument("--verify-artifacts",action="store_true")
    check=sub.add_parser("check-turn",help="Validate a proposed record, no writes")
    check.add_argument("project",type=Path);check.add_argument("turn",type=Path)
    check.add_argument("--verify-artifacts",action="store_true")
    apply=sub.add_parser("apply",help="Record a turn; DOES NOT execute its described action")
    apply.add_argument("project",type=Path);apply.add_argument("turn",type=Path)
    apply.add_argument("--expect-revision",type=int,required=True)
    args=parser.parse_args(argv)
    try:
        if args.command == "init":
            state=init_project(args.project,args.project_id,args.objective,args.criterion,args.controller)
            output={"status":"initialized","project_id":state["project_id"],"mode":"advisory"}
        elif args.command in {"validate","snapshot"}:
            state=read_project(args.project)
            warnings=validate_state(state,args.project,verify_artifacts=args.verify_artifacts)
            output=snapshot(state) if args.command == "snapshot" else {"status":"record_valid","warnings":warnings,"artifact_check":args.verify_artifacts,"scientific_validity":"not_assessed"}
        elif args.command == "check-turn":
            turn=load_json(args.turn)
            candidate=transition(read_project(args.project),turn,args.project,verify_artifacts=args.verify_artifacts)
            output={"status":"proposal_valid","proposed_revision":candidate["revision"],"writes_performed":False,"scientific_validity":"not_assessed"}
        else:
            output=apply_turn(args.project,load_json(args.turn),args.expect_revision)
        print(json.dumps(output,ensure_ascii=False,indent=2,allow_nan=False))
        return 0
    except (CPCError,OSError) as exc:
        print(json.dumps({"status":"error","error":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
