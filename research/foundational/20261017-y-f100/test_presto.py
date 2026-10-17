"""F100R2 source-only contracts: no cohort generation or scientific outcome reads."""
from __future__ import annotations

import importlib.util
import inspect
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("f100_presto_source_under_test",
                                               HERE / "presto.py")
M = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = M
spec.loader.exec_module(M)

BASE = (
    (10, 11, (0,)), (11, 12, (2,)), (12, 13, (4,)), (13, 14, (6,)),
)
NOVEL_LONG = (40, 41, (0, 2, 4, 6, 0))
EXTENDED = BASE + (NOVEL_LONG,)
DANGEROUS = EXTENDED + ((10, 23, (0,)),)
EVENT = (99, 0, 100)


class FakePack:
    def pack(self, a, b, codes):
        assert isinstance(a, int) and isinstance(b, int)
        assert len(codes) in range(1, 7)
        return bytes(12)


class FakeNative:
    def __init__(self, choices=(EXTENDED,), duplicate_baseline=False,
                 corrupt_on_replay=False):
        self.choices = choices
        self.duplicate_baseline = duplicate_baseline
        self.corrupt_on_replay = corrupt_on_replay

    def _f60_step(self, memory, event, pack):
        if (self.corrupt_on_replay and event == (10, 0, 11)
                and NOVEL_LONG in memory):
            return memory + ((88, 89, (0,)),)
        return memory

    def actions(self, memory, event, index, pack):
        primary = (("append", -1, -1, memory, ()),)
        extras = tuple(("merge", i, -1, candidate, ())
                       for i, candidate in enumerate(self.choices))
        if self.duplicate_baseline:
            extras += (("bad-duplicate", -1, -1, memory, ()),)
        return primary + extras

    def _valid_memory(self, memory, pack):
        assert len(memory) <= 12
        for r in memory:
            assert len(pack.pack(*r)) == 12
        return None


class FrozenGraph:
    class ClosureLimitExceeded(Exception):
        pass

    @staticmethod
    def closure(*args, **kwargs):
        # Use the actual frozen F99 implementation in ALL feature tests.
        return REAL_F99.closure(*args, **kwargs)


old = HERE.parent / "20261016-y-f99" / "causal_closure.py"
spec99 = importlib.util.spec_from_file_location("f100_f99_exact_pure", old)
REAL_F99 = importlib.util.module_from_spec(spec99)
sys.modules[spec99.name] = REAL_F99
spec99.loader.exec_module(REAL_F99)


class F100SourceContracts(unittest.TestCase):
    def select(self, candidate=EXTENDED, used=False, index=10, native=None):
        n = native if native is not None else FakeNative((candidate,))
        return M.select(BASE, EVENT, index, used, FakePack(), n, REAL_F99)

    def test_frozen_prereg_r2_and_parent_imports_are_exact(self):
        f = M.frozen_sources()
        self.assertIsNotNone(f)
        self.assertEqual(M.blob(HERE / "prereg_r2.json"), M.PREREG_R2_SHA)

    def test_online_choice_has_no_task_answer_or_history_parameter(self):
        self.assertEqual(tuple(inspect.signature(M.select).parameters),
                         ("memory", "event", "index", "used_deviation",
                          "pack", "native", "f99"))
        self.assertEqual(tuple(inspect.signature(M.online).parameters),
                         ("stream", "pack", "native", "f99", "trace"))

    def test_retained_singletons_reconstruct_signed_events_without_history(self):
        b = ((10, 11, (0,)), (21, 22, (3,)), (11, 12, (2,)))
        events = M.singleton_self_replay_events(b, EVENT)
        self.assertEqual(events[0], EVENT)
        self.assertIn((10, 0, 11), events)
        self.assertIn((22, 1, 21), events)
        self.assertEqual(len(events), len(set(events)))
        self.assertLessEqual(len(events), 12)

    def test_strict_short_equivalence_allows_disjoint_atomic_long_record(self):
        records, used, details = self.select()
        self.assertTrue(used)
        self.assertEqual(records, EXTENDED)
        self.assertTrue(details["intervened"])
        self.assertEqual(details["selected_native_action_index"], 1)
        self.assertEqual(details["replay_pass"], 1)

    def test_new_short_terminals_force_exact_f60(self):
        records, used, diag = self.select(DANGEROUS)
        self.assertEqual(records, BASE)
        self.assertFalse(used)
        self.assertEqual(diag["current_equal"], 0)
        self.assertEqual(diag["replay_pass"], 0)

    def test_replay_can_veto_current_equivalence_without_extra_history(self):
        rec, used, diag = self.select(
            native=FakeNative((EXTENDED,), corrupt_on_replay=True))
        self.assertEqual(rec, BASE)
        self.assertFalse(used)
        self.assertEqual(diag["current_equal"], 1)
        self.assertEqual(diag["long_gain_eligible"], 1)
        self.assertEqual(diag["replay_pass"], 0)

    def test_pure_f60_safely_selected_when_no_long_gain(self):
        rec, used, diag = self.select(BASE)
        self.assertEqual(rec, BASE)
        self.assertFalse(used)
        self.assertEqual(diag["native_alternatives"], 0)

    def test_used_latch_forbids_second_action(self):
        rec, used, diag = self.select(used=True)
        self.assertEqual(rec, BASE)
        self.assertTrue(used)
        self.assertFalse(diag["intervened"])

    def test_late_action_forbidden(self):
        rec, used, diag = self.select(index=48)
        self.assertEqual(rec, BASE)
        self.assertFalse(used)
        self.assertFalse(diag["intervened"])

    def test_reject_native_parity_ambiguity(self):
        with self.assertRaisesRegex(AssertionError,
                                    "F100_EXACT_F60_ACTION_PARITY"):
            self.select(native=FakeNative(duplicate_baseline=True))

    def test_bad_native_memory_fails_closed(self):
        too_large = BASE + tuple((300+i, 400+i, (0,)) for i in range(9))
        with self.assertRaises(AssertionError):
            self.select(native=FakeNative((too_large,)))

    def test_one_deviation_in_full_synthetic_stream(self):
        fake = FakeNative((EXTENDED,))
        memory, trace, stats = M.online(
            (EVENT for _ in range(72)), FakePack(), fake, REAL_F99,
            trace=True)
        self.assertEqual(memory, ())
        self.assertEqual(len(trace), 72)
        self.assertEqual(stats["interventions"], 0)
        self.assertEqual(stats["persistent_raw_event_history_bytes"], 0)
        self.assertEqual(stats["extra_latch_bits"], 1)
        self.assertLessEqual(stats["max_retained_native_bytes"], 144)

    def test_index_and_latch_type_rejected(self):
        for index in (-1, 72, 1.5):
            with self.assertRaises(ValueError):
                self.select(index=index)
        with self.assertRaises(ValueError):
            M.select(BASE, EVENT, 4, 1, FakePack(),
                     FakeNative(), REAL_F99)


if __name__ == "__main__":
    unittest.main()
