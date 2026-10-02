from __future__ import annotations
import copy
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/cybernetic-project-control'
spec=importlib.util.spec_from_file_location('cpc_reference',SKILL/'scripts/cpc.py')
cpc=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(cpc)

def fixture(root: Path):
    (root/'.project-control/receipts').mkdir(parents=True)
    state=cpc.load_json(SKILL/'assets/state.template.json')
    state['objective']['statement']='Synthetic test objective'
    state['criteria'][0]['description']='Synthetic measurable criterion'
    state['as_of']='2026-10-02T09:00:00Z'
    state['questions']=[{'id':'Q-1','description':'Is the synthetic criterion supported?',
        'blocks':['C-1'],'status':'open','evidence_ids':[]}]
    save(root,state)
    return state

def save(root: Path,state):
    (root/'.project-control/state.json').write_bytes(cpc.canonical_bytes(state))

def turn(state):
    result=cpc.load_json(SKILL/'assets/turn.template.json')
    result.update(id='T-1',project_id=state['project_id'],base_revision=state['revision'],
        objective_version=state['objective']['version'],actor=state['control']['controller_id'],
        created_at='2026-10-02T10:00:00Z',mode='observe',action_class='inspect')
    result['result']={'status':'reported','summary':'Synthetic observation record; not a real agent run.','evidence_ids':[]}
    result['target_questions']=['Q-1']
    return result

def evidence(root: Path, eid='E-1', *, relation='supports', depends=None):
    path=root/'artifacts'/f'{eid}.txt';path.parent.mkdir(exist_ok=True)
    path.write_text(f'Synthetic evidence {eid}\n',encoding='utf-8')
    return {'id':eid,'summary':f'Synthetic evidence {eid}',
        'observed_at':'2026-10-02T08:00:00Z','objective_version':1,
        'targets':['C-1','Q-1'],'relation':relation,'validity':'current','validity_reason':None,
        'review_status':'reviewed','reviewer':'test-fixture',
        'review_note':'Known synthetic content only; not independent scientific verification.',
        'limitations':['Synthetic test only.'],
        'provenance':{'producer':'fixture','run_ref':'test-run','input_ref':'test-input'},
        'artifacts':[{'path':f'artifacts/{eid}.txt','sha256':cpc.hash_file(path)}],
        'depends_on':depends or []}
