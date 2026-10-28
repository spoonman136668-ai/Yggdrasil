"""V20 pre-registered source-only causal credit and matched reward controls.

External V18 synthetic target and conventional-control implementation are
frozen. This harness is not part of the V20 learner and uses NO original world.
"""
import hashlib
import itertools
import json
import math
import subprocess
from pathlib import Path

from research.itd02_v18_intermediate_plasticity_audit import (
    target, ridge_predict, train_candidate, train_v17, read_candidate, read_v17,
)
from research.itd02_v19_local_credit_causality_audit import (
    reconstructed_prediction, EPS as FINITE_EPS,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, PUBLIC_CUES, NeighborCarriedPublicLearnerDev,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    CELLS, CHANNELS, GAIN_LIMITS, INITIAL_GAIN, MAX_CHECKPOINT_BYTES,
    IntermediatePlasticRingDev, canonical,
)
from yggdrasil.itd02_v20_causal_credit_dev import (
    ResponsibilityGatedRingDev,
)

PARENT = "fb3dc5b2f563081a802267e8e7c39f52ccb6f3a3"
PREREG = "d170d628e8ba6d97f236d9e8aeb9ccfbf6abf515"
BLOBS = {
    "yggdrasil/itd02_native_task_bridge_dev.py": "71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
    "yggdrasil/itd02_local_ring_memory_dev.py": "1db0835d5c99456bcf99a013d4836f49314a9d39",
    "yggdrasil/itd02_v18_intermediate_plasticity_dev.py": "711391944be7bd94f1898005d1233bfe52a6f216",
    "research/itd02_v18_intermediate_plasticity_audit.py": "7a8f361ff13cf75f716c544add192c2ff9c5aae9",
}
EPOCHS = 16
ZERO = 1e-10


def git(*args):
    return subprocess.check_output(
        ("git",) + args, text=True, cwd=Path(__file__).resolve().parents[1],
    ).strip()


def verify():
    for sha in (PARENT, PREREG):
        assert git("merge-base", "--is-ancestor", sha, "HEAD") == ""
    for path, expected in BLOBS.items():
        assert git("hash-object", path) == expected, ("ORIGINAL_SOURCE_DRIFT", path)
    assert CELLS == 8 and CHANNELS == 7 and ACTION_SITES == (0, 2, 5)


def real_first(model, cue, first):
    model.start_observation(cue)
    model.accept_first(first)


def causal_derivative_witness():
    cases = list(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
    initial_no_update = 0
    zero_head_derivatives = 0
    local_matches = 0
    nondifferentiable = 0
    checked_nonzero = 0
    max_slope_gap = 0.0
    max_checkpoint = 0
    for nonlinear in (False, True):
        for cue, first, second in cases:
            m = ResponsibilityGatedRingDev()
            base_native = dict(m.native_ids)
            real_first(m, cue, first)
            gradient, _ = m.local_gain_responsibilities(second)
            assert all(v == 0.0 for row in gradient for v in row)
            zero_head_derivatives += 1
            original = [list(row) for row in m.gains]
            m.accept_second(second, target(cue, first, second, nonlinear=nonlinear))
            assert m.gains == original, "FIRST_CAUSALLY_UNGROUNDED_RELAY_UPDATE"
            assert m.native_ids == base_native
            initial_no_update += 1
            raw = m.checkpoint()
            assert ResponsibilityGatedRingDev.restore(raw).checkpoint() == raw
            max_checkpoint = max(max_checkpoint, len(raw))

            # The trained head now supplies causal sensitivity. The local
            # reverse ring trace must match independently recomputed exact
            # finite differences, ignoring *measured* nondifferentiable ties.
            real_first(m, cue, first)
            predicted = m.scores()[ACTIONS.index(second)]
            independent = reconstructed_prediction(
                m, cue, first, second, m.gains)
            assert abs(predicted - independent) < 1e-12
            local, _ = m.local_gain_responsibilities(second)
            for cell in range(CELLS):
                for tag in range(CHANNELS):
                    old = m.gains[cell][tag]
                    if not GAIN_LIMITS[0] + FINITE_EPS < old < GAIN_LIMITS[1] - FINITE_EPS:
                        continue
                    upper = [list(row) for row in m.gains]
                    lower = [list(row) for row in m.gains]
                    upper[cell][tag] += FINITE_EPS
                    lower[cell][tag] -= FINITE_EPS
                    pos = reconstructed_prediction(m, cue, first, second, upper)
                    neg = reconstructed_prediction(m, cue, first, second, lower)
                    forward = (pos - predicted) / FINITE_EPS
                    backward = (predicted - neg) / FINITE_EPS
                    max_slope_gap = max(max_slope_gap, abs(forward-backward))
                    if abs(forward - backward) > 1e-4:
                        nondifferentiable += 1
                        continue
                    truth = (pos - neg) / (2*FINITE_EPS)
                    assert abs(local[cell][tag] - truth) <= 1e-3, (
                        "INCORRECT_LOCAL_CAUSAL_GRADIENT",
                        cell, tag, local[cell][tag], truth)
                    if abs(truth) > 1e-7:
                        checked_nonzero += 1
                    local_matches += 1
            m.accept_second(second, target(cue, first, second, nonlinear=nonlinear))
            assert m.native_ids == base_native
    assert initial_no_update == 72 and zero_head_derivatives == 72
    assert local_matches >= 12
    assert checked_nonzero >= 12, (
        "INSUFFICIENT_NONZERO_INDEPENDENT_CAUSAL_COORDINATES", checked_nonzero)
    return {
        "first_event_no_gain_update_cases": initial_no_update,
        "zero_initial_head_sensitivity_cases": zero_head_derivatives,
        "finite_difference_nonsmooth_exclusions": nondifferentiable,
        "finite_difference_matching_coordinates": local_matches,
        "finite_difference_nonzero_matching_coordinates": checked_nonzero,
        "max_one_sided_slope_disagreement": max_slope_gap,
        "max_probe_checkpoint_bytes": max_checkpoint,
    }


def read_v20(model, heldout):
    raw = model.checkpoint()
    assert len(raw) <= MAX_CHECKPOINT_BYTES
    restored = ResponsibilityGatedRingDev.restore(raw)
    assert restored.checkpoint() == raw
    restored.start_frozen_evaluation()
    frozen = restored.parameters_sha256()
    real_first(restored, heldout[0], heldout[1])
    index = ACTIONS.index(heldout[2])
    result = restored.scores()[index]
    ablated = restored.scores(clamped_initial_gains=True)[index]
    restored.accept_second(heldout[2], 0.0, learning=False)
    assert restored.parameters_sha256() == frozen
    return result, ablated, len(raw)


def heldout_families():
    cases = list(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
    records = []
    errors = {}
    max_checkpoint = 0
    messages_forward = 0
    messages_reverse = 0
    nonzero_gain_changes = 0
    gain_ablation_changed_scores = 0
    for nonlinear in (True, False):
        totals = {
            "v20_responsibility": 0.0, "v18_plastic": 0.0,
            "v18_frozen": 0.0, "v17_additive": 0.0,
            "strong_public_interaction_ridge": 0.0,
            "v20_same_weights_initial_gain_ablation": 0.0,
        }
        for heldout in cases:
            v20 = ResponsibilityGatedRingDev()
            v18 = IntermediatePlasticRingDev(plastic_intermediate=True)
            frozen = IntermediatePlasticRingDev(plastic_intermediate=False)
            v17 = NeighborCarriedPublicLearnerDev()
            native_ids = dict(v20.native_ids)
            training = [c for c in cases if c != heldout]
            assert len(training) == 35
            for _ in range(EPOCHS):
                for cue, first, second in training:
                    reward = target(cue, first, second, nonlinear=nonlinear)
                    train_candidate(v20, cue, first, second, reward)
                    train_candidate(v18, cue, first, second, reward)
                    train_candidate(frozen, cue, first, second, reward)
                    train_v17(v17, cue, first, second, reward)
            assert all(x.native_ids == native_ids for x in (v20, v18, frozen, v17))
            assert v20.learned_updates == v18.learned_updates == frozen.learned_updates == v17.learned_updates == 560
            assert all(len(row) == 7 for row in v20.gains)
            assert all(len(row) == 20 for row in v20.heads)
            nonzero_gain_changes += sum(
                abs(g - INITIAL_GAIN) > ZERO
                for row in v20.gains for g in row)
            predicted, ablated, size = read_v20(v20, heldout)
            p_v18, _, _ = read_candidate(v18, heldout)
            p_frozen, _, _ = read_candidate(frozen, heldout)
            p_v17 = read_v17(v17, heldout)
            p_ridge = ridge_predict(training, heldout, nonlinear=nonlinear)
            truth = target(*heldout, nonlinear=nonlinear)
            values = {
                "v20_responsibility": predicted,
                "v18_plastic": p_v18,
                "v18_frozen": p_frozen,
                "v17_additive": p_v17,
                "strong_public_interaction_ridge": p_ridge,
                "v20_same_weights_initial_gain_ablation": ablated,
            }
            for k, v in values.items():
                assert math.isfinite(v), ("NONFINITE_PREDICTION", k, heldout)
                totals[k] += abs(truth-v)
            if abs(predicted - ablated) > 1e-10:
                gain_ablation_changed_scores += 1
            max_checkpoint = max(max_checkpoint, size)
            messages_forward += v20.forward_messages
            messages_reverse += v20.credit_messages
            records.append({
                "family": "nonadditive" if nonlinear else "additive",
                "cue": heldout[0], "actual_first": heldout[1],
                "selected_second": heldout[2], "feedback": round(truth,12),
                "source_only_predictions": {
                    k: round(v, 12) for k,v in values.items()
                },
            })
        errors["nonadditive" if nonlinear else "additive"] = totals
    assert len(records) == 72
    assert max_checkpoint <= MAX_CHECKPOINT_BYTES
    return {
        "errors": errors,
        "nonzero_relay_gains_across_folds": nonzero_gain_changes,
        "gain_reset_prediction_differences": gain_ablation_changed_scores,
        "max_checkpoint_bytes": max_checkpoint,
        "forward_edge_scalar_messages": messages_forward,
        "reverse_credit_scalar_messages": messages_reverse,
        "records": records,
    }


def main():
    verify()
    witness = causal_derivative_witness()
    results = heldout_families()
    nonlinear = results["errors"]["nonadditive"]
    candidate = nonlinear["v20_responsibility"]
    v18 = nonlinear["v18_plastic"]
    frozen = nonlinear["v18_frozen"]
    ridge = nonlinear["strong_public_interaction_ridge"]
    improvement = candidate <= .95 * v18 and candidate <= .95 * frozen
    if not improvement:
        label = "V20_CAUSAL_CREDIT_STRUCTURAL_PASS_NO_TRANSFER_GAIN__NO_SCIENCE"
    elif candidate >= ridge:
        label = "V20_LOCAL_CREDIT_TOY_GAIN_CONTROL_NOT_BEATEN__NO_SCIENCE"
    else:
        label = "V20_LOCAL_CREDIT_TOY_BENEFIT__NO_SCIENCE"
    rec = {
        "schema": "ygg.itd02.v20.responsibility_gated_comparative.source_only.v1",
        "classification": label, "source_only": True,
        "scientific_first_use": False,
        "original_world_training": False,
        "original_native_and_memory_unchanged": True,
        "original_v18_code_sha": BLOBS[
            "yggdrasil/itd02_v18_intermediate_plasticity_dev.py"],
        "original_native_ring_cells": CELLS,
        "seven_fixed_public_tag_channels": CHANNELS,
        "ring_neighbor_hops": 4,
        "candidate_learned_scalars": 116,
        "original_v18_learned_scalars": 116,
        "heldout_public_histories_per_family": 36,
        "training_updates_per_fold_per_arm": 560,
        "synthetic_families": 2,
        "causal_derivative_witness": witness,
        "matched_heldout_absolute_error": results["errors"],
        "nonadditive_improvement_at_least_5pct_vs_both_v18_arms": improvement,
        "beats_strong_conventional_interaction": candidate < ridge,
        "nonzero_relay_gains_across_folds": results["nonzero_relay_gains_across_folds"],
        "gain_reset_prediction_differences": results["gain_reset_prediction_differences"],
        "max_checkpoint_bytes": max(
            witness["max_probe_checkpoint_bytes"], results["max_checkpoint_bytes"]),
        "forward_edge_scalar_messages": results["forward_edge_scalar_messages"],
        "reverse_credit_scalar_messages": results["reverse_credit_scalar_messages"],
        "canonical_72_case_sha256": hashlib.sha256(
            canonical(results["records"])).hexdigest(),
        "qualification": "ENGINEERING_TOY_ONLY_NOT_NATIVE_SCIENCE",
    }
    print(json.dumps(rec, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
