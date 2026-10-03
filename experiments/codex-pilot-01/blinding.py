"""Structural leakage detection. Lexical occurrence != answer leakage."""
from __future__ import annotations
import hashlib
import json
import re
import stat
from pathlib import Path

ANSWER_KEYS = {'oracle', 'acceptable_actions', 'forbidden_actions', 'human_review_note'}
CORE_FILES = {'TASK.md','input.json','response.schema.json','subject-prompt.md'}
# Exact visible routing instruction; does not name an experimental condition.
CPC_INSTRUCTIONS = b'Read and use skills/cybernetic-project-control/SKILL.md. Load its references progressively as needed.\n'
SKILL_PREFIX = 'skills/cybernetic-project-control/'
PATH_PATTERN = re.compile(
    r'(?:evals\s*/\s*(?:cases(?:/|\b)|run\.py\b)|'
    r'(?<![\w-])(?:coordinator|subject-exports|bundles|results)\s*/|'
    r'(?<![\w.-])(?:manifest\.json|score\.py|scoring\.py)\b|'
    r'(?<![\w.-])\.git(?:/|\b)|(?<![\w-])run-\d{3}(?:/|\b))', re.I)
SERIALIZED_KEY = re.compile(r'''["'](?:oracle|acceptable_actions|forbidden_actions|human_review_note)["']\s*:''', re.I)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory(directory):
    """Inspect every entry, including empty/unexpected directories; no links or devices."""
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('Bundle root must be a real directory')
    hashes = {}; directories = set()
    for f in sorted(directory.rglob('*')):
        mode = f.lstat().st_mode
        name = f.relative_to(directory).as_posix()
        if stat.S_ISDIR(mode):
            directories.add(name)
        elif stat.S_ISREG(mode):
            if f.stat().st_size > 1024*1024:
                raise ValueError(f'File exceeds 1 MiB: {name}')
            hashes[name] = sha(f.read_bytes())
        else:
            raise ValueError(f'Non-regular entry rejected: {name}')
    return hashes, directories


def expected_directories(names):
    result = set()
    for name in names:
        result.update(p.as_posix() for p in Path(name).parents if p.as_posix() != '.')
    return result


def allowed_files(condition, skill_hashes):
    allowed = set(CORE_FILES)
    if condition in ('B-memory','C-generic-pm','D-cpc'):
        allowed.add('condition/INSTRUCTIONS.md')
    if condition == 'D-cpc':
        allowed.update(SKILL_PREFIX+k for k in skill_hashes)
    if condition not in ('A-control','B-memory','C-generic-pm','D-cpc'):
        raise ValueError('Unknown coordinator condition')
    return allowed


def answer_keys(value):
    found = set()
    if isinstance(value, dict):
        for k,v in value.items():
            if k.lower() in ANSWER_KEYS:
                found.add(k)
            found.update(answer_keys(v))
    elif isinstance(value, list):
        for v in value:
            found.update(answer_keys(v))
    return found


def content_errors(name, text, source_root=None):
    """Parse JSON recursively; detect explicit serialized structures in prose/code."""
    errors = []
    def unique(pairs):
        out = {}
        for k,v in pairs:
            if k in out:
                raise ValueError('Duplicate JSON key')
            out[k] = v
        return out
    if name.endswith('.json'):
        try:
            data = json.loads(text, object_pairs_hook=unique,
                parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
            errors.extend('answer-bearing JSON key: '+k for k in sorted(answer_keys(data)))
        except (ValueError, RecursionError) as exc:
            errors.append('Invalid JSON: '+str(exc))
    else:
        # Includes fenced JSON and Python-style literal answer dictionaries.
        if SERIALIZED_KEY.search(text):
            errors.append('Explicit serialized answer structure')
        # Also catch escaped keys in embedded JSON, not only their literal spellings.
        decoder = json.JSONDecoder(object_pairs_hook=unique)
        for match in re.finditer(r'[\[{]', text):
            try:
                value,_ = decoder.raw_decode(text, match.start())
                if answer_keys(value):
                    errors.append('Embedded answer-bearing JSON structure')
                    break
            except (ValueError, RecursionError):
                continue
    normalized = text.replace('\\/', '/').replace('\\', '/')
    if PATH_PATTERN.search(normalized) or PATH_PATTERN.search(name):
        errors.append('Evaluator-only path/source')
    if source_root and str(source_root) in text:
        errors.append('Coordinator source path exposed')
    if 'github.com/Trojon99/cybernetic-project-control' in text:
        errors.append('Coordinator repository URL exposed')
    if any(c.lower() in text.lower() or c.lower() in name.lower()
           for c in ('A-control','B-memory','C-generic-pm','D-cpc')):
        errors.append('Condition label exposed')
    return errors


def validate_bundle(directory, run, skill_hashes, source_root=None):
    """Same validator for original bundles and re-extracted archives."""
    errors = []
    try:
        actual, dirs = inventory(directory)
    except (OSError, ValueError) as exc:
        return {'passed':False,'errors':[str(exc)]}
    allowed = allowed_files(run['condition'], skill_hashes)
    if set(actual) != allowed:
        errors.append('File allowlist mismatch: missing='+str(sorted(allowed-set(actual)))+
                      '; unexpected='+str(sorted(set(actual)-allowed)))
    if dirs != expected_directories(allowed):
        errors.append('Directory allowlist mismatch')
    if actual != run['bundle_hashes']:
        errors.append('Frozen bundle SHA-256 mismatch')
    if run['condition']=='D-cpc':
        frozen = {SKILL_PREFIX+k:v for k,v in skill_hashes.items()}
        if {k:v for k,v in actual.items() if k.startswith(SKILL_PREFIX)} != frozen:
            errors.append('Frozen complete CPC package SHA-256 mismatch')
    for name in actual:
        try:
            text = (Path(directory)/name).read_text(encoding='utf-8')
            errors.extend(name+': '+e for e in content_errors(name,text,source_root))
        except (OSError,UnicodeError) as exc:
            errors.append(name+': unreadable subject file: '+str(exc))
    return {'passed':not errors,'errors':errors}
