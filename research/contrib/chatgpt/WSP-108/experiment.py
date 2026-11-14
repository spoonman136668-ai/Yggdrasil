"""WSP108 preregistered causal-action feedback and unfamiliar-world transfer DEV.

All arms see the same ten interventions per world, observe only feedback,
predict on withheld novel action scenes, and freeze all predictions *before*
the evaluator opens any withheld query oracle truth. Original science data
never opened, and this limited synthetic benchmark cannot prove AGI.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import argparse
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from world import (
    KINDS, FIT_SEEDS, TRANSFER_SEEDS, QUERIES_PER_WORLD, entity,
    hidden_law, oracle, path_features, query_scene, support_evidence,
)
from learners import NumericRuleWeights, SymbolicRuleControl, ConventionalLogistic

ARMS = (
    "numeric_direct", "symbolic_exact", "conventional_logistic",
    "conventional_max_pool", "no_feedback", "rotated_feedback",
)
MAX_WALL_SECONDS = 120


def context_key(seed: int) -> str:
    return f"world-{seed}"


def train_world(seed, numeric, symbolic, conventional, rotated):
    context = context_key(seed)
    support = support_evidence(seed)
    conventional_support = []
    labels = [observed for _, _, _, observed in support[:9]]
    for i, (scene, _before, after, observation) in enumerate(support):
        conventional_support.append((after, observation))
        numeric.program(context, after, observation)
        if i < 9:
            symbolic.observe(context, KINDS[i], observation)
            rotated.program(context, after, labels[(i + 1) % 9])
    if not numeric.complete(context) or not symbolic.complete(context):
        raise AssertionError("insufficient observed support coverage")
    if not rotated.complete(context):
        raise AssertionError("rotated-label negative did not receive full budget")
    conventional.fit(context, tuple(conventional_support))
    return {
        "conventional_gradient_inf_norm":
            conventional.diagnostics[context]["gradient_inf_norm"],
        "conventional_newton_steps": conventional.diagnostics[context]["newton_steps"],
        "observed_support_actions": len(support),
        "observed_singleton_actions": len(support) - 1,
    }


def predict_all_arms(seed, scene, numeric, symbolic, conventional, rotated):
    context = context_key(seed)
    before = scene.before
    after = scene.after()
    left = path_features(before, scene.source, scene.target)
    right = path_features(after, scene.source, scene.target)
    def collect(features, edges):
        return {
            "numeric_direct": numeric.predict(context, features),
            "symbolic_exact": symbolic.predict_edges(context, edges,
                                                     scene.source, scene.target),
            "conventional_logistic": conventional.predict(context, features),
            "conventional_max_pool": conventional.predict(context, features,
                                                          max_pool=True),
            "no_feedback": False,
            "rotated_feedback": rotated.predict(context, features),
        }
    return {
        "seed": seed, "scene": scene.scene_id,
        "before": collect(left, before),
        "after": collect(right, after),
    }


def score_cohort(predictions):
    """Only called after predictions sealed and after all training is over."""
    by_arm = {
        arm: {
            "total": 0, "before_correct": 0, "after_correct": 0,
            "changed_correct": 0,
            "actual_changed_total": 0, "actual_changed_correct": 0,
            "actual_unchanged_total": 0, "actual_unchanged_correct": 0,
        } for arm in ARMS
    }
    actual_post_positive = 0
    actual_pre_positive = 0
    for record in predictions:
        seed, index = record["seed"], record["scene"]
        scene = query_scene(seed, index)
        truth_before = oracle(seed, scene.before, scene.source, scene.target)
        truth_after = oracle(seed, scene.after(), scene.source, scene.target)
        changed = truth_before != truth_after
        actual_pre_positive += int(truth_before)
        actual_post_positive += int(truth_after)
        for arm in ARMS:
            pred_before = record["before"][arm]
            pred_after = record["after"][arm]
            result = by_arm[arm]
            result["total"] += 1
            result["before_correct"] += int(pred_before == truth_before)
            result["after_correct"] += int(pred_after == truth_after)
            correct_change = (pred_before != pred_after) == changed
            result["changed_correct"] += int(correct_change)
            category = "actual_changed" if changed else "actual_unchanged"
            result[category + "_total"] += 1
            result[category + "_correct"] += int(correct_change)
    for arm, result in by_arm.items():
        n = result["total"]
        if n == 0 or result["actual_changed_total"] < 10 or (
                result["actual_unchanged_total"] < 10):
            raise ValueError("frozen intervention cohort lacks diagnostic headroom")
        for count_field, suffix in (
            ("before_correct", "before_accuracy"),
            ("after_correct", "after_accuracy"),
            ("changed_correct", "action_change_accuracy"),
        ):
            result[suffix] = result[count_field] / n
        for label in ("actual_changed", "actual_unchanged"):
            result[label + "_accuracy"] = (
                result[label + "_correct"] / result[label + "_total"])
    return {
        "queries": len(predictions),
        "actual_before_positive": actual_pre_positive,
        "actual_after_positive": actual_post_positive,
        "arms": by_arm,
    }


def evaluate():
    started = time.monotonic()
    cpu_start = time.process_time()
    numeric, symbolic = NumericRuleWeights(), SymbolicRuleControl()
    conventional, rotated = ConventionalLogistic(), NumericRuleWeights()
    evidence = []
    predictions = {"fit": [], "transfer": []}
    arm_nanos = defaultdict(int)
    all_seen_entity_ids: set[str] = set()
    for cohort_name, seeds in (("fit", FIT_SEEDS), ("transfer", TRANSFER_SEEDS)):
        for seed in seeds:
            observations = train_world(seed, numeric, symbolic,
                                       conventional, rotated)
            evidence.append((seed, observations))
            for i in range(QUERIES_PER_WORLD):
                if time.monotonic() - started > MAX_WALL_SECONDS:
                    raise TimeoutError("frozen causal benchmark time ceiling exceeded")
                scene = query_scene(seed, i)
                if scene.source in all_seen_entity_ids or scene.target in all_seen_entity_ids:
                    raise AssertionError("novel-world entity identity leaked between scenes")
                all_seen_entity_ids.update((scene.source, scene.target))
                tick = time.process_time_ns()
                pred = predict_all_arms(seed, scene, numeric, symbolic,
                                        conventional, rotated)
                arm_nanos["combined_all_arms"] += time.process_time_ns() - tick
                predictions[cohort_name].append(pred)

    # Seal EVERY model prediction across BOTH cohorts before opening any
    # withheld query consequence labels or evaluator-only latent law patterns.
    sealed = {}
    for name in ("fit", "transfer"):
        raw = json.dumps(predictions[name], sort_keys=True,
                         separators=(",", ":"), ensure_ascii=True)
        sealed[name] = sha256(raw.encode("ascii")).hexdigest()

    # Cold weight restoration after training 24 independent latent laws, before
    # any test oracle read. The first training world's knowledge must persist.
    snapshot = numeric.snapshot()
    restored = NumericRuleWeights.restore(snapshot)
    cold_control = conventional.cold_copy()
    for name, records in predictions.items():
        for record in records:
            scene = query_scene(record["seed"], record["scene"])
            context = context_key(record["seed"])
            f_before = path_features(scene.before, scene.source, scene.target)
            f_after = path_features(scene.after(), scene.source, scene.target)
            if (restored.predict(context, f_before) != record["before"]["numeric_direct"] or
                    restored.predict(context, f_after) != record["after"]["numeric_direct"] or
                    cold_control.predict(context, f_before) !=
                        record["before"]["conventional_logistic"] or
                    cold_control.predict(context, f_after, max_pool=True) !=
                        record["after"]["conventional_max_pool"]):
                raise AssertionError("cold retention/prediction parity lost after interference")

    # Restore snapshot validation explicitly rejects mutation, even if valid JSON.
    tampered = json.loads(snapshot)
    first_context = sorted(tampered["payload"])[0]
    tampered["payload"][first_context]["weights"][0][0] = 9.0
    tamper_rejected = False
    try:
        NumericRuleWeights.restore(json.dumps(tampered))
    except ValueError:
        tamper_rejected = True
    if not tamper_rejected:
        raise AssertionError("tampered weight record was accepted")

    # The evaluator-only oracle is FIRST read for query labels here.
    metrics = {name: score_cohort(predictions[name])
               for name in ("fit", "transfer")}
    transfer = metrics["transfer"]["arms"]
    numeric_transfer = transfer["numeric_direct"]
    symbolic_transfer = transfer["symbolic_exact"]
    maxpool_transfer = transfer["conventional_max_pool"]
    if (numeric_transfer["after_correct"] != symbolic_transfer["after_correct"] or
            numeric_transfer["changed_correct"] != symbolic_transfer["changed_correct"]):
        raise AssertionError("numerical and independent symbolic parity broken")
    fit_laws = {hidden_law(s) for s in FIT_SEEDS}
    transfer_laws = {hidden_law(s) for s in TRANSFER_SEEDS}
    novel_patterns = sum(hidden_law(s) not in fit_laws for s in TRANSFER_SEEDS)

    # Policy is strictly DEV even if one implementation reaches 100%.
    classification = ("DEV_CAUSAL_RULE_COMPOSITION_PARITY"
                      if numeric_transfer["after_accuracy"] == 1.0 and
                         numeric_transfer["action_change_accuracy"] == 1.0 and
                         symbolic_transfer["after_accuracy"] == 1.0 and
                         maxpool_transfer["after_accuracy"] == 1.0 and
                         maxpool_transfer["action_change_accuracy"] == 1.0 and
                         numeric_transfer["after_correct"] >
                            transfer["rotated_feedback"]["after_correct"]
                      else "DEV_CAUSAL_RULE_COMPOSITION_NEGATIVE")
    return {
        "schema": "wsp108.prospective-typed-causal-transfer-dev-result.v1",
        "classification": classification,
        "scientific_pass": False,
        "real_causal_world_generalization_proven": False,
        "direct_weight_superiority_proven": False,
        "original_protected_first_use": False,
        "historical_wikidata_or_official_validation_test_read": False,
        "source_parent_sha": "f06b9e87417deb69a8f6e3995e27cc08909b934d",
        "worlds_fit": len(FIT_SEEDS),
        "worlds_unfamiliar_transfer": len(TRANSFER_SEEDS),
        "novel_transfer_law_patterns_vs_fit": novel_patterns,
        "distinct_fit_law_patterns": len(fit_laws),
        "distinct_transfer_law_patterns": len(transfer_laws),
        "observed_intervention_feedback_per_world": 10,
        "worlds_cold_retained_after_interference": len(FIT_SEEDS) + len(TRANSFER_SEEDS),
        "numeric_programmed_weights_count": len(numeric.weights) * 9,
        "conventional_trained_coefficients_count": len(conventional.coefficients) * 10,
        "conventional_support_fit_min_accuracy": min(
            v["support_accuracy"] for v in conventional.diagnostics.values()),
        "conventional_support_max_gradient_inf_norm": max(
            v["gradient_inf_norm"] for v in conventional.diagnostics.values()),
        "conventional_max_newton_steps": max(
            v["newton_steps"] for v in conventional.diagnostics.values()),
        "cold_restore_exact_parity": True,
        "tampered_snapshot_rejected": tamper_rejected,
        "all_prediction_sha256_frozen_before_query_labels": sealed,
        "metrics": metrics,
        "combined_arm_inference_cpu_seconds": arm_nanos["combined_all_arms"] / 1e9,
        "whole_process_cpu_seconds": time.process_time() - cpu_start,
        "whole_process_wall_seconds": time.monotonic() - started,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--predeclared-synthetic-dev-only", action="store_true",
                    required=True)
    ap.parse_args()
    result = evaluate()
    print("WSP108_CAUSAL_TRANSFER_DEV=" +
          json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)
