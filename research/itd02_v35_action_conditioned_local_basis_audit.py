"""V35 frozen D1/D2/D3 synthetic worlds with independently choosing controls.

All selected public feedback is generated AFTER each learner/chooser commits
to a second action. Offline withheld alternative action rewards used only for
frozen score/regret, never for model or policy training.
"""
import copy
import hashlib
import itertools
import json
import subprocess
import time
import tracemalloc
from pathlib import Path

from research.itd02_v18_intermediate_plasticity_audit import target
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v29_observational_equivalence_audit import selected_map,begin
from research.itd02_v26_calibrated_return_audit import RidgeCUSUM
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES,canonical
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev,LEARNED_SCALARS
from yggdrasil.itd02_v30_public_probe_policy_dev import PublicProbePolicyDev
from yggdrasil.itd02_v35_action_conditioned_ring_dev import LocalActionConditionedRingDev

PARENT="fbfd6a97556be1ccb9263ba12725601924ececdf"
PREREG="44fd6face69012d23898e8af34bb92e0ad672463"
WORLDS=("D1","D2","D3")
MODES=("v35_novelty","v35_greedy","v22_shared_novelty",
       "v22_partition_novelty","v22_shared_random",
       "rls_novelty","rls_greedy")
PROBE_INDICES=(0,4,8)
CONTEXTS=tuple(itertools.product(PUBLIC_CUES,ACTIONS))
PINS={
 "yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
 "yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
 "yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
 "yggdrasil/itd02_v24_protected_dual_memory_dev.py":"9ef95a28e9060dd79105f51122d527351756a1e0",
 "yggdrasil/itd02_v25_unlabeled_return_dev.py":"f90e5029b121cbfc2e361f9e0941985eb1e69e3d",
 "yggdrasil/itd02_v26_calibrated_return_dev.py":"8a0417d34c6ba94a4eaef33d767da14a4a5c9709",
 "yggdrasil/itd02_v30_public_probe_policy_dev.py":"bcc1f0b4e2ec0fcd8b2af69dfb0e6d4d2ca27a4a",
 "yggdrasil/itd02_v32_source_surprise_probation_dev.py":"9252b554c25bfdc5b6adb733f94b0c3d2b2ec92e",
 "research/itd02_v33_unseen_family_independent_controls_audit.py":"3545f88f5689f8d5aa6e5d75b1344d7a7a83a8f2",
 "research/itd02_v34_local_credit_spillover_audit.py":"5991b116c5e24d4d6a2a8b1793becefc040cb85f",
}

def verify():
    root=Path(__file__).resolve().parents[1]
    git=lambda *a:subprocess.check_output(("git",)+a,cwd=root,text=True).strip()
    for sha in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",sha,"HEAD")=="",("PREREG_ORDER",sha)
    for path,sha in PINS.items():
        assert git("hash-object",path)==sha,("PROTECTED_NATIVE_DRIFT",path)
    assert LEARNED_SCALARS==163 and len(CONTEXTS)==12

def reward_law(world,case):
    """Hidden evaluator ONLY, never passed to chooser/learner."""
    cue,first,second=case
    c=PUBLIC_CUES.index(cue)
    f=ACTIONS.index(first)
    a=ACTIONS.index(second)
    source=target(cue,first,second,nonlinear=True)
    if world=="D1":
        val=source+(2.4 if (c+2*f+2*a)%4==0 else -0.8)+0.12*(f-1)
    elif world=="D2":
        val=source+1.75*(1 if (c+f)%2==0 else -1)*(-1,0,1)[a]
    elif world=="D3":
        key=("V35-D3-5107:"+str(c)+":"+str(f)+":"+str(a)).encode()
        h=int(hashlib.sha256(key).hexdigest()[:8],16)
        val=source+(3.2 if h%6==0 else -0.55)
    else:
        raise ValueError("V35_UNKNOWN_EVALUATOR_FAMILY")
    return max(-3.0,min(9.0,val))

def make_model(mode,source):
    if mode.startswith("rls_"):return RidgeCUSUM(source)
    if mode.startswith("v35_"):return LocalActionConditionedRingDev()
    return SharedContextRingDev(mode=("action_partition" if "partition" in mode else "shared"))

def rls_scores(m,cue,first):
    return [m.predictions((cue,first,a))[2] for a in ACTIONS]

def model_scores(m,mode,case):
    cue,first,_=case
    if mode.startswith("rls_"):return rls_scores(m,cue,first)
    begin(m,case)
    return m.scores()

def consume(m,mode,case,y,*,native_started=False,learning=True):
    if mode.startswith("rls_"):
        sp,rp,cp,tp=m.predictions(case)
        if learning:m.observe(case,y,sp,rp)
        return cp
    if not native_started:begin(m,case)
    pred=m.score(case[2])
    m.accept_second(case[2],y,learning=learning)
    return pred

def frozen_snapshot(m,mode,world):
    if mode.startswith("rls_"):
        clone=copy.deepcopy(m)
        read=lambda cue,first:rls_scores(clone,cue,first)
        cp=None;parameters=None
    else:
        cp=m.checkpoint()
        clone=type(m).restore(cp)
        clone.start_frozen_evaluation()
        parameters=m.parameters_sha256()
        def read(cue,first):
            begin(clone,(cue,first,ACTIONS[0]))
            scores=clone.scores()
            clone.accept_second(ACTIONS[0],0.0,learning=False)
            return scores
    rows=[]
    for cue,first in CONTEXTS:
        raw=read(cue,first)
        rows.append([round(x,12) for x in raw])
    # Only now, after all frozen model predictions, ask for unselected
    # counterfactual outcomes for evaluator-only decision regret.
    regrets=0.0
    error=0.0
    choices=[]
    for (cue,first),scores in zip(CONTEXTS,rows):
        out=[reward_law(world,(cue,first,a)) for a in ACTIONS]
        idx=max(range(3),key=lambda j:scores[j])
        regrets+=max(out)-out[idx]
        error+=sum(abs(p-y) for p,y in zip(scores,out))
        choices.append([cue,first,ACTIONS[idx]])
    if not mode.startswith("rls_"):
        assert m.checkpoint()==cp
    return {"regret":round(regrets,12),"absolute_error_36":round(error,12),
            "policy":choices,"frozen_predictions":rows,
            "native_weights_sha":parameters,
            "checkpoint_bytes":len(cp) if cp is not None else None}

def run(mode,world,source,observed):
    m=make_model(mode,source)
    policy=PublicProbePolicyDev(mode.rsplit("_",1)[-1])
    source_sha=SharedContextRingDev.restore(source).parameters_sha256()
    events=[]
    for j,case in enumerate(observed):
        y=reward_law(world,case)
        predicted=consume(m,mode,case,y)
        policy.observe_selected(*case)
        events.append({"phase":"base","event":j+1,
            "selected_public":list(case),"reward":round(y,12),
            "predicted_before":round(predicted,12)})
    initial=frozen_snapshot(m,mode,world)
    probes=[]
    for i,index in enumerate(PROBE_INDICES):
        cue,first,_=observed[index]
        case=(cue,first,ACTIONS[0])
        scores=model_scores(m,mode,case)
        chosen=policy.select(cue,first,scores)
        selected=(cue,first,chosen)
        was_unseen=policy.counts[(cue,first)][ACTIONS.index(chosen)]==0
        # Prospective choice complete before evaluator reveals terminal reward.
        y=reward_law(world,selected)
        pred=consume(m,mode,selected,y,native_started=not mode.startswith("rls_"))
        policy.observe_selected(*selected)
        probe={"phase":"probe","event":i+1,
              "selected_public":list(selected),"previously_unselected":was_unseen,
              "reward":round(y,12),"predicted_before":round(pred,12),
              "selected_absolute_error":round(abs(y-pred),12)}
        probes.append(probe);events.append(probe)
    final=frozen_snapshot(m,mode,world)
    if mode.startswith("rls_"):
        assert m.events==15 and m.source.parameters_sha256()==source_sha
        signals=None;scalars=None;updates=m.events
    else:
        assert m.updates==15 and LEARNED_SCALARS==163
        assert len(m.checkpoint())<=12288
        assert type(m).restore(m.checkpoint()).checkpoint()==m.checkpoint()
        signals={"input":m.forward_input_messages,
                 "output":m.forward_output_messages,
                 "reverse":m.reverse_credit_messages}
        scalars=163;updates=m.updates
    return {"world":world,"mode":mode,"source_sha":source_sha,
        "public_events":events,"probes":probes,
        "budget12":initial,"budget15":final,
        "model_updates":updates,"native_scalars":scalars,
        "edge_signals":signals,
        "original_source_frozen":True}

def paired_controls(world,source,events):
    controls={}
    for mode in ("v22_shared_novelty","v22_partition_novelty","rls_novelty"):
        m=make_model(mode,source)
        initial=None
        for i,ev in enumerate(events):
            case=tuple(ev["selected_public"])
            # Reuse only the primary arm's ALREADY ACTUALLY selected public
            # feedback; no alternative action law from this comparator.
            consume(m,mode,case,ev["reward"])
            if i==11:initial=frozen_snapshot(m,mode,world)
        assert initial is not None
        final=frozen_snapshot(m,mode,world)
        controls[mode]={"budget12":initial,"budget15":final,
                        "updates":m.events if mode.startswith("rls_") else m.updates}
        assert controls[mode]["updates"]==15
    return controls

def nonlearning_control(events):
    m=LocalActionConditionedRingDev()
    original=m.parameters_sha256()
    for ev in events:
        case=tuple(ev["selected_public"])
        consume(m,"v35_novelty",case,ev["reward"],learning=False)
    assert m.parameters_sha256()==original and m.updates==0
    cp=m.checkpoint()
    assert LocalActionConditionedRingDev.restore(cp).checkpoint()==cp
    return {"unchanged":True,"updates":m.updates,
            "initial_parameters_sha":original,"checkpoint_bytes":len(cp)}

def classify(records):
    d={(r["world"],r["mode"]):r for r in records}
    families={}
    wins=0;self_gain=0
    for world in WORLDS:
        v=d[(world,"v35_novelty")]
        shared=d[(world,"v22_shared_novelty")]
        rls_n=d[(world,"rls_novelty")]
        rls_g=d[(world,"rls_greedy")]
        target=v["budget15"]["regret"]
        baseline=shared["budget15"]["regret"]
        is_win=(baseline>1e-10 and target<=0.9*baseline)
        is_self=(v["budget12"]["regret"]>1e-10 and target<=0.9*v["budget12"]["regret"])
        conventional=min(rls_n["budget15"]["regret"],rls_g["budget15"]["regret"])
        beats_conventional=conventional>1e-10 and target<=0.9*conventional
        wins+=int(is_win)
        self_gain+=int(is_self)
        families[world]={
            "v35_novelty_regret12":v["budget12"]["regret"],
            "v35_novelty_regret15":target,
            "v35_greedy_regret15":d[(world,"v35_greedy")]["budget15"]["regret"],
            "v22_shared_novelty_regret15":baseline,
            "v22_partition_novelty_regret15":d[(world,"v22_partition_novelty")]["budget15"]["regret"],
            "v22_shared_random_regret15":d[(world,"v22_shared_random")]["budget15"]["regret"],
            "rls_own_novelty_regret15":rls_n["budget15"]["regret"],
            "rls_own_greedy_regret15":rls_g["budget15"]["regret"],
            "v35_10pct_win_over_shared":is_win,
            "v35_self_gain_10pct":is_self,
            "v35_independent_rls_win_10pct":beats_conventional,
            "v35_error36":v["budget15"]["absolute_error_36"],
            "shared_error36":shared["budget15"]["absolute_error_36"]}
    avg=lambda name:sum(families[w][name] for w in WORLDS)/3
    avg_v35=avg("v35_novelty_regret15")
    avg_shared=avg("v22_shared_novelty_regret15")
    avg_rls_n=avg("rls_own_novelty_regret15")
    avg_rls_g=avg("rls_own_greedy_regret15")
    avg_error_v35=avg("v35_error36")
    avg_error_shared=avg("shared_error36")
    matched_gain=wins>=2 and avg_shared>1e-10 and avg_v35<=0.9*avg_shared
    conv_good=(avg_rls_n>1e-10 and avg_rls_g>1e-10
               and avg_v35<=0.9*avg_rls_n and avg_v35<=0.9*avg_rls_g
               and sum(families[w]["v35_independent_rls_win_10pct"] for w in WORLDS)>=2
               and avg_error_v35<=1.10*avg_error_shared)
    if not matched_gain:
        category="V35_LOCAL_BASIS_TRANSFER_GAIN_NOT_ESTABLISHED__NO_SCIENCE"
    elif not conv_good:
        category="V35_STRONG_CONTROL_OR_PREDICTION_GATES_FAILED__NO_SCIENCE"
    else:
        category="V35_BOUNDED_NEW_LOCAL_BASIS_ENGINEERING_POSITIVE__NO_SCIENCE"
    return category,{"families":families,"candidate_10pct_shared_wins":wins,
        "candidate_10pct_self_gains":self_gain,
        "mean_v35_regret":round(avg_v35,12),
        "mean_v22_shared_regret":round(avg_shared,12),
        "mean_rls_novelty_regret":round(avg_rls_n,12),
        "mean_rls_greedy_regret":round(avg_rls_g,12),
        "mean_v35_error36":round(avg_error_v35,12),
        "mean_shared_error36":round(avg_error_shared,12),
        "matched_gain_gate":matched_gain,"conventional_and_prediction_gate":conv_good}

def main():
    verify()
    t=time.perf_counter();cpu=time.process_time();tracemalloc.start()
    source=train_source()["pretrained_shared"]
    source_sha=SharedContextRingDev.restore(source).parameters_sha256()
    observed,mapping=selected_map()
    assert len(observed)==12 and len(set(observed))==12
    manifests={w:hashlib.sha256(canonical([
        reward_law(w,case) for case in itertools.product(PUBLIC_CUES,ACTIONS,ACTIONS)
    ])).hexdigest() for w in WORLDS}
    assert len(set(manifests.values()))==3
    rows=[run(mode,world,source,observed) for world in WORLDS for mode in MODES]
    paired={w:paired_controls(w,source,
               next(r for r in rows if r["world"]==w and r["mode"]=="v35_novelty")["public_events"])
            for w in WORLDS}
    negatives={w:nonlearning_control(
               next(r for r in rows if r["world"]==w and r["mode"]=="v35_novelty")["public_events"])
            for w in WORLDS}
    assert all(r["source_sha"]==source_sha and len(r["public_events"])==15 and
               r["original_source_frozen"] and r["model_updates"]==15 for r in rows)
    assert all(x["unchanged"] and x["updates"]==0 for x in negatives.values())
    label,gates=classify(rows)
    digest=hashlib.sha256(canonical({"arms":rows,"paired":paired,"negative":negatives})).hexdigest()
    print(json.dumps({
        "schema":"ygg.itd02.v35.fixed_local_action_basis.source_only.v1",
        "classification":label,"source_only":True,"scientific_first_use":False,
        "original_world_training":False,"learned_native_action_identities":False,
        "original_8cell_ring_modified":False,"FORGE_mutated":False,
        "worlds":list(WORLDS),"independent_modes":list(MODES),
        "independent_arms":len(rows),"paired_mode_count_per_world":3,
        "source_pretraining_selected_rewards":576,
        "target_common_selected_rewards":12,"extra_public_probes":3,
        "native_trainable_scalars":163,"source_parameters_sha":source_sha,
        "world_truth_table_sha256":manifests,
        "predeclared_gates":gates,
        "canonical_public_events_predictions_regret_sha256":digest,
        "independent_arm_summary":[{
          "world":r["world"],"mode":r["mode"],
          "probe_actions":[x["selected_public"] for x in r["probes"]],
          "regret12":r["budget12"]["regret"],
          "regret15":r["budget15"]["regret"],
          "error36_15":r["budget15"]["absolute_error_36"],
          "checkpoint_bytes":r["budget15"]["checkpoint_bytes"],
          "native_scalars":r["native_scalars"],
          "edge_messages":r["edge_signals"]}
          for r in rows],
        "paired_action_control_regret15":{
           w:{mode:result["budget15"]["regret"]
              for mode,result in p.items()} for w,p in paired.items()},
        "negative_controls":negatives,
        "host_only_resources":{
          "wall_seconds":time.perf_counter()-t,
          "cpu_seconds":time.process_time()-cpu,
          "tracemalloc_peak_bytes":tracemalloc.get_traced_memory()[1],
          "retail_pc_qualified":False}
    },sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
