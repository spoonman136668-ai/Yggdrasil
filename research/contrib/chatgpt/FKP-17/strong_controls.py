"""Independent public-only symbolic Bayesian and count/retrieval FKP-17 controls.

No imports from candidate numeric relation memory or evaluator/source_fixture.
All training data are real *public* action consequences supplied by caller,
never future action returns or hidden private laws. These are research controls,
not accepted Yggdrasil native architecture or a claim of scientific superiority.
"""
from __future__ import annotations

from array import array
from hashlib import sha256
import json
import math
import struct

FOUNDATION_RECORDS = 32768
MAX_WORLD_RECORDS = 256
ACTIONS = 8
REGISTERS = 8
VALUES = 16
MAX_MEMORY = 1048576
FIELDS = ("before", "action", "after", "reward", "done", "history")
HISTORY_FIELDS = ("before", "action", "reward", "after", "done")
CELL_COUNT = ACTIONS * REGISTERS * VALUES * VALUES
EXEMPLAR_BYTES = 18
# Fixed prior concentration; no dynamic/held score based hyperparameter tuning.
DIRICHLET_ALPHA = 1.0 / VALUES
K_NEIGHBORS = 5


def _state(state):
    if type(state) not in (tuple, list) or len(state) != REGISTERS:
        raise ValueError("FKP17_STRONG_PUBLIC_STATE")
    if any(type(v) is not int or not 0 <= v < VALUES for v in state):
        raise ValueError("FKP17_STRONG_STATE_VALUE")
    return tuple(state)


def _row(record):
    if tuple(getattr(record, "_fields", ())) != FIELDS:
        raise ValueError("FKP17_STRONG_REQUIRES_PUBLIC_RECORD_ONLY")
    before, action, after, reward, done, history = record
    before, after = _state(before), _state(after)
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("FKP17_STRONG_ACTION_INVALID")
    if type(reward) not in (int, float) or not math.isfinite(reward) or not -1 <= reward <= 1:
        raise ValueError("FKP17_STRONG_REWARD_INVALID")
    if type(done) is not bool or type(history) is not tuple or len(history) > 16:
        raise ValueError("FKP17_STRONG_HISTORY_INVALID")
    past = []
    for old in history:
        if tuple(getattr(old, "_fields", ())) != HISTORY_FIELDS:
            raise ValueError("FKP17_STRONG_HISTORY_PRIVATE")
        b, a, r, after_old, d = old
        b, after_old = _state(b), _state(after_old)
        if type(a) is not int or not 0 <= a < ACTIONS or type(d) is not bool:
            raise ValueError("FKP17_STRONG_HISTORY_ACTION_INVALID")
        if type(r) not in (int, float) or not math.isfinite(r) or not -1 <= r <= 1:
            raise ValueError("FKP17_STRONG_HISTORY_REWARD_INVALID")
        past.append([list(b), a, float(r), list(after_old), d])
    return (before, action, after, float(reward), done, past)


def _receipt_bytes(checked):
    before, action, after, reward, done, history = checked
    raw = json.dumps([list(before), action, list(after), reward, done, history],
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    return len(raw).to_bytes(4, "little") + raw


def _index(action, register, before, delta):
    return (((action * REGISTERS + register) * VALUES + before) * VALUES + delta)


class _IndependentPublicLearner:
    """Common custody, deliberately separate from candidate class hierarchy."""
    def __init__(self):
        self._digest = sha256()
        self.foundation_count = 0
        self.world_count = 0
        self._sealed = False

    @property
    def foundation_sha256(self):
        return self._digest.hexdigest()

    def fit_public_foundation(self, records):
        if self._sealed or self.foundation_count:
            raise ValueError("FKP17_STRONG_ALREADY_FIT")
        for record in records:
            if self.foundation_count >= FOUNDATION_RECORDS:
                raise ValueError("FKP17_STRONG_FOUNDATION_OVERBUDGET")
            checked = _row(record)
            self._fit_observation(checked, foundation=True)
            self._digest.update(_receipt_bytes(checked))
            self.foundation_count += 1
        if self.foundation_count != FOUNDATION_RECORDS:
            raise ValueError("FKP17_STRONG_FOUNDATION_INCOMPLETE")
        self._sealed = True
        if self.memory_bytes > MAX_MEMORY:
            raise ValueError("FKP17_STRONG_OVER_CAPACITY")
        return self

    def begin_world(self):
        if not self._sealed:
            raise ValueError("FKP17_STRONG_PRIOR_NOT_SEALED")
        self._clear_world()
        self.world_count = 0

    def observe_public(self, record):
        if not self._sealed or self.world_count >= MAX_WORLD_RECORDS:
            raise ValueError("FKP17_STRONG_WORLD_NOT_READY_OR_OVERBUDGET")
        checked = _row(record)
        self._fit_observation(checked, foundation=False)
        self.world_count += 1
        if self.memory_bytes > MAX_MEMORY:
            raise ValueError("FKP17_STRONG_WORLD_EXCEEDED_CAPACITY")


class SymbolicBayes(_IndependentPublicLearner):
    """Independent factored Dirichlet model of public action effects.

    Unlike the native candidate's direct action→delta numeric bank, this
    model conditions every observed target delta on that register's current
    value. Every action has all 8×16×16 categorical hypotheses, with
    calibrated pseudocounts and local evidence updating Dirichlet posteriors.
    No trainer is given a generator-law or a target held family template.
    """
    def __init__(self):
        super().__init__()
        self._prior = array("H", [0]) * CELL_COUNT
        self._online = array("H", [0]) * CELL_COUNT

    @property
    def memory_bytes(self):
        return 2 * len(self._prior) * self._prior.itemsize

    def _clear_world(self):
        self._online = array("H", [0]) * CELL_COUNT

    def _fit_observation(self, row, *, foundation):
        before, action, after, *_ = row
        counts = self._prior if foundation else self._online
        ids = [_index(action, reg, before[reg], (after[reg] - before[reg]) % VALUES)
               for reg in range(REGISTERS)]
        if any(counts[idx] == 65535 for idx in ids):
            raise OverflowError("FKP17_STRONG_BAYES_COUNTER_OVERFLOW")
        for idx in ids:
            counts[idx] += 1

    def choose_public(self, state):
        state = _state(state)
        best, best_score = 0, float("-inf")
        old_cost = sum(abs(x - 8) for x in state)
        for action in range(ACTIONS):
            expected = 0.0
            for reg, value in enumerate(state):
                first = _index(action, reg, value, 0)
                prior = self._prior[first:first + VALUES]
                online = self._online[first:first + VALUES]
                # One total pseudocount worth of cross-world prior, calibrated
                # by the public support count, versus each actual world action.
                n = sum(prior)
                numerator = 0.0
                denominator = 0.0
                for delta in range(VALUES):
                    p = (prior[delta] / n if n else 0.0)
                    weight = DIRICHLET_ALPHA + p + online[delta]
                    numerator += weight * abs(((value + delta) % VALUES) - 8)
                    denominator += weight
                expected += numerator / denominator
            score = (old_cost - expected) / REGISTERS
            if score > best_score:
                best, best_score = action, score
        return best

    def state_receipt(self):
        h = sha256()
        h.update(b"FKP17-SYMBOLIC-BAYES-V1")
        h.update(self._digest.digest())
        h.update(self._prior.tobytes())
        h.update(self._online.tobytes())
        h.update(struct.pack("<II?", self.foundation_count, self.world_count,
                             self._sealed))
        return h.hexdigest()


class CountRetrieval(_IndependentPublicLearner):
    """Exact public exemplar nearest-action retrieval, no candidate code reuse.

    Each public fact is packed as 8 before values, 8 after values and a
    signed int16 source-earned reward. The action is the owning bucket.
    Thus all 32,768 original facts fit in < 1 MiB *as packed parameter bytes*.
    No privileged alternate action outcomes are ever stored.
    """
    def __init__(self, neighbors=K_NEIGHBORS):
        super().__init__()
        if type(neighbors) is not int or not 1 <= neighbors <= 15:
            raise ValueError("FKP17_STRONG_K_FIXED_RANGE")
        self.neighbors = neighbors
        self._prior = [bytearray() for _ in range(ACTIONS)]
        self._online = [bytearray() for _ in range(ACTIONS)]

    @property
    def memory_bytes(self):
        return sum(len(b) for b in (*self._prior, *self._online))

    def _clear_world(self):
        self._online = [bytearray() for _ in range(ACTIONS)]

    def _fit_observation(self, row, *, foundation):
        before, action, after, reward, *_ = row
        encoded = bytes(before) + bytes(after) + struct.pack("<h", int(round(reward * 32767)))
        bucket = (self._prior if foundation else self._online)[action]
        if self.memory_bytes + EXEMPLAR_BYTES > MAX_MEMORY:
            raise ValueError("FKP17_STRONG_EXEMPLAR_CAPACITY")
        bucket.extend(encoded)

    def choose_public(self, state):
        state = _state(state)
        before_cost = sum(abs(v - 8) for v in state)
        best, score_best = 0, float("-inf")
        # Deterministic K nearest actual public before-states per action.
        for action in range(ACTIONS):
            nearest = []
            for buf in (self._online[action], self._prior[action]):
                for start in range(0, len(buf), EXEMPLAR_BYTES):
                    old = buf[start:start + REGISTERS]
                    distance = sum(abs(state[i] - old[i]) for i in range(REGISTERS))
                    # The exemplar's effect delta is applied to the requested
                    # state, not treated as a privileged future transition.
                    after = buf[start + REGISTERS:start + 2 * REGISTERS]
                    future_cost = sum(abs(((state[i] + after[i] - old[i]) % VALUES) - 8)
                                      for i in range(REGISTERS))
                    score = (before_cost - future_cost) / REGISTERS
                    if len(nearest) < self.neighbors:
                        nearest.append((distance, score))
                        nearest.sort(key=lambda x: x[0])
                    elif distance < nearest[-1][0]:
                        nearest[-1] = (distance, score)
                        nearest.sort(key=lambda x: x[0])
            result = sum(x[1] for x in nearest) / len(nearest) if nearest else 0.0
            if result > score_best:
                best, score_best = action, result
        return best

    def state_receipt(self):
        h = sha256()
        h.update(b"FKP17-COUNT-RETRIEVAL-V1")
        h.update(self._digest.digest())
        h.update(bytes([self.neighbors]))
        for buffers in (self._prior, self._online):
            for buf in buffers:
                h.update(len(buf).to_bytes(4, "little"))
                h.update(buf)
        h.update(struct.pack("<II?", self.foundation_count, self.world_count,
                             self._sealed))
        return h.hexdigest()


def assert_strong_public_information(controls, candidate_foundation_sha):
    """Common public facts; no false assertion that information use is equal."""
    inputs = tuple(controls)
    if len(inputs) != 2 or {type(c) for c in inputs} != {SymbolicBayes, CountRetrieval}:
        raise ValueError("FKP17_STRONG_CONTROL_SET_INCOMPLETE")
    if any(c.foundation_count != FOUNDATION_RECORDS for c in inputs):
        raise ValueError("FKP17_STRONG_FOUNDATION_COUNT")
    if any(c.foundation_sha256 != candidate_foundation_sha for c in inputs):
        raise ValueError("FKP17_STRONG_SHARED_PUBLIC_DIGEST")
    if any(c.memory_bytes > MAX_MEMORY for c in inputs):
        raise ValueError("FKP17_STRONG_CAPACITY")
    return candidate_foundation_sha
