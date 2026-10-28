"""V34 original-native action-credit and spillover forensic audit (SOURCE-ONLY).

All learned updates consume ACTUAL selected terminal public feedback. The
unselected synthetic law is evaluator-only, AFTER frozen prospective scores.
No accepted V22/V32 native code or V33 benchmark is changed.
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
from research.itd02_v29_observational_equivalence_audit import selected_map,begin
from research.itd02_v26_calibrated_return_audit import RidgeCUSUM
from research.itd02_v33_unseen_family_independent_controls_audit import law
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES,canonical
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev,LEARNED_SCALARS
from yggdrasil.itd02_v30_public_probe_policy_dev import PublicProbePolicyDev
from yggdrasil.itd02_v32_source_surprise_probation_dev import SourceSurpriseProbationDev

PARENT="5bb6d0cfe095cddce438028cdd30d934239c4de7"
PREREG="8f6ced6d662bdff819e6133ed6974830a47d4524"
WORLDS=("U1","U2","U3")
PROBES=(0,4,8)
CONTEXTS=tuple(itertools.product(PUBLIC_CUES,ACTIONS))
PIN={
 "yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
 "yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
 "yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
 "yggdrasil/itd02_v24_protected_dual_memory_dev.py":"9ef95a28e9060dd79105f51122d527351756a1e0",
 "yggdrasil/itd02_v25_unlabeled_return_dev.py":"f90e5029b121cbfc2e361f9e0941985eb1e69e3d",
 "yggdrasil/itd02_v26_calibrated_return_dev.py":"8a0417d34c6ba94a4eaef33d767da14a4a5c9709",
 "yggdrasil/itd02_v30_public_probe_policy_dev.py":"bcc1f0b4e2ec0fcd8b2af69dfb0e6d4d2ca27a4a",
 "yggdrasil/itd02_v32_source_surprise_probation_dev.py":"9252b554c25bfdc5b6adb733f94b0c3d2b2ec92e",
 "research/itd02_v33_unseen_family_independent_controls_audit.py":"3545f88f5689f8d5aa6e5d75b1344d7a7a83a8f2",
}

def check_source():
    root=Path(__file__).resolve().parents[1]
    git=lambda *a:subprocess.check_output(("git",)+a,cwd=root,text=True).strip()
    for a in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",a,"HEAD")=="",("FROZEN_CHRONOLOGY",a)
    for f,blob in PIN.items():
        assert git("hash-object",f)==blob,("SOURCE_CHANGED",f)
    assert LEARNED_SCALARS==163 and len(CONTEXTS)==12 and len(ACTIONS)==3

def public_native_scores(m):
    """Build only 36 frozen predictions from a V22 learned bank snapshot."""
    cp=m.checkpoint()
    x=SharedContextRingDev.restore(cp)
    x.start_frozen_evaluation()
    score=[]
    for cue,first in CONTEXTS:
        x.start_observation(cue);x.accept_first(first)
        row=x.scores()
        assert len(row)==3
        score.append([round(y,12) for y in row])
        x.accept_second(ACTIONS[0],0.0,learning=False)
    assert cp==m.checkpoint()
    return score

def public_rls_scores(m):
    x=copy.deepcopy(m)
    return [[round(x.predictions((cue,first,second))[2],12)
             for second in ACTIONS] for cue,first in CONTEXTS]

def evaluate_frozen(rows,world):
    """Only evaluator reads withheld other-action true reward; no model accesses."""
    actions=[]
    regret=0.0
    abs_error=0.0
    for (cue,first),pred in zip(CONTEXTS,rows):
        j=max(range(3),key=lambda k:pred[k])
        acts=[law(world,(cue,first,a)) for a in ACTIONS]
        regret+=max(acts)-acts[j]
        abs_error+=sum(abs(x-y) for x,y in zip(pred,acts))
        actions.append([cue,first,ACTIONS[j]])
    return {"regret":round(regret,12),"error_36":round(abs_error,12),"choices":actions}

def frozen_snapshot(candidate,mirror,partition,nolearn,rls,world):
    fast=candidate.bank.fast
    sources={
       "v32_fast":public_native_scores(fast),
       "shared_mirror":public_native_scores(mirror),
       "action_partition":public_native_scores(partition),
       "nonlearning":public_native_scores(nolearn),
       "rls_same_actions":public_rls_scores(rls),
    }
    assert fast.parameters_sha256()==mirror.parameters_sha256()
    assert sources["v32_fast"]==sources["shared_mirror"]
    outcomes={n:evaluate_frozen(rows,world) for n,rows in sources.items()}
    return {"predictions":sources,"evaluations":outcomes,
            "fast_sha":fast.parameters_sha256(),
            "mirror_sha":mirror.parameters_sha256(),
            "partition_sha":partition.parameters_sha256(),
            "nonlearning_sha":nolearn.parameters_sha256(),
            "source_sha":candidate.bank.source_sha,
            "fast_selected":candidate.use_fast,
            "fast_updates":fast.updates,
            "partition_updates":partition.updates,
            "rls_updates":rls.events}

def delta_record(pre,post,case):
    cue,first,selected=case
    c=CONTEXTS.index((cue,first))
    a=ACTIONS.index(selected)
    v0=pre["predictions"];v1=post["predictions"]
    out={}
    for name in ("v32_fast","action_partition"):
        delta=[[v1[name][i][j]-v0[name][i][j] for j in range(3)]
               for i in range(12)]
        chosen_delta=delta[c][a]
        other_actions=[delta[c][j] for j in range(3) if j!=a]
        other_context=[delta[i][j] for i in range(12) if i!=c for j in range(3)]
        assert len(other_context)==33 and len(other_actions)==2
        out[name]={
          "selected_action_prediction_delta":round(chosen_delta,12),
          "same_context_other_action_deltas":[round(x,12) for x in other_actions],
          "other_context_abs_delta_sum":round(sum(abs(x) for x in other_context),12),
          "other_context_abs_delta_mean":round(sum(abs(x) for x in other_context)/33.0,12),
          "other_context_max_abs_delta":round(max(abs(x) for x in other_context),12),
          "spillover_ratio":round(sum(abs(x) for x in other_context)/(abs(chosen_delta)+1e-9),12),
        }
    return out

def accept_public(candidate,mirror,partition,nolearn,rls,policy,case,world,index,phase,started=False):
    cue,first,selected=case
    if not started:begin(candidate,case)
    pre_active=candidate.score(selected)
    pre_fast=candidate.bank.fast_score(selected)
    for m in (mirror,partition,nolearn):
        m.start_observation(cue);m.accept_first(first)
    pre_mirror=mirror.score(selected)
    pre_part=partition.score(selected)
    source_sha=candidate.bank.source_sha
    fast_before=candidate.bank.fast.parameters_sha256()
    neg_before=nolearn.parameters_sha256()
    sp,rp,conv,tp=rls.predictions(case)
    # Evaluator receives selected action BEFORE knowing outcome.
    reward=law(world,case)
    candidate.accept_second(selected,reward)
    mirror.accept_second(selected,reward)
    partition.accept_second(selected,reward)
    nolearn.accept_second(selected,reward,learning=False)
    rls.observe(case,reward,sp,rp)
    policy.observe_selected(*case)
    assert candidate.bank.slow.parameters_sha256()==source_sha
    assert candidate.bank.fast.parameters_sha256()==mirror.parameters_sha256()
    assert nolearn.parameters_sha256()==neg_before
    assert len(candidate.checkpoint())<=12288
    assert SourceSurpriseProbationDev.restore(candidate.checkpoint()).checkpoint()==candidate.checkpoint()
    return {"phase":phase,"index":index,"actual_public":[cue,first,selected],
            "actual_selected_reward":round(reward,12),
            "prospective_selected_predictions":{
                "active":round(pre_active,12),"fast":round(pre_fast,12),
                "shared_mirror":round(pre_mirror,12),"action_partition":round(pre_part,12),
                "rls":round(conv,12)},
            "selected_error":{
                "fast":round(abs(reward-pre_fast),12),
                "partition":round(abs(reward-pre_part),12),
                "rls":round(abs(reward-conv),12)},
            "fast_parameters_changed":fast_before!=candidate.bank.fast.parameters_sha256(),
            "fast_sha":candidate.bank.fast.parameters_sha256(),
            "partition_sha":partition.parameters_sha256(),
            "native_fast_update_count":candidate.bank.fast.updates,
            "v32_active_fast_after":candidate.use_fast}

def run_world(world,source,observed):
    cand=SourceSurpriseProbationDev(source)
    mirror=SharedContextRingDev(mode="shared")
    part=SharedContextRingDev(mode="action_partition")
    neg=SharedContextRingDev(mode="shared")
    rls=RidgeCUSUM(source)
    chooser=PublicProbePolicyDev("novelty")
    neg0=neg.parameters_sha256()
    source_sha=cand.bank.source_sha
    start_snap=frozen_snapshot(cand,mirror,part,neg,rls,world)
    events=[]
    for i,case in enumerate(observed):
        events.append(accept_public(cand,mirror,part,neg,rls,chooser,case,world,i+1,"base"))
    s12=frozen_snapshot(cand,mirror,part,neg,rls,world)
    diagnostics=[]
    snapshots=[{"budget":0,"snapshot":s12}]
    for i,idx in enumerate((0,4,8)):
        cue,first,_=observed[idx]
        begin(cand,(cue,first,ACTIONS[0]))
        scores=cand.scores()
        selected=chooser.select(cue,first,scores)
        case=(cue,first,selected)
        before=frozen_snapshot_pre_started(cand,mirror,part,neg,rls,world)
        event=accept_public(cand,mirror,part,neg,rls,chooser,case,world,i+1,"probe",started=True)
        events.append(event)
        after=frozen_snapshot(cand,mirror,part,neg,rls,world)
        diagnostics.append({
            "probe":i+1,"actual_selected_public":list(case),
            "selected_reward":event["actual_selected_reward"],
            "selected_errors":event["selected_error"],
            "delta":delta_record(before,after,case),
            "active_fast_after":cand.use_fast})
        snapshots.append({"budget":i+1,"snapshot":after})
    assert len(events)==15
    assert cand.bank.slow.parameters_sha256()==source_sha
    assert cand.bank.fast.updates==15
    assert mirror.updates==part.updates==15 and neg.updates==0
    assert neg.parameters_sha256()==neg0
    assert len(cand.checkpoint())<=12288
    assert len(mirror.checkpoint())<=12288
    assert len(part.checkpoint())<=12288
    assert SharedContextRingDev.restore(part.checkpoint()).checkpoint()==part.checkpoint()
    assert rls.events==15
    return {"world":world,
       "events":events,"probes":diagnostics,
       "initial_snapshot":start_snap,"snapshots":snapshots,
       "source_bank_sha":source_sha,
       "source_unchanged":True,"fast_matches_shared_mirror":True,
       "no_learning_control_unchanged":True,
       "fast_count":cand.bank.fast.updates,
       "action_partition_count":part.updates,
       "rls_count":rls.events,
       "native_learned_scalar_count":LEARNED_SCALARS,
       "checkpoint_bytes":{
           "dual_selector":len(cand.checkpoint()),
           "shared":len(mirror.checkpoint()),
           "partition":len(part.checkpoint())},
       "local_native_edge_messages":{
           "shared_input":mirror.forward_input_messages,
           "shared_output":mirror.forward_output_messages,
           "shared_reverse":mirror.reverse_credit_messages,
           "partition_input":part.forward_input_messages,
           "partition_output":part.forward_output_messages,
           "partition_reverse":part.reverse_credit_messages}}

def frozen_snapshot_pre_started(candidate,mirror,part,neg,rls,world):
    """Prospective inference has opened candidate's actual public first step.
    Temporarily use its *completed* FAST weights in a separate V22 clone.
    Never modify or checkpoint candidate with a pending episode.
    """
    fast=candidate.bank.fast
    snapshots={
        "v32_fast":public_native_scores_started_fast(fast),
        "shared_mirror":public_native_scores(mirror),
        "action_partition":public_native_scores(part),
        "nonlearning":public_native_scores(neg),
        "rls_same_actions":public_rls_scores(rls),
    }
    assert snapshots["v32_fast"]==snapshots["shared_mirror"]
    return {"predictions":snapshots}

def public_native_scores_started_fast(fast):
    """Live fast has an open episode; construct independent readout from its
    weights on a fresh V22 bank rather than checkpoint a pending episode.
    """
    tmp=SharedContextRingDev(mode="shared")
    tmp.cell_weights=copy.deepcopy(fast.cell_weights)
    tmp.action_biases=list(fast.action_biases)
    return public_native_scores(tmp)

def classify(rows):
    v={}
    for r in rows:
        n=r["world"]
        begin=r["snapshots"][0]["snapshot"]["evaluations"]
        end=r["snapshots"][-1]["snapshot"]["evaluations"]
        v[n]={
          "shared_regret0":begin["v32_fast"]["regret"],
          "shared_regret3":end["v32_fast"]["regret"],
          "partition_regret0":begin["action_partition"]["regret"],
          "partition_regret3":end["action_partition"]["regret"],
          "rls_regret3_same_actions":end["rls_same_actions"]["regret"],
          "shared_36_abs_prediction_error":end["v32_fast"]["error_36"],
          "partition_36_abs_prediction_error":end["action_partition"]["error_36"],
          "shared_policy_changed":begin["v32_fast"]["choices"]!=end["v32_fast"]["choices"],
          "partition_policy_changed":begin["action_partition"]["choices"]!=end["action_partition"]["choices"],
          "shared_probe_spillover_ratios":[p["delta"]["v32_fast"]["spillover_ratio"] for p in r["probes"]],
          "partition_probe_spillover_ratios":[p["delta"]["action_partition"]["spillover_ratio"] for p in r["probes"]],
        }
    wins=sum(
        v[w]["shared_regret3"]>1e-10 and
        v[w]["partition_regret3"]<=0.9*v[w]["shared_regret3"]
        for w in WORLDS)
    mean_part=sum(v[w]["partition_regret3"] for w in WORLDS)/3
    mean_shared=sum(v[w]["shared_regret3"] for w in WORLDS)/3
    label=("V34_ACTION_PARTITION_LOCALIZATION_DIAGNOSTIC_POSITIVE__NO_SCIENCE"
          if wins>=2 and mean_part<=mean_shared+1e-10 else
          "V34_FIXED_LOCAL_CREDIT_ABLATION_NO_RESCUE__NO_SCIENCE")
    return label,{"families":v,"partition_10pct_win_count":wins,
      "mean_partition_regret3":round(mean_part,12),
      "mean_original_fast_regret3":round(mean_shared,12),
      "ablation_overall_wins":wins>=2 and mean_part<=mean_shared+1e-10}

def main():
    check_source()
    t=time.perf_counter();cpu=time.process_time();tracemalloc.start()
    source=train_source()["pretrained_shared"]
    observed,_=selected_map()
    assert len(observed)==12
    rows=[run_world(w,source,observed) for w in WORLDS]
    assert len(rows)==3
    label,gates=classify(rows)
    digest=hashlib.sha256(canonical(rows)).hexdigest()
    print(json.dumps({
      "schema":"ygg.itd02.v34.native_local_credit_spillover.source_only.v1",
      "classification":label,"source_only":True,"scientific_first_use":False,
      "native_original_changed":False,"trained_new_autonomous_model":False,
      "original_world_training":False,
      "worlds":list(WORLDS),"source_training_selected_rewards":576,
      "actual_selected_target_updates_per_family":15,
      "each_original_native_bank_learned_scalars":163,
      "protected_dual_stored_scalars":326,
      "matched_public_feedback_mirror":True,
      "nonlearning_control_verified":True,
      "conventional_full_matrix_rls_same_selected_feedback":True,
      "preregistration_verified":True,
      "gates":gates,
      "canonical_case_credit_and_score_sha256":digest,
      "rows":[{"world":r["world"],"probes":r["probes"],
               "base_selected_events":len([e for e in r["events"] if e["phase"]=="base"]),
               "target_extra_probes":len(r["probes"]),
               "checkpoint_bytes":r["checkpoint_bytes"],
               "source_unchanged":r["source_unchanged"],
               "native_edge_messages":r["local_native_edge_messages"]}
              for r in rows],
      "host_specific_resources":{
          "wall_seconds":time.perf_counter()-t,
          "cpu_seconds":time.process_time()-cpu,
          "tracemalloc_peak_bytes":tracemalloc.get_traced_memory()[1],
          "retail_pc_qualification":False}
    },sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
