"""Gate27 frozen evaluator and true Python subprocess cold checkpoints.

The experiment uses 64 prospectively held seeds. Every arm sees the same actual
public action/outcome exposures. No hidden family labels enter the learner.
Never mutate canonical Yggdrasil checkpoint or accepted refs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import core

SELF = Path(__file__).resolve()
HERE = SELF.parent
COHORTS = (("shifted_A_B_A", 401000, 32),
           ("stationary", 402000, 16),
           ("pure_noise", 403000, 16))
ARMS = ("archive", "hazard", "source_recent_bayes", "rolling",
        "source", "all_history", "no_archive", "null")


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def identity(state):
    return hashlib.sha256(core.pack(state)).hexdigest()


def phase_test(state, seed, family, phase):
    """Prequential action-outcome predictions, then public feedback only."""
    losses = {k: 0.0 for k in ARMS}
    false_route = False
    observations = list(core.training_rows(seed, family, phase))
    assert len(observations) == 64
    for x, action, y in observations:
        p = core.forecasts(state, x, action)
        assert set(p) == set(ARMS)
        for arm in ARMS:
            losses[arm] += (p[arm] - y) ** 2 / 64
        core.update(state, (x, action, y))
        if core.archive_weight(state) < .5:
            false_route = True

    held = {k: {"reward": 0.0, "accuracy": 0.0, "brier": 0.0}
            for k in ARMS}
    unseen = {row[0] for row in core.probes(seed, family, phase)}
    exposed = {row[0] for step in ("A", "B", "R")
               for row in core.training_rows(seed, family, step)}
    assert len(unseen) == 32 and not unseen.intersection(exposed)
    for x, index in core.probes(seed, family, phase):
        for arm in ARMS:
            p0 = core.forecasts(state, x, 0)[arm]
            p1 = core.forecasts(state, x, 1)[arm]
            action = int(p1 > p0)
            realized = core.reward(seed, family, phase, x, action, index, 998)
            held[arm]["reward"] += realized / 32
            held[arm]["brier"] += ((p1 if action else p0) - realized) ** 2 / 32
            if family != "pure_noise":
                held[arm]["accuracy"] += int(
                    action == core.preferred(seed, family, phase, x)) / 32
    return {
        "prequential_brier": {k: round(v, 8) for k, v in losses.items()},
        "held": {arm: {metric: round(v, 8)
                       for metric, v in metrics.items()}
                 for arm, metrics in held.items()},
        "false_archive_rejection": false_route,
        "held_context_disjoint": True,
        "equal_action_exposure": True,
        "hypotheses_evaluated": state["work"],
        "source_immutable": core.source_digest(state["source"])
                            == state["source_digest"],
    }


def stage(seed, family, phase, input_file, output_file):
    assert family in dict((fam, n) for fam, first, n in COHORTS)
    if phase == "A":
        if input_file is not None or output_file is None:
            raise ValueError("G27_INVALID_A_PATHS")
        state = core.init(list(core.training_rows(seed, family, "A")))
        metrics = {}
    else:
        if input_file is None:
            raise ValueError("G27_COLD_CHECKPOINT_REQUIRED")
        state = core.unpack(input_file.read_bytes())
        metrics = phase_test(state, seed, family, phase)
    payload = core.pack(state)
    if output_file is not None:
        output_file.write_bytes(payload)
    checks = [(x, tuple(round(core.forecasts(state, x, a)["archive"], 8)
                         for a in (0, 1)))
              for x in (0, 33, 79, 141, 201, 255)]
    return {"phase": phase, "pid": os.getpid(), "checkpoint_digest":
            hashlib.sha256(payload).hexdigest(), "checkpoint_bytes": len(payload),
            "source_digest": state["source_digest"], "functional_readouts": checks,
            "metrics": metrics}


def child(seed, family, phase, infile=None, outfile=None):
    cmd = [sys.executable, "-B", str(SELF), "--child", phase,
           "--seed", str(seed), "--family", family]
    if infile is not None:
        cmd.extend(["--input", str(infile)])
    if outfile is not None:
        cmd.extend(["--output", str(outfile)])
    p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True,
                       timeout=120, check=False)
    if p.returncode != 0:
        raise RuntimeError("G27_CHILD_FAILURE_" + phase + ": " +
                           p.stderr[-600:])
    value = json.loads(p.stdout)
    if value["phase"] != phase or value["pid"] == os.getpid():
        raise AssertionError("G27_PROCESS_IDENTITY")
    return value


def pair_diff(rows, arm_a, arm_b, section, metric):
    values = [row[section][metric][arm_a] - row[section][metric][arm_b]
              if section == "prequential" else
              row[section][arm_a][metric] - row[section][arm_b][metric]
              for row in rows]
    n = len(values)
    mean = sum(values) / n
    var = sum((x - mean) ** 2 for x in values) / (n - 1)
    margin = 1.96 * (var / n) ** .5
    return {"mean": round(mean, 8),
            "ci95": [round(mean - margin, 8), round(mean + margin, 8)]}


def aggregate():
    groups = {}
    related = []
    total = 0
    for family, first, count in COHORTS:
        outcomes = []
        for seed in range(first, first + count):
            with tempfile.TemporaryDirectory(prefix="ygg-g27-") as folder:
                a_file = Path(folder) / "source.checkpoint"
                b_file = Path(folder) / "interference.checkpoint"
                cold_a = child(seed, family, "A", outfile=a_file)
                cold_b = child(seed, family, "B", infile=a_file, outfile=b_file)
                cold_r = child(seed, family, "R", infile=b_file)
                pids = [cold_a["pid"], cold_b["pid"], cold_r["pid"]]
                if len(set(pids)) != 3:
                    raise AssertionError("G27_THREE_DISTINCT_CHILD_PROCESSES")
                source_bytes = a_file.read_bytes()
                warm = core.init(list(core.training_rows(seed, family, "A")))
                if core.pack(warm) != source_bytes:
                    raise AssertionError("G27_A_WARM_COLD_DIFFER")
                before_src = warm["source_digest"]
                b_warm = phase_test(warm, seed, family, "B")
                if core.pack(warm) != b_file.read_bytes():
                    raise AssertionError("G27_B_WARM_COLD_DIFFER")
                r_warm = phase_test(warm, seed, family, "R")
                if cold_b["metrics"] != b_warm or cold_r["metrics"] != r_warm:
                    raise AssertionError("G27_FUNCTIONAL_WARM_COLD_DIFFER")
                if identity(warm) != cold_r["checkpoint_digest"]:
                    raise AssertionError("G27_R_WARM_COLD_CHECKPOINT_DIFFER")
                if not (before_src == cold_a["source_digest"] ==
                        cold_b["source_digest"] == cold_r["source_digest"] ==
                        warm["source_digest"]):
                    raise AssertionError("G27_SOURCE_MEMORY_CHANGED")
                if len(source_bytes) > 20000 or b_file.stat().st_size > 20000:
                    raise AssertionError("G27_CAPACITY_EXCEEDED")
                if cold_b["checkpoint_bytes"] > 20000 or cold_r["checkpoint_bytes"] > 20000:
                    raise AssertionError("G27_CHECKPOINT_CAPACITY_EXCEEDED")
                outcomes.append({
                    "seed": seed, "process_identity": True,
                    "cold_state_exact": True, "functional_replay_exact": True,
                    "source_immutable": True,
                    "equal_public_action_exposure": b_warm["equal_action_exposure"]
                        and r_warm["equal_action_exposure"],
                    "held_disjoint": b_warm["held_context_disjoint"]
                        and r_warm["held_context_disjoint"],
                    "B": b_warm, "R": r_warm,
                    "source_bytes": len(source_bytes),
                    "B_bytes": cold_b["checkpoint_bytes"],
                    "R_bytes": cold_r["checkpoint_bytes"]
                })
                total += 1
        if family == "shifted_A_B_A":
            related = outcomes
        avg = lambda fn: round(sum(fn(t) for t in outcomes) / count, 8)
        groups[family] = {
            "trials": count, "seed_first": first, "seed_last": first + count - 1,
            "B_prequential": {arm: avg(lambda t, arm=arm:
                                        t["B"]["prequential_brier"][arm])
                               for arm in ARMS},
            "R_prequential": {arm: avg(lambda t, arm=arm:
                                        t["R"]["prequential_brier"][arm])
                               for arm in ARMS},
            "B_held_reward": {arm: avg(lambda t, arm=arm:
                                       t["B"]["held"][arm]["reward"])
                              for arm in ARMS},
            "R_held_reward": {arm: avg(lambda t, arm=arm:
                                       t["R"]["held"][arm]["reward"])
                              for arm in ARMS},
            "R_held_accuracy": {arm: avg(lambda t, arm=arm:
                                         t["R"]["held"][arm]["accuracy"])
                                for arm in ARMS},
            "R_held_brier": {arm: avg(lambda t, arm=arm:
                                      t["R"]["held"][arm]["brier"])
                             for arm in ARMS},
            "false_archive_rejection_trials": sum(
                t["B"]["false_archive_rejection"] or t["R"]["false_archive_rejection"]
                for t in outcomes),
            "cold_exact": sum(t["cold_state_exact"] for t in outcomes),
            "functional_exact": sum(t["functional_replay_exact"] for t in outcomes),
            "source_immutable": sum(t["source_immutable"] for t in outcomes),
            "held_disjoint": sum(t["held_disjoint"] for t in outcomes),
            "equal_exposure": sum(t["equal_public_action_exposure"] for t in outcomes),
            "mean_work": avg(lambda t: t["R"]["hypotheses_evaluated"]),
            "max_checkpoint_bytes": max(
                max(t["source_bytes"], t["B_bytes"], t["R_bytes"]) for t in outcomes)
        }
    assert total == 64 and len(related) == 32
    def paired(a, b, phase="R", section="held", metric="reward"):
        return pair_diff([{"prequential": t[phase]["prequential_brier"],
                           "held": t[phase]["held"]} for t in related],
                         a, b, section, metric)
    r_h = paired("archive", "hazard")
    r_mix = paired("archive", "source_recent_bayes")
    r_roll = paired("archive", "rolling")
    b_reg = paired("archive", "hazard", "B", "prequential", "brier")
    r_reg = paired("archive", "hazard", "R", "prequential", "brier")
    r_no = paired("archive", "no_archive")
    g_stationary = groups["stationary"]
    g_noise = groups["pure_noise"]
    conditions = {
        "related_R_held_reward_gain_vs_hazard_min": r_h["mean"] >= .02,
        "related_R_held_reward_gain_vs_hazard_ci_lower_positive":
            r_h["ci95"][0] > 0,
        "related_R_held_reward_gain_vs_source_recent_mixture_min":
            r_mix["mean"] >= .01,
        "related_R_held_reward_gain_vs_source_recent_mixture_ci_lower_positive":
            r_mix["ci95"][0] > 0,
        "related_R_held_reward_gain_vs_recent_global_min": r_roll["mean"] >= .02,
        "related_R_held_reward_gain_vs_recent_global_ci_lower_positive":
            r_roll["ci95"][0] > 0,
        "related_R_unseen_best_action_accuracy_min":
            groups["shifted_A_B_A"]["R_held_accuracy"]["archive"] >= .70,
        "related_B_prequential_regret_vs_hazard_max": b_reg["mean"] <= .02,
        "related_R_prequential_regret_vs_hazard_max": r_reg["mean"] <= .02,
        "related_R_held_reward_gain_vs_no_archive_min": r_no["mean"] >= .02,
        "stationary_spurious_archive_rejection_fraction_max":
            g_stationary["false_archive_rejection_trials"] / 16 <= .20,
        "noise_held_brier_regression_vs_null_max":
            g_noise["R_held_brier"]["archive"] -
            g_noise["R_held_brier"]["null"] <= .02,
        "cross_process_checkpoint_exact_all":
            all(v["cold_exact"] == v["trials"] for v in groups.values()),
        "cross_process_functional_replay_all":
            all(v["functional_exact"] == v["trials"] for v in groups.values()),
        "source_archive_unchanged_all":
            all(v["source_immutable"] == v["trials"] for v in groups.values()),
        "held_contexts_out_of_sample_all":
            all(v["held_disjoint"] == v["trials"] for v in groups.values()),
        "equal_public_action_exposure_all":
            all(v["equal_exposure"] == v["trials"] for v in groups.values()),
        "all_work_counts_finite":
            all(v["mean_work"] > 0 and v["max_checkpoint_bytes"] <= 20000
                for v in groups.values()),
    }
    summary = {
        "R_held_gain_vs_hazard": r_h,
        "R_held_gain_vs_source_recent_mixture": r_mix,
        "R_held_gain_vs_recent_global": r_roll,
        "B_prequential_archive_minus_hazard": b_reg,
        "R_prequential_archive_minus_hazard": r_reg,
        "R_held_gain_vs_no_archive": r_no,
        "R_held_best_action_accuracy": groups["shifted_A_B_A"]["R_held_accuracy"]["archive"],
        "stationary_false_rejection": g_stationary["false_archive_rejection_trials"],
        "noise_R_brier_archive_minus_null":
            round(g_noise["R_held_brier"]["archive"] -
                  g_noise["R_held_brier"]["null"], 8),
    }
    return {
        "schema": "yggdrasil.gate27.causal-signature-cold-transfer.v1",
        "prereg_commit": "aeb7418b8ec5f36e306eaa1f722b9c8e72a879e4",
        "parent_commit": "28f6ebe1552b52386e407248ddac8d576deb3be1",
        "design": {"seeds": 64, "related_seeds": 32, "cold_child_processes": 192,
                   "source_A_events": 96, "B_events": 64, "R_events": 64,
                   "held_per_phase": 32, "rule_hypotheses": len(core.HYP),
                   "checkpoint_bytes_ceiling": 20000},
        "groups": groups, "summary": summary,
        "conditions": conditions,
        "verdict": "PROVISIONAL_SYNTHETIC_TRANSFER_SIGNAL" if all(conditions.values())
                   else "SCIENTIFIC_NO_GO_STRUCTURAL_TRANSFER",
        "limitations": {"native_amalgam_integration": False,
                        "native_model_first_use": False,
                        "process_exit_cold_state": True,
                        "real_world_transfer": False,
                        "equal_compute": False,
                        "active_policy_learned": False,
                        "general_intelligence": False,
                        "accepted_checkpoint_promotion": False}
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", choices=["A", "B", "R"])
    parser.add_argument("--seed", type=int)
    parser.add_argument("--family", choices=[f for f, _, _ in COHORTS])
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.child:
        if args.seed is None or args.family is None:
            raise ValueError("G27_MISSING_CHILD_SEED_OR_FAMILY")
        result = stage(args.seed, args.family, args.child, args.input, args.output)
        print(canon(result))
    else:
        result = aggregate()
        if args.verify:
            expected = json.loads(args.verify.read_text(encoding="utf-8"))
            if result != expected:
                raise AssertionError("GATE27_EXACT_RESULT_MISMATCH")
            print("GATE27_EXACT_REPLAY_PASS " + result["verdict"])
        else:
            print("GATE27_PRIMARY_JSON " + canon(result))


if __name__ == "__main__":
    main()
