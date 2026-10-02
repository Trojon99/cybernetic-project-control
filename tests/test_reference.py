from __future__ import annotations
import copy
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from tests.helpers import ROOT, SKILL, cpc, evidence, fixture, save, turn

class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.s=fixture(self.root);self.t=turn(self.s)
    def invalid(self, state=None):
        with self.assertRaises(cpc.CPCError):cpc.validate_state(state or self.s,self.root,verify_artifacts=True)
    def bad_turn(self):
        with self.assertRaises(cpc.CPCError):cpc.transition(self.s,self.t,self.root,verify_artifacts=True)
    def test_empty_state_valid(self):
        self.assertEqual(cpc.validate_state(self.s,self.root,verify_artifacts=True),[])
    def test_current_reviewed_evidence_valid(self):
        self.s['evidence']=[evidence(self.root)]
        self.s['criteria'][0].update(status='supported',evidence_ids=['E-1'])
        cpc.validate_state(self.s,self.root,verify_artifacts=True)
    def test_wrong_hash(self):
        self.s['evidence']=[evidence(self.root)]
        self.s['evidence'][0]['artifacts'][0]['sha256']='0'*64;self.invalid()
    def test_missing_artifact(self):
        self.s['evidence']=[evidence(self.root)]
        (self.root/'artifacts/E-1.txt').unlink();self.invalid()
    def test_stale_artifact_does_not_need_current_bytes(self):
        e=evidence(self.root);e.update(validity='stale',validity_reason='Input changed')
        self.s['evidence']=[e];(self.root/'artifacts/E-1.txt').unlink()
        cpc.validate_state(self.s,self.root,verify_artifacts=True)
    def test_symlink_artifact_refused(self):
        self.s['evidence']=[evidence(self.root)]
        target=self.root/'artifacts/E-1.txt';target.rename(target.with_suffix('.original'))
        target.symlink_to(target.with_suffix('.original'));self.invalid()
    def test_symlink_parent_refused(self):
        real=self.root/'real';real.mkdir();(real/'f.txt').write_text('x')
        (self.root/'alias').symlink_to(real,target_is_directory=True)
        with self.assertRaises(cpc.CPCError):cpc.safe_relative(self.root,'alias/f.txt')
    def test_path_traversal_refused(self):
        for path in ('../outside','a/../../b','./a','/tmp/a','C:/tmp/a','a\\b','a//b','https://x/file'):
            with self.subTest(path=path),self.assertRaises(cpc.CPCError):cpc.safe_relative(self.root,path)
    def test_no_duplicate_json_keys(self):
        p=self.root/'bad.json';p.write_text('{"x":1,"x":2}')
        with self.assertRaises(cpc.CPCError):cpc.load_json(p)
    def test_nonfinite_json_refused(self):
        for val in ('NaN','Infinity','-Infinity'):
            p=self.root/'bad.json';p.write_text('{"x":'+val+'}')
            with self.subTest(val=val),self.assertRaises(cpc.CPCError):cpc.load_json(p)
    def test_nonobject_json_refused(self):
        p=self.root/'bad.json';p.write_text('[]')
        with self.assertRaises(cpc.CPCError):cpc.load_json(p)
    def test_record_size_limit(self):
        p=self.root/'big.json';p.write_text('{"x":"abcdefgh"}')
        with patch.object(cpc,'MAX_RECORD_BYTES',8),self.assertRaises(cpc.CPCError):cpc.load_json(p)
    def test_bad_utf8_refused(self):
        p=self.root/'bad.json';p.write_bytes(b'\xff')
        with self.assertRaises(cpc.CPCError):cpc.load_json(p)
    def test_symlink_json_refused(self):
        p=self.root/'copy.json';p.symlink_to(self.root/'.project-control/state.json')
        with self.assertRaises(cpc.CPCError):cpc.load_json(p)
    def test_artifact_size_limit(self):
        e=evidence(self.root)
        with patch.object(cpc,'MAX_ARTIFACT_BYTES',2),self.assertRaises(cpc.CPCError):cpc.hash_file(self.root/e['artifacts'][0]['path'])
    def test_schema_version_refused(self):
        self.s['schema_version']='9.9';self.invalid()
    def test_unknown_field_refused(self):
        self.s['auto_approve_everything']=True;self.invalid()
    def test_duplicate_criterion_id(self):
        self.s['criteria'].append(copy.deepcopy(self.s['criteria'][0]));self.invalid()
    def test_unknown_evidence_target(self):
        e=evidence(self.root);e['targets']=['C-missing'];self.s['evidence']=[e];self.invalid()
    def test_unknown_evidence_dependency(self):
        self.s['evidence']=[evidence(self.root,depends=['E-missing'])];self.invalid()
    def test_evidence_dependency_cycle(self):
        self.s['evidence']=[evidence(self.root,'E-1',depends=['E-2']),evidence(self.root,'E-2',depends=['E-1'])];self.invalid()
    def test_resolved_claim_needs_evidence(self):
        self.s['criteria'][0]['status']='supported';self.invalid()
    def test_review_requires_reviewer(self):
        e=evidence(self.root);e['reviewer']=None;self.s['evidence']=[e];self.invalid()
    def test_unreviewed_cannot_support(self):
        e=evidence(self.root);e['review_status']='unreviewed';e['reviewer']=None
        self.s['evidence']=[e];self.s['criteria'][0].update(status='supported',evidence_ids=['E-1']);self.invalid()
    def test_stale_cannot_support(self):
        e=evidence(self.root);e.update(validity='stale',validity_reason='changed input')
        self.s['evidence']=[e];self.s['criteria'][0].update(status='supported',evidence_ids=['E-1']);self.invalid()
    def test_contrary_evidence_blocks_promotion(self):
        self.s['evidence']=[evidence(self.root),evidence(self.root,'E-2',relation='contradicts')]
        self.s['criteria'][0].update(status='supported',evidence_ids=['E-1']);self.invalid()
    def test_conflicts_can_be_retained_as_unknown(self):
        self.s['evidence']=[evidence(self.root),evidence(self.root,'E-2',relation='contradicts')]
        cpc.validate_state(self.s,self.root,verify_artifacts=True)
    def test_wrong_evidence_relation(self):
        self.s['evidence']=[evidence(self.root,relation='inconclusive')]
        self.s['criteria'][0].update(status='supported',evidence_ids=['E-1']);self.invalid()
    def test_wrong_evidence_claim_target(self):
        e=evidence(self.root);e['targets']=['Q-1'];self.s['evidence']=[e]
        self.s['criteria'][0].update(status='supported',evidence_ids=['E-1']);self.invalid()
    def test_resolved_question_requires_informative_evidence(self):
        self.s['evidence']=[evidence(self.root,relation='inconclusive')]
        self.s['questions'][0].update(status='resolved',evidence_ids=['E-1']);self.invalid()
    def test_current_evidence_objective_version(self):
        e=evidence(self.root);e['objective_version']=2;self.s['evidence']=[e];self.invalid()
    def test_future_observation(self):
        e=evidence(self.root);e['observed_at']='2026-10-03T12:00:00Z';self.s['evidence']=[e];self.invalid()
    def test_invalidated_evidence_requires_reason(self):
        e=evidence(self.root);e['validity']='stale';self.s['evidence']=[e];self.invalid()
    def test_current_child_of_stale_parent(self):
        e=evidence(self.root);e.update(validity='stale',validity_reason='changed')
        self.s['evidence']=[e,evidence(self.root,'E-2',depends=['E-1'])];self.invalid()
    def test_invalidation_propagates(self):
        self.s['evidence']=[evidence(self.root),evidence(self.root,'E-2',depends=['E-1'])]
        self.s['criteria'][0].update(status='supported',evidence_ids=['E-2'])
        self.s['questions'][0].update(status='resolved',evidence_ids=['E-2'])
        self.t['invalidate_evidence']=[{'id':'E-1','reason':'Input withdrawn'}]
        candidate=cpc.transition(self.s,self.t,self.root,verify_artifacts=True)
        self.assertEqual(candidate['evidence'][1]['validity'],'stale')
        self.assertEqual(candidate['criteria'][0]['status'],'unknown')
        self.assertEqual(candidate['questions'][0]['status'],'open')
    def test_transition_does_not_mutate_input(self):
        before=copy.deepcopy(self.s);cpc.transition(self.s,self.t,self.root);self.assertEqual(before,self.s)
    def test_recorded_actor_must_match_controller(self):
        self.t['actor']='worker';self.bad_turn()
    def test_stale_revision(self):
        self.t['base_revision']=1;self.bad_turn()
    def test_wrong_project(self):
        self.t['project_id']='other-project';self.bad_turn()
    def test_changed_objective_version(self):
        self.t['objective_version']=2;self.bad_turn()
    def test_cannot_change_objective_in_turn(self):
        self.t['objective']={'statement':'different goal'};self.bad_turn()
    def test_cannot_change_budget_in_turn(self):
        self.t['max_actions']=999;self.bad_turn()
    def test_turn_cannot_predate_state(self):
        self.t['created_at']='2026-10-01T08:00:00Z';self.bad_turn()
    def test_unexecuted_plan_is_not_active_turn(self):
        self.t['result']['status']='not_run';self.bad_turn()
    def test_checked_requires_evidence(self):
        self.t['result']['status']='checked';self.bad_turn()
    def test_advisory_does_not_allow_edit(self):
        self.t.update(mode='act',action_class='local_edit');self.bad_turn()
    def test_bounded_allows_scoped_edit(self):
        self.s['control'].update(mode='bounded',allowed_action_classes=['inspect','local_edit'])
        self.t.update(mode='act',action_class='local_edit')
        cpc.transition(self.s,self.t,self.root)
    def test_protected_execution_refused(self):
        self.s['control']['mode']='bounded'
        for cls in cpc.PROTECTED_CLASSES:
            self.t.update(mode='act',action_class=cls)
            with self.subTest(cls=cls):self.bad_turn()
    def test_action_outside_scope(self):
        self.s['control']['mode']='bounded';self.t.update(mode='act',action_class='local_compute');self.bad_turn()
    def test_budget_blocks_action(self):
        self.s['control']['max_actions']=0;self.bad_turn()
    def test_exhausted_budget_allows_escalation_record(self):
        self.s['control']['max_actions']=0;self.t.update(mode='escalate',action_class='none')
        self.t['result']['status']='not_run'
        candidate=cpc.transition(self.s,self.t,self.root)
        self.assertEqual(candidate['control']['actions_used'],0)
    def test_nonactive_turn_cannot_smuggle_state_updates(self):
        self.t.update(mode='wait',action_class='none');self.t['result']['status']='not_run'
        self.t['criterion_updates']=[{'id':'C-1','status':'unknown','evidence_ids':[]}];self.bad_turn()
    def test_duplicate_update_ids(self):
        u={'id':'C-1','status':'unknown','evidence_ids':[]};self.t['criterion_updates']=[u,u];self.bad_turn()
    def test_unknown_question_update(self):
        self.t['question_updates']=[{'id':'Q-missing','status':'open','evidence_ids':[]}];self.bad_turn()
    def test_cannot_replace_old_evidence(self):
        e=evidence(self.root);self.s['evidence']=[e];self.t['add_evidence']=[copy.deepcopy(e)];self.bad_turn()
    def test_unknown_diagnosis_evidence(self):
        self.t['diagnosis']['evidence_ids']=['E-missing'];self.bad_turn()
    def pending(self):
        return {'id':'P-1','description':'test','task_ref':'job-1','owner':'worker',
            'expected_at':'2026-10-03T09:00:00Z','timeout_at':'2026-10-03T11:00:00Z','status':'waiting'}
    def test_pending_timestamps(self):
        p=self.pending();p['timeout_at']='2026-10-02T11:00:00Z';self.s['pending_effects']=[p];self.invalid()
    def test_no_pending_id_reuse_for_new_task(self):
        self.s['pending_effects']=[self.pending()]
        p=self.pending();p['task_ref']='job-2';self.t['pending_updates']=[p];self.bad_turn()
    def test_no_reopening_finished_pending(self):
        p=self.pending();p['status']='received';self.s['pending_effects']=[p]
        self.t['pending_updates']=[self.pending()];self.bad_turn()
    def test_apply_creates_receipt_and_valid_state(self):
        result=cpc.apply_turn(self.root,self.t,0)
        self.assertEqual(result['status'],'applied')
        state=cpc.read_project(self.root);cpc.validate_state(state,self.root,verify_artifacts=True)
        self.assertEqual(state['revision'],1)
        self.assertTrue((self.root/'.project-control/receipts/T-1.json').is_file())
    def test_apply_is_idempotent(self):
        cpc.apply_turn(self.root,self.t,0)
        replay=cpc.apply_turn(self.root,self.t,0)
        self.assertEqual(replay['status'],'already_applied')
        self.assertEqual(cpc.read_project(self.root)['control']['actions_used'],1)
    def test_duplicate_turn_id_different_content(self):
        cpc.apply_turn(self.root,self.t,0);self.t['result']['summary']='different'
        with self.assertRaises(cpc.CPCError):cpc.apply_turn(self.root,self.t,0)
    def test_expected_revision_conflict(self):
        with self.assertRaises(cpc.CPCError):cpc.apply_turn(self.root,self.t,9)
    def test_lock_not_stolen(self):
        p=self.root/'.project-control/.write.lock';p.write_text('existing writer')
        with self.assertRaises(cpc.CPCError):cpc.apply_turn(self.root,self.t,0)
        self.assertEqual(p.read_text(),'existing writer')
    def test_corrupt_receipt_detected(self):
        cpc.apply_turn(self.root,self.t,0)
        p=self.root/'.project-control/receipts/T-1.json';r=cpc.load_json(p);r['result']['summary']='corrupted';p.write_bytes(cpc.canonical_bytes(r))
        with self.assertRaises(cpc.CPCError):cpc.validate_state(cpc.read_project(self.root),self.root,verify_artifacts=True)
    def test_crash_between_receipt_and_state_is_recoverable(self):
        original=cpc.atomic_write
        def fail_state(path,payload):
            if path.name=='state.json':raise OSError('simulated failure')
            return original(path,payload)
        with patch.object(cpc,'atomic_write',side_effect=fail_state),self.assertRaises(OSError):cpc.apply_turn(self.root,self.t,0)
        self.assertEqual(cpc.read_project(self.root)['revision'],0)
        self.assertTrue((self.root/'.project-control/receipts/T-1.json').is_file())
        self.assertFalse((self.root/'.project-control/.write.lock').exists())
        self.assertEqual(cpc.apply_turn(self.root,self.t,0)['status'],'applied')
    def test_conflicting_orphan_receipt(self):
        different=copy.deepcopy(self.t);different['result']['summary']='other'
        (self.root/'.project-control/receipts/T-1.json').write_bytes(cpc.canonical_bytes(different))
        with self.assertRaises(cpc.CPCError):cpc.apply_turn(self.root,self.t,0)
    def test_concurrent_writers_do_not_both_commit(self):
        t2=copy.deepcopy(self.t);t2['id']='T-2'
        def attempt(t):
            try:return cpc.apply_turn(self.root,t,0)['status']
            except cpc.CPCError:return 'conflict'
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,[self.t,t2]))
        self.assertEqual(results.count('applied'),1)
        self.assertEqual(results.count('conflict'),1)
        self.assertEqual(cpc.read_project(self.root)['revision'],1)
    def test_history_budget_mismatch(self):
        self.s['control']['actions_used']=1;self.invalid()
    def test_snapshot_is_read_only(self):
        before=copy.deepcopy(self.s);out=cpc.snapshot(self.s)
        self.assertEqual(self.s,before);self.assertIn('limits',out)
    def test_init_never_overwrites(self):
        before=(self.root/'.project-control/state.json').read_bytes()
        with self.assertRaises(cpc.CPCError):cpc.init_project(self.root,'x','goal','criterion','agent')
        self.assertEqual(before,(self.root/'.project-control/state.json').read_bytes())
    def test_init_preserves_project_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'AGENTS.md').write_text('existing rules')
            s=cpc.init_project(root,'demo','Approved goal','Explicit criterion','controller',now='2026-10-02T09:00:00Z')
            self.assertEqual(s['control']['mode'],'advisory')
            self.assertEqual((root/'AGENTS.md').read_text(),'existing rules')
    def test_init_rejects_known_existing_state(self):
        for marker in ('.loopx','.apm','.project','PROJECT_STATE.md','_knowledge'):
            with self.subTest(marker=marker),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);(root/marker).mkdir()
                with self.assertRaises(cpc.CPCError):cpc.init_project(root,'x','goal','criterion','agent')
    def test_timezone_required(self):
        with self.assertRaises(cpc.CPCError):cpc.timestamp('2026-10-02T10:00:00')

if __name__=='__main__':unittest.main()
