"""WSP-120 isolated structural-growth research, source-safe public only.

No pretrained architecture/weights, hidden source, protected cohort or native mutation.
A finite composition/conditional *grammar* is supplied: growth is not invention of
a genuinely unknown primitive. Do not call engineering checks scientific PASS.
"""
from __future__ import annotations

from array import array
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
import random

N = 64
R = 6
MAX_QUERIES = 32
PUBLIC_SEEDS = tuple(range(120000, 120024))
RESERVED_SEEDS = tuple(range(120800, 120864))
TIERS = (192, 288, 384)
EXPOSURES = (0, 4, 8, 16, 32)
ENGINEERING_SEED = 120900
MAX_PROGRAMS = 16384
MAX_NUMERIC_BYTES = 131072
SCHEMA = "wsp120.numeric-growth.cold.v1"


def _chain_programs(degrees):
    for degree in degrees:
        for law in product(range(R), repeat=degree):
            yield ("c", law)


FIXED3 = tuple(_chain_programs((3,)))


def _novel_programs():
    yield from _chain_programs((4, 5))
    pairs = tuple(product(range(R), repeat=2))
    for a in pairs:
        for b in pairs:
            if a != b:
                yield ("g", (a, b))


NOVEL = tuple(_novel_programs())
GRAMMAR = FIXED3 + NOVEL
assert len(GRAMMAR) == 216 + 6**4 + 6**5 + 36*35
assert len(GRAMMAR) <= MAX_PROGRAMS


def walk(graph, subject, program):
    """Pure public-graph interpreter. A missing primitive edge means UNKNOWN."""
    if type(subject) is not int or not 0 <= subject < N:
        raise ValueError("WSP120_INVALID_SUBJECT")
    kind, rule = program
    if kind == "c":
        path = rule
    elif kind == "g":
        path = rule[subject & 1]
    else:
        raise ValueError("WSP120_UNKNOWN_OPERATOR")
    value = subject
    for relation in path:
        value = graph[relation].get(value)
        if value is None:
            return None
    return value


def _full_signature(edges, law):
    return tuple(walk(tuple(dict(enumerate(row)) for row in edges), s, law) for s in range(N))


@dataclass(frozen=True)
class World:
    seed: int
    edges: tuple
    targets: tuple
    source_order: tuple
    reveal_order: tuple

    def public_graph(self, visible_edges):
        if visible_edges not in TIERS:
            raise PermissionError("WSP120_INVALID_VISIBLE_TIER")
        graph = [dict() for _ in range(R)]
        for rel, subject in self.reveal_order[:visible_edges]:
            graph[rel][subject] = self.edges[rel][subject]
        return tuple(graph)


def _construct_world(seed):
    rng = random.Random(seed)
    edges = tuple(tuple(rng.sample(range(N), N)) for _ in range(R))
    public_full = tuple(dict(enumerate(row)) for row in edges)
    older_signatures = {
        tuple(walk(public_full, s, law) for s in range(N))
        for law in _chain_programs((1, 2, 3))
    }
    used = set(older_signatures)
    candidates = {
        "CHAIN4": tuple(_chain_programs((4,))),
        "CHAIN5": tuple(_chain_programs((5,))),
        "GATE2": tuple(p for p in NOVEL if p[0] == "g"),
    }
    targets = []
    for family in ("CHAIN4", "CHAIN5", "GATE2"):
        indices = list(range(len(candidates[family])))
        rng.shuffle(indices)
        chosen = None
        for index in indices:
            program = candidates[family][index]
            signature = tuple(walk(public_full, s, program) for s in range(N))
            if signature not in used:
                chosen = program
                used.add(signature)
                break
        if chosen is None:
            raise AssertionError("WSP120_NONIDENTIFIABLE_SOURCE_FAMILY")
        targets.append(chosen)
    subjects = list(range(N))
    rng.shuffle(subjects)
    reveal = list(product(range(R), range(N)))
    rng.shuffle(reveal)
    return World(seed, edges, tuple(targets), tuple(subjects), tuple(reveal))


def source_safe_world(seed):
    if type(seed) is not int or seed not in PUBLIC_SEEDS:
        raise PermissionError("WSP120_PUBLIC_ONLY")
    return _construct_world(seed)


def engineering_fixture_world():
    """Disjoint open fixture: NEVER a primary-source or reserved world."""
    return _construct_world(ENGINEERING_SEED)


def inquiry_pool(world):
    return tuple(world.source_order[:40])


def held_subjects(world):
    return tuple(world.source_order[40:])


class EvidenceSource:
    """Externally verified toy consequences, one per selected legal action."""
    def __init__(self, world, target):
        if target not in world.targets:
            raise ValueError("WSP120_BAD_TARGET_CUSTODY")
        self.__world = world
        self.__target = target
        self.allowed = set(inquiry_pool(world))
        self.used = set()
        self.receipt = sha256()

    def query(self, subject):
        if type(subject) is not int or subject not in self.allowed:
            raise PermissionError("WSP120_HELD_OR_INVALID_QUERY")
        if subject in self.used or len(self.used) >= MAX_QUERIES:
            raise PermissionError("WSP120_REPLAY_OR_SOURCE_CAP")
        self.used.add(subject)
        answer = walk(tuple(dict(enumerate(row)) for row in self.__world.edges),
                      subject, self.__target)
        self.receipt.update(bytes((subject, answer)))
        return answer

    @property
    def count(self):
        return len(self.used)


def _gini(graph, candidates, subject):
    counts = Counter(walk(graph, subject, law) for law in candidates)
    n = sum(counts.values())
    return n*n - sum(v*v for v in counts.values())


class NumericGrow:
    """Bounded numeric synapses, with verified-evidence replay on structural growth."""
    def __init__(self, graph, *, active=True, grow=True, updates=True):
        self.graph = tuple(dict(g) for g in graph)
        self.active = bool(active)
        self.allow_growth = bool(grow)
        self.updates = bool(updates)
        self.grown = False
        self.programs = list(FIXED3)
        self.weights = array("i", [0]) * (2*len(self.programs))
        if self.weights.itemsize != 4:
            raise RuntimeError("WSP120_REQUIRES_INT32")
        self.observed = []
        self.seen = set()
        self.feedback_errors = 0

    def viable(self):
        return tuple(p for i, p in enumerate(self.programs)
                     if self.weights[2*i+1] == 0)

    def choose(self, pool):
        available = tuple(s for s in pool if s not in self.seen)
        if not available or len(self.observed) >= MAX_QUERIES:
            raise ValueError("WSP120_SOURCE_CAP_OR_EMPTY")
        if not self.active:
            return available[0]
        candidates = self.viable()
        if not candidates:
            # Fail-closed when graph incompleteness or unsupported law prevents recovery.
            return min(available)
        return max(sorted(available), key=lambda s: _gini(self.graph, candidates, s))

    def _apply(self, first_index, evidence):
        rejected = 0
        for i in range(first_index, len(self.programs)):
            predicted = walk(self.graph, evidence[0], self.programs[i])
            if predicted is None:
                continue
            j = 2*i + (0 if predicted == evidence[1] else 1)
            if self.weights[j] >= 2**31-2:
                raise OverflowError("WSP120_WEIGHT_OVERFLOW")
            if predicted != evidence[1] and self.weights[2*i+1] == 0:
                rejected += 1
            self.weights[j] += 1
        return rejected

    def observe(self, subject, outcome):
        if (type(subject) is not int or type(outcome) is not int
                or not 0 <= subject < N or not 0 <= outcome < N):
            raise ValueError("WSP120_REQUIRES_EXTERNAL_SOURCE_RESULT")
        if subject in self.seen or len(self.observed) >= MAX_QUERIES:
            raise ValueError("WSP120_DUPLICATE_OR_OVER_BUDGET")
        self.seen.add(subject)
        self.observed.append((subject, outcome))
        if not self.updates:
            return 0
        rejected = self._apply(0, (subject, outcome))
        self.feedback_errors += rejected
        if self.allow_growth and not self.grown and not self.viable():
            old_count = len(self.programs)
            self.programs.extend(NOVEL)
            if len(self.programs) > MAX_PROGRAMS:
                raise AssertionError("WSP120_PROPOSAL_CAP")
            self.weights.extend(array("i", [0]) * (2*len(NOVEL)))
            if len(self.weights)*4 > MAX_NUMERIC_BYTES:
                raise AssertionError("WSP120_NUMERIC_CAP")
            self.grown = True
            # Reconstruct new circuits exclusively from previously VERIFIED evidence.
            for evidence in self.observed:
                self.feedback_errors += self._apply(old_count, evidence)
        return rejected

    def law(self):
        possible = [(p, self.weights[2*i]) for i, p in enumerate(self.programs)
                    if self.weights[2*i+1] == 0]
        if len(possible) != 1 or possible[0][1] < 3:
            return None
        return possible[0][0]

    def infer(self, subject):
        law = self.law()
        return walk(self.graph, subject, law) if law is not None else None

    def snapshot(self):
        state = {
            "schema": SCHEMA, "graph_sha256": _graph_hash(self.graph),
            "active": self.active, "grow": self.allow_growth, "updates": self.updates,
            "grown": self.grown, "observed": self.observed, "weights": list(self.weights),
        }
        raw = json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
        return raw + b"\n" + sha256(raw).hexdigest().encode("ascii")

    @classmethod
    def restore(cls, graph, blob):
        if type(blob) is not bytes or b"\n" not in blob:
            raise ValueError("WSP120_BAD_COLD_SCHEMA")
        raw, sep, digest = blob.rpartition(b"\n")
        if not sep or sha256(raw).hexdigest().encode("ascii") != digest:
            raise ValueError("WSP120_COLD_TAMPER")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError):
            raise ValueError("WSP120_BAD_COLD_JSON") from None
        if (data.get("schema") != SCHEMA or
                data.get("graph_sha256") != _graph_hash(graph)):
            raise ValueError("WSP120_COLD_WRONG_GRAPH_OR_SCHEMA")
        if any(type(data.get(k)) is not bool for k in ("active", "grow", "updates", "grown")):
            raise ValueError("WSP120_COLD_INVALID_MODES")
        learner = cls(graph, active=data["active"], grow=data["grow"],
                      updates=data["updates"])
        if data["grown"]:
            if not learner.allow_growth or not learner.updates:
                raise ValueError("WSP120_INVALID_EXPANSION_STATE")
            learner.programs.extend(NOVEL)
            learner.grown = True
        saved = data.get("weights")
        observations = data.get("observed")
        if (type(saved) is not list or len(saved) != 2*len(learner.programs)
                or not all(type(w) is int and 0 <= w <= MAX_QUERIES for w in saved)
                or type(observations) is not list or len(observations) > MAX_QUERIES):
            raise ValueError("WSP120_COLD_INVALID_SIZES")
        for item in observations:
            if (type(item) is not list or len(item) != 2
                    or any(type(v) is not int or not 0 <= v < N for v in item)):
                raise ValueError("WSP120_COLD_INVALID_EVIDENCE")
        if len(set(item[0] for item in observations)) != len(observations):
            raise ValueError("WSP120_COLD_DUPLICATE_EVIDENCE")
        learner.observed = [tuple(pair) for pair in observations]
        learner.seen = {s for s, _ in learner.observed}
        learner.weights = array("i", saved)
        # Fail closed on valid-hash malicious changes: counters must recompute
        # exactly from the externally supplied verified observation ledger.
        expected = cls(graph, active=learner.active, grow=learner.allow_growth,
                       updates=learner.updates)
        for s, y in learner.observed:
            expected.observe(s, y)
        if expected.grown != learner.grown or list(expected.weights) != saved:
            raise ValueError("WSP120_COLD_COUNTER_PROVENANCE")
        return learner


def _graph_hash(graph):
    pairs = [[sorted((int(k), int(v)) for k, v in g.items())] for g in graph]
    return sha256(json.dumps(pairs, separators=(",", ":")).encode()).hexdigest()


class SymbolicGrow:
    """Independent exact symbolic control. It does NOT reuse numeric synapses."""
    def __init__(self, graph):
        self.graph = tuple(dict(g) for g in graph)
        self.hypotheses = set(GRAMMAR)
        self.history = []
        self.seen = set()

    def choose(self, pool):
        remaining = tuple(s for s in pool if s not in self.seen)
        if not remaining or len(self.history) >= MAX_QUERIES:
            raise ValueError("WSP120_SYMBOLIC_SOURCE_CAP")
        choices = tuple(sorted(self.hypotheses))
        return max(sorted(remaining), key=lambda s: _gini(self.graph, choices, s))

    def observe(self, subject, actual):
        if (subject in self.seen or len(self.history) >= MAX_QUERIES
                or type(subject) is not int or type(actual) is not int
                or not 0 <= subject < N or not 0 <= actual < N):
            raise ValueError("WSP120_SYMBOLIC_BAD_PUBLIC_OBSERVATION")
        self.seen.add(subject)
        self.history.append((subject, actual))
        self.hypotheses = {p for p in self.hypotheses
                           if walk(self.graph, subject, p) in (None, actual)}

    def law(self):
        if len(self.hypotheses) != 1 or len(self.history) < 3:
            return None
        p = next(iter(self.hypotheses))
        if sum(walk(self.graph, s, p) == y for s, y in self.history) < 3:
            return None
        return p

    def infer(self, subject):
        law = self.law()
        return walk(self.graph, subject, law) if law is not None else None
