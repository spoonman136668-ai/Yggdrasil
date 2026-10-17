"""F99P pure tests: no cohort reads, no learned policy, no protected inputs."""
from __future__ import annotations

import importlib.util
import inspect
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("f99_closure_under_test", HERE / "causal_closure.py")
C = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = C
spec.loader.exec_module(C)

BASE = (
    (10, 11, (0,)),
    (11, 12, (2,)),
    (12, 13, (4,)),
    (13, 14, (6,)),
)
EXTENDED = BASE + (
    (14, 15, (0,)),
    (15, 16, (2,)),
)


class FakePack:
    def pack(self, src, target, roles):
        assert type(src) is int and type(target) is int and roles
        return bytes(12)


class FakeNative:
    def _f60_step(self, memory, event, pack):
        return BASE

    def actions(self, memory, event, index, pack):
        return (
            ("append", -1, -1, BASE, ()),
            ("merge", 1, -1, EXTENDED, ()),
        )

    def _valid_memory(self, memory, pack):
        assert len(memory) <= 12
        for row in memory:
            assert len(pack.pack(*row)) == 12


class Tests(unittest.TestCase):
    def test_signed_reverse_order_and_direction(self):
        self.assertEqual(C.signed_reverse((0, 3, 6)), (7, 2, 1))
        self.assertEqual(C.signed_reverse(C.signed_reverse((0, 3, 6))), (0, 3, 6))

    def test_endpoint_join_and_role_order(self):
        found = C.closure(BASE, max_hops=4)
        self.assertIn((10, (0, 2, 4, 6), 14), found)
        self.assertIn((14, (7, 5, 3, 1), 10), found)

    def test_disconnected_endpoints_never_join(self):
        found = C.closure(((10, 11, (0,)), (20, 21, (2,))))
        self.assertNotIn((10, (0, 2), 21), found)

    def test_atomic_native_multirole_record_has_no_fake_internal_vertex(self):
        found = C.closure(((10, 20, (0, 2, 4)),))
        self.assertIn((10, (0, 2, 4), 20), found)
        self.assertNotIn((10, (0,), 20), found)

    def test_four_hop_closure_preserved_with_novel_six_hop(self):
        result = C.eligible_closure(BASE, EXTENDED)
        self.assertTrue(result["short_signatures_preserved"])
        self.assertEqual(result["four_hop_signatures_lost"], 0)
        self.assertGreater(result["novel_five_six_hop_signatures"], 0)
        self.assertTrue(result["eligible"])

    def test_hard_loss_gate_rejects_novelty_with_erasure(self):
        damaging = BASE[:2] + tuple((30+i, 31+i, (2*(i%4),)) for i in range(6))
        result = C.eligible_closure(BASE, damaging)
        self.assertGreater(result["four_hop_signatures_lost"], 0)
        self.assertGreater(result["novel_five_six_hop_signatures"], 0)
        self.assertFalse(result["eligible"])

    def test_memory_record_and_signature_caps_fail_closed(self):
        with self.assertRaises(ValueError):
            C.closure(tuple((i, i + 1, (0,)) for i in range(13)))
        with self.assertRaises(C.ClosureLimitExceeded):
            C.closure(((1, 2, (0,)),), max_signatures=1)

    def test_illegal_codes_and_endpoints_fail_closed(self):
        with self.assertRaises(ValueError):
            C.closure(((1, 2, (8,)),))
        with self.assertRaises(ValueError):
            C.closure(((1, 1, (0,)),))

    def test_native_action_screen_has_no_question_or_future_input(self):
        self.assertEqual(tuple(inspect.signature(C.audit_native_prefix).parameters),
                         ("memory", "event", "index", "pack", "native"))
        baseline, alternatives = C.audit_native_prefix(
            (), (99, 0, 100), 12, FakePack(), FakeNative())
        self.assertEqual(baseline, BASE)
        self.assertEqual(len(alternatives), 1)
        self.assertTrue(alternatives[0]["eligible"])

    def test_f60_native_parity_rejection(self):
        class FakeDuplicate(FakeNative):
            def actions(self, *args):
                return super().actions(*args) + (("bad", 0, 0, BASE, ()),)
        with self.assertRaisesRegex(AssertionError, "F99_NATIVE_F60_PARITY"):
            C.audit_native_prefix((), (99, 0, 100), 9, FakePack(), FakeDuplicate())


if __name__ == "__main__":
    unittest.main()
