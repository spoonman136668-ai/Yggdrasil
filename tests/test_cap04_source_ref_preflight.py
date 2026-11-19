"""CAP04 source-reference preflight; original registered first use stays locked."""
import importlib.util
from dataclasses import replace
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/contrib/chatgpt/YGG-CAP04/source_ref_preflight.py"
spec = importlib.util.spec_from_file_location("cap04_ref_preflight", SOURCE)
a = importlib.util.module_from_spec(spec)
# Dataclasses consult sys.modules for their module's namespace.
import sys
sys.modules[spec.name] = a
spec.loader.exec_module(a)


class SourceReferencePreflightTests(unittest.TestCase):
    def test_pinned_git_candidate_and_cold_prereg_verified_without_secret(self):
        receipt = a.verify_source_references(ROOT)
        self.assertEqual(receipt["schema"], a.SCHEMA)
        self.assertEqual(receipt["status"], "PUBLIC_SOURCE_REF_VERIFIED_ONLY")
        self.assertFalse(receipt["registered_first_use_authorized"])
        self.assertFalse(receipt["private_entropy_custody_verified"])
        self.assertFalse(receipt["owner_source_key_uniqueness_verified"])
        self.assertFalse(receipt["scientific_effectiveness_verified"])
        self.assertEqual(receipt, json.loads(json.dumps(receipt)))
        self.assertTrue(all("secret" not in key and "entropy" not in key
                            or key == "private_entropy_custody_verified"
                            for key in receipt))

    def test_wrong_public_ref_tree_blob_and_freeze_rejected(self):
        invalid = [
            replace(a.FROZEN, candidate_sha="0" * 40),
            replace(a.FROZEN, candidate_tree_sha="0" * 40),
            replace(a.FROZEN, source_blob_sha="0" * 40),
            replace(a.FROZEN, prereg_blob_sha="0" * 40),
            replace(a.FROZEN, prereg_freeze_commit="0" * 40),
            replace(a.FROZEN, cap03_source_blob_sha="0" * 40),
        ]
        for frozen in invalid:
            with self.subTest(frozen=frozen), self.assertRaises(ValueError):
                a.verify_source_references(ROOT, frozen)

    def test_malformed_shas_wrong_path_and_public_approval_rejected(self):
        for value in (None, "", False, 42, "A" * 40, "f" * 39,
                      "f" * 41, "0" * 20 + ":source"):
            with self.assertRaisesRegex(ValueError, "INVALID_SHA"):
                a.validate_sha(value)
        with self.assertRaisesRegex(ValueError, "REPOSITORY_ROOT"):
            a.verify_source_references(ROOT / "not-a-repo")
        receipt = a.verify_source_references(ROOT)
        with self.assertRaisesRegex(ValueError, "FIRST_USE_NOT_AUTHORIZED"):
            a.prevent_public_receipt_promotion(receipt)
        for forged in (
            dict(receipt, registered_first_use_authorized=True),
            dict(receipt, private_entropy_custody_verified=True),
            dict(receipt, schema="wrong"),
        ):
            with self.assertRaisesRegex(ValueError, "INVALID_PUBLIC_RECEIPT"):
                a.prevent_public_receipt_promotion(forged)


if __name__ == "__main__":
    unittest.main()
