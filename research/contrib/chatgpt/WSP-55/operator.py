"""WSP55: prospective, source-blind noncommuting affine operator compiler.

Engineering probe only. Input is the public action-consequence observation stream;
never import source.py, source operator tables, oracle lexical roles, or phase labels.
Uses an explicitly declared, restrictive modular-affine hypothesis class.
All ambiguous, exhausted, or contradictory models abstain.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
import json

from compiler import GradientlessCausalCompiler, grounded_entity, splits, validate_raw, validate_state, prefix_compatible

MAX_NODES = 300000
MAX_MODELS = 512
MAX_SNAPSHOT = 3000000
AFFINE = tuple(product(range(7), repeat=2))


def compact(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def step(x, coeff):
    return (coeff[0] * x + coeff[1]) % 7


def parse(row, entity_map, e_slot, first_slot, words):
    """All candidate raw parsings, rejecting ungrounded or ambiguous entity changes."""
    b, raw, after = row
    changed = grounded_entity(b, after)
    other = 3 - e_slot - first_slot
    out = set()
    for parts in splits(raw):
        eword = parts[e_slot]
        if eword not in entity_map:
            continue
        e = entity_map[eword]
        if changed is not None and changed != e:
            continue
        if any(b[j] != after[j] for j in range(8) if j != e):
            continue
        w1, w2 = parts[first_slot], parts[other]
        if w1 not in words or w2 not in words or w1 == w2:
            continue
        out.add((e, w1, w2))
    return out


class SearchExceeded(Exception):
    pass


class NoncommutingCompiler:
    """Construct candidate op functions and order from raw physical evidence.

    A/B training block sizes follow the prospective source protocol (48 + 12).
    No prediction method accepts a phase label. The most recent charged evidence
    is used to filter all surviving A/B role assignments; irreducible ambiguity
    leads to abstention. The action-count boundary remains an explicit limitation.
    """
    gradient_steps = 0

    def __init__(self):
        self.rows = []
        self.a_models = []
        self.b_models = []
        self.nodes = 0
        self.incomplete = False

    def _tick(self):
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise SearchExceeded("WSP55 search budget exceeded")

    def observe(self, row):
        if len(self.rows) >= 60:
            raise ValueError("60-action ceiling")
        before = validate_state(row.before, "noncommuting_order")
        after = validate_state(row.after, "noncommuting_order")
        raw = validate_raw(row.acoustic_bits)
        if type(row.action_cost) is not int or row.action_cost != 1 or type(row.reset_cost) is not int or row.reset_cost != 0:
            raise ValueError("incorrect action/reset charge")
        self.rows.append((before, raw, after))
        if len(self.rows) == 48:
            self._fit_a()
        if len(self.rows) == 60:
            self._fit_b()

    @staticmethod
    def _compatible(c1, c2, examples):
        return all(step(step(x, c1), c2) == y for x, y in examples)

    def _solve(self, edges, words):
        # AC-3-style bounded constraint propagation on the 49-function library.
        # The four operation codes share their coefficients across all entities.
        domains = {w: tuple(AFFINE) for w in words}
        pairs = sorted(edges)
        supports = {}
        for u, v in pairs:
            self._tick()
            examples = edges[(u, v)]
            supports[(u, v)] = {
                (a, b) for a in AFFINE for b in AFFINE
                if self._compatible(a, b, examples)
            }
            if not supports[(u, v)]:
                return []

        answers = []

        def restrict(d):
            while True:
                changed = False
                for u, v in pairs:
                    legal = supports[(u, v)]
                    du = tuple(a for a in d[u] if any((a, b) in legal for b in d[v]))
                    dv = tuple(b for b in d[v] if any((a, b) in legal for a in du))
                    if not du or not dv:
                        return None
                    if len(du) < len(d[u]) or len(dv) < len(d[v]):
                        changed = True
                        d[u], d[v] = du, dv
                if not changed:
                    return d

        def dfs(d):
            self._tick()
            d = restrict(d)
            if d is None:
                return
            if all(len(v) == 1 for v in d.values()):
                answers.append({w: list(d[w][0]) for w in words})
                if len(answers) > MAX_MODELS:
                    raise SearchExceeded("operator-function hypothesis cap")
                return
            w = min((w for w in words if len(d[w]) > 1), key=lambda k: (len(d[k]), k))
            for x in d[w]:
                child = dict(d)
                child[w] = (x,)
                dfs(child)

        dfs(domains)
        return answers

    def _fit_a(self):
        # Reuse only WSP54's public-data lexical-candidate enumerator; none of
        # its anchored physical effect rules or phase/oracle information.
        lexical = GradientlessCausalCompiler(family="noncommuting_order")
        lexical.a = self.rows[:48]
        models = []
        try:
            for e_slot in range(3):
                for entity_map in lexical._entity_options(lexical.a, e_slot):
                    for first_slot in range(3):
                        if first_slot == e_slot:
                            continue
                        second_slot = 3 - e_slot - first_slot
                        counts = Counter()
                        for before, raw, after in self.rows[:48]:
                            changed = grounded_entity(before, after)
                            candidates = set()
                            for p in splits(raw):
                                if p[e_slot] not in entity_map:
                                    continue
                                if changed is not None and entity_map[p[e_slot]] != changed:
                                    continue
                                candidates.update((p[first_slot], p[second_slot]))
                            counts.update(candidates)
                        ordered = [
                            w for w, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
                            if n >= 3 and prefix_compatible(w, tuple(entity_map))
                        ][:8]
                        for candidate_words in combinations(ordered, 4):
                            self._tick()
                            if any(not prefix_compatible(w, candidate_words[:i])
                                   for i, w in enumerate(candidate_words)):
                                continue
                            vocabulary = set(candidate_words)
                            edges = defaultdict(list)
                            used = set()
                            for row in self.rows[:48]:
                                choices = parse(row, entity_map, e_slot, first_slot, vocabulary)
                                if len(choices) != 1:
                                    break
                                e, w1, w2 = next(iter(choices))
                                used.update((w1, w2))
                                edges[(w1, w2)].append((row[0][e], row[2][e]))
                            else:
                                if len(used) != 4:
                                    continue
                                for mapping in self._solve(edges, tuple(sorted(vocabulary))):
                                    models.append({
                                        "entity_map": dict(entity_map),
                                        "e_slot": e_slot, "first_slot": first_slot,
                                        "functions": mapping
                                    })
                                    if len(models) > MAX_MODELS:
                                        raise SearchExceeded("model count cap")
            self.nodes += lexical.nodes
            if self.nodes > MAX_NODES:
                raise SearchExceeded("lexical search budget")
            self.a_models = models
        except SearchExceeded:
            self.incomplete = True
            self.a_models = []
            self.b_models = []

    @staticmethod
    def _infer(before, raw, h):
        try:
            raw_parts = splits(raw)
        except ValueError:
            return None
        e_slot, first_slot = h["e_slot"], h["first_slot"]
        other_slot = 3 - e_slot - first_slot
        answers = set()
        for p in raw_parts:
            if p[e_slot] not in h["entity_map"]:
                continue
            if p[first_slot] not in h["functions"] or p[other_slot] not in h["functions"]:
                continue
            e = h["entity_map"][p[e_slot]]
            out = list(before)
            out[e] = step(step(before[e], h["functions"][p[first_slot]]),
                          h["functions"][p[other_slot]])
            answers.add(tuple(out))
        return next(iter(answers)) if len(answers) == 1 else None

    def _fit_b(self):
        if self.incomplete or not self.a_models:
            return
        try:
            candidates = []
            for h in self.a_models:
                for es in range(3):
                    for fs in range(3):
                        if fs == es:
                            continue
                        self._tick()
                        b = {**h, "e_slot": es, "first_slot": fs}
                        if all(self._infer(before, raw, b) == after
                               for before, raw, after in self.rows[48:60]):
                            candidates.append(b)
                            if len(candidates) > MAX_MODELS:
                                raise SearchExceeded("phase B model cap")
            self.b_models = candidates
        except SearchExceeded:
            self.incomplete = True
            self.a_models = []
            self.b_models = []

    def predict(self, before, raw):
        """Phase-free consensus over hypotheses compatible with recent consequences."""
        before = validate_state(before, "noncommuting_order")
        raw = validate_raw(raw)
        if self.incomplete or len(self.rows) < 48:
            return None
        if len(self.rows) < 60:
            models = self.a_models
        else:
            # A and B are not selected by an evaluator-provided phase marker.
            # Compare both assignments to last 12 physically observed B actions.
            models = [
                h for h in self.a_models + self.b_models
                if all(self._infer(b, s, h) == a for b, s, a in self.rows[-12:])
            ]
        if not models:
            return None
        predictions = {self._infer(before, raw, h) for h in models}
        return next(iter(predictions)) if len(predictions) == 1 else None

    def snapshot(self):
        body = {
            "schema": "wsp55.operator.v1",
            "rows": [[list(b), s, list(a)] for b, s, a in self.rows],
            "a_models": self.a_models, "b_models": self.b_models,
            "nodes": self.nodes, "incomplete": self.incomplete
        }
        raw = compact(body)
        if len(raw) > MAX_SNAPSHOT:
            raise OverflowError("snapshot exceeds budget")
        return compact({"payload": body, "sha256": sha256(raw.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls, text):
        if type(text) is not str or len(text) > MAX_SNAPSHOT + 1000:
            raise ValueError("invalid snapshot size")
        try:
            wrapper = json.loads(text)
            if type(wrapper) is not dict or set(wrapper) != {"payload", "sha256"}:
                raise ValueError("invalid envelope")
            payload = wrapper["payload"]
            if type(payload) is not dict or payload["schema"] != "wsp55.operator.v1":
                raise ValueError("invalid schema")
            if sha256(compact(payload).encode("ascii")).hexdigest() != wrapper["sha256"]:
                raise ValueError("snapshot hash mismatch")
            obj = cls()
            if type(payload["rows"]) is not list or len(payload["rows"]) > 60:
                raise ValueError("invalid rows")
            for b, bits, a in payload["rows"]:
                class Row:
                    pass
                row = Row()
                row.before, row.acoustic_bits, row.after = tuple(b), bits, tuple(a)
                row.action_cost, row.reset_cost = 1, 0
                obj.observe(row)
            if obj.snapshot() != text:
                raise ValueError("noncanonical or inconsistent evidence")
            return obj
        except (TypeError, KeyError, IndexError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("malformed snapshot") from exc

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8
