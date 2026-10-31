"""MR32 recurrent state-space comparator (development-only baseline).

A compact fixed recurrent feature state with a trained online linear readout.
The recurrence/projection is deterministic and fixed; only the readout learns.
This is a simple reservoir/state-space control, not a capable tuned SOTA RNN.
"""
from __future__ import annotations
import json
import math
from typing import Iterable
from residual_belief import FEATURES, TARGETS, _vector, Prediction


HIDDEN = 16
ACTIONS = 3
LEARNING_RATE = 0.08
DECAY = 0.75


def _tanh(x: float) -> float:
    # Stable scalar tanh; avoid a third-party numerical dependency.
    if x > 10: return 1.0
    if x < -10: return -1.0
    e = math.exp(2.0*x)
    return (e-1.0)/(e+1.0)


class RecurrentStateSpaceControl:
    """Fixed recurrent state + online readout trained from observed outcomes."""
    def __init__(self):
        self.state = [0.0] * HIDDEN
        self.readout = [[0.0] * HIDDEN for _ in range(TARGETS)]
        self.steps = 0
        self.pending = None

    @staticmethod
    def _action_code(action: int) -> tuple[float, float, float]:
        if isinstance(action, bool) or action not in (0, 1, 2):
            raise ValueError("SELECTED_ACTION_OUT_OF_RANGE")
        return tuple(1.0 if i == action else 0.0 for i in range(ACTIONS))

    def _advance(self, features: tuple[float, ...], action: int) -> list[float]:
        onehot = self._action_code(action)
        next_state = []
        for j in range(HIDDEN):
            # Cyclic fixed projection includes all public coordinates and action.
            x = sum(features[(j*5+k*7) % FEATURES] * (1 if (j+k) % 2 else -1)
                    for k in range(4)) * 0.125
            a = onehot[j % ACTIONS] * 0.25
            carry = self.state[j] * DECAY
            cross = self.state[(j+5) % HIDDEN] * 0.125
            next_state.append(_tanh(carry + cross + x + a))
        return next_state

    def predict(self, public_features: Iterable[float], selected_action: int) -> Prediction:
        if self.pending is not None:
            raise RuntimeError("PENDING_OUTCOME_MUST_BE_RESOLVED")
        x = _vector(public_features, FEATURES, "FEATURES")
        self._action_code(selected_action)
        candidate_state = self._advance(x, selected_action)
        values = tuple(max(-1.0, min(1.0, sum(w*h for w, h in zip(row, candidate_state))))
                       for row in self.readout)
        covered = self.steps > 0
        self.pending = (candidate_state, values)
        return Prediction(values, 1.0 if not covered else 0.5, covered)

    def observe_selected_outcome(self, actual_outcome: Iterable[float]) -> None:
        if self.pending is None:
            raise RuntimeError("NO_PENDING_SELECTED_ACTION")
        y = _vector(actual_outcome, TARGETS, "OUTCOME")
        candidate_state, predicted = self.pending
        self.pending = None
        residual = [target - pred for target, pred in zip(y, predicted)]
        for row, error in zip(self.readout, residual):
            for j, h in enumerate(candidate_state):
                row[j] = max(-2.0, min(2.0, row[j] + LEARNING_RATE*error*h))
        self.state = candidate_state
        self.steps += 1

    def snapshot(self) -> bytes:
        if self.pending is not None:
            raise RuntimeError("CANNOT_CHECKPOINT_PENDING_OUTCOME")
        payload = {"schema":"yggdrasil.mr32.recurrent-control.v1",
                   "state":self.state,"readout":self.readout,"steps":self.steps}
        canonical = json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        import hashlib
        return json.dumps({"payload":payload,"sha256":hashlib.sha256(canonical).hexdigest()},
                          sort_keys=True,separators=(",",":"),allow_nan=False).encode()

    @classmethod
    def restore(cls, raw: bytes) -> "RecurrentStateSpaceControl":
        import hashlib
        try:
            envelope=json.loads(raw.decode("utf-8"));payload=envelope["payload"]
            canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        except Exception as exc:
            raise ValueError("CHECKPOINT_FORMAT") from exc
        if hashlib.sha256(canonical).hexdigest()!=envelope.get("sha256"):
            raise ValueError("CHECKPOINT_HASH_MISMATCH")
        if payload.get("schema")!="yggdrasil.mr32.recurrent-control.v1":
            raise ValueError("CHECKPOINT_SCHEMA")
        model=cls()
        state=_vector(payload["state"],HIDDEN,"STATE")
        readout=payload["readout"]
        if not isinstance(readout,list) or len(readout)!=TARGETS:
            raise ValueError("CHECKPOINT_READOUT")
        rows=[]
        for row in readout:
            rows.append(list(_vector(row,HIDDEN,"READOUT")))
        if not isinstance(payload.get("steps"),int) or payload["steps"]<0:
            raise ValueError("CHECKPOINT_STEPS")
        model.state=list(state);model.readout=rows;model.steps=payload["steps"]
        return model

    def state_bytes(self) -> bytes:
        return self.snapshot()
