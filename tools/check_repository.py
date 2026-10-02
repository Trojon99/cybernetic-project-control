#!/usr/bin/env python3
"""Offline package, source syntax, schema, link and fixture checks."""
from __future__ import annotations
import importlib.util
import json
import re
import sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/cybernetic-project-control'
spec=importlib.util.spec_from_file_location('cpc_check',SKILL/'scripts/cpc.py')
cpc=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(cpc)

def repository_files(root: Path):
    excluded={'.git','.venv','venv','__pycache__','.pytest_cache','node_modules','dist','build','local','source'}
    for path in root.rglob('*'):
        rel=path.relative_to(root)
        if any(part in excluded for part in rel.parts):continue
        if rel.parts[:2] == ('experiments','codex-pilot-01'):
            if rel.name in {'manifest.json','.coordinator.lock'}:continue
            if len(rel.parts)>2 and rel.parts[2] in {'bundles','trajectory','results','reports'}:continue
        if rel.parts[:2] == ('evals','runs'):continue
        if rel.parts[:2] == ('evals','private') and rel.parts != ('evals','private','README.md'):continue
        if path.is_file():yield path

def main():
    errors=[];checks={}
    text=(SKILL/'SKILL.md').read_text(encoding='utf-8')
    try:
        head=text.split('---',2)[1];meta=yaml.safe_load(head)
        assert meta['name']==SKILL.name
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',meta['name']) and len(meta['name'])<=64
        assert 0<len(meta['description'])<=1024
        assert len(meta.get('compatibility',''))<=500
        assert all(isinstance(k,str) and isinstance(v,str) for k,v in meta.get('metadata',{}).items())
        assert len(text.splitlines())<500
        checks['skill_frontmatter_and_size']='pass'
    except (ValueError,AssertionError,KeyError,TypeError,yaml.YAMLError) as exc:errors.append(f'Skill metadata invalid: {exc}')
    files=list(repository_files(ROOT))
    for p in files:
        if p.suffix=='.py':
            try:compile(p.read_text(encoding='utf-8'),str(p),'exec')
            except (SyntaxError,UnicodeError) as exc:errors.append(f'{p.relative_to(ROOT)}: {exc}')
        if p.suffix=='.json':
            try:
                d=cpc.load_json(p)
                if p.name.endswith('.schema.json'):Draft202012Validator.check_schema(d)
            except (cpc.CPCError,ValueError) as exc:errors.append(f'{p.relative_to(ROOT)}: {exc}')
        if p.suffix=='.md':
            for target in re.findall(r'\[[^\]\n]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)',p.read_text(encoding='utf-8')):
                if '://' in target or target.startswith(('#','mailto:')):continue
                target=target.split('#',1)[0]
                if target and not (p.parent/target).exists():errors.append(f'Broken link in {p.relative_to(ROOT)}: {target}')
                if p.is_relative_to(SKILL) and target and not (p.parent/target).resolve().is_relative_to(SKILL.resolve()):errors.append(f'Standalone skill links outside package: {target}')
        if p.suffix.lower() in {'.pdf','.pem','.key'}:errors.append(f'Forbidden release material: {p.relative_to(ROOT)}')
    for project in (ROOT/'examples').iterdir():
        if not (project/'.project-control/state.json').is_file():continue
        try:
            state=cpc.read_project(project);cpc.validate_state(state,project,verify_artifacts=True)
            if (project/'turn.json').is_file():cpc.transition(state,cpc.load_json(project/'turn.json'),project,verify_artifacts=True)
        except cpc.CPCError as exc:errors.append(f'Example {project.name}: {exc}')
    cases=[json.loads(p.read_text()) for p in (ROOT/'evals/cases').glob('E*.json')]
    ids={c['id'] for c in cases}
    if len(ids)!=len(cases):errors.append('Duplicate evaluation case ids')
    trace=(ROOT/'theory/traceability.md').read_text()
    for case_id in re.findall(r'\bE\d{2}\b',trace):
        if case_id not in ids:errors.append('Traceability references missing case '+case_id)
    for n in range(1,13):
        if f'CPC-{n:02d}' not in trace:errors.append(f'Missing rule CPC-{n:02d}')
    checks.update(python_syntax='pass' if not errors else 'see_errors',public_cases=len(cases),
        skill_lines=len(text.splitlines()),relative_links='checked',source_pdf_bundled=False,
        live_agent_evaluation='not_run')
    print(json.dumps({'status':'pass' if not errors else 'fail','checks':checks,'errors':errors},ensure_ascii=False,indent=2))
    return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
