"""AAI-08A immutable source/evidence tests; NEVER run consumed science seeds."""
import gzip
import hashlib
import json
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parent


class ExactSourceContract(unittest.TestCase):
    def test_original_protocol_and_amendment(self):
        p=json.loads((ROOT/"prereg.json").read_text(encoding="utf8"))
        a=json.loads((ROOT/"prereg-amendment.json").read_text(encoding="utf8"))
        self.assertEqual(p["id"],"AAI-08A")
        self.assertEqual(a["original_prereg_commit"],
                         "db263b1de02fdaaec2152b44947a1e11b5305262")
        self.assertEqual(p["protocol"]["seeds"]["transfer"],
                         {"start":892000,"count":64})

    def test_original_science_negative(self):
        s=json.loads((ROOT/"result-summary.json").read_text(encoding="utf8"))
        self.assertEqual(s["classification"],"VALID_NEGATIVE_NO_INTEGRATION")
        self.assertFalse(s["checks"]["positive_scientific_gain"])
        self.assertFalse(s["checks"]["return_A_recall"])
        self.assertFalse(s["checks"]["relative_compute"])
        self.assertTrue(s["checks"]["shuffle_negative"])
        self.assertEqual(s["integration"],"NONE")

    def test_original_raw_archive_digest_and_world_rows(self):
        p=json.loads((ROOT/"provenance.json").read_text(encoding="utf8"))
        binary=(ROOT/"primary-original.json.gz").read_bytes()
        raw=gzip.decompress(binary)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),p["original_primary_json_sha256"])
        record=json.loads(raw)
        compact=json.loads((ROOT/"result-summary.json").read_text(encoding="utf8"))
        self.assertEqual(record["all_worlds_sha256"],compact["all_worlds_sha256"])
        self.assertEqual(record["classification"],compact["classification"])
        self.assertEqual({k:len(v) for k,v in record["world_records"].items()},
                         {"dev":32,"transfer":64,"negative":32})

    def test_scientific_source_does_not_use_hidden_transition_metadata(self):
        tree=ast.parse((ROOT/"evaluate.py").read_text(encoding="utf8"))
        banned={"unwrapped","get_planning_env","transition_matrix"}
        self.assertFalse(any(isinstance(node,ast.Attribute) and node.attr in banned
                             for node in ast.walk(tree)))
        p=json.loads((ROOT/"provenance.json").read_text(encoding="utf8"))
        self.assertEqual(p["scientific_first_use_count"],1)
        self.assertTrue(p["source_unchanged_after_first_use"])
        self.assertEqual(p["integration"],"NONE")
        self.assertFalse(p["native_model_changed"])


if __name__=="__main__":
    unittest.main()
