"""CB5 source-only public developmental study. No private owner-held first use."""
from __future__ import annotations
from hashlib import sha1,sha256
import json,random,statistics,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
for folder in ('FKP18-CB1','FKP18-CB3'):
    directory=HERE.parent/folder
    if directory.exists():sys.path.insert(0,str(directory))
import binding,gate_binding
import public_source as source
import sensor_inference as mechanism

PINNED={'binding.py':'a2c2c64ada23d78ca1872725c31798a57b4f634a',
        'gate_binding.py':'346512769aa2b49a32dd7d5abcd9c3d7c47dd9be'}

def _pin():
    for module,want in ((binding,PINNED['binding.py']),(gate_binding,PINNED['gate_binding.py'])):
        raw=Path(module.__file__).read_bytes()
        actual=sha1(b'blob '+str(len(raw)).encode('ascii')+b'\x00'+raw).hexdigest()
        if actual!=want:raise RuntimeError(f'CB5_PARENT_EXACT_BLOB_MISMATCH:{actual}')

def _canonical_probe(row):
    return [list(x) if type(x) is tuple else x for x in row]

def one_world(seed):
    start=time.perf_counter()
    rows=source.training(seed)
    native=gate_binding.DiscoveredGateBinder()
    symbolic=gate_binding.ConventionalExhaustiveFour()
    for row in rows:
        native.observe_public(row)
        symbolic.observe_public(row)
    native.seal()
    symbolic.seal()
    features_native=tuple(sorted(native.learned[:4]))
    features_symbolic=tuple(sorted(symbolic.fitted[1]))
    a=mechanism.DirectCausalSensor(features_native)
    b=mechanism.ConventionalSensorPosterior(features_symbolic)
    env_a=source.PaidInterventionWorld(seed)
    env_b=source.PaidInterventionWorld(seed)
    upstream_a=[]
    upstream_b=[]
    while (f:=a.next_bit()) is not None:
        probe=env_a.bit_probe(f)
        a.observe_bit(probe)
        upstream_a.append(_canonical_probe(probe))
    while (f:=b.next_bit()) is not None:
        probe=env_b.bit_probe(f)
        b.observe_bit(probe)
        upstream_b.append(_canonical_probe(probe))
    if upstream_a!=upstream_b:
        raise AssertionError('CB5_UPSTREAM_MATCHED_SOURCE_ACTIONS_FAIL')
    no_downstream_guess=a.no_downstream_guess
    raw_a=env_a.baseline_action()
    raw_b=env_b.baseline_action()
    a.observe_baseline(raw_a)
    b.observe_baseline(raw_b)
    if raw_a!=raw_b:
        raise AssertionError('CB5_BASELINE_PAID_ACTION_MISMATCH')
    downstream_a=[_canonical_probe(raw_a)]
    downstream_b=[_canonical_probe(raw_b)]
    while (ch:=a.next_channel()) is not None:
        probe=env_a.sensor_action(ch)
        a.observe_sensor(probe)
        downstream_a.append(_canonical_probe(probe))
    while (ch:=b.next_channel()) is not None:
        probe=env_b.sensor_action(ch)
        b.observe_sensor(probe)
        downstream_b.append(_canonical_probe(probe))
    if downstream_a!=downstream_b or env_a.paid!=env_b.paid:
        raise AssertionError('CB5_SAME_SOURCE_OPPORTUNITY_AND_PAID_ACTION_MISMATCH')
    if a.selected!=b.selected:
        raise AssertionError('CB5_STRONG_CONVENTIONAL_CAUSAL_IDENTIFICATION_DIFFERENCE')
    content,gate,mediator=source._private_audit(seed)
    found_c,found_parents=a.selected
    learned_c,learned_parents=b.selected
    new_query=tuple(source.unseen_queries(seed))
    score_a=sum(native.choose_public(state,history)==target for state,history,target in new_query)
    score_b=sum(symbolic.choose_public(state,history)==target for state,history,target in new_query)
    score_no_update=sum(target==0 for _,_,target in new_query)
    proof=a.snapshot()
    clone=mechanism.DirectCausalSensor.restore(proof)
    if clone.selected!=a.selected or clone.proof()!=proof:
        raise AssertionError('CB5_COLD_SENSOR_CAUSAL_PROOF_MISMATCH')
    tape=sha256(json.dumps([[list(r.before),r.action,list(r.after),r.reward]
                           for r in rows],separators=(',',':')).encode('ascii')).hexdigest()
    return {'seed':seed,
            'public_training_tape_sha256':tape,
            'learned_four_native':features_native,
            'learned_four_symbolic':features_symbolic,
            'source_owner_mediator_channel':mediator,
            'source_owner_content_pair':content,
            'selected_mediator_channel_native':found_c,
            'selected_mediator_channel_conventional':learned_c,
            'learned_source_content_pair_native':found_parents,
            'learned_source_content_pair_conventional':learned_parents,
            'no_downstream_channel_guess':no_downstream_guess[0],
            'wrong_attribution_channel_guess':a.wrong_attribution,
            'paired_paid_actions_each':env_a.paid,
            'direct_lookups_sensor_count':len(a.candidates()),
            'intervention_probe_trace_sha256':sha256(json.dumps(
                [upstream_a,downstream_a],separators=(',',':')).encode('ascii')).hexdigest(),
            'native_cold_checkpoint_sha256':sha256(proof).hexdigest(),
            'native_cold_checkpoint_bytes':len(proof),
            'new_context_correct_of_128':{'direct':score_a,'conventional':score_b,'no_update':score_no_update},
            'whole_world_wall_seconds':time.perf_counter()-start}

def study():
    _pin()
    begin=time.perf_counter()
    rows=[one_world(s) for s in source.SEEDS]
    correct=lambda k:sum(r[k]==r['source_owner_mediator_channel'] for r in rows)
    c_native=correct('selected_mediator_channel_native')
    c_conv=correct('selected_mediator_channel_conventional')
    passive=correct('no_downstream_channel_guess')
    wrong=correct('wrong_attribution_channel_guess')
    content_a=sum(tuple(r['learned_source_content_pair_native'])==tuple(r['source_owner_content_pair']) for r in rows)
    content_b=sum(tuple(r['learned_source_content_pair_conventional'])==tuple(r['source_owner_content_pair']) for r in rows)
    feat_a=sum(set(r['learned_four_native'])==set(r['learned_four_symbolic'])==
               (set(r['source_owner_content_pair']) | set(source._private_audit(r['seed'])[1])) for r in rows)
    accuracy_a=sum(r['new_context_correct_of_128']['direct'] for r in rows)/(32*128)
    accuracy_b=sum(r['new_context_correct_of_128']['conventional'] for r in rows)/(32*128)
    paired=[int(r['selected_mediator_channel_native']==r['source_owner_mediator_channel'])-
            int(r['selected_mediator_channel_conventional']==r['source_owner_mediator_channel']) for r in rows]
    rng=random.Random(82560)
    boot=sorted(statistics.mean(rng.choices(paired,k=32)) for _ in range(1000))
    checks={
        'candidate_four_features_at_least_30':feat_a>=30,
        'conventional_four_features_at_least_30':feat_a>=30,
        'candidate_causal_sensor_at_least_30':c_native>=30,
        'conventional_causal_sensor_at_least_30':c_conv>=30,
        'candidate_source_content_pair_at_least_30':content_a>=30,
        'conventional_content_pair_at_least_30':content_b>=30,
        'passive_sensor_guess_max_12':passive<=12,
        'misattributed_downstream_sensor_guess_max_12':wrong<=12,
        'candidate_public_action_accuracy_0_95':accuracy_a>=.95,
        'conventional_public_action_accuracy_0_95':accuracy_b>=.95,
        'paid_interventions_max_11_and_matched':all(r['paired_paid_actions_each']<=11 for r in rows),
        'direct_minus_strong_sensor_accuracy_min_0_05':statistics.mean(paired)>=.05,
        'paired_bootstrap_lower95_gt_0_01':boot[24]>.01,
    }
    stable=[{k:v for k,v in r.items() if k!='whole_world_wall_seconds'} for r in rows]
    return {
        'schema':'yggdrasil.cb5.blind-mechanism-result.v1',
        'classification':('PUBLIC_BLIND_SENSOR_IDENTIFIABLE_BUT_STRONG_CONTROL_TIE'
                          if all(list(checks.values())[:11]) and not all(list(checks.values())[11:])
                          else 'PUBLIC_CB5_MIXED_OR_NO_GO'),
        'scientific_pass':False,'original_protected_first_use':False,
        'worlds':32,'public_source_train_actions':32*515,
        'earned_delayed_training_credits':32*512,
        'paid_total_each_arm':sum(r['paired_paid_actions_each'] for r in rows),
        'paid_per_world_max':max(r['paired_paid_actions_each'] for r in rows),
        'new_context_source_owner_only_action_scores_per_arm':32*128,
        'mediator_identified_worlds':{'native':c_native,'conventional':c_conv,'passive':passive,'wrong_outcome':wrong},
        'source_content_pair_identified':{'native':content_a,'conventional':content_b},
        'four_features_identified_worlds':feat_a,
        'action_accuracy':{'native':accuracy_a,'conventional':accuracy_b},
        'paired_mediator_delta_mean':statistics.mean(paired),
        'paired_95_interval':[boot[24],boot[975]],
        'frozen_predicates':checks,
        'stable_worlds_sha256':sha256(json.dumps(stable,sort_keys=True,
                 separators=(',',':')).encode('ascii')).hexdigest(),
        'elapsed_seconds':time.perf_counter()-begin,
        'per_world':stable,
    }

if __name__=='__main__':print(json.dumps(study(),indent=2,sort_keys=True))
