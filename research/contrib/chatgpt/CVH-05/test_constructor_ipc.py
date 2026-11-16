"""CVH-05 pre-first-use source-free parent/real-child protocol tests.

The original CausalGym package is NEVER imported and the original source
constructor is NEVER invoked in this suite. Genuine source process custody
is separately checked on the exact original Git SHA on Windows and Ubuntu.
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

import constructor_ipc as c
import source_child as s
import probe_original_child as probe

HERE=Path(__file__).resolve().parent


class RecordingStringIO(io.StringIO):
    def close(self):
        self.saved=self.getvalue()
        super().close()


class FakeProcess:
    """Explicit fake handshake, NOT an original CausalGym process."""
    def __init__(self,lines):
        self.pid=os.getpid()+77
        self.stdin=RecordingStringIO()
        self.stdout=io.StringIO("".join(lines))
        self.stderr=None
        self.returncode=None
    def poll(self):
        return self.returncode
    def terminate(self):
        self.returncode=-15
    def kill(self):
        self.returncode=-9
    def wait(self,timeout=None):
        if self.returncode is None:
            self.returncode=0
        return self.returncode


def fake_ready():
    return {
        "schema":c.SCHEMA,"kind":"ready","source_sha":c.PIN,
        "source_blobs":16,"original_objects":1,
        "source_actions":0,"source_resets":0,
    }


def wire(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n"


class CVH05ConstructorBoundaryTests(unittest.TestCase):
    def test_01_unchanged_verified_CVH03_factory_file_present(self):
        parent=HERE.parent/"CVH-03"/"source_binding.py"
        self.assertTrue(parent.is_file())
        self.assertTrue((HERE.parent/"CVH-04"/"public_ipc.py").is_file())

    def test_02_source_worker_module_import_does_not_load_upstream(self):
        self.assertFalse(any(n=="causal_gym" or n.startswith("causal_gym.")
                             for n in sys.modules))
        self.assertTrue(callable(s.source_factory))

    def test_03_parent_never_imports_original_source_or_source_private_modules(self):
        syntax=ast.parse((HERE/"constructor_ipc.py").read_text())
        allimports=[]
        for node in ast.walk(syntax):
            if isinstance(node,ast.Import):
                allimports.extend(item.name for item in node.names)
            elif isinstance(node,ast.ImportFrom):
                allimports.append(node.module or "")
        self.assertTrue(all(not x.startswith("causal_gym") for x in allimports))
        self.assertTrue(all(not x.startswith("source_binding") for x in allimports))
        self.assertFalse(any(x.startswith("causal_gym") for x in sys.modules))

    def test_04_exact_minimal_public_ready_schema(self):
        hello=fake_ready()
        self.assertEqual(set(hello),c.REQUIRED_READY)
        self.assertEqual(c._validate_ready(hello),hello)
        self.assertEqual(hello["source_actions"],0)
        self.assertEqual(hello["source_resets"],0)

    def test_05_nonpublic_source_metadata_rejected(self):
        for k in ("info","source_private","get_graph","world_id",
                  "exogenous","counterfactual","env"):
            hello=fake_ready()
            hello[k]="private"
            with self.subTest(field=k),self.assertRaisesRegex(
                    c.SourceCustodyError,"NONPUBLIC_SOURCE_ACK"):
                c._validate_ready(hello)

    def test_06_wrong_source_sha_and_blobs_rejected(self):
        variants=[("source_sha","f"*40),("source_blobs",15),
                  ("source_blobs",True),("original_objects",2),
                  ("original_objects",True),("source_actions",1),
                  ("source_resets",1),("source_actions",False)]
        for key,val in variants:
            hello=fake_ready()
            hello[key]=val
            with self.subTest(key=key,value=val),self.assertRaisesRegex(
                    c.SourceCustodyError,"CUSTODY_MISMATCH"):
                c._validate_ready(hello)

    def test_07_closed_acks_accept_only_schema_and_kind(self):
        self.assertTrue(c._validate_closed({"schema":c.SCHEMA,
                                             "kind":"closed"}))
        for bad in ({"schema":c.SCHEMA,"kind":"closed","reward":1},
                    {"schema":c.SCHEMA,"kind":"event"},
                    {"kind":"closed"}):
            with self.assertRaises(c.SourceCustodyError):
                c._validate_closed(bad)

    def test_08_malformed_json_and_oversize_refused(self):
        for raw in ("[]\n","null\n","bad\n","{}",
                    "x"*4097+"\n", "12\n"):
            with self.subTest(raw=raw[:20]),self.assertRaises(
                    c.SourceCustodyError):
                c._frame(raw)

    def test_09_worker_accepts_only_exact_close_command(self):
        valid=wire({"schema":s.SCHEMA,"kind":"close"}).encode()
        self.assertTrue(s.parse_close(valid))
        for msg in (
            {"schema":s.SCHEMA,"kind":"act","action":0},
            {"schema":s.SCHEMA,"kind":"reset"},
            {"schema":s.SCHEMA,"kind":"do"},
            {"schema":s.SCHEMA,"kind":"close","seed":996100},
            {"schema":s.SCHEMA,"kind":"close","private_info":True},
            {"schema":"wrong","kind":"close"},
        ):
            with self.subTest(m=msg),self.assertRaises(ValueError):
                s.parse_close(wire(msg).encode())

    def test_10_worker_rejects_truncated_and_oversize_close(self):
        for raw in (b"",b"{}\n",b"{not-json}\n",b"X"*4097+b"\n",
                    wire({"schema":s.SCHEMA,"kind":"close"}).encode()[:-1]):
            with self.assertRaises(ValueError):
                s.parse_close(raw)

    def test_11_worker_source_free_dummy_context_constructs_only_once(self):
        created=[]
        class DummyFactory:
            constructed=0
            def __call__(self):
                self.constructed+=1
                obj=object()
                created.append(obj)
                return obj
        @contextmanager
        def fake_factory(checkout):
            self.assertEqual(checkout,"dummy-not-original")
            f=DummyFactory()
            yield f,{"source_sha":c.PIN,"source_blobs_verified":16,
                    "source_action_calls":0,"source_reset_calls":0,
                    "source_first_use":False,"scientific_pass":False}
        emitted=[]
        with mock.patch.object(s,"source_factory",return_value=fake_factory), \
             mock.patch.object(s,"emit",side_effect=emitted.append):
            code=s.execute_constructor_only(
                "dummy-not-original",
                lambda maxbytes:wire({"schema":s.SCHEMA,
                                     "kind":"close"}).encode())
        self.assertEqual(code,0)
        self.assertEqual(len(created),1)
        self.assertEqual(len(emitted),2)
        self.assertEqual(set(emitted[0]),s.HELLO_KEYS)
        self.assertEqual(emitted[0]["source_actions"],0)
        self.assertEqual(emitted[1],{"schema":s.SCHEMA,"kind":"closed"})

    def test_12_worker_dummy_denies_action_and_private_input(self):
        @contextmanager
        def fake_factory(_checkout):
            class One:
                constructed=0
                def __call__(self):
                    self.constructed+=1
                    return object()
            yield One(),{"source_sha":c.PIN,"source_blobs_verified":16,
                          "source_action_calls":0,"source_reset_calls":0,
                          "source_first_use":False,"scientific_pass":False}
        emit=[]
        with mock.patch.object(s,"source_factory",return_value=fake_factory), \
             mock.patch.object(s,"emit",side_effect=emit.append):
            rc=s.execute_constructor_only(
                "dummy-only",lambda n:wire({"schema":s.SCHEMA,"kind":"act",
                                             "seq":1,"action":1}).encode())
        self.assertEqual(rc,2)
        self.assertEqual(emit[-1]["code"],"ONLY_EXPLICIT_CLOSE_ALLOWED")

    def test_13_parent_mock_child_handshake_then_close_and_reap(self):
        fake=FakeProcess([wire(fake_ready()),wire(
            {"schema":c.SCHEMA,"kind":"closed"})])
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(c.subprocess,"Popen",return_value=fake) as spawn:
                with c.OriginalSourceConstructorSession(tmp,timeout_seconds=2) as session:
                    rec=session.public_receipt()
                    self.assertTrue(rec["source_process_isolated"])
                    self.assertEqual(session.pid,os.getpid()+77)
                    self.assertEqual(rec["source_actions"],0)
                    self.assertFalse(rec["source_seed_first_use"])
                self.assertTrue(session.closed)
                self.assertEqual(fake.poll(),0)
                self.assertEqual(fake.stdin.saved,wire(
                    {"schema":c.SCHEMA,"kind":"close"}))
                self.assertIn("--constructor-only",spawn.call_args.args[0])
                self.assertNotIn("--source-action",spawn.call_args.args[0])
                self.assertNotIn("996100",str(spawn.call_args))

    def test_14_parent_mock_child_rejects_private_ready_before_use(self):
        hello=fake_ready()
        hello["private_action_law"]="LEAK"
        fake=FakeProcess([wire(hello)])
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(c.subprocess,"Popen",return_value=fake):
                with self.assertRaisesRegex(c.SourceCustodyError,
                                            "NONPUBLIC_SOURCE_ACK"):
                    with c.OriginalSourceConstructorSession(tmp) as _s:
                        self.fail("private data should have been denied")
            self.assertEqual(fake.poll(),-15)

    def test_15_parent_prevents_source_import_in_learner_interpreter(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(sys.modules,{
                 "causal_gym":types.ModuleType("causal_gym")}):
                with mock.patch.object(c.subprocess,"Popen") as spawn:
                    with self.assertRaisesRegex(c.SourceCustodyError,
                                              "PARENT_ORIGINAL_SOURCE_IMPORT_FORBIDDEN"):
                        with c.OriginalSourceConstructorSession(tmp):pass
                    spawn.assert_not_called()

    def test_16_source_firstuse_option_denied_before_checkout_or_import(self):
        p=subprocess.run([sys.executable,"-I","-B",str(HERE/"source_child.py"),
                          "--checkout","/missing/not-approved"],
                         capture_output=True,text=True,timeout=5)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("SOURCE_ACTIONS_AND_WORLD_FIRSTUSE_DISARMED",p.stdout)
        q=subprocess.run([sys.executable,"-B",str(HERE/"probe_original_child.py"),
                          "--checkout","/missing/not-approved","--out",
                          "/unwritable/never.json","--source-action"],
                         capture_output=True,text=True,timeout=5)
        self.assertNotEqual(q.returncode,0)
        self.assertIn("SOURCE_RESET_DO_FIRST_USE_NOT_AUTHORIZED",q.stderr)

    def test_17_parent_requires_clean_preexisting_checkout_directory(self):
        with mock.patch.object(c.subprocess,"Popen") as spawn:
            with self.assertRaises(FileNotFoundError):
                with c.OriginalSourceConstructorSession(
                    "/cvh05/not-present/directory"):pass
            spawn.assert_not_called()

    def test_18_empty_receipt_and_reused_session_denied(self):
        p=c.OriginalSourceConstructorSession(".")
        with self.assertRaises(c.SourceCustodyError):
            p.public_receipt()
        p.closed=True
        with self.assertRaisesRegex(c.SourceCustodyError,"ALREADY_CONSUMED"):
            with p:pass

    def test_19_no_reset_do_or_step_invocations_in_any_new_code(self):
        for path in (HERE/"constructor_ipc.py",HERE/"source_child.py",
                     HERE/"probe_original_child.py"):
            tree=ast.parse(path.read_text(encoding="utf-8"))
            attrs={n.func.attr for n in ast.walk(tree)
                   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
            self.assertTrue({"reset","do","see","step","ctf_do"}.isdisjoint(attrs))

    def test_20_constructor_probe_never_claims_original_science(self):
        fixed={
          "schema":c.SCHEMA,"kind":"ready","source_sha":c.PIN,
          "source_blobs":16,"original_objects":1,
          "source_actions":0,"source_resets":0,
          "source_process_isolated":True,"source_seed_first_use":False,
          "original_source_action_executed":False,"model_updated":False,
        }
        with mock.patch.object(probe,"run_checked_constructor",
                               side_effect=[dict(fixed),dict(fixed)]):
            receipt=probe.evaluate("/not/real/source")
        self.assertEqual(receipt["original_source_actions"],0)
        self.assertEqual(receipt["source_seed_first_uses"],0)
        self.assertTrue(receipt["two_separately_reaped_source_processes"])
        self.assertFalse(receipt["scientific_pass"])
        self.assertFalse(receipt["source_first_use"])

if __name__=="__main__":
    unittest.main()
