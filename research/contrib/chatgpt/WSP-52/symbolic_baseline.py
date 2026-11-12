"""WSP52 independent, finite symbolic compositional comparator (SELFTEST prototype).

Learns *raw binary substring* hypotheses and physical state transitions from
observations. No generator vocabulary, hidden grammar, exact action IDs, latent
roles, direct-writer numerical weights or gradient steps are read.

This is an evidence-restricted, partial symbolic candidate; it is NOT the
preregistered exhaustive all-consistent-hypotheses baseline. The bounded
hypothesis ranking can still confidently mispredict; report all errors.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
import json

WORD_LENGTHS = (4, 5, 6)
MAX_SEGMENTS = 27
A_BUDGET = 36
B_BUDGET = 6


def _encode(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _state(obj):
    if type(obj) is not tuple or len(obj) != 8 or any(type(x) is not int or not (0 <= x < 4) for x in obj):
        raise ValueError("state must be eight physical locations in 0..3")


def _split(bits):
    if type(bits) is not str or not bits or set(bits) - {"0", "1"}:
        raise ValueError("expected undelimited binary stream")
    parsed = []
    for lengths in product(WORD_LENGTHS, repeat=3):
        if sum(lengths) == len(bits):
            offset = 0
            words = []
            for length in lengths:
                words.append(bits[offset:offset + length])
                offset += length
            parsed.append(tuple(words))
    if len(parsed) > MAX_SEGMENTS:
        raise ValueError("segmentation bound exceeded")
    return tuple(parsed)


def _event(row):
    before, after, bits = row.before, row.after, row.acoustic_bits
    _state(before)
    _state(after)
    _split(bits)
    if type(row.action_cost) is not int or row.action_cost != 1 or type(row.reset_cost) is not int or row.reset_cost != 0:
        raise ValueError("unaccounted action/reset cost")
    changed = tuple(i for i, (a, b) in enumerate(zip(before, after)) if a != b)
    if len(changed) > 1:
        raise ValueError("action library changes at most one physical entity")
    return None if not changed else (changed[0], after[changed[0]])


def _hypotheses(rows, inherited_words=None):
    """Corpus-only word intersections and ordered effect-pair lookup.

    Missing or ambiguous word boundaries remain unknown rather than guessed.
    This uses no generator's hidden codebook or phase order. Word constraints
    are derived from repeated *changed* physical observations only.
    """
    events = [(row, _event(row)) for row in rows]
    informative = [(row, label) for row, label in events if label is not None]
    models = []
    for slot in range(3):
        word_candidates = {}
        for entity in range(8):
            if inherited_words is not None:
                known = inherited_words.get(entity)
                if known is not None:
                    word_candidates[entity] = known
                continue
            appearances = [row for row, ev in informative if ev[0] == entity]
            if not appearances:
                continue
            possible = None
            for row in appearances:
                options = {parts[slot] for parts in _split(row.acoustic_bits)}
                possible = options if possible is None else possible & options
            if possible is not None and len(possible) == 1:
                word_candidates[entity] = next(iter(possible))
        # A missing lexical concept is not filled from the evaluator.
        if not word_candidates or len(set(word_candidates.values())) != len(word_candidates):
            continue
        lexical = tuple(word_candidates.values())
        if any(a != b and (a.startswith(b) or b.startswith(a)) for a in lexical for b in lexical):
            continue
        pair_evidence = defaultdict(set)
        uniquely_parsed = 0
        for row, ev in informative:
            entity, effect = ev
            word = word_candidates.get(entity)
            if word is None:
                continue
            matches = [parts for parts in _split(row.acoustic_bits) if parts[slot] == word]
            if len(matches) != 1:
                continue
            parts = matches[0]
            pair = tuple(parts[j] for j in range(3) if j != slot)
            pair_evidence[pair].add(effect)
            uniquely_parsed += 1
        learned = {key: next(iter(v)) for key, v in pair_evidence.items() if len(v) == 1}
        # No conflicts are silently replaced with majority decisions.
        conflicts = {key for key, v in pair_evidence.items() if len(v) > 1}
        models.append({"slot": slot, "lex": word_candidates, "pairs": learned,
                       "conflicts": conflicts, "support": uniquely_parsed})
    if not models:
        return ()
    best = max(m["support"] for m in models)
    # Retain ties to force abstention if observational hypotheses disagree.
    return tuple(m for m in models if m["support"] == best)


def _prediction_candidates(model, before, bits, orientation, extra=None):
    slot = model["slot"]
    reverse = orientation == 1
    answers = set()
    has_unknown = False
    entity_for = {word: entity for entity, word in model["lex"].items()}
    for words in _split(bits):
        entity = entity_for.get(words[slot])
        if entity is None:
            continue
        pair = tuple(words[j] for j in range(3) if j != slot)
        if reverse:
            pair = pair[::-1]
        primary = model["pairs"].get(pair)
        supplemental = None if extra is None else extra.get(pair)
        if pair in model["conflicts"] or primary is not None and supplemental is not None and primary != supplemental:
            has_unknown = True
            continue
        effect = primary if primary is not None else supplemental
        if effect is None:
            has_unknown = True
            continue
        result = list(before)
        result[entity] = effect
        answers.add(tuple(result))
    if has_unknown or len(answers) != 1:
        return None
    return next(iter(answers))


class SymbolicCorpusLearner:
    """Two-phase finite symbolic learner with disclosed structural priors."""

    def __init__(self):
        self.phase_a = []
        self.phase_b = []
        self.sealed = False
        self.finalized = False
        self.phase = "A"
        self.replay_parses = 0
        self.validation_predictions = 0
        self._a_models = ()
        self._b_models = ()

    def observe(self, observation):
        if self.finalized:
            raise ValueError("model frozen")
        _event(observation)
        rows = self.phase_b if self.sealed else self.phase_a
        if len(rows) >= (B_BUDGET if self.sealed else A_BUDGET):
            raise ValueError("evidence budget exceeded")
        rows.append(observation)

    def seal_a(self):
        if self.sealed or len(self.phase_a) != A_BUDGET:
            raise ValueError("requires exactly 36 phase-A observations")
        self._a_models = _hypotheses(self.phase_a)
        self.sealed = True

    def finalize_b(self):
        if not self.sealed or self.finalized or len(self.phase_b) != B_BUDGET:
            raise ValueError("requires exactly six phase-B observations")
        candidates = []
        changed = [(r, _event(r)) for r in self.phase_b]
        for base in self._a_models:
            # Choose a new entity slot and optional pair reordering using
            # *observed* phase-B consequences, never heldout labels.
            for slot in range(3):
                model = _hypotheses(self.phase_b, inherited_words=base["lex"])
                for parsed in model:
                    if parsed["slot"] != slot:
                        continue
                    for reverse in (0, 1):
                        correct = wrong = identifiable = 0
                        supplemental = parsed["pairs"]
                        # Validation is *resubstitution*, not a science metric:
                        # charge every such prediction and report optimism risk.
                        for row, event in changed:
                            if event is None:
                                continue
                            guess = _prediction_candidates(
                                {"slot": slot, "lex": base["lex"], "pairs": base["pairs"],
                                 "conflicts": base["conflicts"]},
                                row.before, row.acoustic_bits, reverse, supplemental)
                            self.validation_predictions += 1
                            if guess is None:
                                continue
                            identifiable += 1
                            if guess == row.after:
                                correct += 1
                            else:
                                wrong += 1
                        rank = (correct - 2 * wrong, correct, identifiable)
                        candidates.append((rank, {"slot": slot, "lex": base["lex"],
                                                  "pairs": base["pairs"], "conflicts": base["conflicts"],
                                                  "orientation": reverse, "extra": supplemental}))
        if candidates:
            best = max(score for score, _ in candidates)
            self._b_models = tuple(model for score, model in candidates if score == best)
        self.replay_parses = sum(len(_split(r.acoustic_bits)) for r in self.phase_a + self.phase_b)
        self.finalized = True
        self.phase = "B"

    def use_phase(self, phase):
        if phase not in ("A", "B") or phase == "B" and not self.finalized:
            raise ValueError("phase unavailable")
        self.phase = phase

    def predict(self, before, acoustic_bits):
        _state(before)
        _split(acoustic_bits)
        models = self._a_models if self.phase == "A" else self._b_models
        # Before sealing, infer from A only; never look at external target.
        if not self.sealed and len(self.phase_a) == A_BUDGET:
            models = _hypotheses(self.phase_a)
        if not models:
            return None
        guesses = set()
        for model in models:
            guess = _prediction_candidates(
                model, before, acoustic_bits, model.get("orientation", 0),
                model.get("extra"))
            if guess is None:
                return None
            guesses.add(guess)
        return next(iter(guesses)) if len(guesses) == 1 else None

    @property
    def actions(self):
        return len(self.phase_a) + len(self.phase_b)

    def snapshot(self):
        # Store raw observations because this finite symbolic baseline rebuilds
        # all hypotheses from evidence. This storage cost is NOT free.
        def pack(r):
            return [list(r.before), r.acoustic_bits, list(r.after), r.action_cost, r.reset_cost]
        payload = {"schema": "wsp52.symbolic-corpus-prototype.v1",
                   "a": [pack(r) for r in self.phase_a], "b": [pack(r) for r in self.phase_b],
                   "sealed": self.sealed, "finalized": self.finalized, "phase": self.phase}
        return _encode({"payload": payload,
                        "sha256": sha256(_encode(payload).encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls, snapshot):
        from source import Observation  # only the five-field interface type
        if type(snapshot) is not str:
            raise ValueError("invalid snapshot type")
        try:
            envelope = json.loads(snapshot)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("invalid envelope")
            payload = envelope["payload"]
            if type(payload) is not dict or set(payload) != {"schema", "a", "b", "sealed", "finalized", "phase"}:
                raise ValueError("invalid payload")
            if payload["schema"] != "wsp52.symbolic-corpus-prototype.v1":
                raise ValueError("wrong schema")
            if sha256(_encode(payload).encode("ascii")).hexdigest() != envelope["sha256"]:
                raise ValueError("tampered snapshot")
            obj = cls()
            for row in payload["a"]:
                if type(row) is not list or len(row) != 5:
                    raise ValueError("bad observation")
                obj.observe(Observation(tuple(row[0]), row[1], tuple(row[2]), row[3], row[4]))
            if payload["sealed"]:
                obj.seal_a()
            for row in payload["b"]:
                obj.observe(Observation(tuple(row[0]), row[1], tuple(row[2]), row[3], row[4]))
            if payload["finalized"]:
                obj.finalize_b()
            obj.use_phase(payload["phase"])
            if obj.snapshot() != snapshot:
                raise ValueError("noncanonical state")
            return obj
        except (ValueError, KeyError, TypeError, IndexError, json.JSONDecodeError, UnicodeError) as err:
            raise ValueError("invalid symbolic snapshot") from err

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8
