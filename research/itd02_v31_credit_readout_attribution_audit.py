"""V31 source-only native credit response versus readout attribution audit.

No new learner or selected policy. Offline counterfactual reward queries occur
ONLY after frozen decisions. Original source/fast banks stay untouched except
legal actual selected feedback to fast; original native V22 source is pinned.
"""
import copy
import hashlib
import itertools
import json
import subprocess
import time
import tracemalloc
from pathlib import Path

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v29_observational_equivalence_audit import selected_map, law, begin
from research.itd02_v26_calibrated_return_audit import RidgeCUSUM
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES, canonical
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev
from yggdrasil.itd02_v30_public_probe_policy_dev import PublicProbePolicyDev

PARENT="d3e75f7e9bb223bab5818ed1b741101b505827ec"
PREREG="823669ec0cd68934581dde9ea8c3e12adad0e2c7"
BUDGETS=(0,1,3)
WORLDS=("A","B","B0")
PROBE_INDICES=(0,4,8)
HEADS=("active","fast","source")
PINS={
 "yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
 "yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
 "yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
 "yggdrasil/itd02_v24_protected_dual_memory_dev.py":"9ef95a28e9060dd79105f51122d527351756a1e0",
 "yggdrasil/itd02_v25_unlabeled_return_dev.py":"f90e5029b121cbfc2e361f9e0941985eb1e69e3d",
 "yggdrasil/itd02_v26_calibrated_return_dev.py":"8a0417d34c6ba94a4eaef33d767da14a4a5c9709",
 "yggdrasil/itd02_v30_public_probe_policy_dev.py":"bcc1f0b4e2ec0fcd8b2af69dfb0e6d4d2ca27a4a",
 "research/itd02_v29_observational_equivalence_audit.py":"86e30048b336b20d15a7a2c76d87d48d205c023f",
 "research/itd02_v30_budgeted_action_exploration_audit.py":"2991bdcf8e2c6878691548a0d3e9d5521b9eb85c",
}


def verify():
    root=Path(__file__).resolve().parents[1]
    git=lambda *args:subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for sha in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",sha,"HEAD")=="",("FROZEN_CHRONOLOGY",sha)
    for path,blob in PINS.items():
        assert git("hash-object",path)==blob,("PROTECTED_SOURCE_DRIFT",path)


def readout(model, world, mapping):
    """Frozen post-training evaluator chooses action from each EXISTING head."""
    cp=model.checkpoint()
    clone=CalibratedReturnRingDev.restore(cp)
    clone.start_frozen_evaluation()
    decisions={h:[] for h in HEADS}
    regrets={h:0.0 for h in HEADS}
    traces=[]
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        begin(clone,(cue,first,ACTIONS[0]))
        scores={
            "active":clone.scores(),
            "fast":clone.bank.fast.scores(),
            "source":clone.bank.slow.scores(),
        }
        choices={h:ACTIONS[max(range(3),key=lambda i:scores[h][i])]
                 for h in HEADS}
        for h in HEADS:
            decisions[h].append([cue,first,choices[h]])
        # Only NOW may evaluator inspect unselected reward counterfactuals.
        outcomes=[law(world,(cue,first,a),mapping) for a in ACTIONS]
        best=max(outcomes)
        for h in HEADS:
            regrets[h]+=best-outcomes[ACTIONS.index(choices[h])]
        traces.append({"context":[cue,first],
                       "scores":{h:[round(x,12) for x in scores[h]] for h in HEADS},
                       "choices":choices,
                       "ranking_margins":{h:round(sorted(scores[h])[-1]-sorted(scores[h])[-2],12)
                                          for h in HEADS}})
        clone.accept_second(choices["active"],0.0,learning=False)
    assert model.checkpoint()==cp, "READOUT_LEAKED_BACK_INTO_LIVE_MODEL"
    return {"regret":{h:round(regrets[h],12) for h in HEADS},
            "actions":decisions,"trace":traces,
            "fast_active_disagreements":sum(
                a[2]!=b[2] for a,b in zip(decisions["fast"],decisions["active"]))}


def conventional_readout(rls,world,mapping):
    clone=copy.deepcopy(rls)
    choices=[]
    total=0.0
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        scores=[clone.predictions((cue,first,a))[2] for a in ACTIONS]
        best_idx=max(range(3),key=lambda i:scores[i])
        action=ACTIONS[best_idx]
        values=[law(world,(cue,first,a),mapping) for a in ACTIONS]
        total+=max(values)-values[best_idx]
        choices.append([cue,first,action])
    return {"regret":round(total,12),"actions":choices}


def selected_base(source,observed,mapping,world):
    model=CalibratedReturnRingDev(source)
    rls=RidgeCUSUM(source)
    explorer=PublicProbePolicyDev("novelty")
    public=[]
    source_sha=model.bank.source_sha
    for i,case in enumerate(observed):
        begin(model,case)
        selected_prediction=model.score(case[2])
        sp,rp,cp,tp=rls.predictions(case)
        outcome=law(world,case,mapping)
        model.accept_second(case[2],outcome)
        rls.observe(case,outcome,sp,rp)
        explorer.observe_selected(case[0],case[1],case[2])
        public.append({"i":i+1,"public":list(case),"selected_reward":round(outcome,12),
                       "native_pre":round(selected_prediction,12),
                       "rls_pre":round(cp,12)})
    assert model.bank.slow.parameters_sha256()==source_sha
    assert model.bank.slow.updates==576 and model.bank.fast.updates==12
    assert CalibratedReturnRingDev.restore(model.checkpoint()).checkpoint()==model.checkpoint()
    return model,rls,explorer,public


def arm(source,observed,mapping,world,budget):
    model,rls,explorer,base=selected_base(source,observed,mapping,world)
    protected_sha=model.bank.source_sha
    baseline_fast_sha=model.bank.fast.parameters_sha256()
    baseline_selected_updates=model.bank.fast.updates
    nolearn=CalibratedReturnRingDev.restore(model.checkpoint())
    initial_readout=readout(model,world,mapping)
    initial_rls=conventional_readout(rls,world,mapping)
    probes=[]
    snapshots=[]
    for i in range(budget):
        cue,first,_=observed[PROBE_INDICES[i]]
        begin(model,(cue,first,ACTIONS[0]))
        active_scores=model.scores()
        fast_scores=model.bank.fast.scores()
        source_scores=model.bank.slow.scores()
        selected=explorer.select(cue,first,active_scores)
        assert selected in ACTIONS
        unobserved=explorer.counts[(cue,first)][ACTIONS.index(selected)]==0
        case=(cue,first,selected)
        prior_sha=model.bank.fast.parameters_sha256()
        pre_native=active_scores[ACTIONS.index(selected)]
        pre_fast=fast_scores[ACTIONS.index(selected)]
        pre_source=source_scores[ACTIONS.index(selected)]
        # Legitimate, causally ordered prospective public action/reward:
        # the evaluator computes the reward only AFTER the policy selects.
        outcome=law(world,case,mapping)
        sp,rp,conventional_pre,tp=rls.predictions(case)
        model.accept_second(selected,outcome)
        rls.observe(case,outcome,sp,rp)
        explorer.observe_selected(cue,first,selected)
        # The deliberately nonlearning control gets identical observed actions
        # and feedback but may never change its weight or selector state.
        begin(nolearn,case)
        nolearn.accept_second(selected,outcome,learning=False)
        assert nolearn.bank.fast.parameters_sha256()==baseline_fast_sha
        assert nolearn.bank.fast.updates==baseline_selected_updates
        assert model.bank.slow.parameters_sha256()==protected_sha
        assert model.bank.fast.updates==baseline_selected_updates+i+1
        assert len(model.checkpoint())<=12288
        assert CalibratedReturnRingDev.restore(model.checkpoint()).checkpoint()==model.checkpoint()
        after_sha=model.bank.fast.parameters_sha256()
        probes.append({
          "probe":i+1,"actual_public":[cue,first,selected],
          "new_action":bool(unobserved),
          "reward_observed":round(outcome,12),
          "pre_prediction":{"active":round(pre_native,12),
                            "fast":round(pre_fast,12),
                            "source":round(pre_source,12),
                            "rls":round(conventional_pre,12)},
          "pre_fast_sha":prior_sha,"post_fast_sha":after_sha,
          "fast_parameter_change":prior_sha!=after_sha,
          "selected_abs_pre_error":round(abs(pre_native-outcome),12),
          "active_fast_after":model.fast,
          "public_gate_evidence":[round(x,12) for x in model.evidence],
          "local_credit_messages":model.bank.fast.reverse_credit_messages,
        })
        snapshots.append({"probe":i+1,"readout":readout(model,world,mapping),
                          "matched_rls":conventional_readout(rls,world,mapping)})
    assert model.bank.slow.parameters_sha256()==protected_sha
    assert nolearn.bank.fast.parameters_sha256()==baseline_fast_sha
    assert nolearn.bank.slow.parameters_sha256()==protected_sha
    assert CalibratedReturnRingDev.restore(nolearn.checkpoint()).checkpoint()==nolearn.checkpoint()
    final=readout(model,world,mapping)
    final_rls=conventional_readout(rls,world,mapping)
    signals={"input":model.bank.fast.forward_input_messages,
             "output":model.bank.fast.forward_output_messages,
             "reverse":model.bank.fast.reverse_credit_messages}
    return {"world_evaluator_only":world,"budget":budget,
        "common_selected_public":base,
        "probe_public":probes,
        "probe_frozen_readouts":snapshots,
        "first_readout":initial_readout,
        "final_readout":final,
        "first_matched_rls":initial_rls,
        "final_matched_rls":final_rls,
        "base_fast_sha":baseline_fast_sha,
        "final_fast_sha":model.bank.fast.parameters_sha256(),
        "fast_parameter_changed":model.bank.fast.parameters_sha256()!=baseline_fast_sha,
        "source_sha":protected_sha,"source_frozen":True,
        "fast_updates":model.bank.fast.updates,"expected_fast_updates":12+budget,
        "nonlearning_control_fast_unchanged":True,
        "checkpoint_cold_restore":True,"checkpoint_bytes":len(model.checkpoint()),
        "local_messages":signals,
        "final_active_selector_fast":model.fast,
        "stored_native_scalars":326,
    }


def classify(rows):
    lookup={(r["world_evaluator_only"],r["budget"]):r for r in rows}
    for b in BUDGETS:
        assert lookup[("A",b)]["common_selected_public"]==lookup[("B",b)]["common_selected_public"]==lookup[("B0",b)]["common_selected_public"]
        assert lookup[("A",b)]["first_readout"]["actions"]==lookup[("B",b)]["first_readout"]["actions"]==lookup[("B0",b)]["first_readout"]["actions"]
        for key in ("probe_public","final_readout","final_matched_rls","base_fast_sha","final_fast_sha"):
            assert lookup[("A",b)][key]==lookup[("B0",b)][key],("B0_IDENTITY_FAILED",key,b)
    b0=lookup[("B",0)];b3=lookup[("B",3)]
    active0=b0["final_readout"]["regret"]["active"]
    active3=b3["final_readout"]["regret"]["active"]
    fast0=b0["final_readout"]["regret"]["fast"]
    fast3=b3["final_readout"]["regret"]["fast"]
    native_actions_changed=b0["final_readout"]["actions"]["active"]!=b3["final_readout"]["actions"]["active"]
    fast_actions_changed=b0["final_readout"]["actions"]["fast"]!=b3["final_readout"]["actions"]["fast"]
    source0=lookup[("A",0)]["final_readout"]["regret"]["active"]
    source3=lookup[("A",3)]["final_readout"]["regret"]["active"]
    rls3=b3["final_matched_rls"]["regret"]
    if not b3["fast_parameter_changed"]:
        category="V31_NO_FAST_PARAMETER_RESPONSE__NO_SCIENCE"
    elif not fast_actions_changed and abs(fast3-fast0)<=1e-10:
        category="V31_FAST_UPDATE_WITHOUT_DECISION_SHIFT__NO_SCIENCE"
    elif fast3+1e-10<fast0 and active3+1e-10>=active0 and not b3["final_active_selector_fast"]:
        category="V31_READOUT_MASKS_FAST_IMPROVEMENT__NO_SCIENCE"
    elif not native_actions_changed or active3>0.9*rls3 or source3>1.1*source0+1e-10:
        category="V31_NATIVE_DECISION_GAIN_NOT_QUALIFIED__NO_SCIENCE"
    else:
        category="V31_BOUNDED_SYNTHETIC_CREDIT_READOUT_ENGINEERING_POSITIVE__NO_SCIENCE"
    return category,{"B_active_regret_0":active0,"B_active_regret_3":active3,
        "B_fast_regret_0":fast0,"B_fast_regret_3":fast3,
        "B_source_regret_0":b0["final_readout"]["regret"]["source"],
        "B_source_regret_3":b3["final_readout"]["regret"]["source"],
        "A_active_regret_0":source0,"A_active_regret_3":source3,
        "B_conventional_rls_regret_3":rls3,
        "B_fast_weights_changed":b3["fast_parameter_changed"],
        "B_fast_policy_changed":fast_actions_changed,
        "B_active_policy_changed":native_actions_changed,
        "B_selector_fast_after_three":b3["final_active_selector_fast"],
        "B_active_fast_disagreements_after_three":b3["final_readout"]["fast_active_disagreements"]}


def verify():
    root=Path(__file__).resolve().parents[1]
    git=lambda *args:subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for pin in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",pin,"HEAD")=="",("CHRONOLOGY",pin)
    for path,sha in PINS.items():
        assert git("hash-object",path)==sha,("SOURCE_DRIFT",path)


def main():
    verify()
    start=time.perf_counter();cpu=time.process_time()
    tracemalloc.start()
    trained=train_source()["pretrained_shared"]
    observed,mapping=selected_map()
    assert len(observed)==12
    rows=[arm(trained,observed,mapping,world,budget)
          for world in WORLDS for budget in BUDGETS]
    assert len(rows)==9
    assert all(r["nonlearning_control_fast_unchanged"] and r["source_frozen"]
               and r["checkpoint_cold_restore"] and r["checkpoint_bytes"]<=12288
               and r["fast_updates"]==r["expected_fast_updates"]
               and r["stored_native_scalars"]==326 for r in rows)
    label,summary=classify(rows)
    digest=hashlib.sha256(canonical(rows)).hexdigest()
    print(json.dumps({
       "schema":"ygg.itd02.v31.native_credit_readout_attribution.source_only.v1",
       "classification":label,"source_only":True,
       "scientific_first_use":False,"original_world_training":False,
       "new_native_learning_architecture":False,"source_memory_mutated":False,
       "worlds":list(WORLDS),"budgets":list(BUDGETS),"independent_arms":len(rows),
       "source_pretraining_selected_rewards":576,"common_public_selected_rewards":12,
       "native_learned_scalars":326,"target_adaptive_scalars":163,
       "matched_RLS_full_matrix_control":True,"nonlearning_public_feedback_control":True,
       "source_checkpoint_cold_restore":True,
       "summary":summary,
       "rows":[{k:v for k,v in r.items() if k not in ("common_selected_public",
            "probe_frozen_readouts","first_readout","final_readout")}
             for r in rows],
       "canonical_full_credit_and_policy_sha256":digest,
       "host_resource_only":{"cpu_seconds":time.process_time()-cpu,
            "wall_seconds":time.perf_counter()-start,
            "tracemalloc_peak_bytes":tracemalloc.get_traced_memory()[1],
            "not_retail_pc_benchmark":True}
    },sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
