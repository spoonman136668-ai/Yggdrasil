"""Frozen-source V13 feasibility audit: public two-step context encodings only.

No original-world data, fitting, source-law oracle, dispatch, or scientific claims.
The source blob check prevents reusing the receipt against a different learner.
"""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, OBSERVATIONS, ACTION_SITES
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev

EXPECTED_BRIDGE_BLOB = "71eff80e3cfabb627e9d08d558b63f4043ce1fd5"
PUBLIC_CUES = ("LRV", "MRV", "docked_LRV", "docked_MRV")
NEXT_OBSERVATION = "Nothing"
SITES = {1: "hi", 7: "lo", 3: "lo", 4: "hi", 6: "lo"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def independent_public_phase(observation, action, phase):
    if observation not in OBSERVATIONS or action not in ACTIONS or phase not in (0, 1):
        raise ValueError("INVALID_SOURCE_PUBLIC_CONTEXT")
    index = ACTIONS.index(action) * len(OBSERVATIONS) + OBSERVATIONS.index(observation)
    high, low = divmod(index, 4)
    out = [0] * 8
    for site, symbol in SITES.items():
        out[site] = ((high if symbol == "hi" else low) >> phase) & 1
    return out


def independent_pair(cue, first, second):
    return tuple(
        independent_public_phase(NEXT_OBSERVATION, second, phase)[site]
        ^ independent_public_phase(cue, first, phase)[site]
        for phase in (0, 1) for site in range(8)
    )


def actual_frozen_pair(cue, first, second):
    model = NativeTaskRingBridgeDev()
    identities = model.model_identities()
    model.start_frozen_evaluation(identities["native"], identities["memory"])
    model.start_observation(cue)
    model.accept_public_transition(first, NEXT_OBSERVATION, 0,
                                   learning=False, terminal=False)
    model.start_observation(NEXT_OBSERVATION)
    checkpoint = model.checkpoint()
    assert NativeTaskRingBridgeDev.restore(checkpoint).checkpoint() == checkpoint
    bits = tuple(bit for phase in (0, 1)
                 for bit in model._task_bits(NEXT_OBSERVATION, second, phase))
    assert model.model_identities() == identities
    model.accept_public_transition(second, NEXT_OBSERVATION, 0,
                                   learning=False, terminal=True)
    assert model.temporal_eligibility is None
    assert model.model_identities() == identities
    model.reset_episode()
    return bits


def main():
    root = Path(__file__).resolve().parents[1]
    blob = subprocess.check_output(
        ["git", "hash-object", "yggdrasil/itd02_native_task_bridge_dev.py"],
        cwd=root, text=True).strip()
    if blob != EXPECTED_BRIDGE_BLOB:
        raise SystemExit("FAIL_CLOSED_SOURCE_BLOB_DRIFT:" + blob)

    cases = []
    groups = {}
    reward_neighbor_codes = {str(site): set() for site in ACTION_SITES}
    for cue, first, second in itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS):
        reconstructed = independent_pair(cue, first, second)
        actual = actual_frozen_pair(cue, first, second)
        assert actual == reconstructed, (cue, first, second)
        entry = {"cue": cue, "first_selected": first, "second_selected": second,
                 "v12_two_phase_binary": list(actual)}
        cases.append(entry)
        groups.setdefault(actual, []).append((cue, first, second))
        for site in ACTION_SITES:
            neighbors = ((site - 1) % 8, (site + 1) % 8)
            fingerprint = tuple(actual[phase * 8 + n]
                                for phase in (0, 1) for n in neighbors)
            reward_neighbor_codes[str(site)].add(fingerprint)

    assert len(cases) == len(PUBLIC_CUES) * len(ACTIONS) ** 2 == 36
    aliased = len(cases) - len(groups)
    assert len(groups) == 15 and aliased == 21, "SOURCE_PINNED_AUDIT_EXPECTATION_DRIFT"
    witnesses = [items for items in groups.values() if len(items) > 1]
    assert witnesses and all(len(items) > 1 for items in witnesses)
    outcome = {
        "schema": "ygg.itd02.v13.public-context-capacity.source-free.v1",
        "source_git_blob": blob,
        "source_only": True,
        "original_world_training": False,
        "scientific_first_use": False,
        "learner_parameters_modified": False,
        "legal_public_two_step_contexts": 36,
        "distinct_v12_full_context_codes": len(groups),
        "aliased_contexts": aliased,
        "local_reward_head_neighbor_code_counts": {
            site: len(codes) for site, codes in reward_neighbor_codes.items()},
        "record_sha256": hashlib.sha256(canonical(cases)).hexdigest(),
        "example_collisions": [group[:4] for group in witnesses[:4]],
        "classification": "V12_CONTEXT_NONIDENTIFIABLE__NO_SCIENCE",
        "next_gate": "QUALIFY_PUBLIC_ONLY_NONCOLLIDING_LOCAL_CONTEXT_ENCODING_BEFORE_ACTING",
    }
    print(json.dumps(outcome, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
