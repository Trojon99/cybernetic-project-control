"""Deterministic single-run payloads; never launch tasks or generate responses."""
from __future__ import annotations
import gzip
import io
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
import blinding
import pilot


def extract_archive(archive, target):
    """Extract bounded regular allowlist candidates, never links, traversal or devices."""
    target = Path(target)
    if not target.is_dir() or target.is_symlink() or any(target.iterdir()):
        raise ValueError('Require fresh empty extraction directory')
    if Path(archive).is_symlink():
        raise ValueError('Archive symlink rejected')
    seen = set(); total = 0
    with tarfile.open(archive,'r:gz') as stream:
        for member in stream:
            name = member.name
            parts = PurePosixPath(name).parts
            if (not name or name.startswith('/') or '\\' in name or
                any(p in ('.','..','') for p in name.split('/')) or
                PurePosixPath(name).as_posix()!=name or name in seen or
                not member.isfile() or member.pax_headers or member.linkname):
                raise ValueError('Unsafe/duplicate archive member: '+name)
            if len(seen)>=128 or member.size>1024*1024 or member.size<0:
                raise ValueError('Archive member bounds exceeded')
            total+=member.size
            if total>16*1024*1024:
                raise ValueError('Archive content exceeds bounds')
            seen.add(name)
            out = target.joinpath(*parts)
            out.parent.mkdir(parents=True,exist_ok=True)
            raw = stream.extractfile(member).read(member.size+1)
            if len(raw)!=member.size:
                raise ValueError('Truncated archive')
            out.write_bytes(raw)
    return seen


def check_one(archive, run, skill_hashes):
    with tempfile.TemporaryDirectory(prefix='cpc-export-check-') as tmp:
        try:
            extract_archive(archive,Path(tmp))
            return blinding.validate_bundle(Path(tmp),run,skill_hashes,pilot.ROOT)
        except (OSError,ValueError,tarfile.TarError,EOFError) as exc:
            return {'passed':False,'errors':[str(exc)]}


def export(base=pilot.HERE):
    base=Path(base).resolve()
    with pilot.lock(base):
        m=pilot.manifest(base)
        validated=pilot.verify(base)
        if not validated['passed']:
            raise ValueError('Source bundle validation failed: '+str(validated['errors']))
        directory=base/'subject-exports'
        if directory.exists():
            raise ValueError('Refusing to overwrite subject exports')
        directory.mkdir()
        records=[]
        for run in m['runs']:
            archive=directory/(run['run_id']+'.tar.gz')
            source=pilot.coordinator(base)/'bundles'/run['run_id']
            # No original path, gzip filename, timestamps, owners or PAX attributes.
            with archive.open('xb') as output:
                with gzip.GzipFile(fileobj=output,filename='',mode='wb',mtime=0) as compressed:
                    with tarfile.open(fileobj=compressed,mode='w',format=tarfile.USTAR_FORMAT) as tar:
                        for name in sorted(run['bundle_hashes']):
                            raw=(source/name).read_bytes()
                            if blinding.sha(raw)!=run['bundle_hashes'][name]:
                                raise ValueError('Bundle changed during export')
                            member=tarfile.TarInfo(name)
                            member.size=len(raw);member.mode=0o644;member.mtime=0
                            member.uid=member.gid=0;member.uname=member.gname=''
                            tar.addfile(member,io.BytesIO(raw))
            check=check_one(archive,run,m['skill_package_hashes'])
            if not check['passed']:
                raise ValueError('Re-extracted export failed: '+str(check['errors']))
            records.append({'run_id':run['run_id'],'archive':archive.name,
                'sha256':pilot.digest(archive),'bytes':archive.stat().st_size,
                'reextracted_blinding':check})
        pilot.write(pilot.coordinator(base)/'export-manifest.json',{'exports':records})
        (pilot.coordinator(base)/'export-checksums.sha256').write_text(
            ''.join(r['sha256']+'  '+r['archive']+'\n' for r in records))
    return {'exports':len(records),'all_reextracted_passed':True,'model_runs':0}


def verify_exports(base=pilot.HERE):
    base=Path(base)
    m=pilot.manifest(base)
    records=pilot.read(pilot.coordinator(base)/'export-manifest.json')['exports']
    directory=base/'subject-exports'
    errors=[];checks=[]
    expected={r['run_id']+'.tar.gz' for r in m['runs']}
    if directory.is_symlink() or not directory.is_dir():
        return {'passed':False,'errors':['Missing or symlink export directory'],'exports_checked':0}
    if {f.name for f in directory.iterdir()}!=expected:
        errors.append('Export allowlist differs from exactly 32 opaque archives')
    by_id={r['run_id']:r for r in records}
    if len(records)!=32 or set(by_id)!={r['run_id'] for r in m['runs']}:
        errors.append('Export checksum manifest coverage mismatch')
    for run in m['runs']:
        rid=run['run_id'];archive=directory/(rid+'.tar.gz');record=by_id.get(rid)
        if not record or archive.is_symlink() or not archive.is_file():
            errors.append(rid+': missing/unsafe export');continue
        if record['archive']!=archive.name or pilot.digest(archive)!=record['sha256']:
            errors.append(rid+': archive SHA-256 mismatch')
        result=check_one(archive,run,m['skill_package_hashes'])
        errors.extend(rid+': '+e for e in result['errors'])
        checks.append({'run_id':rid,**result})
    return {'passed':not errors,'errors':errors,'exports_checked':len(checks),
            'checks':checks,'isolation_proven':False,'model_runs':0}
