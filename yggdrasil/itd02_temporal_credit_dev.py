"""Bounded local eligibility-trace extension for the ITD-02 ring-memory candidate.

Development-only: source-public events are supplied by an authorized owner.
This module is NOT a Shuttle producer, experiment launcher, or science permit.
It composes the existing eight-cell ring memory without editing it or R7.
"""
import hashlib
import json
import math

from .itd02_local_ring_memory_dev import (
    ACTIONS, ACTION_SITES, CELLS, MAX_CHECKPOINT_BYTES,
    NativeRingMemoryDev, _canonical, _finite, _local_exchange,
)

SCHEMA = "ygg.itd02.temporal_credit_ring_dev.v1"
GAMMA = 0.95
LAMBDA = 0.80
TRACE_DECAY = GAMMA * LAMBDA
LEARNING_RATE = 0.08
ERROR_CAP = 2.0
TRACE_CAP = 8.0
MAX_EVENTS = 100000000


def _clip(value, cap):
    return max(-cap, min(cap, value))


def _features_for_action(memory, action):
    if not memory.pending:
        raise ValueError("PUBLIC_OBSERVATION_REQUIRED")
    if type(action) is not str or action not in ACTIONS:
        raise ValueError("INVALID_PUBLIC_ACTION")
    now = _local_exchange(memory._pulse)
    retained = _local_exchange(memory.memory)
    site = ACTION_SITES[ACTIONS.index(action)]
    return (1.0, now[site], 16.0 * retained[site])


class TemporalCreditRingDev:
    """Existing local ring learner plus bounded action-feature eligibility.

    The trace updates only from the reward actually supplied for the chosen
    public action. It propagates credit to earlier selected action features;
    it does not infer unchosen outcomes or read source-law/hidden state.
    """

    def __init__(self, memory=None):
        self.memory = NativeRingMemoryDev() if memory is None else memory
        if type(self.memory) is not NativeRingMemoryDev:
            raise ValueError("REQUIRES_EXISTING_RING_MEMORY")
        self.eligibility = [[0.0, 0.0, 0.0] for _ in ACTIONS]
        self._selected_action = None
        self._selected_features = None
        self.events = 0

    def parameter_sha256(self):
        return hashlib.sha256(_canonical({
            "schema": SCHEMA,
            "memory_parameters": self.memory.parameter_sha256(),
        })).hexdigest()

    def advance(self, observation):
        if self._selected_action is not None:
            raise ValueError("PREVIOUS_ACTION_NOT_FINALIZED")
        self.memory.advance(observation)

    def q_values(self):
        return self.memory.q_values()

    def choose(self):
        if self._selected_action is not None:
            raise ValueError("ACTION_ALREADY_SELECTED")
        action = self.memory.choose()
        self._selected_action = action
        self._selected_features = _features_for_action(self.memory, action)
        return action

    def _next_eligibility(self, action, features):
        out = [[_clip(v * TRACE_DECAY, TRACE_CAP) for v in row]
               for row in self.eligibility]
        idx = ACTIONS.index(action)
        for j, value in enumerate(features):
            out[idx][j] = _clip(out[idx][j] + value, TRACE_CAP)
        return out

    def feedback(self, action, reward, *, learning=True, terminal=False):
        if self._selected_action is None or self._selected_features is None:
            raise ValueError("NO_PENDING_PUBLIC_ACTION")
        if action != self._selected_action:
            raise ValueError("SELECTED_ACTION_MISMATCH")
        if type(action) is not str or action not in ACTIONS:
            raise ValueError("INVALID_PUBLIC_ACTION")
        if not _finite(reward) or abs(reward) > 10000:
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool:
            raise ValueError("INVALID_PUBLIC_FLAGS")
        if self.events >= MAX_EVENTS:
            raise ValueError("TEMPORAL_EVENT_BUDGET_EXHAUSTED")
        if self.memory._frozen_hash is not None:
            if learning:
                raise ValueError("FITTING_FORBIDDEN_DURING_EVALUATION")
            if self.memory.parameter_sha256() != self.memory._frozen_hash:
                raise ValueError("FROZEN_WEIGHTS_CHANGED")
        elif not learning:
            raise ValueError("FROZEN_EVALUATION_REQUIRED")

        # Prepare all child state before allowing the established learner to
        # accept the event. No trace update survives a rejected feedback.
        features = tuple(self._selected_features)
        next_trace = self._next_eligibility(action, features)
        idx = ACTIONS.index(action)
        old_weights = tuple(self.memory.heads[idx])
        predicted = sum(w * x for w, x in zip(old_weights, features))
        delta = _clip(float(reward) - predicted, ERROR_CAP)
        old_memory_snapshot = self.memory.checkpoint()
        old_frozen_hash = self.memory._frozen_hash
        old_traces = self.eligibility
        old_selected = self._selected_action
        old_features = self._selected_features
        old_events = self.events
        try:
            # Preserve existing immediate-reward update and all its fail-closed
            # checks. Temporal credit is additive and only follows accepted
            # selected feedback.
            self.memory.feedback(action, reward, learning=learning,
                                 terminal=terminal)
            if learning:
                for action_index, row in enumerate(next_trace):
                    weights = self.memory.heads[action_index]
                    for j, eligibility in enumerate(row):
                        weights[j] = _clip(
                            weights[j] + LEARNING_RATE * delta * eligibility,
                            16.0,
                        )
                self.events += 1
            self.eligibility = next_trace
            self._selected_action = None
            self._selected_features = None
            if terminal:
                self.eligibility = [[0.0, 0.0, 0.0] for _ in ACTIONS]
        except Exception:
            self.memory = NativeRingMemoryDev.restore(old_memory_snapshot)
            self.memory._frozen_hash = old_frozen_hash
            self.eligibility = old_traces
            self._selected_action = old_selected
            self._selected_features = old_features
            self.events = old_events
            raise

    def reset_episode(self):
        if self._selected_action is not None:
            raise ValueError("PENDING_ACTION_NOT_FINALIZED")
        self.memory.reset_episode()
        self.eligibility = [[0.0, 0.0, 0.0] for _ in ACTIONS]

    def start_frozen_evaluation(self, expected_sha):
        if self._selected_action is not None:
            raise ValueError("PENDING_TRAINING_EVENT")
        if type(expected_sha) is not str or expected_sha != self.parameter_sha256():
            raise ValueError("FITTED_PARAMETER_IDENTITY_MISMATCH")
        self.memory.start_frozen_evaluation(self.memory.parameter_sha256())

    def checkpoint(self):
        body = {
            "schema": SCHEMA,
            "memory": json.loads(self.memory.checkpoint()),
            "eligibility": self.eligibility,
            "selected_action": self._selected_action,
            "selected_features": self._selected_features,
            "events": self.events,
            "frozen_hash": self.memory._frozen_hash,
        }
        payload = _canonical(body)
        if len(payload) > MAX_CHECKPOINT_BYTES * 2:
            raise ValueError("TEMPORAL_CHECKPOINT_OVER_BUDGET")
        return _canonical({
            "body": body,
            "sha256": hashlib.sha256(payload).hexdigest(),
        })

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_CHECKPOINT_BYTES * 2:
                raise ValueError("TEMPORAL_CHECKPOINT_SIZE")
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"body", "sha256"}:
                raise ValueError("TEMPORAL_CHECKPOINT_ENVELOPE")
            body = envelope["body"]
            if hashlib.sha256(_canonical(body)).hexdigest() != envelope["sha256"]:
                raise ValueError("TEMPORAL_CHECKPOINT_DIGEST")
            expected = {
                "schema", "memory", "eligibility", "selected_action",
                "selected_features", "events", "frozen_hash",
            }
            if type(body) is not dict or set(body) != expected or body["schema"] != SCHEMA:
                raise ValueError("TEMPORAL_CHECKPOINT_SCHEMA")
            trace = body["eligibility"]
            if type(trace) is not list or len(trace) != len(ACTIONS):
                raise ValueError("TEMPORAL_CHECKPOINT_TRACE_SHAPE")
            for row in trace:
                if type(row) is not list or len(row) != 3 or any(
                    not _finite(x) or abs(x) > TRACE_CAP for x in row
                ):
                    raise ValueError("TEMPORAL_CHECKPOINT_TRACE_VALUE")
            selected = body["selected_action"]
            features = body["selected_features"]
            if selected is None:
                if features is not None:
                    raise ValueError("TEMPORAL_CHECKPOINT_PENDING_MISMATCH")
            elif (type(selected) is not str or selected not in ACTIONS
                  or type(features) is not list or len(features) != 3
                  or any(not _finite(x) or abs(x) > 16 for x in features)):
                raise ValueError("TEMPORAL_CHECKPOINT_PENDING_MISMATCH")
            events = body["events"]
            if type(events) is not int or not 0 <= events <= MAX_EVENTS:
                raise ValueError("TEMPORAL_CHECKPOINT_COUNTER")
            frozen = body["frozen_hash"]
            if frozen is not None and (
                type(frozen) is not str or len(frozen) != 64
            ):
                raise ValueError("TEMPORAL_CHECKPOINT_FROZEN_HASH")
            memory = NativeRingMemoryDev.restore(_canonical(body["memory"]))
            if frozen is not None:
                if memory.parameter_sha256() != frozen:
                    raise ValueError("TEMPORAL_CHECKPOINT_FROZEN_DRIFT")
                memory._frozen_hash = frozen
            obj = cls(memory)
            obj.eligibility = [[float(v) for v in row] for row in trace]
            obj._selected_action = selected
            obj._selected_features = (
                None if features is None else tuple(float(v) for v in features)
            )
            obj.events = events
            return obj
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            raise ValueError("UNTRUSTED_TEMPORAL_CHECKPOINT") from exc
