"""FKP-24 original source-safe external CausalGym admission/provenance tests.

No real upstream module import, source seed or scientific first-use here.
"""
from pathlib import Path
import json
import unittest

import native_public_mdp as adapter
import verify_upstream as proof

ROOT=Path(__file__).resolve().parent


class FrozenIndependentMDPSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((ROOT/"prereg.json").read_text("utf-8"))

    def test_first_frozen_parent_and_exact_independent_upstream(self):
        x=self.p
        self.assertEqual(x["schema"],"yggdrasil.external-research-prereg.v1")
        self.assertEqual(x["experiment_id"],
                         "FKP-24-EXTERNAL-CONFOUNDED-MDP-SOURCE-ADMISSION")
        self.assertTrue(x["prereg_first"])
        self.assertEqual(x["exact_parent_sha"],
                         "6a9d908c270bb209f13eb87db407bfd463f16446")
        u=x["external_source"]
        self.assertEqual(u["repo"],"CausalAILab/Causal-Gymnasium")
        self.assertEqual(u["sha"],proof.PIN)
        self.assertEqual(u["license"],"Apache-2.0")
        self.assertEqual(u["license_blob"],proof.REQUIRED["LICENSE"])
        self.assertEqual(proof.REQUIRED["causal_gym/envs/mdp.py"],
                         "6264ec5450754c009e98c3e85f6d5927ece0a9ab")
        for p,blob in u["source_blobs"].items():
            self.assertEqual(proof.REQUIRED[p],blob)

    def test_api_public_excludes_counterfactual_and_hidden_graph(self):
        u=self.p["external_source"]
        self.assertEqual(u["class"],"MDPPCH")
        self.assertIn("LearningRegime.do",u["init"])
        self.assertIn("env.do(",u["native_step"])
        self.assertIn("discard info",u["native_step"])
        self.assertIn("not a secure Python",u["not_a_security_sandbox"])
        self.assertEqual(adapter.MECHANICAL_PUBLIC_SEEDS,
                         (996100,996101,996102,996103))
        self.assertEqual(adapter.MAX_ACTIONS,32)

    def test_protected_owner_first_use_and_native_promotion_denied(self):
        x=self.p
        self.assertFalse(x["frozen_stages"]["no_original_first_use"] is False)
        self.assertEqual(x["frozen_stages"]["source_actions_in_current_gate"],0)
        self.assertEqual(x["frozen_stages"]["protected_dev"],"996500..996531")
        self.assertEqual(x["frozen_stages"]["protected_transfer"],"996600..996663")
        for k in ("protected_first_use","accepted_main_mutation",
                  "native_admission","merge",
                  "runner_scheduler_or_controller_change","paid_api"):
            self.assertFalse(x["authority"][k])
        self.assertTrue(x["authority"]["research_only"])
        self.assertTrue(x["no_new_workflow_file"])
        self.assertTrue(x["no_scheduled_tasks"])

    def test_all_source_research_artifacts_exist_without_vendor_copy(self):
        for name in ("prereg.json","native_public_mdp.py",
                     "verify_upstream.py","test_native_public_mdp.py",
                     "test_prereg.py","README.md"):
            self.assertTrue((ROOT/name).is_file())
        self.assertFalse(any((ROOT/p).exists()
                 for p in ("mdp.py","pch.py","causal_gym","LICENSE")))

    def test_readonly_source_pin_verification_success_and_tamper_failure(self):
        root=ROOT
        state={"sha":proof.PIN,"dirty":False,"bad":None,"calls":[]}
        class R:
            def __init__(self,stdout):
                self.stdout=stdout
        def runner(args,*,check,capture_output,text):
            self.assertTrue(check and capture_output and text)
            self.assertEqual(args[:3],["git","-C",str(root.resolve())])
            state["calls"].append(args[3:])
            command=args[3:]
            if command==["rev-parse","HEAD"]:
                return R(state["sha"]+"\n")
            if command==["status","--porcelain","--untracked-files=all"]:
                return R("?? private_future.txt\n" if state["dirty"] else "")
            if command[0:2]==["rev-parse","HEAD:"+command[1][5:]]:
                # This branch is intentionally unreachable; exact-key path
                # handling follows below.
                pass
            if command[0]=="rev-parse" and len(command)==2 and command[1].startswith("HEAD:"):
                key=command[1][5:]
                return R((state["bad"] if key=="setup.py" and state["bad"]
                          else proof.REQUIRED[key])+"\n")
            raise AssertionError("UNEXPECTED_GIT_MUTATING_INVOCATION")
        valid=proof.inspect_exact_checkout(root,runner=runner)
        self.assertTrue(valid["clean"])
        self.assertFalse(valid["actual_env_executed"])
        self.assertEqual(valid["blobs"],dict(sorted(proof.REQUIRED.items())))
        self.assertEqual(len(state["calls"]),2+len(proof.REQUIRED))
        state["sha"]="0"*40
        with self.assertRaisesRegex(ValueError,"COMMIT_DRIFT"):
            proof.inspect_exact_checkout(root,runner=runner)
        state["sha"]=proof.PIN
        state["dirty"]=True
        with self.assertRaisesRegex(ValueError,"SOURCE_DIRTY"):
            proof.inspect_exact_checkout(root,runner=runner)
        state["dirty"]=False
        state["bad"]="0"*40
        with self.assertRaisesRegex(ValueError,"BLOB_CHANGED:setup.py"):
            proof.inspect_exact_checkout(root,runner=runner)


if __name__=="__main__":
    unittest.main()
