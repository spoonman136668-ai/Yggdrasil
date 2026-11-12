"""WSP52 independent bounded symbolic version-space search: SELFTEST engineering only.

Enumerate every consistent assignment in a constrained three-word, 4..6-bit,
8 entity / 4 destination / 3 verb hypothesis class until a hard resource cap.
If the search is truncated, prediction MUST abstain. No generator or oracle
vocabulary, role-order labels, heldout targets, gradient model, or direct-writer
weights are imported. The observed-word projection can include hypotheses that
cannot extend to a full 15-word codebook: it is conservative, not a certificate
of the preregistered full exhaustive symbolic comparator.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import permutations, product
from time import monotonic_ns
import json

ORDERS = tuple(permutations((0, 1, 2)))
LENGTHS = (4, 5, 6)
NODE_CAP, MODEL_CAP, STATE_CAP, TIME_CAP_SECONDS = 20000, 2000, 4000, 15


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _parts(bits):
    if type(bits) is not str or not bits or set(bits) - {"0", "1"}:
        raise ValueError("invalid binary observation")
    for a, b, c in product(LENGTHS, repeat=3):
        if a + b + c == len(bits):
            yield bits[:a], bits[a:a+b], bits[a+b:]


def _visible(row):
    for state in (row.before, row.after):
        if (type(state) is not tuple or len(state) != 8
                or any(type(x) is not int or not 0 <= x < 4 for x in state)):
            raise ValueError("invalid eight-object state")
    if (type(row.action_cost) is not int or row.action_cost != 1
            or type(row.reset_cost) is not int or row.reset_cost != 0):
        raise ValueError("incorrect action accounting")
    changed = [i for i, (before, after) in enumerate(zip(row.before, row.after))
               if before != after]
    if len(changed) > 1:
        raise ValueError("not a single-entity action")
    # A no-op cannot ground an entity: preserve all eight possible explanations.
    return ((changed[0], row.after[changed[0]]),) if changed else tuple(
        (i, row.before[i]) for i in range(8))


def _extend(lexicon, indexes, words):
    state = list(lexicon)
    for i, word in zip(indexes, words):
        if state[i] is not None and state[i] != word:
            return None
        state[i] = word
    assigned = [x for x in state if x is not None]
    if len(assigned) != len(set(assigned)):
        return None
    if any(x != y and (x.startswith(y) or y.startswith(x))
           for x in assigned for y in assigned):
        return None
    return tuple(state)


class BoundedVersionSpace:
    """Conservative comparator: exhaustive inside declared caps, else INCOMPLETE."""

    def __init__(self, *, node_cap=NODE_CAP, model_cap=MODEL_CAP,
                 state_cap=STATE_CAP, time_cap_seconds=TIME_CAP_SECONDS):
        caps = (node_cap, model_cap, state_cap, time_cap_seconds)
        if any(type(c) is not int or c < 1 for c in caps):
            raise ValueError("positive integer caps required")
        self.caps = caps
        self.a, self.b = [], []
        self.sealed = self.finalized = False
        self.phase = "A"
        self.models_a = self.models_ab = ()
        self.receipt_a = self.receipt_ab = None

    def observe(self, row):
        if self.finalized:
            raise ValueError("frozen learner")
        _visible(row)
        tuple(_parts(row.acoustic_bits))
        items = self.b if self.sealed else self.a
        if len(items) >= (6 if self.sealed else 36):
            raise ValueError("action budget exceeded")
        items.append(row)

    def _search(self, rows):
        phases = ("A", "B") if any(p == "B" for p, _ in rows) else ("A",)
        prepared = [(phase, _visible(row), tuple(_parts(row.acoustic_bits)))
                    for phase, row in rows]
        prepared.sort(key=lambda item: (len(item[1]), len(item[2]), item[0]))
        nodes = 0
        complete, reason = True, None
        models, seen = set(), set()
        t0 = monotonic_ns()

        def visit(k, lexicon, orders):
            nonlocal nodes, complete, reason
            if not complete:
                return
            key = (k, lexicon, orders)
            if key in seen:
                return
            seen.add(key)
            if len(seen) > self.caps[2]:
                complete, reason = False, "STATE_CAP"
                return
            if k == len(prepared):
                models.add((orders, lexicon))
                if len(models) > self.caps[1]:
                    complete, reason = False, "MODEL_CAP"
                return
            phase, effects, splits = prepared[k]
            order = orders[0] if phase == "A" else orders[1]
            slots = tuple(order.index(role) for role in (0, 1, 2))
            for split in splits:
                words = tuple(split[slot] for slot in slots)
                for entity, effect in effects:
                    for destination in range(4):
                        for verb in range(3):
                            if (destination + verb) % 4 != effect:
                                continue
                            nodes += 1
                            if nodes > self.caps[0]:
                                complete, reason = False, "NODE_CAP"
                                return
                            if (nodes % 256 == 0 and
                                monotonic_ns() - t0 > self.caps[3] * 1_000_000_000):
                                complete, reason = False, "TIME_CAP"
                                return
                            updated = _extend(lexicon, (entity, 8+destination, 12+verb), words)
                            if updated is not None:
                                visit(k+1, updated, orders)
                            if not complete:
                                return

        for orders in product(ORDERS, repeat=len(phases)):
            visit(0, (None,)*15, orders)
            if not complete:
                break
        return tuple(sorted(models, key=_canonical)), {
            "complete": complete, "reason": reason, "nodes": nodes,
            "models": len(models), "elapsed_ms": (monotonic_ns()-t0)//1_000_000}

    def seal_a(self):
        if self.sealed or len(self.a) != 36:
            raise ValueError("requires exactly 36 A experiences")
        self.models_a, self.receipt_a = self._search(tuple(("A", x) for x in self.a))
        self.sealed = True

    def finalize_b(self):
        if not self.sealed or self.finalized or len(self.b) != 6:
            raise ValueError("requires exactly 6 B experiences")
        rows = tuple(("A", x) for x in self.a) + tuple(("B", x) for x in self.b)
        self.models_ab, self.receipt_ab = self._search(rows)
        self.finalized, self.phase = True, "B"

    def use_phase(self, phase):
        if phase not in ("A", "B") or phase == "B" and not self.finalized:
            raise ValueError("phase not available")
        self.phase = phase

    def predict(self, before, acoustic_bits):
        if (type(before) is not tuple or len(before) != 8
                or any(type(v) is not int or not 0 <= v < 4 for v in before)):
            raise ValueError("invalid state")
        splits = tuple(_parts(acoustic_bits))
        receipt = self.receipt_a if self.phase == "A" else self.receipt_ab
        models = self.models_a if self.phase == "A" else self.models_ab
        if receipt is None or not receipt["complete"] or not models:
            return None
        answers = set()
        for orders, lexicon in models:
            # Unknown full-codebook completions cannot be ruled out by a
            # partial mapping, even if a fitted subset happens to agree.
            if any(word is None for word in lexicon):
                return None
            order = orders[0] if self.phase == "A" else orders[1]
            slots = tuple(order.index(role) for role in (0,1,2))
            possible = set()
            for split in splits:
                try:
                    entity = lexicon[:8].index(split[slots[0]])
                    destination = lexicon[8:12].index(split[slots[1]])
                    verb = lexicon[12:].index(split[slots[2]])
                except ValueError:
                    continue
                after = list(before)
                after[entity] = (destination+verb)%4
                possible.add(tuple(after))
            if len(possible) != 1:
                return None
            answers.update(possible)
            if len(answers) != 1:
                return None
        return next(iter(answers)) if answers else None

    @property
    def actions(self):
        return len(self.a) + len(self.b)

    def snapshot(self):
        def pack(row):
            return [list(row.before), row.acoustic_bits, list(row.after),
                    row.action_cost, row.reset_cost]
        payload = {"schema": "wsp52.bounded-symbolic.v1",
                   "caps": list(self.caps), "a": [pack(row) for row in self.a],
                   "b": [pack(row) for row in self.b], "sealed": self.sealed,
                   "finalized": self.finalized, "phase": self.phase}
        return _canonical({"payload": payload,
                           "sha256": sha256(_canonical(payload).encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls, data):
        from source import Observation  # interface type only: no generator access
        try:
            envelope = json.loads(data)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("invalid envelope")
            payload = envelope["payload"]
            if (type(payload) is not dict or
                set(payload) != {"schema","caps","a","b","sealed","finalized","phase"} or
                payload["schema"] != "wsp52.bounded-symbolic.v1"):
                raise ValueError("wrong schema")
            if (_canonical(envelope) != data or
                sha256(_canonical(payload).encode("ascii")).hexdigest() != envelope["sha256"]):
                raise ValueError("noncanonical/tampered state")
            obj = cls(node_cap=payload["caps"][0], model_cap=payload["caps"][1],
                      state_cap=payload["caps"][2], time_cap_seconds=payload["caps"][3])
            if (payload["finalized"] and not payload["sealed"]) or (payload["b"] and not payload["sealed"]):
                raise ValueError("invalid phase")
            def replay(rows):
                for row in rows:
                    if type(row) is not list or len(row) != 5:
                        raise ValueError("invalid observation")
                    obj.observe(Observation(tuple(row[0]), row[1], tuple(row[2]),
                                            row[3], row[4]))
            replay(payload["a"])
            if payload["sealed"]:
                obj.seal_a()
            replay(payload["b"])
            if payload["finalized"]:
                obj.finalize_b()
            obj.use_phase(payload["phase"])
            if obj.snapshot() != data:
                raise ValueError("noncanonical reconstruction")
            return obj
        except (KeyError, IndexError, TypeError, ValueError, UnicodeError) as exc:
            raise ValueError("invalid symbolic snapshot") from exc

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii")) * 8
