"""WSP52 constructive raw-acoustic address learning: exploratory SELFTEST only.

The sole gradient target is an entity whose physical location visibly changed.
A 64-step learner assigns raw *overlapping substring evidence* to entities.
It subsequently routes observed consequences into sparse numeric weights.
No oracle words, token IDs, true role/grammar, heldout answers or hidden source
properties enter the learner. Supplying commutative effect keys is an explicit
prior and therefore this is NOT general syntax acquisition.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math

from direct_writer import _canonical, _parts, _validate_state

STEPS = 64
RATE = 0.35
MIN_MARGIN = 0.004
MIN_SUPPORT = 2


def _observable(row):
    _validate_state(row.before)
    _validate_state(row.after)
    if (type(row.action_cost) is not int or row.action_cost != 1 or
            type(row.reset_cost) is not int or row.reset_cost != 0):
        raise ValueError("invalid action accounting")
    splits = _parts(row.acoustic_bits)
    if not splits:
        raise ValueError("uninterpretable raw acoustic length")
    changed = [i for i, (a, b) in enumerate(zip(row.before, row.after)) if a != b]
    if len(changed) > 1:
        raise ValueError("more than one physical location changed")
    return splits, (changed[0], row.after[changed[0]]) if changed else None


def _features(bits):
    """Bag of undecided 4..6-bit windows over all legal stream partitions."""
    splits = _parts(bits)
    if not splits:
        raise ValueError("no legal segmentation")
    counter = Counter(w for words in splits for w in words)
    denom = sum(counter.values())
    return {w: n / denom for w, n in counter.items()}


class ConstructiveAddressWriter:
    """Gradient-trained raw-address map, followed by numerical consequence writes.

    This is an independently tracked *successor diagnostic*, not the frozen
    preregistered WSP52 minimal-train-then-direct arm. It supplies symmetric
    effect-pair addressing and does not claim to discover physical commutativity.
    """
    def __init__(self, *, steps=STEPS):
        if type(steps) is not int or steps not in (0, STEPS):
            raise ValueError("only frozen 0-step ablation or 64-step candidate")
        self.steps = steps
        self.gradient_steps = 0
        self.a, self.b = [], []
        self.sealed = self.finalized = False
        self.phase = "A"
        self.coefficients = {}
        self.support = defaultdict(Counter)
        self.entity_numeric = defaultdict(Counter)
        self.effect_numeric = defaultdict(Counter)
        self.seen = {}
        self.conflicts = set()
        self.gradient_operations = 0
        self.write_candidates = 0

    def observe(self, row):
        splits, consequence = _observable(row)
        if self.finalized:
            raise ValueError("closed observation stage")
        target = self.b if self.sealed else self.a
        if len(target) >= (6 if self.sealed else 36):
            raise ValueError("experience limit exceeded")
        key = (_canonical(row.before), row.acoustic_bits)
        if key in self.seen and self.seen[key] != row.after:
            self.conflicts.add(key)
        self.seen[key] = row.after
        target.append(row)
        if consequence is not None:
            entity, _ = consequence
            for word in set(w for parts in splits for w in parts):
                self.support[word][entity] += 1
        if self.sealed:
            self._write(row, splits, consequence)

    def _learn(self):
        informative = [(r, consequence[0]) for r in self.a
                       if (consequence := _observable(r)[1]) is not None]
        if not informative:
            return
        features = [(list(_features(r.acoustic_bits).items()), entity)
                    for r, entity in informative]
        for iteration in range(self.steps):
            feat, label = features[iteration % len(features)]
            scores = [sum(self.coefficients.setdefault(word, [0.0] * 8)[i] * value
                          for word, value in feat) for i in range(8)]
            high = max(scores)
            exp = [math.exp(x - high) for x in scores]
            total = sum(exp)
            for word, value in feat:
                params = self.coefficients[word]
                for i in range(8):
                    params[i] += RATE * value * ((1 if i == label else 0) - exp[i] / total)
                    self.gradient_operations += 1
            self.gradient_steps += 1

    def _entity_score(self, word, entity):
        params = self.coefficients.get(word)
        counts = self.support.get(word, {})
        if (params is None or counts.get(entity, 0) < MIN_SUPPORT or
                sum(counts.values()) != counts[entity]):
            return None
        rival = max(params[i] for i in range(8) if i != entity)
        margin = params[entity] - rival
        return margin if margin >= MIN_MARGIN else None

    def _write(self, row, splits, consequence):
        if consequence is None:
            return
        entity, effect = consequence
        candidate_words = set(w for split in splits for w in split)
        scores = sorted(((margin, w) for w in candidate_words
                         if (margin := self._entity_score(w, entity)) is not None),
                        reverse=True)
        self.write_candidates += len(scores)
        if not scores:
            return
        # Pick the most strongly grounded raw address. The gradient chooses
        # WHICH numerical associations to write; it does not predict an answer.
        winner_score, word = scores[0]
        if len(scores) > 1 and winner_score <= scores[1][0] * 1.01:
            return
        pairs = set(tuple(sorted(x for i, x in enumerate(split) if i != slot))
                    for split in splits for slot in range(3) if split[slot] == word)
        if not pairs:
            return
        self.entity_numeric[word][entity] += 1
        for pair in pairs:
            self.effect_numeric[pair][effect] += 1

    def seal_a(self):
        if self.sealed or len(self.a) != 36:
            raise ValueError("requires 36 action observations")
        self._learn()
        for row in self.a:
            splits, consequence = _observable(row)
            self._write(row, splits, consequence)
        self.sealed = True

    def finalize_b(self):
        if not self.sealed or self.finalized or len(self.b) != 6:
            raise ValueError("requires six B observations")
        self.finalized, self.phase = True, "B"

    def use_phase(self, phase):
        if phase not in ("A", "B") or phase == "B" and not self.finalized:
            raise ValueError("phase not available")
        self.phase = phase

    @staticmethod
    def _unanimous(values):
        if not values:
            return None
        if len(values) != 1:
            return None
        (label, count), = values.items()
        return (label, count) if count >= MIN_SUPPORT else None

    def predict(self, before, acoustic_bits):
        _validate_state(before)
        if not self.sealed:
            return None
        splits = _parts(acoustic_bits)
        if not splits:
            return None
        if (_canonical(before), acoustic_bits) in self.conflicts:
            return None
        supported = {}
        for split in splits:
            for slot, word in enumerate(split):
                entity = self._unanimous(self.entity_numeric.get(word))
                if entity is None or self._entity_score(word, entity[0]) is None:
                    continue
                effect_key = tuple(sorted(x for i, x in enumerate(split) if i != slot))
                effect = self._unanimous(self.effect_numeric.get(effect_key))
                if effect is None:
                    continue
                candidate = list(before)
                candidate[entity[0]] = effect[0]
                outcome = tuple(candidate)
                supported[outcome] = max(supported.get(outcome, 0),
                                         min(entity[1], effect[1]))
        if not supported:
            return None
        # Conflict of equally supported physical consequences is not evidence.
        ranked = sorted(supported.items(), key=lambda item: (-item[1], item[0]))
        if len(ranked) > 1 and ranked[0][1] <= 2 * ranked[1][1]:
            return None
        return ranked[0][0]

    @property
    def actions(self):
        return len(self.a) + len(self.b)

    @property
    def numeric_weight_count(self):
        return sum(len(x) for x in self.entity_numeric.values()) + \
               sum(len(x) for x in self.effect_numeric.values())

    def snapshot(self):
        def pack(r):
            return [list(r.before), r.acoustic_bits, list(r.after),
                    r.action_cost, r.reset_cost]
        payload = {
            "schema": "wsp52.constructive-address.selftest.v1",
            "steps": self.steps,
            "a": [pack(r) for r in self.a],
            "b": [pack(r) for r in self.b],
            "sealed": self.sealed,
            "finalized": self.finalized,
            "phase": self.phase,
            "gradient_steps": self.gradient_steps,
            "gradient_operations": self.gradient_operations,
            "write_candidates": self.write_candidates,
            "coefficients": [[w, values] for w, values in sorted(self.coefficients.items())],
            "support": [[w, sorted(counts.items())] for w, counts in sorted(self.support.items())],
            "entity_numeric": [[w, sorted(counts.items())] for w, counts in sorted(self.entity_numeric.items())],
            "effect_numeric": [[list(pair), sorted(counts.items())] for pair, counts in
                               sorted(self.effect_numeric.items())],
            "conflicts": [list(k) for k in sorted(self.conflicts)]
        }
        raw = _canonical(payload)
        return _canonical({"payload": payload, "sha256": sha256(raw.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls, blob):
        from source import Observation  # interface type only
        try:
            env = json.loads(blob)
            if (type(env) is not dict or set(env) != {"payload", "sha256"} or
                    _canonical(env) != blob):
                raise ValueError("noncanonical envelope")
            p = env["payload"]
            if (type(p) is not dict or
                    sha256(_canonical(p).encode("ascii")).hexdigest() != env["sha256"] or
                    p["schema"] != "wsp52.constructive-address.selftest.v1"):
                raise ValueError("invalid payload")
            expected = {"schema", "steps", "a", "b", "sealed", "finalized", "phase",
                        "gradient_steps", "gradient_operations", "write_candidates",
                        "coefficients", "support", "entity_numeric",
                        "effect_numeric", "conflicts"}
            if set(p) != expected:
                raise ValueError("unknown snapshot fields")
            obj = cls(steps=p["steps"])
            def row(v):
                if type(v) is not list or len(v) != 5 or \
                        type(v[0]) is not list or type(v[2]) is not list:
                    raise ValueError("invalid observation")
                return Observation(tuple(v[0]), v[1], tuple(v[2]), v[3], v[4])
            for v in p["a"]:
                obj.observe(row(v))
            if p["sealed"]:
                obj.seal_a()
            elif p["b"] or p["finalized"]:
                raise ValueError("invalid stage")
            for v in p["b"]:
                obj.observe(row(v))
            if p["finalized"]:
                obj.finalize_b()
            obj.use_phase(p["phase"])
            # Reconstruction checks *all* provenance, numeric weights,
            # gradient parameters, action counts and stage flags.
            if obj.snapshot() != blob:
                raise ValueError("model state disagrees with observed experience")
            return obj
        except (ValueError, TypeError, KeyError, IndexError,
                UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid or tampered snapshot") from exc

    def capacity_bits(self):
        return 8 * len(self.snapshot().encode("ascii"))
