from __future__ import annotations
import hashlib
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path
from tests.helpers import ROOT


def module(name, filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/filename)
    item=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(item)
    return item

release=module('cpc_release','package_release.py')
checks=module('cpc_checker','check_repository.py')


class ReleaseTests(unittest.TestCase):
    def test_private_eval_cases_excluded(self):
        self.assertFalse(release.include_path(Path('evals/private/secret.json')))
        self.assertTrue(release.include_path(Path('evals/private/README.md')))
    def test_environment_and_cache_excluded(self):
        for path in ('.venv/a.py','tests/__pycache__/a.pyc','evals/runs/output.json','local/data.json','.git/config'):
            with self.subTest(path=path):self.assertFalse(release.include_path(Path(path)))
    def test_source_and_skill_selected(self):
        for path in ('README.md','README.zh-CN.md','LICENSE','CITATION.cff','codemeta.json','.github/workflows/check.yml','skills/cybernetic-project-control/SKILL.md','examples/software-delivery/.project-control/state.json'):
            with self.subTest(path=path):self.assertTrue(release.include_path(Path(path)))
    def test_pdf_and_keys_excluded(self):
        for path in ('docs/book.pdf','docs/secret.key','LICENSE.pem','.env'):
            with self.subTest(path=path):self.assertFalse(release.include_path(Path(path)))
    def test_archives_reproducible_and_manifest_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);files={'README.md':b'Synthetic package.\n','a.txt':b'content'}
            release.write_archive(root/'a.zip','demo',files)
            release.write_archive(root/'b.zip','demo',files)
            self.assertEqual((root/'a.zip').read_bytes(),(root/'b.zip').read_bytes())
            with zipfile.ZipFile(root/'a.zip') as z:
                self.assertIsNone(z.testzip())
                for line in z.read('demo/MANIFEST.sha256').decode().splitlines():
                    expected,name=line.split('  ',1)
                    self.assertEqual(hashlib.sha256(z.read('demo/'+name)).hexdigest(),expected)
    def test_archive_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'a.zip';p.write_bytes(b'existing')
            with self.assertRaises(ValueError):release.write_archive(p,'demo',{'a.txt':b'new'})
            self.assertEqual(p.read_bytes(),b'existing')
    def test_checker_skips_virtualenv_and_real_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel in ('README.md','.venv/installed-package/bad.json','evals/runs/raw.json','evals/private/secret.json','evals/private/README.md'):
                p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('not necessarily JSON')
            found={p.relative_to(root).as_posix() for p in checks.repository_files(root)}
            self.assertEqual(found,{'README.md','evals/private/README.md'})
