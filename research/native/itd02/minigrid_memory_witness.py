"""Public-event-only verifier for same-observation/different-history witnesses.

Consumes already-recorded public episodes. It never imports, instantiates,
resets, or steps MiniGrid and never reads hidden environment state.
A PASS validates the recorded witness shape, not scientific source admission.
"""
import hashlib
import json

from .minigrid_memory_event_contract import (
    public_receipt_digest,
    validate_episode,
)

SCHEMA = "ygg.itd02.minigrid_memory.witness_pair.v1"


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("ascii")


def _observation_digest(observation):
    return hashlib.sha256(_canonical(observation)).hexdigest()


def verify_history_witness_pair(episode_a, episode_b):
    """Verify two public episodes sharing a decision observation but differing
    in prior history and successful final action.

    The decision observation is the observation immediately before the final
    transition. Both final transitions must be terminal successes under the
    public reward record, but the selected actions must differ. This is a
    necessary recorded-event witness shape, not proof that the pair came from
    authentic source episodes or that no hidden data contaminated collection.
    """
    a = validate_episode(episode_a)
    b = validate_episode(episode_b)
    final_a, final_b = a[-1], b[-1]
    decision_a, decision_b = a[-2], b[-2]

    if not (final_a["terminated"] and not final_a["truncated"]):
        raise ValueError("WITNESS_A_NOT_TERMINAL_SUCCESS")
    if not (final_b["terminated"] and not final_b["truncated"]):
        raise ValueError("WITNESS_B_NOT_TERMINAL_SUCCESS")
    if final_a["reward"] <= 0.0:
        raise ValueError("WITNESS_A_NO_PUBLIC_SUCCESS_REWARD")
    if final_b["reward"] <= 0.0:
        raise ValueError("WITNESS_B_NO_PUBLIC_SUCCESS_REWARD")

    decision_digest_a = _observation_digest(decision_a["observation"])
    decision_digest_b = _observation_digest(decision_b["observation"])
    if decision_digest_a != decision_digest_b:
        raise ValueError("WITNESS_DECISION_OBSERVATION_MISMATCH")

    # Compare histories strictly before the shared decision observation; the
    # common observation itself is not allowed to make the histories differ.
    prefix_a = [
        {"observation": e["observation"], "action": e["action"],
         "reward": e["reward"], "terminated": e["terminated"],
         "truncated": e["truncated"]}
        for e in a[:-2]
    ]
    prefix_b = [
        {"observation": e["observation"], "action": e["action"],
         "reward": e["reward"], "terminated": e["terminated"],
         "truncated": e["truncated"]}
        for e in b[:-2]
    ]
    if _canonical(prefix_a) == _canonical(prefix_b):
        raise ValueError("WITNESS_PRIOR_HISTORIES_IDENTICAL")
    if final_a["action"] == final_b["action"]:
        raise ValueError("WITNESS_SUCCESS_ACTIONS_NOT_DISTINCT")

    return {
        "schema": SCHEMA,
        "source": a[0]["source"],
        "decision_observation_sha256": decision_digest_a,
        "history_a_sha256": hashlib.sha256(_canonical(prefix_a)).hexdigest(),
        "history_b_sha256": hashlib.sha256(_canonical(prefix_b)).hexdigest(),
        "episode_a_sha256": public_receipt_digest(a),
        "episode_b_sha256": public_receipt_digest(b),
        "successful_action_a": final_a["action"],
        "successful_action_b": final_b["action"],
        "claim": "PUBLIC_EVENT_WITNESS_SHAPE_PASS_SOURCE_PROVENANCE_NOT_ATTESTED",
    }
