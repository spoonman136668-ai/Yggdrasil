"""FKP-17 public-only relationship-vs-flat memory DEV comparators.

No source import, no hidden law access, no first-use, no native Yggdrasil edit.
This is a deliberately small, explicit *research* learner/ablation for checking
information parity and action-conditioned consequences before strong Bayesian
and fully trained recurrent comparators are supplied. NOT SCIENTIFIC_PASS.
"""
from __future__ import annotations

from array import array
import hashlib
import json
import math
import struct

ARMS = ("STRUCTURED", "FLAT", "SHUFFLED", "MINIMAL", "NO_UPDATE")
ACTIONS = 8
REGISTERS = 8
VALUES = 16
FOUNDATION_EXPECTED = 32768
CAPACITY_BYTES = 1048576
_HIST_SIZE = ACTIONS * REGISTERS * VALUES
_PUBLIC_FIELDS = ("before", "action", "after", "reward", "done", "history")


def _state(value):
    if type(value) not in (tuple, list) or len(value) != REGISTERS:
        raise ValueError("FKP17_PUBLIC_STATE_SIZE")
    if any(type(x) is not int or x < 0 or x >= VALUES for x in value):
        raise ValueError("FKP17_PUBLIC_STATE_VALUE")
    return tuple(value)


def _action(value):
    if type(value) is not int or not 0 <= value < ACTIONS:
        raise ValueError("FKP17_PUBLIC_ACTION")
    return value


def _verified_public_row(row):
    # Accept exactly the public schema, never a purported future/reward oracle.
    if tuple(getattr(row, "_fields", ())) != _PUBLIC_FIELDS:
        raise ValueError("FKP17_PUBLIC_ONLY_TRANSITION_REQUIRED")
    before, action, after, reward, done, history = row
    before, action, after = _state(before), _action(action), _state(after)
    if type(reward) not in (int, float) or not math.isfinite(reward):
        raise ValueError("FKP17_PUBLIC_REWARD_INVALID")
    if reward < -1.0 or reward > 1.0 or type(done) is not bool:
        raise ValueError("FKP17_PUBLIC_REWARD_OR_DONE")
    if type(history) is not tuple or len(history) > 16:
        raise ValueError("FKP17_PUBLIC_HISTORY")
    # Cannot look into any future labels; the history objects are public only.
    for old in history:
        if tuple(getattr(old, "_fields", ())) != ("before", "action", "reward", "after", "done"):
            raise ValueError("FKP17_HISTORY_CONTAINS_PRIVATE_FIELDS")
    return before, action, after, float(reward), done, history


def _index(action, register, delta):
    return (action * REGISTERS + register) * VALUES + delta


def _empty_hist():
    return array("I", [0]) * _HIST_SIZE


def _observed_signature(values):
    # Public digest is purely behavioral and stable across the compared arms.
    before, action, after, reward, done, history = values
    past = [[list(x.before), x.action, float(x.reward), list(x.after), x.done] for x in history]
    raw = json.dumps([list(before), action, list(after), reward, done, past],
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    return len(raw).to_bytes(4, "little") + raw


class PublicRelationArm:
    """One bounded parameter table with exactly shared factual exposures.

    STRUCTURED uses directionally addressed register-change distributions.
    FLAT collapses relationships into action-mean observed reward.
    SHUFFLED retains topology size but permutes learned target registers.
    MINIMAL processes common facts for custody but does not initialize priors.
    NO_UPDATE freezes native structure after foundation, preserving world input.
    Each is intentionally weaker than the required independent exact
    Bayesian/symbolic and fully trained recurrent strong controls.
    """
    __slots__ = ("variant", "_foundation", "_world", "_foundation_rewards",
                 "_foundation_visits", "_world_rewards", "_world_visits",
                 "_digest", "_foundation_rows", "_world_rows", "_frozen")

    def __init__(self, variant: str):
        if variant not in ARMS or type(variant) is not str:
            raise ValueError("FKP17_UNKNOWN_RESEARCH_ARM")
        self.variant = variant
        self._foundation = _empty_hist()
        self._world = _empty_hist()
        self._foundation_rewards = [0.0] * ACTIONS
        self._foundation_visits = [0] * ACTIONS
        self._world_rewards = [0.0] * ACTIONS
        self._world_visits = [0] * ACTIONS
        self._digest = hashlib.sha256()
        self._foundation_rows = 0
        self._world_rows = 0
        self._frozen = False

    @property
    def received_foundation_count(self):
        return self._foundation_rows

    @property
    def foundation_sha256(self):
        return self._digest.hexdigest()

    @property
    def observed_world_count(self):
        return self._world_rows

    def _observe(self, row, *, foundation: bool):
        before, action, after, reward, done, history = _verified_public_row(row)
        if foundation:
            if self._frozen or self._foundation_rows >= FOUNDATION_EXPECTED:
                raise ValueError("FKP17_FOUNDATION_MUTATION_OR_OVERBUDGET")
            if self.variant == "MINIMAL":
                self._digest.update(_observed_signature((before, action, after,
                                                          reward, done, history)))
                self._foundation_rows += 1
                return
            counts, sums, visits = (self._foundation,
                                    self._foundation_rewards,
                                    self._foundation_visits)
        else:
            if not self._frozen:
                raise ValueError("FKP17_WORLD_BEFORE_FOUNDATION_SEAL")
            if self._world_rows >= 256:
                raise ValueError("FKP17_WORLD_ACTION_BUDGET")
            if self.variant == "NO_UPDATE":
                self._world_rows += 1
                return
            counts, sums, visits = (self._world, self._world_rewards,
                                    self._world_visits)
        offsets = [_index(action, register,
                          (after[register] - before[register]) % VALUES)
                   for register in range(REGISTERS)]
        # Validate every counter before changing ANY state, including custody
        # count and public source digest. An overflow cannot partially learn.
        if any(counts[offset] >= 65535 for offset in offsets):
            raise OverflowError("FKP17_PUBLIC_COUNT_OVERFLOW")
        if foundation:
            self._digest.update(_observed_signature((before, action, after,
                                                      reward, done, history)))
            self._foundation_rows += 1
        else:
            self._world_rows += 1
        visits[action] += 1
        sums[action] += reward
        for offset in offsets:
            counts[offset] += 1

    def fit_public_foundation(self, public_rows):
        for row in public_rows:
            self._observe(row, foundation=True)
        if self._foundation_rows != FOUNDATION_EXPECTED:
            raise ValueError("FKP17_FOUNDATION_INCOMPLETE")
        self._frozen = True
        if self.learned_bytes > CAPACITY_BYTES:
            raise ValueError("FKP17_MEMORY_CAPACITY")
        return self

    def begin_world(self):
        if not self._frozen:
            raise ValueError("FKP17_PRIOR_NOT_SEALED")
        self._world = _empty_hist()
        self._world_rewards = [0.0] * ACTIONS
        self._world_visits = [0] * ACTIONS
        self._world_rows = 0

    def observe_public(self, row):
        self._observe(row, foundation=False)

    @property
    def learned_bytes(self):
        # Fixed-layout direct numeric slots, both base and per-world counts.
        # Public upstream data streams are not retained here.
        return 2 * _HIST_SIZE * 4 + 2 * ACTIONS * (8 + 4)

    def _expected_cost(self, value, action, register):
        local = self._world
        prior = self._foundation
        # Public source training priors get ONE pseudo-observation total;
        # actual local interventions dominate when present.
        lo = _index(action, register, 0)
        local_sum = sum(local[lo:lo + VALUES])
        prior_sum = sum(prior[lo:lo + VALUES])
        total_weight = local_sum + (1 if prior_sum else 0)
        if total_weight == 0:
            return abs(value - 8)
        accum = 0.0
        if local_sum:
            for delta in range(VALUES):
                n = local[lo + delta]
                accum += n * abs(((value + delta) % VALUES) - 8)
        if prior_sum:
            accum += sum((prior[lo + delta] / prior_sum) *
                         abs(((value + delta) % VALUES) - 8)
                         for delta in range(VALUES))
        return accum / total_weight

    def choose_public(self, public_state):
        """Pure pre-outcome choice: accepts ONLY current eight public registers."""
        state = _state(public_state)
        scores = []
        for action in range(ACTIONS):
            if self.variant == "FLAT":
                if self._world_visits[action]:
                    score = self._world_rewards[action] / self._world_visits[action]
                elif self._foundation_visits[action]:
                    score = self._foundation_rewards[action] / self._foundation_visits[action]
                else:
                    score = 0.0
            else:
                before_cost = sum(abs(v - 8) for v in state)
                predicted = 0.0
                for register in range(REGISTERS):
                    # SHUFFLED keeps its learned edge counts/capacity but
                    # transfers each target distribution onto a different node.
                    source_register = (register - 3) % REGISTERS if self.variant == "SHUFFLED" else register
                    predicted += self._expected_cost(state[register], action, source_register)
                score = (before_cost - predicted) / 8
            scores.append(score)
        return max(range(ACTIONS), key=lambda a: scores[a])

    def state_receipt(self):
        """Source-independent deterministic parameter identity; no future data."""
        out = hashlib.sha256()
        out.update(self.variant.encode("ascii"))
        out.update(self._digest.digest())
        for table in (self._foundation, self._world):
            out.update(struct.pack("<" + "I" * len(table), *table))
        for numbers in (self._foundation_rewards, self._world_rewards):
            out.update(struct.pack("<" + "d" * len(numbers), *numbers))
        for numbers in (self._foundation_visits, self._world_visits):
            out.update(struct.pack("<" + "I" * len(numbers), *numbers))
        out.update(struct.pack("<II?", self._foundation_rows,
                               self._world_rows, self._frozen))
        return out.hexdigest()


def assert_equal_public_foundation(arms):
    """Fails closed before any scored run on missing or divergent priors."""
    received = tuple(arms)
    if len(received) != len(ARMS) or {arm.variant for arm in received} != set(ARMS):
        raise ValueError("FKP17_MISSING_MATCHED_ABLATION")
    if any(arm.received_foundation_count != FOUNDATION_EXPECTED for arm in received):
        raise ValueError("FKP17_PRIOR_COUNT_MISMATCH")
    digests = {arm.foundation_sha256 for arm in received}
    if len(digests) != 1:
        raise ValueError("FKP17_PRIOR_SOURCE_SHA_MISMATCH")
    if any(arm.learned_bytes > CAPACITY_BYTES for arm in received):
        raise ValueError("FKP17_CAPACITY_MISMATCH")
    return next(iter(digests))
