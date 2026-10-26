"""Public-event-only verifier for a preregistered history witness pair.

Consumes already-recorded public episodes only; never imports, instantiates,
resets or steps MiniGrid. A PASS is a receipt-shape result, not source authority.
"""
import hashlib
import json

from .minigrid_memory_event_contract import public_receipt_digest, validate_episode

SCHEMA = "ygg.itd02.minigrid_memory.witness_pair.v1"


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("ascii")


def _observation_digest(observation):
    return hashlib.sha256(_canonical(observation)).hexdigest()


def verify_history_witness_pair(episode_a, episode_b, *, decision_seq_a, decision_seq_b):
    """Verify a preselected decision point in two public episodes.

    `decision_seq_*` identifies the event whose observation is the decision
    observation. The *next event's action* is the action selected at that
    observation. Later public terminal success confirms both recorded paths
    ultimately succeeded; this avoids incorrectly comparing the action on the
    terminal transition (which may be the same forward action in both paths).

    Exact indices must be preregistered before held-out outcomes are opened.
    This validates only event structure; it cannot attest authentic collection
    or independently establish the optimal label from hidden source fields.
    """
    a = validate_episode(episode_a)
    b = validate_episode(episode_b)

    if type(decision_seq_a) is not int or type(decision_seq_b) is not int:
        raise ValueError("WITNESS_DECISION_SEQUENCE_INVALID")
    if not (0 <= decision_seq_a < len(a) - 1):
        raise ValueError("WITNESS_A_DECISION_OUT_OF_RANGE")
    if not (0 <= decision_seq_b < len(b) - 1):
        raise ValueError("WITNESS_B_DECISION_OUT_OF_RANGE")
    decision_a, decision_b = a[decision_seq_a], b[decision_seq_b]
    if decision_a["seq"] != decision_seq_a or decision_b["seq"] != decision_seq_b:
        raise ValueError("WITNESS_DECISION_SEQUENCE_DRIFT")

    final_a, final_b = a[-1], b[-1]
    for label, final in (("A", final_a), ("B", final_b)):
        if not (final["terminated"] and not final["truncated"]):
            raise ValueError("WITNESS_" + label + "_NOT_TERMINAL_SUCCESS")
        if final["reward"] <= 0.0:
            raise ValueError("WITNESS_" + label + "_NO_PUBLIC_SUCCESS_REWARD")

    digest_a = _observation_digest(decision_a["observation"])
    digest_b = _observation_digest(decision_b["observation"])
    if digest_a != digest_b:
        raise ValueError("WITNESS_DECISION_OBSERVATION_MISMATCH")

    # The event after a decision observation carries the action chosen there.
    action_a = a[decision_seq_a + 1]["action"]
    action_b = b[decision_seq_b + 1]["action"]
    if action_a == action_b:
        raise ValueError("WITNESS_DECISION_ACTIONS_NOT_DISTINCT")

    prefix_a = [
        {"observation": e["observation"], "action": e["action"],
         "reward": e["reward"], "terminated": e["terminated"],
         "truncated": e["truncated"]}
        for e in a[:decision_seq_a]
    ]
    prefix_b = [
        {"observation": e["observation"], "action": e["action"],
         "reward": e["reward"], "terminated": e["terminated"],
         "truncated": e["truncated"]}
        for e in b[:decision_seq_b]
    ]
    if _canonical(prefix_a) == _canonical(prefix_b):
        raise ValueError("WITNESS_PRIOR_HISTORIES_IDENTICAL")

    return {
        "schema": SCHEMA,
        "source": a[0]["source"],
        "decision_seq_a": decision_seq_a,
        "decision_seq_b": decision_seq_b,
        "decision_observation_sha256": digest_a,
        "history_a_sha256": hashlib.sha256(_canonical(prefix_a)).hexdigest(),
        "history_b_sha256": hashlib.sha256(_canonical(prefix_b)).hexdigest(),
        "episode_a_sha256": public_receipt_digest(a),
        "episode_b_sha256": public_receipt_digest(b),
        "decision_action_a": action_a,
        "decision_action_b": action_b,
        "terminal_reward_a": final_a["reward"],
        "terminal_reward_b": final_b["reward"],
        "claim": "PUBLIC_EVENT_WITNESS_SHAPE_PASS_SOURCE_PROVENANCE_NOT_ATTESTED",
    }
