"""Public-event boundary for the pinned upstream MiniGrid MemoryEnv.

Pure validator/projector only. Never imports, instantiates, resets, or steps
MiniGrid. The observation is the raw public Gymnasium observation; the upstream
info dictionary and environment instance are never forwarded to a learner.
This contract does not attest the executing worker or grant first-use rights.
"""
from __future__ import annotations

import hashlib
import json
import math
from operator import index

SCHEMA = "ygg.itd02.minigrid_memory.public_event.v1"
MISSION = "go to the matching object at the end of the hallway"
SOURCE = {
    "repository": "Farama-Foundation/Minigrid",
    "commit": "7f5853792ea7f04f75614661006d87fcf949f26d",
    "memory_git_blob": "660b0a1b769948034c87bb421759c2b9a4f24548",
    "base_env_git_blob": "eb29e9a902de0715ab77ec981a2113576d7664fa",
    "actions_git_blob": "b440438bcb5a76a113d9d947b87a54dc8479ab15",
    "registration_git_blob": "41b4a731255d19bdf61072b7100e752a759a3ae4",
    "license_git_blob": "880057397a1f9f7b3b1f0870eb84fa699ecbf50c",
    "claim": "PINNED_SOURCE_IDENTITY_NOT_EXECUTION_ATTESTATION",
}
MAX_SEED = (1 << 32) - 1
MAX_STEPS = 245  # fixed MiniGrid-MemoryS7-v0 default: 5 * size**2
PUBLIC_EVENT_KEYS = frozenset({
    "schema", "source", "episode_seed", "seq", "kind", "observation",
    "action", "reward", "terminated", "truncated",
})


def _int(value, low, high, label):
    if isinstance(value, bool):
        raise ValueError("INVALID_" + label.upper())
    try:
        number = index(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("INVALID_" + label.upper()) from exc
    if not low <= number <= high:
        raise ValueError("INVALID_" + label.upper())
    return int(number)


def source_identity(receipt):
    """Check stated immutable source identity; this is not worker attestation."""
    if type(receipt) is not dict or receipt != SOURCE:
        raise ValueError("SOURCE_PIN_MISMATCH")
    return dict(SOURCE)


def _image_rows(image):
    shape = getattr(image, "shape", None)
    if shape is not None and tuple(shape) != (7, 7, 3):
        raise ValueError("INVALID_PUBLIC_IMAGE_SHAPE")
    tolist = getattr(image, "tolist", None)
    if callable(tolist):
        image = tolist()
    if type(image) not in (list, tuple) or len(image) != 7:
        raise ValueError("INVALID_PUBLIC_IMAGE_ROWS")
    rows = []
    for row in image:
        if type(row) not in (list, tuple) or len(row) != 7:
            raise ValueError("INVALID_PUBLIC_IMAGE_COLUMNS")
        encoded_row = []
        for cell in row:
            if type(cell) not in (list, tuple) or len(cell) != 3:
                raise ValueError("INVALID_PUBLIC_IMAGE_CHANNELS")
            encoded_cell = [_int(channel, 0, 255, "image_byte") for channel in cell]
            encoded_row.append(encoded_cell)
        rows.append(encoded_row)
    return rows


def project_observation(observation):
    """Preserve all public observation fields; reject extras and private objects."""
    if type(observation) is not dict or set(observation) != {"image", "direction", "mission"}:
        raise ValueError("PUBLIC_OBSERVATION_SCHEMA_MISMATCH")
    direction = _int(observation["direction"], 0, 3, "direction")
    mission = observation["mission"]
    if type(mission) is not str or mission != MISSION:
        raise ValueError("MISSION_MISMATCH")
    return {
        "image": _image_rows(observation["image"]),
        "direction": direction,
        "mission": mission,
    }


def _event(seed, seq, kind, observation, action, reward, terminated, truncated, receipt):
    seed = _int(seed, 0, MAX_SEED, "episode_seed")
    seq = _int(seq, 0, MAX_STEPS, "sequence")
    if kind not in ("reset", "transition"):
        raise ValueError("INVALID_EVENT_KIND")
    if type(terminated) is not bool or type(truncated) is not bool:
        raise ValueError("INVALID_TERMINATION_FLAGS")
    event = {
        "schema": SCHEMA,
        "source": source_identity(receipt),
        "episode_seed": seed,
        "seq": seq,
        "kind": kind,
        "observation": project_observation(observation),
        "action": action,
        "reward": reward,
        "terminated": terminated,
        "truncated": truncated,
    }
    if set(event) != PUBLIC_EVENT_KEYS:
        raise ValueError("PUBLIC_EVENT_SCHEMA_DRIFT")
    return event


def project_reset(result, *, episode_seed, source_receipt):
    """Project obs only; never inspect/reset-info or copy it to learner context."""
    if type(result) is not tuple or len(result) != 2:
        raise ValueError("INVALID_UPSTREAM_RESET_SHAPE")
    observation, _info = result
    return _event(episode_seed, 0, "reset", observation, None, 0.0,
                  False, False, source_receipt)


def project_step(result, *, episode_seed, seq, action, source_receipt):
    """Project the five-tuple while dropping raw info without traversing it."""
    seq = _int(seq, 1, MAX_STEPS, "sequence")
    action = _int(action, 0, 6, "action")
    if type(result) is not tuple or len(result) != 5:
        raise ValueError("INVALID_UPSTREAM_STEP_SHAPE")
    observation, reward, terminated, truncated, _info = result
    # _info is intentionally not read, traversed, copied or serialized.
    if type(reward) not in (int, float) or isinstance(reward, bool):
        raise ValueError("INVALID_PUBLIC_REWARD")
    reward = float(reward)
    if not math.isfinite(reward) or not 0.0 <= reward <= 1.0:
        raise ValueError("INVALID_PUBLIC_REWARD")
    return _event(episode_seed, seq, "transition", observation, action, reward,
                  terminated, truncated, source_receipt)


def validate_episode(events):
    """Check public receipt order and reject data after the first terminal event."""
    if type(events) not in (list, tuple) or not 2 <= len(events) <= MAX_STEPS + 1:
        raise ValueError("INVALID_EPISODE_LENGTH")
    if any(type(event) is not dict or set(event) != PUBLIC_EVENT_KEYS for event in events):
        raise ValueError("NONPUBLIC_EVENT_FIELDS")
    if any(event.get("schema") != SCHEMA or event.get("source") != SOURCE for event in events):
        raise ValueError("EVENT_SOURCE_DRIFT")
    seeds = {event.get("episode_seed") for event in events}
    if len(seeds) != 1:
        raise ValueError("EPISODE_SEED_DRIFT")
    for event in events:
        if type(event["episode_seed"]) is not int or not 0 <= event["episode_seed"] <= MAX_SEED:
            raise ValueError("INVALID_EPISODE_SEED")
        if type(event["seq"]) is not int or not 0 <= event["seq"] <= MAX_STEPS:
            raise ValueError("INVALID_EVENT_SEQUENCE")
        if type(event["terminated"]) is not bool or type(event["truncated"]) is not bool:
            raise ValueError("INVALID_TERMINATION_FLAGS")
        normalized = project_observation(event["observation"])
        if normalized != event["observation"]:
            raise ValueError("NONCANONICAL_PUBLIC_OBSERVATION")
    first = events[0]
    if first["kind"] != "reset" or first["seq"] != 0 or first["action"] is not None:
        raise ValueError("MISSING_RESET_EVENT")
    if type(first["reward"]) is not float or first["reward"] != 0.0 or first["terminated"] or first["truncated"]:
        raise ValueError("INVALID_RESET_EVENT")
    for i, event in enumerate(events[1:], start=1):
        if event["kind"] != "transition" or event["seq"] != i:
            raise ValueError("EVENT_SEQUENCE_DRIFT")
        if type(event["action"]) is not int or not 0 <= event["action"] <= 6:
            raise ValueError("INVALID_PUBLIC_ACTION")
        if type(event["reward"]) is not float or not math.isfinite(event["reward"]) or not 0 <= event["reward"] <= 1:
            raise ValueError("INVALID_PUBLIC_REWARD")
        if (event["terminated"] or event["truncated"]) and i != len(events) - 1:
            raise ValueError("EVENT_AFTER_TERMINAL")
    return tuple(events)


def public_receipt_digest(events):
    rows = validate_episode(events)
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()
