"""V19 preregistered source-only causal responsibility audit of unchanged V18.

Does NOT modify or replace a learner. No protected original-world experiment.
All toy targets are supplied from the unmodified V18 external test harness.
"""
import hashlib
import itertools
import json
import math
import subprocess
from pathlib import Path

from research.itd02_v18_intermediate_plasticity_audit import target
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, PUBLIC_CUES, site_pulses,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    CELLS, CHANNELS, INITIAL_GAIN, MAX_CHECKPOINT_BYTES,
    IntermediatePlasticRingDev, canonical, forward_local,
)

PARENT = "46097b7fd03e40ceec6b74918430b7f6c11cc53e"
PREREG = "25df62bdbe406541d68fd3474ad5b8883815aefc"
BLOBS = {
    "yggdrasil/itd02_native_task_bridge_dev.py": "71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
    "yggdrasil/itd02_local_ring_memory_dev.py": "1db0835d5c99456bcf99a013d4836f49314a9d39",
    "yggdrasil/itd02_v18_intermediate_plasticity_dev.py": "711391944be7bd94f1898005d1233bfe52a6f216",
    "research/itd02_v18_intermediate_plasticity_audit.py": "7a8f361ff13cf75f716c544add192c2ff9c5aae9",
}
EPS = 1e-5
FLAT = 1e-7
DELTA = 1e-10


def git(*args):
    return subprocess.check_output(
        ("git",) + args, cwd=Path(__file__).resolve().parents[1],
        text=True).strip()


def check_sources():
    for ancestor in (PARENT, PREREG):
        assert git("merge-base", "--is-ancestor", ancestor, "HEAD") == ""
    for path, expected in BLOBS.items():
        assert git("hash-object", path) == expected, ("SOURCE_BLOB_DRIFT", path)
    assert CELLS == 8 and CHANNELS == 7 and ACTION_SITES == (0, 2, 5)


def reconstructed_prediction(model, cue, first, second, gains):
    """Independent source-exact V18 local readout, no gradient oracle."""
    pulses = site_pulses(cue, first)
    delivered, eligibility, count = forward_local(pulses, gains)
    assert count == 448
    site_index = ACTIONS.index(second)
    channel = delivered[ACTION_SITES[site_index]]
    features = [1.0] + list(channel) + [
        channel[c] * channel[4 + a]
        for c in range(4) for a in range(3)
    ]
    assert len(features) == len(model.heads[site_index]) == 20
    prediction = sum(
        w * x for w, x in zip(model.heads[site_index], features))
    assert math.isfinite(prediction)
    return prediction


def jacobian(model, cue, first, second):
    """56 source-parameter-specific central finite differences at fixed heads."""
    expected = model.scores()[ACTIONS.index(second)]
    observed = reconstructed_prediction(
        model, cue, first, second, model.gains)
    assert abs(expected - observed) < 1e-12, (
        "INDEPENDENT_READOUT_RECONSTRUCTION_DRIFT", expected, observed)
    gradients = []
    for cell in range(CELLS):
        row = []
        for channel in range(CHANNELS):
            up = [list(v) for v in model.gains]
            down = [list(v) for v in model.gains]
            up[cell][channel] += EPS
            down[cell][channel] -= EPS
            higher = reconstructed_prediction(model, cue, first, second, up)
            lower = reconstructed_prediction(model, cue, first, second, down)
            row.append((higher - lower) / (2.0 * EPS))
        gradients.append(row)
    return expected, gradients


def first(model, cue, actual_first):
    model.start_observation(cue)
    model.accept_first(actual_first)


def matrix_differences(after, before):
    return [
        [after[i][j] - before[i][j] for j in range(CHANNELS)]
        for i in range(CELLS)
    ]


def main():
    check_sources()
    contexts = list(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
    assert len(contexts) == len(set(contexts)) == 36
    case_records = []
    zero_gradient_cases = 0
    initial_non_output_gain_updates = 0
    initial_gain_updates_with_zero_sensitivity = 0
    initial_nonzero_feedback_events = 0
    postfit_nonzero_gradient_coordinates = 0
    postfit_changed_gains_with_zero_gradient = 0
    postfit_changed_gains_with_wrong_direction = 0
    postfit_gain_changes = 0
    original_models_untouched = True
    max_checkpoint_bytes = 0
    total_forward_messages = 0
    total_credit_messages = 0
    for nonlinear in (False, True):
        for cue, actual_first, second in contexts:
            model = IntermediatePlasticRingDev(plastic_intermediate=True)
            original = dict(model.native_ids)
            assert all(all(v == 0.0 for v in row) for row in model.heads)
            assert all(all(v == INITIAL_GAIN for v in row) for row in model.gains)
            first(model, cue, actual_first)
            prediction, grad_initial = jacobian(
                model, cue, actual_first, second)
            assert prediction == 0.0, "INITIAL_ACTION_HEAD_NOT_ZERO"
            assert all(abs(g) < 1e-10 for row in grad_initial for g in row), (
                "NONZERO_INITIAL_GAIN_CAUSAL_SENSITIVITY")
            zero_gradient_cases += 1
            initial_state = model.checkpoint()
            assert (IntermediatePlasticRingDev.restore(initial_state).checkpoint()
                    == initial_state)
            max_checkpoint_bytes = max(max_checkpoint_bytes, len(initial_state))
            before_gains = [list(v) for v in model.gains]
            before_heads = [list(v) for v in model.heads]
            supplied_reward = target(
                cue, actual_first, second, nonlinear=nonlinear)
            assert -3 <= supplied_reward <= 10
            if supplied_reward != 0:
                initial_nonzero_feedback_events += 1
            model.accept_second(second, supplied_reward, learning=True)
            changes = matrix_differences(model.gains, before_gains)
            updated = sum(abs(d) > DELTA for row in changes for d in row)
            spurious = sum(
                abs(changes[i][j]) > DELTA and abs(grad_initial[i][j]) < FLAT
                for i in range(CELLS) for j in range(CHANNELS))
            assert spurious == updated
            non_output = sum(
                abs(changes[i][j]) > DELTA
                for i in range(CELLS) if i not in ACTION_SITES
                for j in range(CHANNELS))
            initial_non_output_gain_updates += non_output
            initial_gain_updates_with_zero_sensitivity += spurious
            idx = ACTIONS.index(second)
            for h in range(3):
                if h != idx:
                    assert model.heads[h] == before_heads[h], (
                        "UNSELECTED_HEAD_PARAMETER_MUTATION", h)
            assert model.native_ids == original
            assert model.learned_updates == 1
            assert model.credit_messages == 8 * 2 * 4
            original_models_untouched &= (model.native_ids == original)
            trained = model.checkpoint()
            assert IntermediatePlasticRingDev.restore(trained).checkpoint() == trained
            max_checkpoint_bytes = max(max_checkpoint_bytes, len(trained))

            # A second public event now has a nonzero trained head. Audit
            # true finite-difference responsibility separately from
            # existing source-blind V18 eligibility updates.
            first(model, cue, actual_first)
            second_pred, trained_gradient = jacobian(
                model, cue, actual_first, second)
            true_nonzero = sum(
                abs(v) >= FLAT for row in trained_gradient for v in row)
            postfit_nonzero_gradient_coordinates += true_nonzero
            feedback_error = supplied_reward - second_pred
            old_gains = [list(v) for v in model.gains]
            model.accept_second(second, supplied_reward, learning=True)
            changed_again = matrix_differences(model.gains, old_gains)
            wrong = 0
            flat_changes = 0
            moved = 0
            for i in range(CELLS):
                for j in range(CHANNELS):
                    difference = changed_again[i][j]
                    grad = trained_gradient[i][j]
                    if abs(difference) <= DELTA:
                        continue
                    moved += 1
                    if abs(grad) < FLAT:
                        flat_changes += 1
                    elif difference * feedback_error * grad < 0:
                        wrong += 1
            postfit_gain_changes += moved
            postfit_changed_gains_with_zero_gradient += flat_changes
            postfit_changed_gains_with_wrong_direction += wrong
            assert model.native_ids == original
            total_forward_messages += model.forward_messages
            total_credit_messages += model.credit_messages

            # Counterfactual identical public event, exactly zero reward
            # error at all-zero initialized heads -> no parameter update.
            zero_control = IntermediatePlasticRingDev(plastic_intermediate=True)
            first(zero_control, cue, actual_first)
            identity = zero_control.parameters_sha256()
            pending = zero_control.checkpoint()
            try:
                zero_control.accept_second(second, float("nan"), learning=True)
            except ValueError:
                pass
            else:
                raise AssertionError("NONFINITE_PUBLIC_REWARD_NOT_REJECTED")
            assert zero_control.checkpoint() == pending
            zero_control.accept_second(second, 0.0, learning=True)
            assert zero_control.parameters_sha256() == identity

            case_records.append({
                "family": "nonlinear" if nonlinear else "additive",
                "cue": cue, "actual_first": actual_first, "second": second,
                "public_feedback": round(supplied_reward, 12),
                "initial_gain_jacobian_nonzero": 0,
                "initial_gain_cells_updated": updated,
                "initial_intermediate_gains_updated": non_output,
                "postfit_gain_jacobian_nonzero": true_nonzero,
                "postfit_gain_cells_updated": moved,
                "postfit_updated_but_flat": flat_changes,
                "postfit_updated_wrong_direction": wrong,
                "original_native_parameters_changed": False,
            })

    assert len(case_records) == 72
    assert zero_gradient_cases == 72
    assert max_checkpoint_bytes <= MAX_CHECKPOINT_BYTES
    if initial_non_output_gain_updates > 0:
        classification = "V19_V18_UNATTRIBUTED_LOCAL_CREDIT_CONFIRMED__NO_SCIENCE"
    else:
        classification = "V19_V18_INITIAL_CREDIT_ALIGNED__NO_SCIENCE"
    result = {
        "schema": "ygg.itd02.v19.credit_causal_responsibility.source_only.v1",
        "classification": classification, "source_only": True,
        "scientific_first_use": False, "original_world_training": False,
        "original_native_model_parameters_unchanged": original_models_untouched,
        "source_original_v18_blob": BLOBS[
            "yggdrasil/itd02_v18_intermediate_plasticity_dev.py"],
        "public_contexts_per_family": 36,
        "synthetic_family_count": 2,
        "initial_zero_sensitivity_cases": zero_gradient_cases,
        "initial_nonzero_feedback_cases": initial_nonzero_feedback_events,
        "initial_nonoutput_gain_updates": initial_non_output_gain_updates,
        "initial_gain_updates_with_zero_causal_sensitivity": (
            initial_gain_updates_with_zero_sensitivity),
        "postfit_true_nonzero_causal_gain_gradients": (
            postfit_nonzero_gradient_coordinates),
        "postfit_gain_updates": postfit_gain_changes,
        "postfit_updated_gains_with_flat_causal_gradient": (
            postfit_changed_gains_with_zero_gradient),
        "postfit_updated_gains_against_local_loss_descent": (
            postfit_changed_gains_with_wrong_direction),
        "max_checkpoint_bytes": max_checkpoint_bytes,
        "total_forward_neighbor_scalar_messages": total_forward_messages,
        "total_reward_credit_scalar_messages": total_credit_messages,
        "original_native_ring_cells": CELLS,
        "original_v18_learned_scalar_budget": 116,
        "canonical_case_sha256": hashlib.sha256(canonical(case_records)).hexdigest(),
        "next_gate": "PREREGISTERED_CAUSAL_ELIGIBILITY_UPDATE_VERSUS_FROZEN_V18_AND_STRONG_CONTROLS",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
