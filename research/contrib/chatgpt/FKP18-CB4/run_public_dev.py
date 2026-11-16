"""CB4 preregistered PUBLIC synthetic diagnostic, no owner-held science.

The mediator probe is a paid source-state intervention and discloses its
before/after readout only to the querying arm, not a hidden source law label.
"""
from __future__ import annotations
from hashlib import sha1,sha256
from itertools import combinations
import json,random,statistics,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
for folder in ('FKP18-CB1','FKP18-CB3'):
    candidate=HERE.parent/folder
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0,str(candidate))

import binding, gate_binding
import mediated_source as source
import role_interventions as roles

PINNED={
 'binding.py':'a2c2c64ada23d78ca1872725c31798a57b4f634a',
 'gate_binding.py':'346512769aa2b49a32dd7d5abcd9c3d7c47dd9be',
}

def _verify_sources():
    for module,want in ((binding,PINNED['binding.py']),(gate_binding,PINNED['gate_binding.py'])):
        p=Path(module.__file__);b=p.read_bytes()
        gitblob=sha1(b'blob '+str(len(b)).encode('ascii')+b'\0'+b).hexdigest()
        if gitblob!=want:raise RuntimeError(f'CB4_PINNED_DEPENDENCY_MISMATCH:{p.name}')


def _shuffled_control(public_probes,all_features):
    """Negative: misattribute each intervention response to NEXT source feature."""
    pairs=set(combinations(all_features,2))
    for record in public_probes:
        effect=record.mediator_before != record.mediator_after
        idx=all_features.index(record.target_feature)
        wrong_target=all_features[(idx+1)%4]
        pairs={p for p in pairs if (wrong_target in p)==effect}
    if not pairs:
        return None
    content=min(pairs)
    return content,tuple(x for x in all_features if x not in content)


def _accuracy_on_unseen(fitted,seed):
    return sum(int(fitted.choose_public(state,history)==correct)
               for state,history,correct in source.queries(seed))


def one_world(seed):
    began=time.perf_counter()
    actions=source.training(seed)
    direct=gate_binding.DiscoveredGateBinder()
    conventional=gate_binding.ConventionalExhaustiveFour()
    for public in actions:
        direct.observe_public(public)
        conventional.observe_public(public)
    start=time.process_time();direct.seal();direct_cpu=time.process_time()-start
    start=time.process_time();conventional.seal();conventional_cpu=time.process_time()-start
    original_c=tuple(sorted(direct.learned[:4]))
    original_b=tuple(sorted(conventional.fitted[1]))
    candidate=roles.DirectRoleProbe(original_c)
    control=roles.ConventionalExactPartitions(original_b)
    public_c=source.PublicInterventionSource(seed)
    public_b=source.PublicInterventionSource(seed)
    observations=[]
    while (j:=candidate.next_feature()) is not None:
        event=public_c.probe(j)
        candidate.observe_public(event)
        observations.append(event)
    while (j:=control.next_feature()) is not None:
        event=public_b.probe(j)
        control.observe_public(event)
    cold=roles.DirectRoleProbe.restore(candidate.snapshot())
    if cold.roles!=candidate.roles or cold.snapshot()!=candidate.snapshot():
        raise AssertionError('CB4_COLD_RESULT_MISMATCH')
    if candidate.roles!=control.roles:
        # A real divergence is recorded, not hidden by source labels.
        equal=False
    else:
        equal=True
    true_content,true_gate=source._owner_audit(seed)
    no_probe=(tuple(sorted(direct.learned[:2])),tuple(sorted(direct.learned[2:4])))
    shuffled=_shuffled_control(observations,original_c)
    results={
      'candidate_role':candidate.roles== (true_content,true_gate),
      'conventional_role':control.roles== (true_content,true_gate),
      'no_probe_role':no_probe== (true_content,true_gate),
      'shuffled_role':shuffled== (true_content,true_gate),
      'four_features_direct':original_c==tuple(sorted(true_content+true_gate)),
      'four_features_control':original_b==tuple(sorted(true_content+true_gate)),
      'candidate_unseen_action_correct':_accuracy_on_unseen(direct,seed),
      'conventional_unseen_action_correct':_accuracy_on_unseen(conventional,seed),
    }
    return {
      'seed':seed,
      'learned_four_features_direct':original_c,
      'learned_four_features_conventional':original_b,
      'true_private_content_owner_audit':true_content,
      'true_private_gate_owner_audit':true_gate,
      'predicted_candidate_roles':candidate.roles,
      'predicted_conventional_roles':control.roles,
      'predicted_no_probe_roles':no_probe,
      'predicted_shuffled_roles':shuffled,
      'roles_equal_across_informed_arms':equal,
      'candidate_paid_interventions':public_c.paid,
      'conventional_paid_interventions':public_b.paid,
      'probe_trace_public':[
        [list(r.before_state),r.target_feature,list(r.after_state),
         r.mediator_before,r.mediator_after,r.cost] for r in observations],
      'candidate_proof_sha256':sha256(candidate.snapshot()).hexdigest(),
      'candidate_checkpoint_bytes':len(candidate.snapshot()),
      'CB3_direct_checkpoint_bytes':len(direct.snapshot()),
      'delayed_earned_credits':direct._count,
      'source_public_action_tape_sha256':sha256(json.dumps(
          [[list(r.before),r.action,list(r.after),r.reward] for r in actions],
          separators=(',',':')).encode('ascii')).hexdigest(),
      'outcomes':results,
      'timing_seconds':{'direct_fit_CPU':direct_cpu,'conventional_fit_CPU':conventional_cpu,
                        'world_wall':time.perf_counter()-began}
    }


def study():
    _verify_sources()
    begin=time.perf_counter()
    details=[one_world(seed) for seed in source.WORLDS]
    count=lambda k:sum(int(w['outcomes'][k]) for w in details)
    correct={k:count(k) for k in details[0]['outcomes'] if not k.endswith('_correct')}
    held={k:sum(w['outcomes'][k] for w in details) for k in (
       'candidate_unseen_action_correct','conventional_unseen_action_correct')}
    paired=[int(w['outcomes']['candidate_role'])-int(w['outcomes']['conventional_role']) for w in details]
    rng=random.Random(82490)
    bootstrap=sorted(statistics.mean(rng.choices(paired,k=len(details))) for _ in range(1000))
    paid_candidate=sum(w['candidate_paid_interventions'] for w in details)
    paid_control=sum(w['conventional_paid_interventions'] for w in details)
    checks={
       'candidate_four_feature_set_at_least_30':correct['four_features_direct']>=30,
       'control_four_feature_set_at_least_30':correct['four_features_control']>=30,
       'candidate_roles_at_least_30':correct['candidate_role']>=30,
       'conventional_roles_at_least_30':correct['conventional_role']>=30,
       'role_improvement_over_passive_at_least_0_35':(correct['candidate_role']-correct['no_probe_role'])/32>=.35,
       'shuffled_roles_at_most_0_70':correct['shuffled_role']/32<=.7,
       'candidate_held_action_at_least_0_95':held['candidate_unseen_action_correct']/(32*128)>=.95,
       'conventional_held_action_at_least_0_95':held['conventional_unseen_action_correct']/(32*128)>=.95,
       'paid_max_3_and_matched':all(w['candidate_paid_interventions']<=3 and
         w['candidate_paid_interventions']==w['conventional_paid_interventions'] for w in details),
       'candidate_over_conventional_role_at_least_0_05':statistics.mean(paired)>=.05,
       'paired_bootstrap_lower95_gt_0_01':bootstrap[24]>.01,
    }
    stable=[{k:v for k,v in row.items() if k!='timing_seconds'} for row in details]
    jsonstable=json.dumps(stable,sort_keys=True,separators=(',',':')).encode('ascii')
    return {
     'schema':'yggdrasil.CB4.public-mediated-intervention-result.v1',
     'study':'FKP18-CB4-PUBLIC-MEDIATOR-INTERVENTIONS-FOR-ROLE-IDENTIFIABILITY',
     'classification':('PUBLIC_ROLE_IDENTIFIABLE_BUT_NO_UNIQUE_ADVANTAGE' if all(list(checks.values())[:9])
                       else 'PUBLIC_DEVELOPMENT_FAILED_ONE_OR_MORE_PRIMARY_CHECKS'),
     'scientific_pass':False,
     'worlds':32,'actual_training_actions':32*515,'actual_delayed_credits':32*512,
     'paid_mediator_probes_candidate':paid_candidate,
     'paid_mediator_probes_conventional':paid_control,
     'source_mediator_before_after_measurements_each_arm':2*paid_candidate,
     'held_new_context_scored_actions_each_arm':32*128,
     'correct_worlds':correct,'held_correct_actions':held,
     'candidate_minus_conventional_role_accuracy':statistics.mean(paired),
     'paired_world_bootstrap_95':[bootstrap[24],bootstrap[975]],
     'frozen_predicates':checks,
     'source_owner_readonly_interventions_not_held_science':True,
     'all_world_stable_receipts_sha256':sha256(jsonstable).hexdigest(),
     'total_direct_fit_CPU_seconds':sum(r['timing_seconds']['direct_fit_CPU'] for r in details),
     'total_conventional_fit_CPU_seconds':sum(r['timing_seconds']['conventional_fit_CPU'] for r in details),
     'whole_study_wall_seconds':time.perf_counter()-begin,
     'per_world':stable
    }

if __name__=='__main__':print(json.dumps(study(),sort_keys=True,indent=2))
