"""NLD07: prospective recent-plasticity rollback at source-blind surprise alarm.

The causal intervention rewinds learned weights only. No source task, switch
clock or private label enters a candidate model or original NLD06 detector.
Previously exposed R9 smoke seed 3; no protected first use.
"""
from __future__ import annotations
import argparse
import copy
from collections import deque
import hashlib
import json
import sys
from pathlib import Path

P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/"nld06"))
from continuous_surprise import (
    Detector,original_public_stream,CueNative,CuePerceptron,CueEpisodic,
    PUBLIC_CODES,PATTERNS,PROBES,SCORED,SEED,FIT,DELAY,TOTAL,
    source_eval_private,digest,canonical)
from context_formation import source_only_correct_action

SCHEMA="itd01.nld07.recent-plasticity-rollback-public-dev.v1"
DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS=(129,140,257)
ROLLBACK_WINDOW=16


def learned_snapshot(model):
    """Exclude pending feedback ledger and delivered feedback count."""
    if isinstance(model,CueNative):
        cells=[{"fast":c.fast,"slow":c.slow,"updates":c.public_updates}
               for c in model.cells]
        state={"kind":"native","cells":cells,"bias":model.bias,
               "weight_changes":model.weight_changes}
    elif isinstance(model,CuePerceptron):
        state={"kind":"perceptron","weights":list(model.weights),
               "bias":model.bias}
    elif isinstance(model,CueEpisodic):
        state={"kind":"episodic","memory":dict(model.memory)}
    else:
        raise TypeError("NLD07_UNQUALIFIED_LEARNER")
    return state


def restore_learned_only(model,state):
    """Never edit pending tokens, action-time context or feedback event count."""
    previous_feedback=model.feedback_updates
    previous_pending=copy.deepcopy(model.pending)
    if state["kind"]=="native" and isinstance(model,CueNative):
        if len(state["cells"])!=len(model.cells):
            raise ValueError("NLD07_CELL_COUNT")
        for c,s in zip(model.cells,state["cells"]):
            c.fast=s["fast"]
            c.slow=s["slow"]
            c.public_updates=s["updates"]
        model.bias=state["bias"]
        model.weight_changes=state["weight_changes"]
    elif state["kind"]=="perceptron" and isinstance(model,CuePerceptron):
        if len(state["weights"])!=len(model.weights):
            raise ValueError("NLD07_WEIGHT_COUNT")
        model.weights=list(state["weights"])
        model.bias=state["bias"]
    elif state["kind"]=="episodic" and isinstance(model,CueEpisodic):
        model.memory=dict(state["memory"])
    else:
        raise ValueError("NLD07_BAD_STATE_KIND")
    if model.feedback_updates!=previous_feedback or model.pending!=previous_pending:
        raise AssertionError("NLD07_FEEDBACK_CUSTODY_MUTATED")


def retrospective_accuracy(model):
    """Private evaluator reads 16 disclosed source patterns; never trains/controls."""
    return {fam+"_"+str(slot):sum(
        model.choose(p,slot)==source_only_correct_action(fam,p)
        for p in PATTERNS)
        for fam in ("A","B") for slot in PUBLIC_CODES}


def train(arms,oracle,stream):
    due={}
    snapshots={name:deque(maxlen=ROLLBACK_WINDOW)
               for name,m,r,rollback in arms if rollback}
    peak_saved_bytes={name:0 for name in snapshots}
    rollback_records={name:[] for name in snapshots}
    forensic={}
    for tick in range(TOTAL+DELAY):
        for item in due.pop(tick,[]):
            for name,model,router,rollback in arms:
                ring=snapshots.get(name)
                if rollback:
                    ring.append(learned_snapshot(model))
                    peak_saved_bytes[name]=max(
                        peak_saved_bytes[name],
                        sum(len(canonical(s)) for s in ring))
                before=len(router.transitions)
                model.learn_delayed(item["token"],item["success"],tick)
                router.feedback(item)
                if rollback and len(router.transitions)>before:
                    if len(ring)!=ROLLBACK_WINDOW:
                        raise AssertionError("NLD07_INCOMPLETE_WINDOW_AT_TRIGGER")
                    original_count=model.feedback_updates
                    restore_learned_only(model,ring[0])
                    if model.feedback_updates!=original_count:
                        raise AssertionError("NLD07_PUBLIC_EVENT_ACCOUNTING_LOST")
                    rollback_records[name].append({
                        "trigger_feedback_tick":tick,
                        "oldest_rolled_back_delivery_count":
                            router.feedback_count-ROLLBACK_WINDOW+1,
                        "rolled_back_parameter_updates":ROLLBACK_WINDOW,
                        "feedback_events_still_received":model.feedback_updates})
                    ring.clear()
            oracle.learn_delayed(item["token"],item["success"],tick)
        if tick in DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS:
            forensic[str(tick)]={
                name:retrospective_accuracy(model)
                for name,model,router,rollback in arms}
        if tick>=TOTAL:continue
        item=stream[tick]
        for name,model,router,rollback in arms:
            router.observe(item["token"],item["sensors"],
                           item["action"],tick,model)
            model.observe_public_action(item["token"],item["sensors"],
                                        router.active,item["action"],tick)
        # Private oracle only, not counted as an equal-information contender.
        oracle.observe_public_action(item["token"],item["sensors"],
                                     PUBLIC_CODES[tick//FIT],
                                     item["action"],tick)
        due.setdefault(tick+DELAY,[]).append(item)
    if due or oracle.pending or oracle.feedback_updates!=TOTAL:
        raise AssertionError("NLD07_UNDRAINED_SOURCE")
    if any(m.pending or router.pending or m.feedback_updates!=TOTAL or
           router.feedback_count!=TOTAL for name,m,router,rollback in arms):
        raise AssertionError("NLD07_LOST_OR_DUPLICATED_FEEDBACK")
    return forensic,rollback_records,peak_saved_bytes


def score(arms,oracle,stage):
    probes,public_sensors,private_truth=source_eval_private(stage)
    probes=[{**r,"token":"PUB-EVAL-%03d"%i}
            for i,r in enumerate(probes)]
    saved={name:(m.save(),router.save())
           for name,m,router,rollback in arms}
    inferred={}
    counts={}
    own_oldslot={}
    for name,model,router,rollback in arms:
        picked=router.route(model,probes)
        inferred[name]=picked
        counts[name]=sum(model.choose(s,picked["slot"])==answer
                         for s,answer in zip(public_sensors,private_truth))
        # Private attribution only: does not feed model/router or select its cue.
        own_oldslot[name]=sum(model.choose(s,PUBLIC_CODES[stage])==answer
                             for s,answer in zip(public_sensors,private_truth))
    counts["privileged_phase_known_source_oracle"]=sum(
        oracle.choose(s,PUBLIC_CODES[stage])==answer
        for s,answer in zip(public_sensors,private_truth))
    if any(saved[name]!=(m.save(),router.save())
           for name,m,router,rollback in arms):
        raise AssertionError("NLD07_EVALUATION_UPDATED_WEIGHTS")
    return {
        "private_source_for_posthoc_audit":("A","B")[stage],
        "original_public_role_steps":64,
        "public_unscored_delayed_probes":PROBES,
        "scored_observations":SCORED,
        "routed_correct_of_56":counts,
        "oracle_task_slot_correct_of_56_evaluator_only":own_oldslot,
        "public_probe_context_decisions":inferred,
        "public_probe_history_sha256":digest(probes),
        "no_fitting_during_scoring":True,
    }


def run(seed=SEED):
    if type(seed) is not int or seed!=SEED:
        raise ValueError("NLD07_ONLY_PRIOR_PUBLIC_SMOKE_SEED3")
    stream,receipts=original_public_stream()
    arms=[
        ("native_baseline",CueNative(True),Detector(),False),
        ("native_rollback",CueNative(True),Detector(),True),
        ("native_never_switch",CueNative(True),Detector(False),False),
        ("perceptron_baseline",CuePerceptron(True),Detector(),False),
        ("perceptron_rollback",CuePerceptron(True),Detector(),True),
        ("episodic_baseline",CueEpisodic(True),Detector(),False),
        ("episodic_rollback",CueEpisodic(True),Detector(),True),
    ]
    oracle=CueNative(True)
    forensic,rollbacks,highwater=train(arms,oracle,stream)
    n=arms[0][1]; router=arms[0][2]
    native_raw=n.save()
    router_raw=router.save()
    if Detector.restore(router_raw).save()!=router_raw or any(
        n.choose(p,c)!=CueNative.restore(native_raw).choose(p,c)
        for p in PATTERNS for c in PUBLIC_CODES):
        raise AssertionError("NLD07_COLD_RESTART")
    a=score(arms,oracle,0)
    b=score(arms,oracle,1)
    if (a["routed_correct_of_56"]["native_baseline"]!=48 or
        a["routed_correct_of_56"]["native_never_switch"]!=33 or
        a["routed_correct_of_56"]["perceptron_baseline"]!=48 or
        b["routed_correct_of_56"]["native_baseline"]!=56 or
        arms[0][2].transitions!=[{
            "feedback_tick":140,"observation_tick":138,
            "feedback_count":139,"rolling_prediction_errors":6}]):
        raise AssertionError("NLD07_ORIGINAL_NLD06_BASELINE_DRIFT")
    for name,model,r,rollback in arms:
        if rollback and r.transitions and len(rollbacks[name])!=1:
            raise AssertionError("NLD07_ROLLBACK_MISSING_OR_REPEATED")
    return {
        "schema":SCHEMA,
        "original_nld06_head":"95ccf52bfe4207d22dbe0cd22369ec3c1447740e",
        "source_free_old_dev_seed":SEED,
        "protected_first_use":False,
        "original_scientific_r9_101_211_307_replayed":False,
        "original_source_receipts":receipts,
        "global_public_stream_sha256":digest(stream),
        "uninterrupted_public_actions":TOTAL,
        "all_models_feedback_events_delivered":TOTAL,
        "no_phase_reset_received_by_models":True,
        "source_boundary_known_to_oracle_and_private_audit_only":FIT,
        "forensic_private_feedback_ticks":list(DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS),
        "private_full_16_pattern_forensic_accuracy":forensic,
        "retrospective_parameter_rollbacks":rollbacks,
        "extra_16_snapshot_ring_peak_bytes":highwater,
        "detector_alarms":{name:r.transitions for name,m,r,rollback in arms},
        "model_and_router_checkpoint_bytes":{
            name:len(m.save())+len(r.save()) for name,m,r,rollback in arms},
        "learned_public_feedback_counts":{
            name:m.feedback_updates for name,m,r,rollback in arms},
        "native_cold_checkpoint_sha256":hashlib.sha256(native_raw).hexdigest(),
        "native_cold_router_sha256":hashlib.sha256(router_raw).hexdigest(),
        "native_cold_predictions_verified":32,
        "score_A_retained_after_B":a,
        "score_B":b,
        "causal_composition":"NOT_TESTED",
        "unfamiliar_transfer":"NOT_TESTED_OLD_R9_C_ZERO_SHOT_NO_GO",
        "per_model_cpu_rss_efficiency_claim":False,
        "authenticated_ckb_scientific_admission":"NOT_OBSERVED",
        "disposition":"NLD07_EXISTING_PUBLIC_SOURCE_ROLLBACK_ABLATION_RETAIN_ALL_POSITIVES_AND_NEGATIVES",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--smoke",action="store_true",required=True)
    p.parse_args()
    print(json.dumps(run(),sort_keys=True,separators=(",",":"),allow_nan=False))
