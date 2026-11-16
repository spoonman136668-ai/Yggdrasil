"""Independent WSP-121 *engineering-only* source and held-score custodian.

No import from a learner, reducer or WSP-120 implementation. Neither this
module nor its public view implements or opens the sealed primary source.
The engineering gate here is public development code, NOT confidential science.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import random

SCHEMA = "wsp121.independent-engineering-custody.v1"
N, RELATIONS = 64, 6
ENGINEERING = frozenset(range(121900, 121904))
PRIMARY = frozenset(range(121000, 121048))
PROTECTED = frozenset(range(121800, 121864)) | frozenset(range(120800, 120864))
# Separate engineering demonstration law; no relationship to original truth tables.
_DEMO_GATE = sha256(b"wsp121-independent-engineering-demo-gate-v1").digest()[0]


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _hash(value):
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


def _require_subject(subject):
    if type(subject) is not int or not 0 <= subject < N:
        raise ValueError("WSP121_CUSTODY_INVALID_SUBJECT")


@dataclass(frozen=True)
class PublicView:
    """Only graph and membership; never carries the hidden engineering gate."""
    seed: int
    graph: tuple[tuple[int, ...], ...]
    legal: tuple[int, ...]
    held: tuple[int, ...]

    def feature(self, subject):
        _require_subject(subject)
        return ((subject & 1)
                | ((self.graph[0][subject] & 1) << 1)
                | ((self.graph[2][subject] & 1) << 2))

    def routes(self, subject):
        _require_subject(subject)
        return (self.graph[1][self.graph[0][subject]],
                self.graph[3][self.graph[2][subject]])

    def fingerprint(self):
        return _hash({"seed": self.seed, "graph": self.graph,
                      "legal": self.legal, "held": self.held})


def _construct_engineering_view(seed):
    """Disjoint public graph and legal/held split, independently of learner."""
    if type(seed) is not int or seed not in ENGINEERING:
        raise PermissionError("WSP121_CUSTODY_ENGINEERING_ONLY")
    for attempt in range(1024):
        rng = random.Random((seed << 8) + attempt)
        graph = tuple(tuple(rng.sample(range(N), N))
                      for _ in range(RELATIONS))
        # Candidate checks do NOT use an oracle or hidden outcome.
        def context(s):
            return ((s & 1) | ((graph[0][s] & 1) << 1)
                    | ((graph[2][s] & 1) << 2))
        if any(graph[1][graph[0][s]] == graph[3][graph[2][s]]
               for s in range(N)):
            continue
        groups = [[s for s in range(N) if context(s) == k]
                  for k in range(8)]
        if any(len(group) < 3 for group in groups):
            continue
        for group in groups:
            rng.shuffle(group)
        first = [group.pop() for group in groups]
        remainder = [s for group in groups for s in group]
        rng.shuffle(remainder)
        order = tuple(first + remainder)
        return PublicView(seed, graph, order[:40], order[40:])
    raise RuntimeError("WSP121_CUSTODY_GRAPH_REJECTION_EXHAUSTED")


class EngineeringCustodian:
    """One bounded oracle transcript and one full held-set scoring receipt.

    Not a security boundary against a reader of this development source code.
    A real primary cohort requires an external owner and sealed oracle.
    """
    def __init__(self, seed):
        # Validate BEFORE construction, ensuring primary/protected IDs never
        # reach random graph construction, even through malformed types.
        if type(seed) is not int or seed not in ENGINEERING:
            raise PermissionError("WSP121_CUSTODY_FIRST_USE_DENIED")
        self._public = _construct_engineering_view(seed)
        self._budget = 8 if seed in (121900, 121901) else 4
        self._observed: dict[int, int] = {}
        self._transcript: list[list[int]] = []
        self._scored = False

    @property
    def public(self):
        return self._public

    @property
    def budget(self):
        return self._budget

    @property
    def count(self):
        return len(self._observed)

    @property
    def source_sha256(self):
        return _hash({"seed": self._public.seed,
                      "public_sha256": self._public.fingerprint(),
                      "observations": self._transcript})

    def _answer(self, subject):
        feature = self._public.feature(subject)
        route = (_DEMO_GATE >> feature) & 1
        return self._public.routes(subject)[route]

    def query(self, subject):
        _require_subject(subject)
        if (self._scored or subject not in self._public.legal
                or subject in self._observed or self.count >= self._budget):
            raise PermissionError("WSP121_CUSTODY_WITHHELD_DUPLICATE_OR_CAP")
        answer = self._answer(subject)
        self._observed[subject] = answer
        self._transcript.append([subject, answer])
        return answer

    def score_held_once(self, predictions):
        """One aggregate report, no withheld labels or per-subject feedback."""
        if self._scored or self.count != self._budget:
            raise PermissionError("WSP121_CUSTODY_SCORE_NOT_READY_OR_REUSED")
        if type(predictions) is not dict or (set(predictions) !=
                set(self._public.held)) or len(predictions) != 24:
            raise ValueError("WSP121_CUSTODY_HELD_SET_MISMATCH")
        if any(value is not None and (type(value) is not int
                                     or not 0 <= value < N)
               for value in predictions.values()):
            raise ValueError("WSP121_CUSTODY_BAD_PREDICTION")
        ordered = [[s, predictions[s]] for s in sorted(self._public.held)]
        correct = sum(predictions[s] == self._answer(s)
                      for s in self._public.held
                      if predictions[s] is not None)
        abstained = sum(predictions[s] is None for s in self._public.held)
        self._scored = True
        return {
            "schema": SCHEMA,
            "seed": self._public.seed,
            "budget": self._budget,
            "source_calls": self.count,
            "public_sha256": self._public.fingerprint(),
            "source_sha256": self.source_sha256,
            "held_predictions_sha256": _hash(ordered),
            "held": len(self._public.held),
            "correct": correct,
            "wrong_confident": len(self._public.held) - correct - abstained,
            "abstained": abstained,
            "scientific_pass": False,
            "source_first_use": False,
            "native_admission": False,
        }


def open_original(seed):
    """Fail closed even for legitimate primary seed. No bypass/authorization flag."""
    raise PermissionError("WSP121_PRIMARY_SOURCE_NOT_INSTALLED")
