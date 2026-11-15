"""ST2 fixed-budget controls, fixed before all original held outcomes.

No semantic object IDs, rewards, privileged source fields or neural tokens.
The conventional recurrent uses exactly 45 trained coefficients and eight
episodic states; local features use each cell's three public bytes, delta,
announced action and recurrence, not a private evaluator feature.
"""
import json
import math

from research.mr18.native_public_learning import validate, scale
from research.nci04_st2.event_memory import (
    EventGroundedMemory45, correspondences, ACTIONS, N, MAX_COUNT, canonical
)
from research.nci04_s1.local_messages import LocalPredictiveMessages45
from yggdrasil.developmental import sig, valid

SHUFFLE_OFFSET = 3  # Fixed before any source outcome, never selected on DEV.
RECURRENT_SCHEMA = "yggdrasil.nci04.st2.conventional-recurrent-delta45.v1"


def brier(probs, targets):
    valid(targets)
    if (type(probs) not in (tuple, list) or len(probs) != N or
        any(type(p) not in (int, float) or not math.isfinite(p) or
            not 0 <= p <= 1 for p in probs)):
        raise ValueError("ST2_BRIER_INVALID_PROBABILITY")
    return sum((p - y) ** 2 for p, y in zip(probs, targets)) / N


def assert_public_outcome(raw, action, target, next_raw):
    validate(raw, (0,) * N, action)
    validate(next_raw, (0,) * N, action)
    valid(target)
    if action >= ACTIONS or list(target) != [
        int(tuple(raw[3*i:3*i+3]) != tuple(next_raw[3*i:3*i+3]))
        for i in range(N)
    ]:
        raise ValueError("ST2_CONTROL_PUBLIC_OUTCOME_MISMATCH")


def update_pair(pair, event):
    if max(pair) == MAX_COUNT:
        pair[0] //= 2
        pair[1] //= 2
    pair[0 if event else 1] += 1


def estimate(base, pair):
    changed, unchanged = pair
    return (0.5 * base + 0.5 * (1 + changed) /
            (2 + changed + unchanged)) if sum(pair) >= 4 else base


class FixedCameraCount45:
    """Same eight x six x two uint16 locations as candidate; no identity."""

    def __init__(self, snapshot):
        self.native = LocalPredictiveMessages45.restore(snapshot)
        self.counts = [[[0, 0] for _ in range(ACTIONS)] for _ in range(N)]
        self.previous_raw = None

    def predict(self, raw, bits, action):
        validate(raw, bits, action)
        if action >= ACTIONS:
            raise ValueError("ST2_CONTROL_ACTION_OUT_OF_RANGE")
        base = self.native.predict(raw, bits, action)
        # Same source-observation opportunity mask as the candidate. Fixed
        # *location*, not appearance identity, indexes each retained count.
        return [
            estimate(base[i], self.counts[i][action])
            if match is not None else base[i]
            for i, match in enumerate(correspondences(self.previous_raw, raw))
        ]

    def observe(self, raw, bits, action, target, next_raw, train=True):
        assert_public_outcome(raw, action, target, next_raw)
        if type(train) is not bool:
            raise ValueError("ST2_CONTROL_MODE_INVALID")
        pred = self.predict(raw, bits, action)
        mask = correspondences(self.previous_raw, raw)
        self.native.observe(raw, bits, action, target, train=False)
        if train:
            for i, m in enumerate(mask):
                if m is not None:
                    update_pair(self.counts[i][action], target[i])
        self.previous_raw = list(raw)
        return pred

    def reset_episode(self):
        self.native.reset_episode()
        self.previous_raw = None

    def snapshot(self):
        return canonical({
            "schema": "yggdrasil.nci04.st2.fixed-camera.v1",
            "native": json.loads(self.native.snapshot()),
            "counts": self.counts, "previous_raw": self.previous_raw
        })

    def accounting(self):
        return {"counter_uint16_bytes": 192,
                "reserved_signature_bytes_for_equal_budget": 24,
                "checkpoint_bytes": len(self.snapshot().encode("utf-8"))}


def shuffled_prediction(model, raw, bits, action):
    """Same data, count memory and update cost; read fixed-offset track.

    The fixed permutation was selected without reference to results. It is a
    deliberately broken association readout, not a random independent learner.
    """
    if type(model) is not EventGroundedMemory45:
        raise ValueError("ST2_SHUFFLE_NOT_EXACT_CANDIDATE")
    validate(raw, bits, action)
    if action >= ACTIONS:
        raise ValueError("ST2_SHUFFLE_ACTION")
    base = model.native.predict(raw, bits, action)
    for i, match in enumerate(correspondences(model.previous_raw, raw)):
        if match is None:
            continue
        slot = model._slot(match[0])
        if slot is not None:
            base[i] = estimate(
                base[i], model.counts[(slot + SHUFFLE_OFFSET) % N][action]
            )
    return base


class RecurrentDelta45:
    """Trained conventional 45-coefficient local recurrent, fixed data budget."""

    def __init__(self):
        self.local = [[0.0] * 5 for _ in range(N)]
        self.shared = [0.0] * 5
        self.state = [0.0] * N

    def features(self, raw, bits, action, i):
        validate(raw, bits, action)
        if action >= ACTIONS or not 0 <= i < N:
            raise ValueError("ST2_CONVENTIONAL_BAD_FEATURE")
        k = i * 3
        appearance = sum(scale(raw[k+j]) for j in range(3)) / 3
        return (1.0, appearance, float(2 * bits[i] - 1),
                (action - 3.0) / 3.0, self.state[i])

    def predict(self, raw, bits, action):
        return [
            sig(sum((self.local[i][j] + self.shared[j]) * v
                    for j, v in enumerate(self.features(raw, bits, action, i))))
            for i in range(N)
        ]

    def advance_history(self, raw, bits, action):
        for i in range(N):
            k = i * 3
            appearance = sum(scale(raw[k+j]) for j in range(3)) / 3
            self.state[i] = 0.7 * self.state[i] + 0.3 * appearance

    def observe(self, raw, bits, action, targets, train):
        valid(targets)
        if type(train) is not bool:
            raise ValueError("ST2_CONVENTIONAL_MODE")
        before = self.predict(raw, bits, action)
        if train:
            for i, y in enumerate(targets):
                f = self.features(raw, bits, action, i)
                error = y - before[i]
                for j, v in enumerate(f):
                    self.local[i][j] = max(-15.0, min(
                        15.0, self.local[i][j] + 0.035 * error * v
                    ))
                    self.shared[j] = max(-15.0, min(
                        15.0, self.shared[j] + 0.035 * error * v / N
                    ))
        self.advance_history(raw, bits, action)
        return before

    def reset_episode(self):
        self.state = [0.0] * N

    def weights_snapshot(self):
        return canonical({"local": self.local, "shared": self.shared})

    def snapshot(self):
        return canonical({
            "schema": RECURRENT_SCHEMA, "local": self.local,
            "shared": self.shared, "state": self.state
        })

    @classmethod
    def restore(cls, payload):
        if type(payload) is not str or len(payload) > 16384:
            raise ValueError("ST2_CONVENTIONAL_BAD_SNAPSHOT_SIZE")
        try:
            d = json.loads(payload)
            if (type(d) is not dict or set(d) != {
                    "schema", "local", "shared", "state"
                } or d["schema"] != RECURRENT_SCHEMA or
                type(d["local"]) is not list or len(d["local"]) != N or
                any(type(r) is not list or len(r) != 5
                    for r in d["local"]) or
                type(d["shared"]) is not list or len(d["shared"]) != 5 or
                type(d["state"]) is not list or len(d["state"]) != N or
                any(type(v) not in (int, float) or
                    not math.isfinite(v) or abs(v) > 20
                    for row in d["local"] for v in row) or
                any(type(v) not in (int, float) or
                    not math.isfinite(v) or abs(v) > 20
                    for v in d["shared"] + d["state"])):
                raise ValueError("ST2_CONVENTIONAL_BAD_SNAPSHOT_SHAPE")
            m = cls()
            m.local = d["local"]
            m.shared = d["shared"]
            m.state = d["state"]
            if m.snapshot() != payload:
                raise ValueError("ST2_CONVENTIONAL_NONCANONICAL_SNAPSHOT")
            return m
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError("ST2_CONVENTIONAL_RESTORE_FAILED") from exc
