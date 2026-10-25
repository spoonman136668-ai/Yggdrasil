"""R7-C30 fail-closed authentic source/native conventional qualification."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;P=json.loads((HERE/'PREREG.json').read_text())
D=Path(sys.argv[1])
r=[json.loads((D/f'run-{i}.json').read_text()) for i in (1,2)]
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
for k,row in enumerate(r,1):
    assert row['schema']==P['schema']
    assert row['protocol_sha256']==hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest()
    assert row['original_upstream']==P['upstream']
    assert row['original_owner_R10']==P['owner_R10_head'] and row['original_owner_R11']==P['owner_R11_head']
    assert row['public_DEV_episodes']==0 and row['protected_scientific_first_use'] is False
    assert row['original_native_owner_source_modified'] is False
    train,val,preds=(row['training'],row['validation_source'],row['validation_predictions'])
    assert train['role']=='training' and val['role']=='validation'
    assert len(train['episodes'])==len(P['protocol_roles']['training_fit_seeds'])
    assert len(val['episodes'])==len(P['protocol_roles']['validation_fit_seeds'])
    assert row['trained_native_samples']==row['trained_conventional_samples']==train['actual_selected_actions']==1664
    assert row['trained_native_contexts']==row['trained_conventional_contexts']
    assert train['real_pickups']==8 and train['real_opened_doors']==8
    assert val['real_pickups']==4 and val['real_opened_doors']==4
    assert preds['selected_events']==val['actual_selected_actions']==1024
    assert len(preds['actual_preaction_prediction_receipts'])==1024
    assert preds['source_public_context_covered']+preds['source_public_context_abstained']==1024
    assert preds['native_conventional_prediction_disagreements']==0
    assert preds['native_exact_event_predictions']==preds['independent_conventional_exact_event_predictions']
    assert row['full_cold_state']['fresh_python_next_prediction_parity'] is True
    assert row['full_cold_state']['tamper_rejection_both'] is True
    for role,episodes,seeds in (
        ('training',train['episodes'],P['protocol_roles']['training_fit_seeds']),
        ('validation',val['episodes'],P['protocol_roles']['validation_fit_seeds'])):
        for index,e in enumerate(episodes):
            assert e['role']==role and e['fit_seed']==seeds[index]
            assert 0<len(e['actual_source_selected_events'])<=P['protocol_roles']['source_episode_action_cap']
            assert e['actions']==len(e['actual_source_selected_events'])
            assert hashlib.sha256(canon(e['actual_source_selected_events'])).hexdigest()==P['expected_prior_source_prefix_hashes'][str(e['fit_seed'])]
            assert e['prior_C29_source_prefix_sha256']==P['expected_prior_source_prefix_hashes'][str(e['fit_seed'])]
    for kind in ('native','conventional'):
        blob=(D/f'checkpoint-{kind}-run-{k}.json').read_bytes().strip()
        assert hashlib.sha256(blob).hexdigest()==row['full_cold_state'][f'{kind}_checkpoint_sha256']
        assert len(blob)==row['full_cold_state'][f'{kind}_checkpoint_bytes']
        assert 0<len(blob)<180000
    assert row['cpu_training_s']>=0 and row['cpu_validation_s']>=0 and row['peak_python_rss_kib']>0
for fld in ('training','validation_source','validation_predictions','trained_native_samples','trained_conventional_samples',
            'trained_native_contexts','trained_conventional_contexts','full_cold_state',
            'native_checkpoint_sha256','conventional_checkpoint_sha256','scientific_decision'):
    assert r[0][fld]==r[1][fld],('SCIENTIFIC_NONDETERMINISM',fld)
assert all((D/f'checkpoint-{kind}-run-1.json').read_bytes()==(D/f'checkpoint-{kind}-run-2.json').read_bytes() for kind in ('native','conventional'))
v=r[0]['validation_predictions']
out={'schema':'mass.r7c30.authentic-selected-original-source-native-R11-conventional-reconciled.v1',
     'upstream':P['upstream'],'owner_native_R11_blob':P['owner_R11_blob'],
     'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
     'source_native_R11_trained_samples':r[0]['trained_native_samples'],
     'source_training_original_actions':r[0]['training']['actual_selected_actions'],
     'source_validation_original_actions':r[0]['validation_source']['actual_selected_actions'],
     'real_train_pickups':r[0]['training']['real_pickups'],
     'real_train_door_openings':r[0]['training']['real_opened_doors'],
     'real_validation_pickups':r[0]['validation_source']['real_pickups'],
     'real_validation_door_openings':r[0]['validation_source']['real_opened_doors'],
     'public_validation_context_covered':v['source_public_context_covered'],
     'public_validation_context_abstained':v['source_public_context_abstained'],
     'native_validation_modal_exact':v['native_exact_event_predictions'],
     'conventional_validation_modal_exact':v['independent_conventional_exact_event_predictions'],
     'native_conventional_prediction_disagreements':v['native_conventional_prediction_disagreements'],
     'source_genuine_positive_effect_validation':{
       k:{q:n for q,n in v[k].items()} for k in
       ('visible_pickup_events','visible_door_state_change_events','source_goal_reward_events','front_changes')},
     'full_native_conventional_cold_restore_and_tamper_rejection':True,
     'complete_native_checkpoint_bytes':r[0]['full_cold_state']['native_checkpoint_bytes'],
     'complete_conventional_checkpoint_bytes':r[0]['full_cold_state']['conventional_checkpoint_bytes'],
     'native_source_owner_unchanged':True,'protected_first_use':False,
     'DEV_not_consumed':True,'two_complete_original_source_processes_identical':True,
     'scientific_decision':'REAL_ORIGINAL_SOURCE_NATIVE_R11_SELECTED_PUBLIC_EFFECT_LEARNING_PASS_NO_CONVENTIONAL_SUPERIORITY',
     'resource_reference':{k:r[0][k] for k in ('cpu_training_s','cpu_validation_s','peak_python_rss_kib')}}
(D/'comparison.json').write_bytes(canon(out)+b'\n')
print('R7C30_AUTHENTIC_ORIGINAL_SOURCE_DOUBLE_PROCESS=PASS')
print('R7C30_RECONCILED_SHA256='+hashlib.sha256(canon(out)).hexdigest())
print('R7C30_NATIVE_SELECTED_SOURCE_TRAIN_SAMPLES='+str(out['source_native_R11_trained_samples']))
print('R7C30_ORIGINAL_PUBLIC_VALIDATION_CONTEXT_COVERED='+str(out['public_validation_context_covered']))
print('R7C30_NATIVE_VS_MATCHED_CONVENTIONAL_MODAL_EQUALITY=PASS')
print('R7C30_SCIENTIFIC_DECISION='+out['scientific_decision'])
