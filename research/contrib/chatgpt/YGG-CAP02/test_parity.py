"""CAP02 learned-weight cross-platform tolerance cannot hide source corruption."""
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("cap02_parity",HERE/"parity.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class CAP02ParityTests(unittest.TestCase):
    def test_floating_ulp_disclosed(self):
        r=mod.compare({"brier":[.125]},{"brier":[.12500000000000003]})
        self.assertEqual(r["numeric_count"],1)
        self.assertGreater(r["max_abs_difference"],0)

    def test_scientific_and_public_source_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,"EXACT_SOURCE_OR_VERDICT"):
            mod.compare({"development_go":False},{"development_go":True})
        with self.assertRaisesRegex(ValueError,"EXACT_SOURCE_OR_VERDICT"):
            mod.compare({"phase":"A"},{"phase":"B"})
        with self.assertRaisesRegex(ValueError,"EXACT_SOURCE_OR_VERDICT"):
            mod.compare({"source_id":"a"*64},{"source_id":"b"*64})

    def test_expected_os_original_pins_cannot_be_replaced(self):
        a={"replicas":[{"old_training_checkpoint_sha256":
             mod.PARENT_SHA_PAIRS[0][0]}]}
        b={"replicas":[{"old_training_checkpoint_sha256":
             mod.PARENT_SHA_PAIRS[0][1]}]}
        self.assertEqual(len(mod.compare(a,b)["original_source_receipts"]),1)
        with self.assertRaisesRegex(ValueError,"ORIGINAL_PUBLISHED_SOURCE_SHA"):
            mod.compare(a,{"replicas":[{"old_training_checkpoint_sha256":
                                  "f"*64}]})

    def test_new_trained_shas_retained_not_forged_to_match(self):
        a={"replicas":[{"native_continued_sha256":"a"*64}]}
        b={"replicas":[{"native_continued_sha256":"b"*64}]}
        self.assertEqual(len(mod.compare(a,b)["trained_sha_receipts"]),1)
        with self.assertRaisesRegex(ValueError,"TRAINED_SHA_FORMAT"):
            mod.compare(a,{"replicas":[{"native_continued_sha256":"x"*64}]})

    def test_source_dimensions_and_large_drift_rejected(self):
        with self.assertRaisesRegex(ValueError,"FIELDS"):
            mod.compare({"a":1},{"b":1})
        with self.assertRaisesRegex(ValueError,"COUNT"):
            mod.compare({"events":[1]},{"events":[1,2]})
        with self.assertRaisesRegex(ValueError,"FLOAT_DRIFT"):
            mod.compare({"error":.12},{"error":.13})

    def test_checkpoint_byte_size_bounded_and_reported(self):
        a={"native_checkpoint_bytes":250000}
        b={"native_checkpoint_bytes":250006}
        self.assertEqual(
            mod.compare(a,b)["checkpoint_byte_receipts"][0]["difference"],6)
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_BYTE_SIZE"):
            mod.compare(a,{"native_checkpoint_bytes":400000})

if __name__=="__main__":
    unittest.main()
