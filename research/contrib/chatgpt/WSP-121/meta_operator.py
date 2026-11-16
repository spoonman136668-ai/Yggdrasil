"""WSP-121 engineering-only fast-weight discovery of an unnamed route operator.

Distinct from WSP-120's 10548 enumerated programs. This prototype NEVER
opens WSP121 primary seeds or its parent's consumed original source.
Three input bits and the two two-hop route primitives ARE supplied: no
claim that a new universal primitive or general intelligence was invented.
"""
from __future__ import annotations

from array import array
from dataclasses import dataclass
from hashlib import sha256
import json
import random

N, R = 64, 6
ENGINEERING_SEEDS = tuple(range(121900, 121904))
PRIMARY_SEEDS = tuple(range(121000, 121048))
RESERVED_SEEDS = tuple(range(121800, 121864)) + tuple(range(120800, 120864))
FIT_BUDGET, TRANSFER_BUDGET = 8, 4
MAX_SIGNED = 2**31 - 1
SCHEMA = 'wsp121.fastweight-operator-cold.v1'


def _dump(doc):
    return json.dumps(doc, sort_keys=True, separators=(',', ':'))


def _check(value, message):
    if not value:
        raise ValueError('WSP121_' + message)


def _public_world(seed, attempt):
    if type(seed) is not int or seed not in ENGINEERING_SEEDS:
        raise PermissionError("WSP121_ENGINEERING_SEED_ONLY")
    rng = random.Random((seed << 8) + attempt)
    graph = tuple(tuple(rng.sample(range(N), N)) for _ in range(R))
    first = [(_paths(graph, s)) for s in range(N)]
    # All 64 subjects must be informative: gate label never aliases a=b.
    if any(a == b for a, b in first):
        return None
    contexts = [_context(graph, s) for s in range(N)]
    if any(contexts.count(k) < 3 for k in range(8)):
        return None
    groups = [list(s for s in range(N) if contexts[s] == k) for k in range(8)]
    for group in groups:
        rng.shuffle(group)
    # First eight legal inquiries each cover a distinct operator context.
    head = [group.pop() for group in groups]
    tail = [v for group in groups for v in group]
    rng.shuffle(tail)
    order = tuple(head + tail)
    return PublicWorld(seed, graph, order[:40], order[40:])


def _paths(graph, s):
    return graph[1][graph[0][s]], graph[3][graph[2][s]]


def _context(graph, s):
    return (s & 1) | ((graph[0][s] & 1) << 1) | ((graph[2][s] & 1) << 2)


@dataclass(frozen=True)
class PublicWorld:
    seed: int
    graph: tuple
    legal: tuple
    held: tuple

    def feature(self, subject):
        _check(type(subject) is int and 0 <= subject < N, 'BAD_SUBJECT')
        return _context(self.graph, subject)

    def routes(self, subject):
        _check(type(subject) is int and 0 <= subject < N, 'BAD_SUBJECT')
        return _paths(self.graph, subject)


def engineering_world(seed=121900):
    if type(seed) is not int or seed not in ENGINEERING_SEEDS:
        raise PermissionError('WSP121_ENGINEERING_SEED_ONLY')
    for attempt in range(1024):
        world = _public_world(seed, attempt)
        if world is not None:
            return world
    raise AssertionError('WSP121_ENGINEERING_WORLD_REJECTION_EXHAUSTED')


def original_world(seed):
    # Deliberately no primary generator in this source-safe engineering gate.
    raise PermissionError('WSP121_PRIMARY_FIRST_USE_NOT_AUTHORIZED')


# The target table is kept in a source-only closure and never passed to
# learners. This engineering fixture's gate is XOR of all three visible bits.
def _fixture_gate(context):
    return (context.bit_count() & 1)


class EvidenceSource:
    def __init__(self, world, *, budget):
        _check(type(world) is PublicWorld and world.seed in ENGINEERING_SEEDS,
               'ENGINEERING_SOURCE_ONLY')
        _check(budget in (FIT_BUDGET, TRANSFER_BUDGET), 'BAD_BUDGET')
        self._world = world
        self._budget = budget
        self._used = set()
        self._receipt = sha256()

    def query(self, subject):
        if type(subject) is not int or subject not in self._world.legal:
            raise PermissionError('WSP121_WITHHELD_OR_INVALID_QUERY')
        if subject in self._used or len(self._used) >= self._budget:
            raise PermissionError('WSP121_SOURCE_DUPLICATE_OR_CAP')
        context = self._world.feature(subject)
        routes = self._world.routes(subject)
        answer = routes[_fixture_gate(context)]
        self._used.add(subject)
        self._receipt.update(bytes((subject, answer)))
        return answer

    @property
    def count(self):
        return len(self._used)

    @property
    def receipt(self):
        return self._receipt.hexdigest()


def _route_label(public, subject, outcome):
    options = public.routes(subject)
    _check(options[0] != options[1], 'ROUTE_NOT_IDENTIFIABLE')
    if type(outcome) is not int or outcome not in options:
        raise ValueError('WSP121_UNVERIFIED_OR_BAD_OUTCOME')
    return 0 if outcome == options[0] else 1


class NumericFastWeights:
    """Sixteen learned signed int32 weights, no list of whole-law programs."""
    def __init__(self):
        self.weights = array('i', [0] * 16)
        self.history = []

    def _write(self, context, route):
        if self.weights[2*context + route] >= MAX_SIGNED:
            raise OverflowError('WSP121_NUMERIC_OVERFLOW')
        if self.weights[2*context + 1-route] <= -MAX_SIGNED:
            raise OverflowError('WSP121_NUMERIC_OVERFLOW')
        self.weights[2*context+route] += 1
        self.weights[2*context+1-route] -= 1

    def observe(self, public, subject, outcome):
        _check(type(public) is PublicWorld, 'PUBLIC_VIEW_ONLY')
        context = public.feature(subject)
        route = _route_label(public, subject, outcome)
        # Contradictory evidence for same shared operator means a detected
        # potential context/domain shift; never overwrite it and assert success.
        prior = self.infer_route(context)
        if prior is not None and prior != route:
            raise ValueError('WSP121_OPERATOR_CONTRADICTION')
        self._write(context, route)
        self.history.append([context, route])

    def infer_route(self, context):
        _check(type(context) is int and 0 <= context < 8, 'BAD_CONTEXT')
        a, b = self.weights[2*context:2*context+2]
        if a == b:
            return None
        return 0 if a > b else 1

    def infer(self, public, subject):
        _check(type(public) is PublicWorld, 'PUBLIC_VIEW_ONLY')
        route = self.infer_route(public.feature(subject))
        return None if route is None else public.routes(subject)[route]

    def snapshot(self):
        payload = {'schema': SCHEMA, 'weights': list(self.weights),
                   'history': self.history}
        return _dump({'payload': payload,
                      'sha256': sha256(_dump(payload).encode()).hexdigest()})

    @classmethod
    def restore(cls, blob):
        doc = json.loads(blob)
        payload = doc['payload']
        if payload.get('schema') != SCHEMA or sha256(
                _dump(payload).encode()).hexdigest() != doc.get('sha256'):
            raise ValueError('WSP121_COLD_DIGEST_INVALID')
        weights, history = payload.get('weights'), payload.get('history')
        if (type(weights) is not list or len(weights) != 16
                or any(type(w) is not int or abs(w) > MAX_SIGNED for w in weights)
                or type(history) is not list):
            raise ValueError('WSP121_COLD_FORMAT_INVALID')
        obj = cls()
        for record in history:
            if (type(record) is not list or len(record) != 2 or
                    any(type(i) is not int for i in record) or
                    not (0 <= record[0] < 8 and record[1] in (0, 1))):
                raise ValueError('WSP121_COLD_HISTORY_INVALID')
            obj._write(*record)
            obj.history.append(record[:])
        if list(obj.weights) != weights:
            raise ValueError('WSP121_COLD_COUNTER_PROVENANCE')
        return obj


class SymbolicMemo:
    """Optimized independent exact symbolic table, not slow enumeration."""
    def __init__(self):
        self.table = {}

    def observe(self, public, subject, outcome):
        context = public.feature(subject)
        route = _route_label(public, subject, outcome)
        if context in self.table and self.table[context] != route:
            raise ValueError('WSP121_OPERATOR_CONTRADICTION')
        self.table[context] = route

    def infer(self, public, subject):
        route = self.table.get(public.feature(subject))
        return None if route is None else public.routes(subject)[route]


class SymbolicEnumerative:
    """Exact 256 possible three-bit route tables, diagnostic secondary only."""
    def __init__(self):
        self.table_ids = list(range(256))

    def observe(self, public, subject, outcome):
        context = public.feature(subject)
        route = _route_label(public, subject, outcome)
        self.table_ids = [i for i in self.table_ids if ((i >> context) & 1) == route]
        if not self.table_ids:
            raise ValueError('WSP121_OPERATOR_CONTRADICTION')

    def infer(self, public, subject):
        context = public.feature(subject)
        routes = {(i >> context) & 1 for i in self.table_ids}
        return public.routes(subject)[next(iter(routes))] if len(routes) == 1 else None


class NoUpdate:
    def observe(self, public, subject, outcome):
        _route_label(public, subject, outcome)

    def infer(self, public, subject):
        return None


def _held_counts(learner, world):
    truth = [world.routes(s)[_fixture_gate(world.feature(s))] for s in world.held]
    pred = [learner.infer(world, s) for s in world.held]
    return {'correct': sum(p is not None and p == y for p, y in zip(pred, truth)),
            'wrong_confident': sum(p is not None and p != y for p, y in zip(pred, truth)),
            'abstained': sum(p is None for p in pred), 'held': len(truth)}


def engineering_fixture():
    """All original science seeds prohibited; no semantic or hidden claims."""
    learners = {'NUMERIC_FAST': NumericFastWeights(),
                'SYMBOLIC_MEMO': SymbolicMemo(),
                'SYMBOLIC_ENUM': SymbolicEnumerative(),
                'NO_UPDATE': NoUpdate()}
    per_world = []
    result = {'schema': 'wsp121.source-safe-fixture.v1', 'scientific': False,
              'source_first_use': False, 'source_worlds': [],
              'source_calls': {}, 'worlds': []}
    for ordinal, seed in enumerate(ENGINEERING_SEEDS):
        world = engineering_world(seed)
        budget = FIT_BUDGET if ordinal < 2 else TRANSFER_BUDGET
        sources = {key: EvidenceSource(world, budget=budget) for key in learners}
        for subject in world.legal[:budget]:
            for key, learner in learners.items():
                response = sources[key].query(subject)
                learner.observe(world, subject, response)
        ledger = {key: {'source_calls': sources[key].count,
                        'source_sha256': sources[key].receipt,
                        **_held_counts(learner, world)}
                  for key, learner in learners.items()}
        if len({record['source_sha256'] for record in ledger.values()}) != 1:
            raise AssertionError('WSP121_SOURCE_PARITY')
        per_world.append({'seed': seed, 'budget': budget, 'arms': ledger})
    numeric = learners['NUMERIC_FAST']
    restored = NumericFastWeights.restore(numeric.snapshot())
    for seed in ENGINEERING_SEEDS:
        w = engineering_world(seed)
        if [numeric.infer(w, s) for s in w.held] != [
                restored.infer(w, s) for s in w.held]:
            raise AssertionError('WSP121_COLD_CHANGED_PREDICTIONS')
    result['worlds'] = per_world
    result['cold_ok'] = True
    result['numeric_learned_bytes'] = len(numeric.weights) * numeric.weights.itemsize
    result['retained_contexts'] = sum(numeric.infer_route(i) is not None
                                      for i in range(8))
    result['strong_symbolic_identical'] = all(
        data['arms']['NUMERIC_FAST']['correct'] == data['arms']['SYMBOLIC_MEMO']['correct']
        and data['arms']['NUMERIC_FAST']['wrong_confident'] == data['arms']['SYMBOLIC_MEMO']['wrong_confident']
        for data in per_world)
    return result
