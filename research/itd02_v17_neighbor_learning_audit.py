"""V17 frozen source-only 36-fold public-composition engineering audit.

The reward formula below is an explicitly declared TOY function, not any world
law, target from source-owner information, or scientific first-use.
"""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CHANNELS, CELLS, HOPS, MAX_BYTES,
    NeighborCarriedPublicLearnerDev, PUBLIC_CUES, RING,
    neighbor_transport, site_pulses,
)

PARENT = "a63ccae27cb5f88e6e3851b0e5acc0d39aef8c7e"
PREREG = "92531456e6052d3b2d76cc95dd982fb6ff020781"
BRIDGE_BLOB = "71eff80e3cfabb627e9d08d558b63f4043ce1fd5"
RING_MEMORY_BLOB = "1db0835d5c99456bcf99a013d4836f49314a9d39"
CUE_CONTRIBUTIONS = (-0.8, 0.3, 1.0, -0.2)
FIRST_CONTRIBUTIONS = (-0.5, 0.0, 0.5)
SECOND_CONTRIBUTIONS = (-0.5, 0.0, 0.5)
EPOCHS = 16


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def toy_reward(cue, first, second):
    return (-1.0 + CUE_CONTRIBUTIONS[PUBLIC_CUES.index(cue)] +
            FIRST_CONTRIBUTIONS[ACTIONS.index(first)] +
            SECOND_CONTRIBUTIONS[ACTIONS.index(second)])


def git(*args):
    return subprocess.check_output(
        ("git",) + args, text=True, cwd=Path(__file__).resolve().parents[1],
    ).strip()


def verify_source():
    assert git("merge-base", "--is-ancestor", PARENT, "HEAD") == ""
    assert git("merge-base", "--is-ancestor", PREREG, "HEAD") == ""
    assert git("hash-object", "yggdrasil/itd02_native_task_bridge_dev.py") == BRIDGE_BLOB
    assert git("hash-object", "yggdrasil/itd02_local_ring_memory_dev.py") == RING_MEMORY_BLOB
    assert CELLS == 8 and CHANNELS == 7 and HOPS == 4
    assert ACTION_SITES == (0, 2, 5) and len(RING) == CELLS


def first_step(model, cue, actual_first):
    model.start_observation(cue)
    model.accept_first(actual_first)


def train(model, cue, first, second):
    first_step(model, cue, first)
    model.accept_second(second, toy_reward(cue, first, second), learning=True)


def main():
    verify_source()
    contexts = list(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
    assert len(contexts) == 36 and len(set(contexts)) == 36
    records = []
    total_full_error = 0.0
    total_no_message_error = 0.0
    total_zero_lookup_error = 0.0
    max_checkpoint_bytes = 0
    total_edge_messages = 0
    for heldout in contexts:
        model = NeighborCarriedPublicLearnerDev()
        original = dict(model.native_ids)
        for _ in range(EPOCHS):
            for other in contexts:
                if other != heldout:
                    train(model, *other)
        assert model.learned_updates == 35 * EPOCHS
        assert model.transitions == 2 * 35 * EPOCHS
        assert model.edge_scalar_messages == 35 * EPOCHS * 8 * 2 * 7 * 4
        assert model.native_ids == original
        assert len(model.weights) == 3 and all(len(row) == 8 for row in model.weights)
        saved = model.checkpoint()
        max_checkpoint_bytes = max(max_checkpoint_bytes, len(saved))
        recovered = NeighborCarriedPublicLearnerDev.restore(saved)
        assert recovered.checkpoint() == saved
        first_step(recovered, heldout[0], heldout[1])
        selected = ACTIONS.index(heldout[2])
        delivered = recovered.delivered[ACTION_SITES[selected]]
        assert sum(delivered) == 2.0
        assert delivered[PUBLIC_CUES.index(heldout[0])] == 1.0
        assert delivered[4 + ACTIONS.index(heldout[1])] == 1.0
        full_score = recovered.local_scores()[selected]
        no_message_score = recovered.diagnostic_zero_message_scores()[selected]
        truth = toy_reward(*heldout)
        full_err = abs(truth - full_score)
        no_message_err = abs(truth - no_message_score)
        zero_lookup_err = abs(truth)  # V15 unvisited unique slot defaults zero
        total_full_error += full_err
        total_no_message_error += no_message_err
        total_zero_lookup_error += zero_lookup_err
        assert recovered.native_ids == original
        before = recovered.parameters_sha256()
        recovered.accept_second(heldout[2], truth, learning=False)
        assert recovered.parameters_sha256() == before
        total_edge_messages += recovered.edge_scalar_messages
        records.append({
            "cue": heldout[0], "actual_first": heldout[1],
            "selected_second": heldout[2], "toy_reward": truth,
            "neighbor_prediction": full_score,
            "same_weights_no_message_prediction": no_message_score,
            "zero_unvisited_lookup_prediction": 0.0,
            "full_absolute_error": full_err,
            "no_message_absolute_error": no_message_err,
            "lookup_absolute_error": zero_lookup_err,
            "trained_other_histories": 35,
            "training_epochs": EPOCHS,
        })

    # Direct local source pulse is NOT an all-cells/global history broadcast.
    for cue in PUBLIC_CUES:
        for action in ACTIONS:
            pulse = site_pulses(cue, action)
            raw, zero_count = neighbor_transport(pulse, hops=0)
            delivered, four_hop_count = neighbor_transport(pulse, hops=4)
            assert raw == pulse and zero_count == 0
            assert four_hop_count == 448
            assert sum(sum(row) for row in raw) == 2.0
            assert all(sum(row) == 2.0 for row in delivered)
    # Source-only toy engineering acceptance. No scientific inference.
    assert total_full_error < 2.0, ("LOW_RANK_TOY_TRANSFER_FAILED", total_full_error)
    assert total_no_message_error > 10.0, (
        "NEIGHBOR_TRANSPORT_CAUSAL_ABLATION_FAILED", total_no_message_error)
    assert total_full_error < total_zero_lookup_error
    assert max_checkpoint_bytes <= MAX_BYTES
    result = {
        "schema": "ygg.itd02.v17.neighbor_carried_additive_toy.source_only.v1",
        "source_only": True, "scientific_first_use": False,
        "original_world_training": False,
        "original_native_model_unchanged": True,
        "original_memory_model_unchanged": True,
        "fixed_message_routing_learned": False,
        "intermediate_cell_plasticity_demonstrated": False,
        "four_hops_effectively_global": True,
        "public_histories": 36, "leave_one_out_folds": 36,
        "synthetic_training_epochs": EPOCHS,
        "synthetic_training_updates_per_fold": 35 * EPOCHS,
        "learned_action_head_scalars": 3 * 8,
        "fixed_public_tag_channels": 7,
        "source_local_pulse_sites": 8,
        "neighbor_hops": HOPS,
        "total_training_and_frozen_eval_edge_scalar_messages": total_edge_messages,
        "max_checkpoint_bytes": max_checkpoint_bytes,
        "heldout_neighbor_total_absolute_error": total_full_error,
        "heldout_no_message_total_absolute_error": total_no_message_error,
        "heldout_zero_lookup_total_absolute_error": total_zero_lookup_error,
        "complete_case_record_sha256": hashlib.sha256(canonical(records)).hexdigest(),
        "classification": "V17_NEIGHBOR_CARRIED_ADDITIVE_TOY_TRANSFER__NO_SCIENCE",
        "next_gate": "NON_ADDITIVE_COMPOSITION_AND_LEARNED_INTERMEDIATE_CELL_PLASTICITY",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
