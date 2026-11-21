"""Gate27 research receipt verification, not an independent learner reproduction.

The full source's deterministic rerun is separately in G29 CI on both platforms.
This audit independently checks frozen thresholds, aggregate arithmetic,
source/held exposure constraints, and negative control classification.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
pre = json.loads((ROOT / "prereg.json").read_text("utf-8"))
res = json.loads((ROOT / "result.json").read_text("utf-8"))
core = (ROOT / "core.py").read_text("utf-8")
run = (ROOT / "run.py").read_text("utf-8")

def close(x, y, eps=3e-8):
    assert abs(x - y) <= eps, ("G27_ARITHMETIC_MISMATCH", x, y)

assert pre["experiment_id"] == "GATE27-INTERFERENCE-RESISTANT-CAUSAL-RULE-TRANSFER-20261120"
assert pre["exact_parent_sha"] == res["parent_commit"] == "28f6ebe1552b52386e407248ddac8d576deb3be1"
assert res["prereg_commit"] == "aeb7418b8ec5f36e306eaa1f722b9c8e72a879e4"
assert res["schema"] == "yggdrasil.gate27.causal-signature-cold-transfer.v1"
assert res["design"]["seeds"] == 64 and res["design"]["related_seeds"] == 32
assert res["design"]["cold_child_processes"] == 192
assert res["design"]["rule_hypotheses"] == 56
assert res["design"]["checkpoint_bytes_ceiling"] == 20000
assert len(res["conditions"]) == 18
assert set(res["conditions"]) == set(pre["frozen_thresholds"])
families = {"shifted_A_B_A": (401000, 32), "stationary": (402000, 16),
            "pure_noise": (403000, 16)}
arms = {"archive", "hazard", "source_recent_bayes", "rolling", "source",
        "all_history", "no_archive", "null"}
for family, (start, count) in families.items():
    row = res["groups"][family]
    assert [row["seed_first"], row["seed_last"], row["trials"]] == [
        start, start + count - 1, count]
    assert row["cold_exact"] == row["functional_exact"] == count
    assert row["source_immutable"] == row["held_disjoint"] == count
    assert row["equal_exposure"] == count
    assert 0 < row["mean_work"] and 0 < row["max_checkpoint_bytes"] <= 20000
    for name in ("B_prequential", "R_prequential", "B_held_reward",
                 "R_held_reward", "R_held_accuracy", "R_held_brier"):
        assert set(row[name]) == arms, name
        assert all(0 <= x <= 1 for x in row[name].values()), name
related = res["groups"]["shifted_A_B_A"]
r = res["summary"]
for label, reference in (
    ("R_held_gain_vs_hazard", "hazard"),
    ("R_held_gain_vs_source_recent_mixture", "source_recent_bayes"),
    ("R_held_gain_vs_recent_global", "rolling"),
    ("R_held_gain_vs_no_archive", "no_archive")):
    close(r[label]["mean"],
          related["R_held_reward"]["archive"] - related["R_held_reward"][reference])
close(r["B_prequential_archive_minus_hazard"]["mean"],
      related["B_prequential"]["archive"] - related["B_prequential"]["hazard"])
close(r["R_prequential_archive_minus_hazard"]["mean"],
      related["R_prequential"]["archive"] - related["R_prequential"]["hazard"])
close(r["R_held_best_action_accuracy"], related["R_held_accuracy"]["archive"])
close(r["noise_R_brier_archive_minus_null"],
      res["groups"]["pure_noise"]["R_held_brier"]["archive"] -
      res["groups"]["pure_noise"]["R_held_brier"]["null"])
assert res["groups"]["stationary"]["false_archive_rejection_trials"] == 6
assert r["stationary_false_rejection"] == 6
assert r["R_held_best_action_accuracy"] == 1
assert all(r[k]["mean"] == 0 and r[k]["ci95"] == [0, 0] for k in (
    "R_held_gain_vs_hazard", "R_held_gain_vs_source_recent_mixture",
    "R_held_gain_vs_recent_global", "R_held_gain_vs_no_archive"))
assert res["groups"]["pure_noise"]["R_held_brier"]["archive"] > (
    res["groups"]["pure_noise"]["R_held_brier"]["null"] + .02)
assert r["stationary_false_rejection"] / 16 > .2
limits = pre["frozen_thresholds"]
conditions = {
    "related_R_held_reward_gain_vs_hazard_min":
        r["R_held_gain_vs_hazard"]["mean"] >= limits["related_R_held_reward_gain_vs_hazard_min"],
    "related_R_held_reward_gain_vs_hazard_ci_lower_positive":
        r["R_held_gain_vs_hazard"]["ci95"][0] > 0,
    "related_R_held_reward_gain_vs_source_recent_mixture_min":
        r["R_held_gain_vs_source_recent_mixture"]["mean"] >= limits["related_R_held_reward_gain_vs_source_recent_mixture_min"],
    "related_R_held_reward_gain_vs_source_recent_mixture_ci_lower_positive":
        r["R_held_gain_vs_source_recent_mixture"]["ci95"][0] > 0,
    "related_R_held_reward_gain_vs_recent_global_min":
        r["R_held_gain_vs_recent_global"]["mean"] >= limits["related_R_held_reward_gain_vs_recent_global_min"],
    "related_R_held_reward_gain_vs_recent_global_ci_lower_positive":
        r["R_held_gain_vs_recent_global"]["ci95"][0] > 0,
    "related_R_unseen_best_action_accuracy_min":
        r["R_held_best_action_accuracy"] >= limits["related_R_unseen_best_action_accuracy_min"],
    "related_B_prequential_regret_vs_hazard_max":
        r["B_prequential_archive_minus_hazard"]["mean"] <= limits["related_B_prequential_regret_vs_hazard_max"],
    "related_R_prequential_regret_vs_hazard_max":
        r["R_prequential_archive_minus_hazard"]["mean"] <= limits["related_R_prequential_regret_vs_hazard_max"],
    "related_R_held_reward_gain_vs_no_archive_min":
        r["R_held_gain_vs_no_archive"]["mean"] >= limits["related_R_held_reward_gain_vs_no_archive_min"],
    "stationary_spurious_archive_rejection_fraction_max":
        r["stationary_false_rejection"]/16 <= limits["stationary_spurious_archive_rejection_fraction_max"],
    "noise_held_brier_regression_vs_null_max":
        r["noise_R_brier_archive_minus_null"] <= limits["noise_held_brier_regression_vs_null_max"],
    "cross_process_checkpoint_exact_all":
        all(v["cold_exact"]==v["trials"] for v in res["groups"].values()),
    "cross_process_functional_replay_all":
        all(v["functional_exact"]==v["trials"] for v in res["groups"].values()),
    "source_archive_unchanged_all":
        all(v["source_immutable"]==v["trials"] for v in res["groups"].values()),
    "held_contexts_out_of_sample_all":
        all(v["held_disjoint"]==v["trials"] for v in res["groups"].values()),
    "equal_public_action_exposure_all":
        all(v["equal_exposure"]==v["trials"] for v in res["groups"].values()),
    "all_work_counts_finite":
        all(v["mean_work"]>0 and v["max_checkpoint_bytes"]<=20000
            for v in res["groups"].values())}
assert conditions == res["conditions"], ("G27_THRESHOLD_LOGIC_DRIFT", conditions, res["conditions"])
assert sum(conditions.values()) == 9 and len(conditions) == 18
assert res["verdict"] == "SCIENTIFIC_NO_GO_STRUCTURAL_TRANSFER"
assert "def update(state, event):" in core and "state[\"source_digest\"] == source_digest" in core
assert "core.update(state, (x, action, y))" in run
assert "subprocess.run(cmd" in run and "core.unpack(input_file.read_bytes())" in run
assert "assert len(unseen) == 32 and not unseen.intersection(exposed)" in run
print("GATE27_RECEIPT_AUDIT_PASS COLD_REUSE_EXACT STRUCTURAL_SCIENTIFIC_NO_GO")
