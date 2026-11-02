"""Evaluator-only deterministic MR32-P route world and exact coalition replay.

Do not import this module from the policy process.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Mapping, Sequence

TOTAL = 16
ACTIVE = 7
EVENTS = 16
WORLD_SIZE = 11
ROLE_WEIGHTS = ((1, 3, 2, 5), (4, 1, 5, 2))
TASK_SCHEMA = "yggdrasil.mr32p.private-task-spec.v1"


@dataclass(frozen=True)
class PrivateTaskSpec:
    schema: str
    seed: int
    regime: int
    episode: int
    public_items: tuple[int, ...]
    initial_position: int
    target_position: int


def public_memory_records() -> list[dict]:
    rows = []
    for item in range(TOTAL):
        rows.append({
            "item_id": item,
            "evidence_level": item % 8,
            "error_level": (item // 2 + item // 8) % 4,
            "contradiction_level": (3 * item + item // 4) % 4,
            "proposed_action": (7 * item + 3) & 1,
        })
    return rows


def make_private_task(seed: int, regime: int, episode: int) -> PrivateTaskSpec:
    if isinstance(seed, bool) or not isinstance(seed, int) or seed <= 0:
        raise ValueError("TASK_SEED_RANGE")
    if regime not in (0, 1):
        raise ValueError("TASK_REGIME_RANGE")
    if isinstance(episode, bool) or not isinstance(episode, int) or episode < 0:
        raise ValueError("TASK_EPISODE_RANGE")
    episode_seed = (
        (seed * 1_000_003) ^ (regime * 97_409)
        ^ (episode * 65_537) ^ 0x4D523250
    )
    public_items = tuple(random.Random(episode_seed).sample(range(TOTAL), EVENTS))
    records = {row["item_id"]: row for row in public_memory_records()}
    weights = ROLE_WEIGHTS[regime]
    target_sum = seed % WORLD_SIZE
    for item in public_items:
        row = records[item]
        target_sum += (
            (item + 1) * weights[item % 4]
            + 2 * row["evidence_level"]
            + 3 * row["error_level"]
            - row["contradiction_level"]
        )
    return PrivateTaskSpec(
        TASK_SCHEMA, seed, regime, episode, public_items,
        seed % WORLD_SIZE, target_sum % WORLD_SIZE
    )


def transition(position: int, item: int, action: int, regime: int) -> int:
    if not 0 <= position < WORLD_SIZE:
        raise ValueError("WORLD_POSITION_RANGE")
    if not 0 <= item < TOTAL:
        raise ValueError("WORLD_ITEM_RANGE")
    if isinstance(action, bool) or not isinstance(action, int) or action not in (0, 1):
        raise ValueError("WORLD_ACTION_RANGE")
    if regime not in (0, 1):
        raise ValueError("WORLD_REGIME_RANGE")
    evidence_level = item % 8
    return (
        position + (2 * action - 1) * (1 + evidence_level)
        + (item % 3) + 1 + regime
    ) % WORLD_SIZE


def terminal_return(actions_by_item: Mapping[int, int],
                    spec: PrivateTaskSpec) -> int:
    if spec.schema != TASK_SCHEMA:
        raise ValueError("PRIVATE_TASK_SCHEMA")
    if set(actions_by_item) != set(range(TOTAL)):
        raise ValueError("TASK_ACTION_ITEM_SET")
    position = spec.initial_position
    for item in spec.public_items:
        action = actions_by_item[item]
        position = transition(position, item, action, spec.regime)
    return int(position == spec.target_position)


def evaluate_all_coalitions(
    spec: PrivateTaskSpec,
    selected_item_ids: Sequence[int],
) -> dict[int, int]:
    """Run the complete 128-player-subset game from identical initial state.

    Bit j of a coalition mask denotes selected_item_ids[j]. Item IDs must be
    ascending, which also fixes tie/remainder order in the attribution kernel.
    """
    if spec.schema != TASK_SCHEMA:
        raise ValueError("PRIVATE_TASK_SCHEMA")
    if len(selected_item_ids) != ACTIVE:
        raise ValueError("COALITION_PLAYER_COUNT")
    if tuple(selected_item_ids) != tuple(sorted(selected_item_ids)):
        raise ValueError("COALITION_PLAYERS_NOT_SORTED")
    if len(set(selected_item_ids)) != ACTIVE:
        raise ValueError("COALITION_PLAYERS_NOT_UNIQUE")
    if any(item not in range(TOTAL) for item in selected_item_ids):
        raise ValueError("COALITION_PLAYER_RANGE")
    records = {row["item_id"]: row for row in public_memory_records()}
    bit_by_item = {item: index for index, item in enumerate(selected_item_ids)}
    values = {}
    for mask in range(1 << ACTIVE):
        position = spec.initial_position
        for item in spec.public_items:
            player_index = bit_by_item.get(item)
            enabled = player_index is not None and bool(mask & (1 << player_index))
            action = records[item]["proposed_action"] if enabled else 0
            position = transition(position, item, action, spec.regime)
        values[mask] = int(position == spec.target_position)
    if set(values) != set(range(1 << ACTIVE)):
        raise RuntimeError("COALITION_MASK_COVERAGE")
    return values


def public_policy_begin_message(method: str, state: dict,
                               policy_nonce: int) -> dict:
    """Policy receives public memory records but no query stream or task identity."""
    return {
        "schema": "yggdrasil.mr32p.policy-message.v1",
        "operation": "begin",
        "method": method,
        "records": public_memory_records(),
        "state": state,
        "policy_nonce": policy_nonce,
    }


def public_policy_step_message(method: str, step: int, item_id: int,
                               selected_items: Sequence[int],
                               state: dict) -> dict:
    """Pass only the current public cue; never pass future query items."""
    records = public_memory_records()
    if isinstance(item_id, bool) or not isinstance(item_id, int) or item_id not in range(TOTAL):
        raise ValueError("PUBLIC_POLICY_STEP_ITEM_RANGE")
    return {
        "schema": "yggdrasil.mr32p.policy-message.v1",
        "operation": "step",
        "method": method,
        "step": step,
        "item_id": item_id,
        "selected_items": list(selected_items),
        "record": records[item_id],
        "state": state,
    }
