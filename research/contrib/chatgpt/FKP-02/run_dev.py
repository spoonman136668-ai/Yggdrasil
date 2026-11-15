"""FKP-02 original DEV-only (200..215) actual causal-law selection, blinded held labels.

All 16 outcomes per world come from genuine PublicCausalWorld.observe() calls.
The held evaluator is invoked ONLY AFTER predictions from every arm are sealed
as immutable tuples. No protected owner key, original primary world, paid API,
scientific first-use, native model update or evaluator answer flows into fit().
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import PublicCausalWorld
from foundation import acquire_foundation_bank, compose_generic_programs
from learner import fit, predict, cold_roundtrip, hypothesis_functions
from audit_headroom import signature_pair, fit_and_score

DEV = range(200, 216)


def train_budgeted_logistic(xs: tuple[int, ...], ys: tuple[int, ...]) -> list[list[float]]:
    """Independent fixed-budget conventional logistic control, NOT a converged claim."""
    weights = []
    for effect in range(4):
        w = [0.0] * 17  # 16 binary inputs and bias
        for _ in range(1000):
            grads = [0.0] * 17
            for x, y in zip(xs, ys):
                signal = w[16] + sum(w[i] for i in range(16) if (x >> i) & 1)
                prob = 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, signal))))
                err = prob - ((y >> effect) & 1)
                grads[16] += err
                for i in range(16):
                    if (x >> i) & 1:
                        grads[i] += err
            for i in range(17):
                grads[i] = grads[i] / 16 + (0.001 * w[i] if i < 16 else 0.0)
                w[i] -= 0.4 * grads[i]
        weights.append(w)
    return weights


def predict_logistic(weights: list[list[float]], x: int) -> int:
    value = 0
    for output, w in enumerate(weights):
        signal = w[16] + sum(w[i] for i in range(16) if (x >> i) & 1)
        value |= int(signal > 0.0) << output
    return value


def exact_reference_predictions(
    xs: tuple[int, ...], ys: tuple[int, ...], held: tuple[int, ...], family: str
) -> tuple[int, ...]:
    # Deliberately generous source-family-aware exact reference, independent
    # algorithm and supplied the family. Its family prior is NOT given to B.
    options = tuple(signature_pair(xs, held, family))
    predictions = []
    for output in range(4):
        target = sum(((y >> output) & 1) << i for i, y in enumerate(ys))
        effect_predictions, n_consistent = fit_and_score(options, target, 0, 16)
        assert n_consistent >= 1
        predictions.append(effect_predictions)
    return tuple(sum(predictions[out][i] << out for out in range(4))
                 for i in range(len(held)))


def flat_unstructured_predictions(ys: tuple[int, ...], held: tuple[int, ...]) -> tuple[int, ...]:
    # Deliberately weak diagnostic, never substitute for the exact comparator.
    mode = sum((sum((y >> output) & 1 for y in ys) > 8) << output
               for output in range(4))
    return (mode,) * len(held)


def measured_accuracy(predictions: tuple[int, ...], observed_labels: tuple[int, ...]) -> float:
    assert len(predictions) == len(observed_labels) == 128
    return sum(a == b for a, b in zip(predictions, observed_labels)) / 128


def run_dev() -> dict[str, object]:
    start = time.perf_counter()
    foundation = acquire_foundation_bank()
    assert foundation["source_actions_observed"] == 16384
    assert foundation["ambiguous_effects"] == 0
    learned_gates = tuple(int(k) for k in foundation["learned_table_counts"])
    grammar, composition_counts = compose_generic_programs(learned_gates, max_depth=5)
    learned_functions = hypothesis_functions(grammar)
    assert len(grammar) == 256
    foundation_elapsed = time.perf_counter() - start
    arms = ("structured", "same_grammar_unprimed", "exact_family_symbolic",
            "budgeted_logistic", "flat")
    world_rows = []
    all_predictions_sha = hashlib.sha256()
    for seed in DEV:
        world = PublicCausalWorld(seed)
        public = world.public_view()
        xs = tuple(public.allowed_actions[:16])
        ys = tuple(world.observe(action) for action in xs)
        held = tuple(public.held_inputs)
        assert len(set(xs)) == 16
        assert len(set(held)) == 128
        assert set(xs).isdisjoint(held)
        family = "mux3" if seed % 2 == 0 else "majority3"
        phase_start = time.perf_counter()
        native = fit(xs, ys, learned_functions, use_learned_depth=True)
        restored, state_sha = cold_roundtrip(native)
        structured_pred = tuple(predict(restored, x) for x in held)
        assert all(predict(restored, x) == y for x, y in zip(xs, ys))
        native_seconds = time.perf_counter() - phase_start
        other = fit(xs, ys, learned_functions, use_learned_depth=False)
        no_prior_pred = tuple(predict(other, x) for x in held)
        assert all(predict(other, x) == y for x, y in zip(xs, ys))
        symbolic_pred = exact_reference_predictions(xs, ys, held, family)
        logistic = train_budgeted_logistic(xs, ys)
        logistic_pred = tuple(predict_logistic(logistic, x) for x in held)
        flat_pred = flat_unstructured_predictions(ys, held)
        predictions = {
            "structured": structured_pred,
            "same_grammar_unprimed": no_prior_pred,
            "exact_family_symbolic": symbolic_pred,
            "budgeted_logistic": logistic_pred,
            "flat": flat_pred,
        }
        assert set(predictions) == set(arms)
        # All candidate predictions are now built. Only this evaluator step
        # uses withheld labels. NO held output can reach learner.fit().
        held_labels = tuple(world.development_only_eval(x) for x in held)
        scores = {arm: measured_accuracy(pred, held_labels)
                  for arm, pred in predictions.items()}
        digest = hashlib.sha256()
        for arm in arms:
            digest.update(bytes(predictions[arm]))
            all_predictions_sha.update(bytes(predictions[arm]))
        world_rows.append({
            "family": family,
            "held_count": len(held),
            "public_train_action_count": len(xs),
            "vector_accuracy": scores,
            "native_consistent_hypotheses_by_effect": native["compatible_hypotheses_per_effect"],
            "native_hypothesis_count_search": native["programs_searched"],
            "native_depth_programs": native["programs"],
            "native_checkpoint_sha256": state_sha,
            "native_fit_predict_elapsed_seconds_local_DEV": round(native_seconds, 6),
            "all_arms_prediction_sha256": digest.hexdigest(),
            "previous_learned_knowledge_retention_after_new_world": "NOT_TESTED",
        })
    total = {name: sum(row["vector_accuracy"][name] for row in world_rows) / len(world_rows)
             for name in arms}
    family_means = {family: {name: sum(row["vector_accuracy"][name] for row in world_rows
                                         if row["family"] == family) / 8
                             for name in arms}
                    for family in ("mux3", "majority3")}
    # Independent source-only exact reference audit before DEV was frozen at
    # 0.7529296875. Agreeing confirms no accidental changes to its source data
    # or to held-out metric units. This is not a native-model performance goal.
    assert total["exact_family_symbolic"] == 0.7529296875
    out = {
        "schema": "fkp02.native-style-dev-selection-result.v1",
        "claim": "DEV_ONLY_FROZEN_SELECTOR_NOT_NATIVE_SCIENCE",
        "protected_first_use": False,
        "foundation_worlds": 256,
        "foundation_real_action_consequences": 16384,
        "learned_binary_relation_types": dict(sorted(foundation["learned_table_counts"].items())),
        "three_input_function_count": len(grammar),
        "genuinely_three_input_candidate_function_count": len(learned_functions),
        "foundation_acquisition_elapsed_seconds_local_DEV": round(foundation_elapsed, 6),
        "run_wall_seconds_local_DEV": round(time.perf_counter() - start, 6),
        "dev_world_count": len(world_rows),
        "dev_scored_held_vectors": 128 * len(world_rows),
        "public_action_budget_per_arm_world": 16,
        "primary_accuracy_all": total,
        "accuracy_by_unseen_rule_family": family_means,
        "prediction_receipt_sha256": all_predictions_sha.hexdigest(),
        "worlds": world_rows,
        "trained_comparator_qualification": "budgeted_logistic_1000_epochs_not_certified_converged",
        "strongest_symbolic_control_eligible": True,
        "cold_retention_across_worlds": "NOT_TESTED",
        "full_process_cost_parity": "NOT_QUALIFIED",
        "science_status": "DEV_ONLY_UNVERIFIED",
        "integration": "NONE",
    }
    print(json.dumps(out, sort_keys=True, indent=2))
    return out


if __name__ == "__main__":
    run_dev()
