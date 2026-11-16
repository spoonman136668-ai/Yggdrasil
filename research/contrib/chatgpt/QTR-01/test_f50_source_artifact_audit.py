"""F50 source role-key artifact: fail-closed negatives, no target first use."""
import tempfile
import unittest
from pathlib import Path

import f50_source_artifact_audit as q
import f50_worlds as world


class F50SourceArtifactCustodyTests(unittest.TestCase):
    def test_retained_archive_roles_and_source_protocol(self):
        self.assertEqual(q.ARTIFACT_ID, 14185250784)
        self.assertEqual(q.ARTIFACT_RUN_ID, 43771961699)
        self.assertEqual(len(q.ROLES), 3)
        self.assertEqual(len(q.NAMES), 4)
        self.assertEqual(tuple(q.ROLES),
                         ("graph_conditioned_gru", "law_conditioned_set_mlp",
                          "graph_conditioned_logistic"))
        self.assertEqual(q.PREREG, world.PREREG_BLOB)
        self.assertEqual(q.SOURCE_DATA,
                         "5ffae27d69f20188f9fe987b2139cf6a8ca17be74875da269e4caaea8c9ce369")
        self.assertNotIn("target_ast", q.__dict__)
        self.assertNotIn("PrivateTargetEvaluator", q.__dict__)

    def test_missing_extra_mock_or_tampered_artifact_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            with self.assertRaisesRegex(q.AuditRejected, "EXACT_FILE_INVENTORY"):
                q.audit(folder)
            for name in q.NAMES:
                (folder / name).write_bytes(b"untrained fixture")
            with self.assertRaisesRegex(q.AuditRejected, "DIGEST_MISMATCH"):
                q.audit(folder)
            (folder / "target-truth.json").write_text("{}")
            with self.assertRaisesRegex(q.AuditRejected, "EXACT_FILE_INVENTORY"):
                q.audit(folder)

    def test_duplicate_key_and_bad_digest_rejected(self):
        with self.assertRaisesRegex(q.AuditRejected, "DUPLICATE_RECEIPT_KEY"):
            q.no_duplicate_keys([("scientific_pass", False),
                                 ("scientific_pass", True)])
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "model.npz"
            p.write_bytes(b"fake")
            with self.assertRaisesRegex(q.AuditRejected, "DIGEST_MISMATCH"):
                q.pinned_bytes(p, "f" * 64, 1000)
            with self.assertRaisesRegex(q.AuditRejected, "UNBOUNDED_FILE"):
                q.pinned_bytes(p, "f" * 64, 3)

    def test_original_training_source_math_role_verification(self):
        original = q.reconciliation.verify_role_semantics()
        self.assertTrue(original["source_program_changed_for_logistic"])
        self.assertEqual(len(original["neural_source_math_sha256"]), 64)
        self.assertEqual(q.CANDIDATE,
                         "4f02269f7a21d0207bfb335d1c435b9037a9d07a")


if __name__ == "__main__":
    unittest.main()
