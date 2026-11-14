"""MD31 one-shot synthetic comparison; no official MD30/31 first-use.

Every environment action is physically charged and every policy starts with
the same frozen public training traces. The harness, but never the policy,
knows synthetic seeds, structural motifs, or the hidden stable/rewire label.
"""
import json
import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dg1-md30-20261114"))
from bayesian_control import (BayesianGraphControl, paid_training_episodes)
from native_tournament import (CausalTournament, PersistentCausalMemory,
                               trained_memory)
from structural_catalog import (TRANSFER_MOTIFS, _distinguishing_probes,
                                synthetic_pair, synthetic_world)
from structural_rewire import canonical, digest
from change_ledger import PaidChangeLedger, PREREG

SEEDS = tuple(range(8301, 8421))
PREFLIGHT = tuple(range(7301, 7313))
ARMS = (
    "evidence_gate",
    "sham_stage1_gate",
    "always_carry_gate",
    "frozen_md30_persistent",
    "frozen_md30_bayesian",
    "fixed_A",
)
MODES = {
    "evidence_gate": "evidence",
    "sham_stage1_gate": "sham_stage1",
    "always_carry_gate": "always_carry",
}
assert PREREG["allocation"]["new_synthetic_scoring_seeds"] == [8301, 8420]
assert PREREG["allocation"]["preflight_fixture_seeds"] == [7301, 7312]


def identifiability_preflight():
    rows = []
    for seed in PREFLIGHT:
        motif = TRANSFER_MOTIFS[(seed - PREFLIGHT[0]) % 3]
        before, after = synthetic_pair(seed, motif)
        different = _distinguishing_probes(before, after)
        if (before.respond((0, 0)) != after.respond((0, 0))
                or not different):
            raise AssertionError("MD31_TASK_NO_GO_UNIDENTIFIABLE_STRUCTURAL_CHANGE")
        stable = synthetic_world(seed, motif, rewire=False)
        changed = synthetic_world(seed, motif, rewire=True)
        action = {"kind": "actuator", "node": 0, "value": 1}
        obs_a, _, done_a = stable.step(action)
        obs_b, _, done_b = changed.step(action)
        if done_a or done_b or obs_a != obs_b or obs_a["phase"] != 1:
            raise AssertionError("MD31_TASK_NO_GO_UNANNOUNCED_CHANGE_LEAKAGE")
        node, value = different[0]
        probe = {"kind": "diagnostic", "node": node, "value": value}
        sensor_a, cost_a, done_a = stable.step(probe)
        sensor_b, cost_b, done_b = changed.step(probe)
        if (done_a or done_b or cost_a != -0.05 or cost_b != -0.05
                or sensor_a["sensor_vector"] == sensor_b["sensor_vector"]):
            raise AssertionError("MD31_TASK_NO_GO_NO_CONSEQUENTIAL_DIAGNOSTIC")
        rows.append({
            "seed": seed, "motif": motif,
            "probe": [node, value],
            "stable_sensor": sensor_a["sensor_vector"],
            "rewire_sensor": sensor_b["sensor_vector"],
        })
    return {
        "fixture_cases": len(rows),
        "all_initial_stage1_public_observations_identical": True,
        "all_paid_internal_diagnostics_distinguish": True,
        "preflight_sha256": digest(rows),
    }


def run_episode(seed, arm, hypotheses, memory, bayesian_prior):
    if type(seed) is not int or seed not in SEEDS:
        raise AssertionError("MD31_UNAUTHORIZED_OR_REUSED_SCIENCE_SEED")
    if arm not in ARMS:
        raise AssertionError("MD31_UNKNOWN_ARM")
    motif = TRANSFER_MOTIFS[(seed - SEEDS[0]) % 3]
    change = seed % 2 == 0
    world = synthetic_world(seed, motif, rewire=change)
    if arm in MODES:
        policy = PaidChangeLedger(hypotheses, memory, MODES[arm])
    elif arm == "frozen_md30_persistent":
        policy = CausalTournament(hypotheses, memory, "persistent")
    elif arm == "frozen_md30_bayesian":
        policy = BayesianGraphControl(hypotheses, bayesian_prior)
    else:
        policy = None
    physical_steps = 0
    while True:
        before = world.observe()
        if before["phase"] == "done":
            break
        action = ({"kind": "actuator", "node": 0, "value": 1}
                  if policy is None else policy.choose(before))
        after, _, done = world.step(action)
        if after["charged_history"][-1]["action"] != action:
            raise AssertionError("MD31_UNCHARGED_POLICY_ACTION")
        if arm in MODES:
            policy.consume(before, action, after)
        elif arm == "frozen_md30_persistent":
            policy.consume(before, action, after)
        elif arm == "frozen_md30_bayesian":
            policy.posterior_step(action, after["charged_history"][-1])
        physical_steps += 1
        if physical_steps > 8:
            raise AssertionError("MD31_PAID_ACTION_CAP_BROKEN")
        if done:
            break
    receipt = world.receipt()
    if receipt["paid_steps"] != physical_steps:
        raise AssertionError("MD31_PHYSICAL_RECEIPT_MISMATCH")
    gate = policy.audit() if arm in MODES else None
    return {
        "seed": seed, "motif": motif,
        "rewire": change,
        "net_reward": receipt["net_utility"],
        "paid_actions": receipt["paid_steps"],
        "paid_diagnostics": sum(
            a["action"]["kind"] == "diagnostic" for a in receipt["trace"]),
        "trace_sha256": receipt["physical_sha256"],
        "gate": gate,
    }


def score_arm(rows):
    if len(rows) != len(SEEDS):
        raise AssertionError("MD31_INCORRECT_EVALUATION_COUNT")
    def mean(pts):
        return round(math.fsum(x["net_reward"] for x in pts) / len(pts), 6)
    motifs = {name: mean([r for r in rows if r["motif"] == name])
              for name in TRANSFER_MOTIFS}
    stable = mean([r for r in rows if not r["rewire"]])
    rewire = mean([r for r in rows if r["rewire"]])
    result = {
        "episodes": len(rows), "mean_reward": mean(rows),
        "motifs": motifs, "stable_mean": stable,
        "rewire_mean": rewire,
        "charged_actions": sum(r["paid_actions"] for r in rows),
        "charged_probes": sum(r["paid_diagnostics"] for r in rows),
        "trace_digest": digest([r["trace_sha256"] for r in rows]),
    }
    if rows[0]["gate"] is not None:
        decisions = {
            "stable_stage0": sum((not r["rewire"]) and
                                 r["gate"]["bank_decision"] == "stage0"
                                 for r in rows),
            "stable_stage1": sum((not r["rewire"]) and
                                 r["gate"]["bank_decision"] == "stage1"
                                 for r in rows),
            "rewire_stage0": sum(r["rewire"] and
                                 r["gate"]["bank_decision"] == "stage0"
                                 for r in rows),
            "rewire_stage1": sum(r["rewire"] and
                                 r["gate"]["bank_decision"] == "stage1"
                                 for r in rows),
        }
        result["change_detection_confusion"] = decisions
        result["change_detection_accuracy"] = round(
            (decisions["stable_stage0"] + decisions["rewire_stage1"]) / 120, 6)
        result["paid_gate_probe_sha256"] = digest(
            [r["gate"]["phase1_paid_probe"] for r in rows])
    return result


def paired_bootstrap_lower(deltas):
    """Frozen 2,000 pair-level resamples; sort, report low 2.5% bound."""
    if len(deltas) != 120:
        raise AssertionError("MD31_BAD_PAIRED_BOOTSTRAP_COUNT")
    rng = random.Random(83131)
    draws = sorted(math.fsum(deltas[rng.randrange(120)]
                             for _ in range(120)) / 120
                   for _ in range(2000))
    return round(draws[49], 6)


def classify(rows, summaries):
    baseline = max(("frozen_md30_bayesian", "frozen_md30_persistent"),
                   key=lambda k: (summaries[k]["mean_reward"], k))
    candidate = rows["evidence_gate"]
    ref = rows[baseline]
    differences = [x["net_reward"] - y["net_reward"]
                   for x, y in zip(candidate, ref)]
    delta = round(math.fsum(differences) / len(differences), 6)
    ci_lower = paired_bootstrap_lower(differences)
    per_motif = {
        motif: round(math.fsum(
            a["net_reward"] - b["net_reward"]
            for a, b in zip(candidate, ref) if a["motif"] == motif) / 40, 6)
        for motif in TRANSFER_MOTIFS
    }
    regimes = {
        name: round(math.fsum(a["net_reward"] - b["net_reward"]
                     for a, b in zip(candidate, ref)
                     if a["rewire"] is change) / 60, 6)
        for name, change in (("stable", False), ("rewire", True))
    }
    ablation_deltas = {
        name: round(summaries["evidence_gate"]["mean_reward"] -
                    summaries[name]["mean_reward"], 6)
        for name in ("sham_stage1_gate", "always_carry_gate")
    }
    change_accuracy = summaries["evidence_gate"]["change_detection_accuracy"]
    threshold_met = (
        delta >= 0.05 and ci_lower > 0.0
        and min(per_motif.values()) >= -0.03
        and min(regimes.values()) >= -0.03
        and change_accuracy >= 0.65
        and min(ablation_deltas.values()) >= 0.03
    )
    return {
        "chosen_strongest_frozen_reference": baseline,
        "paired_mean_delta": delta,
        "paired_bootstrap_95pct_lower": ci_lower,
        "per_motif_deltas": per_motif,
        "stable_rewire_deltas": regimes,
        "vs_matched_paid_gate_ablations": ablation_deltas,
        "change_detection_accuracy": change_accuracy,
        "all_development_thresholds_met": threshold_met,
        "classification": (
            "DEVELOPMENT_ONLY_CANDIDATE_NEEDS_SEPARATE_SCIENCE"
            if threshold_met else "DEVELOPMENT_MIXED_NO_PROMOTION"
        ),
        "official_scientific_pass": False,
    }


def run_development():
    start = time.process_time()
    preflight = identifiability_preflight()
    # This is the same earlier physically charged training set for EVERY
    # policy; neither hidden physics nor official seeds are used in training.
    sessions, custody = paid_training_episodes()
    hypotheses, memory = trained_memory(sessions, custody)
    baseline = BayesianGraphControl(hypotheses).fit(sessions)
    fit_seconds = time.process_time() - start
    checkpoint = json.loads(canonical(memory.checkpoint()))
    from_cold = PersistentCausalMemory.from_checkpoint(hypotheses, checkpoint)
    if from_cold.checkpoint() != checkpoint:
        raise AssertionError("MD31_COLD_CHECKPOINT_DIFFERENCE")
    work_start = time.process_time()
    rows = {arm: [] for arm in ARMS}
    for seed in SEEDS:
        same_probe = None
        for arm in ARMS:
            rec = run_episode(seed, arm, hypotheses, from_cold, baseline.prior)
            if arm in MODES:
                paid_probe = rec["gate"]["phase1_paid_probe"]
                if same_probe is None:
                    same_probe = paid_probe
                if same_probe != paid_probe:
                    raise AssertionError("MD31_MATCHED_GATE_PHYSICAL_PROBE_DRIFT")
            rows[arm].append(rec)
    results = {name: score_arm(cases) for name, cases in rows.items()}
    verdict = classify(rows, results)
    witness_before = run_episode(SEEDS[0], "evidence_gate", hypotheses,
                                 memory, baseline.prior)
    witness_cold = run_episode(SEEDS[0], "evidence_gate", hypotheses,
                               from_cold, baseline.prior)
    if witness_before != witness_cold:
        raise AssertionError("MD31_COLD_PHYSICAL_ACTION_REPLAY_DRIFT")
    return {
        "schema": "yggdrasil.dg1-md31-paid-change-ledger-development.v1",
        "status": "SYNTHETIC_DEV_ONLY_NO_OFFICIAL_FIRST_USE",
        "prereg_sha256": digest(PREREG),
        "official_data_used": False,
        "training": {
            "episodes": len(sessions),
            "charged_actions": custody["charged_steps"],
            "training_trace_sha256": custody["physical_sha256"],
            "hypothesis_count": len(hypotheses),
            "native_checkpoint_sha256": digest(checkpoint),
            "bayesian_checkpoint_sha256": digest(baseline.checkpoint()),
            "native_checkpoint_bytes": len(canonical(checkpoint).encode("utf-8")),
        },
        "task_preflight": preflight,
        "evaluation_seed_range": [SEEDS[0], SEEDS[-1]],
        "frozen_arms": results,
        "paired_verdict": verdict,
        "cold_replay": {
            "identical": True,
            "witness_trace_sha256": witness_before["trace_sha256"],
        },
        "cpu_seconds": {
            "task_preflight_and_training": round(fit_seconds, 4),
            "evaluation": round(time.process_time() - work_start, 4),
        },
        "limitations": (
            "Independent synthetic successor study, not official science; "
            "frozen MD30 outcomes unaltered; no parameter tuning after "
            "first MD31 outcomes; no native Yggdrasil integration."
        ),
    }


def portable_receipt(report):
    return {k: v for k, v in report.items() if k != "cpu_seconds"}


if __name__ == "__main__":
    print(canonical(run_development()))
