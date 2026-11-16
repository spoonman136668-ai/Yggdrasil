"""FKP-25 no-first-use original constructor gate negative controls.

This focused suite MUST NOT import the actual upstream source, touch an
upstream causal world, install packages or call reset/do.
"""
import ast
import json
import sys
from pathlib import Path
import tempfile
import types
import unittest

import runtime_probe as p

ROOT=Path(__file__).resolve().parent
ONE="1"*40


class ReadonlyExactSourceNativeConstructor(unittest.TestCase):
    def test_contract_pinned_all_original_runtime_blobs(self):
        self.assertEqual(p.PIN,"c94e9a4cd3641588b6b8507e71ccee5c27032bdf")
        self.assertEqual(p.ALL_SOURCE_BLOBS["causal_gym/envs/mdp.py"],
                         "6264ec5450754c009e98c3e85f6d5927ece0a9ab")
        self.assertEqual(p.ALL_SOURCE_BLOBS["causal_gym/core/__init__.py"],
                         "7affd0694b0f31dcc05e3d6b47a5eaf3d311e327")
        self.assertEqual(len(p.ALL_SOURCE_BLOBS),16)
        self.assertEqual(p.PINNED_PACKAGES,{
            "numpy":"1.26.4","gymnasium":"0.29.1","networkx":"3.2.1",
            "toposort":"1.10","pydash":"8.0.5"})

    def test_dependency_check_requires_exact_versions(self):
        self.assertEqual(p._require_dependency_versions(
            get_version=lambda x:p.PINNED_PACKAGES[x]),p.PINNED_PACKAGES)
        with self.assertRaisesRegex(ValueError,"DRIFT:networkx"):
            p._require_dependency_versions(
                get_version=lambda x:"2.0" if x=="networkx" else p.PINNED_PACKAGES[x])
        from importlib import metadata
        def not_available(x):
            if x=="pydash":
                raise metadata.PackageNotFoundError(x)
            return p.PINNED_PACKAGES[x]
        with self.assertRaisesRegex(ValueError,"MISSING:pydash"):
            p._require_dependency_versions(get_version=not_available)

    def test_exact_readonly_source_check_and_unexpected_blob_rejected(self):
        class Out:
            def __init__(self,out):self.stdout=out
        state={"head":p.PIN,"dirty":False,"bad":False,"calls":[]}
        def run(args,*,check,capture_output,text):
            self.assertTrue(check and capture_output and text)
            self.assertEqual(args[:3],["git","-C",str(ROOT.resolve())])
            command=args[3:]
            state["calls"].append(command)
            if command==["rev-parse","HEAD"]:
                return Out(state["head"]+"\n")
            if command==["status","--porcelain","--untracked-files=all"]:
                return Out(" M mdp.py\n" if state["dirty"] else "")
            if len(command)==2 and command[0]=="rev-parse" and command[1].startswith("HEAD:"):
                name=command[1][5:]
                value=p.ALL_SOURCE_BLOBS[name]
                if state["bad"] and name=="causal_gym/core/graph.py":
                    value=ONE
                return Out(value+"\n")
            raise AssertionError("ILLEGAL_GIT_MUTATING_COMMAND")
        good=p.verify_extended_original_git(ROOT,runner=run)
        self.assertTrue(good["clean"])
        self.assertEqual(good["real_actions"],0)
        self.assertEqual(len(good["checked_original_blobs"]),16)
        self.assertEqual(len(state["calls"]),2+len(p.FKP24_REQUIRED)+len(p.DIRECT_PINNED))
        state["bad"]=True
        with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_DRIFT"):
            p.verify_extended_original_git(ROOT,runner=run)
        state["bad"]=False
        state["dirty"]=True
        with self.assertRaisesRegex(ValueError,"SOURCE_DIRTY"):
            p.verify_extended_original_git(ROOT,runner=run)
        state["dirty"]=False
        state["head"]=ONE
        with self.assertRaisesRegex(ValueError,"COMMIT_DRIFT"):
            p.verify_extended_original_git(ROOT,runner=run)

    def test_refuse_already_loaded_global_source_module_before_import(self):
        old=sys.modules.get("causal_gym")
        sys.modules["causal_gym"]=types.ModuleType("causal_gym")
        try:
            with self.assertRaisesRegex(ValueError,"NOT_ISOLATED"):
                p._constructor_in_isolated_import_space(ROOT)
        finally:
            if old is None:
                del sys.modules["causal_gym"]
            else:
                sys.modules["causal_gym"]=old

    def test_source_dir_symlink_and_outside_checkout_forbidden(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            (root/"mock.py").write_text("value=1\n","utf-8")
            self.assertEqual(p._ensure_checkout_file("mock.py",root),root/"mock.py")
            with self.assertRaises((ValueError,FileNotFoundError)):
                p._ensure_checkout_file("outside.py",root)

    def test_original_import_not_rebranded_as_stock_package(self):
        body=Path(p.__file__).read_text("utf-8")
        self.assertIn("PINNED_TARGETED_NAMESPACE_NOT_STOCK_PACKAGE_INIT",body)
        self.assertIn("causal_gym/core/__init__.py",body)
        self.assertIn("causal_gym/envs/mdp.py",body)
        self.assertIn("source_first_use",body)
        self.assertIn("source_classes_unmodified",body)
        self.assertNotIn("import public_repair_source",body)
        self.assertNotIn("995200",body)
        self.assertNotIn("996500",body)

    def test_no_physical_action_or_privileged_oracle_called_in_probe(self):
        node=ast.parse(Path(p.__file__).read_text("utf-8"))
        forbidden={"reset","do","see","step","ctf_do","_true_consequence"}
        invoked=[]
        for n in ast.walk(node):
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in forbidden:
                invoked.append(n.func.attr)
        self.assertEqual(invoked,[])
        self.assertFalse(hasattr(p,"native_env_rewards"))
        self.assertNotIn("public_mechanical_episode",Path(p.__file__).read_text("utf-8"))

    def test_canonical_json_evidence_preserves_byte_stable_digest(self):
        a={"source_sha":p.PIN,"full":False,"constructor":True}
        b={"constructor":True,"full":False,"source_sha":p.PIN}
        self.assertEqual(p._json(a),p._json(b))
        self.assertEqual(len(__import__("hashlib").sha256(p._json(a)).hexdigest()),64)


if __name__=="__main__":
    unittest.main()
