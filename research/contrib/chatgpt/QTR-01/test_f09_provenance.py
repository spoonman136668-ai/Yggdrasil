"""QTR-01 F09 fixture-only tests; no remote operations or donor inference."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
p=Path(__file__).with_name("f09_provenance.py")
spec=importlib.util.spec_from_file_location("qtr_f09",p)
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class F09Tests(unittest.TestCase):
    def test_frozen_url(self):
        self.assertIn(m.REV,m.ROOT)
        self.assertIn(m.REV,m.README)
    def test_tree(self):
        x=m.inspect_tree(json.dumps([{"path":"README.md"},{"path":"icalens.json"}]).encode())
        self.assertTrue(x["readme_listed"])
        self.assertTrue(x["icalens_manifest_listed"])
    def test_bad_tree(self):
        for v in (b"",b"null",b"{}",b"{",json.dumps([{"path":"../secret"}]).encode()):
            with self.subTest(v=v[:12]),self.assertRaises(m.Blocked):
                m.inspect_tree(v)
    def test_wrong_sha(self):
        with self.assertRaisesRegex(m.Blocked,"SHA256_MISMATCH"):
            m.inspect_readme(b"license: mit")
    def test_license_clause(self):
        self.assertIsNone(m.LICENSE.fullmatch("The software uses the MIT license."))
        self.assertEqual(m.LICENSE.fullmatch("license: apache-2.0").group(1),"apache-2.0")
    def test_source_sha_explicit(self):
        s=m.MODEL+" revision "+"a"*40
        self.assertEqual(m.SHA40.search(s).group(0),"a"*40)
    def test_partial_not_ready(self):
        source={"readme_listed":True}
        for a,b in (([],[]),(["mit"],[]),([],["a"*40])):
            out=m.classify(source,{"artifact_license_claims":a,"explicit_qwen_source_revision_claims":b})
            self.assertEqual(out["decision"],"NO_GO_SOURCE_RIGHTS_OR_CHECKPOINT")
            self.assertFalse(out["transplant_ready"])
    def test_claims_not_proof(self):
        out=m.classify({"readme_listed":True},{"artifact_license_claims":["mit"],"explicit_qwen_source_revision_claims":["a"*40]})
        self.assertEqual(out["decision"],"DECLARATIONS_EXIST_NOT_VERIFIED")
        self.assertFalse(out["transplant_ready"])

if __name__=="__main__":
    unittest.main()
