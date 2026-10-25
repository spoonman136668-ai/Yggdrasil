"""Frozen development-only causal audit of Ygg ITD-01 R7 retention attribution.

Original native_cells.py and test_native_cells.py are NOT modified.
No external world, protected source, new prospective cohort or first-use.
"""
from __future__ import annotations

import itertools
import json
import pathlib
import sys
import time
import tracemalloc

ROOT = pathlib.Path(__file__).resolve().parents[1] / "r7"
sys.path.insert(0, str(ROOT))
from native_cells import (  # noqa: E402
    Colony,
    PublicDevGenerator,
    _examples,
    _score,
    gates,
    study,
)

PUBLIC_SEEDS = (17, 31, 47)


def cells_snapshot(model, context):
    return tuple((cell.fast, cell.slow, cell.updates)
                 for cell in model.cells[context])


def audit_one(seed):
    # Reproduce exactly the original chronological DEV example construction.
    g = PublicDevGenerator(seed + 71)
    train_a = _examples(g, "A", 320)
    valid_a = _examples(g, "A", 160)
    train_b = _examples(g, "B", 320)
    retained_a = _examples(g, "A", 160)
    held_b = _examples(g, "B", 160)

    model = Colony()
    for context, sensors, outcome in train_a:
        model.predict(context, sensors)
        model.learn_completed_public_feedback(context, sensors, outcome, 2)

    pre_blob = model.checkpoint()
    pre = Colony.restore(pre_blob)
    no_b_ablation = Colony.restore(pre_blob)
    pre_a_cells = cells_snapshot(pre, "A")
    pre_b_cells = cells_snapshot(pre, "B")
    pre_val_a = _score(pre, valid_a)
    pre_retained_a = _score(pre, retained_a)
    pre_held_b = _score(pre, held_b)
    patterns = tuple(itertools.product((False, True), repeat=4))
    before_preds = tuple(pre.predict("A", s) for s in patterns)
    before_b_preds = tuple(pre.predict("B", s) for s in patterns)

    for context, sensors, outcome in train_b:
        model.predict(context, sensors)
        model.learn_completed_public_feedback(context, sensors, outcome, 2)

    post_blob = model.checkpoint()
    cold = Colony.restore(post_blob)
    post_a_cells = cells_snapshot(cold, "A")
    post_b_cells = cells_snapshot(cold, "B")
    after_preds = tuple(cold.predict("A", s) for s in patterns)
    after_b_preds = tuple(cold.predict("B", s) for s in patterns)
    paired_pre_val = _score(pre, valid_a)
    paired_post_val = _score(cold, valid_a)
    paired_pre_ret = _score(pre, retained_a)
    paired_post_ret = _score(cold, retained_a)
    original = study(seed)

    out = {
        "seed": seed,
        "original_frozen_gate_a_before_b_valid_a": original["a_before_b"],
        "original_frozen_gate_a_after_b_different_retained_a": original["a_after_b"],
        "original_frozen_gate_between_sample_drop": round(
            original["a_before_b"] - original["a_after_b"], 8),
        "paired_same_valid_a_before": paired_pre_val,
        "paired_same_valid_a_after": paired_post_val,
        "paired_same_retained_a_before": paired_pre_ret,
        "paired_same_retained_a_after": paired_post_ret,
        "no_b_ablation_same_retained_a": _score(no_b_ablation, retained_a),
        "before_b_on_held_b": pre_held_b,
        "after_b_on_held_b": _score(cold, held_b),
        "a_all_16_inputs_unchanged": before_preds == after_preds,
        "a_all_4_local_cells_unchanged": pre_a_cells == post_a_cells,
        "b_local_cells_modified": pre_b_cells != post_b_cells,
        "b_all_16_inputs_changed_count": sum(a != b for a, b in zip(before_b_preds, after_b_preds)),
        "b_local_feedback_updates": [c.updates for c in cold.cells["B"]],
        "b_training_experiences": len(train_b),
        "original_frozen_cold_restore_exact": original["cold_restore_exact"],
        "original_frozen_checkpoint_bytes": original["serialized_state_bytes"],
        "original_gate_cohort_result_kept": original,
        "pre_checkpoint_bytes": len(pre_blob),
        "post_checkpoint_bytes": len(post_blob),
    }
    if not (
        pre_val_a == original["a_before_b"] and
        paired_post_ret == original["a_after_b"] and
        after_preds == before_preds and
        pre_a_cells == post_a_cells and
        paired_pre_val == paired_post_val and
        paired_pre_ret == paired_post_ret and
        _score(no_b_ablation, retained_a) == paired_post_ret and
        all(c.updates == 320 for c in cold.cells["B"]) and
        pre_b_cells != post_b_cells and
        after_b_preds != before_b_preds and
        original["cold_restore_exact"]
    ):
        raise AssertionError("R7_PAIRED_ATTRIBUTION_INVARIANT_FAILED:" + json.dumps(out, sort_keys=True))
    return out, original


def main():
    t0 = time.process_time()
    tracemalloc.start()
    all_rows, original_rows = [], []
    for seed in PUBLIC_SEEDS:
        row, original = audit_one(seed)
        all_rows.append(row)
        original_rows.append(original)
        print("R7_DEV_PAIRED_ATTRIBUTION=" + json.dumps(row, sort_keys=True), flush=True)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    prior_gate = gates(original_rows)
    if prior_gate or not (
        original_rows[1]["a_before_b"] - original_rows[1]["a_after_b"] > .05
    ):
        raise AssertionError("ORIGINAL_FROZEN_NEGATIVE_WAS_NOT_PRESERVED")
    summary = {
        "schema": "ygg.itd01.r7.dev_retention_causal_audit.v1",
        "cohorts": list(PUBLIC_SEEDS),
        "original_frozen_gate_pass": prior_gate,
        "paired_all_A_accuracy_changes": [round(x["paired_same_valid_a_before"] - x["paired_same_valid_a_after"], 8) for x in all_rows],
        "all_A_cells_and_all_16_predictions_unchanged": all(
            x["a_all_4_local_cells_unchanged"] and x["a_all_16_inputs_unchanged"]
            for x in all_rows),
        "no_B_training_reproduces_original_after_B_retained_A_accuracy": all(
            x["no_b_ablation_same_retained_a"] == x["original_frozen_gate_a_after_b_different_retained_a"]
            for x in all_rows),
        "real_B_feedback_executed": all(x["b_training_experiences"] == 320 and x["b_local_cells_modified"]
                                      and x["b_all_16_inputs_changed_count"] > 0 for x in all_rows),
        "audit_cpu_process_seconds": round(time.process_time() - t0, 6),
        "audit_peak_traced_python_bytes": peak,
        "causal_interpretation": "Original between-sample A accuracy gap cannot be caused by B updates in unchanged native model; same-sample A predictions are invariant.",
        "unfamiliar_external_world_episode_count": 0,
        "protected_source_first_use": False,
        "scientific_go": False,
    }
    assert all(value == 0 for value in summary["paired_all_A_accuracy_changes"])
    print("R7_DEV_PAIRED_CAUSAL_AUDIT_SUMMARY=" + json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
