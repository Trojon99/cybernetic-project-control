# Quick Start

This guide gets CPC into a project without creating a second source of truth.

## 1. Read before writing

Ask the agent to inspect the target project in **read-only mode** first. It should identify:

- the human-approved objective and acceptance conditions;
- the authoritative project-state source, if one already exists;
- recent evidence and artifacts;
- unresolved questions, risks and delayed feedback;
- the next decision that actually blocks progress.

Do not initialize CPC state merely because a `.project-control/` directory is absent. If the project already uses LoopX, Project State Governor, GitHub Issues, Notion, a lab notebook, or another authoritative backend, map to that system instead of duplicating it.

## 2. Load the skill

Copy the whole package:

```text
skills/cybernetic-project-control/
```

A generic prompt:

> Read `skills/cybernetic-project-control/SKILL.md`. Inspect this project in read-only mode. Reuse existing state. Return a five-part control card: verified facts, critical gap, next action with one rejected alternative, expected feedback and branches, and human/authorization boundaries.

## 3. Review the control card

The minimum control card is:

1. **Verified current facts** — what was actually checked; what is stale/unknown.
2. **Critical gap** — the unmet condition or risk that most blocks the agreed objective.
3. **Next action and rationale** — one bounded action and why at least one meaningful alternative is lower priority.
4. **Feedback and branches** — expected signal, maturity time, acceptance check and what different results imply.
5. **Boundaries and resume point** — budget, protected actions, human decisions and where to resume after a pause.

## 4. Authorize bounded execution

Approve a scope and resource budget, for example:

> You may modify files under `analysis/`, run local tests and create draft outputs for the next two hours. Do not change the research question, acceptance criteria, raw data, public branches or external systems. Stop and ask me if the evidence implies a strategic direction change.

CPC is designed to reduce micro-management, not remove human authority.

## 5. Evaluate real feedback

After execution, the agent should read the actual logs, tables, figures, tests or source documents. It should separate:

```text
execution completed
→ artifact exists
→ artifact passed a check
→ evidence supports a claim
→ project state changes
→ next action changes
```

Each arrow is a separate inference.

## 6. Pause and resume

Before a long pause, store the verified current state, pending feedback, important negative evidence, uncommitted changes, open risks and the next safe action in the project's existing authoritative state system.

When resuming — with the same agent or a different one — re-read that state and verify it against the current repository before continuing.

## Optional offline checks

```bash
python -m pip install -r requirements-dev.txt
python tools/check_repository.py
python tools/demo.py
```

The validators check recorded structure and some consistency properties. They do not prove scientific truth or project-management effectiveness.
