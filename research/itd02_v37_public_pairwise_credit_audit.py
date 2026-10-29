"""V37 frozen prospective F1/F2/F3 public pairwise credit comparison.

All 21 independent learners choose public feedback prospectively; every
counterfactual complete truth table is consumed ONLY by frozen evaluator.
No world label, alternative reward or 36-case table enters the learner.
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
from yggdrasil.itd02_v37_public_pairwise_credit_dev import PublicPairwiseCreditRingDev

PARENT="1862966187560bf09f3accd76c270f7afd171d26"
PREREG="8d765ca11d938b2252cf1dea26c09f43f81d9c35"
WORLDS=("F1","F2","F3")
MODES=("v37_novelty","v37_greedy","v22_shared_novelty",
       "v22_partition_novelty","v35_novelty",
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
 "yggdrasil/itd02_v35_action_conditioned_ring_dev.py":"04c21dc35054e98bc1a366af7c962983e64ef02d",
 "research/itd02_v36_public_identifiability_rank_audit.py":"2ccaab236ca56f347d59e47f756e9e78f9104479",
}
def verify():
    root=Path(__file__).resolve().parents[1]
    git=lambda *a:subprocess.check_output(("git",)+a,cwd=root,text=True).strip()
    for p in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",p,"HEAD")=="",("V37_PREREG_ORDER",p)
    for path,blob in PINS.items():
        assert git("hash-object",path)==blob,("PROTECTED_NATIVE_BLOB_CHANGED",path)
    assert LEARNED_SCALARS==163 and len(CONTEXTS)==12

def reward(world,case):
    """Evaluator-only world law, invisible to learning and action choice."""
    cue,first,second=case
    c=PUBLIC_CUES.index(cue);f=ACTIONS.index(first);a=ACTIONS.index(second)
    r0=target(cue,first,second,nonlinear=True)
    if world=="R0":return r0
    if world=="F1":
        value=r0+(2.60 if (2*c+f+a)%5==0 else -0.90)+0.15*(c-1.5)
    elif world=="F2":
        value=r0+1.60*(1 if (c+2*f)%2==0 else -1)*(1 if a==(c+f)%3 else -0.50)
    elif world=="F3":
        h=int(hashlib.sha256(f"V37-F3-7711:{c}:{f}:{a}".encode()).hexdigest()[:8],16)
        value=r0+(3.15 if h%7 in (0,1) else -0.65)
    else:
        raise ValueError("UNKNOWN_V37_EVALUATOR_WORLD")
    return max(-3.0,min(9.0,value))

def model(mode,source):
    if mode.startswith("rls_"):return RidgeCUSUM(source)
    if mode.startswith("v37_"):return PublicPairwiseCreditRingDev()
    if mode.startswith("v35_"):return LocalActionConditionedRingDev()
    return SharedContextRingDev(mode=("action_partition" if "partition" in mode else "shared"))

def predictions(m,mode,cue,first,*,begin_native):
    if mode.startswith("rls_"):
        return [m.predictions((cue,first,act))[2] for act in ACTIONS]
    if begin_native:begin(m,(cue,first,ACTIONS[0]))
    return m.scores()

def update_selected(m,mode,case,y,*,already_started=False,learning=True):
    if mode.startswith("rls_"):
        s,r,c,t=m.predictions(case)
        if learning:m.observe(case,y,s,r)
        return c
    if not already_started:begin(m,case)
    before=m.score(case[2])
    m.accept_second(case[2],y,learning=learning)
    return before

def snapshot(m,mode,world):
    """All 36 scores first frozen. Only THEN query unavailable action rewards."""
    if mode.startswith("rls_"):
        frozen=copy.deepcopy(m)
        weights_sha=None
        checkpoint_bytes=None
    else:
        checkpoint=m.checkpoint()
        frozen=type(m).restore(checkpoint)
        frozen.start_frozen_evaluation()
        weights_sha=m.parameters_sha256()
        checkpoint_bytes=len(checkpoint)
        assert checkpoint_bytes<=12288
        assert type(m).restore(checkpoint).checkpoint()==checkpoint
    scores=[]
    decisions=[]
    for cue,first in CONTEXTS:
        s=predictions(frozen,mode,cue,first,begin_native=not mode.startswith("rls_"))
        scores.append([round(q,12) for q in s])
        idx=max(range(3),key=lambda j:s[j])
        decisions.append([cue,first,ACTIONS[idx]])
        if not mode.startswith("rls_"):
            frozen.accept_second(ACTIONS[0],0.0,learning=False)
    if not mode.startswith("rls_"):assert m.checkpoint()==checkpoint
    regret=0.0
    error36=0.0
    for (cue,first),s,selected in zip(CONTEXTS,scores,decisions):
        law=[reward(world,(cue,first,a)) for a in ACTIONS]
        regret+=max(law)-law[ACTIONS.index(selected[2])]
        error36+=sum(abs(y-p) for y,p in zip(law,s))
    return {"scores":scores,"actions":decisions,
            "regret":round(regret,12),"error36":round(error36,12),
            "native_weight_sha":weights_sha,
            "checkpoint_bytes":checkpoint_bytes}

def world_arm(world,mode,source,observed):
    m=model(mode,source)
    explorer=PublicProbePolicyDev(mode.rsplit("_",1)[-1])
    source_sha=SharedContextRingDev.restore(source).parameters_sha256()
    events=[]
    for i,case in enumerate(observed):
        observed_y=reward(world,case)
        pred=update_selected(m,mode,case,observed_y)
        explorer.observe_selected(*case)
        events.append({"phase":"base","index":i+1,"selected_public":list(case),
                       "selected_reward":observed_y,
                       "selected_pre_prediction":round(pred,12)})
    after12=snapshot(m,mode,world)
    after12_return=m.margin_updates if mode.startswith("v37_") else None
    probe_events=[]
    for i,index in enumerate(PROBE_INDICES):
        cue,first,_=observed[index]
        scores=predictions(m,mode,cue,first,begin_native=not mode.startswith("rls_"))
        selected=explorer.select(cue,first,scores)
        case=(cue,first,selected)
        # Crucial: reward is generated only AFTER this model's chooser selects.
        actual=reward(world,case)
        pred=update_selected(m,mode,case,actual,
                             already_started=not mode.startswith("rls_"))
        explorer.observe_selected(*case)
        row={"phase":"prospective_probe","index":i+1,
             "selected_public":list(case),"selected_reward":actual,
             "selected_pre_prediction":round(pred,12),
             "selected_abs_error":round(abs(actual-pred),12)}
        events.append(row);probe_events.append(row)
    after15=snapshot(m,mode,world)
    contrastive_updates=(m.margin_updates if mode.startswith("v37_") else None)
    extra_edges=(m.margin_edge_messages if mode.startswith("v37_") else None)
    # This is the already-preregistered original-source return. The learner
    # receives exactly selected SOURCE rewards, without a return-stage signal.
    source_feedback=[]
    for i,case in enumerate(observed):
        y=reward("R0",case)
        pred=update_selected(m,mode,case,y)
        source_feedback.append({"selected_public":list(case),
                                "selected_reward":y,
                                "selected_abs_error":round(abs(y-pred),12)})
    source_return=snapshot(m,mode,"R0")
    if mode.startswith("rls_"):
        assert m.events==27 and m.source.parameters_sha256()==source_sha
        counts={"rls_updates":m.events}
        frozen_identity=True
        cp=None
    else:
        assert m.updates==27 and LEARNED_SCALARS==163
        assert len(m.checkpoint())<=12288
        assert type(m).restore(m.checkpoint()).checkpoint()==m.checkpoint()
        counts={"native_updates":m.updates,
                "source_input_edges":m.forward_input_messages,
                "forward_native_edges":m.forward_output_messages,
                "selected_credit_reverse_edges":m.reverse_credit_messages,
                "extra_pairwise_rival_reverse_edges":extra_edges,
                "extra_pairwise_margin_updates":contrastive_updates}
        frozen_identity=True
        cp=len(m.checkpoint())
    return {"world":world,"mode":mode,"source_sha":source_sha,
        "actual_public_feedback":events,
        "actual_source_return_feedback":source_feedback,
        "snapshot12":after12,"snapshot15":after15,
        "source_return_snapshot":source_return,
        "margin_updates_after_base12":after12_return,
        "margin_updates_after_extra15":contrastive_updates,
        "source_protected":frozen_identity,
        "resource_counters":counts,"final_checkpoint_bytes":cp}

def paired(world,source,events):
    paired_modes=("v22_shared_novelty","v35_novelty","rls_novelty")
    result={}
    for mode in paired_modes:
        m=model(mode,source)
        for event in events:
            case=tuple(event["selected_public"])
            update_selected(m,mode,case,event["selected_reward"])
        result[mode]={"regret15":snapshot(m,mode,world)["regret"],
                      "events":m.events if mode.startswith("rls_") else m.updates}
        assert result[mode]["events"]==15
    return result

def negative(events):
    m=PublicPairwiseCreditRingDev()
    sha=m.parameters_sha256()
    for event in events:
        update_selected(m,"v37_novelty",tuple(event["selected_public"]),
                        event["selected_reward"],learning=False)
    assert m.parameters_sha256()==sha and m.margin_updates==0 and m.updates==0
    cp=m.checkpoint()
    assert PublicPairwiseCreditRingDev.restore(cp).checkpoint()==cp
    return {"unchanged":True,"updates":0,"margin_updates":0,
            "checkpoint_bytes":len(cp)}

def classify(rows):
    lookup={(x["world"],x["mode"]):x for x in rows}
    info={}
    wins=0;self_wins=0;conv_wins=0
    for world in WORLDS:
        a=lookup[(world,"v37_novelty")]
        b=lookup[(world,"v22_shared_novelty")]
        rg=lookup[(world,"rls_greedy")]
        rn=lookup[(world,"rls_novelty")]
        av=a["snapshot15"]["regret"]
        bv=b["snapshot15"]["regret"]
        ar=a["snapshot12"]["regret"]
        r=min(rg["snapshot15"]["regret"],rn["snapshot15"]["regret"])
        win=bv>1e-10 and av<=0.9*bv
        own=ar>1e-10 and av<=0.9*ar
        conv=r>1e-10 and av<=0.9*r
        wins+=int(win);self_wins+=int(own);conv_wins+=int(conv)
        info[world]={"v37_base12":ar,"v37_after15":av,
          "shared_after15":bv,
          "partition_after15":lookup[(world,"v22_partition_novelty")]["snapshot15"]["regret"],
          "v35_after15":lookup[(world,"v35_novelty")]["snapshot15"]["regret"],
          "rls_novelty_after15":rn["snapshot15"]["regret"],
          "rls_greedy_after15":rg["snapshot15"]["regret"],
          "v37_source_return_regret":a["source_return_snapshot"]["regret"],
          "shared_source_return_regret":b["source_return_snapshot"]["regret"],
          "v37_prediction_error36":a["snapshot15"]["error36"],
          "shared_prediction_error36":b["snapshot15"]["error36"],
          "v37_margin_updates_base12":a["margin_updates_after_base12"],
          "v37_margin_updates_after15":a["margin_updates_after_extra15"],
          "v37_beats_shared_by_10pct":win,"v37_self_gain_10pct":own,
          "v37_beats_independent_RLS_10pct":conv,
          "v37_12_action_changes":sum(x[2]!=y[2] for x,y in
                   zip(a["snapshot12"]["actions"],a["snapshot15"]["actions"]))}
    avg=lambda name:sum(info[w][name] for w in WORLDS)/3
    v=avg("v37_after15");shared=avg("shared_after15")
    rlsn=avg("rls_novelty_after15");rlsg=avg("rls_greedy_after15")
    primary=(wins>=2 and self_wins>=2 and shared>1e-10 and v<=0.9*shared)
    secondary=(conv_wins>=2 and rlsn>1e-10 and rlsg>1e-10 and
        v<=0.9*rlsn and v<=0.9*rlsg and
        avg("v37_prediction_error36")<=1.1*avg("shared_prediction_error36") and
        avg("v37_source_return_regret")<=1.1*avg("shared_source_return_regret")+1e-10)
    if not primary:
        label="V37_PUBLIC_MARGIN_DID_NOT_IMPROVE_TRANSFER__NO_SCIENCE"
    elif not secondary:
        label="V37_STRONG_CONTROL_OR_RETENTION_FAILED__NO_SCIENCE"
    else:
        label="V37_BOUNDED_SYNTHETIC_MARGIN_CREDIT_ENGINEERING_POSITIVE__NO_SCIENCE"
    return label,{"family_results":info,"v37_strict_world_shared_wins":wins,
        "v37_self_gain_world_count":self_wins,
        "v37_world_conventional_wins":conv_wins,
        "v37_mean_regret_after15":round(v,12),
        "shared_mean_regret_after15":round(shared,12),
        "rls_novelty_mean_regret_after15":round(rlsn,12),
        "rls_greedy_mean_regret_after15":round(rlsg,12),
        "v37_source_return_mean_regret":round(avg("v37_source_return_regret"),12),
        "shared_source_return_mean_regret":round(avg("shared_source_return_regret"),12),
        "primary_new_world_gain_pass":primary,
        "independent_control_and_retention_pass":secondary}

def main():
    verify()
    t=time.perf_counter();cpu=time.process_time();tracemalloc.start()
    source=train_source()["pretrained_shared"]
    observed,_=selected_map()
    assert len(observed)==12 and len(set(observed))==12
    source_sha=SharedContextRingDev.restore(source).parameters_sha256()
    manifests={w:hashlib.sha256(canonical([
      reward(w,case) for case in itertools.product(PUBLIC_CUES,ACTIONS,ACTIONS)
    ])).hexdigest() for w in WORLDS}
    assert len(set(manifests.values()))==3
    rows=[world_arm(w,mode,source,observed) for w in WORLDS for mode in MODES]
    assert len(rows)==21
    paired_controls={}
    negative_controls={}
    for w in WORLDS:
        primary=next(r for r in rows if r["world"]==w and r["mode"]=="v37_novelty")
        paired_controls[w]=paired(w,source,primary["actual_public_feedback"])
        negative_controls[w]=negative(primary["actual_public_feedback"])
    assert all(r["source_sha"]==source_sha and r["source_protected"] and
        len(r["actual_public_feedback"])==15 and
        len(r["actual_source_return_feedback"])==12 for r in rows)
    assert all(n["unchanged"] and n["updates"]==0 and
               n["margin_updates"]==0 for n in negative_controls.values())
    label,gates=classify(rows)
    sha=hashlib.sha256(canonical({"rows":rows,"paired":paired_controls,
                                 "negative":negative_controls})).hexdigest()
    print(json.dumps({"schema":"ygg.itd02.v37.public_pairwise_local_margin.source_only.v1",
        "classification":label,"source_only":True,"scientific_first_use":False,
        "native_original_mutated":False,"known_unselected_reward_to_model":False,
        "native_action_identities_learned":False,
        "worlds":list(WORLDS),"independent_modes":list(MODES),
        "independent_arm_count":21,
        "pretrained_protected_source_public_updates":576,
        "actual_base_target_public_updates":12,
        "additional_prospective_target_public_updates":3,
        "source_return_selected_public_updates":12,
        "native_trainable_scalars_per_model":163,
        "source_parameters_sha":source_sha,
        "frozen_world_manifest_sha":manifests,
        "predeclared_outcome":gates,
        "canonical_selected_policy_and_credit_sha":sha,
        "arm_summary":[{"world":x["world"],"mode":x["mode"],
            "regret12":x["snapshot12"]["regret"],
            "regret15":x["snapshot15"]["regret"],
            "return_source_regret":x["source_return_snapshot"]["regret"],
            "margin_updates15":x["margin_updates_after_extra15"],
            "chosen_probe_actions":[e["selected_public"] for e in
                                    x["actual_public_feedback"][12:]],
            "edge_counts":x["resource_counters"],
            "checkpoint_bytes":x["final_checkpoint_bytes"]}
            for x in rows],
        "paired_same_actual_selected_feedback":paired_controls,
        "no_learning_controls":negative_controls,
        "host_specific_resources":{
            "wall_seconds":time.perf_counter()-t,
            "cpu_seconds":time.process_time()-cpu,
            "tracemalloc_peak_bytes":tracemalloc.get_traced_memory()[1],
            "retail_pc_performance_witness":False}
    },sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
