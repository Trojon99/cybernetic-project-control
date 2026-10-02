from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tests.helpers import cpc, fixture, turn, evidence, save
from tests.test_package_and_evals import evalrun


class RecordHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.state=fixture(self.root)
    def test_checked_result_cannot_cite_invalidated_evidence(self):
        self.state['evidence']=[evidence(self.root)]
        proposal=turn(self.state)
        proposal['invalidate_evidence']=[{'id':'E-1','reason':'Synthetic withdrawal.'}]
        proposal['result'].update(status='checked',evidence_ids=['E-1'])
        with self.assertRaisesRegex(cpc.CPCError,'current reviewed'):
            cpc.transition(self.state,proposal,self.root)
    def test_checked_result_cannot_mix_reviewed_and_unreviewed(self):
        a=evidence(self.root);b=evidence(self.root,'E-2');b['review_status']='unreviewed';b['reviewer']=None
        self.state['evidence']=[a,b];proposal=turn(self.state)
        proposal['result'].update(status='checked',evidence_ids=['E-1','E-2'])
        with self.assertRaisesRegex(cpc.CPCError,'current reviewed'):
            cpc.transition(self.state,proposal,self.root)
    def test_checked_result_accepts_current_reviewed_reference(self):
        proposal=turn(self.state);proposal['add_evidence']=[evidence(self.root)]
        proposal['result'].update(status='checked',evidence_ids=['E-1'])
        self.assertEqual(cpc.transition(self.state,proposal,self.root,verify_artifacts=True)['revision'],1)
    def test_receipt_actor_metadata_must_match(self):
        proposal=turn(self.state);cpc.apply_turn(self.root,proposal,0)
        state=cpc.read_project(self.root);state['history'][0]['actor']='another-controller'
        with self.assertRaisesRegex(cpc.CPCError,'metadata'):
            cpc.validate_state(state,self.root,verify_artifacts=True)
    def test_receipt_summary_must_match(self):
        cpc.apply_turn(self.root,turn(self.state),0)
        state=cpc.read_project(self.root);state['history'][0]['summary']='Fabricated completion.'
        with self.assertRaisesRegex(cpc.CPCError,'summary'):
            cpc.validate_state(state,self.root,verify_artifacts=True)
    def test_history_uses_canonical_receipt_path(self):
        cpc.apply_turn(self.root,turn(self.state),0)
        state=cpc.read_project(self.root);state['history'][0]['receipt_path']='artifacts/other.json'
        with self.assertRaisesRegex(cpc.CPCError,'Noncanonical'):
            cpc.validate_state(state,self.root)
    def test_history_times_are_monotonic(self):
        cpc.apply_turn(self.root,turn(self.state),0)
        state=cpc.read_project(self.root);p=turn(state);p['id']='T-2';p['created_at']='2026-10-02T11:00:00Z'
        cpc.apply_turn(self.root,p,1);state=cpc.read_project(self.root)
        state['history'][1]['at']='2026-10-02T09:30:00Z'
        with self.assertRaisesRegex(cpc.CPCError,'monotonic'):
            cpc.validate_state(state,self.root)
    def test_decisions_cannot_supersede_future_decisions(self):
        d={'id':'D-1','summary':'Synthetic first decision','rationale':'Fixture only.',
           'alternatives':['Defer'],'evidence_ids':[], 'revisit_when':'New evidence', 'supersedes':'D-2'}
        self.state['decisions']=[d,{**copy.deepcopy(d),'id':'D-2','supersedes':'D-1'}]
        with self.assertRaisesRegex(cpc.CPCError,'earlier decision'):
            cpc.validate_state(self.state,self.root)


class EvalInputHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'input.json'
    def test_duplicate_response_keys_rejected(self):
        self.path.write_text('{"mode":"act","mode":"stop"}')
        with self.assertRaisesRegex(ValueError,'Duplicate'):evalrun.load_json(self.path)
    def test_nonfinite_response_rejected(self):
        self.path.write_text('{"cost":NaN}')
        with self.assertRaisesRegex(ValueError,'Non-finite'):evalrun.load_json(self.path)
    def test_response_root_must_be_object(self):
        self.path.write_text('[]')
        with self.assertRaisesRegex(ValueError,'object'):evalrun.load_json(self.path)
    def test_bounded_input(self):
        self.path.write_bytes(b' '* (1024*1024+1))
        with self.assertRaisesRegex(ValueError,'1 MiB'):evalrun.load_json(self.path)
    def test_escalation_needs_concrete_question(self):
        c=evalrun.load_case('E10')
        r={'selected_action':c['oracle']['acceptable_actions'][0], 'mode':'escalate', 'evidence_ids':c['oracle']['required_evidence_ids'], 'rationale':'Synthetic contract test only.', 'expected_feedback':'Human decides.', 'contingency':'Keep current authorization.', 'human_question':None}
        self.assertFalse(evalrun.score(c,r)['contract_valid'])
