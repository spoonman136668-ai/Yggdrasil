"""Equal-information conventional tabular TD(lambda) comparator (development only).

Consumes only the current public observation, selected legal action, observed reward,
and terminal flag. It does not call or model any environment and has no source oracle.
"""
import hashlib
import json
import math

from .itd02_local_ring_memory_dev import ACTIONS, OBSERVATIONS, _canonical, _finite

SCHEMA = "ygg.itd02.conventional_td_lambda_control_dev.v1"
GAMMA = 0.95
LAMBDA = 0.80
ALPHA = 0.08
TRACE_CAP = 8.0
WEIGHT_CAP = 16.0
MAX_EVENTS = 100000000

def _clip(x, cap):
    return max(-cap, min(cap, x))

class ConventionalTDLambdaControlDev:
    """Tabular observation-action Q(lambda), a conventional fitted comparator.

    Eligibility traces are maintained per observed (observation, action) pair.
    Only the observed action receives immediate credit; prior traces receive
    the same TD error. No unchosen action is assigned an observed outcome.
    """
    def __init__(self):
        self.q = {}
        self.traces = {}
        self.pending = None
        self.events = 0
        self.frozen_digest = None

    @staticmethod
    def _key(observation, action):
        if type(observation) is not str or observation not in OBSERVATIONS:
            raise ValueError("INVALID_PUBLIC_OBSERVATION")
        if type(action) is not str or action not in ACTIONS:
            raise ValueError("INVALID_PUBLIC_ACTION")
        return observation + "|" + action

    def parameter_sha256(self):
        return hashlib.sha256(_canonical({"schema": SCHEMA, "q": self.q})).hexdigest()

    def advance(self, observation):
        if self.pending is not None:
            raise ValueError("PREVIOUS_ACTION_NOT_FINALIZED")
        if self.frozen_digest is not None and self.parameter_sha256() != self.frozen_digest:
            raise ValueError("FROZEN_CONTROL_DRIFT")
        if type(observation) is not str or observation not in OBSERVATIONS:
            raise ValueError("INVALID_PUBLIC_OBSERVATION")
        self.pending = observation

    def q_values(self):
        if self.pending is None:
            raise ValueError("PUBLIC_OBSERVATION_REQUIRED")
        return [self.q.get(self._key(self.pending, action), 0.0) for action in ACTIONS]

    def choose(self):
        values = self.q_values()
        return ACTIONS[max(range(len(ACTIONS)), key=lambda i: values[i])]

    def feedback(self, action, reward, next_observation=None, *, terminal=False, learning=True):
        if self.pending is None:
            raise ValueError("NO_PENDING_PUBLIC_ACTION")
        key = self._key(self.pending, action)
        if not _finite(reward) or abs(reward) > 10000 or type(terminal) is not bool or type(learning) is not bool:
            raise ValueError("INVALID_PUBLIC_REWARD_OR_FLAGS")
        if terminal:
            if next_observation is not None and (type(next_observation) is not str or next_observation not in OBSERVATIONS):
                raise ValueError("INVALID_TERMINAL_OBSERVATION")
        elif type(next_observation) is not str or next_observation not in OBSERVATIONS:
            raise ValueError("NEXT_PUBLIC_OBSERVATION_REQUIRED")
        if self.events >= MAX_EVENTS:
            raise ValueError("CONTROL_EVENT_BUDGET_EXHAUSTED")
        if self.frozen_digest is not None:
            if learning:
                raise ValueError("FITTING_FORBIDDEN_DURING_EVALUATION")
            if self.parameter_sha256() != self.frozen_digest:
                raise ValueError("FROZEN_CONTROL_DRIFT")
        elif not learning:
            raise ValueError("FROZEN_EVALUATION_REQUIRED")

        old_q = dict(self.q)
        old_traces = dict(self.traces)
        old_pending = self.pending
        old_events = self.events
        try:
            if learning:
                # Accumulating eligibility trace for the currently selected pair.
                for k in list(self.traces):
                    self.traces[k] = _clip(self.traces[k] * GAMMA * LAMBDA, TRACE_CAP)
                    if abs(self.traces[k]) < 1e-12:
                        del self.traces[k]
                self.traces[key] = _clip(self.traces.get(key, 0.0) + 1.0, TRACE_CAP)
                old_value = self.q.get(key, 0.0)
                if terminal:
                    target = float(reward)
                else:
                    future = [self.q.get(self._key(next_observation, a), 0.0) for a in ACTIONS]
                    target = float(reward) + GAMMA * max(future)
                delta = _clip(target - old_value, 2.0)
                for traced_key, eligibility in self.traces.items():
                    self.q[traced_key] = _clip(self.q.get(traced_key, 0.0) + ALPHA * delta * eligibility, WEIGHT_CAP)
                self.events += 1
                if terminal:
                    self.traces = {}
            elif terminal:
                self.traces = {}
            self.pending = None
        except Exception:
            self.q = old_q
            self.traces = old_traces
            self.pending = old_pending
            self.events = old_events
            raise

    def reset_episode(self):
        if self.pending is not None:
            raise ValueError("PENDING_ACTION_NOT_FINALIZED")
        self.traces = {}

    def start_frozen_evaluation(self, expected_digest):
        if self.pending is not None:
            raise ValueError("PENDING_TRAINING_EVENT")
        if type(expected_digest) is not str or expected_digest != self.parameter_sha256():
            raise ValueError("FITTED_CONTROL_IDENTITY_MISMATCH")
        self.frozen_digest = expected_digest
        self.traces = {}

    def checkpoint(self):
        body = {"schema": SCHEMA, "q": self.q, "traces": self.traces, "pending": self.pending,
                "events": self.events, "frozen_digest": self.frozen_digest}
        payload = _canonical(body)
        if len(payload) > 16384:
            raise ValueError("CONTROL_CHECKPOINT_OVER_BUDGET")
        return _canonical({"body": body, "sha256": hashlib.sha256(payload).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= 16384:
                raise ValueError("CONTROL_CHECKPOINT_SIZE")
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"body", "sha256"}:
                raise ValueError("CONTROL_CHECKPOINT_ENVELOPE")
            body = envelope["body"]
            if hashlib.sha256(_canonical(body)).hexdigest() != envelope["sha256"]:
                raise ValueError("CONTROL_CHECKPOINT_DIGEST")
            if type(body) is not dict or set(body) != {"schema", "q", "traces", "pending", "events", "frozen_digest"} or body["schema"] != SCHEMA:
                raise ValueError("CONTROL_CHECKPOINT_SCHEMA")
            if type(body["q"]) is not dict or type(body["traces"]) is not dict:
                raise ValueError("CONTROL_CHECKPOINT_MAPS")
            if any(type(k) is not str or not math.isfinite(v) or abs(v) > WEIGHT_CAP for k, v in body["q"].items()):
                raise ValueError("CONTROL_CHECKPOINT_VALUE")
            if any(type(k) is not str or not math.isfinite(v) or abs(v) > TRACE_CAP for k, v in body["traces"].items()):
                raise ValueError("CONTROL_CHECKPOINT_TRACE")
            for key in list(body["q"]) + list(body["traces"]):
                bits = key.split("|")
                if len(bits) != 2 or bits[0] not in OBSERVATIONS or bits[1] not in ACTIONS:
                    raise ValueError("CONTROL_CHECKPOINT_KEY")
            if body["pending"] is not None and (type(body["pending"]) is not str or body["pending"] not in OBSERVATIONS):
                raise ValueError("CONTROL_CHECKPOINT_PENDING")
            if type(body["events"]) is not int or not 0 <= body["events"] <= MAX_EVENTS:
                raise ValueError("CONTROL_CHECKPOINT_COUNTER")
            obj = cls()
            obj.q = {k: float(v) for k, v in body["q"].items()}
            obj.traces = {k: float(v) for k, v in body["traces"].items()}
            obj.pending = body["pending"]
            obj.events = body["events"]
            obj.frozen_digest = body["frozen_digest"]
            if obj.frozen_digest is not None and obj.frozen_digest != obj.parameter_sha256():
                raise ValueError("CONTROL_CHECKPOINT_FROZEN_DRIFT")
            return obj
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            raise ValueError("UNTRUSTED_CONTROL_CHECKPOINT") from exc

