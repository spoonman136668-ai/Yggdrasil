"""CAP04 v2 exact-source Git custody gate; engineering tests only."""
import importlib.util
from pathlib import Path
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/contrib/chatgpt/YGG-CAP04/source_ref_attestation.py"
SPEC = importlib.util.spec_from_file_location("cap04_source_ref_attestation", SOURCE)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class SourceRefPreflightTests(unittest.TestCase):
    def test_pinned_source_and_prereg_readonly_attestation(self):
        proof = audit.verify_source_refs(ROOT)
        self.assertEqual(proof["classification"], "ENGINEERING_SOURCE_REFS_ONLY")
        self.assertEqual(proof["anchor_commit"],
                         "5d6a04843c53507b316d94993faafcf08dc04afc")
        self.assertEqual(proof["anchor_tree"],
                         "571cdb44c17cedb0ef6aa35bac9c0a198ae4760a")
        self.assertEqual(proof["protected_first_use"], "LOCKED")
        self.assertEqual(proof["owner_entropy_custody"], "UNVERIFIED")
        self.assertEqual(proof["scientific_efficacy"], "UNVERIFIED")
        self.assertEqual(proof["owner_source_acceptance"], "UNVERIFIED")
        self.assertEqual(set(proof["verified_git_blobs"]), set(audit.BLOBS))
        self.assertTrue(set(proof["changed_paths"]).issubset(
            audit.ALLOWED_DESCENDANT_CHANGES))
        self.assertNotIn("private_key", str(proof))
        self.assertEqual(proof, audit.verify_source_refs(ROOT))

    def test_wrong_pinned_tree_rejected(self):
        with patch.object(audit, "ANCHOR_TREE", "0" * 40):
            with self.assertRaisesRegex(ValueError, "CAP04_REF_ANCHOR_TREE"):
                audit.verify_source_refs(ROOT)

    def test_wrong_prereg_or_source_blob_rejected(self):
        for name in ("research/contrib/chatgpt/YGG-CAP04/prereg.json",
                     "research/contrib/chatgpt/YGG-CAP04/prospective_source_v2.py"):
            altered = dict(audit.BLOBS)
            altered[name] = "0" * 40
            with self.subTest(path=name), patch.object(audit, "BLOBS", altered):
                with self.assertRaisesRegex(ValueError, "CAP04_REF_SOURCE_BLOB_DRIFT"):
                    audit.verify_source_refs(ROOT)

    def test_unexpected_delta_rejected(self):
        real = audit._git

        def substituted(root, *args):
            if args and args[0] == "diff":
                return "research/contrib/chatgpt/YGG-CAP04/prereg.json"
            return real(root, *args)

        with patch.object(audit, "_git", substituted):
            with self.assertRaisesRegex(ValueError, "CAP04_REF_UNEXPECTED_DELTA"):
                audit.verify_source_refs(ROOT)

    def test_dirty_worktree_rejected(self):
        real = audit._git

        def substituted(root, *args):
            if args and args[0] == "status":
                return " M research/contrib/chatgpt/YGG-CAP04/prereg.json"
            return real(root, *args)

        with patch.object(audit, "_git", substituted):
            with self.assertRaisesRegex(ValueError, "CAP04_REF_DIRTY_WORKTREE"):
                audit.verify_source_refs(ROOT)

    def test_git_access_failure_closed(self):
        with patch.object(audit, "_git", side_effect=ValueError(
                "CAP04_REF_GIT_UNAVAILABLE")):
            with self.assertRaisesRegex(ValueError, "CAP04_REF_GIT_UNAVAILABLE"):
                audit.verify_source_refs(ROOT)


if __name__ == "__main__":
    unittest.main()
