"""F99P native closure / frozen F85 solver interface regression (no cohorts).

The query appears only in an *offline test assertion*. F99's candidate
eligibility remains query-blind. This demonstrates that local path preservation
is a necessary-condition screen, not a final-answer safety guarantee.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
F99_BLOB = "5de08fe74eb74dd917a7559cc3a8755185aac823"
F85_BLOB = "e4eb4bfbd6a01212f8c1eebc38af09b15c6d9cc3"


def load_frozen(name, file, expected):
    raw = Path(file).read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if actual != expected:
        raise AssertionError(f"F99_F85_INTERFACE_SOURCE_DRIFT:{name}")
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C = load_frozen("f99_f85_interface_closure", HERE / "causal_closure.py", F99_BLOB)
F85 = load_frozen("f99_f85_interface_global_solver",
                  ROOT / "20261016-y-f85" / "global_solver.py", F85_BLOB)


class Codec:
    """The same six-role, twelve-byte codec semantics as F85's pure tests."""

    def pack(self, a, b, codes):
        assert 0 <= a < 2**32 and 0 <= b < 2**32 and 1 <= len(codes) <= 6
        payload = sum(code << (i * 3) for i, code in enumerate(codes))
        return a.to_bytes(4, "little") + b.to_bytes(4, "little") + (
            payload.to_bytes(3, "little") + bytes((len(codes),))
        )

    def unpack(self, record):
        a = int.from_bytes(record[:4], "little")
        b = int.from_bytes(record[4:8], "little")
        payload = int.from_bytes(record[8:11], "little")
        length = record[11]
        return a, b, tuple((payload >> (i * 3)) & 7 for i in range(length))

    def mirrored(self, record):
        a, b, codes = record
        return b, a, tuple(code ^ 1 for code in reversed(codes))


BASELINE = (
    (10, 11, (0,)), (11, 12, (2,)), (12, 13, (4,)),
    (13, 14, (6,)),
)
SAFE_EXTENSION = BASELINE + ((14, 15, (0,)), (15, 16, (2,)))
AMBIGUOUS_EXTENSION = BASELINE + (
    (10, 21, (0,)), (21, 22, (2,)), (22, 23, (4,)),
    (23, 24, (6,)), (14, 15, (0,)), (15, 16, (2,)),
)
FOUR_STEP_QUESTION = dict(
    start=10, ops=((0, 1), (1, 1), (2, 1), (3, 1))
)


class F99F85InterfaceTests(unittest.TestCase):
    def test_preserved_short_paths_and_novel_long_paths_can_remain_correct(self):
        comparison = C.eligible_closure(BASELINE, SAFE_EXTENSION)
        self.assertTrue(comparison["eligible"])
        self.assertEqual(comparison["four_hop_signatures_lost"], 0)
        answer, details = F85.solve_global(
            SAFE_EXTENSION, FOUR_STEP_QUESTION, Codec()
        )
        self.assertEqual(answer, 14)
        self.assertFalse(details["resource_cap_triggered"])

    def test_closure_eligibility_does_not_guarantee_f85_correctness(self):
        comparison = C.eligible_closure(BASELINE, AMBIGUOUS_EXTENSION)
        self.assertTrue(comparison["eligible"])
        self.assertEqual(comparison["four_hop_signatures_lost"], 0)
        self.assertGreater(comparison["novel_five_six_hop_signatures"], 0)
        baseline_answer, baseline_diag = F85.solve_global(
            BASELINE, FOUR_STEP_QUESTION, Codec()
        )
        modified_answer, modified_diag = F85.solve_global(
            AMBIGUOUS_EXTENSION, FOUR_STEP_QUESTION, Codec()
        )
        self.assertEqual(baseline_answer, 14)
        self.assertEqual(baseline_diag["distinct_final_endpoints"], 1)
        self.assertIsNone(modified_answer)
        self.assertEqual(modified_diag["distinct_final_endpoints"], 2)
        self.assertFalse(modified_diag["resource_cap_triggered"])
        self.assertLessEqual(modified_diag["persistent_memory_bytes"], 144)

    def test_same_path_ends_and_signed_orientation_are_query_consistent(self):
        arcs = C.native_arcs(BASELINE)
        self.assertIn((11, (0,)), arcs[10])
        self.assertIn((10, (1,)), arcs[11])
        found = C.closure(BASELINE, max_hops=4)
        self.assertIn((10, (0, 2, 4, 6), 14), found)
        self.assertIn((14, (7, 5, 3, 1), 10), found)


if __name__ == "__main__":
    unittest.main()
