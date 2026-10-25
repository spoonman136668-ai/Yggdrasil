"""R7-C29 fail-closed authentic source FIT selected-seven-action reconciliation."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PREREG.json').read_text())
D=Path(sys.argv[1])
R=[json.loads((D/f'fit-{r}.json').read_text()) for r in (1,2)]
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
for row in R:
    assert row['schema']==P['schema'] and row['source']==P['upstream']
    assert row['native_R10_original']==P['owner_R10_source_head']
    assert row['protocol_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
    assert row['DEV_episodes']==0 and row['protected_episodes']==0
    assert row['FIT_only_episodes']==len(P['fit_seeds'])
    assert len(row['episodes'])==len(P['fit_seeds'])
    assert row['peak_python_rss_kib']>0 and row['cpu_total_s']>0
    counts={str(a):0 for a in range(7)}
    picks=opens=goals=0
    for i,ep in enumerate(row['episodes']):
        assert ep['episode_index']==i and ep['fit_original_seed']==P['fit_seeds'][i]
        assert ep['original_actions']==len(ep['selected_actions'])>0
        assert ep['original_actions']<=P['max_original_steps_per_seed']
        assert ep['trace_sha256']==hashlib.sha256(canon(ep['selected_actions'])).hexdigest()
        assert ep['public_adapter_snapshot_bytes']>0 and len(ep['snapshot_sha256'])==64
        for t,event in enumerate(ep['selected_actions']):
            assert event['step']==t
            assert type(event['action']) is int and 0<=event['action']<=6
            assert event['name'] in ('left','right','forward','pickup','drop','toggle','done')
            assert type(event['visible_key_pickup']) is bool and type(event['visible_door_opened']) is bool
            assert type(event['terminated']) is bool and type(event['truncated']) is bool
            assert len(event['before_public_sha256'])==len(event['after_public_sha256'])==64
            assert type(event['source_reward']) is float and -1<=event['source_reward']<=1
            if t:assert ep['selected_actions'][t-1]['after_public_sha256']==event['before_public_sha256']
            if t+1<len(ep['selected_actions']):
                assert not (event['terminated'] or event['truncated'])
            counts[str(event['action'])]+=1
            picks+=int(event['visible_key_pickup'])
            opens+=int(event['visible_door_opened'])
            goals+=int(event['source_reward']>0)
    assert row['selected_actions']==counts
    assert row['total_genuine_source_actions']==sum(counts.values())
    assert row['visible_pickups']==picks and row['visible_opened_doors']==opens
    assert row['actual_goals']==goals
    qualified=all(counts[str(a)]>0 for a in range(7)) and picks>0 and opens>0
    assert row['FIT_public_action_consequence_qualification']==('PASS' if qualified else 'NO_GO')
for key in ('episodes','selected_actions','FIT_only_episodes','total_genuine_source_actions',
            'visible_pickups','visible_opened_doors','actual_goals',
            'FIT_public_action_consequence_qualification'):
    assert R[0][key]==R[1][key],('NONDETERMINISTIC_ORIGINAL_SOURCE',key)
qualified=R[0]['FIT_public_action_consequence_qualification']=='PASS'
out={'schema':'mass.r7c29.original-doorkey-public-fit-reconciled.v1',
     'source':P['upstream'],'original_owner_R10':P['owner_R10_source_head'],
     'fit_only_source_actions':R[0]['total_genuine_source_actions'],
     'selected_action_counts':R[0]['selected_actions'],
     'visible_key_pickup_returns':R[0]['visible_pickups'],
     'visible_door_open_returns':R[0]['visible_opened_doors'],
     'original_goal_rewards':R[0]['actual_goals'],
     'science_reproduced_twice':True,
     'original_R10_owner_unchanged':True,'public_DEV_consumed':False,'protected_first_use':False,
     'native_learned_causal_success_claim':False,
     'scientific_decision':'ORIGINAL_DOORKEY_PUBLIC_SOURCE_ACTIONS_QUALIFIED_ONLY_NOT_NATIVE_LEARNING' if qualified
                            else 'NO_GO_ORIGINAL_FIT_AFFORDANCE_EVENTS_INSUFFICIENT',
     'process_resource':{k:R[0][k] for k in ('cpu_total_s','peak_python_rss_kib')}}
blob=canon(out)
(D/'comparison.json').write_bytes(blob+b'\n')
print('R7C29_TWO_ORIGINAL_SOURCE_PROCESSES=PASS')
print('R7C29_RECONCILED_SHA256='+hashlib.sha256(blob).hexdigest())
print('R7C29_DECISION='+out['scientific_decision'])
print('R7C29_SELECTED_SEVEN_ACTIONS='+json.dumps(out['selected_action_counts'],sort_keys=True))
print('R7C29_VISIBLE_PICKUPS='+str(out['visible_key_pickup_returns']))
print('R7C29_VISIBLE_DOOR_OPENINGS='+str(out['visible_door_open_returns']))
