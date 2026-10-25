"""R7-C31: reconcile two independent full original DoorKey selected-action FIT trials."""
import hashlib,json,sys
from pathlib import Path
D=Path(sys.argv[1]);P=json.loads((Path(__file__).resolve().parent/'PREREG.json').read_text())
xs=[json.loads((D/f'run-{i}.json').read_text()) for i in (1,2)]
for x in xs:
    assert x['schema']==P['schema'] and x['source_original']==P['original_upstream']
    assert x['owner_R12_source_head']==P['owner_R12_source_commit']
    assert x['protocol_sha256']==hashlib.sha256((Path(__file__).resolve().parent/'PREREG.json').read_bytes()).hexdigest()
    assert x['training_real_source_selected_actions']==P['expected_original_FIT_training_events']
    assert x['test_original_FIT_episodes']==len(P['fresh_original_public_FIT_test_seeds'])
    assert x['new_DEV_episodes_consumed']==0 and x['protected_scientific_first_use'] is False
    assert x['native_checkpoint_bytes']>0 and x['conventional_checkpoint_bytes']>0
    assert x['peak_rss_kib']>0 and x['cpu_fit_s']>=0 and x['cpu_eval_s']>=0
    rec=x['complete_original_source_episode_and_branch_evidence']
    assert len(rec)==len(P['fresh_original_public_FIT_test_seeds'])
    assert [ep['seed'] for ep in rec]==P['fresh_original_public_FIT_test_seeds']
    for ep in rec:
        assert ep['source_actions']>=1
        for f in ep['source_observation_forks']:
            assert f['fit_seed']==ep['seed']
            for arm in ('native','conventional','collector'):
                fork=f[f'source_{arm}_fork']
                if fork['executed']:
                    assert fork['public_action'] is not None and 0<=fork['public_action']<7
                    assert fork['source_before_sha256']==f['actual_public_context_sha256']
                    assert fork['actual_source_event_sha256'] and fork['source_after_sha256']
                else:
                    assert arm!='collector'
                    assert fork['public_action'] is None and fork['source_reward'] is None
    for arm in ('real_native_R12','independent_conventional','original_public_collector'):
        assert x[arm]['selected']+x[arm]['abstained']==sum(x['test_original_FIT_objective_trigger_counts'].values())
for key in ('test_original_FIT_objective_trigger_counts','real_native_R12',
    'independent_conventional','original_public_collector',
    'native_conventional_choice_disagreements',
    'source_native_vs_conventional_real_effect_disagreements',
    'complete_original_source_episode_and_branch_evidence',
    'native_checkpoint_sha256','conventional_checkpoint_sha256',
    'native_checkpoint_bytes','conventional_checkpoint_bytes'):
    assert xs[0][key]==xs[1][key],('ORIGINAL_SOURCE_NONREPRODUCIBLE',key)
x=xs[0]
if x['real_native_R12']['selected']==0:
    status='NO_GO_NATIVE_R12_NEVER_CHOSE_REAL_SOURCE_ACTION'
elif (x['real_native_R12']['real_source_objective_success']==0):
    status='NO_GO_NATIVE_R12_NO_PHYSICALLY_REALIZED_LEARNED_EFFECT'
elif x['native_conventional_choice_disagreements']==0:
    status='QUALIFIED_NATIVE_REAL_SOURCE_EFFECT_ACTION_CONVENTIONAL_EXACT_PARITY'
elif x['real_native_R12']['real_source_objective_success']<=x['independent_conventional']['real_source_objective_success']:
    status='NO_NATIVE_PHYSICAL_OUTCOME_SUPERIORITY_TO_CONVENTIONAL'
else:status='PUBLIC_FIT_NATIVE_DIFFERENCE_NOT_INDEPENDENT_SCIENTIFIC_ADMISSION'
report={'schema':'mass.r7c31.reconciled-original-door-key-physical-R12-FIT.v1',
  'source':P['original_upstream'],'prereg_sha256':x['protocol_sha256'],
  'training_original_effect_samples':1664,
  'FIT_test_fresh_episodes':x['test_original_FIT_episodes'],
  'public_objective_trigger_counts':x['test_original_FIT_objective_trigger_counts'],
  'native_R12_real_source':x['real_native_R12'],
  'equal_information_conventional_real_source':x['independent_conventional'],
  'original_handcoded_collector':x['original_public_collector'],
  'native_vs_conventional_action_mismatch':x['native_conventional_choice_disagreements'],
  'native_vs_conventional_real_effect_mismatch':x['source_native_vs_conventional_real_effect_disagreements'],
  'native_checkpoint_bytes':x['native_checkpoint_bytes'],
  'conventional_checkpoint_bytes':x['conventional_checkpoint_bytes'],
  'original_two_whole_runs_scientifically_identical':True,
  'original_R12_owner_source_unchanged':True,'DEV_consumed':0,
  'protected_first_use':False,'learned_mission_or_goal_understanding_proven':False,
  'decision':status}
b=json.dumps(report,sort_keys=True,separators=(',',':')).encode()
(D/'comparison.json').write_bytes(b+b'\n')
print('R7C31_TWO_INDEPENDENT_ORIGINAL_DOORKEY_PROCESSES=PASS')
print('R7C31_REPORT_SHA256='+hashlib.sha256(b).hexdigest())
print('R7C31_SCIENTIFIC_DECISION='+status)
print('R7C31_NATIVE_REAL_ACTIONS='+json.dumps(x['real_native_R12'],sort_keys=True))
print('R7C31_CONVENTIONAL_REAL_ACTIONS='+json.dumps(x['independent_conventional'],sort_keys=True))
