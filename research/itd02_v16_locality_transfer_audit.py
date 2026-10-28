"""V16 source-only negative audit of V15 adapter locality and transfer.

This uses only V15's preregistered synthetic public-feedback fixture.
Not original-world learning, protected science, or native architecture acceptance.
"""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from research.itd02_v14_three_phase_context_capacity import (
    PUBLIC_CUES, ordered_local_word, phase_bits,
)
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, ACTION_SITES
from yggdrasil.itd02_native_task_bridge_dev import REWARDS, RING
from yggdrasil.itd02_v15_three_phase_readout_dev import (
    FrozenNativeThreePhaseReadoutDev, HEAD_ENTRIES,
)

PARENT = "332786ac0beca178dbe3f4da442c0512609ceb7c"
PREREG = "792095ac93c40bef2a430db8891b1662ebba18cf"
SOURCE_BLOBS = {
    "yggdrasil/itd02_native_task_bridge_dev.py": "71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
    "yggdrasil/itd02_local_ring_memory_dev.py": "1db0835d5c99456bcf99a013d4836f49314a9d39",
    "research/itd02_v14_three_phase_context_capacity.py": "ac8f24466b5b3ed5977a0abb1116d259f5d28cdc",
    "yggdrasil/itd02_v15_three_phase_readout_dev.py": "fd719f7de63e42247b7eafad75272930e779d1e4",
    "tests/test_itd02_v15_frozen_native_local_readout.py": "d76961595eb5596f3137d13b2acc745e835f728f",
}


def canonical(obj):
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def git(*args):
    return subprocess.check_output(
        ("git",) + args, text=True,
        cwd=Path(__file__).resolve().parents[1],
    ).strip()


def assert_original_source():
    assert git("merge-base", "--is-ancestor", PARENT, "HEAD") == ""
    assert git("merge-base", "--is-ancestor", PREREG, "HEAD") == ""
    for path, sha in SOURCE_BLOBS.items():
        assert git("hash-object", path) == sha, "SOURCE_BLOB_DRIFT: " + path
    assert ACTION_SITES == (0, 2, 5)
    assert all(len(RING[site]) == 2 for site in ACTION_SITES)
    assert HEAD_ENTRIES == 64


def reward(cue, first, second):
    # V15 SYNTHETIC public mechanical fixture, NOT an original reward law.
    return REWARDS[
        (PUBLIC_CUES.index(cue) + ACTIONS.index(first) + ACTIONS.index(second)) % 3
    ]


def begin(model, cue, first):
    model.start_observation(cue)
    model.accept_public_transition(
        first, "Nothing", 0, learning=False, terminal=False)
    model.start_observation("Nothing")


def train(model, cue, first, second):
    begin(model, cue, first)
    model.accept_public_transition(
        second, "Nothing", reward(cue, first, second),
        learning=True, terminal=True)
    model.reset_episode()


def assert_neighborhood_sensitivity():
    checks = 0
    for site in ACTION_SITES:
        phases = [
            phase_bits("docked_LRV", "Backup", "GoForward", p)
            for p in range(3)
        ]
        baseline = ordered_local_word(phases, site)
        left, right = RING[site]
        assert left != right and site not in (left, right)
        for phase in range(3):
            for neighbor in (left, right):
                changed = [list(v) for v in phases]
                changed[phase][neighbor] ^= 1
                assert ordered_local_word(changed, site) != baseline
                checks += 1
            # Both reward-head site itself and another remote non-neighbor
            # must have no effect on its local readout word.
            distant = next(
                j for j in range(8)
                if j not in (site, left, right)
            )
            for remote in (site, distant):
                changed = [list(v) for v in phases]
                changed[phase][remote] ^= 1
                assert ordered_local_word(changed, site) == baseline
                checks += 1
    assert checks == 36
    return checks


def main():
    assert_original_source()
    neighborhood_checks = assert_neighborhood_sensitivity()
    histories = list(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
    assert len(histories) == 36 and len(set(histories)) == 36

    per_site_words = {site: set() for site in ACTION_SITES}
    for cue, first, second in histories:
        phases = [phase_bits(cue, first, second, p) for p in range(3)]
        for site in ACTION_SITES:
            per_site_words[site].add(ordered_local_word(phases, site))
    assert all(len(x) == 36 for x in per_site_words.values())

    records = []
    nonzero_unpredicted = 0
    state_ablation_matches = 0
    for heldout in histories:
        model = FrozenNativeThreePhaseReadoutDev()
        ids = dict(model.original_ids)
        assert len(model.heads) == 3
        assert all(len(head) == 64 for head in model.heads)
        initial_params = model.parameters_sha256()
        for context in histories:
            if context != heldout:
                train(model, *context)
        assert model.local_updates == 35
        assert model.bridge.model_identities() == ids
        assert model.parameters_sha256() != initial_params

        checkpoint = model.checkpoint()
        model = FrozenNativeThreePhaseReadoutDev.restore(checkpoint)
        assert model.checkpoint() == checkpoint
        begin(model, heldout[0], heldout[1])

        action_index = ACTIONS.index(heldout[2])
        predicted = model.local_scores()[action_index]
        expected = reward(*heldout)
        # One-to-one public context lookup cannot update this unseen slot.
        assert predicted == 0.0, ("UNEXPECTED_HELDOUT_TRANSFER", heldout, predicted)
        if expected != 0:
            nonzero_unpredicted += 1

        # Alter native inference/retained state, *not* the public tuple
        # or source-learned parameters; the LOCAL-only table still reads
        # identically because it doesn't consume these native messages.
        perturbed = FrozenNativeThreePhaseReadoutDev.restore(model.checkpoint())
        perturbed.bridge.cell_trace[0] = 0.75
        perturbed.bridge.memory.memory[0] = 0.25
        assert perturbed.local_scores() == model.local_scores()
        assert perturbed.bridge.model_identities() == ids
        state_ablation_matches += 1

        model.accept_public_transition(
            heldout[2], "Nothing", expected, learning=False, terminal=True)
        model.reset_episode()
        assert model.bridge.model_identities() == ids
        records.append({
            "public_cue": heldout[0], "actual_first_action": heldout[1],
            "heldout_second_action": heldout[2], "synthetic_reward": expected,
            "local_prediction": predicted, "other_histories_trained": 35,
            "original_native_model_unchanged": True,
            "cold_restore_equal": True,
            "internal_inference_state_ablation_invariant": True,
        })

    assert len(records) == 36 and nonzero_unpredicted == 24
    assert state_ablation_matches == 36
    total_error = sum(abs(r["synthetic_reward"] - r["local_prediction"]) for r in records)
    assert total_error == 156
    outcome = {
        "schema": "ygg.itd02.v16.locality_falsification.source_only.v1",
        "source_only": True, "scientific_first_use": False,
        "original_world_training": False,
        "model_parameters_modified": False,
        "public_histories": 36,
        "leave_one_context_out_folds": len(records),
        "trained_other_histories_each_fold": 35,
        "unseen_context_local_zero_predictions": 36,
        "nonzero_unseen_rewards_not_predicted": nonzero_unpredicted,
        "heldout_absolute_reward_error": total_error,
        "local_internal_state_ablation_invariant_count": state_ablation_matches,
        "neighbor_vs_distant_bit_checks": neighborhood_checks,
        "per_reward_site_distinct_context_words": {
            str(s): len(per_site_words[s]) for s in ACTION_SITES
        },
        "learned_adapter_scalars": len(ACTION_SITES) * HEAD_ENTRIES,
        "original_v15_adapter_blob": SOURCE_BLOBS[
            "yggdrasil/itd02_v15_three_phase_readout_dev.py"],
        "complete_case_record_sha256": hashlib.sha256(canonical(records)).hexdigest(),
        "classification": (
            "V16_ASSOCIATIVE_LOOKUP_NO_HELDOUT_TRANSFER__"
            "NOT_NATIVE_DISTRIBUTED_PROOF"
        ),
        "next_gate": "NEW_BOUNDED_NEIGHBOR_CARRIED_LEARNED_STATE_BEFORE_SCIENCE",
    }
    print(json.dumps(outcome, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
