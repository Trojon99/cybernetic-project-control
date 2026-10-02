#!/usr/bin/env python3
"""Reproduce one complete record-update loop on a disposable synthetic copy.

Does not call an AI, perform an experiment, or modify the shipped examples.
"""
from __future__ import annotations
import copy
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cpc_demo',ROOT/'skills/cybernetic-project-control/scripts/cpc.py')
cpc=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(cpc)

def main():
    with tempfile.TemporaryDirectory(prefix='cpc-demo-') as temp:
        project=Path(temp)/'research-measurement'
        shutil.copytree(ROOT/'examples/research-measurement',project)
        before=cpc.read_project(project);turn=cpc.load_json(project/'turn.json')
        cpc.validate_state(before,project,verify_artifacts=True)
        first=cpc.apply_turn(project,turn,0)
        after=cpc.read_project(project);cpc.validate_state(after,project,verify_artifacts=True)
        replay=cpc.apply_turn(project,turn,0)
        stale=copy.deepcopy(turn);stale['id']='T-stale'
        stale_rejected=False
        try:cpc.apply_turn(project,stale,0)
        except cpc.CPCError:stale_rejected=True
        assert first['status']=='applied'
        assert after['criteria'][0]['status']=='contradicted'
        assert after['criteria'][1]['status']=='unknown'
        assert replay['status']=='already_applied' and stale_rejected
        print(json.dumps({'demo':'synthetic_record_loop','initial_revision':before['revision'],
            'final_revision':after['revision'],'first_apply':first['status'],
            'duplicate_apply':replay['status'],'stale_update_rejected':stale_rejected,
            'calibration_claim':after['criteria'][0]['status'],
            'scientific_conclusion':after['criteria'][1]['status'],
            'next_action':after['handoff']['next_action'],
            'actual_agent_or_lab_run':False,'source_examples_modified':False},ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
