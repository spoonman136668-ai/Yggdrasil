"""FIT-only native episode vs compact online Beta; existing synthetic evidence only.

No protected first-use, held scoring, source training, or accepted-state update.
Reverse chronology is an artificial order-negative, not a new world run.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

TRACE = (Path(__file__).resolve().parents[1] /
         "research/contrib/chatgpt/CAUSAL-AMALGAM/selection-dev-01/trace.json")
TRACE_PIN = "36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114"
COHORT = "amalgam-selection-transition-local-dev-v1"


def fit():
    raw = TRACE.read_bytes()
    if sha256(raw).hexdigest() != TRACE_PIN:
        raise ValueError("PCER02_SOURCE_DRIFT")
    trace = json.loads(raw)
    if type(trace) is not list or len(trace) != 96:
        raise ValueError("PCER02_TRACE_SHAPE")
    rows = []
    for i, event in enumerate(trace[:50]):
        phase, index = divmod(i, 32)
        ident = digest(canonical([COHORT, (764013, 764029)[phase], index]))
        if event["id"] != ident or event["phase"] != phase:
            raise ValueError("PCER02_IDENTITY")
        views = tuple(tuple(v) for v in event["views"])
        row = event["row"]
        if (len(views) != 2 or any(len(v) != 2 for v in views) or
                any(type(b) is not int or b not in (0, 1)
                    for v in views for b in v) or
                set(row) != {"s1", "x1", "s2", "x2", "y"} or
                any(type(row[k]) is not int or row[k] not in (0, 1)
                    for k in ("s1", "x1", "s2", "x2", "y")) or
                views[0][0] != views[1][0] or row["s1"] != views[0][0]):
            raise ValueError("PCER02_PUBLIC_ROW")
        rows.append((ident, views, row))
    return rows


class Compact:
    """Two-stage conventional counts and prequential losses; no witness ledger."""

    def __init__(self):
        self.t = [[[0, 0] for _ in range(2)] for _ in range(3)]
        self.y = [[[0, 0] for _ in range(2)] for _ in range(14)]
        self.tloss = [Fraction(0), Fraction(0)]
        self.yloss = [Fraction(0), Fraction(0)]
        self.projection = None
        self.mismatch = [0, 0]
        self.n = 0
        self.buffer = []

    @staticmethod
    def p(bank, slot, action):
        fails, wins = bank[slot][action]
        return Fraction(wins + 1, fails + wins + 2)

    @staticmethod
    def selected(loss):
        return 0 if loss[0] < loss[1] else 1

    @staticmethod
    def slots(context, first, state):
        return ((12 + state, 12 + state) if context is None else
                (context + 2 * first + 4 * state, 8 + context + 2 * state))

    def context(self, views):
        if self.projection is None:
            return None
        a, b = (v[self.projection] for v in views)
        return a if a == b else None

    def projected(self, views, first, state, second, reward):
        context = self.context(views)
        if context is not None:
            full, pooled = self.slots(context, first, state)
            self.t[context][first][state] += 1
            self.y[full][second][reward] += 1
            self.y[pooled][second][reward] += 1

    def observe(self, views, row):
        first, state, second, reward = (row[k] for k in ("x1", "s2", "x2", "y"))
        context = self.context(views)
        full, pooled = self.slots(context, first, state)
        for i, slot in enumerate((2 if context is None else context, 2)):
            self.tloss[i] += (self.p(self.t, slot, first) - state) ** 2
        for i, slot in enumerate((full, pooled)):
            self.yloss[i] += (self.p(self.y, slot, second) - reward) ** 2
        self.t[2][first][state] += 1
        self.y[12 + state][second][reward] += 1
        self.projected(views, first, state, second, reward)
        self.n += 1
        if self.n <= 8:
            self.buffer.append((views, first, state, second, reward))
            for pos in (0, 1):
                self.mismatch[pos] += int(views[0][pos] != views[1][pos])
            if self.n == 8 and self.mismatch[0] != self.mismatch[1]:
                self.projection = int(self.mismatch[1] < self.mismatch[0])
                for event in self.buffer:
                    self.projected(*event)
                self.buffer.clear()

    def forecast(self, view, first, state=None, second=None):
        context = None if self.projection is None else view[self.projection]
        if state is None:
            if second is not None:
                raise ValueError("PCER02_STAGE_ONE")
            slots, bank, losses, action = ((2 if context is None else context, 2),
                                          self.t, self.tloss, first)
        else:
            if second is None:
                raise ValueError("PCER02_STAGE_TWO")
            slots, bank, losses, action = (self.slots(context, first, state),
                                          self.y, self.yloss, second)
        return self.p(bank, slots[self.selected(losses)], action)

    def checkpoint(self):
        if self.buffer:
            raise ValueError("PCER02_INCOMPLETE_PROJECTION")
        return canonical({"t": self.t, "y": self.y,
                          "tloss": [[x.numerator, x.denominator] for x in self.tloss],
                          "yloss": [[x.numerator, x.denominator] for x in self.yloss],
                          "projection": self.projection, "mismatch": self.mismatch,
                          "count": self.n})

    @classmethod
    def restore(cls, raw, pin):
        if type(raw) is not bytes or digest(raw) != pin:
            raise ValueError("PCER02_COMPACT_PIN")
        obj = cls()
        d = json.loads(raw)
        if set(d) != {"t", "y", "tloss", "yloss", "projection", "mismatch", "count"}:
            raise ValueError("PCER02_COMPACT_SHAPE")
        obj.t, obj.y = d["t"], d["y"]
        obj.tloss = [Fraction(*pair) for pair in d["tloss"]]
        obj.yloss = [Fraction(*pair) for pair in d["yloss"]]
        obj.projection, obj.mismatch, obj.n = d["projection"], d["mismatch"], d["count"]
        if obj.checkpoint() != raw:
            raise ValueError("PCER02_COMPACT_RESTORE")
        return obj


class NativeFitReplay(unittest.TestCase):
    def test_source_is_exact_and_frozen(self):
        evidence = fit()
        self.assertEqual(len(evidence), 50)
        self.assertEqual(evidence[0][0],
                         "f21c705258698a9a2f287870fc94d3f90f223797a9db8127f0ab176e60af9723")
        self.assertEqual(evidence[-1][0],
                         "fa41b1f46abfb41d614e650a54046191bb16c48c3eb26bfc112fe5ab3941065d")

    def test_exact_native_vs_compact_and_cold_restore(self):
        evidence = fit()
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                native, control = NativeEpisodeExperience(), Compact()
                for ident, views, row in (evidence[::-1] if reverse else evidence):
                    native = native.observe(ident, views, row)
                    control.observe(views, row)
                self.assertEqual(native.info()["count"], 50)
                self.assertEqual(native.info()["repairs"], [])
                self.assertEqual(native._projection, control.projection)
                self.assertEqual(native._transition_loss, control.tloss)
                self.assertEqual(native._terminal_loss, control.yloss)
                self.assertEqual(native._selected(native._transition_loss),
                                 control.selected(control.tloss))
                self.assertEqual(native._selected(native._terminal_loss),
                                 control.selected(control.yloss))
                for context in (0, 1):
                    view = (context, 0)
                    for first in (0, 1):
                        self.assertEqual(native.forecast(view, first), control.forecast(view, first))
                        for state in (0, 1):
                            for second in (0, 1):
                                self.assertEqual(native.forecast(view, first, state, second),
                                                 control.forecast(view, first, state, second))
                raw, small = native.checkpoint(), control.checkpoint()
                self.assertEqual(len(raw), 4715)
                self.assertLess(len(small), len(raw))
                self.assertEqual(NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint(), raw)
                self.assertEqual(native.consolidate().checkpoint(), raw)
                self.assertEqual(Compact.restore(small, digest(small)).checkpoint(), small)
                with self.assertRaises(ValueError):
                    NativeEpisodeExperience.restore(raw[:-1] + b"!", digest(raw))
                with self.assertRaises(ValueError):
                    Compact.restore(small[:-1] + b"!", digest(small))
                self.assertEqual(native._selected(native._transition_loss), 1 if reverse else 0)
                self.assertEqual(native.forecast((0, 0), 0),
                                 Fraction(10, 27) if reverse else Fraction(7, 13))

    def test_exact_duplicate_is_native_noop_but_compact_counts_twice(self):
        evidence = fit()
        native, control = NativeEpisodeExperience(), Compact()
        for ident, views, row in evidence:
            native = native.observe(ident, views, row)
            control.observe(views, row)
        initial_native = native.checkpoint()
        initial_compact = control.checkpoint()
        witness_id, views, row = evidence[0]
        repeated = native.observe(witness_id, views, row)
        self.assertIs(repeated, native)
        self.assertEqual(native.checkpoint(), initial_native)
        self.assertEqual(native.info()["count"], 50)
        self.assertEqual(native.forecast((0, 0), 0), Fraction(7, 13))
        control.observe(views, row)
        self.assertNotEqual(control.checkpoint(), initial_compact)
        self.assertEqual(control.n, 51)
        self.assertEqual(control.forecast((0, 0), 0), Fraction(4, 7))

    def test_conflicting_replay_rejected_by_native_not_identity_free_control(self):
        evidence = fit()
        native, control = NativeEpisodeExperience(), Compact()
        for ident, views, row in evidence:
            native = native.observe(ident, views, row)
            control.observe(views, row)
        initial_native = native.checkpoint()
        witness_id, views, row = evidence[0]
        conflict = dict(row)
        conflict["s2"] ^= 1
        with self.assertRaisesRegex(ValueError, "EPISODE_CONFLICTING_REPLAY"):
            native.observe(witness_id, views, conflict)
        self.assertEqual(native.checkpoint(), initial_native)
        self.assertEqual(native.info()["count"], 50)
        control.observe(views, conflict)
        self.assertEqual(control.n, 51)
        self.assertEqual(control.forecast((0, 0), 0), Fraction(1, 2))

    def test_reverse_preserves_all_static_two_stage_counts(self):
        evidence = fit()
        def cells(rows):
            counts = {}
            for _, views, row in rows:
                key = (views[0][0], row["x1"], row["s2"], row["x2"], row["y"])
                counts[key] = counts.get(key, 0) + 1
            return counts
        self.assertEqual(cells(evidence), cells(evidence[::-1]))
        self.assertEqual(sum(cells(evidence).values()), 50)


if __name__ == "__main__":
    unittest.main()
