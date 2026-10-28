"""V33: preregistered prospective new-to-V32 synthetic families, autonomous controls.

Only selected public terminal reward is delivered to models; all 36
alternative action rewards are consulted by the evaluator AFTER policy
freezing. No original native learner, source bank or selector modifications.
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
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev
from yggdrasil.itd02_v30_public_probe_policy_dev import PublicProbePolicyDev
from yggdrasil.itd02_v32_source_surprise_probation_dev import SourceSurpriseProbationDev

PARENT="446af1295c5c318c4c520f467b767d6ed700c9fe"
PREREG="07ea08ada05a09008a055d077ea4edb996f2b237"
WORLDS=("A0","U1","U2","U3")
MODES=("v32_novelty","v32_greedy","v32_round_robin","v32_random",
       "v26_novelty","rls_novelty","rls_greedy")
CONTEXT_INDICES=(0,4,8)
PINS={
 "yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
 "yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
 "yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
 "yggdrasil/itd02_v24_protected_dual_memory_dev.py":"9ef95a28e9060dd79105f51122d527351756a1e0",
 "yggdrasil/itd02_v25_unlabeled_return_dev.py":"f90e5029b121cbfc2e361f9e0941985eb1e69e3d",
 "yggdrasil/itd02_v26_calibrated_return_dev.py":"8a0417d34c6ba94a4eaef33d767da14a4a5c9709",
 "yggdrasil/itd02_v30_public_probe_policy_dev.py":"bcc1f0b4e2ec0fcd8b2af69dfb0e6d4d2ca27a4a",
 "yggdrasil/itd02_v32_source_surprise_probation_dev.py":"9252b554c25bfdc5b6adb733f94b0c3d2b2ec92e",
 "research/itd02_v32_source_surprise_probation_audit.py":"a300f3ff6512d4266131092344a5443f00062511",
}

def pin_source():
    root=Path(__file__).resolve().parents[1]
    git=lambda *x:subprocess.check_output(("git",)+x,cwd=root,text=True).strip()
    for sha in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",sha,"HEAD")=="",("FREEZE_ORDER",sha)
    for path,sha in PINS.items():
        assert git("hash-object",path)==sha,("SOURCE_BLOB_DRIFT",path)

def law(world,case):
    """Evaluator ONLY: not imported in any native/probe chooser module."""
    cue,first,second=case
    c=PUBLIC_CUES.index(cue)
    f=ACTIONS.index(first)
    a=ACTIONS.index(second)
    r=target(*case,nonlinear=True)
    if world=="A0":return r
    if world=="U1":
        candidate=r+1.4*(-1.0 if (c+f)%2 else 1.0)*(-1.0,0.0,1.0)[a]+0.20*(f-1)
    elif world=="U2":
        candidate=r+(2.1 if (c+f+2*a)%3==0 else -1.1)
    elif world=="U3":
        key=f"V33-U3-9093:{c}:{f}:{a}".encode("utf-8")
        h=int(hashlib.sha256(key).hexdigest()[:8],16)
        candidate=r+(3.0 if h%5==0 else -0.40)
    else:raise ValueError("V33_INVALID_OFFLINE_WORLD")
    return max(-3.0,min(9.0,candidate))

def model_scores(m,case):
    begin(m,case)
    return m.scores()

def rls_scores(m,case):
    cue,first,_=case
    return [m.predictions((cue,first,a))[2] for a in ACTIONS]

def chooser_for(mode):
    kind=mode.split("_",1)[1]
    return PublicProbePolicyDev(kind)

def clone_policy(m,mode):
    """Single frozen readout, never train from evaluator-only outcomes."""
    if mode.startswith("v32_"):
        clone=SourceSurpriseProbationDev.restore(m.checkpoint())
    elif mode.startswith("v26_"):
        clone=CalibratedReturnRingDev.restore(m.checkpoint())
    else:
        clone=copy.deepcopy(m)
    if not mode.startswith("rls_"):
        clone.start_frozen_evaluation()
    choices=[]
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        case=(cue,first,ACTIONS[0])
        if mode.startswith("rls_"):
            values=rls_scores(clone,case)
        else:
            values=model_scores(clone,case)
        idx=max(range(3),key=lambda i:values[i])
        a=ACTIONS[idx]
        choices.append([cue,first,a])
        if not mode.startswith("rls_"):
            clone.accept_second(a,0.0,learning=False)
    return choices

def native_head_regret(m,mode,world):
    if mode.startswith("rls_"):return None
    clone=(SourceSurpriseProbationDev.restore(m.checkpoint()) if mode.startswith("v32_")
           else CalibratedReturnRingDev.restore(m.checkpoint()))
    clone.start_frozen_evaluation()
    regrets={"source":0.0,"fast":0.0,"active":0.0}
    actions={"source":[],"fast":[],"active":[]}
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        case=(cue,first,ACTIONS[0])
        begin(clone,case)
        source=[clone.bank.source_score(a) for a in ACTIONS]
        fast=[clone.bank.fast_score(a) for a in ACTIONS]
        active=fast if (clone.use_fast if mode.startswith("v32_") else clone.fast) else source
        actual=[law(world,(cue,first,a)) for a in ACTIONS]
        optimal=max(actual)
        for head,scores in (("source",source),("fast",fast),("active",active)):
            j=max(range(3),key=lambda i:scores[i])
            regrets[head]+=optimal-actual[j]
            actions[head].append([cue,first,ACTIONS[j]])
        clone.accept_second(actions["active"][-1][2],0.0,learning=False)
    return {"regret":{k:round(v,12) for k,v in regrets.items()},
            "actions":actions}

def assess(world,choices):
    detail=[]
    total=0.0
    correct=0
    for cue,first,chosen in choices:
        ys=[law(world,(cue,first,a)) for a in ACTIONS]
        regret=max(ys)-ys[ACTIONS.index(chosen)]
        assert regret>=-1e-10
        total+=regret
        correct+=int(regret<=1e-10)
        detail.append({"public_context":[cue,first],"chosen":chosen,
                       "offline_regret":round(regret,12)})
    return {"regret":round(total,12),"correct_contexts":correct,"detail":detail}

def event(m,mode,case,y):
    """One actually observed selected reward; no offline alternative action reward."""
    if mode.startswith("rls_"):
        sp,rp,cp,tp=m.predictions(case)
        m.observe(case,y,sp,rp)
        return cp
    begin(m,case)
    pred=m.score(case[2])
    m.accept_second(case[2],y)
    return pred

def run(world,mode,source,observed):
    rls=mode.startswith("rls_")
    m=(RidgeCUSUM(source) if rls else
       CalibratedReturnRingDev(source) if mode.startswith("v26_") else
       SourceSurpriseProbationDev(source))
    probe=chooser_for(mode)
    original_source_sha=(m.source.parameters_sha256() if rls else m.bank.source_sha)
    records=[]
    for idx,case in enumerate(observed):
        # Fixed previously selected 12 cases; selection was frozen by V23.
        y=law(world,case)
        pred=event(m,mode,case,y)
        probe.observe_selected(*case)
        records.append({"phase":"target_base","n":idx+1,"selected":list(case),
                        "reward":round(y,12),"pre_selected_score":round(pred,12)})
    snap0=assess(world,clone_policy(m,mode))
    head0=native_head_regret(m,mode,world)
    assert (m.source.parameters_sha256() if rls else m.bank.slow.parameters_sha256())==original_source_sha
    assert (m.events==12 if rls else m.bank.fast.updates==12)
    target_choices=[]
    for i,idx in enumerate(CONTEXT_INDICES):
        cue,first,_old=observed[idx]
        template=(cue,first,ACTIONS[0])
        # Selection is BEFORE evaluator computes actual reward.
        if rls:
            scores=rls_scores(m,template)
        else:
            scores=model_scores(m,template)
        selected=probe.select(cue,first,scores)
        chosen=(cue,first,selected)
        predicted=scores[ACTIONS.index(selected)]
        actual=law(world,chosen)
        if rls:
            sp,rp,cp,tp=m.predictions(chosen)
            m.observe(chosen,actual,sp,rp)
        else:
            m.accept_second(selected,actual)
        probe.observe_selected(*chosen)
        target_choices.append(list(chosen))
        records.append({"phase":"chosen_probe","n":i+1,"selected":list(chosen),
                        "reward":round(actual,12),"pre_selected_score":round(predicted,12),
                        "public_score_error":round(abs(actual-predicted),12)})
        if not rls:
            assert len(m.checkpoint())<=12288
    snap3=assess(world,clone_policy(m,mode))
    head3=native_head_regret(m,mode,world)
    # Return to original source law is hidden from any model/chooser.
    latency=None
    false_fast_last8=0
    return_states=[]
    for i,case in enumerate(observed):
        y=law("A0",case)
        pred=event(m,mode,case,y)
        probe.observe_selected(*case)
        isfast=(m.use_fast if mode.startswith("v32_") else m.fast
                if mode.startswith("v26_") else m.use_ridge)
        return_states.append(isfast)
        if latency is None and not isfast:latency=i+1
        if i>=4 and isfast:false_fast_last8+=1
        records.append({"phase":"unannounced_source_return","n":i+1,
                        "selected":list(case),"reward":round(y,12),
                        "pre_selected_score":round(pred,12),
                        "fast_active_after":bool(isfast)})
        if i==3:
            return4=assess("A0",clone_policy(m,mode))
    return12=assess("A0",clone_policy(m,mode))
    # Frozen controls never receive evaluator-only alternatives.
    final_source_sha=(m.source.parameters_sha256() if rls else m.bank.slow.parameters_sha256())
    assert final_source_sha==original_source_sha
    if not rls:
        cp=m.checkpoint()
        assert len(cp)<=12288
        assert type(m).restore(cp).checkpoint()==cp
        assert m.bank.slow.updates==576 and m.bank.fast.updates==27
        messages={"input":m.bank.fast.forward_input_messages,
                  "output":m.bank.fast.forward_output_messages,
                  "reverse":m.bank.fast.reverse_credit_messages}
    else:
        assert m.events==27
        cp=None
        messages=None
    return {"world":world,"mode":mode,"selected_public_feedback":len(records),
            "prospective_public_records":records,
            "chosen_probe_actions":target_choices,
            "budget0":snap0,"budget3":snap3,
            "native_heads_budget0":head0,"native_heads_budget3":head3,
            "source_return_first4":return4,"source_return_all12":return12,
            "source_return_states":return_states,
            "source_return_latency":latency,
            "false_fast_last8_return":false_fast_last8,
            "original_source_sha":original_source_sha,
            "source_unchanged":True,
            "final_checkpoint_bytes":len(cp) if cp is not None else None,
            "learned_native_scalars":326 if not rls else None,
            "fast_trainable_scalars":163 if not rls else None,
            "native_updates":m.bank.fast.updates if not rls else None,
            "conventional_updates":m.events if rls else None,
            "native_transport_messages":messages}

def classify(rows):
    d={(r["world"],r["mode"]):r for r in rows}
    for world in WORLDS:
        for mode in MODES:
            r=d[(world,mode)]
            assert r["selected_public_feedback"]==27
            assert len(r["chosen_probe_actions"])==3
            assert r["source_unchanged"]
            assert r["native_updates"]==27 if not mode.startswith("rls_") else r["conventional_updates"]==27
            if not mode.startswith("rls_"):
                assert r["final_checkpoint_bytes"]<=12288 and r["learned_native_scalars"]==326
    a=d[("A0","v32_novelty")]
    worlds=("U1","U2","U3")
    target0={w:d[(w,"v32_novelty")]["budget0"]["regret"] for w in worlds}
    target3={w:d[(w,"v32_novelty")]["budget3"]["regret"] for w in worlds}
    rls_best={w:min(d[(w,"rls_novelty")]["budget3"]["regret"],
                    d[(w,"rls_greedy")]["budget3"]["regret"]) for w in worlds}
    individual_gain={w:target3[w]<=0.9*target0[w] for w in worlds}
    mean0=sum(target0.values())/3
    mean3=sum(target3.values())/3
    mean_rls_n=sum(d[(w,"rls_novelty")]["budget3"]["regret"] for w in worlds)/3
    mean_rls_g=sum(d[(w,"rls_greedy")]["budget3"]["regret"] for w in worlds)/3
    at_least_2=sum(individual_gain.values())>=2
    mean_gain=mean3<=0.9*mean0
    return_ok=all(d[(w,"v32_novelty")]["source_return_latency"] is not None
                  and d[(w,"v32_novelty")]["source_return_latency"]<=4 and
                  d[(w,"v32_novelty")]["false_fast_last8_return"]==0 for w in worlds)
    source0=a["budget0"]["regret"];source3=a["budget3"]["regret"]
    source_retention=source3<=1.1*source0+1e-10
    rls_mean_win=mean3<=0.9*mean_rls_n and mean3<=0.9*mean_rls_g
    per_family_wins=sum(target3[w]<=0.9*rls_best[w] for w in worlds)>=2
    policy_changes=sum(d[(w,"v32_novelty")]["budget0"]["detail"]!=
                       d[(w,"v32_novelty")]["budget3"]["detail"] for w in worlds)>=2
    if not(at_least_2 and mean_gain):
        label="V33_UNSEEN_WORLD_LEARNING_GAIN_NOT_ESTABLISHED__NO_SCIENCE"
    elif not(return_ok and source_retention):
        label="V33_RETURN_OR_SOURCE_RETENTION_FAILED__NO_SCIENCE"
    elif not(rls_mean_win and per_family_wins and policy_changes):
        label="V33_HOLDOUT_STRONG_CONTROL_GAIN_NOT_ESTABLISHED__NO_SCIENCE"
    else:
        label="V33_BOUNDED_SYNTHETIC_UNSEEN_FAMILY_ENGINEERING_POSITIVE__NO_SCIENCE"
    return label,{"family_target0_regret":target0,"family_target3_regret":target3,
                  "family_best_independent_rls_budget3_regret":rls_best,
                  "family_10pct_own_gain":individual_gain,
                  "mean_v32_budget0":round(mean0,12),
                  "mean_v32_budget3":round(mean3,12),
                  "mean_rls_novelty_budget3":round(mean_rls_n,12),
                  "mean_rls_greedy_budget3":round(mean_rls_g,12),
                  "two_of_three_own_gain":at_least_2,
                  "mean_10pct_self_gain":mean_gain,
                  "all_three_return_within_four_and_stable":return_ok,
                  "source_A0_regret_budget0":source0,
                  "source_A0_regret_budget3":source3,
                  "source_retention":source_retention,
                  "mean_10pct_better_than_both_RLS":rls_mean_win,
                  "two_of_three_family_RLS_wins":per_family_wins,
                  "two_of_three_active_policies_changed":policy_changes,
                  "individual_return_latencies":{w:d[(w,"v32_novelty")]["source_return_latency"] for w in worlds},
                  "individual_false_fast_last8":{w:d[(w,"v32_novelty")]["false_fast_last8_return"] for w in worlds},
                  "all_budget3_regrets":{w:{m:d[(w,m)]["budget3"]["regret"] for m in MODES} for w in WORLDS}}

def main():
    pin_source()
    t=time.perf_counter();cpu=time.process_time()
    tracemalloc.start()
    source=train_source()["pretrained_shared"]
    observed,mapping=selected_map()
    assert len(observed)==12 and len(set(observed))==12
    assert len(set((c,f) for c,f,a in observed))==12
    manifest={world:[law(world,case) for case in itertools.product(PUBLIC_CUES,ACTIONS,ACTIONS)]
              for world in WORLDS}
    manifest_sha={world:hashlib.sha256(canonical(manifest[world])).hexdigest() for world in WORLDS}
    assert len(set(manifest_sha.values()))==4
    rows=[run(world,mode,source,observed) for world in WORLDS for mode in MODES]
    assert len(rows)==28
    result,gates=classify(rows)
    digest=hashlib.sha256(canonical(rows)).hexdigest()
    print(json.dumps({
        "schema":"ygg.itd02.v33.prospective_unseen_action_control.source_only.v1",
        "classification":result,
        "scientific_first_use":False,"original_world_training":False,
        "unknown_real_world_generalization":False,"native_learned_selector":False,
        "source_only":True,"worlds":list(WORLDS),"independent_chooser_modes":list(MODES),
        "independent_arm_count":28,
        "source_training_selected_rewards":576,
        "base_selected_reward_budget":12,"extra_chooser_budget":3,
        "source_return_selected_rewards":12,"native_stored_learned_scalars":326,
        "native_fast_trainable_scalars":163,
        "frozen_world_manifest_sha256":manifest_sha,
        "predeclared_gates":gates,
        "canonical_all_selected_feedback_and_regret_sha256":digest,
        "rows":[{"world":r["world"],"mode":r["mode"],
                 "probe_selected_public":r["chosen_probe_actions"],
                 "budget0_regret":r["budget0"]["regret"],
                 "budget3_regret":r["budget3"]["regret"],
                 "return_latency":r["source_return_latency"],
                 "wrong_fast_final8":r["false_fast_last8_return"],
                 "source_identity_sha":r["original_source_sha"],
                 "learned_native_scalars":r["learned_native_scalars"],
                 "native_fast_updates":r["native_updates"],
                 "rls_updates":r["conventional_updates"],
                 "checkpoint_bytes":r["final_checkpoint_bytes"],
                 "edge_messages":r["native_transport_messages"]}
                for r in rows],
        "host_only_resources":{
            "wall_seconds":time.perf_counter()-t,
            "cpu_seconds":time.process_time()-cpu,
            "tracemalloc_peak_bytes":tracemalloc.get_traced_memory()[1],
            "not_retail_device_validation":True}
    },sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    main()
