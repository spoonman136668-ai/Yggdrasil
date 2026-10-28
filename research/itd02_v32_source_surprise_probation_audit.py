"""V32 fixed-source synthetic probation/return audit, preregistered before code.

Reward laws are evaluator-only. Every learner gets ONLY selected public reward.
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
from research.itd02_v29_observational_equivalence_audit import selected_map,law,begin
from research.itd02_v26_calibrated_return_audit import RidgeCUSUM
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES,canonical
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev
from yggdrasil.itd02_v30_public_probe_policy_dev import PublicProbePolicyDev
from yggdrasil.itd02_v32_source_surprise_probation_dev import SourceSurpriseProbationDev

PARENT="fccbe73ad48f40ea5ac0b45482a9ace025b62573"
PREREG="889c618a6a1c087d3e5be32b58c61d2933ffc818"
KINDS=("A","B","B0")
PROBE_INDICES=(0,4,8)
HEADS=("active","fast","source","v26","rls","two_expert")
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
 "research/itd02_v31_credit_readout_attribution_audit.py":"d51b0dd9e04288372d899387d2823c947d4d037e",
}

def verify():
    root=Path(__file__).resolve().parents[1]
    def git(*args):return subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for sha in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",sha,"HEAD")=="",("V32_CHRONOLOGY",sha)
    for path,sha in PINS.items():
        assert git("hash-object",path)==sha,("V32_PROTECTED_BLOB_DRIFT",path)

def snapshot(candidate,baseline,rls,world,mapping):
    """Offline evaluation on FROZEN CLONES; all unselected rewards remain here."""
    cp=candidate.checkpoint()
    a=SourceSurpriseProbationDev.restore(cp)
    b=CalibratedReturnRingDev.restore(baseline.checkpoint())
    q=copy.deepcopy(rls)
    a.start_frozen_evaluation()
    b.start_frozen_evaluation()
    choices={k:[] for k in HEADS}
    regrets={k:0.0 for k in HEADS}
    ranking={}
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        begin(a,(cue,first,ACTIONS[0]))
        begin(b,(cue,first,ACTIONS[0]))
        source_scores=[a.bank.source_score(act) for act in ACTIONS]
        fast_scores=[a.bank.fast_score(act) for act in ACTIONS]
        scores={
            "source":source_scores,"fast":fast_scores,
            "active":fast_scores if a.use_fast else source_scores,
            "v26":b.scores(),
        }
        r=[q.predictions((cue,first,act)) for act in ACTIONS]
        scores["rls"]=[x[2] for x in r]
        scores["two_expert"]=[x[3] for x in r]
        ranking[(cue,first)]=scores
        outcome=[law(world,(cue,first,act),mapping) for act in ACTIONS]
        optimal=max(outcome)
        for name in HEADS:
            index=max(range(3),key=lambda j:scores[name][j])
            action=ACTIONS[index]
            choices[name].append([cue,first,action])
            regrets[name]+=optimal-outcome[index]
        a.accept_second(choices["active"][-1][-1],0.0,learning=False)
        b.accept_second(choices["v26"][-1][-1],0.0,learning=False)
    assert candidate.checkpoint()==cp
    return {"regret":{k:round(v,12) for k,v in regrets.items()},
            "choices":choices,
            "score_sha":hashlib.sha256(canonical(
                [{"context":list(k),"scores":{name:[round(z,12) for z in s]
                                    for name,s in vals.items()}}
                 for k,vals in ranking.items()])).hexdigest(),
            "source_vs_fast_disagreements":sum(
                x[-1]!=y[-1] for x,y in zip(choices["source"],choices["fast"]))}

def selected_feedback(candidate,baseline,rls,chooser,case,world,mapping,phase,number):
    cue,first,selected=case
    begin(candidate,case)
    begin(baseline,case)
    pre={name:round(score,12) for name,score in
         (("active",candidate.score(selected)),
          ("fast",candidate.bank.fast_score(selected)),
          ("source",candidate.bank.source_score(selected)),
          ("v26",baseline.score(selected)))}
    ps,pr,pc,pt=rls.predictions(case)
    pre["rls"]=round(pc,12)
    pre["two_expert"]=round(pt,12)
    prior_fast=candidate.use_fast
    before_fast_sha=candidate.bank.fast.parameters_sha256()
    source_sha=candidate.bank.source_sha
    # Only evaluator knows world; legal public selected reward delivered AFTER choice.
    observed=law(world,case,mapping)
    candidate.accept_second(selected,observed)
    baseline.accept_second(selected,observed)
    rls.observe(case,observed,ps,pr)
    chooser.observe_selected(cue,first,selected)
    assert candidate.bank.slow.parameters_sha256()==source_sha
    assert baseline.bank.slow.parameters_sha256()==source_sha
    assert candidate.bank.fast.parameters_sha256()==baseline.bank.fast.parameters_sha256()
    assert len(candidate.checkpoint())<=12288
    assert SourceSurpriseProbationDev.restore(candidate.checkpoint()).checkpoint()==candidate.checkpoint()
    return {
        "phase_evaluator_only":phase,"number":number,
        "selected_public":[cue,first,selected],"observed_reward":round(observed,12),
        "pre_selected_prediction":pre,
        "prior_fast":prior_fast,"after_fast":candidate.use_fast,
        "internal_v26_fast":baseline.fast,
        "selector_streak_after":candidate.streak,
        "new_fast_parameter_sha":candidate.bank.fast.parameters_sha256(),
        "fast_changed":before_fast_sha!=candidate.bank.fast.parameters_sha256(),
        "native_updates":candidate.bank.fast.updates,
        "slow_source_sha":source_sha}

def run_world(world,source,observed,mapping):
    m=SourceSurpriseProbationDev(source)
    v=CalibratedReturnRingDev(source)
    q=RidgeCUSUM(source)
    chooser=PublicProbePolicyDev("novelty")
    records=[]
    snaps={}
    for n,case in enumerate(observed):
        records.append(selected_feedback(m,v,q,chooser,case,world,mapping,"base",n+1))
    snaps["budget0"]=snapshot(m,v,q,world,mapping)
    assert len(records)==12
    for i,index in enumerate(PROBE_INDICES):
        cue,first,_=observed[index]
        begin(m,(cue,first,ACTIONS[0]))
        scores=m.scores()
        chosen=chooser.select(cue,first,scores)
        # Candidate has just begun actual first. Do not double start.
        case=(cue,first,chosen)
        pred={x:round(y,12) for x,y in zip(ACTIONS,scores)}
        v.start_observation(cue);v.accept_first(first)
        ps,pr,pc,pt=q.predictions(case)
        s0=m.bank.source_sha
        native_sha_before=m.bank.fast.parameters_sha256()
        before_fast=m.use_fast
        y=law(world,case,mapping)
        m.accept_second(chosen,y)
        v.accept_second(chosen,y)
        q.observe(case,y,ps,pr)
        chooser.observe_selected(cue,first,chosen)
        assert m.bank.slow.parameters_sha256()==s0
        assert m.bank.fast.parameters_sha256()==v.bank.fast.parameters_sha256()
        assert len(m.checkpoint())<=12288
        records.append({
          "phase_evaluator_only":"probe","number":i+1,
          "selected_public":list(case),"observed_reward":round(y,12),
          "chosen_prospectively":True,
          "observed_pre_scores":pred,
          "prior_fast":before_fast,"after_fast":m.use_fast,
          "new_fast_parameter_sha":m.bank.fast.parameters_sha256(),
          "fast_changed":native_sha_before!=m.bank.fast.parameters_sha256(),
          "native_updates":m.bank.fast.updates,
          "slow_source_sha":s0})
        if i==0:
            snaps["budget1"]=snapshot(m,v,q,world,mapping)
    snaps["budget3"]=snapshot(m,v,q,world,mapping)
    final_target_fast=m.use_fast
    return_latency=None
    wrong_fast_last8=0
    # Exactly twelve extra source events; no boundary callback to any learner.
    for i,case in enumerate(observed):
        row=selected_feedback(m,v,q,chooser,case,"A",mapping,"source_return",i+1)
        records.append(row)
        if return_latency is None and not m.use_fast:
            return_latency=i+1
        if i>=4:
            wrong_fast_last8+=int(m.use_fast)
        if i==3:
            snaps["return4"]=snapshot(m,v,q,"A",mapping)
    snaps["return12"]=snapshot(m,v,q,"A",mapping)
    return {"world":world,"records":records,
            "snapshots":snaps,
            "return_latency":return_latency,
            "false_fast_postwarmup":wrong_fast_last8,
            "probation_fast_after_probes":final_target_fast,
            "original_source_sha":m.bank.source_sha,
            "original_source_unchanged":True,
            "final_checkpoint_bytes":len(m.checkpoint()),
            "learned_scalars":326,
            "native_fast_updates":m.bank.fast.updates,
            "source_training_updates":m.bank.slow.updates,
            "fast_signal_counts":{
                "forward_input":m.bank.fast.forward_input_messages,
                "forward_output":m.bank.fast.forward_output_messages,
                "reverse_credit":m.bank.fast.reverse_credit_messages}}

def outcome(results):
    by={r["world"]:r for r in results}
    a,b,b0=by["A"],by["B"],by["B0"]
    # A/B0 identical full laws; all public and model states must match.
    assert a["records"]==b0["records"]
    assert a["snapshots"]==b0["snapshots"]
    # A/B identical selected feedback BEFORE unobserved probe.
    assert a["records"][:12]==b["records"][:12]
    snaps=b["snapshots"]
    at0=snaps["budget0"]["regret"]["active"]
    at3=snaps["budget3"]["regret"]["active"]
    fast3=snaps["budget3"]["regret"]["fast"]
    rls3=snaps["budget3"]["regret"]["rls"]
    original_source_regret=a["snapshots"]["budget0"]["regret"]["source"]
    source_regret=a["snapshots"]["budget3"]["regret"]["active"]
    native_changed=snaps["budget0"]["choices"]["active"]!=snaps["budget3"]["choices"]["active"]
    unlocked=b["probation_fast_after_probes"] and at3<at0
    recovered=b["return_latency"] is not None and b["return_latency"]<=4
    clean_return=b["false_fast_postwarmup"]==0
    source_safe=source_regret <=1.1*original_source_regret+1e-10
    strong=at3<=0.9*rls3 and native_changed and at3<=1.1*fast3+1e-10
    if not unlocked:
        category="V32_SOURCE_SURPRISE_DID_NOT_UNLOCK_LEARNING__NO_SCIENCE"
    elif not recovered or not clean_return or not source_safe:
        category="V32_SOURCE_RETENTION_OR_RETURN_FAILED__NO_SCIENCE"
    elif not strong:
        category="V32_SELECTIVITY_WITHOUT_STRONG_DECISION_GAIN__NO_SCIENCE"
    else:
        category="V32_BOUNDED_SYNTHETIC_PROBATION_ENGINEERING_POSITIVE__NO_SCIENCE"
    return category,{"B_active_regret0":at0,"B_active_regret3":at3,
        "B_fast_regret3":fast3,"B_RLS_regret3":rls3,
        "B_active_policy_changed":native_changed,
        "B_fast_probation_after_three":b["probation_fast_after_probes"],
        "B_return_latency":b["return_latency"],
        "B_wrong_fast_last8_return":b["false_fast_postwarmup"],
        "A_active_regret3":source_regret,
        "A_original_source_regret0":original_source_regret,
        "probe_selector_unlocks":unlocked,
        "return_to_source_by_four":recovered,
        "no_false_fast_last8":clean_return,
        "source_no_regression":source_safe,
        "strong_conventional_gain":strong}

def main():
    verify()
    start=time.perf_counter()
    cpu=time.process_time()
    tracemalloc.start()
    source=train_source()["pretrained_shared"]
    observed,mapping=selected_map()
    results=[run_world(world,source,observed,mapping) for world in KINDS]
    assert all(x["native_fast_updates"]==27 and
               x["source_training_updates"]==576 and
               x["learned_scalars"]==326 and
               x["final_checkpoint_bytes"]<=12288 and
               x["original_source_unchanged"] for x in results)
    classification,gates=outcome(results)
    digest=hashlib.sha256(canonical(results)).hexdigest()
    print(json.dumps({
        "schema":"ygg.itd02.v32.public_probation_return.source_only.v1",
        "classification":classification,"scientific_first_use":False,
        "source_only":True,"independent_unfamiliar_transfer":False,
        "original_native_modified":False,"new_learned_native_parameters":0,
        "preregistration_locked":True,
        "worlds":list(KINDS),"extra_probe_budget":3,"return_public_feedback":12,
        "candidate_public_reward_updates":27,
        "original_source_training_updates":576,
        "stored_native_learned_scalars":326,
        "native_fast_trainable_scalars":163,
        "conventional_full_matrix_rls":True,
        "original_v26_baseline_unchanged":True,
        "gates":gates,
        "canonical_cases_and_policy_sha256":digest,
        "results":[{k:v for k,v in row.items() if k!="records"}
                    for row in results],
        "host_only_resources":{
            "cpu_seconds":time.process_time()-cpu,
            "wall_seconds":time.perf_counter()-start,
            "peak_python_bytes":tracemalloc.get_traced_memory()[1],
            "not_retail_pc_benchmark":True}
    },sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    main()
