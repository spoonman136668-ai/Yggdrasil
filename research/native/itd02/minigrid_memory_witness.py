"""Public-event-only verifier for a preregistered history witness pair.

Consumes already-recorded public episodes only; never imports, instantiates,
resets or steps MiniGrid. A PASS is a receipt-shape result, not source authority.
"""
import hashlib
import json

from .minigrid_memory_event_contract import public_receipt_digest, validate_episode
from .minigrid_memory_witness_rules import FORWARD, expected_branch_action

SCHEMA = "ygg.itd02.minigrid_memory.witness_pair.v1"


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("ascii")


def _observation_digest(observation):
    return hashlib.sha256(_canonical(observation)).hexdigest()


def verify_history_witness_pair(
    episode_a,
    episode_b,
    *,
    decision_seq_a,
    decision_seq_b,
    public_start_cue_a,
    public_start_cue_b,
    public_upper_end_object,
    agent_direction_a,
    agent_direction_b,
):
    """Verify a preregistered decision point in two public episodes.

    decision_seq_* identifies the event whose observation is the decision
    observation. The next event's action is the action selected there. Later
    terminal success confirms that each recorded path ultimately succeeded.
    The exact decision indices must be frozen before held-out outcomes open.

    This validates receipt structure and supplied public-object classifications.
    It cannot attest authentic collection or independently prove that the
    classifications were extracted from public pixels.
    """
    a = validate_episode(episode_a)
    b = validate_episode(episode_b)

    if type(decision_seq_a) is not int or type(decision_seq_b) is not int:
        raise ValueError("WITNESS_DECISION_SEQUENCE_INVALID")
    if not (0 <= decision_seq_a < len(a) - 2):
        raise ValueError("WITNESS_A_DECISION_OUT_OF_RANGE")
    if not (0 <= decision_seq_b < len(b) - 2):
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

    action_a = a[decision_seq_a + 1]["action"]
    action_b = b[decision_seq_b + 1]["action"]
    expected_a = expected_branch_action(
        public_start_cue_a,
        public_upper_end_object,
        agent_direction=agent_direction_a,
    )
    expected_b = expected_branch_action(
        public_start_cue_b,
        public_upper_end_object,
        agent_direction=agent_direction_b,
    )
    if action_a != expected_a:
        raise ValueError("WITNESS_A_ACTION_DOES_NOT_MATCH_PUBLIC_SOURCE_RULE")
    if action_b != expected_b:
        raise ValueError("WITNESS_B_ACTION_DOES_NOT_MATCH_PUBLIC_SOURCE_RULE")
    if a[decision_seq_a + 2]["action"] != FORWARD:
        raise ValueError("WITNESS_A_DID_NOT_CONTINUE_FORWARD")
    if b[decision_seq_b + 2]["action"] != FORWARD:
        raise ValueError("WITNESS_B_DID_NOT_CONTINUE_FORWARD")
    if action_a == action_b:
        raise ValueError("WITNESS_DECISION_ACTIONS_NOT_DISTINCT")



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
        "public_start_cue_a": public_start_cue_a,
        "public_start_cue_b": public_start_cue_b,
        "public_upper_end_object": public_upper_end_object,
        "expected_action_a": expected_a,
        "expected_action_b": expected_b,
        "classification_provenance": "CLAIMED_PUBLIC_IMAGE_CLASSIFICATIONS_NOT_INDEPENDENTLY_ATTESTED",
        "terminal_reward_a": final_a["reward"],
        "terminal_reward_b": final_b["reward"],
        "claim": "PUBLIC_EVENT_WITNESS_SHAPE_PASS_SOURCE_PROVENANCE_NOT_ATTESTED",
    }
