"""Static preflight for pinned upstream DTR source; never imports/runs its environment."""
import ast
import os
import subprocess
import unittest
from pathlib import Path

from research.native.itd02.dtr_public_event_contract import PUBLIC_KEYS

UPSTREAM_COMMIT = "c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
DTR_BLOB = "6af2371dce21804140ea141ccb7be14e003ba275"
PCH_BLOB = "ff37780c6b791877c70583b8d5f699be7fcd8817"
LICENSE_BLOB = "993e3a4922f003dced0fd061735697c850ea7205"


def git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, check=True, timeout=15
    ).stdout


def class_methods(tree, class_name):
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {n.name: n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    raise AssertionError("missing class " + class_name)


class PinnedDTRSourcePreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("CAUSAL_GYM_SOURCE")
        if not source:
            raise RuntimeError("CAUSAL_GYM_SOURCE_REQUIRED")
        cls.root = Path(source).resolve()
        cls.dtr_path = cls.root / "causal_gym" / "envs" / "dtr.py"
        cls.pch_path = cls.root / "causal_gym" / "core" / "pch.py"
        if not cls.dtr_path.is_file() or not cls.pch_path.is_file():
            raise RuntimeError("PINNED_UPSTREAM_FILES_MISSING")
        cls.dtr_bytes = cls.dtr_path.read_bytes()
        cls.pch_bytes = cls.pch_path.read_bytes()
        cls.dtr = ast.parse(cls.dtr_bytes.decode("utf-8"), filename=str(cls.dtr_path))
        cls.pch = ast.parse(cls.pch_bytes.decode("utf-8"), filename=str(cls.pch_path))

    def test_exact_commit_blobs_license_and_clean_checkout(self):
        self.assertEqual(git(self.root, "rev-parse", "HEAD").decode().strip(), UPSTREAM_COMMIT)
        self.assertEqual(git(self.root, "rev-parse", "HEAD:causal_gym/envs/dtr.py").decode().strip(), DTR_BLOB)
        self.assertEqual(git(self.root, "rev-parse", "HEAD:causal_gym/core/pch.py").decode().strip(), PCH_BLOB)
        self.assertEqual(git(self.root, "rev-parse", "HEAD:LICENSE").decode().strip(), LICENSE_BLOB)
        self.assertEqual(git(self.root, "status", "--porcelain").decode().strip(), "")
        self.assertEqual(git(self.root, "hash-object", str(self.dtr_path)).decode().strip(), DTR_BLOB)
        self.assertEqual(git(self.root, "hash-object", str(self.pch_path)).decode().strip(), PCH_BLOB)

    def test_upstream_dtr_interface_is_two_stage_and_binary(self):
        methods = class_methods(self.dtr, "DTRSCM")
        self.assertTrue({"__init__", "reset", "step"}.issubset(methods))
        reset_text = ast.unparse(methods["reset"])
        step_text = ast.unparse(methods["step"])
        self.assertIn("self.rng = np.random.default_rng(seed)", reset_text)
        self.assertIn("return (self.s1", reset_text)
        self.assertIn("if self.stage == 0", step_text)
        self.assertIn("elif self.stage == 1", step_text)
        self.assertIn("self.stage = 1", step_text)
        self.assertIn("self.stage = 2", step_text)
        self.assertIn("return (self.s2, 0, False, False", step_text)
        self.assertIn("return (None, self.y, True, False", step_text)
        self.assertIn("self.u = self.rng.random()", reset_text)
        self.assertIn("self.env.u", ast.unparse(class_methods(self.dtr, "DTRPCH")["see"]))

    def test_diagnostic_info_and_pch_policy_expose_fields_the_learner_must_not_receive(self):
        step_text = ast.unparse(class_methods(self.dtr, "DTRSCM")["step"])
        pch = class_methods(self.dtr, "DTRPCH")
        see_text = ast.unparse(pch["see"])
        do_text = ast.unparse(pch["do"])
        ctf_text = ast.unparse(pch["ctf_do"])
        for key in ("'s1'", "'x1'", "'s2'", "'x2'", "'y'", "'stage'"):
            self.assertIn(key, step_text)
        self.assertIn("self.env.u", see_text)
        self.assertIn("self.env.s1", see_text)
        self.assertIn("self.env.s2", do_text)
        self.assertIn("self.env.action()", ctf_text)
        for private in ("info", "u", "s1", "x1", "s2", "x2", "y", "get_graph", "env"):
            self.assertNotIn(private, PUBLIC_KEYS)

    def test_preflight_imports_only_source_text_and_never_instantiates_environment(self):
        test_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        call_nodes = [node for node in ast.walk(test_tree) if isinstance(node, ast.Call)]
        self.assertFalse(any(isinstance(node.func, ast.Name) and node.func.id == "DTRSCM" for node in call_nodes))
        self.assertFalse(any(isinstance(node.func, ast.Attribute) and node.func.attr in ("reset", "step") for node in call_nodes))
        imports = [node.module for node in ast.walk(test_tree) if isinstance(node, ast.ImportFrom)]
        self.assertFalse(any(module and module.startswith("causal_gym") for module in imports))


if __name__ == "__main__":
    unittest.main()
