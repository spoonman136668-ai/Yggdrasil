"""R7-C34: repeatable science and actual one-step DoorKey source rescue certificate."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PROTOCOL.json').read_text())
d=Path(sys.argv[1])
r=[json.loads((d/f'result-{k}.json').read_text()) for k in (1,2)]
for x in r:
    assert x['schema']==P['schema']
    assert x['protocol_sha256']==hashlib.sha256((HERE/'PROTOCOL.json').read_bytes()).hexdigest()
    assert x['authentic_original_artifact_sha256']==P['source']['artifactZipSha256']
    assert x['two_original_independent_source_science_runs_match'] is True
    assert x['protected_first_use'] is False and x['old_original_FIT_replays_only'] is True
    assert [e['seed'] for e in x['archived_cases']]==P['originalFITSeeds']
    assert len(x['archived_cases'])==12
    assert x['failed_after_door']==10
    assert x['physically_forced_forward_positive_original_goal']==len(x['original_source_physically_replayed_cases'])
    assert x['total_additional_counterfactual_source_steps']==len(x['original_source_physically_replayed_cases'])
    assert x['source_full_python_peak_rss_kib']>0 and x['source_cpu_seconds']>=0
    for k in x['original_source_physically_replayed_cases']:
        assert k['source_forward_one_step_terminal'] and k['source_forward_one_step_reward']>0
        assert k['source_prefix_verified_selected_actions']==k['first_goal_front_t']+1
        assert k['original_one_step_terminal'] is (k['archive_selected_action']==2)
        assert k['archive_selected_action'] in (1,2)
science_keys=[key for key in r[0] if key not in
    ('source_cpu_seconds','source_full_python_peak_rss_kib')]
assert {k:r[0][k] for k in science_keys}=={k:r[1][k] for k in science_keys},'SOURCE_PROCESS_SCIENCE_MISMATCH'
science={k:r[0][k] for k in science_keys}
data=json.dumps(science,sort_keys=True,separators=(',',':')).encode()
result={'schema':'mass.r7c34.verified-original-source-intervention.v1',
    'science_sha256':hashlib.sha256(data).hexdigest(),
    'independent_source_process_science_same':True,
    'original_failed_goal_visible':science['failed_cases_actually_saw_goal_directly_ahead'],
    'observed_goal_ahead_failure_occurrences':science['failed_after_door_goal_directly_ahead_occurrences'],
    'actual_same_state_goal_rescue_count':science['physically_rescuable_recorded_failed_seed_count'],
    'real_source_replayed_prefix_actions':science['total_actual_original_source_replayed_actions'],
    'new_fit_or_dev_cohorts_used':False,'protected_first_use':False,
    'scientific_disposition':science['scientific_disposition']}
(d/'comparison.json').write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n')
print('R7C34_TWO_INDEPENDENT_ORIGINAL_SOURCE_EXECUTIONS=PASS')
print('R7C34_SCIENCE_SHA256='+result['science_sha256'])
print('R7C34_ORIGINAL_FAILED_GOAL_VISIBLE='+str(result['original_failed_goal_visible']))
print('R7C34_AUTHENTIC_PHYSICAL_GOAL_ONE_STEP_RESCUES='+str(result['actual_same_state_goal_rescue_count']))
print('R7C34_DISPOSITION='+result['scientific_disposition'])
