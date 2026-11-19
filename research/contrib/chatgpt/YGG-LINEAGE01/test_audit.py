"""Negative and contract controls for accepted Yggdrasil custody preflight."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ygg_lineage01_audit",HERE/"audit.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class LineageTests(unittest.TestCase):
    def test_manifest_scope_and_no_execution_claim(self):
        p=json.loads((HERE/"manifest.json").read_text())
        self.assertFalse(p["claims"]["canonical_accepted_cumulative_checkpoint_identified"])
        self.assertFalse(p["boundaries"]["new_science_executed"])
        self.assertEqual(p["boundaries"]["deployment"],"NONE")
        self.assertEqual(p["snapshots"]["accepted_main"]["sha"],mod.MAIN)

    def test_ref_drift_is_fail_closed_before_external_git_read(self):
        p=json.loads((HERE/"manifest.json").read_text())
        p["snapshots"]["accepted_main"]["sha"]="0"*40
        with self.assertRaisesRegex(ValueError,"PINNED_REFS"):
            mod.check(p)

    def test_cannot_forge_owner_or_research_candidate(self):
        p=json.loads((HERE/"manifest.json").read_text())
        p["snapshots"]["owner_research_branch"]["observed_sha"]="f"*40
        with self.assertRaisesRegex(ValueError,"PINNED_REFS"):
            mod.check(p)
        p=json.loads((HERE/"manifest.json").read_text())
        p["snapshots"]["research_candidate"]["sha"]="a"*40
        with self.assertRaisesRegex(ValueError,"PINNED_REFS"):
            mod.check(p)

    def test_reject_unknown_schema(self):
        p=json.loads((HERE/"manifest.json").read_text())
        p["schema"]="unqualified"
        with self.assertRaisesRegex(ValueError,"MANIFEST_SCHEMA"):
            mod.check(p)

if __name__=="__main__":
    unittest.main()
