"""V14 preregistered source-PUBLIC context capacity, without model training.

Follows research/itd02_v14_three_phase_context_preregistration.md, committed
FIRST at 703b2c4f98c332e8f5ba54860e825f597cd3d6a4.

This is not an acting experiment, native readout integration, science or
evidence that the public adapter's fan-out is genuinely local computation.
"""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from yggdrasil.itd02_local_ring_memory_dev import (
    ACTIONS, ACTION_SITES, CELLS, OBSERVATIONS,
)
from yggdrasil.itd02_native_task_bridge_dev import RING

EXPECTED_PARENT = "214657d6acdca51493022b96a8688f7f41ff8752"
EXPECTED_PREREG = "703b2c4f98c332e8f5ba54860e825f597cd3d6a4"
EXPECTED_BRIDGE_BLOB = "71eff80e3cfabb627e9d08d558b63f4043ce1fd5"
EXPECTED_MEMORY_BLOB = "1db0835d5c99456bcf99a013d4836f49314a9d39"
PUBLIC_CUES = ("LRV", "MRV", "docked_LRV", "docked_MRV")
SECOND_PUBLIC_OBSERVATION = "Nothing"
REWARD_SITES = (0, 2, 5)
EXPECTED_NEIGHBORS = ((7, 1), (1, 3), (4, 6))


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def phase_bits(cue, first, second, phase):
    """Public-only fixed injection ports; no hidden world/answer parameters."""
    if type(cue) is not str or cue not in PUBLIC_CUES:
        raise ValueError("INVALID_FIRST_PUBLIC_CUE")
    if type(first) is not str or first not in ACTIONS:
        raise ValueError("INVALID_FIRST_SELECTED_PUBLIC_ACTION")
    if type(second) is not str or second not in ACTIONS:
        raise ValueError("INVALID_SECOND_PUBLIC_CANDIDATE")
    if type(phase) is not int or phase not in (0, 1, 2):
        raise ValueError("INVALID_PUBLIC_PHASE")
    index = 9 * PUBLIC_CUES.index(cue) + 3 * ACTIONS.index(first) + ACTIONS.index(second)
    low = (index >> (2 * phase)) & 1
    high = (index >> (2 * phase + 1)) & 1
    bits = [0] * CELLS
    bits[1] = bits[6] = low
    bits[7] = bits[3] = bits[4] = high
    return bits


def ordered_local_word(phases, site):
    if site not in REWARD_SITES:
        raise ValueError("INVALID_REWARD_SITE")
    left, right = RING[site]
    word = 0
    for phase in phases:
        if type(phase) is not list or len(phase) != CELLS:
            raise ValueError("INVALID_PUBLIC_VECTOR")
        if any(type(v) is not int or v not in (0, 1) for v in phase):
            raise ValueError("NONBINARY_PUBLIC_VECTOR")
        word = (word << 1) | phase[left]
        word = (word << 1) | phase[right]
    return word


def git(*args):
    return subprocess.check_output(
        ("git",) + args,
        text=True, cwd=Path(__file__).resolve().parents[1],
    ).strip()


def source_pin():
    assert git("hash-object", "yggdrasil/itd02_native_task_bridge_dev.py") == EXPECTED_BRIDGE_BLOB
    assert git("hash-object", "yggdrasil/itd02_local_ring_memory_dev.py") == EXPECTED_MEMORY_BLOB
    assert git("merge-base", "--is-ancestor", EXPECTED_PARENT, "HEAD") == ""
    assert git("merge-base", "--is-ancestor", EXPECTED_PREREG, "HEAD") == ""


def main():
    source_pin()
    assert CELLS == 8 and ACTION_SITES == REWARD_SITES
    assert tuple(RING[site] for site in REWARD_SITES) == EXPECTED_NEIGHBORS
    assert SECOND_PUBLIC_OBSERVATION in OBSERVATIONS
    assert len(PUBLIC_CUES) == 4 and len(ACTIONS) == 3
    assert 2 ** (2 * 2) < 36 <= 2 ** (2 * 3)

    records = []
    full_vectors = set()
    per_site = {site: set() for site in REWARD_SITES}
    per_site_2phase = {site: set() for site in REWARD_SITES}
    for ordinal, (cue, first, second) in enumerate(
        itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS)
    ):
        assert ordinal == 9 * PUBLIC_CUES.index(cue) + 3 * ACTIONS.index(first) + ACTIONS.index(second)
        views = [phase_bits(cue, first, second, p) for p in range(3)]
        full_vector = tuple(v for view in views for v in view)
        words = tuple(ordered_local_word(views, site) for site in REWARD_SITES)
        records.append({
            "cue": cue, "first_selected_action": first,
            "second_candidate_action": second,
            "phases": views,
            "ordered_reward_words": words,
        })
        full_vectors.add(full_vector)
        for i, site in enumerate(REWARD_SITES):
            per_site[site].add(words[i])
            per_site_2phase[site].add(ordered_local_word(views[:2], site))

    assert len(records) == 36
    assert len(full_vectors) == 36
    assert all(len(per_site[s]) == 36 for s in REWARD_SITES)
    assert all(len(per_site_2phase[s]) == 16 for s in REWARD_SITES)
    assert all(0 <= n < 64 for s in REWARD_SITES for n in per_site[s])

    # Negative controls: invalid and out-of-band fields must not enter context.
    invalid = [
        ("Unknown", "GoForward", "Backup", 0),
        ("LRV", "Unknown", "Backup", 0),
        ("LRV", "GoForward", "Unknown", 0),
        ("LRV", "GoForward", "Backup", 3),
        ("LRV", "GoForward", "Backup", -1),
        ("LRV", "GoForward", "Backup", True),
    ]
    for args in invalid:
        try:
            phase_bits(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(("INVALID_CONTEXT_ACCEPTED", args))
    try:
        phase_bits("LRV", "GoForward", "Backup", 0, source_law="secret")
    except TypeError:
        pass
    else:
        raise AssertionError("HIDDEN_FIELD_ACCEPTED")

    outcome = {
        "schema": "ygg.itd02.v14.source_public_three_phase.capacity.v1",
        "source_only": True,
        "scientific_first_use": False,
        "original_world_training": False,
        "learner_parameters_modified": False,
        "native_ring_modified": False,
        "public_context_count": len(records),
        "distinct_full_context_codes": len(full_vectors),
        "per_reward_site_distinct_ordered_codes": {
            str(s): len(per_site[s]) for s in REWARD_SITES
        },
        "negative_control_per_site_two_phase_codes": {
            str(s): len(per_site_2phase[s]) for s in REWARD_SITES
        },
        "minimum_binary_neighbor_phases": 3,
        "original_native_bridge_blob": EXPECTED_BRIDGE_BLOB,
        "original_local_memory_blob": EXPECTED_MEMORY_BLOB,
        "source_public_records_sha256": hashlib.sha256(canonical(records)).hexdigest(),
        "classification": "V14_PUBLIC_CONTEXT_CAPACITY_POSSIBLE__NO_SCIENCE",
        "next_gate": "INDEPENDENT_LOCAL_READOUT_ADMISSIBILITY_AND_LEARNING_QUALIFICATION",
    }
    print(json.dumps(outcome, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
