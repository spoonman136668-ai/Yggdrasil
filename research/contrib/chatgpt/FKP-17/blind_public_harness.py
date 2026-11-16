"""FKP-17 source-agnostic blind action-before-outcome public-episode custody.

No simulator/source, model, or private-law imports. This is a source-safe
TRAIN/VAL harness only. A later held evaluator requires independent ownership.
SHA256 action receipts prove logged order, not evaluator authenticity.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math

ARMS = ("STRUCTURED", "FLAT", "SHUFFLED", "MINIMAL", "NO_UPDATE",
        "BAYES_SYMBOLIC", "COUNT_RETRIEVAL", "RECURRENT")
EXPLORATION_STEPS = 24
SCORING_STEPS = 16
ACTION_COUNT = 8
REGISTERS = 8


def _public_state(value):
    if type(value) is not tuple or len(value) != REGISTERS:
        raise ValueError("FKP17_BLIND_INVALID_PUBLIC_STATE")
    if any(type(v) is not int or not 0 <= v < 16 for v in value):
        raise ValueError("FKP17_BLIND_STATE_RANGE")
    return value


def _commit(kind, arm, trial, tick, before, choice):
    if type(choice) is not int or choice not in range(ACTION_COUNT):
        raise ValueError("FKP17_BLIND_INVALID_ACTION")
    if type(trial) is not int or trial < 0:
        raise ValueError("FKP17_BLIND_INVALID_WORLD_ID")
    fields = [kind, arm, trial, tick, list(before), choice]
    raw = json.dumps(fields, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("ascii")).hexdigest()


def _verify_public(actual, before, choice):
    if tuple(getattr(actual, "_fields", ())) != (
            "before", "action", "after", "reward", "done", "history"):
        raise ValueError("FKP17_BLIND_PUBLIC_SCHEMA_MISMATCH")
    if actual.before != before or actual.action != choice:
        raise ValueError("FKP17_BLIND_CHOICE_OUTCOME_MISMATCH")
    _public_state(actual.after)
    if type(actual.reward) not in (int, float) or (
            not math.isfinite(actual.reward) or abs(actual.reward) > 1):
        raise ValueError("FKP17_BLIND_REWARD_INVALID")
    if type(actual.done) is not bool:
        raise ValueError("FKP17_BLIND_DONE_INVALID")
    if type(actual.history) is not tuple or len(actual.history) > 16:
        raise ValueError("FKP17_BLIND_HISTORY_INVALID")
    if actual.history and actual.history[-1].after != before:
        raise ValueError("FKP17_BLIND_TIME_REVERSAL")
    return actual


def _row_digest(rows):
    public = []
    for row in rows:
        history = [[list(x.before), x.action, float(x.reward), list(x.after), x.done]
                   for x in row.history]
        public.append([list(row.before), row.action, list(row.after),
                       float(row.reward), row.done, history])
    return sha256(json.dumps(public, separators=(",", ":"), allow_nan=False).
                  encode("ascii")).hexdigest()


def evaluate_training_fixture(session_factory, public_actions, policies, trial):
    """Each arm acts on independent fresh TRAIN/VAL episode after common tape.

    session_factory must return a new public-only session per arm; the caller
    independently enforces source cohort. All recorded scores are explicitly
    unqualified source-safe diagnostics, never original held scientific data.
    """
    tape = tuple(public_actions)
    if len(tape) != EXPLORATION_STEPS or any(
            type(a) is not int or a not in range(ACTION_COUNT) for a in tape):
        raise ValueError("FKP17_BLIND_FROZEN_ACTION_TAPE")
    names = tuple(policies)
    if len(names) != len(ARMS) or set(names) != set(ARMS):
        raise ValueError("FKP17_BLIND_MISSING_STRONG_ARM")
    if type(trial) is not int or trial < 0:
        raise ValueError("FKP17_BLIND_INVALID_TRIAL")
    records = {}
    common_exploration_sha = None
    for name in ARMS:
        policy = policies[name]
        policy.begin_world()
        session = session_factory()
        if not hasattr(session, "current_public") or not callable(
                getattr(session, "apply_public", None)):
            raise ValueError("FKP17_BLIND_SESSION_PUBLIC_API_REQUIRED")
        exploration, scored, commits = [], [], []
        for tick, action in enumerate(tape):
            before = _public_state(session.current_public)
            seal = _commit("explore", name, trial, tick, before, action)
            result = _verify_public(session.apply_public(action), before, action)
            policy.observe_public(result)
            commits.append(seal)
            exploration.append(result)
            if result.done:
                raise ValueError("FKP17_BLIND_EARLY_EXPLORATION_TERMINATION")
        fact_digest = _row_digest(exploration)
        if common_exploration_sha is None:
            common_exploration_sha = fact_digest
        if fact_digest != common_exploration_sha:
            raise ValueError("FKP17_BLIND_DIFFERENT_EXPLORATION_DATA")
        for tick in range(SCORING_STEPS):
            before = _public_state(session.current_public)
            action = policy.choose_public(before)
            seal = _commit("scored", name, trial, tick, before, action)
            result = _verify_public(session.apply_public(action), before, action)
            policy.observe_public(result)
            commits.append(seal)
            scored.append(result)
            if result.done:
                break
        records[name] = {
            "selected_actions": [row.action for row in scored],
            "actual_public_reward": sum(float(row.reward) for row in scored),
            "scored_steps": len(scored),
            "termination_events": sum(bool(row.done) for row in scored),
            "shared_exploration_sha256": fact_digest,
            "chosen_outcome_sha256": _row_digest(scored),
            "action_commit_sha256": sha256("".join(commits).encode("ascii")).hexdigest(),
            "parameter_receipt_after": policy.state_receipt(),
        }
    return {
        "schema": "fkp17.public-training-onpolicy-only.v1",
        "trial": trial,
        "public_exploration_actions": list(tape),
        "identical_exploration_sha256": common_exploration_sha,
        "arms": records,
        "original_dev_opened": False,
        "reserved_transfer_opened": False,
        "scientific_pass": False,
        "native_promoted": False,
    }
