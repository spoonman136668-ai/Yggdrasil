"""F50 source checkpoint reuse must be semantically qualified and fail closed.

No F50 target AST, target law, protected outcomes or new source FIT are opened
by this test module.
"""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import f50_source_reconcile as q
import f50_source_fit as sf
import f50_conventional_controls as c
import f50_worlds as world


class TestF50SourceRoleReuse(unittest.TestCase):
    def test_exact_old_new_math_roles_and_frozen_source(self):
        x=q.verify_role_semantics()
        self.assertTrue(x["source_program_changed_for_logistic"])
        self.assertEqual(len(x["f50_prereg.json"]),64)
        self.assertEqual(world.freeze()["schema"],
                         "yggdrasil.qtr01.f50.law-conditioned-association-transfer.prereg.v1")
        self.assertEqual(len(x["neural_source_math_sha256"]),64)
        self.assertEqual(len(x["current_logistic_source_sha256"]),64)
        self.assertNotEqual(x["neural_source_math_sha256"],
                            x["current_logistic_source_sha256"])
        self.assertEqual(q.SOURCE_DATA_SHA256,
                         "5ffae27d69f20188f9fe987b2139cf6a8ca17be74875da269e4caaea8c9ce369")
        self.assertEqual(q.OLD_SOURCE,"0f62f98e1a8778e9d7afd8f229d8f5635ec7d3ee")
        self.assertEqual(q.NEW_SOURCE,"def7e7a88517b9afadc6854bd7847d7e4a5d42e6")
        self.assertEqual(q.SCHEMA,"yggdrasil.qtr01.f50.role-key-reuse-source-only.v1")

    def test_neural_role_equivalence_aborts_if_math_changes(self):
        a=q.verify_role_semantics()
        with patch.object(q,"git_bytes",return_value=b"nonmatching"):
            with self.assertRaises(q.ReconcileRejected):
                q.verify_role_semantics()
        self.assertEqual(a["source_program_changed_for_logistic"],True)

    def test_old_or_new_receipt_drift_fails_before_any_fit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path=root/"f50-source-fit-receipt.json"
            path.write_bytes(b"{}")
            with self.assertRaisesRegex(q.ReconcileRejected,"BYTES_TAMPERED"):
                q.verify_prior_receipt(root,q.OLD_RECEIPT_SHA256,q.OLD_SOURCE,
                                       "ALL_THREE_SOURCE_ONLY_TRAINED",
                                       list(c.KINDS))
        self.assertEqual(q.OLD_ARTIFACT,14182614963)
        self.assertEqual(q.NEW_ARTIFACT,14184063472)
        self.assertEqual(q.MLP_SHA256,
                         "33e57b5fe4eea03f3b1778589776a9219dd1f9f51291577e54af0ad971e952e8")
        self.assertEqual(q.GRU_SHA256,
                         "334c562ba6c3b48f1ea8233e9a7efcb787b37fcaf38dd3d06c3d1bf4f5395ecf")

    def test_source_only_reconciliation_rejects_unfrozen_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            for sha in ("", "invalid", "a"*39):
                with self.assertRaises(q.ReconcileRejected):
                    q.reconcile(tmp,tmp,Path(tmp)/"out",sha,max_logistic_cpu=600)
            for limit in (0,601,True,-1):
                with self.assertRaises(q.ReconcileRejected):
                    q.reconcile(tmp,tmp,Path(tmp)/"out","a"*40,
                                max_logistic_cpu=limit)
        self.assertEqual(q.MAX_LOGISTIC_CPU_SECONDS,600)
        self.assertFalse(hasattr(q,"target_ast"))
        self.assertFalse(hasattr(q,"target_law"))
        self.assertFalse(hasattr(q,"evaluate_target"))

    def test_reserved_seeds_remain_unopened(self):
        with self.assertRaises(world.F50Rejected):
            world._check_dev_seed(4127)
        with self.assertRaises(world.F50Rejected):
            world._check_dev_seed(4159)
        self.assertEqual(world.PREREG_BLOB,
                         "4bd3c4e0d3de0e3910094e38c14a0141c97ad380")
        self.assertEqual(q.SOURCE_DIR,"research/contrib/chatgpt/QTR-01")


if __name__=="__main__":
    unittest.main()
