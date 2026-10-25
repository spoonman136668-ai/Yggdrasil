"""R12 learned-public-consequence action selection.

The objective is explicit ("carrying_changed", "visible_door_state_changed",
"positive_reward"); it is NOT autonomously inferred from a mission. Selection
uses exact selected-action consequence counts from the existing R11 learner,
never hand-codes "key => pickup", "door => toggle" or true simulator state.

All costs, predictions and abstentions are public-observation source-only.
"""
from __future__ import annotations

import math

from research.native.itd02.r10.public_adapter import ACTION_NAMES, public_cues
from research.native.itd02.r11.affordance_cells import (
    PublicAffordanceCells, _feature,
)

OBJECTIVE_BITS = {
    "carrying_changed": 2,
    "visible_door_state_changed": 1,
    "positive_reward": 4,
}


def select_public_action(learner, public_obs, objective, costs=None, min_samples=1):
    """Select a supported legal action based only on previously learned effects.

    No exploration claim: unobserved action/context cells are explicitly
    reported rather than assigned an optimistic outcome, and zero/negative
    net-utility cells cannot drive source actions.
    """
    if type(learner) is not PublicAffordanceCells:
        raise ValueError("R12_UNTRUSTED_LEARNER")
    if type(objective) is not str or objective not in OBJECTIVE_BITS:
        raise ValueError("R12_OBJECTIVE_NOT_PUBLIC")
    if type(min_samples) is not int or not 1 <= min_samples <= 4096:
        raise ValueError("R12_INVALID_MINIMUM_EVIDENCE")
    if costs is None:
        costs = [0.0] * len(ACTION_NAMES)
    if type(costs) not in (list, tuple) or len(costs) != len(ACTION_NAMES):
        raise ValueError("R12_INVALID_COST_VECTOR")
    if any(type(c) not in (float, int) or not math.isfinite(c) or not 0 <= c <= 1
           for c in costs):
        raise ValueError("R12_INVALID_COST_VALUE")

    # public_cues rejects hidden/global state, invalid pixel encoding and mission.
    cues = public_cues(public_obs)
    choices = []
    unknown = []
    insufficient = []
    bit = OBJECTIVE_BITS[objective]

    for action in range(len(ACTION_NAMES)):
        context = _feature(cues["front"], cues["carried"], action)
        rows = learner.counts.get(context)
        if rows is None:
            unknown.append(action)
            continue
        if type(rows) is not dict or any(type(n) is not int or not 1 <= n <= 4096
                                        for n in rows.values()):
            raise ValueError("R12_LEARNER_COUNT_CORRUPTION")
        samples = sum(rows.values())
        if samples < min_samples:
            insufficient.append(action)
            continue
        successes = sum(n for code, n in rows.items() if int(code) & (1 << bit))
        probability = successes / samples
        advantage = probability - float(costs[action])
        if probability > 0 and advantage > 0:
            choices.append((advantage, probability, samples, action))

    summary = {
        "objective": objective,
        "unknown_actions": unknown,
        "insufficient_evidence_actions": insufficient,
        "public_observation_sha256": cues["observation_sha256"],
    }
    if not choices:
        return dict(summary, status="ABSTAIN_NO_LEARNED_POSITIVE_ACTION",
                    action=None, action_name=None, expected_benefit=0.0,
                    net_benefit=0.0, training_samples=0)

    # Same-score deterministic lower original source action ID, never a
    # handcrafted action-to-goal mapping.
    advantage, probability, samples, action = sorted(
        choices, key=lambda x: (-x[0], x[3])
    )[0]
    return dict(summary, status="SELECT_LEARNED_PUBLIC_ACTION",
                action=action, action_name=ACTION_NAMES[action],
                expected_benefit=probability, net_benefit=advantage,
                training_samples=samples)
