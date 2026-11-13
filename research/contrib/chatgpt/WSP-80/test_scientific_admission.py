"""WSP80 prereg/source first-use static admission; no registered sources loaded."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).parent))
from scientific_admission import (audit_static_readonly, validate_frozen_protocol,
                                  PINNED, PRE_COMMIT, PARENT)


class StaticAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        cls.data = json.loads(Path(__file__).with_name("prereg.json").read_text())

    def test_frozen_protocol_valid_and_16_registered_seeds_not_run(self):
        self.assertTrue(validate_frozen_protocol(self.data))
        self.assertEqual(self.data["source"]["seeds"], list(range(5601, 5617)))
        self.assertEqual(len(PINNED), 3)

    def test_false_changed_authority_rejected(self):
        data = {**self.data, "authority": {**self.data["authority"],
                                            "protected_scientific_first_use": True}}
        with self.assertRaises(PermissionError):
            validate_frozen_protocol(data)

    def test_changed_threshold_and_seed_rejected(self):
        data = {**self.data, "frozen_thresholds": {
            **self.data["frozen_thresholds"],
            "candidate_train_infer_CPU_over_MLP_train_infer_max": 3}}
        with self.assertRaises(ValueError):
            validate_frozen_protocol(data)
        data = {**self.data, "source": {**self.data["source"],
                                       "seeds": list(range(5601, 5616))}}
        with self.assertRaises(ValueError):
            validate_frozen_protocol(data)

    def test_real_readonly_git_admission_and_no_first_use_claim(self):
        audit = audit_static_readonly()
        self.assertEqual(audit["read_only_git_source_identity"], "PASS")
        self.assertEqual(audit["wsp79_parent_sha"], PARENT)
        self.assertEqual(audit["prereg_first_commit"], PRE_COMMIT)
        self.assertFalse(audit["historic_consumption_ledger_authenticated"])
        self.assertFalse(audit["registered_source_first_use_authorized"])

    def test_pr_checkout_head_mismatch_fails_closed(self):
        import os
        with patch.dict(os.environ, {
                "GITHUB_EVENT_NAME": "pull_request",
                "WSP80_CHECKOUT_HEAD_SHA": "0" * 40}):
            with self.assertRaisesRegex(RuntimeError, "exact checkout SHA mismatch"):
                audit_static_readonly()

    def test_never_imports_or_executes_registered_source_generator(self):
        code = Path(__file__).with_name("scientific_admission.py").read_text()
        self.assertNotIn("from source import", code)
        self.assertNotIn("import source", code)
        self.assertNotIn("build_world(", code)
        self.assertNotIn("training_session(", code)


if __name__ == "__main__":
    unittest.main()
