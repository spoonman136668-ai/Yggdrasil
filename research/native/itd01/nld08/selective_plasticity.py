"""ITD-01 NLD-08: causal plasticity gating without parameter snapshot buffers.

Read only the existing NLD-06 prequential prediction-error window, not a source
family, private change clock, phase reset, or the hidden A/B decision rule.
The already-exposed R9 seed-3 source is the only learner experience.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/"nld07"))
from rollback import (
    CueNative,CuePerceptron,CueEpisodic,Detector,DELAY,FIT,TOTAL,SEED,
    PUBLIC_CODES,PATTERNS,DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS,
    original_public_stream,source_eval_private,retrospective_accuracy,
    score,canonical,digest
)
from context_formation import public_correct

SCHEMA="itd01.nld08.early_plasticity_gate_public_dev.v1"
GATE_ERROR_THRESHOLD=3
DETECTOR_WARMUP=64
PRIOR_ROLLBACK_EXTRA_NATIVE_SNAPSHOT_BYTES=18702


class SelectivePlasticityGate:
    """One source-blind condition, two counters. No state history or replay."""
    def __init__(self, enabled):
        if type(enabled) is not bool:
            raise ValueError("NLD08_INVALID_GATE_MODE")
        self.enabled=enabled
        self.suppressed=0
        self.first_tick=None

    def decision(self,router):
        # Prior feedback errors only: current item's outcome is not yet read.
        return bool(self.enabled and
                    router.feedback_count>=DETECTOR_WARMUP and
                    router.codes==[-1] and
                    sum(router.errors)>=GATE_ERROR_THRESHOLD)

    def save(self):
        return canonical({"schema":SCHEMA,"enabled":self.enabled,
                          "suppressed":self.suppressed,"first_tick":self.first_tick})


def consume_public_feedback_without_plasticity(model,item,tick):
    """Validate and consume authentic feedback, never refund learner exposure."""
    if item["token"] not in model.pending:
        raise ValueError("NLD08_PENDING_ACTION_MISSING")
    pending=model.pending[item["token"]]
    if type(pending) is not tuple or len(pending)!=4:
        raise ValueError("NLD08_PENDING_EVENT_SHAPE")
    sensors,cue,action,born=pending
    if (type(tick) is not int or type(born) is not int or
        type(item["success"]) is not bool or
        tick-born!=DELAY or
        born!=item["tick"] or
        tick!=item["feedback_tick"] or
        tuple(item["sensors"])!=tuple(sensors) or
        action!=item["action"]):
        raise ValueError("NLD08_PUBLIC_CAUSAL_EVENT_MISMATCH")
    # This also rejects illegal action/outcome shape without revealing source truth.
    public_correct(item)
    model.feedback_updates+=1
    del model.pending[item["token"]]


def run(seed=SEED):
    if type(seed) is not int or seed!=SEED:
        raise ValueError("NLD08_ONLY_ALREADY_EXPOSED_PUBLIC_SEED3")
    events,receipts=original_public_stream()
    arms=[
        ("native_baseline",CueNative(True),Detector(),SelectivePlasticityGate(False)),
        ("native_gate",CueNative(True),Detector(),SelectivePlasticityGate(True)),
        ("native_never_switch",CueNative(True),Detector(False),SelectivePlasticityGate(False)),
        ("perceptron_baseline",CuePerceptron(True),Detector(),SelectivePlasticityGate(False)),
        ("perceptron_gate",CuePerceptron(True),Detector(),SelectivePlasticityGate(True)),
        ("episodic_baseline",CueEpisodic(True),Detector(),SelectivePlasticityGate(False)),
        ("episodic_gate",CueEpisodic(True),Detector(),SelectivePlasticityGate(True)),
    ]
    privileged_oracle=CueNative(True)
    due={}
    forensic={}
    for tick in range(TOTAL+DELAY):
        for item in due.pop(tick,[]):
            for name,model,router,gate in arms:
                if gate.decision(router):
                    consume_public_feedback_without_plasticity(model,item,tick)
                    gate.suppressed+=1
                    if gate.first_tick is None:
                        gate.first_tick=tick
                else:
                    model.learn_delayed(item["token"],item["success"],tick)
                # Original detector always processes real feedback unmodified.
                router.feedback(item)
            privileged_oracle.learn_delayed(item["token"],item["success"],tick)
        if tick in DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS:
            forensic[str(tick)]={
                name:retrospective_accuracy(model)
                for name,model,router,gate in arms}
        if tick>=TOTAL:continue
        item=events[tick]
        for name,model,router,gate in arms:
            router.observe(item["token"],item["sensors"],item["action"],tick,model)
            model.observe_public_action(item["token"],item["sensors"],
                                        router.active,item["action"],tick)
        privileged_oracle.observe_public_action(
            item["token"],item["sensors"],PUBLIC_CODES[tick//FIT],
            item["action"],tick)
        due.setdefault(tick+DELAY,[]).append(item)
    if (due or privileged_oracle.pending or
        privileged_oracle.feedback_updates!=TOTAL):
        raise AssertionError("NLD08_UNDRAINED_PUBLIC_STREAM")
    if any(model.pending or router.pending or
           router.feedback_count!=TOTAL or model.feedback_updates!=TOTAL
           for name,model,router,gate in arms):
        raise AssertionError("NLD08_MISSING_OR_DUPLICATE_FEEDBACK")
    for name,model,router,gate in arms:
        if not gate.enabled and gate.suppressed:
            raise AssertionError("NLD08_UNINTENDED_BASELINE_INTERVENTION")
        if isinstance(model,CueNative):
            # Cell public_updates count is the actual number of applied feedback
            # updates (all 20 cells updated together).
            expected=TOTAL-gate.suppressed
            if any(cell.public_updates!=expected for cell in model.cells):
                raise AssertionError("NLD08_NATIVE_ACTUAL_UPDATE_COUNT_DRIFT")
    oracle=privileged_oracle
    # Reuse original NLD-07 evaluator without modifying implementation.
    oldshape=[(name,model,router,False) for name,model,router,gate in arms]
    before_gates={name:gate.save() for name,m,r,gate in arms}
    a=score(oldshape,oracle,0)
    b=score(oldshape,oracle,1)
    if any(gate.save()!=before_gates[name] for name,m,r,gate in arms):
        raise AssertionError("NLD08_EVALUATOR_CHANGED_GATE")
    baselineA=a["routed_correct_of_56"]
    baselineB=b["routed_correct_of_56"]
    if (baselineA["native_baseline"]!=48 or
        baselineA["perceptron_baseline"]!=48 or
        baselineA["native_never_switch"]!=33 or
        baselineB["native_baseline"]!=56 or
        arms[0][2].transitions!=[{
            "feedback_tick":140,"observation_tick":138,
            "feedback_count":139,"rolling_prediction_errors":6}]):
        raise AssertionError("NLD08_PREVIOUS_NLD06_SCIENCE_BASELINE_DRIFT")
    n,r,g=arms[1][1:]
    native=n.save()
    router=r.save()
    if (Detector.restore(router).save()!=router or
        CueNative.restore(native).save()!=native or
        any(n.choose(p,c)!=CueNative.restore(native).choose(p,c)
            for c in PUBLIC_CODES for p in PATTERNS)):
        raise AssertionError("NLD08_COLD_RESTART_DRIFT")
    return {
        "schema":SCHEMA,
        "predecessor_nld07_sha":"0afbccffba01606766b0ed28fbb6f2dcd6707da6",
        "previously_exposed_public_dev_seed":SEED,
        "protected_first_use":False,
        "original_r9_science_seeds_101_211_307_used":False,
        "original_private_source_receipts":receipts,
        "source_free_continuous_trace_sha256":digest(events),
        "source_reset_visible_to_learners":False,
        "source_actions_received":TOTAL,
        "actual_public_feedback_events_received_each_arm":{
            name:model.feedback_updates for name,model,router,gate in arms},
        "applied_public_feedback_updates_each_arm":{
            name:model.feedback_updates-gate.suppressed
            for name,model,router,gate in arms},
        "selective_gate_frozen_prior_error_threshold":GATE_ERROR_THRESHOLD,
        "original_detector_window":16,
        "original_detector_warmup":DETECTOR_WARMUP,
        "original_detector_alarm_threshold":6,
        "native_gate_extra_parameter_snapshot_buffer_bytes":0,
        "original_nld07_rollback_peak_extra_native_snapshot_bytes_reference":
            PRIOR_ROLLBACK_EXTRA_NATIVE_SNAPSHOT_BYTES,
        "gates":{
            name:{"enabled":gate.enabled,
                  "suppressed_plastic_updates":gate.suppressed,
                  "first_suppression_feedback_tick":gate.first_tick,
                  "serialized_gate_bytes":len(gate.save())}
            for name,model,router,gate in arms},
        "alarms":{name:router.transitions for name,model,router,gate in arms},
        "private_forensic_reference_feedback_ticks":
            list(DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS),
        "private_readonly_16_pattern_attribution":forensic,
        "native_gate_checkpoint":{
            "policy_sha256":hashlib.sha256(native).hexdigest(),
            "detector_sha256":hashlib.sha256(router).hexdigest(),
            "matching_cold_public_predictions":32},
        "model_plus_detector_plus_gate_serialized_bytes":{
            name:len(model.save())+len(router.save())+len(gate.save())
            for name,model,router,gate in arms},
        "a_retained_after_b":a,
        "b_post_learning":b,
        "historical_nld07_retained_A_rollback_reference":56,
        "historical_nld07_retained_B_rollback_reference":56,
        "novel_causal_composition":"NOT_TESTED",
        "unfamiliar_source_transfer":"NOT_TESTED_R9_C_NEGATIVE_PRESERVED",
        "isolated_model_cpu_rss_parity":False,
        "ckb_scientific_admission":"NOT_OBSERVED",
        "disposition":"NLD08_PUBLIC_DEV_EARLY_PLASTICITY_GATE_RETAIN_ALL_OUTCOMES",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--smoke",action="store_true",required=True)
    p.parse_args()
    print(json.dumps(run(),sort_keys=True,separators=(",",":"),allow_nan=False))
