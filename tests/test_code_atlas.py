import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_code_atlas as atlas


class G29(unittest.TestCase):
    def test_source_and_pinned_artifact(self):
        file = ROOT / ".ice/code-atlas.json"
        rev = json.loads(file.read_text("utf-8"))["source_commit"] if file.exists() else atlas.git(ROOT, "rev-parse", "HEAD").decode().strip()
        data = atlas.snapshot(ROOT, rev)
        self.assertGreater(data["counts"]["files"], 30)
        self.assertGreater(data["counts"]["symbols"], 10)
        self.assertEqual(data["source_reviewed_labels"], 0)
        self.assertFalse(data["wingless_evidence_imported"])
        if file.exists():
            for name, value in atlas.render(data).items():
                committed = atlas.git(ROOT, "show", "HEAD:" + name)
                self.assertEqual(committed, value.encode("utf-8"))
                self.assertEqual((ROOT / name).read_bytes().replace(b"\r\n", b"\n"),
                                 committed.replace(b"\r\n", b"\n"))

    def test_native_python_symbols(self):
        tree = ast.parse((ROOT / "scripts/portable_checkpoint.py").read_text("utf-8"))
        self.assertIn("validate_rel_path", [n.name for n in tree.body if isinstance(n, ast.FunctionDef)])

    def test_uncommitted_source_rejected(self):
        with tempfile.TemporaryDirectory(prefix="ygg-g29-") as temp:
            clone = Path(temp) / "clone"
            subprocess.run(["git", "clone", "-q", "--no-hardlinks", "--no-checkout", str(ROOT), str(clone)], check=True)
            commit = atlas.git(ROOT, "rev-parse", "HEAD").decode().strip()
            subprocess.run(["git", "-C", str(clone), "checkout", "-q", "--detach", commit], check=True)
            path = clone / "research/fanout/smoke_candidate.py"
            path.write_bytes(path.read_bytes() + b"\n# synthetic delta\n")
            with self.assertRaisesRegex(RuntimeError, "working source mismatch"):
                atlas.snapshot(clone, commit)

    def test_html_injection_encoding(self):
        commit = atlas.git(ROOT, "rev-parse", "HEAD").decode().strip()
        data = atlas.snapshot(ROOT, commit)
        data["files"][0]["path"] = "</script><script>leak()</script>"
        html = atlas.render(data)[".ice/code-atlas.html"]
        self.assertIn("\\u003c/script", html)


if __name__ == "__main__":
    unittest.main()
