"""Independent read-only Mass R7-C33 source-original DoorKey after-door audit.

Only previously consumed original FIT receipts from authenticated C32 are used.
No MiniGrid reset/step, no source-owner modifications, no new DEV or protected first-use.
"""
import collections
import hashlib
import json
import sys
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PROTOCOL.json').read_text())
zippath=Path(sys.argv[1])
outpath=Path(sys.argv[2])
assert hashlib.sha256(zippath.read_bytes()).hexdigest()==P['exact_original_zip_sha256']
with zipfile.ZipFile(zippath) as archive:
    assert archive.testzip() is None
    receipt1=json.loads(archive.read('run-1.json'))
    receipt2=json.loads(archive.read('run-2.json'))
    original_comparison=json.loads(archive.read('comparison.json'))
assert receipt1['source_original']==P['source']
assert receipt1['native_owner_head']==P['unchanged_R12_owner_sha']
assert receipt1['source_dev_episodes_consumed']==0
assert receipt1['protected_first_use'] is False
assert receipt1['owner_source_changed'] is False
for field in (
 'original_episode_and_step_evidence','per_arm_actual_source',
 'FIT_original_selected_actions','original_R12_checkpoint_sha256',
 'independent_conventional_checkpoint_sha256','protocol_sha256'):
    assert receipt1[field]==receipt2[field],('ORIGINAL_C32_SCIENCE_DRIFT',field)
assert receipt1['FIT_original_selected_actions']==1664
assert original_comparison['two_independent_full_original_source_processes_identical']
arms={}
for rec in receipt1['original_episode_and_step_evidence']:
    arm=rec['arm']
    cases=[]
    for record,source in zip(rec['episodes'],rec['complete_original_public_step_records']):
        events=source['events']
        assert record['seed']==source['seed']
        assert record['source_actions']==len(events)
        assert record['trace_sha256']==hashlib.sha256(
            json.dumps(events,sort_keys=True,separators=(',',':')).encode()
        ).hexdigest()
        def first(pred):
            return next((i for i,e in enumerate(events) if pred(e)),None)
        pickup=first(lambda e:bool(e['pickup']))
        opened=first(lambda e:bool(e['opened']))
        goal=first(lambda e:e['r']>0)
        assert sum(bool(e['pickup']) for e in events)==record['key_pickups']
        assert sum(bool(e['opened']) for e in events)==record['door_openings']
        assert (goal is None)==(record['goals']==0)
        assert pickup is not None and opened is not None and pickup<opened
        post=events[opened+1:]
        seen_states={e['public_before_sha256'] for e in post}
        undos=sum(post[i-1]['a'] in (0,1) and post[i]['a'] in (0,1)
                  and post[i-1]['a']!=post[i]['a'] for i in range(1,len(post)))
        acts=collections.Counter(e['a'] for e in post)
        cases.append({
            'seed':record['seed'],'source_actions':len(events),
            'pickup_ordinal':pickup+1,'door_open_ordinal':opened+1,
            'goal_ordinal':goal+1 if goal is not None else None,
            'goal':int(goal is not None),
            'post_open_actions':len(post),
            'post_open_observation_repeats':len(post)-len(seen_states),
            'post_open_turn_reversals':undos,
            'post_open_learned_delegations':sum(e['learned_action'] is not None for e in post),
            'post_open_action_histogram':{str(i):acts[i] for i in range(7)}
        })
    assert len(cases)==12
    summary={
        'episodes':len(cases),
        'goals':sum(c['goal'] for c in cases),
        'key_pickups':sum(c['pickup_ordinal'] is not None for c in cases),
        'doors_opened':sum(c['door_open_ordinal'] is not None for c in cases),
        'door_open_but_goal_failed':sum(c['door_open_ordinal'] is not None and not c['goal'] for c in cases),
        'post_open_actions_failed':sum(c['post_open_actions'] for c in cases if not c['goal']),
        'post_open_public_observation_repeats_failed':sum(c['post_open_observation_repeats'] for c in cases if not c['goal']),
        'post_open_turn_reversals_failed':sum(c['post_open_turn_reversals'] for c in cases if not c['goal']),
        'post_open_learned_delegations_failed':sum(c['post_open_learned_delegations'] for c in cases if not c['goal'])
    }
    assert summary['goals']==receipt1['per_arm_actual_source'][arm]['source_goals']
    assert summary['doors_opened']==receipt1['per_arm_actual_source'][arm]['actual_door_openings']
    arms[arm]={'summary':summary,'per_seed':cases}
native=arms['native_local_effect_delegation']
conventional=arms['conventional_equal_learned_effect_delegation']
assert native['summary']==conventional['summary']
for left,right in zip(native['per_seed'],conventional['per_seed']):
    assert {k:v for k,v in left.items() if k!='seed'}=={k:v for k,v in right.items() if k!='seed'}
    assert left['seed']==right['seed']
assert native['summary']['door_open_but_goal_failed']==10
assert native['summary']['post_open_actions_failed']==6185
assert native['summary']['post_open_public_observation_repeats_failed']==5830
assert native['summary']['post_open_learned_delegations_failed']==0
result={
 'schema':P['schema'],'original_source_zip_sha256':P['exact_original_zip_sha256'],
 'original_source':receipt1['source_original'],
 'original_c32_science_double_process_exact':True,
 'original_native_and_equal_learned_conventional_full_traces_exact':True,
 'retrospective_exposed_FIT_only':True,'new_original_source_steps':0,
 'protected_first_use':False,'original_owner_source_unchanged':True,
 'scientific_decision':'NO_GO_MISSING_LEARNED_POST_DOOR_NAVIGATION_NATIVE_CONVENTIONAL_EXACT_PARITY',
 'arms':arms
}
outpath.write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
print('R7C33_ORIGINAL_SOURCE_CUSTODY=PASS')
print('R7C33_C32_TWO_PROCESS_REPRODUCTION=PASS')
print('R7C33_NATIVE_CONVENTIONAL_AFTER_DOOR_PARITY=PASS')
print('R7C33_RESULT_SHA256='+hashlib.sha256(outpath.read_bytes()).hexdigest())
print('R7C33_NATIVE_SUMMARY='+json.dumps(native['summary'],sort_keys=True))
print('R7C33_SCIENTIFIC_DECISION='+result['scientific_decision'])
