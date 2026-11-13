"""WSP62 expandable source-blind Boolean rule writer.

Numerical model: algebraic-normal-form degree 0/1, expanding to degree 2
when observed physical consequences contradict the degree-1 mechanism.
To avoid unjustified confidence *before* a contradiction appears, all public
predictions are guarded by the full degree-2 version space: they are emitted
only when the corresponding query is identifiable from actual observations.
Unknown => abstain. No simulator import, oracle channels, gradient, token
autoregression or arbitrary-state training query.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import sys

_PARENT = Path(__file__).resolve().parents[1] / "WSP-61"
sys.path.insert(0, str(_PARENT))
from learner import ReachableCausalLearner, _state, ACTIONS, INITIAL, _canon

FEATURE_TERMS = tuple(combinations(range(4), degree)
                      for degree in (0, 1, 2))
TERMS = tuple(term for family in FEATURE_TERMS for term in family)
DEGREE1_COLUMNS = 5
DEGREE2_COLUMNS = 11
MAX_SNAPSHOT_BYTES = 300000


def _features(state):
    return sum(1 << j for j, term in enumerate(TERMS)
               if all(state[x] for x in term))


def _linear_basis(equations, width):
    """Reduce linear equations over GF(2); retain output RHS for prediction.

    A conflicting RHS for a zero-reduced equation means the model family
    cannot explain the charged observations, in which case refuse.
    """
    pivots = {}
    for mask, rhs in equations:
        mask &= (1 << width) - 1
        while mask:
            pivot = mask.bit_length() - 1
            previous = pivots.get(pivot)
            if previous is None:
                pivots[pivot] = (mask, rhs)
                break
            mask ^= previous[0]
            rhs ^= previous[1]
        if not mask and rhs:
            return None
    return pivots


def _certain_value(basis, mask):
    if basis is None:
        return None
    rhs = 0
    while mask:
        pivot = mask.bit_length() - 1
        equation = basis.get(pivot)
        if equation is None:
            return None
        mask ^= equation[0]
        rhs ^= equation[1]
    return rhs


class ExpandedCausalLearner(ReachableCausalLearner):
    gradient_updates = 0

    def __init__(self):
        super().__init__()
        self._anf_cache = {}

    def observe(self, experience):
        super().observe(experience)
        self._anf_cache.clear()

    def _systems(self, action):
        if action in self._anf_cache:
            return self._anf_cache[action]
        observations = [
            (_features(before), after)
            for before, a, after in self.ledger if a == action
        ]
        if not observations:
            self._anf_cache[action] = None
            return None
        systems = []
        for output_bit in range(4):
            equations = [(f, y[output_bit]) for f, y in observations]
            linear = _linear_basis(equations, DEGREE1_COLUMNS)
            quadratic = _linear_basis(equations, DEGREE2_COLUMNS)
            systems.append({
                "linear": linear,
                "quadratic": quadratic,
                # This flag is a learned contradiction-triggered promotion,
                # NOT a truth-table supplied by the evaluator.
                "promoted": linear is None and quadratic is not None
            })
        self._anf_cache[action] = tuple(systems)
        return self._anf_cache[action]

    def predict(self, before, action, memory_only=False):
        before = _state(before)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("invalid public action")
        if memory_only:
            return super().predict(before, action, memory_only=True)
        systems = self._systems(action)
        if systems is None:
            return None
        features = _features(before)
        output = []
        for bit in systems:
            # Compare all degree-2 solutions, regardless of whether degree-1
            # has yet been contradicted, so guesses cannot be made merely
            # because fewer-parent rules are easier to fit.
            v = _certain_value(bit["quadratic"], features)
            if v is None:
                return None
            output.append(v)
        return tuple(output)

    def expansions(self):
        return tuple(
            (action, bit)
            for action in ACTIONS for bit, rule in
            enumerate(self._systems(action) or ())
            if rule["promoted"]
        )

    def rank_receipts(self):
        return tuple(
            tuple({
                "degree1_rank": len(entry["linear"])
                                if entry["linear"] is not None else -1,
                "degree2_rank": len(entry["quadratic"])
                                if entry["quadratic"] is not None else -1,
                "expanded": entry["promoted"]
            } for entry in (self._systems(action) or ()))
            for action in ACTIONS
        )

    def committed_numeric_weights(self):
        """Only count an exact coefficient vector when its 11-d basis has
        full rank; partial systems are *not* billed as known fitted weights."""
        known = 0
        for action in ACTIONS:
            for entry in self._systems(action) or ():
                if entry["quadratic"] is not None:
                    known += len(entry["quadratic"])
        return known

    def snapshot(self):
        payload = {
            "schema": "wsp62.expanded-anf.v1",
            "ledger": [[list(b), a, list(y)] for b, a, y in self.ledger],
            "gradient_updates": 0
        }
        envelope = {
            "payload": payload,
            "sha256": sha256(_canon(payload).encode("ascii")).hexdigest()
        }
        raw = _canon(envelope)
        if len(raw.encode("ascii")) > MAX_SNAPSHOT_BYTES:
            raise OverflowError("snapshot memory ceiling")
        return raw

    @classmethod
    def restore(cls, raw):
        if type(raw) is not str or len(raw.encode("utf-8")) > MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid memory snapshot")
        try:
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("invalid envelope")
            p = envelope["payload"]
            if (type(p) is not dict or p.get("schema") != "wsp62.expanded-anf.v1" or
                    p.get("gradient_updates") != 0 or
                    sha256(_canon(p).encode("ascii")).hexdigest() != envelope["sha256"]):
                raise ValueError("tampered source/weights")
            if type(p.get("ledger")) is not list or len(p["ledger"]) > 80:
                raise ValueError("invalid ledger size")
            learner = cls()
            for entry in p["ledger"]:
                if type(entry) is not list or len(entry) != 3:
                    raise ValueError("bad evidence row")
                before, action, after = entry
                class PhysicalExperience:
                    pass
                row = PhysicalExperience()
                row.before, row.action, row.after, row.action_cost = (
                    tuple(before), action, tuple(after), 1)
                learner.observe(row)
            if learner.snapshot() != raw:
                raise ValueError("noncanonical or inconsistent snapshot")
            return learner
        except (ValueError, TypeError, KeyError, IndexError, UnicodeError,
                json.JSONDecodeError) as exc:
            raise ValueError("invalid memory snapshot") from exc

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8


class LinearOnlyLearner(ExpandedCausalLearner):
    """Diagnostic fixed degree-one learner, not safe under quadratic worlds."""
    def predict(self, before, action, memory_only=False):
        before = _state(before)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("bad action")
        if memory_only:
            return super().predict(before, action, memory_only=True)
        systems = self._systems(action)
        if systems is None:
            return None
        f = _features(before) & ((1 << DEGREE1_COLUMNS) - 1)
        answer = [_certain_value(x["linear"], f) for x in systems]
        return tuple(answer) if all(v is not None for v in answer) else None
