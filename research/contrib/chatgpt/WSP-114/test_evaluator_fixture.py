"""Complete WSP114 evaluator fixture with wholly fabricated law responses.

The hidden original WSP114 oracle is never imported or opened: fake oracle
functions are injected before importing the evaluation-only module.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from hashlib import sha256

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from native import NativeWriter
from controls import independent_predict

def fake_parameters(nodes,world):
    return tuple(sum(1<<k for k in range(min(12,j)+
             (min(12,j)*(min(12,j)-1))//2)
              if sha256(f"FAKE|WSP114|{nodes}|{world}|{j}|{k}".encode()).digest()[0]%7==0)
              for j in range(nodes))

def fake_train(nodes=16,seed="fixture"):
    data=[]
    for world in range(32):
        model=fake_parameters(nodes,world+101)
        group=[]
        for i in range(256):
            s,a=NativeWriter.candidate(world,i,0,nodes,"WSP114|FAKE|TRAIN")
            group.append((s,a,independent_predict(s,a,model,nodes)))
        data.append(tuple(group))
    return tuple(data)

def fake_heldout(nodes,world,count=16,seed="fixture"):
    return tuple(NativeWriter.candidate(world,i,0,nodes,"WSP114|FAKE|HOLDOUT")
                 for i in range(count))

def fake_transfer(nodes,world,state,action,seed="fixture"):
    return independent_predict(state,action,fake_parameters(nodes,world),nodes)

class TestWholeEvaluatorWithoutOriginalOracle(unittest.TestCase):
    def test_two_world_32_first_downward_prefix_control_and_sealing(self):
        module=types.ModuleType("oracle")
        module.common_training=fake_train
        module.heldout_inputs=fake_heldout
        module.transfer_effect=fake_transfer
        existing=sys.modules.get("oracle")
        try:
            sys.modules["oracle"]=module
            spec=importlib.util.spec_from_file_location(
                "wsp114_fabricated_evaluator_only",HERE/"experiment.py")
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            test=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test)
            result=test.evaluation_capacity(
                nodes=16,worlds=2,budget=32,ladder=(32,16,8),heldout=16)
        finally:
            if existing is None:sys.modules.pop("oracle",None)
            else:sys.modules["oracle"]=existing
        self.assertEqual(result["primary_nodes"],16)
        self.assertEqual(result["worlds"],2)
        self.assertEqual(result["max_interventions_per_arm_per_world"],32)
        self.assertEqual(result["budget_ladder"],[32,16,8])
        self.assertEqual(result["heldout_full_state_per_arm_per_budget"],32)
        self.assertEqual(result["native_cold_restore_worlds"],2)
        self.assertTrue(result["tampered_checkpoint_rejected"])
        self.assertEqual(result["per_arm_all_inclusive_observed_cpu_wall_peak"]
                         ["direct"]["observations"],64)
        self.assertFalse(result["scientific_pass"])
        self.assertEqual(len(result["original_before_score_all_arm_transcript_and_prediction_sha256"]),64)
        self.assertEqual(result["scores"]["direct"]["32"]["full_total"],32)
        self.assertEqual(result["scores"]["matched_independent_symbolic"]["8"]["full_total"],32)
        self.assertEqual(result["scores"]["conventional_ridge"]["16"]["full_total"],32)

if __name__=="__main__":
    unittest.main()
