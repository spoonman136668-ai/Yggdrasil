"""WSP57 source-blind sparse permutation constraint learner.

Only public charged unary/pair action-consequence observations are accepted.
Unknown operator functions are inferred from evidence as candidate 7-state
permutations; no generator import, true table/grammar, gradients, tokens,
pretrained representations, or oracle intervention choice.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from itertools import permutations
from math import log2
import json

ALL_OPS = (0, 1, 2, 3)
STATES = tuple(range(7))
UNARY_INPUTS = (0, 2, 4)
ALL_QUERIES = tuple((i, j, x) for i in ALL_OPS for j in ALL_OPS
                    if i != j for x in STATES)
MAX_ACTIONS = 36
MAX_SNAPSHOT_BYTES = 1000000
MAX_SEARCH_CHECKS = 20000000


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class SparsePermutationWriter:
    gradient_steps = 0

    def __init__(self):
        self.rows = []
        self.unary = {i: {} for i in ALL_OPS}
        self.pairs = []
        self.domains = {i: () for i in ALL_OPS}
        self.total_checks = 0
        self.incomplete = False

    def observe(self, row):
        if len(self.rows) >= MAX_ACTIONS:
            raise ValueError("charged action ceiling")
        if (row.kind not in ("unary", "pair") or type(row.first) is not int
                or row.first not in ALL_OPS or type(row.before) is not int
                or row.before not in STATES or type(row.after) is not int
                or row.after not in STATES or type(row.action_cost) is not int
                or row.action_cost != 1):
            raise ValueError("invalid physical observation")
        if row.kind == "unary":
            if row.second is not None or row.before not in UNARY_INPUTS or self.pairs:
                raise ValueError("bad or late unary intervention")
            if row.before in self.unary[row.first]:
                raise ValueError("duplicate unary input")
            if len(self.rows) >= 12:
                raise ValueError("exceeded unary probe budget")
            self.unary[row.first][row.before] = row.after
        else:
            if (type(row.second) is not int or row.second not in ALL_OPS
                    or row.second == row.first or len(self.rows) < 12 or
                    len(self.pairs) >= 24 or
                    (row.first, row.second, row.before) in
                    {(a, b, x) for a, b, x, y in self.pairs}):
                raise ValueError("invalid or duplicate pair intervention")
            self.pairs.append((row.first, row.second, row.before, row.after))
        self.rows.append((row.kind, row.first, row.second, row.before, row.after, row.action_cost))
        if len(self.rows) >= 12:
            self._rebuild()

    def _rebuild(self):
        if any(set(self.unary[i]) != set(UNARY_INPUTS) for i in ALL_OPS):
            self.incomplete = True
            self.domains = {i: () for i in ALL_OPS}
            return
        d = {}
        for i in ALL_OPS:
            d[i] = tuple(p for p in permutations(STATES)
                         if all(p[x] == y for x, y in self.unary[i].items()))
        if any(not d[i] for i in ALL_OPS):
            self.incomplete = True
            self.domains = {i: () for i in ALL_OPS}
            return
        checks = 0
        for _ in range(100):
            changed = False
            for i, j, x, y in self.pairs:
                before_i = d[i]
                before_j = d[j]
                allowed_i = []
                for fi in before_i:
                    if any(fj[fi[x]] == y for fj in before_j):
                        allowed_i.append(fi)
                    checks += len(before_j)
                allowed_j = []
                for fj in before_j:
                    if any(fj[fi[x]] == y for fi in allowed_i):
                        allowed_j.append(fj)
                    checks += len(allowed_i)
                if not allowed_i or not allowed_j or checks > MAX_SEARCH_CHECKS:
                    self.incomplete = True
                    self.domains = {k: () for k in ALL_OPS}
                    self.total_checks += checks
                    return
                if len(allowed_i) < len(before_i):
                    d[i] = tuple(allowed_i)
                    changed = True
                if len(allowed_j) < len(before_j):
                    d[j] = tuple(allowed_j)
                    changed = True
            if not changed:
                break
        else:
            self.incomplete = True
            self.domains = {i: () for i in ALL_OPS}
            self.total_checks += checks
            return
        self.total_checks += checks
        self.domains = d

    def _outcome_counts(self, i, j, x):
        if self.incomplete or not all(self.domains[k] for k in ALL_OPS):
            return Counter()
        relevant = [(a, b, v, y) for a, b, v, y in self.pairs
                    if a == i and b == j]
        counts = Counter()
        for fi in self.domains[i]:
            for fj in self.domains[j]:
                if all(fj[fi[v]] == y for _, _, v, y in relevant):
                    counts[fj[fi[x]]] += 1
        return counts

    def predict(self, first, second, before):
        if (type(first) is not int or type(second) is not int or
                type(before) is not int or (first, second, before) not in ALL_QUERIES):
            raise ValueError("invalid physical query")
        candidates = self._outcome_counts(first, second, before)
        return next(iter(candidates)) if len(candidates) == 1 else None

    def available_actions(self):
        seen = {(i, j, x) for i, j, x, y in self.pairs}
        return tuple(q for q in ALL_QUERIES if q not in seen)

    def select_active(self):
        """Maximize predicted information gain on the current candidate set."""
        if len(self.rows) < 12 or len(self.pairs) >= 24 or self.incomplete:
            raise ValueError("active query unavailable")
        best = None
        best_score = float("-inf")
        for query in self.available_actions():
            counts = self._outcome_counts(*query)
            total = sum(counts.values())
            if total == 0:
                continue
            entropy = -sum((n / total) * log2(n / total) for n in counts.values())
            if entropy > best_score + 1e-12:
                best_score = entropy
                best = query
        if best is None:
            raise ValueError("no informative query")
        return best

    def snapshot(self):
        data = {
            "schema": "wsp57.sparse-writer.v1",
            "rows": [list(row) for row in self.rows],
            "domains": {str(i): [list(p) for p in self.domains[i]]
                        for i in ALL_OPS},
            "incomplete": self.incomplete, "total_checks": self.total_checks,
            "gradient_steps": self.gradient_steps
        }
        content = canonical(data)
        packed = canonical({"payload": data, "sha256": sha256(content.encode("ascii")).hexdigest()})
        if len(packed.encode("ascii")) > MAX_SNAPSHOT_BYTES:
            raise OverflowError("snapshot capacity")
        return packed

    @classmethod
    def restore(cls, text):
        if type(text) is not str or len(text) > MAX_SNAPSHOT_BYTES:
            raise ValueError("invalid snapshot")
        try:
            env = json.loads(text)
            if type(env) is not dict or set(env) != {"payload", "sha256"}:
                raise ValueError("invalid envelope")
            data = env["payload"]
            if data.get("schema") != "wsp57.sparse-writer.v1" or (
                sha256(canonical(data).encode("ascii")).hexdigest() != env["sha256"]
            ):
                raise ValueError("invalid source or hash")
            if type(data["rows"]) is not list or len(data["rows"]) > MAX_ACTIONS:
                raise ValueError("invalid action ledger")
            obj = cls()
            for row in data["rows"]:
                if type(row) is not list or len(row) != 6:
                    raise ValueError("invalid row")
                class PublicRow:
                    pass
                x = PublicRow()
                x.kind, x.first, x.second, x.before, x.after, x.action_cost = row
                obj.observe(x)
            if obj.snapshot() != text:
                raise ValueError("noncanonical or inconsistent snapshot")
            return obj
        except (TypeError, KeyError, IndexError, UnicodeError, json.JSONDecodeError) as e:
            raise ValueError("malformed snapshot") from e

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8

    def hypothesis_counts(self):
        return tuple(len(self.domains[i]) for i in ALL_OPS)
