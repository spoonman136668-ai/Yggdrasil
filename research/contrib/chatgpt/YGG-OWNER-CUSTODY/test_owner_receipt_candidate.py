"""Only synthetic owner receipt integrity fixtures; no actual checkpoint accessed."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("owner_receipt_candidate_verify",HERE/"verify_owner_receipt_candidate.py")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

def sha(x):
    return hashlib.sha256(x).hexdigest()

def construct(root):
    data={
      "prior_checkpoint":b"fixture-model-source-old",
      "continued_checkpoint":b"fixture-model-source-old+action-feedback",
      "cold_restored_checkpoint":b"fixture-model-source-old+action-feedback",
      "prior_source_log":b"historical-observation-1\nhistorical-observation-2\n",
      "continued_source_log":b"historical-observation-1\nhistorical-observation-2\nnew-witnessed-feedback\n",
      "prior_capability_probe":b"old-relationship-readout-unchanged",
      "continued_prior_capability_probe":b"old-relationship-readout-unchanged"
    }
    for name,content in data.items():
        (root/name).write_bytes(content)
    manifest={
      "schema":M.SCHEMA,
      "source":{
       "repo":"spoonman136668-ai/Yggdrasil",
       "branch":M.PINNED_OWNER_BRANCH,
       "git_sha":M.PINNED_OWNER_SHA,
       "tree_sha":M.PINNED_OWNER_TREE
      },
      "scope":"research-only-candidate-integrity",
      "checkpoint_schema":"fixture.no-real-model.v1",
      "files":{name:{"bytes":len(v),"sha256":sha(v)} for name,v in data.items()},
      "lineage":{
        "parent_checkpoint_sha256":sha(data["prior_checkpoint"]),
        "continued_checkpoint_sha256":sha(data["continued_checkpoint"]),
        "original_source_log_sha256":sha(data["prior_source_log"]),
        "continued_source_log_sha256":sha(data["continued_source_log"]),
      },
      "old_ledger_entries":2,
      "new_ledger_entries":3,
      "external_owner_acceptance":None,
    }
    save(root,manifest)
    return manifest

def save(root,manifest):
    (root/"receipt.json").write_text(json.dumps(manifest,sort_keys=True),encoding="utf-8")

class OwnerReceiptIntakeFixtures(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="YGG-OWNER-READ-ONLY-FIXTURE-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.manifest=construct(self.root)

    def must_fail(self,code):
        with self.assertRaisesRegex(M.IntakeError,"YGG_OWNER_INTAKE_"+code):
            M.verify_bundle(self.root)

    def test_integrity_pass_does_not_mean_owner_science_or_acceptance(self):
        result=M.verify_bundle(self.root)
        self.assertEqual(result["status"],"INTEGRITY_CONSISTENT_BUT_UNTRUSTED")
        self.assertEqual(result["sha256_checked_roles"],7)
        self.assertTrue(result["prior_source_log_byte_prefix_exact"])
        self.assertTrue(result["cold_restored_checkpoint_byte_hash_equal"])
        self.assertTrue(result["old_probe_output_byte_hash_equal"])
        self.assertEqual(result["owner_authority"],"UNVERIFIED")
        self.assertEqual(result["accepted_owner_state"],"UNVERIFIED")
        self.assertEqual(result["native_learning_efficacy"],"UNVERIFIED")
        self.assertEqual(result["deployment"],"NONE")
        self.assertFalse(result["ledger_entry_counts_verified_against_event_parser"])

    def test_reject_attempt_to_self_claim_owner_acceptance(self):
        self.manifest["external_owner_acceptance"]={"accepted":True}
        save(self.root,self.manifest)
        self.must_fail("UNTRUSTED_ACCEPTANCE")

    def test_reject_wrong_main_or_owner_source_identity(self):
        self.manifest["source"]["git_sha"]="f"*40
        save(self.root,self.manifest)
        self.must_fail("SOURCE_NOT_PINNED")

    def test_reject_unexpected_key_and_untrusted_scope(self):
        self.manifest["elevated_authority"]=True
        save(self.root,self.manifest)
        self.must_fail("RECEIPT_KEYS")
        del self.manifest["elevated_authority"]
        self.manifest["scope"]="accepted-owner"
        save(self.root,self.manifest)
        self.must_fail("NO_ACCEPTANCE_AUTHORITY")

    def test_detect_checkpoint_changed_without_updating_digest(self):
        (self.root/"continued_checkpoint").write_bytes(b"fixture-tampered-model-with-same-size!!")
        self.must_fail("FILE_SIZE_CONTINUED_CHECKPOINT")

    def test_detect_cold_restore_cannot_match_tampered_checkpoint(self):
        value=b"not-an-identical-cold-restore"
        (self.root/"cold_restored_checkpoint").write_bytes(value)
        self.manifest["files"]["cold_restored_checkpoint"]={"bytes":len(value),"sha256":sha(value)}
        save(self.root,self.manifest)
        self.must_fail("COLD_RESTORE_NOT_IDENTICAL")

    def test_detect_prior_source_history_replacement(self):
        prev=(self.root/"prior_source_log").read_bytes()
        value=b"rewritten"+(self.root/"continued_source_log").read_bytes()[9:]
        self.assertEqual(len(value),(self.root/"continued_source_log").stat().st_size)
        (self.root/"continued_source_log").write_bytes(value)
        self.manifest["files"]["continued_source_log"]={"bytes":len(value),"sha256":sha(value)}
        self.manifest["lineage"]["continued_source_log_sha256"]=sha(value)
        save(self.root,self.manifest)
        self.must_fail("SOURCE_HISTORY_NOT_PREFIX")

    def test_detect_old_capability_readout_change_even_with_forged_new_digest(self):
        value=b"old-relationship-now-different"
        (self.root/"continued_prior_capability_probe").write_bytes(value)
        self.manifest["files"]["continued_prior_capability_probe"]={"bytes":len(value),"sha256":sha(value)}
        save(self.root,self.manifest)
        self.must_fail("PREVIOUS_CAPABILITY_PROBE_DRIFT")

    def test_reject_ledger_growth_claim_reverse_or_boolean(self):
        self.manifest["new_ledger_entries"]=1
        save(self.root,self.manifest)
        self.must_fail("LEDGER_ENTRY_COUNT_CLAIM")
        self.manifest["new_ledger_entries"]=True
        save(self.root,self.manifest)
        self.must_fail("LEDGER_ENTRY_COUNT_CLAIM")

    def test_reject_corrupt_digest_and_duplicate_json(self):
        self.manifest["files"]["prior_checkpoint"]["sha256"]="0"*64
        save(self.root,self.manifest)
        self.must_fail("FILE_HASH_PRIOR_CHECKPOINT")
        (self.root/"receipt.json").write_text('{"schema":"x","schema":"y"}',encoding="utf-8")
        self.must_fail("DUPLICATE_JSON_KEY")

    def test_reject_symlink_escape_and_nonregular(self):
        target=self.root/"prior_checkpoint"
        target.unlink()
        target.symlink_to(self.root/"continued_checkpoint")
        self.must_fail("SYMLINK_REJECTED")

if __name__=="__main__":
    unittest.main()
