"""Negative G36 receipt-custody tests; transient synthetic bytes never evidence."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ygg_db01_g36", HERE / "g36_originals.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class G36OriginalReceiptChecks(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((HERE / "g36_evidence_index.json").read_text("utf-8"))

    def test_real_proposed_index_missing_without_invented_custody(self):
        result = module.inspect(copy.deepcopy(self.index), HERE)
        self.assertEqual(result["status"], "MISSING_ORIGINAL_RECEIPTS")
        self.assertEqual(len(result["missing_original_receipts"]), 9)
        self.assertEqual(result["verified_receipt_byte_hashes"], [])
        self.assertFalse(result["original_source_authenticated"])
        self.assertFalse(result["independent_custody_authenticated"])
        self.assertFalse(result["primary_execution_allowed"])
        self.assertEqual(len(result["g35_plan_sha256"]), 64)

    def test_all_authority_raises_fail_closed(self):
        for field in self.index["authority"]:
            candidate = copy.deepcopy(self.index)
            candidate["authority"][field] = True
            with self.assertRaisesRegex(ValueError, "authority"):
                module.inspect(candidate, HERE)
        candidate = copy.deepcopy(self.index)
        candidate["status"] = "FROZEN"
        with self.assertRaisesRegex(ValueError, "status"):
            module.inspect(candidate, HERE)

    def prepare_synthetic(self, root, complete=False):
        root = Path(root)
        (root / "originals").mkdir()
        original_plan = (HERE / "g35_candidate.json").read_bytes()
        (root / "g35_candidate.json").write_bytes(original_plan)
        idx = copy.deepcopy(self.index)
        idx["g35_candidate_sha256"] = hashlib.sha256(original_plan).hexdigest()
        slots = module.SLOTS if complete else module.SLOTS[:1]
        first = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for i, slot in enumerate(slots):
            # Synthetic only, ephemeral test data; not a historical custody receipt.
            data = json.dumps({"test_only": slot}, sort_keys=True).encode()
            (root / "originals" / (slot + ".json")).write_bytes(data)
            idx["records"][slot] = {
                "path": "originals/" + slot + ".json",
                "sha256": hashlib.sha256(data).hexdigest(),
                "original_ref": "https://github.com/example/synthetic/blob/" +
                                "1" * 40 + "/" + slot + ".json",
                "actor": "synthetic-test-only",
                "recorded_at_utc": (first + timedelta(days=i)).isoformat()
                                   .replace("+00:00", "Z")
            }
        return idx

    def test_partial_bytes_verify_without_custody_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.prepare_synthetic(tmp)
            status = module.inspect(idx, tmp)
            self.assertEqual(status["status"], "MISSING_ORIGINAL_RECEIPTS")
            self.assertEqual(status["verified_receipt_byte_hashes"],
                             ["task_manifest"])
            self.assertFalse(status["original_source_authenticated"])
            self.assertFalse(status["primary_execution_allowed"])

    def test_hash_tampering_and_injected_path_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.prepare_synthetic(tmp)
            path = Path(tmp) / "originals" / "task_manifest.json"
            path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                module.inspect(idx, tmp)
            idx["records"]["task_manifest"]["path"] = "../../secrets.json"
            with self.assertRaisesRegex(ValueError, "unbound original"):
                module.inspect(idx, tmp)

    def test_missing_source_reference_and_unpinned_plan_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.prepare_synthetic(tmp)
            idx["records"]["task_manifest"]["original_ref"] = (
                "https://github.com/example/synthetic/blob/main/task_manifest.json")
            with self.assertRaisesRegex(ValueError, "unbound original"):
                module.inspect(idx, tmp)
            idx = self.prepare_synthetic_existing(tmp)
            idx["g35_candidate_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "G35 plan hash"):
                module.inspect(idx, tmp)

    def prepare_synthetic_existing(self, root):
        idx = self.prepare_synthetic_reuse(root)
        return idx

    def prepare_synthetic_reuse(self, root):
        # No second mkdir when reusing the test fixture root.
        idx = copy.deepcopy(self.index)
        idx["g35_candidate_sha256"] = hashlib.sha256(
            (Path(root) / "g35_candidate.json").read_bytes()).hexdigest()
        return idx

    def test_even_complete_synthetic_bytes_cannot_authorize_science(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.prepare_synthetic(tmp, complete=True)
            status = module.inspect(idx, tmp)
            self.assertEqual(status["status"], "HASHES_MATCH_AUTHENTICITY_UNVERIFIED")
            self.assertEqual(len(status["verified_receipt_byte_hashes"]), 9)
            self.assertFalse(status["original_source_authenticated"])
            self.assertFalse(status["independent_custody_authenticated"])
            self.assertFalse(status["receipt_actor_and_time_independently_verified"])
            self.assertFalse(status["scientific_acceptance_allowed"])
            self.assertFalse(status["primary_execution_allowed"])

    def test_seal_release_order_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = self.prepare_synthetic(tmp, complete=True)
            idx["records"]["label_release_receipt"]["recorded_at_utc"] = (
                idx["records"]["prediction_seal_receipt"]["recorded_at_utc"])
            with self.assertRaisesRegex(ValueError, "ordering"):
                module.inspect(idx, tmp)

    def test_missing_receipt_or_extra_slot_denied(self):
        idx = copy.deepcopy(self.index)
        del idx["records"]["label_release_receipt"]
        with self.assertRaisesRegex(ValueError, "slot"):
            module.inspect(idx, HERE)
        idx = copy.deepcopy(self.index)
        idx["untrusted_promote"] = True
        with self.assertRaisesRegex(ValueError, "schema"):
            module.inspect(idx, HERE)


if __name__ == "__main__":
    unittest.main()
