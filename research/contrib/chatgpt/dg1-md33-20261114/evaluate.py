"""MD33 frozen synthetic conventional-control qualification.

A separate physical world is charged for each control/seed. The policy
receives only observations and paid public sensor/reward receipts; only this
external harness sees hidden motif/offset/rewire for posthoc stratification.
No original MD32 training/DEV/cold/registered seed is opened.
"""
import json
import math
import time
from pathlib import Path

from synthetic import (LOCK, STARTS, public_teacher_blocks, synthetic_world,
                       structural_split_audit, valid_allocation)
from categorical_controls import (EmpiricalCausalControl, public_result,
                                  validate_public_probe)
from recurrent_control import RecurrentWorldModel
from compositional_relay import (canonical, digest, run_public_blind,
                                 run_public_two_probe, run_privileged_oracle)

ARMS = (
    "trained_factorized_bayesian",
    "trained_recurrent_world_model",
    "trained_empirical_model_based_rl",
    "handcoded_public_two_probe",
    "blind_fixed_terminal_0",
    "privileged_oracle_upper_bound",
)
TRAINED = ARMS[:3]
CONTRACT = LOCK["one_shot_protocol"]
assert CONTRACT["arms"] == list(ARMS)
assert LOCK["status"] == "FROZEN_BEFORE_NEW_GENERATOR_BASELINES_OR_OUTCOMES"


def _top_index(probabilities):
    return min(range(4), key=lambda i: (-probabilities[i], i))


def run_policy(world, model):
    """Two irreversible decisions; each diagnostic invokes a real step."""
    precursor = world.observe()["required_precursor"]
    p = model.predict("encoder", precursor)
    intermediate = _top_index(p)
    if model.should_probe(p):
        old = world.observe()
        request = {"kind": "diagnostic", "mechanism": "encoder",
                   "channel": precursor}
        after, reward, done = world.step(request)
        if done or reward != -0.08:
            raise AssertionError("MD33_INVALID_PHYSICAL_ENCODER_PROBE")
        intermediate = validate_public_probe(old, request, after)
        model.observe("encoder", precursor, intermediate)
    after, stage_cost, done = world.step(
        {"kind": "actuator", "channel": precursor})
    if done or stage_cost != -0.02 or after["phase"] != 1:
        raise AssertionError("MD33_UNCHARGED_IRREVERSIBLE_PRECURSOR")
    p = model.predict("decoder", intermediate)
    terminal = _top_index(p)
    if model.should_probe(p):
        before = world.observe()
        request = {"kind": "diagnostic", "mechanism": "decoder",
                   "channel": intermediate}
        after, cost, done = world.step(request)
        if done or cost != -0.08:
            raise AssertionError("MD33_UNCHARGED_DECODER_PROBE")
        terminal = validate_public_probe(before, request, after)
        model.observe("decoder", intermediate, terminal)
    after, terminal_reward, done = world.step(
        {"kind": "actuator", "channel": terminal})
    if not done or terminal_reward not in (0.98, -0.52):
        raise AssertionError("MD33_UNCHARGED_TERMINAL_ACTION")
    result = world.receipt()
    if not 2 <= result["paid_steps"] <= 4:
        raise AssertionError("MD33_PUBLIC_PHYSICAL_STEP_CAP_DRIFT")
    return result


def group_stats(rows):
    if not rows:
        raise AssertionError("MD33_EMPTY_TEST_COHORT")
    def mean(xs):
        return round(math.fsum(x["reward"] for x in xs) / len(xs), 6)
    def subgroup(pred):
        p = [x for x in rows if pred(x)]
        if not p:
            raise AssertionError("MD33_UNBALANCED_TEST_SUBGROUP")
        return mean(p)
    return {
        "episodes": len(rows),
        "mean_net_utility": mean(rows),
        "goal_success_fraction": round(
            sum(x["correct"] for x in rows) / len(rows), 6),
        "charged_physical_steps": sum(x["steps"] for x in rows),
        "charged_physical_diagnostics": sum(x["probes"] for x in rows),
        "per_motif": {motif: subgroup(lambda x: x["motif"] == motif)
                      for motif in STARTS["transfer"][2]},
        "stable_mean": subgroup(lambda x: not x["rewire"]),
        "rewire_mean": subgroup(lambda x: x["rewire"]),
        "public_physical_receipts_sha256": digest(
            [x["trace_sha256"] for x in rows]),
    }


def evaluate(cohort, models):
    first, last, _ = STARTS[cohort]
    if cohort not in ("transfer", "cold"):
        raise AssertionError("MD33_EVALUATION_ONLY_FROZEN_NONOFFICIAL")
    result = {}
    for arm in ARMS:
        model = models.get(arm)
        raw = []
        calls_before = 0 if model is None else model.model_calls
        for first_seed in range(first, last + 1, 4):
            if model is not None:
                model.begin_block()
            for k in range(4):
                seed = first_seed + k
                world = synthetic_world(seed)
                if arm == "handcoded_public_two_probe":
                    receipt = run_public_two_probe(world)
                elif arm == "blind_fixed_terminal_0":
                    receipt = run_public_blind(world)
                elif arm == "privileged_oracle_upper_bound":
                    # Harness-only upper bound; policy models never get spec.
                    _, _, _, rewire, spec = valid_allocation(seed)
                    receipt = run_privileged_oracle(world, spec, rewire)
                else:
                    receipt = run_policy(world, model)
                _, _, motif, rewire, _ = valid_allocation(seed)
                trace = receipt["trace"]
                if len(trace) != receipt["paid_steps"] or not (
                        2 <= len(trace) <= 4):
                    raise AssertionError("MD33_RECEIPT_UNPAID_OR_BAD_LENGTH")
                if [t["action"]["kind"] for t in trace].count(
                        "actuator") != 2:
                    raise AssertionError("MD33_TWO_IRREVERSIBLE_ACTIONS_REQUIRED")
                raw.append({
                    "reward": receipt["net_utility"],
                    "correct": trace[-1]["reward"] == 0.98,
                    "steps": len(trace),
                    "probes": len(trace) - 2,
                    "trace_sha256": receipt["public_trace_sha256"],
                    "motif": motif,
                    "rewire": rewire,
                })
        stats = group_stats(raw)
        stats["model_calls"] = (
            0 if model is None else model.model_calls - calls_before)
        result[arm] = stats
    if any(x["episodes"] != last-first+1 for x in result.values()):
        raise AssertionError("MD33_TEST_COHORT_MISSING_EPISODES")
    return result


def classify(transfer, cold):
    qualified = {
        a: transfer[a]["mean_net_utility"] >= 0.91 and
           cold[a]["mean_net_utility"] >= 0.91
        for a in TRAINED
    }
    if any(qualified.values()):
        outcome = "TRIVIAL_FOR_NOVEL_GAIN_STOP"
    elif max(transfer[a]["mean_net_utility"] for a in TRAINED) <= 0.8:
        outcome = "CONVENTIONAL_CONTROLS_UNDERQUALIFIED_NO_NATIVE_GATE"
    elif any(
        transfer[a]["per_motif"][motif] <
        transfer["blind_fixed_terminal_0"]["per_motif"][motif] + 0.05
        for a in TRAINED
        for motif in STARTS["transfer"][2]):
        outcome = "CONTROL_TRANSFER_MIXED_NO_SCIENCE"
    else:
        outcome = "SYNTHETIC_DEVELOPMENT_HEADROOM_UNVERIFIED"
    return {
        "classification": outcome,
        "strongest_trained_transfer_mean": max(
            transfer[a]["mean_net_utility"] for a in TRAINED),
        "best_public_nonlearning_reference_mean":
            transfer["handcoded_public_two_probe"]["mean_net_utility"],
        "oracle_upper_bound": transfer["privileged_oracle_upper_bound"][
            "mean_net_utility"],
        "qualified_conventional_ceiling_saturators": qualified,
        "scientific_pass": False,
        "native_model_integration_authorized": False,
        "compute_matched_scientifically": False,
    }


def run_development():
    start = time.process_time()
    split = structural_split_audit()
    training, training_custody = public_teacher_blocks("train")
    validation, validation_custody = public_teacher_blocks("validation")
    if training_custody["charged_actions"] != 3072:
        raise AssertionError("MD33_WRONG_PHYSICAL_TRAINING_ACTIONS")
    fitted = {}
    checkpoints = {}
    metrics = {}
    cpu = {}
    for arm, model in (
        (TRAINED[0], EmpiricalCausalControl("bayesian")),
        (TRAINED[1], RecurrentWorldModel()),
        (TRAINED[2], EmpiricalCausalControl("empirical_rl")),
    ):
        begin = time.process_time()
        if arm == TRAINED[1]:
            model.fit(training, validation)
            measure = model.training_report
        else:
            model.fit(training)
            measure = {"fit_public_probe_samples": model.fit_examples,
                       "validation_categorical_nll":
                       model.validation(validation)}
        if model is None:
            raise AssertionError("MD33_UNFITTED_CONVENTIONAL_CONTROL")
        checkpoints[arm] = model.checkpoint()
        metrics[arm] = measure
        cpu[arm] = round(time.process_time() - begin, 4)
        fitted[arm] = model
    train_cpu = time.process_time() - start
    eval_start = time.process_time()
    transfer = evaluate("transfer", fitted)
    evaluation_cpu = time.process_time() - eval_start
    # Restore all control models from frozen trained checkpoints before
    # independent cold-scored sequences. No global weights are updated.
    restored = {
        TRAINED[0]: EmpiricalCausalControl.from_checkpoint(
            json.loads(canonical(checkpoints[TRAINED[0]]))),
        TRAINED[1]: RecurrentWorldModel.from_checkpoint(
            json.loads(canonical(checkpoints[TRAINED[1]]))),
        TRAINED[2]: EmpiricalCausalControl.from_checkpoint(
            json.loads(canonical(checkpoints[TRAINED[2]]))),
    }
    cold_start = time.process_time()
    cold = evaluate("cold", restored)
    cold_cpu = time.process_time() - cold_start
    # A cold-restored second read of the fixed synthetic cold set is a
    # reproducibility check; no parameter/result selection occurs.
    restored_again = {
        TRAINED[0]: EmpiricalCausalControl.from_checkpoint(checkpoints[TRAINED[0]]),
        TRAINED[1]: RecurrentWorldModel.from_checkpoint(checkpoints[TRAINED[1]]),
        TRAINED[2]: EmpiricalCausalControl.from_checkpoint(checkpoints[TRAINED[2]]),
    }
    cold_repeat = evaluate("cold", restored_again)
    for arm in TRAINED:
        if cold_repeat[arm] != cold[arm]:
            raise AssertionError("MD33_COLD_PERSISTENT_MODEL_REPLAY_DRIFT")
    outcome = classify(transfer, cold)
    return {
        "schema": "yggdrasil.dg1-md33-conventional-controls-synthetic.v1",
        "status": "SYNTHETIC_CONVENTIONAL_CONTROL_DIAGNOSTIC_NO_SCIENTIFIC_PASS",
        "official_first_use": False,
        "original_md32_source_unchanged": True,
        "physical_split": split,
        "shared_charged_training": training_custody,
        "charged_validation": validation_custody,
        "train_model_reports": metrics,
        "training_checkpoints": {
            arm: {
                "sha256": digest(checkpoint),
                "bytes": len(canonical(checkpoint).encode("utf-8")),
            } for arm, checkpoint in checkpoints.items()
        },
        "transfer": transfer,
        "cold_restored": cold,
        "cold_replay_byte_equal": True,
        "decision": outcome,
        "cpu_seconds": {
            "whole_process_training_and_validation": round(train_cpu, 4),
            "per_control_training": cpu,
            "one_shot_transfer": round(evaluation_cpu, 4),
            "cold_restored": round(cold_cpu, 4),
        },
        "limitations": (
            "Synthetic-only controls and non-learning physical reference; "
            "whole-process model compute unequal and original Yggdrasil "
            "official science/first-use still forbidden. No native gain."
        ),
    }


def portable_receipt(report):
    """Keep physical action/utility receipt exact, exclude runtime/floating
    model weights and training numerical loss from cross-OS physics parity."""
    return {
        "schema": report["schema"], "status": report["status"],
        "official_first_use": report["official_first_use"],
        "physical_split": report["physical_split"],
        "shared_charged_training": report["shared_charged_training"],
        "charged_validation": report["charged_validation"],
        "transfer": report["transfer"],
        "cold_restored": report["cold_restored"],
        "cold_replay_byte_equal": report["cold_replay_byte_equal"],
        "decision": report["decision"],
    }


if __name__ == "__main__":
    print(canonical(run_development()))
