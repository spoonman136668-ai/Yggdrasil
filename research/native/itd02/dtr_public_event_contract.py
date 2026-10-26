"""Pinned public-event contract for source-original Causal-Gymnasium DTR.

Pure validator only: it does not import or run the upstream environment. It
never provides info dictionaries, PCH/env objects, SCM, graph or hidden fields
to a learner. A separately qualified worker is required; this module does not
authenticate that worker and grants no first-use permission.
"""
import hashlib
import json

SCHEMA = "ygg.itd02.causal_gym_dtr.public_event.v1"
SOURCE = {
    "repository": "CausalAILab/Causal-Gymnasium",
    "commit": "c94e9a4cd3641588b6b8507e71ccee5c27032bdf",
    "dtr_git_blob": "6af2371dce21804140ea141ccb7be14e003ba275",
    "pch_git_blob": "ff37780c6b791877c70583b8d5f699be7fcd8817",
    "claim": "PINNED_SOURCE_IDENTITY_NOT_EXECUTION_ATTESTATION",
}
MAX_SEED = (1 << 32) - 1
PUBLIC_KEYS = frozenset({
    "schema", "source", "episode_seed", "seq", "stage_before",
    "stage_after", "action", "observation", "reward", "terminated",
    "truncated",
})


def _integer(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("INVALID_" + name.upper())
    return value


def _binary(value, name, allow_none=False):
    if allow_none and value is None:
        return None
    if type(value) is not int or value not in (0, 1):
        raise ValueError("INVALID_" + name.upper())
    return value


def _reward(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("INVALID_PUBLIC_REWARD")
    return value


def source_identity(receipt):
    """Check the static pin; this is not a signed source receipt."""
    if type(receipt) is not dict or receipt != SOURCE:
        raise ValueError("SOURCE_PIN_MISMATCH")
    return dict(SOURCE)


def _event(seed, seq, before, after, action, observation, reward,
           terminated, truncated, receipt):
    _integer(seed, 0, MAX_SEED, "episode_seed")
    _integer(seq, 0, 2, "sequence")
    if before is not None:
        _integer(before, 0, 1, "stage_before")
    _integer(after, 0, 2, "stage_after")
    if action is not None:
        _binary(action, "action")
    _binary(observation, "observation", allow_none=True)
    _reward(reward)
    if type(terminated) is not bool or type(truncated) is not bool:
        raise ValueError("INVALID_TERMINATION_FLAGS")
    event = {
        "schema": SCHEMA,
        "source": source_identity(receipt),
        "episode_seed": seed,
        "seq": seq,
        "stage_before": before,
        "stage_after": after,
        "action": action,
        "observation": observation,
        "reward": reward,
        "terminated": terminated,
        "truncated": truncated,
    }
    if set(event) != PUBLIC_KEYS:
        raise ValueError("PUBLIC_EVENT_SCHEMA_DRIFT")
    return event


def project_reset(result, *, episode_seed, source_receipt):
    """Read reset observation only; never inspect or retain reset info."""
    if type(result) is not tuple or len(result) != 2:
        raise ValueError("INVALID_UPSTREAM_RESET_SHAPE")
    observation = _binary(result[0], "initial_observation")
    # result[1] is intentionally not inspected, copied, or serialized.
    return _event(episode_seed, 0, None, 0, None, observation, 0,
                  False, False, source_receipt)


def project_step(result, *, episode_seed, seq, stage_before, action,
                 source_receipt):
    """Project Gymnasium's five-tuple without reading its info dictionary."""
    _integer(episode_seed, 0, MAX_SEED, "episode_seed")
    _integer(seq, 1, 2, "sequence")
    _integer(stage_before, 0, 1, "stage_before")
    _binary(action, "action")
    if type(result) is not tuple or len(result) != 5:
        raise ValueError("INVALID_UPSTREAM_STEP_SHAPE")
    observation, reward, terminated, truncated, _info = result
    # _info is deliberately not traversed or copied.
    reward = _reward(reward)
    if type(terminated) is not bool or type(truncated) is not bool:
        raise ValueError("INVALID_TERMINATION_FLAGS")
    if truncated:
        raise ValueError("UNEXPECTED_SOURCE_TRUNCATION")
    if stage_before == 0:
        if terminated or reward != 0:
            raise ValueError("INVALID_FIRST_STAGE_OUTCOME")
        observation = _binary(observation, "stage_two_observation")
        stage_after = 1
    else:
        if not terminated or observation is not None:
            raise ValueError("INVALID_TERMINAL_STAGE_OUTCOME")
        stage_after = 2
    return _event(episode_seed, seq, stage_before, stage_after, action,
                  observation, reward, terminated, truncated, source_receipt)


def validate_episode(events):
    """Validate a complete two-decision chain; do not transform the events."""
    if type(events) not in (list, tuple) or len(events) != 3:
        raise ValueError("DTR_EPISODE_MUST_HAVE_THREE_EVENTS")
    rows = tuple(events)
    if any(type(row) is not dict or set(row) != PUBLIC_KEYS for row in rows):
        raise ValueError("NONPUBLIC_EVENT_FIELDS")
    if any(row.get("schema") != SCHEMA or row.get("source") != SOURCE for row in rows):
        raise ValueError("EVENT_SOURCE_DRIFT")
    if len({row.get("episode_seed") for row in rows}) != 1:
        raise ValueError("EPISODE_SEED_DRIFT")
    expected = [
        (0, None, 0, False, False),
        (1, 0, 1, False, False),
        (2, 1, 2, True, False),
    ]
    for i, (row, signature) in enumerate(zip(rows, expected)):
        seq, before, after, terminated, truncated = signature
        if (row["seq"], row["stage_before"], row["stage_after"],
                row["terminated"], row["truncated"]) != signature:
            raise ValueError("DTR_EPISODE_STAGE_OR_SEQUENCE_INVALID")
        if i == 0 and (row["action"] is not None or row["reward"] != 0
                       or row["observation"] not in (0, 1)):
            raise ValueError("DTR_RESET_EVENT_INVALID")
        if i == 1 and (row["action"] not in (0, 1) or row["reward"] != 0
                       or row["observation"] not in (0, 1)):
            raise ValueError("DTR_FIRST_DECISION_EVENT_INVALID")
        if i == 2 and (row["action"] not in (0, 1)
                       or row["observation"] is not None
                       or row["reward"] not in (0, 1)):
            raise ValueError("DTR_TERMINAL_EVENT_INVALID")
    return rows


def public_receipt_digest(events):
    """Hash only validated public fields, never raw source info."""
    rows = validate_episode(events)
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()
