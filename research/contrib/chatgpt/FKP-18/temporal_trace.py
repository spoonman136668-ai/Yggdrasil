"""FKP-18: sparse non-token causal event traces with contradiction-gated forks.

Research-only prototype. No source-generator, native engine, LLM, transformer,
GPU, private evaluator, held cohort, or external library is imported.

Public evidence is received only AFTER its real action. The ledger initially
stores an action -> target -> delta marginal. On observed conflict, it allocates
a bounded source-value-conditional *fork* and backfills the first witness.
An ordered adjacency trace remembers actually observed predecessor actions;
a trace alone does NOT establish causation or delayed credit. Evidence,
allocation, and cold numeric identity are deliberately interpretable.
"""
from __future__ import annotations

from collections import namedtuple
from hashlib import sha256
import json
import math

PublicTransition = namedtuple("PublicTransition", "before action reward after done")
PublicStep = namedtuple("PublicStep", "before action after reward done history")
PUB_FIELDS = PublicStep._fields
HIST_FIELDS = PublicTransition._fields
MAX_SLOTS = 512
MAX_LOGICAL_BYTES = 65536
MAX_EVENTS = 256
MAGIC = "FKP18_SPARSE_TRACE_V1"


def _state(value):
    if type(value) not in (tuple, list) or len(value) != 8:
        raise ValueError("FKP18_PUBLIC_STATE")
    if any(type(x) is not int or not 0 <= x < 16 for x in value):
        raise ValueError("FKP18_PUBLIC_UINT4")
    return tuple(value)


def _act(value):
    if type(value) is not int or not 0 <= value < 8:
        raise ValueError("FKP18_PUBLIC_ACTION")
    return value


def _valid(row):
    if tuple(getattr(row, "_fields", ())) != PUB_FIELDS:
        raise ValueError("FKP18_NO_PRIVATE_OR_FUTURE_FIELDS")
    before, action, after, reward, done, history = row
    before, action, after = _state(before), _act(action), _state(after)
    if type(reward) not in (int, float) or not math.isfinite(reward) or not -1 <= reward <= 1:
        raise ValueError("FKP18_PUBLIC_REWARD")
    if type(done) is not bool or type(history) is not tuple or len(history) > 16:
        raise ValueError("FKP18_PUBLIC_HISTORY")
    validated_history = []
    for past in history:
        if tuple(getattr(past, "_fields", ())) != HIST_FIELDS:
            raise ValueError("FKP18_HISTORY_PRIVATE_FIELD")
        pb, pa, pr, pafter, pdone = past
        pb, pa, pafter = _state(pb), _act(pa), _state(pafter)
        if type(pr) not in (int, float) or not math.isfinite(pr) or not -1 <= pr <= 1:
            raise ValueError("FKP18_HISTORY_BAD_REWARD")
        if type(pdone) is not bool:
            raise ValueError("FKP18_HISTORY_BAD_DONE")
        validated_history.append(PublicTransition(pb, pa, float(pr), pafter, pdone))
    return PublicStep(before, action, after, float(reward), done,
                      tuple(validated_history))


def _delta(before, after):
    diff = (after - before) % 16
    return diff if diff <= 7 else diff - 16


def _encode(value):
    return json.dumps(value, sort_keys=True, allow_nan=False,
                      separators=(",", ":")).encode("ascii")


def _public_prior(row):
    return PublicTransition(row.before, row.action, row.reward, row.after, row.done)


class SparseTemporalTrace:
    """Bounded public memory, no dense causal grammar and no private labels."""

    def __init__(self, *, context_forks=True, temporal_order=True,
                 slot_budget=MAX_SLOTS):
        if type(context_forks) is not bool or type(temporal_order) is not bool:
            raise ValueError("FKP18_BAD_ABLATION_FLAG")
        if type(slot_budget) is not int or not 1 <= slot_budget <= MAX_SLOTS:
            raise ValueError("FKP18_SLOT_BUDGET")
        self.context_forks = context_forks
        self.temporal_order = temporal_order
        self.slot_budget = slot_budget
        self.begin_world()

    def begin_world(self):
        self._marginal = {}
        self._first = {}
        self._forks = {}
        self._splits = set()
        self._order = {}
        self._last = None
        self._count = 0
        self._last_feedback = ()
        self._guard_capacity()
        return self

    @property
    def public_observations(self):
        return self._count

    @property
    def discovered_conditional_forks(self):
        return len(self._splits)

    @property
    def learned_relation_slots(self):
        return len(self._forks) + len(self._order)

    @property
    def logical_learned_bytes(self):
        # Explicit compact fixed-width *logical state* accounting; NOT Python RSS.
        return (len(self._marginal) * 16 + len(self._first) * 16 +
                len(self._forks) * 20 + len(self._order) * 16 +
                len(self._splits) * 8 + (64 if self.temporal_order and self._last else 0))

    def _guard_capacity(self):
        if (self.learned_relation_slots > self.slot_budget or
                self.logical_learned_bytes > MAX_LOGICAL_BYTES):
            raise ValueError("FKP18_CAUSAL_TRACE_CAPACITY")

    def _staged(self, row, event_id):
        if type(event_id) is not int or event_id != self._count:
            raise ValueError("FKP18_DUPLICATE_OR_REORDERED_PUBLIC_EVENT_ID")
        if self._count >= MAX_EVENTS:
            raise ValueError("FKP18_EVENT_BUDGET")
        step = _valid(row)
        if self._last is None:
            if step.history:
                raise ValueError("FKP18_FIRST_EVENT_HAS_UNOBSERVED_HISTORY")
        elif (not step.history or
              step.history[-1] != self._last or
              step.before != self._last.after or self._last.done):
            raise ValueError("FKP18_UNWITNESSED_OR_NONPHYSICAL_HISTORY")
        return step

    def observe_public(self, row, *, event_id):
        """Atomic receipt: validate and compute all derived relations first."""
        step = self._staged(row, event_id)
        marginal = dict(self._marginal)
        first = dict(self._first)
        forks = dict(self._forks)
        splits = set(self._splits)
        order = dict(self._order)
        feedback = []
        for target in range(8):
            delta = _delta(step.before[target], step.after[target])
            root = (step.action, target)
            m = (step.action, target, delta)
            marginal[m] = marginal.get(m, 0) + 1
            if root not in first:
                first[root] = (step.before[target], delta)
            elif first[root][1] != delta and self.context_forks:
                # A second genuinely observed outcome contradicts the
                # action-only hypothesis. Backfill the witnessed first case.
                if root not in splits:
                    old_before, old_delta = first[root]
                    old_key = (step.action, target, old_before, old_delta)
                    forks[old_key] = forks.get(old_key, 0) + 1
                    splits.add(root)
                    feedback.append(("CONTEXT_FORK", step.action, target))
            if self.context_forks and root in splits:
                key = (step.action, target, step.before[target], delta)
                forks[key] = forks.get(key, 0) + 1
            if self.temporal_order and self._last is not None:
                # This is an *observed ordered event*, not a causal oracle.
                key = (self._last.action, step.action, target, delta)
                order[key] = order.get(key, 0) + 1
        old = (self._marginal, self._first, self._forks,
               self._splits, self._order, self._last, self._count)
        self._marginal, self._first, self._forks = marginal, first, forks
        self._splits, self._order = splits, order
        self._last = _public_prior(step)
        self._count += 1
        try:
            self._guard_capacity()
        except ValueError:
            (self._marginal, self._first, self._forks, self._splits,
             self._order, self._last, self._count) = old
            raise
        self._last_feedback = tuple(feedback)
        return self._last_feedback

    def predict_delta(self, public_state, action, target):
        """A learned public intervention effect, or abstain when unsupported."""
        state = _state(public_state)
        action = _act(action)
        if type(target) is not int or not 0 <= target < 8:
            raise ValueError("FKP18_TARGET")
        root = (action, target)
        if root not in self._first:
            return None
        if self.context_forks and root in self._splits:
            counts = [(delta, n) for (a, t, prev, delta), n in self._forks.items()
                      if a == action and t == target and prev == state[target]]
        else:
            counts = [(delta, n) for (a, t, delta), n in self._marginal.items()
                      if a == action and t == target]
        if not counts:
            return None
        # Exact agreement, not a confidence claim from one noisy observation.
        distinct = {v for v, _ in counts}
        return next(iter(distinct)) if len(distinct) == 1 else None

    def observed_order_trace(self):
        return tuple(sorted((*key, count) for key, count in self._order.items()))

    def semantic_receipt(self):
        """Includes only evidence that the chosen ablation can *use*."""
        state = {
            "schema": MAGIC,
            "flags": [self.context_forks, self.temporal_order],
            "marginals": sorted((*k, v) for k, v in self._marginal.items()),
            "first": (sorted((*k, *v) for k, v in self._first.items())
                      if self.context_forks else []),
            "forks": sorted((*k, v) for k, v in self._forks.items()),
            "splits": sorted(self._splits),
            "ordered": self.observed_order_trace() if self.temporal_order else [],
            "count": self._count
        }
        return sha256(_encode(state)).hexdigest()

    def checkpoint(self):
        """Versioned, small, SHA-covered cold data; no pickle/code execution."""
        state = {
            "magic": MAGIC, "context": self.context_forks, "temporal": self.temporal_order,
            "limit": self.slot_budget, "count": self._count,
            "marginals": sorted((*k, n) for k, n in self._marginal.items()),
            "first": (sorted((*k, *v) for k, v in self._first.items())
                      if self.context_forks else []),
            "forks": sorted((*k, n) for k, n in self._forks.items()),
            "splits": sorted(self._splits), "order": list(self.observed_order_trace()),
            "last": (list(self._last) if self._last else None),
            "semantic_sha256": self.semantic_receipt()
        }
        raw = _encode(state)
        if len(raw) > MAX_LOGICAL_BYTES:
            raise ValueError("FKP18_CHECKPOINT_BYTES")
        return _encode({"body": state, "sha256": sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, encoded):
        if type(encoded) is not bytes or len(encoded) > MAX_LOGICAL_BYTES:
            raise ValueError("FKP18_INVALID_SNAPSHOT")
        try:
            payload = json.loads(encoded, object_pairs_hook=_unique_pairs,
                                 parse_constant=lambda _: _invalid_nonfinite())
        except (UnicodeError, ValueError, TypeError) as exc:
            raise ValueError("FKP18_INVALID_SNAPSHOT") from exc
        if type(payload) is not dict or set(payload) != {"body", "sha256"}:
            raise ValueError("FKP18_BAD_CHECKPOINT_ENVELOPE")
        body = payload["body"]
        if type(body) is not dict or set(body) != {
                "magic", "context", "temporal", "limit", "count", "marginals",
                "first", "forks", "splits", "order", "last", "semantic_sha256"}:
            raise ValueError("FKP18_BAD_CHECKPOINT_SCHEMA")
        if sha256(_encode(body)).hexdigest() != payload["sha256"]:
            raise ValueError("FKP18_CHECKPOINT_SHA_MISMATCH")
        if body["magic"] != MAGIC or type(body["count"]) is not int or not 0 <= body["count"] <= MAX_EVENTS:
            raise ValueError("FKP18_CHECKPOINT_VERSION_OR_COUNT")
        obj = cls(context_forks=body["context"], temporal_order=body["temporal"],
                  slot_budget=body["limit"])
        if any(type(v) is not list for k in (
                "marginals","first","forks","splits","order") for v in body[k]):
            raise ValueError("FKP18_CHECKPOINT_BAD_ENTRY")
        obj._marginal = {_signed_delta_key(v[:3], (8,8)): _positive(v[3])
                         for v in body["marginals"]}
        obj._first = {_integer_key(v[:2], (8,8)): tuple(v[2:])
                      for v in body["first"]}
        obj._forks = {_signed_delta_key(v[:4], (8,8,16)): _positive(v[4])
                      for v in body["forks"]}
        obj._splits = {_integer_key(v, (8,8)) for v in body["splits"]}
        obj._order = {_signed_delta_key(v[:4], (8,8,8)): _positive(v[4])
                      for v in body["order"]}
        if body["last"] is not None:
            data = body["last"]
            if type(data) is not list or len(data) != 5:
                raise ValueError("FKP18_BAD_LAST_PUBLIC_EVENT")
            obj._last = PublicTransition(_state(data[0]), _act(data[1]),
                                         float(data[2]), _state(data[3]), data[4])
        obj._count = body["count"]
        obj._guard_capacity()
        if obj.semantic_receipt() != body["semantic_sha256"]:
            raise ValueError("FKP18_RESTORED_SEMANTIC_MISMATCH")
        if obj.checkpoint() != encoded:
            raise ValueError("FKP18_NONCANONICAL_CHECKPOINT")
        return obj


def _invalid_nonfinite():
    raise ValueError("FKP18_NONFINITE_JSON")


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("FKP18_DUPLICATE_CHECKPOINT_KEY")
        result[key] = value
    return result


def _positive(value):
    if type(value) is not int or not 0 < value <= MAX_EVENTS:
        raise ValueError("FKP18_INVALID_OBSERVATION_COUNT")
    return value


def _integer_key(values, sizes):
    if len(values) != len(sizes):
        raise ValueError("FKP18_CHECKPOINT_KEY_LENGTH")
    if any(type(x) is not int or not 0 <= x < size
           for x, size in zip(values, sizes)):
        raise ValueError("FKP18_CHECKPOINT_KEY")
    return tuple(values)

def _signed_delta_key(values, prefix_sizes):
    if len(values) != len(prefix_sizes) + 1:
        raise ValueError("FKP18_CHECKPOINT_DELTA_KEY_LENGTH")
    prefix = _integer_key(values[:-1], prefix_sizes)
    delta = values[-1]
    if type(delta) is not int or not -8 <= delta <= 7:
        raise ValueError("FKP18_CHECKPOINT_DELTA_KEY")
    return prefix + (delta,)
