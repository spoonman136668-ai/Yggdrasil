"""CVH-03 source-free negative tests and exact inherited module custody.

Tests never load upstream CausalGym, never construct its native classes and
never reset/do a source action. Source/factory equivalence is separately
verified by the original upstream constructor-only qualification stage.
"""
from __future__ import annotations

import ast
from hashlib import sha1
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import source_binding as s

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
PROBE=HERE/"probe_constructor.py"
INHERITED_FKP25=PARENT/"FKP-25"/"runtime_probe.py"
INHERITED_FKP24=PARENT/"FKP-24"/"native_public_mdp.py"
INHERITED_CVH02=PARENT/"CVH-02"/"public_policy.py"
FKP25_BLOB="1cfe7fe6cc7b2273cc7232cb38e4d648b25b0236"
FKP24_BLOB="4424eadef179996ff491911efadfbe4e07761062"
CVH02_BLOB="b0efc964312d62930c3a97632ca02d8d17ef84aa"


def git_blob(path):
    buf=path.read_bytes()
    return sha1(b"blob "+str(len(buf)).encode("ascii")+b"\0"+buf).hexdigest()


class MockNative:
    """No external source import; only constructor lifetime semantics."""
    def __init__(self,identity):
        self.identity=identity


class FactorySourceFreeTests(unittest.TestCase):
    def test_required_original_three_files_byte_identical(self):
        self.assertTrue(INHERITED_FKP25.is_file())
        self.assertTrue(INHERITED_FKP24.is_file())
        self.assertTrue(INHERITED_CVH02.is_file())
        self.assertEqual(git_blob(INHERITED_FKP25),FKP25_BLOB)
        self.assertEqual(git_blob(INHERITED_FKP24),FKP24_BLOB)
        self.assertEqual(git_blob(INHERITED_CVH02),CVH02_BLOB)

    def test_module_import_never_loads_original_upstream(self):
        self.assertFalse(any(x=="causal_gym" or x.startswith("causal_gym.")
                             for x in sys.modules))
        self.assertTrue(callable(s.verified_original_factory))

    def test_factory_requires_callable_constructor(self):
        for x in (None,True,0,[],{},b"x"):
            with self.subTest(x=x),self.assertRaisesRegex(ValueError,"CONSTRUCTOR_REQUIRED"):
                s.FactoryLifetime(x)

    def test_live_mock_factory_returns_new_objects(self):
        seen=[]
        def mk():
            v=MockNative(len(seen))
            seen.append(v)
            return v
        f=s.FactoryLifetime(mk)
        first,second=f(),f()
        self.assertIsNot(first,second)
        self.assertEqual((first.identity,second.identity),(0,1))
        self.assertEqual(f.constructed,2)
        self.assertEqual(len(seen),2)

    def test_closed_mock_factory_refuses_even_existing_callable(self):
        f=s.FactoryLifetime(lambda:MockNative(0))
        self.assertIsInstance(f(),MockNative)
        f.close()
        with self.assertRaisesRegex(PermissionError,"FACTORY_CLOSED"):f()
        self.assertEqual(f.constructed,1)

    def test_close_idempotent_and_no_source_creation(self):
        called=[]
        f=s.FactoryLifetime(lambda:called.append(1))
        f.close();f.close()
        with self.assertRaises(PermissionError):f()
        self.assertEqual(called,[])
        self.assertEqual(f.constructed,0)

    def test_constructor_failure_is_never_counted(self):
        def fail():
            raise RuntimeError("mock constructor failure")
        f=s.FactoryLifetime(fail)
        with self.assertRaisesRegex(RuntimeError,"mock constructor failure"):f()
        self.assertEqual(f.constructed,0)
        f.close()

    def test_no_reset_do_step_or_counterfactual_in_binding_ast(self):
        syntax=ast.parse((HERE/"source_binding.py").read_text(encoding="utf-8"))
        forbidden={"reset","do","step","see","ctf_do","natural_action","get_graph"}
        names={n.func.attr for n in ast.walk(syntax)
               if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
        self.assertEqual(names.intersection(forbidden),set())
        self.assertFalse(any(k=="causal_gym" or k.startswith("causal_gym.")
                             for k in sys.modules))

    def test_probe_contains_no_physical_action_calls(self):
        syntax=ast.parse(PROBE.read_text(encoding="utf-8"))
        used={n.func.attr for n in ast.walk(syntax)
              if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
        self.assertTrue({"do","reset","ctf_do","step"}.isdisjoint(used))

    def test_missing_original_checkout_fails_before_source_import(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"not_present"
            before=set(sys.modules)
            with self.assertRaises(FileNotFoundError):
                with s.verified_original_factory(p):pass
            newly={k for k in sys.modules if k not in before
                   and (k=="causal_gym" or k.startswith("causal_gym."))}
            self.assertEqual(newly,set())

    def test_original_fkp25_import_is_lazy_and_source_free(self):
        p=s._original_qualification()
        self.assertEqual(p.PIN,"c94e9a4cd3641588b6b8507e71ccee5c27032bdf")
        self.assertEqual(len(p.ALL_SOURCE_BLOBS),16)
        self.assertEqual(p.PINNED_PACKAGES["numpy"],"1.26.4")
        self.assertEqual(p.PINNED_PACKAGES["gymnasium"],"0.29.1")
        self.assertFalse(any(k=="causal_gym" or k.startswith("causal_gym.")
                             for k in sys.modules))

    def test_preserved_fkp24_exact_adaptation_source_is_not_executed(self):
        text=INHERITED_FKP24.read_text(encoding="utf-8")
        self.assertIn("def public_mechanical_episode",text)
        self.assertIn("def native_source_factory",text)
        self.assertIn("MECHANICAL_PUBLIC_SEEDS=(996100,996101,996102,996103)",text)
        self.assertFalse(any(k=="causal_gym" or k.startswith("causal_gym.")
                             for k in sys.modules))

    def test_cvh02_public_policy_source_remains_unchanged(self):
        text=INHERITED_CVH02.read_text(encoding="utf-8")
        self.assertIn("class PublicEarnedPolicy:",text)
        self.assertIn("def choose(self, state, history):",text)
        self.assertIn("def observe(self, row):",text)

    def test_action_firstuse_cli_refused_before_import_or_checkout(self):
        p=subprocess.run([sys.executable,str(PROBE),"--checkout",
                          "/path/that/does/not/exist","--out","/unwritable/path",
                          "--source-action"],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("CVH03_SOURCE_FIRST_USE_AND_PHYSICAL_ACTIONS_DISARMED",p.stderr)

    def test_importing_probe_does_not_touch_upstream_source(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location("cvh03_source_free_probe",PROBE)
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(callable(mod.probe))
        self.assertFalse(any(k=="causal_gym" or k.startswith("causal_gym.")
                             for k in sys.modules))

    def test_dummy_construction_does_not_prove_upstream_source(self):
        f=s.FactoryLifetime(lambda:MockNative(99))
        v=f()
        self.assertIsInstance(v,MockNative)
        self.assertNotEqual(type(v).__name__,"MDPPCH")
        f.close()


if __name__=="__main__":
    unittest.main()
