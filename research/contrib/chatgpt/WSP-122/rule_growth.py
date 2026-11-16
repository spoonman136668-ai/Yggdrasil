"""WSP-122: source-safe direct rule programming with dynamic interaction growth.

Synthetic engineering fixtures only. Monomial features and GF(2) elimination
are supplied inductive biases, NOT invention of arbitrary primitives.
No original science, external source authority, or native Yggdrasil mutation.
"""
from __future__ import annotations
from array import array
from dataclasses import dataclass
from hashlib import sha256
import json
import random

SCHEMA = "wsp122.weight-programmed-rule-memory.v1"
ENGINEERING = frozenset(range(122900, 122904))
CONTEXTS = 16


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def _terms(degree):
    return tuple(sorted((m for m in range(16) if m.bit_count() <= degree),
                        key=lambda m: (m.bit_count(), m)))


def _features(context, terms):
    return sum(1 << i for i, mask in enumerate(terms) if context & mask == mask)


def _linear_system(samples, degree):
    terms, pivots = _terms(degree), {}
    for context, label in samples:
        vector, rhs = _features(context, terms), label
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (vector, rhs)
                break
            base, value = pivots[pivot]
            vector ^= base
            rhs ^= value
        else:
            if rhs:
                return None
    coefficients = 0
    for pivot in sorted(pivots):
        vector, rhs = pivots[pivot]
        rhs ^= (vector & coefficients).bit_count() & 1
        coefficients |= rhs << pivot
    for context, label in samples:
        if (_features(context, terms) & coefficients).bit_count() % 2 != label:
            raise AssertionError("WSP122_SOLVER_INTEGRITY")
    return terms, pivots, coefficients


def _prediction(system, context):
    if type(context) is not int or not 0 <= context < CONTEXTS:
        raise ValueError("WSP122_BAD_CONTEXT")
    if system is None:
        return None
    terms, pivots, _ = system
    vector, result = _features(context, terms), 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in pivots:
            return None
        row, rhs = pivots[pivot]
        vector ^= row
        result ^= rhs
    return result


@dataclass(frozen=True)
class PublicWorld:
    seed: int
    subjects: tuple
    contexts: tuple
    legal: tuple
    held: tuple

    def feature(self, subject):
        if type(subject) is not int or subject not in self.subjects:
            raise ValueError("WSP122_UNKNOWN_SUBJECT")
        return self.contexts[self.subjects.index(subject)]


def engineering_world(seed):
    if type(seed) is not int or seed not in ENGINEERING:
        raise PermissionError("WSP122_ORIGINAL_OR_PROTECTED_SOURCE_DENIED")
    rng = random.Random(seed)
    subjects = tuple(rng.sample(range(1000, 20000), CONTEXTS))
    contexts = list(range(CONTEXTS))
    rng.shuffle(contexts)
    order = list(subjects)
    rng.shuffle(order)
    return PublicWorld(seed, subjects, tuple(contexts),
                       tuple(order[:12]), tuple(order[12:]))


def original_world(seed):
    raise PermissionError("WSP122_ORIGINAL_FIRST_USE_DENIED")


def _engineering_law(context):
    # Public synthetic engineering law, NOT independently hidden science.
    return (context & 1) ^ (((context >> 1) & 1) & ((context >> 2) & 1))


@dataclass(frozen=True)
class VerifiedObservation:
    seed: int
    subject: int
    context: int
    outcome: int
    source_sha256: str


class EngineeringSource:
    def __init__(self, world, budget):
        if type(world) is not PublicWorld or world.seed not in ENGINEERING:
            raise PermissionError("WSP122_ENGINEERING_SOURCE_ONLY")
        if type(budget) is not int or budget not in (4, 12):
            raise ValueError("WSP122_BAD_BUDGET")
        self.world, self.budget = world, budget
        self._events, self._used = [], set()

    def query(self, subject):
        if (type(subject) is not int or subject not in self.world.legal
                or subject in self._used or len(self._used) >= self.budget):
            raise PermissionError("WSP122_HELD_DUPLICATE_OR_BUDGET_DENIED")
        context = self.world.feature(subject)
        outcome = _engineering_law(context)
        self._used.add(subject)
        self._events.append([self.world.seed, subject, context, outcome])
        return VerifiedObservation(self.world.seed, subject, context,
                                   outcome, digest(self._events))

    @property
    def receipt(self):
        return digest(self._events)

    @property
    def count(self):
        return len(self._events)


class NumericRuleMemory:
    """Program int32 coefficients, allocating higher-degree terms on contradiction."""
    def __init__(self, *, allow_growth=True):
        self.allow_growth = allow_growth
        self.evidence, self._seen = [], set()
        self.degree, self.inconsistent = 1, False
        self.weights = array("i", [0] * 16)
        self._system = _linear_system([], 1)

    def _recompile(self):
        samples = [(row[2], row[3]) for row in self.evidence]
        self._system, self.inconsistent = None, False
        degrees = range(1, 5) if self.allow_growth else range(1, 2)
        for degree in degrees:
            fit = _linear_system(samples, degree)
            if fit is not None:
                self.degree, self._system = degree, fit
                break
        if self._system is None:
            self.inconsistent, self.degree = True, 1
        self.weights = array("i", [0] * 16)
        if self._system is not None:
            terms, _, coefficients = self._system
            for index, term in enumerate(terms):
                self.weights[term] = (coefficients >> index) & 1

    def observe(self, world, evidence):
        if (type(world) is not PublicWorld or world.seed not in ENGINEERING
                or type(evidence) is not VerifiedObservation
                or evidence.seed != world.seed
                or type(evidence.subject) is not int
                or evidence.subject not in world.legal
                or evidence.context != world.feature(evidence.subject)
                or type(evidence.outcome) is not int
                or evidence.outcome not in (0, 1)):
            raise ValueError("WSP122_UNVERIFIED_OBSERVATION")
        key = (evidence.seed, evidence.subject)
        if key in self._seen:
            raise ValueError("WSP122_DUPLICATE_EVIDENCE")
        if any(row[2] == evidence.context and row[3] != evidence.outcome
               for row in self.evidence):
            raise ValueError("WSP122_CAUSAL_CONTRADICTION")
        # A checksum is only syntactic provenance; no trusted-source signature.
        if (type(evidence.source_sha256) is not str
                or len(evidence.source_sha256) != 64
                or any(c not in "0123456789abcdef" for c in evidence.source_sha256)):
            raise ValueError("WSP122_BAD_SOURCE_RECEIPT")
        self.evidence.append([evidence.seed, evidence.subject,
                              evidence.context, evidence.outcome,
                              evidence.source_sha256])
        self._seen.add(key)
        self._recompile()

    def infer_context(self, context):
        return _prediction(self._system, context)

    def infer(self, world, subject):
        return self.infer_context(world.feature(subject))

    def select_query(self, world, available):
        # Public-uncertainty-based selection; no access to unrevealed outcome.
        valid = [s for s in available if s in world.legal
                 and (world.seed, s) not in self._seen]
        if not valid:
            return None
        return min(valid, key=lambda s: (self.infer(world, s) is not None,
                                         world.feature(s), s))

    def snapshot(self):
        body = {"schema": SCHEMA, "allow_growth": self.allow_growth,
                "evidence": self.evidence, "degree": self.degree,
                "inconsistent": self.inconsistent, "weights": list(self.weights)}
        return canonical({"payload": body, "sha256": digest(body)})

    @classmethod
    def restore(cls, snapshot):
        obj = json.loads(snapshot)
        body = obj["payload"]
        if body.get("schema") != SCHEMA or digest(body) != obj.get("sha256"):
            raise ValueError("WSP122_COLD_DIGEST_INVALID")
        if type(body.get("allow_growth")) is not bool:
            raise ValueError("WSP122_COLD_FORMAT_INVALID")
        restored = cls(allow_growth=body["allow_growth"])
        rows = body.get("evidence")
        if type(rows) is not list:
            raise ValueError("WSP122_COLD_FORMAT_INVALID")
        for row in rows:
            if (type(row) is not list or len(row) != 5
                    or any(type(v) is not int for v in row[:4])
                    or row[0] not in ENGINEERING or not 0 <= row[2] < 16
                    or row[3] not in (0, 1) or type(row[4]) is not str
                    or len(row[4]) != 64):
                raise ValueError("WSP122_COLD_HISTORY_INVALID")
            key = (row[0], row[1])
            if key in restored._seen or any(
                    prior[2] == row[2] and prior[3] != row[3]
                    for prior in restored.evidence):
                raise ValueError("WSP122_COLD_HISTORY_CONTRADICTORY")
            restored._seen.add(key)
            restored.evidence.append(row[:])
        restored._recompile()
        if (restored.degree != body.get("degree")
                or restored.inconsistent != body.get("inconsistent")
                or list(restored.weights) != body.get("weights")):
            raise ValueError("WSP122_COLD_WEIGHT_PROVENANCE")
        return restored


class SymbolicTable:
    """Optimized exact memorization control."""
    def __init__(self):
        self.table = {}

    def observe(self, world, evidence):
        context = world.feature(evidence.subject)
        if context in self.table and self.table[context] != evidence.outcome:
            raise ValueError("WSP122_SYMBOLIC_CONTRADICTION")
        self.table[context] = evidence.outcome

    def infer(self, world, subject):
        return self.table.get(world.feature(subject))


class SymbolicANF:
    """Independent symbolic polynomial comparator, low-pivot elimination."""
    def __init__(self):
        self.answers, self.degree = {}, 1

    def _equations(self, degree):
        masks = sorted((m for m in range(16) if m.bit_count() <= degree),
                       key=lambda m: (m.bit_count(), m))
        basis = {}
        for context, answer in sorted(self.answers.items()):
            row = 0
            for i, monomial in enumerate(masks):
                if context & monomial == monomial:
                    row |= 1 << i
            while row:
                pivot = (row & -row).bit_length() - 1
                if pivot not in basis:
                    basis[pivot] = (row, answer)
                    break
                p_row, p_answer = basis[pivot]
                row ^= p_row
                answer ^= p_answer
            else:
                if answer:
                    return None
        return masks, basis

    def observe(self, world, evidence):
        context = world.feature(evidence.subject)
        if context in self.answers and self.answers[context] != evidence.outcome:
            raise ValueError("WSP122_SYMBOLIC_ANF_CONTRADICTION")
        self.answers[context] = evidence.outcome
        for degree in range(1, 5):
            if self._equations(degree) is not None:
                self.degree = degree
                break
        else:
            raise AssertionError("WSP122_SYMBOLIC_ANF_INCONSISTENT")

    def infer(self, world, subject):
        masks, basis = self._equations(self.degree)
        context, row = world.feature(subject), 0
        for i, monomial in enumerate(masks):
            if context & monomial == monomial:
                row |= 1 << i
        answer = 0
        while row:
            pivot = (row & -row).bit_length() - 1
            if pivot not in basis:
                return None
            p_row, p_answer = basis[pivot]
            row ^= p_row
            answer ^= p_answer
        return answer


class NoUpdate:
    def observe(self, world, evidence):
        pass

    def infer(self, world, subject):
        return None


def engineering_fixture():
    """Pure synthetic fixture; never runs original science or native integration."""
    learners = {"NUMERIC_GROW": NumericRuleMemory(),
                "NUMERIC_AFFINE_FIXED": NumericRuleMemory(allow_growth=False),
                "SYMBOLIC_TABLE_STRONG": SymbolicTable(),
                "SYMBOLIC_ANF_STRONG": SymbolicANF(), "NO_UPDATE": NoUpdate()}
    worlds = []
    for index, seed in enumerate(sorted(ENGINEERING)):
        public = engineering_world(seed)
        budget = 12 if index == 0 else 4
        sources = {name: EngineeringSource(public, budget) for name in learners}
        remaining = set(public.legal)
        for _ in range(budget):
            selected = learners["NUMERIC_GROW"].select_query(public, remaining)
            if selected is None:
                raise AssertionError("WSP122_QUERY_EXHAUSTED")
            remaining.remove(selected)
            for name, learner in learners.items():
                observation = sources[name].query(selected)
                learner.observe(public, observation)
        if len({src.receipt for src in sources.values()}) != 1:
            raise AssertionError("WSP122_MISMATCHED_EVIDENCE")
        row = {"seed": seed, "budget": budget, "source_sha256":
               next(iter(sources.values())).receipt, "arms": {}}
        for name, learner in learners.items():
            predictions = [learner.infer(public, s) for s in public.held]
            truth = [_engineering_law(public.feature(s)) for s in public.held]
            correct = sum(p is not None and p == y for p, y in zip(predictions, truth))
            abstained = sum(p is None for p in predictions)
            row["arms"][name] = {"correct": correct,
                                 "wrong_confident": 4 - correct - abstained,
                                 "abstained": abstained}
        worlds.append(row)
    numeric = learners["NUMERIC_GROW"]
    cold = NumericRuleMemory.restore(numeric.snapshot())
    for seed in ENGINEERING:
        w = engineering_world(seed)
        if [numeric.infer(w, s) for s in w.held] != [
                cold.infer(w, s) for s in w.held]:
            raise AssertionError("WSP122_COLD_PREDICTION_DRIFT")
    return {"schema": "wsp122.engineering-fixture.v1", "source_first_use": False,
            "scientific_pass": False, "native_admission": False, "worlds": worlds,
            "numeric_degree": numeric.degree,
            "numeric_slot_bytes": 4 * len(numeric.weights),
            "numeric_evidence_rows": len(numeric.evidence), "cold_ok": True,
            "symbolic_strong_control_included": True,
            "symbolic_anf_matches_numeric": all(
                row["arms"]["NUMERIC_GROW"] == row["arms"]["SYMBOLIC_ANF_STRONG"]
                for row in worlds)}
