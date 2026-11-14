"""F08 source-free guard tests; no Qwen/HF calls or fitted weights downloaded."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
p=Path(__file__).with_name("f08_matrix_custody.py")
s=importlib.util.spec_from_file_location("qtr_f08",p)
m=importlib.util.module_from_spec(s)
sys.modules[s.name]=m
s.loader.exec_module(m)


def entry(path=None,sha=None,size=1024):
    return {"path":path or m.NAME,"size":size,"type":"file",
            "lfs":{"oid":sha if sha is not None else "a"*64}}


class CustodyTests(unittest.TestCase):
    def test_pinned_source_not_main(self):
        self.assertIn(m.REV,m.DIR)
        self.assertIn(m.REV,m.README)
        self.assertNotIn("/main/",m.DIR)

    def test_exact_file_metadata_is_not_independent_hash(self):
        x=m.listed_matrix(json.dumps([entry()]).encode())
        self.assertEqual(x["file"],m.NAME)
        self.assertFalse(x["sha256_independently_recomputed"])
        self.assertFalse(x["fitted_matrix_downloaded"])

    def test_wrong_path_fails_closed(self):
        with self.assertRaisesRegex(m.Invalid,"NOT_LISTED"):
            m.listed_matrix(json.dumps([entry(path="blocks.31.hook_resid_post/sae_weights.safetensors")]).encode())

    def test_hash_must_be_sha256(self):
        for oid in ("xx", "", "0"*40):
            with self.subTest(oid=oid),self.assertRaisesRegex(m.Invalid,"LFS_HASH"):
                m.listed_matrix(json.dumps([entry(sha=oid)]).encode())

    def test_size_validation(self):
        for size in (0,-1,2_000_000_000,"1024"):
            with self.subTest(size=size),self.assertRaisesRegex(m.Invalid,"SIZE"):
                m.listed_matrix(json.dumps([entry(size=size)]).encode())

    def test_readme_license_frontmatter_only(self):
        self.assertEqual(m.license_readme(b"---\nlicense: apache-2.0\n---\nBody")["artifact_repo_license_declaration"],"apache-2.0")
        self.assertEqual(m.license_readme(b"Just says MIT in content")["artifact_repo_license_declaration"],"UNVERIFIED")

    def test_bad_directory_rejected(self):
        for payload in (b"",b"{",b"null",b"x"*(m.SIZE+1)):
            with self.assertRaises(m.Invalid):
                m.listed_matrix(payload)

    def test_malformed_readme_rejected(self):
        for payload in (b"",b"\xff",b"x"*(m.SIZE+1)):
            with self.assertRaises(m.Invalid):
                m.license_readme(payload)


if __name__=="__main__":
    unittest.main()
