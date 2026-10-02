from __future__ import annotations
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tests.helpers import ROOT, SKILL, cpc

spec=importlib.util.spec_from_file_location('cpc_eval_runner',ROOT/'evals/run.py')
evalrun=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(evalrun)

class PackageAndEvalTests(unittest.TestCase):
    def test_examples_are_valid(self):
        for p in (ROOT/'examples').iterdir():
            if (p/'.project-control/state.json').is_file():
                with self.subTest(project=p.name):cpc.validate_state(cpc.read_project(p),p,verify_artifacts=True)
    def test_example_turns_are_consistent(self):
        for p in (ROOT/'examples').iterdir():
            if (p/'turn.json').is_file():
                with self.subTest(project=p.name):cpc.transition(cpc.read_project(p),cpc.load_json(p/'turn.json'),p,verify_artifacts=True)
    def test_standalone_skill_has_every_tool_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'cybernetic-project-control';shutil.copytree(SKILL,target)
            result=subprocess.run([sys.executable,str(target/'scripts/cpc.py'),'validate',str(ROOT/'examples/research-measurement'),'--verify-artifacts'],cwd=tmp,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
    def test_case_ids_and_oracles(self):
        cases=list((ROOT/'evals/cases').glob('E*.json'));self.assertEqual(len(cases),26)
        for path in cases:
            c=json.loads(path.read_text());options={x['id'] for x in c['options']};obs={x['id'] for x in c['observations']}
            with self.subTest(case=c['id']):
                self.assertTrue(set(c['oracle']['acceptable_actions'])<=options)
                self.assertFalse(set(c['oracle']['acceptable_actions']) & set(c['oracle']['forbidden_actions']))
                self.assertTrue(set(c['oracle']['required_evidence_ids'])<=obs)
    def test_public_packet_omits_oracle(self):
        c=evalrun.load_case('E07');p=evalrun.public_packet(c)
        self.assertNotIn('oracle',p);self.assertNotIn('mechanisms',p)
    def response(self,c):
        return {'selected_action':c['oracle']['acceptable_actions'][0],
            'mode':c['oracle']['acceptable_modes'][0],
            'evidence_ids':c['oracle']['required_evidence_ids'],
            'rationale':'Synthetic scorer fixture, not an agent-generated management decision.',
            'expected_feedback':'Synthetic check only.', 'contingency':'Recheck the fixture conditions.',
            'human_question':'Confirm the necessary decision.' if c['oracle']['acceptable_modes'][0]=='escalate' else None}
    def test_scorer_accepts_oracle_contract_fixtures(self):
        for path in (ROOT/'evals/cases').glob('E*.json'):
            c=evalrun.load_case(path.stem)
            with self.subTest(case=c['id']):
                result=evalrun.score(c,self.response(c))
                self.assertTrue(result['all_contract_checks_pass'])
                self.assertEqual(result['behavioral_success'],'not_assessed')
    def test_scorer_rejects_unknown_evidence(self):
        c=evalrun.load_case('E07');r=self.response(c);r['evidence_ids'].append('O999')
        self.assertFalse(evalrun.score(c,r)['all_contract_checks_pass'])
    def test_scorer_rejects_forbidden_action(self):
        c=evalrun.load_case('E11');r=self.response(c);r['selected_action']='A'
        self.assertFalse(evalrun.score(c,r)['all_contract_checks_pass'])
    def test_scorer_rejects_wrong_mode(self):
        c=evalrun.load_case('E07');r=self.response(c);r['mode']='act'
        self.assertFalse(evalrun.score(c,r)['all_contract_checks_pass'])
    def test_scorer_rejects_bad_structure(self):
        self.assertFalse(evalrun.score(evalrun.load_case('E07'),{})['contract_valid'])
    def test_no_case_path_traversal(self):
        with self.assertRaises(ValueError):evalrun.load_case('../../README')
    def test_prepare_has_no_model_run_or_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'case';rc=evalrun.main(['prepare','--case','E07','--output',str(output)])
            self.assertEqual(rc,0);self.assertEqual(set(p.name for p in output.iterdir()),{'input.json','TASK.md','response.schema.json'})
            self.assertNotIn('oracle',json.loads((output/'input.json').read_text()))

if __name__=='__main__':unittest.main()
