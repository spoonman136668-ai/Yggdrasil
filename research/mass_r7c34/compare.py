"""Mass R7-C34 original DoorKey FIT science reconciliation, no outcome invention."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PREREG.json').read_text())
D=Path(sys.argv[1])
reports=[json.loads((D/f'run-{i}.json').read_text()) for i in (1,2)]
for x in reports:
    assert x['schema']==P['schema']
    assert x['source']==P['original_source'] and x['owner_r12_sha']==P['owner_r12_commit']
    assert x['prereg_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
    assert len(x['FIT_actual_collector_episodes'])==len(P['training_source_seeds'])
    assert x['FIT_goals']>=0 and x['FIT_positive_reward_rows']>=0
    assert x['new_DEV_or_protected_episodes_consumed']==0
    assert x['peak_rss_kib']>0 and x['fit_cpu_s']>=0 and x['validation_cpu_s']>=0
    for row in x['FIT_actual_collector_episodes']:
        assert row['seed'] in P['training_source_seeds']
        assert row['source_actions']==len(row['events'])
        assert row['trace_sha256']==hashlib.sha256(json.dumps(row['events'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if x['FIT_qualifies_learned_postdoor']:
        assert x['FIT_goals']>0 and x['FIT_positive_reward_rows']>0
        assert set(x['model_states'])=={'native_local','conventional_full'}
        assert set(x['FIT_validation'])=={'collector_baseline','native_local','conventional_full'}
        for arm,v in x['FIT_validation'].items():
            assert v['episodes']==len(P['validation_source_seeds'])
            assert v['opened_doors']<=v['episodes'] and v['actual_goals']<=v['episodes']
            assert v['physical_actions']<=v['episodes']*P['source_episode_cap']
            for ep in v['actual_original_source_episodes']:
                assert ep['seed'] in P['validation_source_seeds']
                assert ep['arm']==arm
                assert ep['source_actions']==len(ep['events'])
                assert ep['trace_sha256']==hashlib.sha256(json.dumps(ep['events'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    else:
        assert x['FIT_goals']==0 or x['FIT_positive_reward_rows']==0
        assert x['FIT_validation_not_consumed']
for key in ('FIT_actual_collector_episodes','FIT_goals','FIT_genuine_postdoor_source_actions',
    'FIT_positive_reward_rows','FIT_positive_training_digest','FIT_qualifies_learned_postdoor'):
    assert reports[0][key]==reports[1][key],('R7C34_FIT_SCIENCE_REPRODUCTION_FAIL',key)
if reports[0]['FIT_qualifies_learned_postdoor']:
    for key in ('model_states','FIT_validation'):
        assert reports[0][key]==reports[1][key],('R7C34_VALIDATION_REPRODUCTION_FAIL',key)
    x=reports[0]
    results=x['FIT_validation']
    n=results['native_local'];c=results['conventional_full'];baseline=results['collector_baseline']
    assert n['postdoor_decisions']>0 and c['postdoor_decisions']>0
    if n['actual_goals']<=baseline['actual_goals'] or n['actual_goals']<=c['actual_goals']:
        decision='NO_GO_NATIVE_LOCAL_POSTDOOR_GOAL_SUPERIORITY_UNPROVEN'
    else:
        decision='FIT_ONLY_POSITIVE_GOAL_SIGNAL_NEEDS_INDEPENDENT_STRONGER_CONTROL'
else:
    decision='NO_GO_ORIGINAL_SOURCE_FIT_LACKS_SUCCESSFUL_POSTDOOR_TRAINING'
result={'schema':'mass.r7c34.original-source-fit-reconciler.v1',
    'source':P['original_source'],'owner_original_unchanged':True,
    'prereg_sha256':reports[0]['prereg_sha256'],
    'two_whole_original_source_processes_science_identical':True,
    'FIT_successful_source_training_episodes':reports[0]['FIT_goals'],
    'FIT_positive_source_action_rows':reports[0]['FIT_positive_reward_rows'],
    'FIT_validation_source_used':reports[0]['FIT_qualifies_learned_postdoor'],
    'original_DEV_and_protected_source_not_consumed':True,
    'source_training_reward_imitation_not_endogenous_goal_discovery':True,
    'native_local_is_research_proxy_not_original_R12':True,
    'scientific_decision':decision}
if reports[0]['FIT_qualifies_learned_postdoor']:
    result['actual_original_source_FIT_validation']={k:{m:v for m,v in val.items() if m!='actual_original_source_episodes'}
      for k,val in reports[0]['FIT_validation'].items()}
    result['model_sizes_and_contexts']=reports[0]['model_states']
raw=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
(D/'comparison.json').write_bytes(raw+b'\n')
print('R7C34_TWO_AUTHENTIC_ORIGINAL_SOURCE_RUNS=PASS')
print('R7C34_COMPARISON_SHA256='+hashlib.sha256(raw).hexdigest())
print('R7C34_SCIENTIFIC_DECISION='+decision)
print('R7C34_FACTUAL_FIT_VALIDATION='+json.dumps(result.get('actual_original_source_FIT_validation',{}),sort_keys=True))
