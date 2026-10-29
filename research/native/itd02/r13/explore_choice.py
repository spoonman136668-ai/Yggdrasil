"""Opt-in R13 native exploration selector built on unchanged R10/R11/R12.
No privileged MiniGrid state, hand-written DoorKey answer, or external fallback.
"""
from __future__ import annotations

import hashlib

from research.native.itd02.r10.public_adapter import canonical, public_cues
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells, _feature
from research.native.itd02.r12.outcome_choice import select_public_action

SCHEMA = "yggdrasil.itd02.r13.native-uncertainty-sourceonly.v1"
ACTIONS = tuple(range(7))


def propose_native_action(learner: PublicAffordanceCells, observation: dict) -> dict:
    """Choose an original action from local observed evidence or uncertainty.

    This selector neither updates the learner nor controls env.step. The caller
    must submit its chosen action through R10 and learn only the returned real
    selected public consequence through R11. No action-fallback impersonation.
    """
    if type(learner) is not PublicAffordanceCells:
        raise ValueError("R13_UNTRUSTED_NATIVE_CELLS")

    # R10 validates exact public shape, mission, heading and no privileged keys.
    cues = public_cues(observation)
    baseline = select_public_action(learner, observation, "positive_reward")
    if baseline["action"] is not None:
        return {
            "schema": SCHEMA,
            "status": "SELECT_NATIVE_OBSERVED_POSITIVE_REWARD",
            "action": baseline["action"],
            "native_public_observation_sha256": cues["observation_sha256"],
            "learned_context_samples": baseline["training_samples"],
            "external_fallback": False,
        }
    if baseline["status"] != "ABSTAIN_NO_LEARNED_POSITIVE_ACTION":
        raise ValueError("R13_UNRECOGNIZED_NATIVE_BASE_STATUS")

    support = []
    for action in ACTIONS:
        key = _feature(cues["front"], cues["carried"], action)
        rows = learner.counts.get(key, {})
        if type(rows) is not dict:
            raise ValueError("R13_BAD_NATIVE_CONTEXT_COUNTS")
        amount = 0
        for count in rows.values():
            if type(count) is not int or count < 1 or count > 4096:
                raise ValueError("R13_BAD_NATIVE_COUNT")
            amount += count
        if amount > 4096:
            raise ValueError("R13_BAD_NATIVE_CONTEXT_BUDGET")
        support.append(amount)

    # Public local features and native evidence only; no global agent pose/map.
    tie_source = canonical({
        "front": cues["front"],
        "carried": cues["carried"],
        "direction": cues["direction"],
    })
    start = hashlib.sha256(tie_source).digest()[0] % len(ACTIONS)
    least = min(support)
    for delta in range(len(ACTIONS)):
        action = (start + delta) % len(ACTIONS)
        if support[action] == least:
            return {
                "schema": SCHEMA,
                "status": "SELECT_NATIVE_LEAST_OBSERVED_ACTION",
                "action": action,
                "native_public_observation_sha256": cues["observation_sha256"],
                "learned_context_samples": least,
                "external_fallback": False,
            }
    raise ValueError("R13_UNREACHABLE_NATIVE_SUPPORT_INVARIANT")
