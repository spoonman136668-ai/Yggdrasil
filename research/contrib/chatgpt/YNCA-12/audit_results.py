"""Audit saved YNCA-12 development evidence without replaying scored worlds."""
from pathlib import Path
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parent
EXPECTED={
 'experiment.py':'aa43ffe20dfa994a8a9bde98f4a66ab903ecd22a380517d5b5fe73f3d458c089',
 'experiment_B.py':'7ea099aece2765e14f497b1376eadc34d9682b8d9efc16a9bee15ee320a3124a',
 'result_A.json':'355b13dbf38b6908c3696dce4e9864dbfd72770112c40a3ab516f4c14ff18d5e',
 'result_B.json':'343eb204144de419d81a8ca6c4abd97e67cee95bccc50da1f3e28e98957fa9aa',
}


def audit():
    for name,sha in EXPECTED.items():
        actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        assert actual==sha,(name,actual,sha)
    a=json.loads((ROOT/'result_A.json').read_text())
    b=json.loads((ROOT/'result_B.json').read_text())
    assert a['seed']==171200 and b['seed']==181200
    assert a['candidate_pairs']==300 and a['candidate_tables']==24
    assert a['retained_pairs']==b['memory_pairs']==6
    assert a['held_assignments_per_family']==b['held_assignments_per_family']==384
    assert a['revealed_training_pairs']==b['revealed_training_pairs']==128
    assert not a['claims']['B_used']
    assert not a['development_go'] and not b['development_go']
    assert a['cold_max_abs_error']<=1e-12 and b['cold_prediction_max_abs_error']<=1e-12
    for k in ('native_trained','scientific_pass','deployed'):
        assert a['claims'][k] is False and b['claims'][k] is False
    f=a['metrics']['familiar'];n=a['metrics']['novel']
    ca={
      'familiar_gain_vs_best_non_pair':min(f[x]['brier'] for x in ('SINGLE_BAYES','FREQUENCY','NO_MEMORY','LAST_WORLD'))-f['TOP6_PAIR']['brier']>=.02,
      'within_1_15x_full_pair_brier':f['TOP6_PAIR']['brier']<=1.15*f['FULL_PAIR_BAYES']['brier'],
      'accuracy_within_2pp_full_pair':f['FULL_PAIR_BAYES']['accuracy']-f['TOP6_PAIR']['accuracy']<=.02,
      'novel_operator_harm_le_0_02':n['TOP6_PAIR']['brier']-n['NO_MEMORY']['brier']<=.02,
      'cold_parity_le_1e12':a['cold_max_abs_error']<=1e-12,
      'stored_pairs_le_6':a['retained_pairs']<=6}
    assert ca==a['gates']
    f=b['familiar'];n=b['novel'];c=b['combined_brier']
    for key in c:
        assert abs(c[key]-(f[key]['brier']+n[key]['brier'])/2)<=1e-9
    cb={
      'familiar_gain_vs_nonpair':min(f[x]['brier'] for x in ('SINGLE_BAYES','FREQUENCY','NO_MEMORY'))-f['GATED_TOP6_PAIR']['brier']>=.02,
      'familiar_within_1_15x_gated_full':f['GATED_TOP6_PAIR']['brier']<=1.15*f['GATED_FULL_PAIR']['brier'],
      'familiar_accuracy_loss_le_2pp':f['GATED_FULL_PAIR']['accuracy']-f['GATED_TOP6_PAIR']['accuracy']<=.02,
      'novel_harm_le_0_02':n['GATED_TOP6_PAIR']['brier']-n['NO_MEMORY']['brier']<=.02,
      'combined_gain_vs_nonpair':min(c[x] for x in ('SINGLE_BAYES','FREQUENCY','NO_MEMORY'))-c['GATED_TOP6_PAIR']>=.02,
      'cold_parity_le_1e12':b['cold_prediction_max_abs_error']<=1e-12}
    assert cb==b['gates']
    assert sum(ca.values())==5 and sum(cb.values())==3
    return {'source_hashes_verified':2,'result_hashes_verified':2,'A_gates':ca,'B_gates':cb,'status':'AUDIT_PASS_DEVELOPMENT_NO_GO'}

if __name__=='__main__':
    print(json.dumps(audit(),sort_keys=True,indent=2))
