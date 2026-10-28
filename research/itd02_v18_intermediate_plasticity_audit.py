"""V18 locked nonlinear / additive synthetic leave-one-out adversarial controls.

Engineering-only. Toy target is an EXTERNAL harness function, never imported
by either original native learner or V18 candidate. No original-world data.
"""
import hashlib
import itertools
import json
import math
import subprocess
from pathlib import Path

from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, PUBLIC_CUES, NeighborCarriedPublicLearnerDev,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    ACTION_SITES, CELLS, CHANNELS, INITIAL_GAIN, MAX_CHECKPOINT_BYTES,
    IntermediatePlasticRingDev, canonical,
)

BASE = "ac0ca844ebb9b2b65a3a0a67e9e6f6a7bd227919"
PREREG_ORIGINAL = "46d815d78cf6f70cc85a9b1bb19ba3ce20164eeb"
PREREG_RANGE_ADDENDUM = "b149f86f21ed76c6b47bbee36fa6ea98f7c92577"
ORIGINAL_BLOBS = {
    "yggdrasil/itd02_native_task_bridge_dev.py": "71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
    "yggdrasil/itd02_local_ring_memory_dev.py": "1db0835d5c99456bcf99a013d4836f49314a9d39",
    "yggdrasil/itd02_v17_neighbor_carried_learner_dev.py": "4e3c77797e66df3a26742d23d18f038644891e55",
}
C = (-0.8, 0.3, 1.0, -0.2)
A = (-0.5, 0.0, 0.5)
B = (-0.5, 0.0, 0.5)
U = (1.0, -1.0, 1.0, -1.0)
V = (1.0, 0.0, -1.0)
EPOCHS = 16
RIDGE = 1e-6


def git(*args):
    return subprocess.check_output(
        ("git",) + args, cwd=Path(__file__).resolve().parents[1],
        text=True).strip()


def source_pin():
    for ancestor in (BASE, PREREG_ORIGINAL, PREREG_RANGE_ADDENDUM):
        assert git("merge-base", "--is-ancestor", ancestor, "HEAD") == ""
    for path, blob in ORIGINAL_BLOBS.items():
        assert git("hash-object", path) == blob, ("SOURCE_BLOB_CHANGED", path)
    assert CELLS == 8 and CHANNELS == 7 and ACTION_SITES == (0, 2, 5)


def target(cue, first, second, *, nonlinear):
    ci = PUBLIC_CUES.index(cue)
    ai = ACTIONS.index(first)
    bi = ACTIONS.index(second)
    value = -0.5 + C[ci] + A[ai] + B[bi]
    if nonlinear:
        value += 1.2 * U[ci] * V[ai]
    assert -3 <= value <= 10, "UNEXPECTED_V17_REWARD_RANGE"
    return value


def conventional_features(cue, first, second):
    ci = PUBLIC_CUES.index(cue)
    ai = ACTIONS.index(first)
    bi = ACTIONS.index(second)
    return ([1.0] + [float(ci == j) for j in range(4)] +
            [float(ai == j) for j in range(3)] +
            [float(bi == j) for j in range(3)] +
            [float(ci == i and ai == j) for i in range(4) for j in range(3)])


def linear_solve(matrix, target_values):
    """Fully deterministic ridge Gaussian elimination, not source-law oracle."""
    n = len(target_values)
    rows = [list(matrix[i]) + [target_values[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: (abs(rows[r][col]), -r))
        if abs(rows[pivot][col]) < 1e-12:
            raise AssertionError("CONVENTIONAL_CONTROL_RANK_FAILURE")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        denom = rows[col][col]
        for j in range(col, n + 1):
            rows[col][j] /= denom
        for row in range(n):
            if row == col:
                continue
            factor = rows[row][col]
            for j in range(col, n + 1):
                rows[row][j] -= factor * rows[col][j]
    return [rows[i][n] for i in range(n)]


def ridge_predict(training, heldout, *, nonlinear):
    xs = [conventional_features(*context) for context in training]
    ys = [target(*context, nonlinear=nonlinear) for context in training]
    cols = len(xs[0])
    gram = [[sum(x[i]*x[j] for x in xs) + (RIDGE if i == j else 0.0)
             for j in range(cols)] for i in range(cols)]
    response = [sum(x[i]*y for x, y in zip(xs, ys)) for i in range(cols)]
    weights = linear_solve(gram, response)
    return sum(w*x for w, x in zip(weights, conventional_features(*heldout)))


def train_candidate(model, cue, first, second, supplied_reward):
    model.start_observation(cue)
    model.accept_first(first)
    model.accept_second(second, supplied_reward, learning=True)


def train_v17(model, cue, first, second, supplied_reward):
    model.start_observation(cue)
    model.accept_first(first)
    model.accept_second(second, supplied_reward, learning=True)


def read_candidate(model, heldout):
    raw = model.checkpoint()
    assert len(raw) <= MAX_CHECKPOINT_BYTES
    model = IntermediatePlasticRingDev.restore(raw)
    assert model.checkpoint() == raw
    model.start_frozen_evaluation()
    frozen = model.parameters_sha256()
    model.start_observation(heldout[0])
    model.accept_first(heldout[1])
    selected = ACTIONS.index(heldout[2])
    prediction = model.scores()[selected]
    ablated_prediction = model.scores(clamped_initial_gains=True)[selected]
    model.accept_second(heldout[2], 0.0, learning=False)
    assert model.parameters_sha256() == frozen
    return prediction, ablated_prediction, len(raw)


def read_v17(model, heldout):
    raw = model.checkpoint()
    model = NeighborCarriedPublicLearnerDev.restore(raw)
    assert model.checkpoint() == raw
    model.start_frozen_evaluation()
    model.start_observation(heldout[0])
    model.accept_first(heldout[1])
    selected = ACTIONS.index(heldout[2])
    prediction = model.local_scores()[selected]
    model.accept_second(heldout[2], 0.0, learning=False)
    return prediction


def run_family(contexts, *, nonlinear):
    records = []
    totals = {
        "candidate": 0.0, "frozen_intermediate": 0.0,
        "v17_additive": 0.0, "conventional_interaction": 0.0,
        "same_weights_initial_gain_ablation": 0.0,
    }
    max_checkpoint = 0
    gain_changed_cell_count = 0
    max_gain_delta = 0.0
    changed_frozen_predictions = 0
    messages_forward = 0
    messages_credit = 0

    for heldout in contexts:
        candidate = IntermediatePlasticRingDev(plastic_intermediate=True)
        frozen = IntermediatePlasticRingDev(plastic_intermediate=False)
        v17 = NeighborCarriedPublicLearnerDev()
        original_ids = dict(candidate.native_ids)
        training = [case for case in contexts if case != heldout]
        assert len(training) == 35

        for _ in range(EPOCHS):
            for cue, first, second in training:
                reward = target(cue, first, second, nonlinear=nonlinear)
                train_candidate(candidate, cue, first, second, reward)
                train_candidate(frozen, cue, first, second, reward)
                train_v17(v17, cue, first, second, reward)

        assert candidate.native_ids == frozen.native_ids == v17.native_ids == original_ids
        assert candidate.learned_updates == frozen.learned_updates == v17.learned_updates == 560
        assert candidate.credit_messages == 560 * 8 * 2 * 4
        assert frozen.credit_messages == 0
        assert candidate.forward_messages == frozen.forward_messages == 560 * 8 * 2 * 7 * 4
        assert all(len(row) == 20 for row in candidate.heads)
        assert all(len(row) == 7 for row in candidate.gains)
        assert all(row == [INITIAL_GAIN]*7 for row in frozen.gains)

        delta = [(cell, channel, abs(candidate.gains[cell][channel] - INITIAL_GAIN))
                 for cell in range(CELLS) for channel in range(CHANNELS)]
        gain_changed_cell_count += len({
            c for c, k, difference in delta if c not in ACTION_SITES and difference > 1e-10
        })
        max_gain_delta = max(max_gain_delta, max(d for c,k,d in delta))

        predicted, ablated, saved_bytes = read_candidate(candidate, heldout)
        frozen_pred, _, frozen_bytes = read_candidate(frozen, heldout)
        v17_pred = read_v17(v17, heldout)
        conventional_pred = ridge_predict(training, heldout, nonlinear=nonlinear)
        expected = target(*heldout, nonlinear=nonlinear)
        observed = {
            "candidate": predicted, "frozen_intermediate": frozen_pred,
            "v17_additive": v17_pred, "conventional_interaction": conventional_pred,
            "same_weights_initial_gain_ablation": ablated,
        }
        for key, value in observed.items():
            assert math.isfinite(value), ("NONFINITE_HELDOUT", key)
            totals[key] += abs(expected - value)
        if abs(predicted - ablated) > 1e-10:
            changed_frozen_predictions += 1
        max_checkpoint = max(max_checkpoint, saved_bytes, frozen_bytes)
        messages_forward += candidate.forward_messages
        messages_credit += candidate.credit_messages
        records.append({
            "cue": heldout[0], "actual_first": heldout[1],
            "selected_second": heldout[2], "toy_reward": round(expected, 12),
            "candidate": round(predicted, 12),
            "frozen_intermediate": round(frozen_pred, 12),
            "v17_additive": round(v17_pred, 12),
            "conventional_interaction": round(conventional_pred, 12),
            "same_weights_initial_gain_ablation": round(ablated, 12),
        })

    assert len(records) == 36
    assert gain_changed_cell_count > 0, "NO_INTERMEDIATE_CELL_GAIN_CHANGE"
    assert changed_frozen_predictions > 0, "GAIN_ABLATION_CAUSALLY_INERT"
    assert max_checkpoint <= MAX_CHECKPOINT_BYTES
    return {
        "records": records, "errors": totals,
        "intermediate_cell_changes_across_folds": gain_changed_cell_count,
        "max_intermediate_gain_delta": max_gain_delta,
        "gain_ablation_prediction_changes": changed_frozen_predictions,
        "max_checkpoint_bytes": max_checkpoint,
        "forward_edge_scalar_messages": messages_forward,
        "reverse_reward_edge_scalar_messages": messages_credit,
    }


def main():
    source_pin()
    contexts = list(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
    assert len(contexts) == len(set(contexts)) == 36
    nonlinear = run_family(contexts, nonlinear=True)
    additive = run_family(contexts, nonlinear=False)
    full = nonlinear["errors"]["candidate"]
    same_no_gain = nonlinear["errors"]["frozen_intermediate"]
    conventional = nonlinear["errors"]["conventional_interaction"]
    if full > 0.95 * same_no_gain:
        classification = "V18_NO_INTERMEDIATE_PLASTICITY_BENEFIT__NO_SCIENCE"
    elif full >= conventional:
        classification = "V18_INTERMEDIATE_PLASTICITY_BENEFIT_BUT_CONTROL_NOT_BEATEN__NO_SCIENCE"
    else:
        classification = "V18_SYNTHETIC_LOCAL_PLASTICITY_CANDIDATE__NO_SCIENCE"
    records = [
        {"nonlinear": nonlinear["records"][i], "additive": additive["records"][i]}
        for i in range(36)
    ]
    result = {
        "schema": "ygg.itd02.v18.nonlinear_plasticity_falsification.source_only.v1",
        "source_only": True, "scientific_first_use": False,
        "original_world_training": False, "native_model_modified": False,
        "original_memory_modified": False,
        "public_histories": 36, "heldout_folds_per_family": 36,
        "matched_training_samples_per_fold": 35 * EPOCHS,
        "source_native_ring_cells": CELLS,
        "local_tag_channels": CHANNELS, "neighbor_hops": 4,
        "candidate_plastic_intermediate_gains": 8 * 7,
        "candidate_learned_reward_head_scalars": 3 * 20,
        "candidate_total_learned_scalars": 116,
        "additive_errors": additive["errors"],
        "nonlinear_errors": nonlinear["errors"],
        "intermediate_cells_changed_nonlinear": nonlinear["intermediate_cell_changes_across_folds"],
        "intermediate_cells_changed_additive": additive["intermediate_cell_changes_across_folds"],
        "max_nonlinear_gain_delta": nonlinear["max_intermediate_gain_delta"],
        "nonlinear_gain_ablation_prediction_changes": nonlinear["gain_ablation_prediction_changes"],
        "max_checkpoint_bytes": max(
            additive["max_checkpoint_bytes"], nonlinear["max_checkpoint_bytes"]),
        "total_forward_edge_messages": (
            additive["forward_edge_scalar_messages"] + nonlinear["forward_edge_scalar_messages"]),
        "total_reverse_credit_messages": (
            additive["reverse_reward_edge_scalar_messages"] + nonlinear["reverse_reward_edge_scalar_messages"]),
        "canonical_record_sha256": hashlib.sha256(canonical(records)).hexdigest(),
        "classification": classification,
        "conventional_control_beaten": full < conventional,
        "plasticity_vs_frozen_benefit_5pct": full <= 0.95 * same_no_gain,
        "qualifier": "ENGINEERING_TOY_ONLY_NOT_SCIENCE",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
