"""Source/decision parity must not be weakened to hide science failures."""
import importlib.util
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("jepa205_parity",HERE/"parity.py")
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

class CrossOSParity(unittest.TestCase):
    def test_tiny_rounding_is_disclosed(self):
        x={"x":[0.20000000000000001]}
        y={"x":[0.20000000000000012]}
        r=m.compare(x,y)
        self.assertEqual(r["number_differences"],1)
        self.assertGreater(r["max_abs_diff"],0)

    def test_science_and_seed_disagreement_are_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"PARITY_EXACT"):
            m.compare({"development_go":False},{"development_go":True})
        with self.assertRaisesRegex(ValueError,"PARITY_EXACT"):
            m.compare({"seed":99231},{"seed":99247})

    def test_source_and_receipt_shape_must_match(self):
        with self.assertRaisesRegex(ValueError,"PARITY_KEYS"):
            m.compare({"phase":"A"},{"world":"A"})
        with self.assertRaisesRegex(ValueError,"PARITY_COUNT"):
            m.compare({"events":[1]},{"events":[1,2]})

    def test_large_numeric_deviation_rejected(self):
        with self.assertRaisesRegex(ValueError,"PARITY_FLOAT"):
            m.compare({"score":.13},{"score":.15})

    def test_only_designated_learned_weight_shas_can_differ(self):
        sha0="a"*64
        sha1="b"*64
        self.assertEqual(len(m.compare({"updated_model_sha256":sha0},
                                       {"updated_model_sha256":sha1})
                             ["sha_difference_fields"]),1)
        with self.assertRaisesRegex(ValueError,"PARITY_EXACT"):
            m.compare({"original_model_sha256":sha0},
                      {"original_model_sha256":sha1})

    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,"PARITY_NONFINITE"):
            m.compare({"x":float("nan")},{"x":0.1})

if __name__=="__main__":
    unittest.main()
