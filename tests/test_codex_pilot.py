"""Harness tests with synthetic records; never evidence of evaluated agent efficacy."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tests.helpers import ROOT

DIRECTORY = ROOT/'experiments/codex-pilot-01'
sys.path.insert(0, str(DIRECTORY))
import pilot

class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)/'coordinator'
        pilot.prepare(cls.base)
        cls.m = pilot.manifest(cls.base)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_32_bundles_and_exact_pairs(self):
        self.assertEqual(len(list((self.base/'bundles').iterdir())),32)
        self.assertEqual(len(self.m['runs']),32)
        for c in pilot.config()['cases']:
            self.assertEqual({r['condition'] for r in self.m['runs'] if r['case_id']==c},set(pilot.config()['conditions']))

    def test_oracle_fields_absent(self):
        for run in self.m['runs']:
            obj=pilot.read(self.base/'bundles'/run['run_id']/'input.json')
            for key in pilot.TOKENS:self.assertNotIn(key,json.dumps(obj))
            self.assertNotIn('mechanisms',obj)

    def test_both_baselines_unchanged(self):
        for run in self.m['runs']:
            if run['condition'] in ('B-memory','C-generic-pm'):
                src='memory-only.md' if run['condition']=='B-memory' else 'generic-pm.md'
                self.assertEqual((self.base/'bundles'/run['run_id']/'guidance.md').read_bytes(),(ROOT/'evals/baselines'/src).read_bytes())

    def test_complete_skill_only_d(self):
        for run in self.m['runs']:
            package=self.base/'bundles'/run['run_id']/'guidance'
            if run['condition']=='D-cpc':self.assertEqual(pilot.files(package),pilot.files(pilot.SKILL,ignore_cache=True))
            else:self.assertFalse(package.exists())

    def test_identical_prompt_schema_evidence(self):
        for run in self.m['runs']:
            b=self.base/'bundles'/run['run_id']
            self.assertEqual((b/'subject-prompt.md').read_bytes(),(DIRECTORY/'subject-prompt.md').read_bytes())
            self.assertEqual((b/'response.schema.json').read_bytes(),(ROOT/'evals/response.schema.json').read_bytes())
            self.assertEqual(pilot.read(b/'input.json'),pilot.evaluator.public_packet(pilot.evaluator.load_case(run['case_id'])))

    def test_reproducible_randomization_opaque_ids(self):
        with tempfile.TemporaryDirectory() as t:
            other=Path(t)/'copy';pilot.prepare(other)
            runs=pilot.manifest(other)['runs']
            self.assertEqual(runs,self.m['runs'])
            self.assertEqual([r['run_id'] for r in runs],[f'run-{i:03d}' for i in range(1,33)])
            self.assertNotEqual([(r['case_id'],r['condition']) for r in runs],list(pilot.itertools.product(pilot.config()['cases'],pilot.config()['conditions'])))

    def test_strict_scan_reports_literal_in_full_skill(self):
        result=pilot.verify(self.base)
        if any('oracle' in (pilot.SKILL/f).read_text().lower() for f in pilot.files(pilot.SKILL,ignore_cache=True)):
            self.assertFalse(result['passed'])
            self.assertEqual(len(result['errors']),40)
        else:self.assertTrue(result['passed'],result)

    def test_injected_answer_file_and_symlink_rejected(self):
        run=self.m['runs'][0];b=self.base/'bundles'/run['run_id']
        f=b/'answer.json'
        try:
            f.write_text('{"acceptable_actions": ["X"]}')
            result=pilot.verify(self.base)
            self.assertTrue(any('acceptable_actions' in e for e in result['errors']))
        finally:f.unlink()
        try:
            f.symlink_to(ROOT/'evals/run.py')
            with self.assertRaises(ValueError):pilot.verify(self.base)
        finally:f.unlink()

    def test_scorer_blocked_during_running_without_reading_bundles(self):
        rid=self.m['runs'][0]['run_id'];p=self.base/'results'/rid/'metadata.json'
        old=pilot.read(p);running=dict(old,completion_status='running');pilot.write(p,running)
        try:
            with self.assertRaisesRegex(ValueError,'still running'):pilot.score(self.base)
        finally:pilot.write(p,old)

    def test_missing_invalid_counted_and_no_subject_reads(self):
        ids=[r['run_id'] for r in self.m['runs'][:2]]
        originals={}
        for rid in ids:
            p=self.base/'results'/rid/'metadata.json';originals[rid]=pilot.read(p)
            pilot.write(p,dict(originals[rid],completion_status='completed'))
        invalid=self.base/'results'/ids[1]/'response.json';invalid.write_text('{broken')
        real_read=pilot.read
        def guard(path):
            self.assertNotIn('bundles',Path(path).parts)
            return real_read(path)
        try:
            with patch.object(pilot,'read',side_effect=guard):rows=pilot.score(self.base)
            self.assertEqual(len(rows),32)
            for r in rows:
                if r['run_id'] in ids:self.assertFalse(r['contract_valid']);self.assertFalse(r['action_correct'])
                else:self.assertIsNone(r['contract_valid'])
        finally:
            invalid.unlink()
            for rid in ids:pilot.write(self.base/'results'/rid/'metadata.json',originals[rid])

    def test_report_all_planned_na_and_review_blinding(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t)/'coordinator';pilot.prepare(base);summary=pilot.report(base)
            self.assertEqual(sum(x['planned'] for x in summary.values()),32)
            self.assertEqual(sum(x['attempted'] for x in summary.values()),0)
            with (base/'reports/results.csv').open() as f:
                rows=list(pilot.csv.DictReader(f))
            self.assertEqual(len(rows),32)
            self.assertTrue(all(r['action_correct']=='NA' and r['hard_failure']=='NA' for r in rows))
            packet=base/'reports/blind-review'
            self.assertEqual(len(list(packet.glob('review-*'))),32)
            for f in packet.rglob('*'):
                if f.is_file():
                    text=f.read_text()
                    self.assertFalse(any(c in text for c in pilot.config()['conditions']))
            self.assertTrue((base/'reports/review-map.json').exists())

    def test_no_overwrites_or_selective_retries(self):
        with self.assertRaises(ValueError):pilot.prepare(self.base)
        with self.assertRaises(ValueError):pilot.collect(self.base,self.m['runs'][0]['run_id'],None,'failed')

    def test_recorded_lifecycle_collection_and_existing_scoring(self):
        # Synthetic lifecycle only: patch the known strict-scan conflict in this unit test.
        with tempfile.TemporaryDirectory() as t:
            base=Path(t)/'coordinator';pilot.prepare(base)
            run=pilot.manifest(base)['runs'][0];rid=run['run_id']
            metadata={'model':'synthetic-test','host':'unit-test','start_time':'2000-01-01T00:00:00Z',
                'task_id':'synthetic','workspace_id':'synthetic','isolation_evidence':'unit test only','budget':{}}
            with patch.object(pilot,'verify',return_value={'passed':True}):pilot.begin(base,rid,metadata)
            c=pilot.evaluator.load_case(run['case_id'])
            response={'selected_action':c['oracle']['acceptable_actions'][0],
                'mode':c['oracle']['acceptable_modes'][0], 'evidence_ids':c['oracle']['required_evidence_ids'],
                'rationale':'Synthetic lifecycle test, not an evaluated response.',
                'expected_feedback':'Synthetic feedback only.', 'contingency':'Change action if evidence changes.',
                'human_question':'Confirm the goal tradeoff.' if c['oracle']['acceptable_modes'][0]=='escalate' else None}
            raw=Path(t)/'response.json';pilot.write(raw,response)
            pilot.collect(base,rid,raw,'completed',{'end_time':'2000-01-01T00:00:01Z'})
            rows=pilot.score(base);row=next(x for x in rows if x['run_id']==rid)
            self.assertTrue(row['action_correct']);self.assertTrue(row['mode_correct'])
            self.assertEqual(row['behavioral_success'],'not_assessed')
            with self.assertRaises(ValueError):pilot.collect(base,rid,raw,'completed')
            with self.assertRaises(ValueError):pilot.begin(base,rid,metadata)

    def test_package_excludes_generated_includes_harness(self):
        spec=importlib.util.spec_from_file_location('pilot_package',ROOT/'tools/package_release.py')
        package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)
        self.assertTrue(package.include_path(Path('experiments/codex-pilot-01/pilot.py')))
        for suffix in ('manifest.json','bundles/run-001/input.json','results/run-001/response.json','reports/summary.json','trajectory/T1/stage-2/input.json'):
            self.assertFalse(package.include_path(Path('experiments/codex-pilot-01')/suffix))

    def test_stage_order_and_future_outside_subject(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t)/'coordinator';pilot.prepare(base)
            w=Path(t).resolve()/'subject-1';pilot.release(base,'T1',1,w)
            self.assertEqual(set(f.name for f in w.iterdir()),{'TASK.md','input.json','response.schema.json','subject-prompt.md'})
            with self.assertRaises(ValueError):pilot.release(base,'T1',3,Path(t)/'bad')
            response={'selected_action':'A','mode':'observe','evidence_ids':['O1'],'rationale':'Synthetic saved decision for lifecycle test.', 'expected_feedback':'Inspect simulation evidence.', 'contingency':'Replan when evidence changes.', 'human_question':None}
            saved=Path(t)/'response.json';pilot.write(saved,response)
            w2=Path(t).resolve()/'subject-2';pilot.release(base,'T1',2,w2,saved)
            self.assertFalse((w2/'stage-3').exists())
            with self.assertRaises(ValueError):pilot.release(base,'T1',3,base/'subject',saved)

    def test_t4_requires_handoff_without_conversation(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t)/'coordinator';pilot.prepare(base)
            pilot.release(base,'T4',1,Path(t).resolve()/'agent-a')
            with self.assertRaises(ValueError):pilot.release(base,'T4',2,Path(t).resolve()/'agent-b')

if __name__=='__main__':unittest.main()
