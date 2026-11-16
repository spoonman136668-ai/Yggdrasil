"""CVH-04 original CVH02 policy through an actual OS subprocess — MOCK ONLY.

This suite does not import/construct/reset/step CausalGym. Its 1..6 toy
source episodes and consequences are fabricated in a separate Python
process. All conventional comparisons use the SAME public action tape.
"""
from __future__ import annotations

import ast
from collections import namedtuple
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

HERE=Path(__file__).resolve().parent
CVH02=HERE.parent/"CVH-02"
CVH01=HERE.parent/"CVH-01"
sys.path.insert(0,str(CVH02))
sys.path.insert(0,str(CVH01))
from public_policy import PublicEarnedPolicy
from strong_conventional import batch_public_returns
from public_ipc import (
    CHILD,SCHEMA,MAX_ACTIONS,PUBLIC_FIELDS,PublicConsequence,
    SourceWireError,ToySourceSession,_parse_line,_receipt_digest,
)


class PublicProcessBoundaryTests(unittest.TestCase):
    def test_01_old_learner_public_method_contract_unchanged(self):
        self.assertEqual(PUBLIC_FIELDS,
                         ("before","action","reward","after",
                          "terminated","truncated"))
        self.assertEqual(PublicConsequence._fields,PUBLIC_FIELDS)
        self.assertEqual(PublicEarnedPolicy().memory.seen,0)

    def test_02_source_worker_is_distinct_real_os_process(self):
        with ToySourceSession(1) as s:
            self.assertIsInstance(s.worker_pid,int)
            self.assertNotEqual(s.worker_pid,os.getpid())
            self.assertIsNone(s.proc.poll())
        self.assertIsNotNone(s.proc.poll())

    def test_03_one_source_free_episode_seals_only_public_tape(self):
        p=PublicEarnedPolicy()
        with ToySourceSession(2) as s:
            r=s.drive(p)
            self.assertEqual(r["worker_pid"],s.worker_pid)
            self.assertNotEqual(r["worker_pid"],os.getpid())
        self.assertEqual(r["mock_actions"],6)
        self.assertEqual(r["source_actions"],0)
        self.assertTrue(r["mock_only"])
        self.assertFalse(r["source_original_first_use"])
        self.assertFalse(r["forbidden_info_passed_to_policy"])
        self.assertEqual(p.memory.seen,6)
        self.assertEqual(sum(p.attempts),6)
        self.assertEqual(p.episode_history,[])
        self.assertTrue(r["public_events"][-1]["truncated"])
        self.assertEqual(set(r["public_events"][0]),set(PUBLIC_FIELDS))
        self.assertNotIn("private_source_salt",str(r))

    def test_04_original_policy_independent_conventional_batch_parity(self):
        p=PublicEarnedPolicy()
        rows=[]
        for seed in (1,2,3):
            with ToySourceSession(seed) as s:
                r=s.drive(p)
                rows.extend(PublicConsequence(**x) for x in r["public_events"])
        count,total=batch_public_returns(rows)
        self.assertEqual(p.memory.count,count)
        self.assertEqual(p.memory.total,total)
        self.assertEqual(p.memory.seen,18)
        self.assertEqual(sum(p.attempts),18)

    def test_05_cold_restore_and_uninterrupted_identical_new_source(self):
        live=PublicEarnedPolicy()
        with ToySourceSession(1) as s:
            initial=s.drive(live)
        cold=PublicEarnedPolicy.restore(live.snapshot())
        a,b=[],[]
        pids=set()
        for seed in (2,3):
            with ToySourceSession(seed) as s:
                a.append(s.drive(live))
                pids.add(s.worker_pid)
            with ToySourceSession(seed) as s:
                b.append(s.drive(cold))
                pids.add(s.worker_pid)
        self.assertEqual(len(pids),4)
        self.assertEqual([x["public_trace_sha256"] for x in a],
                         [x["public_trace_sha256"] for x in b])
        self.assertEqual(live.snapshot(),cold.snapshot())
        self.assertEqual(live.memory.seen,18)

    def test_06_identical_seed_and_policy_means_identical_public_trace(self):
        receipts=[]
        for _ in range(2):
            p=PublicEarnedPolicy()
            with ToySourceSession(4) as s:
                receipts.append(s.drive(p))
        self.assertNotEqual(receipts[0]["worker_pid"],receipts[1]["worker_pid"])
        self.assertEqual(receipts[0]["public_events"],receipts[1]["public_events"])
        self.assertEqual(receipts[0]["public_trace_sha256"],
                         receipts[1]["public_trace_sha256"])

    def test_07_public_effect_requires_selected_action_first(self):
        with ToySourceSession(3) as s:
            self.assertEqual(s.events,[])
            self.assertEqual(len(s.events),0)
            for a in range(3):
                previous=s.state
                public=s.step(a%2)
                self.assertEqual(public.before,previous)
                self.assertEqual(public.action,a%2)
                self.assertEqual(len(s.events),a+1)
                self.assertNotIn("source_world",public._asdict())
            self.assertEqual(len(s.events),3)

    def test_08_reject_private_metadata_before_learner_observe(self):
        learner=PublicEarnedPolicy()
        with ToySourceSession(2,fault="private") as s:
            action=learner.choose(s.state,tuple(s.events))
            before=learner.memory.snapshot()
            with self.assertRaisesRegex(SourceWireError,"PRIVATE_OR_EXTRA"):
                s.step(action)
            self.assertTrue(s.closed)
            self.assertEqual(learner.memory.snapshot(),before)
            self.assertEqual(learner.memory.seen,0)
            with self.assertRaises(SourceWireError):
                s.step(action)

    def test_09_reject_wrong_action_without_replay(self):
        with ToySourceSession(1,fault="wrong_action") as s:
            with self.assertRaisesRegex(SourceWireError,"ACTION_OR_STATE"):
                s.step(0)
            self.assertEqual(len(s.events),0)
            self.assertTrue(s.closed)

    def test_10_reject_nonmonotonic_sequence_without_replay(self):
        with ToySourceSession(1,fault="wrong_seq") as s:
            with self.assertRaisesRegex(SourceWireError,"NONMONOTONIC"):
                s.step(0)
            self.assertEqual(len(s.events),0)
            self.assertTrue(s.closed)

    def test_11_timeout_closes_uncertain_effect_without_resend(self):
        with ToySourceSession(1,fault="stall",timeout_seconds=3) as s:
            s.timeout_seconds=0.3
            with self.assertRaisesRegex(SourceWireError,"TIMEOUT_NO_REPLAY"):
                s.step(0)
            self.assertTrue(s.closed)
            self.assertEqual(s.events,[])
            self.assertIsNotNone(s.proc.poll())

    def test_12_original_and_protected_seeds_rejected_before_spawn(self):
        with mock.patch("public_ipc.subprocess.Popen") as start:
            for x in (996100,996103,996500,996600,0,7,-1,True,"1"):
                with self.subTest(seed=x),self.assertRaises(PermissionError):
                    ToySourceSession(x)
            start.assert_not_called()

    def test_13_bad_binary_and_duplicate_inflight_fail_closed(self):
        with ToySourceSession(1) as s:
            for a in (True,False,-1,2,"0",0.0):
                with self.subTest(a=a),self.assertRaises(SourceWireError):
                    s.step(a)
            self.assertEqual(s.events,[])
            valid=s.step(0)
            self.assertEqual(valid.action,0)
            s.inflight=True
            with self.assertRaisesRegex(SourceWireError,"IN_FLIGHT"):
                s.step(1)
            s.close()

    def test_14_protocol_rejects_non_object_private_and_oversize(self):
        self.assertEqual(_parse_line('{"info":1}\n'),{"info":1})
        for x in ('[]\n','42\n','null\n','not-json\n',
                  '{"x":'+('0'*4097)+'}\n','{"x":1}'):
            with self.subTest(message=x),self.assertRaises(SourceWireError):
                _parse_line(x)

    def test_15_returned_public_trace_integrity(self):
        p=PublicEarnedPolicy()
        with ToySourceSession(5) as s:
            r=s.drive(p)
            self.assertEqual(r["public_trace_sha256"],
                             _receipt_digest(s.events))
            self.assertEqual(len(r["public_events"]),MAX_ACTIONS)
            self.assertEqual(set(r["public_events"][0]),set(PUBLIC_FIELDS))

    def test_16_finished_episode_denies_any_renewed_action(self):
        with ToySourceSession(6) as s:
            s.drive(PublicEarnedPolicy())
            with self.assertRaisesRegex(SourceWireError,"EPISODE_CLOSED"):
                s.step(0)

    def test_17_no_original_environment_imports_or_entrypoints(self):
        for path in (HERE/"public_ipc.py",CHILD):
            tree=ast.parse(path.read_text(encoding="utf-8"))
            imported=[]
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):
                    imported.extend(a.name for a in node.names)
                elif isinstance(node,ast.ImportFrom):
                    imported.append(node.module or "")
            self.assertFalse(any(x.startswith("causal_gym") for x in imported))
            self.assertFalse(any(x.startswith("FKP-25") for x in imported))
            self.assertFalse(any(x=="websockets" or x=="requests" for x in imported))

    def test_18_worker_refuses_actual_source_seed_on_cli(self):
        p=subprocess.run([sys.executable,"-I","-B",str(CHILD),
                          "--mock-only","--toy-seed","996100"],
                         capture_output=True,text=True,timeout=10)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("NOT_AUTHORIZED_ORIGINAL_SOURCE",p.stdout)

    def test_19_worker_refuses_unarmed_source_mode(self):
        p=subprocess.run([sys.executable,"-I","-B",str(CHILD),
                          "--toy-seed","1"],capture_output=True,text=True,
                         timeout=10)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("NOT_AUTHORIZED_ORIGINAL_SOURCE",p.stdout)

    def test_20_public_receipt_does_not_leak_model_private_state(self):
        p=PublicEarnedPolicy()
        with ToySourceSession(1) as s:
            r=s.drive(p)
        forbidden=("source_private","source_salt","causal_gym",
                   "world_hidden","_env","counterfactual")
        for key in forbidden:
            self.assertNotIn(key,json.dumps(r,sort_keys=True).lower())

if __name__=="__main__":
    unittest.main()
