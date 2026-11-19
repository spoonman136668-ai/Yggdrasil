"""Reject weaker source/decision custody disguised as numeric portability."""
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("cap01_parity",HERE/"parity.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CapacityParityTests(unittest.TestCase):
    def test_subulp_numeric_difference_disclosed(self):
        result=m.compare({"brier":0.12500000000000000},
                         {"brier":0.12500000000000003})
        self.assertEqual(result["different_numeric_fields"],1)
        self.assertTrue(0 < result["max_abs_numeric_difference"]<1e-8)

    def test_science_or_source_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_OR_VERDICT"):
            m.compare({"scientific_pass":False},{"scientific_pass":True})
        with self.assertRaisesRegex(ValueError,"SOURCE_OR_VERDICT"):
            m.compare({"old_source_sha256":"a"*64},
                      {"old_source_sha256":"b"*64})

    def test_root_structure_and_large_numeric_drift_rejected(self):
        with self.assertRaisesRegex(ValueError,"KEYS"):
            m.compare({"a":1},{"b":1})
        with self.assertRaisesRegex(ValueError,"COUNT"):
            m.compare({"events":[1]},{"events":[1,2]})
        with self.assertRaisesRegex(ValueError,"FLOAT"):
            m.compare({"loss":0.1},{"loss":0.2})

    def test_only_continuing_weights_sha_are_permitted_to_differ(self):
        r=m.compare({"continued_sha256":"a"*64},{"continued_sha256":"b"*64})
        self.assertEqual(len(r["learned_checkpoint_sha_differences"]),1)
        with self.assertRaisesRegex(ValueError,"SOURCE_OR_VERDICT"):
            m.compare({"source_git_blob":"a"*64},{"source_git_blob":"b"*64})

if __name__=="__main__":
    unittest.main()
