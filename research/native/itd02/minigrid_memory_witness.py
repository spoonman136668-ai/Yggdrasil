"""Public-event-only verifier for a preregistered history witness pair.

Consumes already-recorded public episodes only; never imports, instantiates,
resets or steps MiniGrid. A PASS is a receipt-shape result, not source authority.
"""
import hashlib
import json

from .minigrid_memory_event_contract import public_receipt_digest, validate_episode
from .minigrid_memory_witness_rules import FORWARD, expected_branch_action, public_object_at, public_key_ball_cells

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
    public_cue_cell_a,
    public_cue_cell_b,
    public_upper_object_cell,
    public_lower_object_cell,
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

    # Lock this candidate to the preregistered MemoryS7 public-view geometry.
    if tuple(public_cue_cell_a) != (2, 6) or tuple(public_cue_cell_b) != (2, 6):
        raise ValueError("WITNESS_CUE_COORDINATE_NOT_PREREGISTERED")
    if tuple(public_upper_object_cell) != (1, 5):
        raise ValueError("WITNESS_UPPER_COORDINATE_NOT_PREREGISTERED")
    if tuple(public_lower_object_cell) != (5, 5):
        raise ValueError("WITNESS_LOWER_COORDINATE_NOT_PREREGISTERED")

    for label, episode, cue_cell in (
        ("A", a, public_cue_cell_a), ("B", b, public_cue_cell_b)
    ):
        reset_observation = episode[0]["observation"]
        if reset_observation["direction"] != 0:
            raise ValueError("WITNESS_" + label + "_RESET_POSE_MISMATCH")
        visible = public_key_ball_cells(reset_observation)
        if visible != [{
            "coordinate": [cue_cell[0], cue_cell[1]],
            "object": public_object_at(reset_observation, cue_cell),
        }]:
            raise ValueError("WITNESS_" + label + "_RESET_CUE_NOT_UNIQUELY_VISIBLE")

    if decision_a["observation"]["direction"] != 0 or decision_b["observation"]["direction"] != 0:
        raise ValueError("WITNESS_DECISION_POSE_MISMATCH")

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
    # Labels are decoded from public image bytes at preregistered coordinates;
    # callers cannot simply assert that an arbitrary cell contains a key/ball.
    public_start_cue_a = public_object_at(a[0]["observation"], public_cue_cell_a)
    public_start_cue_b = public_object_at(b[0]["observation"], public_cue_cell_b)
    public_upper_end_object_a = public_object_at(
        decision_a["observation"], public_upper_object_cell)
    public_upper_end_object_b = public_object_at(
        decision_b["observation"], public_upper_object_cell)
    public_lower_end_object_a = public_object_at(
        decision_a["observation"], public_lower_object_cell)
    public_lower_end_object_b = public_object_at(
        decision_b["observation"], public_lower_object_cell)
    if public_upper_end_object_a != public_upper_end_object_b:
        raise ValueError("WITNESS_UPPER_OBJECT_CLASS_MISMATCH")
    if public_lower_end_object_a != public_lower_end_object_b:
        raise ValueError("WITNESS_LOWER_OBJECT_CLASS_MISMATCH")
    if public_upper_end_object_a == public_lower_end_object_a:
        raise ValueError("WITNESS_END_OBJECTS_NOT_DISTINCT")
    for label, observation in (("A", decision_a["observation"]), ("B", decision_b["observation"])):
        visible = public_key_ball_cells(observation)
        expected = [
            {"coordinate": [public_upper_object_cell[0], public_upper_object_cell[1]],
             "object": public_object_at(observation, public_upper_object_cell)},
            {"coordinate": [public_lower_object_cell[0], public_lower_object_cell[1]],
             "object": public_object_at(observation, public_lower_object_cell)},
        ]
        if visible != expected:
            raise ValueError("WITNESS_" + label + "_END_OBJECTS_NOT_UNIQUELY_VISIBLE")
    public_upper_end_object = public_upper_end_object_a
    # Facing direction is read from the public decision observation itself,
    # never from an independently supplied label.
    expected_a = expected_branch_action(
        public_start_cue_a,
        public_upper_end_object,
        agent_direction=decision_a["observation"]["direction"],
    )
    expected_b = expected_branch_action(
        public_start_cue_b,
        public_upper_end_object,
        agent_direction=decision_b["observation"]["direction"],
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
        "public_lower_end_object": public_lower_end_object_a,
        "visible_end_object_cells": [[1, 5], [5, 5]],
        "expected_action_a": expected_a,
        "expected_action_b": expected_b,
        "classification_provenance": "KEY_BALL_DECODED_FROM_PUBLIC_IMAGE_BYTES_COORDINATES_SEMANTICS_NOT_ATTESTED",
        "terminal_reward_a": final_a["reward"],
        "terminal_reward_b": final_b["reward"],
        "claim": "PUBLIC_EVENT_WITNESS_SHAPE_PASS_SOURCE_PROVENANCE_NOT_ATTESTED",
    }
