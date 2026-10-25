"""Strict R7-C28 training-only original-source causal-value reconciler."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.native.itd02.r1.native_policy import canonical
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PREREG.json').read_text());D=Path(sys.argv[1])
native_runs=[json.loads((D/f'native-{i}.json').read_text()) for i in (1,2)]
for row in native_runs:
    assert row['schema']==P['schema'] and row['kind']=='native'
    assert row['source_original_pin']==P['original_source']
    assert row['fit_sha256']==P['frozen_twelve_actual_motor_FIT_sha256']
    assert row['prereg_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
    assert row['new_DEV_episodes_consumed']==0
    assert row['cpu_fit_s']>=0 and row['whole_peak_rss_kib']>0
    for e in row['fit_training_forks']:
        assert e['same_motion_source_first_row_sha256'] and e['factual_info_trace_sha256']
        assert e['family'] in P['fit_training_seed_cohorts'] and e['seed'] in P['fit_training_seed_cohorts'][e['family']]
for key in ('fit_original_action_count','fit_training','fit_training_forks','fit_validation_episodes_consumed','gate'):
    assert native_runs[0].get(key)==native_runs[1].get(key),('NATIVE_FIT_REPRODUCIBILITY_FAIL',key)
native=native_runs[0]
gate=native['gate']
if gate=='FIT_CAUSAL_INFORMATION_NOT_IDENTIFIED':
    assert native['fit_validation_episodes_consumed']==0
    assert native['fit_training']['new_public_blocked']==0 or (
       native['fit_training']['blocked_next_action_changed']==0 or
       (native['fit_training']['blocked_reward_nonzero']==0 and
        native['fit_training']['blocked_goal_nonzero']==0))
    assert not (D/'conventional-1.json').exists() and not (D/'conventional-2.json').exists(),('FAIL_CLOSED_CONVENTIONAL_WAS_STARTED',)
    verdict='NO_GO_FIT_ORIGINAL_SOURCE_CAUSAL_VALUE_UNIDENTIFIED'
    result={'schema':'mass.r7c28.original-source-training-causal-qualification.v1',
            'prereg_sha256':native['prereg_sha256'],
            'fit_sha256':native['fit_sha256'],
            'native_fit_factual_source_causal_measurements':native['fit_training'],
            'native_fit_validation_not_consumed':True,'public_DEV_not_consumed':True,
            'two_whole_native_runs_science_identical':True,
            'conventional_controls_not_run_due_to_source_gate':True,
            'protected_first_use':False,'owner_r3_source_unchanged':True,
            'scientific_decision':verdict}
else:
    assert gate=='FIT_CAUSAL_INFORMATION_IDENTIFIED_TRAIN_ONLY'
    assert native['fit_training']['new_public_blocked']>0
    assert native['fit_training']['blocked_next_action_changed']>0
    assert native['fit_training']['blocked_reward_nonzero']>0 or native['fit_training']['blocked_goal_nonzero']>0
    assert 'learned_value_model' in native
    for key in ('fit_validation','fit_validation_results','fit_validation_original_source_forks','learned_value_model'):
        assert native_runs[0][key]==native_runs[1][key],('NATIVE_FIT_VALIDATION_REPRODUCIBILITY_FAIL',key)
    conv_runs=[json.loads((D/f'conventional-{i}.json').read_text()) for i in (1,2)]
    for r in conv_runs:
        assert r['schema']==P['schema'] and r['kind']=='conventional'
        assert r['source_original_pin']==P['original_source']
        assert r['prereg_sha256']==native['prereg_sha256'] and r['fit_sha256']==native['fit_sha256']
        assert r['new_DEV_episodes_consumed']==0
    for key in ('fit_original_action_count','fit_training','fit_training_forks','fit_validation','fit_validation_results','fit_validation_original_source_forks','learned_value_model'):
        assert conv_runs[0][key]==conv_runs[1][key],('CONVENTIONAL_FIT_REPRODUCIBILITY_FAIL',key)
    conventional=conv_runs[0]
    nv=native['fit_validation_results'];cv=conventional['fit_validation_results']
    if nv['forks']==0 or nv['blocked_forks']==0:
        verdict='NO_GO_FIT_VALIDATION_NO_BLOCKED_INFORMATION_COVERAGE'
    elif nv['learned_vs_blind']<=0:
        verdict='NO_GO_FIT_VALIDATION_LEARNED_INFORMATION_USE_NO_REWARD_GAIN'
    elif cv['learned_vs_blind']>=nv['learned_vs_blind']:
        verdict='NO_NATIVE_SUPERIORITY_EQUAL_SOURCE_CONVENTIONAL_VALUE_LEARNER_TIES_OR_BEATS'
    else:
        verdict='FIT_ONLY_CAUSAL_INFORMATION_LEARNABLE_PUBLIC_DEV_ADMISSION_SEPARATE'
    result={'schema':'mass.r7c28.original-source-training-causal-qualification.v1',
            'prereg_sha256':native['prereg_sha256'],'fit_sha256':native['fit_sha256'],
            'native_fit_training':native['fit_training'],
            'conventional_fit_training':conventional['fit_training'],
            'native_fit_validation':native['fit_validation'],
            'conventional_fit_validation':conventional['fit_validation'],
            'native_learned_fit_reward_comparison':{k:v for k,v in nv.items() if k!='per_fork_evaluated_original_action_receipts'},
            'conventional_learned_fit_reward_comparison':{k:v for k,v in cv.items() if k!='per_fork_evaluated_original_action_receipts'},
            'two_whole_source_runs_per_arm_science_identical':True,
            'public_DEV_not_consumed':True,'protected_first_use':False,
            'owner_r3_source_unchanged':True,'scientific_decision':verdict}
blob=canonical(result)
(D/'comparison.json').write_bytes(blob+b'\n')
print('R7C28_DUPLICATE_FIT_SOURCE_SCIENCE=PASS')
print('R7C28_RECONCILED_SHA256='+hashlib.sha256(blob).hexdigest())
print('R7C28_NATIVE_FIT_BLOCKED_DISCOVERY='+str(native['fit_training']['new_public_blocked']))
print('R7C28_NATIVE_FIT_CAUSAL_NEXT_ACTION_CHANGES='+str(native['fit_training']['blocked_next_action_changed']))
print('R7C28_SCIENTIFIC_DECISION='+verdict)
