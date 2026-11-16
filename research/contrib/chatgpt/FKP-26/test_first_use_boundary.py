"""FKP-26 source-free tests: no real external seed, reset, or do here."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("fkp26_single_use",HERE/"run_once.py")
p=importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class FakePolicy:
    def __init__(self,n):
        self.actions=n
        self.received=[object() for _ in range(n)]


class FirstUseBoundary(unittest.TestCase):
    def test_frozen_user_approval_and_seed_limit(self):
        self.assertEqual(p.SEEDS,(996100,996101,996102,996103))
        self.assertEqual(p.MAX_ACTIONS,32)
        self.assertEqual(p.SOURCE_PIN,"c94e9a4cd3641588b6b8507e71ccee5c27032bdf")
        p.verify_one_shot_boundary(attempt="1",tag=p.AUTHORITY_TAG,
                                   seeds=p.SEEDS,limit=32)
        for attempt,tag,seeds,lim in (
            ("2",p.AUTHORITY_TAG,p.SEEDS,32),
            ("",p.AUTHORITY_TAG,p.SEEDS,32),
            ("1","not-authorized",p.SEEDS,32),
            ("1",p.AUTHORITY_TAG,(996100,996102),32),
            ("1",p.AUTHORITY_TAG,(*p.SEEDS,996500),32),
            ("1",p.AUTHORITY_TAG,p.SEEDS,33),
            ("1",p.AUTHORITY_TAG,p.SEEDS,0),
            ("1",p.AUTHORITY_TAG,p.SEEDS,True),
        ):
            with self.assertRaises(PermissionError):
                p.verify_one_shot_boundary(attempt=attempt,tag=tag,
                                           seeds=seeds,limit=lim)

    def test_public_only_transcript_sha_and_action_budget(self):
        events=[{"before":0,"action":0,"reward":1,"after":1,
                 "terminated":False,"truncated":True}]
        r={"schema":"fkp24.native-public-mdp-transcript.v1",
           "upstream_sha":p.SOURCE_PIN,"public_seed":996100,
           "physical_do_actions":1,"public_transitions":events,
           "ended_by_source":True,"budget_exhausted":False,
           "counterfactuals_used":False,"forbidden_info_passed_to_policy":False,
           "public_transitions_sha256":p.sha(p.canon(events))}
        p.validate_complete_transcript(r,996100,FakePolicy(1))
        for bad in (
            dict(r,physical_do_actions=33),
            dict(r,physical_do_actions=0),
            dict(r,public_seed=996500),
            dict(r,upstream_sha="0"*40),
            dict(r,forbidden_info_passed_to_policy=True),
            dict(r,counterfactuals_used=True),
            dict(r,public_transitions_sha256="f"*64),
            dict(r,ended_by_source=True,budget_exhausted=True),
            dict(r,ended_by_source=False,budget_exhausted=False),
        ):
            with self.assertRaises(ValueError):
                p.validate_complete_transcript(bad,996100,FakePolicy(1))
        with self.assertRaises(ValueError):
            p.validate_complete_transcript(r,996100,FakePolicy(2))

    def test_reject_source_private_info_and_malformed_public_bits(self):
        public={"before":0,"action":1,"reward":0,"after":1,
                "terminated":False,"truncated":True}
        def row(x):
            return {"schema":"fkp24.native-public-mdp-transcript.v1",
                    "upstream_sha":p.SOURCE_PIN,"public_seed":996103,
                    "physical_do_actions":1,"public_transitions":[x],
                    "ended_by_source":True,"budget_exhausted":False,
                    "counterfactuals_used":False,
                    "forbidden_info_passed_to_policy":False,
                    "public_transitions_sha256":p.sha(p.canon([x]))}
        for change in (
            dict(public,info={"u1":1}),
            dict(public,before=2),
            dict(public,action=True),
            dict(public,reward=1.5),
            dict(public,terminated=1),
            dict(public,truncated=0),
        ):
            with self.assertRaises(ValueError):
                p.validate_complete_transcript(row(change),996103,FakePolicy(1))
        p.validate_complete_transcript(row(public),996103,FakePolicy(1))

    def test_atomic_output_survives_and_checksum_stable(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"audit"/"journal.json"
            obj={"schema":"fixture","seed":996100,
                 "classification":"STARTED_NO_SOURCE_ACTION_YET"}
            p.atomic_receipt(path,obj)
            self.assertEqual(json.loads(path.read_text()),obj)
            self.assertEqual(path.read_bytes(),p.canon(obj)+b"\n")
            p.atomic_receipt(path,{**obj,"classification":"COMPLETED"})
            self.assertEqual(json.loads(path.read_text())["classification"],"COMPLETED")
            self.assertFalse(path.with_name(path.name+".tmp").exists())

    def test_real_source_reset_and_do_never_called_in_unit_suite(self):
        tree=ast.parse((HERE/"run_once.py").read_text(encoding="utf-8"))
        self.assertFalse(any(
            isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
            and node.func.id=="run_approved"
            for node in ast.walk(tree)))
        body=(HERE/"run_once.py").read_text()
        self.assertIn("fkp24.public_mechanical_episode(",body)
        self.assertIn("fkp25.verify_extended_original_git(root)",body)
        self.assertIn("fkp25._require_dependency_versions()",body)
        self.assertIn("GITHUB_RUN_ATTEMPT",body)
        self.assertIn("SOURCE_FIRST_USE_IN_PROGRESS_NO_RETRY",body)
        self.assertIn("STOPPED_AFTER_POTENTIAL_SOURCE_FIRST_USE_NO_REPLAY",body)
        self.assertNotIn("env.ctf_do(",body)
        self.assertNotIn("env.see(",body)
        self.assertNotIn("env.step(",body)

    def test_whole_action_commit_not_simulated_or_replayed_by_test(self):
        # Ensure only ONE place in the actual executor can start a source seed.
        text=(HERE/"run_once.py").read_text(encoding="utf-8")
        self.assertEqual(text.count("fkp24.public_mechanical_episode("),1)
        self.assertEqual(text.count("for seed in SEEDS:"),1)
        self.assertEqual(text.count("atomic_receipt(receipt_path,original)"),1)
        self.assertIn("out_dir.mkdir(parents=True,exist_ok=False)",text)
        self.assertFalse((HERE/"result.json").exists())


if __name__=="__main__":
    unittest.main()
