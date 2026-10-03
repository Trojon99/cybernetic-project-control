#!/usr/bin/env python3
"""Build deterministic source and standalone-Skill ZIPs. No uploads or Git writes."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'cybernetic-project-control'
EXCLUDED_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', '.mypy_cache',
                 'dist', 'build', 'local', 'source', 'node_modules'}
ROOT_FILES = {'README.md','README.zh-CN.md','AGENTS.md','LICENSE','NOTICE.md','VERSION',
              'CHANGELOG.md','CONTRIBUTING.md','CODE_OF_CONDUCT.md','SECURITY.md','CITATION.cff','codemeta.json',
              'requirements.txt','requirements-dev.txt','.gitignore','.editorconfig'}
ROOT_DIRS = {'.github','docs','evals','examples','experiments','integrations','reports','skills','tests','theory','tools'}
ALLOWED_SUFFIXES = {'.md','.json','.py','.txt','.yaml','.yml','.cff'}


def include_path(relative: Path) -> bool:
    """Limit release material; intentionally omit live runs and private eval cases."""
    parts = relative.parts
    if any(p in EXCLUDED_DIRS for p in parts):return False
    if len(parts) == 1 and parts[0] not in ROOT_FILES:return False
    if len(parts) > 1 and parts[0] not in ROOT_DIRS:return False
    if parts[:2] == ('experiments','codex-pilot-01'):
        if relative.name in {'manifest.json','.coordinator.lock'}:return False
        if len(parts)>2 and parts[2] in {'bundles','trajectory','results','reports','coordinator','subject-exports'}:
            return len(parts)==4 and parts[2] in {'results','reports'} and parts[3]=='.gitkeep'
    if parts[:2] == ('evals','runs'):return False
    if parts[:2] == ('evals','private') and parts != ('evals','private','README.md'):return False
    return (relative.suffix.lower() in ALLOWED_SUFFIXES
            or relative.name in {'LICENSE','VERSION','.gitignore','.editorconfig','.gitkeep'})


def release_files(root: Path) -> dict[str, bytes]:
    files = {}
    for p in sorted(root.rglob('*')):
        relative = p.relative_to(root)
        if not include_path(relative):continue
        if p.is_symlink():raise ValueError(f'Refusing release symlink: {relative}')
        if not p.is_file():continue
        files[relative.as_posix()] = p.read_bytes()
    if 'README.md' not in files:raise ValueError('Missing source README')
    return files


def write_archive(path: Path, prefix: str, files: dict[str, bytes]) -> dict:
    if path.exists():raise ValueError(f'Refusing to replace release: {path}')
    manifest = ''.join(f'{hashlib.sha256(data).hexdigest()}  {name}\n'
                       for name, data in sorted(files.items())).encode('utf-8')
    contents = {**files,'MANIFEST.sha256':manifest}
    with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(f'{prefix}/{name}',date_time=(1980,1,1,0,0,0))
            info.create_system=3;info.external_attr=0o100644 << 16
            info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:raise ValueError('ZIP integrity verification failed')
    return {'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes':path.stat().st_size,'content_files':len(files),'manifest_entries':len(files)}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    output=args.output.resolve()
    if output.is_relative_to(ROOT):raise ValueError('Release output must be outside source repository')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9.-]*',version):raise ValueError('Invalid VERSION')
    output.mkdir(parents=True,exist_ok=True)
    files=release_files(ROOT)
    skill_prefix='skills/cybernetic-project-control/'
    standalone={name[len(skill_prefix):]:data for name,data in files.items() if name.startswith(skill_prefix)}
    if 'SKILL.md' not in standalone:raise ValueError('Missing standalone Skill')
    planned=[output/f'cybernetic-project-control-{version}.zip',output/f'cybernetic-project-control-skill-{version}.zip']
    if any(p.exists() for p in planned):raise ValueError('A release archive already exists; use a fresh output directory')
    reports=[write_archive(planned[0],'cybernetic-project-control',files),
             write_archive(planned[1],'cybernetic-project-control',standalone)]
    report={'version':version,'archives':reports,'publication_performed':False,
            'limits':'Byte integrity only. This is not a signature, independent audit or agent evaluation.'}
    (output/'release-checksums.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
