"""Check independent conventional eligibility implementation and source pins."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

DIR = (Path(__file__).resolve().parents[1] /
       "research/contrib/chatgpt/WSCM-TRACE-01")
SPEC = spec_from_file_location("wscm_trace_01", DIR / "trial.py")
TRIAL = module_from_spec(SPEC)
SPEC.loader.exec_module(TRIAL)


class TraceControlTests(unittest.TestCase):
    def test_deterministic_q15_lambda_decay(self):
        events = [(i, i + 100, 0, i % 16) for i in range(16)]
        result = TRIAL.conventional_trace(events, 15, 1)
        self.assertEqual(len(result), 16)
        self.assertEqual(result[-1], (15, 15, 0, 32768, 256))
        self.assertEqual(result[-2], (14, 14, 1, 16384, 256))
        self.assertEqual(result[0], (0, 0, 15, 1, 256))

    def test_negative_no_surprise_and_expired_target(self):
        events = [(i, i + 100, 192, i % 16) for i in range(17)]
        self.assertIsNone(TRIAL.conventional_trace(events, 0, 1))
        self.assertEqual(TRIAL.conventional_trace(events, 16, 1), ())

    def test_source_blob_pinned(self):
        path = DIR.parent / "CAUSAL-AMALGAM" / "wscm01_delayed_credit.py"
        self.assertEqual(TRIAL.git_blob_sha(path), TRIAL.RING_BLOB)


if __name__ == "__main__":
    unittest.main()
