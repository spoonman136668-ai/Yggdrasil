"""Negative checks for strict nonnumeric and tolerant floating readout parity."""
import importlib.util
from pathlib import Path
import unittest
path = Path(__file__).with_name("parity.py")
spec = importlib.util.spec_from_file_location("ret02_parity", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ParityTests(unittest.TestCase):
    def test_one_ulp_floating_disagreement_reported_not_hidden(self):
        left = {"science_pass": False, "seed": 14071, "x": [0.185476009, 0.5]}
        right = {"science_pass": False, "seed": 14071,
                 "x": [0.18547600900000002, 0.5]}
        result = m.parity(left, right)
        self.assertEqual(result["different_float_count"], 1)
        self.assertTrue(0 < result["max_abs_delta"] <= m.TOLERANCE)

    def test_substantive_numeric_change_rejected(self):
        with self.assertRaisesRegex(ValueError, "PARITY_NUMERIC"):
            m.parity({"score": 0.15}, {"score": 0.16})

    def test_verdict_or_source_change_rejected(self):
        with self.assertRaisesRegex(ValueError, "PARITY_EXACT"):
            m.parity({"development_go": False}, {"development_go": True})
        with self.assertRaisesRegex(ValueError, "PARITY_EXACT"):
            m.parity({"source_id": "abcd"}, {"source_id": "abce"})

    def test_structure_and_count_changes_rejected(self):
        with self.assertRaisesRegex(ValueError, "PARITY_KEYS"):
            m.parity({"a": 1}, {"b": 1})
        with self.assertRaisesRegex(ValueError, "PARITY_COUNT"):
            m.parity({"x": [1]}, {"x": [1, 2]})
        with self.assertRaisesRegex(ValueError, "PARITY_TYPE"):
            m.parity({"x": True}, {"x": 1})

    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError, "PARITY_NONFINITE"):
            m.parity({"x": float("nan")}, {"x": 0.5})

if __name__ == "__main__":
    unittest.main()
