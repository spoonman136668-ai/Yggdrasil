"""Frozen active causal knowledge acquisition and finite-prior negative."""
import hashlib
import itertools
import json
import platform
import sys
import time
from knowledge import NumericKnowledge,ACTIONS,PRIOR,features_for
from controls import SymbolicKnowledge,trained_control,trained_joint
from world import World


def run():
    start=time.perf_counter();identified=joint=cold=preserved=actions=agreement=erased=observational=0
    random_cases=random_complete=random_correct=random_covered=random_actions=0
    trained_fits=trained_steps=trained_correct=negative_wrong=negative_faults=0
    state_bytes=[];traces=[];selection_evaluations=observation_joint_correct=observation_joint_covered=0;intervention_histogram={0:0,1:0,2:0}
    timings={'active':0.,'symbolic':0.,'random':0.,'trained':0.}
    for identity in range(64):
        world=World(identity);model=NumericKnowledge();symbolic=SymbolicKnowledge()
        initial=[world.event(u) for u in (0,1)]
        for event in initial:model.observe(event);symbolic.observe(event)
        observational+=not model.complete()
        for u,x,y in itertools.product((0,1),repeat=3):
            p=model.joint(u,x,y);observation_joint_covered+=p is not None
            observation_joint_correct+=p==world.event(u,3,x,y)[3]
        events=list(initial);chosen=[]
        for _ in range(2):
            tick=time.perf_counter();action=model.choose();timings['active']+=time.perf_counter()-tick
            tick=time.perf_counter();other=symbolic.choose();timings['symbolic']+=time.perf_counter()-tick
            if action!=other:raise AssertionError('WSP24_SYMBOLIC_POLICY_DISAGREEMENT')
            agreement+=1
            if action is None:break
            event=world.act(action);events.append(event);chosen.append(action);actions+=1
            tick=time.perf_counter();model.observe(event);timings['active']+=time.perf_counter()-tick
            tick=time.perf_counter();symbolic.observe(event);timings['symbolic']+=time.perf_counter()-tick
        expected=[[((identity>>j)&1) for j in range(3)],[((identity>>(3+j))&1) for j in range(3)]]
        identified+=model.complete() and model.coeff==expected
        selection_evaluations+=model.selection_evaluations;intervention_histogram[len(chosen)]+=1
        raw=model.snapshot();restored=NumericKnowledge.restore(raw)
        if restored.snapshot()!=raw:raise AssertionError('WSP24_COLD_BYTES')
        cold+=1;state_bytes.append(raw)
        tick=time.perf_counter();fitted=trained_control(events);timings['trained']+=time.perf_counter()-tick
        trained_fits+=2;trained_steps+=sum(n for p,n,loss in fitted)
        for u,x,y in itertools.product((0,1),repeat=3):
            target=world.event(u,3,x,y)[3];prediction=restored.joint(u,x,y)
            if prediction!=model.joint(u,x,y) or prediction!=symbolic.joint(u,x,y):raise AssertionError('WSP24_COLD_OR_SYMBOLIC_TRANSFER')
            joint+=prediction==target;trained_correct+=trained_joint(fitted,x,y)==target
            erased+=NumericKnowledge().joint(u,x,y) is None
        # Additional valid do(Y) evidence cannot overwrite Y's acquired rule.
        prior=(model.viable[0][:],model.coeff[0][:],model.known[0][:])
        model.observe(world.event(0,2,0,0))
        preserved+=prior==(model.viable[0],model.coeff[0],model.known[0])
        # Nonlinear alternate world: preserve every acquired actual event,
        # flip only the previously unseen Z-parent combination.
        seen={(e[1],e[2]) for e in events}
        missing=sorted(set(itertools.product((0,1),repeat=2))-seen)
        if len(missing)!=1:raise AssertionError('WSP24_NEGATIVE_UNSEEN_PAIR_CUSTODY')
        pair=missing[0]
        for event in events:
            u,x,y,z,mask=event
            altered=world.event(u,mask,x,y,flip_pair=pair)
            if altered!=event:raise AssertionError('WSP24_COUNTERWORLD_CHANGED_EVIDENCE')
        for u,x,y in itertools.product((0,1),repeat=3):
            negative_wrong+=restored.joint(u,x,y)!=world.event(u,3,x,y,flip_pair=pair)[3]
        restored.observe(world.event(0,3,*pair,flip_pair=pair))
        negative_faults+=restored.fault==1 and all(restored.joint(u,x,y) is None for u,x,y in itertools.product((0,1),repeat=3))
        traces.append({'world':identity,'events':events,'chosen':chosen,'learned_coeff':model.coeff,'checkpoint_sha256':hashlib.sha256(raw).hexdigest(),'missing_pair':pair})
        tick=time.perf_counter()
        for schedule in itertools.permutations(range(8),2):
            control=NumericKnowledge()
            for event in initial:control.observe(event)
            for action_index in schedule:
                if control.complete():break
                control.observe(world.act(ACTIONS[action_index]));random_actions+=1
            random_cases+=1;random_complete+=control.complete()
            for u,x,y in itertools.product((0,1),repeat=3):
                p=control.joint(u,x,y);random_covered+=p is not None
                random_correct+=p==world.event(u,3,x,y)[3]
        timings['random']+=time.perf_counter()-tick
    rate=random_complete/random_cases;gain=identified/64-rate
    supported=(identified==64 and joint==512 and cold==preserved==64 and gain>=.25)
    required=(cold==preserved==64 and erased==512 and observational==64 and trained_fits==128
              and negative_wrong==128 and negative_faults==64 and random_cases==3584)
    report={'schema':'wsp24.active-causal-knowledge.v1','engineering':'PASS' if required else 'FAIL',
            'frozen_hypothesis':'DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE',
            'scientific_classification':'TIE with exact symbolic acquisition; no independent superiority',
            'worlds':64,'identified_worlds':identified,'active_interventions':actions,'max_interventions_per_world':2,
            'active_observation_events':128+actions,'intervention_histogram':intervention_histogram,'selection_candidate_predictions':selection_evaluations,
            'joint_Z_correct_of512':joint,'joint_all_output_bits_correct_of1536':1024+joint,'joint_XY_are_clamped_inputs':True,'cold_restores':cold,'Y_buckets_preserved':preserved,
            'numeric_symbolic_policy_checks':agreement,'observation_only_ambiguous_worlds':observational,
            'observation_only_joint_Z_correct_of512':observation_joint_correct,'observation_only_joint_Z_covered_of512':observation_joint_covered,
            'erasure_abstentions_of512':erased,'random_cases':random_cases,'random_complete':random_complete,
            'random_identification_rate':rate,'active_identification_rate_gain':gain,
            'random_joint_correct':random_correct,'random_joint_total':3584*8,'random_joint_covered':random_covered,'random_actual_interventions':random_actions,
            'trained_bucket_fits_converged':trained_fits,'trained_optimizer_steps':trained_steps,'trained_joint_Z_correct_of512':trained_correct,
            'outside_family_confident_errors_of512':negative_wrong,'outside_family_fault_and_abstention_worlds':negative_faults,
            'resident_task_binary_scalars':37,'static_prior_connections':48,'static_action_descriptor_bits':24,
            'checkpoint_bytes':len(state_bytes[0]),'gradient_steps_candidate':0,
            'checkpoint_digest_sha256':hashlib.sha256(b''.join(state_bytes)).hexdigest(),
            'trace_sha256':hashlib.sha256(json.dumps(traces,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'timings_seconds':timings,'total_seconds':time.perf_counter()-start,
            'environment':{'python':sys.version,'platform':platform.platform()},
            'traces':traces,
            'limitations':'Known affine mechanism class/order and finite hypothesis prior are programmed. Unknown coefficients are learned from real interventions; no true world identity enters the candidate. Information/action maxima matched; capacity and optimizer/selection cost differ. Counterworld negative exposes prior-relative false confidence. No unknown-family discovery, general intelligence, data-free knowledge or total-cost superiority.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report


if __name__=='__main__':run()
