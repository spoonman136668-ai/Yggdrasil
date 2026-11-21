"""Bounded selector provenance tests; fake witnessed systems, no source-world calls."""
import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE

SOURCE = Path(__file__).with_name("specialist_selection.py")
spec = importlib.util.spec_from_file_location("selector_evidence_gate", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Selector = module.SpecialistSelection
VIEWS = ((0, 0), (0, 1))
ROW = {"s1": 0, "x1": 0, "s2": 1, "x2": 0, "y": 1}


class FakeNative:
    def __init__(self, ledger=()):
        self._ledger = ledger

    def _episode_reader(self):
        return self

    def experience_context_forecast(self, view, *actions):
        return Fraction(1, 2)

    def experience_context_plan(self, view):
        return ("retained_native_only", view)


class FakeSystem:
    def __init__(self, ledger=(), mode=None):
        self.native = FakeNative(ledger)
        self.mode = mode

    def checkpoint(self):
        return canonical(self.native._ledger)

    def specialist_forecasts(self, views, *actions):
        return 0.9, 0.1

    def observe_experience(self, identifier, views, row, *, source_sha256, packet_sha256):
        if (source_sha256 != EXPERIENCE_SOURCE or
                packet_sha256 != digest(canonical([identifier, views, row]))):
            raise ValueError("unwitnessed")
        ledger = self.native._ledger
        event = (identifier, views, row["x1"], row["s2"], row["x2"], row["y"])
        for old in ledger:
            if old[0] == identifier:
                if old != event:
                    raise ValueError("conflict")
                return self
        if self.mode == "missing":
            return FakeSystem(ledger)
        if self.mode == "double":
            return FakeSystem(ledger + (event, event))
        if self.mode == "forged":
            return FakeSystem(ledger + (("other", views, 0, 0, 0, 0),))
        return FakeSystem(ledger + (event,))


def new(system=None, **kwargs):
    return Selector(system if system is not None else FakeSystem(),
                    window=3, minimum_count=3,
                    minimum_gain=Fraction(1, 20), **kwargs)


def admit(s, number, views=VIEWS, row=ROW):
    identifier = f"dwsa67-{number}"
    return s.observe_experience(identifier, views, row,
                                source_sha256=EXPERIENCE_SOURCE,
                                packet_sha256=digest(canonical([identifier, views, row])))


class EvidenceTests(unittest.TestCase):
    def test_unwitnessed_fallback(self):
        self.assertEqual(new().forecast(VIEWS, 0), Fraction(1, 2))

    def test_caller_cannot_inject_loss_history(self):
        with self.assertRaises(TypeError):
            new(evidence={(0, 0): ((Fraction(1), Fraction(0)),) * 3})

    def test_caller_cannot_mutate_snapshot(self):
        state = new()
        with self.assertRaises(TypeError):
            state._evidence[(0, 0)] = ((Fraction(1), Fraction(0)),) * 3
        with self.assertRaises(AttributeError):
            state._evidence = {(0, 0): ((Fraction(1), Fraction(0)),) * 3}
        with self.assertRaises(AttributeError):
            state.minimum_gain = Fraction(0)

    def test_only_three_witnesses_enable_specialist(self):
        state = new()
        for i in range(3):
            old = state
            state = admit(state, i)
            self.assertEqual(old.selection(VIEWS, 0), 0)
        self.assertEqual(state.selection(VIEWS, 0), 1)
        self.assertEqual(state.forecast(VIEWS, 0), Fraction(9, 10))

    def test_selector_never_controls_plan(self):
        state = new()
        for i in range(3):
            state = admit(state, i)
        self.assertEqual(state.selection(VIEWS, 0), 1)
        self.assertEqual(state.forecast(VIEWS, 0), Fraction(9, 10))
        self.assertEqual(state.plan(VIEWS), ("retained_native_only", VIEWS[0]))
        self.assertEqual(state.system.native.experience_context_plan(VIEWS[0]),
                         state.plan(VIEWS))

    def test_shadow_plan_rejects_bad_coordinate(self):
        with self.assertRaises(ValueError):
            new().plan(((0, 0), (1, 0)))

    def test_loss_is_prequential(self):
        state = admit(new(), 0)
        self.assertEqual(state._evidence[(0, 0)],
                         ((Fraction(1, 4) - Fraction(1, 100),
                           Fraction(1, 4) - Fraction(81, 100)),))

    def test_duplicate_unchanged(self):
        state = admit(new(), 0)
        self.assertIs(admit(state, 0), state)

    def test_conflicting_receipt_rejected(self):
        state = admit(new(), 0)
        with self.assertRaises(ValueError):
            admit(state, 0, row={**ROW, "y": 0})

    def test_bad_source_or_packet_rejected(self):
        state = new()
        payload = digest(canonical(["dwsa67-x", VIEWS, ROW]))
        for source, packet in (("bad", payload), (EXPERIENCE_SOURCE, "bad")):
            with self.subTest(source=source, packet=packet):
                with self.assertRaises(ValueError):
                    state.observe_experience("dwsa67-x", VIEWS, ROW,
                                             source_sha256=source, packet_sha256=packet)

    def test_mismatched_coordinate_rejected(self):
        with self.assertRaises(ValueError):
            admit(new(), 0, views=((0, 0), (1, 0)))

    def test_missing_or_extra_event_rejected(self):
        for mode in ("missing", "double", "forged"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    admit(new(FakeSystem(mode=mode)), 0)

    def test_cold_replay_matches_prequential_state(self):
        original = FakeSystem()
        state = new(original)
        for i in range(3):
            state = admit(state, i)
        cold = Selector.replay(original, state.system, window=3,
                               minimum_count=3, minimum_gain=Fraction(1, 20))
        self.assertEqual(dict(cold._evidence), dict(state._evidence))
        self.assertEqual(cold.forecast(VIEWS, 0), state.forecast(VIEWS, 0))

    def test_wrong_cold_prefix_rejected(self):
        parent = FakeSystem((("old", VIEWS, 0, 1, 0, 1),))
        with self.assertRaises(ValueError):
            Selector.replay(parent, FakeSystem(), window=3,
                            minimum_count=3, minimum_gain=Fraction(1, 20))

    def test_reward_stays_native_by_default(self):
        state = new()
        for i in range(3):
            state = admit(state, i)
        self.assertEqual(state.selection(VIEWS, 0, 1, 0), 0)

    def test_no_future_label_or_mutation(self):
        original = new()
        self.assertEqual(original.forecast(VIEWS, 0), Fraction(1, 2))
        state = admit(original, 0)
        self.assertEqual(original.forecast(VIEWS, 0), Fraction(1, 2))
        self.assertEqual(state.selection(VIEWS, 0), 0)

    def test_nonfinite_forecast_rejected(self):
        state = new()
        state.system.specialist_forecasts = lambda *a: (float("nan"), 0.1)
        with self.assertRaises(ValueError):
            admit(state, 0)
