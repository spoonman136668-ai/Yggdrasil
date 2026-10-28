"""V22 pre-registered leave-one-public-history-out shared-ring diagnostic.

Two synthetic toy families are imported solely from the immutable external
V18 AUDIT harness; no original-world experience, future data or reward law
enters an actual learner. No scientific acceptance/promotion is implied.
"""
import hashlib
import itertools
import json
import math
import subprocess
from pathlib import Path

from research.itd02_v18_intermediate_plasticity_audit import (
    target, ridge_predict, train_candidate, train_v17,
    read_candidate, read_v17,
)
from research.itd02_v20_responsibility_gated_audit import read_v20
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, PUBLIC_CUES, NeighborCarriedPublicLearnerDev,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    IntermediatePlasticRingDev, canonical, MAX_CHECKPOINT_BYTES,
)
from yggdrasil.itd02_v20_causal_credit_dev import (
    ResponsibilityGatedRingDev,
)
from yggdrasil.itd02_v22_shared_context_ring_dev import (
    CELLS, CHANNELS, HEAD_FEATURES, HOPS, LEARNED_SCALARS, MODES,
    SharedContextRingDev, SOURCE_SIGNAL_PER_PASS, EDGE_SIGNAL_PER_PASS,
)

PARENT = "6147b787068caa55a4782e076dd6ae82e651dcbc"
PREREG = "818ebe040844f9858e74fdded7b4ff0515fa10d0"
BLOBS = {
    "yggdrasil/itd02_native_task_bridge_dev.py":
        "71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
    "yggdrasil/itd02_local_ring_memory_dev.py":
        "1db0835d5c99456bcf99a013d4836f49314a9d39",
    "yggdrasil/itd02_v17_neighbor_carried_learner_dev.py":
        "4e3c77797e66df3a26742d23d18f038644891e55",
    "yggdrasil/itd02_v18_intermediate_plasticity_dev.py":
        "711391944be7bd94f1898005d1233bfe52a6f216",
    "research/itd02_v18_intermediate_plasticity_audit.py":
        "7a8f361ff13cf75f716c544add192c2ff9c5aae9",
    "yggdrasil/itd02_v20_causal_credit_dev.py":
        "c7eb9cfc0a4820400fb3c8b78febeb11ae035570",
    "research/itd02_v21_capacity_learning_audit.py":
        "0e1135d87fe3ed0f823d9956cf1eadde81254ea6",
}
EPOCHS = 16
CONTEXTS = tuple(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))


def git(*args):
    return subprocess.check_output(
        ("git",) + args, text=True,
        cwd=Path(__file__).resolve().parents[1]).strip()


def verify():
    assert git("merge-base", "--is-ancestor", PARENT, "HEAD") == ""
    assert git("merge-base", "--is-ancestor", PREREG, "HEAD") == ""
    for path, expected in BLOBS.items():
        assert git("hash-object", path) == expected, (
            "ORIGINAL_NATIVE_OR_CONTROL_SOURCE_DRIFT", path)
    assert CELLS == 8 and CHANNELS == 7 and HEAD_FEATURES == 20
    assert HOPS == 4 and LEARNED_SCALARS == 163
    assert MODES == ("shared", "action_partition")
    assert len(CONTEXTS) == len(set(CONTEXTS)) == 36


def event(model, cue, first, second, reward):
    model.start_observation(cue)
    model.accept_first(first)
    model.accept_second(second, reward, learning=True)


def inspect(model, heldout):
    raw = model.checkpoint()
    assert len(raw) <= MAX_CHECKPOINT_BYTES
    clone = SharedContextRingDev.restore(raw)
    assert clone.checkpoint() == raw
    clone.start_frozen_evaluation()
    freeze = clone.parameters_sha256()
    clone.start_observation(heldout[0])
    clone.accept_first(heldout[1])
    selected = heldout[2]
    prediction = clone.score(selected)
    clone.accept_second(selected, 0.0, learning=False)
    assert clone.parameters_sha256() == freeze
    assert clone.native_ids == model.native_ids
    return prediction, len(raw)


def structural_witness():
    data = {}
    for mode in MODES:
        m = SharedContextRingDev(mode=mode)
        initial = m.parameters_sha256()
        native = dict(m.native_ids)
        first = ("LRV", "Backup", "GoForward", 2.0)
        second = ("docked_MRV", "TurnAround", "Backup", -1.0)
        for cue, actual_first, second_action, reward in (first, second):
            before = [list(row) for row in m.cell_weights]
            biases = list(m.action_biases)
            m.start_observation(cue)
            m.accept_first(actual_first)
            m.accept_second(second_action, reward)
            selected = ACTIONS.index(second_action)
            assert all(m.action_biases[j] == biases[j]
                       for j in range(3) if j != selected)
            changed = [i for i in range(CELLS)
                       if m.cell_weights[i] != before[i]]
            if mode == "action_partition":
                assert all(i % 3 == selected for i in changed), (
                    "OTHER_ACTION_PRIVATE_CELL_CHANGED", changed)
            else:
                assert any(i % 3 != selected for i in changed), (
                    "SHARED_CELLS_DID_NOT_SPAN_OTHER_ACTION_OWNERS")
        assert m.parameters_sha256() != initial
        assert m.native_ids == native
        assert m.updates == 2 and m.transitions == 4
        assert m.reverse_credit_messages == 2 * EDGE_SIGNAL_PER_PASS
        assert m.forward_input_messages == 2 * SOURCE_SIGNAL_PER_PASS
        cold = m.checkpoint()
        assert SharedContextRingDev.restore(cold).checkpoint() == cold
        assert len(cold) <= MAX_CHECKPOINT_BYTES
        data[mode] = {
            "selected_bias_only": True,
            "two_different_actual_selected_actions_experienced": True,
            "learned_parameter_count": LEARNED_SCALARS,
            "original_native_model_unchanged": True,
            "cold_checkpoint_bytes": len(cold),
        }
    # The two arms have identical learned scalar budgets; not identical
    # readout use, because partitioning is the negative sharing control.
    return data


def run_family(*, nonlinear):
    errors = {
        "v22_shared_ring": 0.0,
        "v22_no_share_partition_163_scalars": 0.0,
        "v20_original_causal_credit": 0.0,
        "v18_plastic_gains": 0.0,
        "v18_frozen_gains": 0.0,
        "v17_additive": 0.0,
        "strong_35_example_pooled_interaction_ridge": 0.0,
    }
    cases = []
    max_checkpoint = 0
    shared_updated_cells = 0
    partition_updated_cells = 0
    edge_messages = {"shared_input":0, "shared_output":0,
                     "shared_reverse":0, "partition_input":0,
                     "partition_output":0, "partition_reverse":0}
    for heldout in CONTEXTS:
        shared = SharedContextRingDev(mode="shared")
        partition = SharedContextRingDev(mode="action_partition")
        v20 = ResponsibilityGatedRingDev()
        v18 = IntermediatePlasticRingDev(plastic_intermediate=True)
        frozen = IntermediatePlasticRingDev(plastic_intermediate=False)
        v17 = NeighborCarriedPublicLearnerDev()
        original = dict(shared.native_ids)
        others = [case for case in CONTEXTS if case != heldout]
        assert len(others) == 35
        for _ in range(EPOCHS):
            for cue, first, second in others:
                reward = target(cue, first, second, nonlinear=nonlinear)
                event(shared, cue, first, second, reward)
                event(partition, cue, first, second, reward)
                train_candidate(v20, cue, first, second, reward)
                train_candidate(v18, cue, first, second, reward)
                train_candidate(frozen, cue, first, second, reward)
                train_v17(v17, cue, first, second, reward)
        assert all(m.native_ids == original for m in (
            partition, v20, v18, frozen, v17))
        assert shared.updates == partition.updates == v20.learned_updates == 560
        assert shared.transitions == partition.transitions == 1120
        assert shared.reverse_credit_messages == partition.reverse_credit_messages == 560*EDGE_SIGNAL_PER_PASS
        assert shared.forward_input_messages == partition.forward_input_messages == 560*SOURCE_SIGNAL_PER_PASS
        shared_updated_cells += sum(any(abs(w)>1e-12 for w in row)
                                    for row in shared.cell_weights)
        partition_updated_cells += sum(any(abs(w)>1e-12 for w in row)
                                       for row in partition.cell_weights)

        predicted, size = inspect(shared, heldout)
        control_pred, size_c = inspect(partition, heldout)
        v20_pred, _, size_v20 = read_v20(v20, heldout)
        v18_pred, _, size_v18 = read_candidate(v18, heldout)
        frozen_pred, _, size_frozen = read_candidate(frozen, heldout)
        v17_pred = read_v17(v17, heldout)
        pooled_pred = ridge_predict(others, heldout, nonlinear=nonlinear)
        max_checkpoint = max(max_checkpoint, size, size_c)
        truth = target(*heldout, nonlinear=nonlinear)
        predictions = {
            "v22_shared_ring": predicted,
            "v22_no_share_partition_163_scalars": control_pred,
            "v20_original_causal_credit": v20_pred,
            "v18_plastic_gains": v18_pred,
            "v18_frozen_gains": frozen_pred,
            "v17_additive": v17_pred,
            "strong_35_example_pooled_interaction_ridge": pooled_pred,
        }
        for name, value in predictions.items():
            assert math.isfinite(value), ("NONFINITE_HELDOUT_PREDICTION", name)
            errors[name] += abs(value-truth)
        for model, prefix in ((shared,"shared"), (partition,"partition")):
            edge_messages[prefix+"_input"] += model.forward_input_messages
            edge_messages[prefix+"_output"] += model.forward_output_messages
            edge_messages[prefix+"_reverse"] += model.reverse_credit_messages
        cases.append({
            "family": "nonadditive" if nonlinear else "additive",
            "public_cue": heldout[0], "actual_first": heldout[1],
            "selected_second": heldout[2],
            "reward": round(truth, 12),
            "matched_heldout_predictions": {
                k: round(v, 12) for k,v in predictions.items()
            },
            "training_examples_per_arm": 560,
            "original_native_model_unchanged": True,
        })
    assert len(cases) == 36
    assert max_checkpoint <= MAX_CHECKPOINT_BYTES
    assert shared_updated_cells > 0 and partition_updated_cells > 0
    return {
        "errors": errors, "cases": cases,
        "shared_updated_cells_over_folds": shared_updated_cells,
        "partition_updated_cells_over_folds": partition_updated_cells,
        "max_checkpoint_bytes": max_checkpoint,
        "edge_scalar_messages": edge_messages,
    }


def main():
    verify()
    structure = structural_witness()
    nonlinear = run_family(nonlinear=True)
    additive = run_family(nonlinear=False)
    non = nonlinear["errors"]
    improved = (non["v22_shared_ring"] <=
                0.95 * non["v22_no_share_partition_163_scalars"] and
                non["v22_shared_ring"] <=
                0.95 * non["v20_original_causal_credit"])
    if not improved:
        classification = "V22_SHARED_LOCAL_LEARNING_NO_CONTROLLED_TRANSFER_GAIN__NO_SCIENCE"
    elif non["v22_shared_ring"] >= non["strong_35_example_pooled_interaction_ridge"]:
        classification = "V22_LOCAL_SHARED_TOY_TRANSFER_CONTROL_NOT_BEATEN__NO_SCIENCE"
    else:
        classification = "V22_LOCAL_SHARED_TOY_TRANSFER__NO_SCIENCE"
    cases = nonlinear["cases"] + additive["cases"]
    result = {
        "schema": "ygg.itd02.v22.neighbor_shared_source_public_toy.v1",
        "classification": classification, "source_only": True,
        "original_world_training": False, "scientific_first_use": False,
        "original_native_model_unchanged": True,
        "original_native_ring_cells": CELLS,
        "fixed_source_public_channels": CHANNELS,
        "scalar_output_neighbor_hops": HOPS,
        "trainable_shared_cell_weights": CELLS*HEAD_FEATURES,
        "trainable_selected_action_biases": len(ACTIONS),
        "trainable_scalars_per_v22_arm": LEARNED_SCALARS,
        "fixed_learning_rate": 1.0,
        "public_histories_per_family": 36,
        "heldout_families": 2,
        "training_updates_per_arm_per_fold": 560,
        "matched_toy_absolute_errors": {
            "nonadditive": nonlinear["errors"],
            "additive": additive["errors"],
        },
        "shared_improves_5pct_vs_both_local_controls": improved,
        "beats_strong_conventional_pooled_control":
            non["v22_shared_ring"] <
            non["strong_35_example_pooled_interaction_ridge"],
        "structural_witness": structure,
        "shared_updated_cells_over_folds":
            nonlinear["shared_updated_cells_over_folds"] +
            additive["shared_updated_cells_over_folds"],
        "partition_updated_cells_over_folds":
            nonlinear["partition_updated_cells_over_folds"] +
            additive["partition_updated_cells_over_folds"],
        "max_checkpoint_bytes": max(
            nonlinear["max_checkpoint_bytes"], additive["max_checkpoint_bytes"]),
        "total_edge_scalar_messages": {
            key: nonlinear["edge_scalar_messages"][key] +
                 additive["edge_scalar_messages"][key]
            for key in nonlinear["edge_scalar_messages"]
        },
        "canonical_72_case_sha256": hashlib.sha256(
            canonical(cases)).hexdigest(),
        "qualifier": "ENGINEERING_SYNTHETIC_SHARING_ONLY__NO_NATIVE_SCIENCE",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
