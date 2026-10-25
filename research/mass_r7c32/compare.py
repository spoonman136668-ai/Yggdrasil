"""Mass R7-C32 fail-closed original source full episode learning comparison."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;P=json.loads((HERE/'PREREG.json').read_text())
D=Path(sys.argv[1])
recs=[json.loads((D/f'run-{i}.json').read_text()) for i in (1,2)]
for r in recs:
    assert r['schema']==P['schema']
    assert r['source_original']==P['original_minigrid']
    assert r['native_owner_head']==P['source_owner_r12_head']
    assert r['protocol_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
    assert r['FIT_original_selected_actions']==P['expected_selected_actual_effect_training_rows']
    assert r['manual_stage_policy_NOT_learned'] and r['hand_written_navigation_collector_NOT_native']
    assert r['source_dev_episodes_consumed']==0 and r['protected_first_use']==False and r['owner_source_changed']==False
    assert set(r['per_arm_actual_source'])==set(P['arms'])
    assert r['fit_cpu_s']>0 and r['test_cpu_s']>0 and r['peak_full_process_rss_kib']>0
    assert len(r['original_episode_and_step_evidence'])==3
    for item in r['original_episode_and_step_evidence']:
        assert item['arm'] in P['arms']
        assert len(item['episodes'])==len(P['fresh_independent_original_FIT_seeds'])
        for ep,raw in zip(item['episodes'],item['complete_original_public_step_records']):
            assert ep['seed']==raw['seed'] and ep['seed'] in P['fresh_independent_original_FIT_seeds']
            assert ep['source_actions']==len(raw['events']) and 0<ep['source_actions']<=P['source_step_cap']
            assert ep['R10_checkpoint_bytes']>0 and ep['R10_checkpoint_sha256']
            assert ep['trace_sha256']==hashlib.sha256(json.dumps(raw['events'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for f in ('source_original','native_owner_head','FIT_original_selected_actions',
          'original_R12_checkpoint_sha256','independent_conventional_checkpoint_sha256',
          'native_checkpoint_bytes','conventional_checkpoint_bytes',
          'per_arm_actual_source','native_vs_other_exact_complete_episode_counts','original_episode_and_step_evidence'):
    assert recs[0][f]==recs[1][f],('COMPLETE_ORIGINAL_SOURCE_SCIENCE_DRIFT',f)
x=recs[0];n=x['per_arm_actual_source']['native_local_effect_delegation']
c=x['per_arm_actual_source']['conventional_equal_learned_effect_delegation']
b=x['per_arm_actual_source']['deterministic_source_public_collector']
if n['delegated_R12_or_conventional_learner_calls']==0:
    verdict='NO_GO_NO_TRUE_NATIVE_DELEGATED_LOCAL_SOURCE_ACTIONS'
elif n['source_goals']<c['source_goals'] or n['source_goals']<b['source_goals']:
    verdict='NO_GO_NATIVE_LOCAL_DELEGATION_GOAL_REGRESSION'
elif n['source_goals']==c['source_goals'] and n['source_steps']==c['source_steps']:
    verdict='ENGINEERING_NATIVE_LOCAL_SEQUENCE_PARITY_NO_ARCHITECTURAL_SUPERIORITY'
else:
    verdict='PUBLIC_FIT_INTEGRATION_RESULT_REQUIRES_FURTHER_SOURCE_AND_CONVENTIONAL_QUALIFICATION'
report={'schema':'mass.r7c32.reconciled-original-source-doorkey-sequence.v1',
        'source_original':P['original_minigrid'],
        'prereg_sha256':x['protocol_sha256'],
        'trained_real_original_effect_samples':x['FIT_original_selected_actions'],
        'two_independent_full_original_source_processes_identical':True,
        'manual_stage_and_navigation_NOT_NATIVE_LEARNING':True,
        'source_DEV_consumed':0,'protected_first_use':False,'original_owner_source_unchanged':True,
        'per_arm':x['per_arm_actual_source'],
        'complete_source_episode_action_equalities':x['native_vs_other_exact_complete_episode_counts'],
        'learned_model_checkpoint_bytes':{'native':x['native_checkpoint_bytes'],
                                           'conventional':x['conventional_checkpoint_bytes']},
        'cpu_reference':{'fit_seconds':x['fit_cpu_s'],'test_seconds':x['test_cpu_s'],
                         'whole_process_rss_kib':x['peak_full_process_rss_kib']},
        'scientific_decision':verdict}
blob=json.dumps(report,sort_keys=True,separators=(',',':')).encode()
(D/'comparison.json').write_bytes(blob+b'\n')
print('R7C32_ORIGINAL_DOORKEY_THREE_ARM_SCIENCE_REPEAT=PASS')
print('R7C32_REPORT_SHA256='+hashlib.sha256(blob).hexdigest())
print('R7C32_SCIENTIFIC_DECISION='+verdict)
for arm,v in report['per_arm'].items():
    print('R7C32_ARM='+arm+' '+json.dumps(v,sort_keys=True))
