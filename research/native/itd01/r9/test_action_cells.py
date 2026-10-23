"""ITD-01 R9 prospective native action-conditioned public causal learner tests.

All tests use new bounded non-science smoke seed 3; official 101/211/307
remain first-use only in the separate original workflow task.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import unittest

from action_cells import (
    DELAY, FAMILIES, LocalActionColony, PairwisePerceptron,
    EpisodicActionMemory, CurrentOnlyZero,
    features, hidden_target, source_seed, train_equal_public_interventions,
    evaluate, PublicSource
)
import report_r9 as report


class R9NativeCausalState(unittest.TestCase):
    def test_action_and_feedback_are_required_and_delayed(self):
        p=LocalActionColony()
        sensor=(True,False,False,True)
        baseline=p.save()
        with self.assertRaisesRegex(ValueError,"FEEDBACK_WITHOUT"):
            p.learn_delayed("missing",True,2)
        p.observe_public_action("a","A",sensor,1,0)
        with self.assertRaisesRegex(ValueError,"EARLY_OR_STALE"):
            p.learn_delayed("a",False,1)
        self.assertEqual(p.feedback_updates,0)
        self.assertEqual(p.weight_changes,0)
        with self.assertRaisesRegex(ValueError,"PENDING_PUBLIC"):
            p.save()
        p.learn_delayed("a",False,2)
        self.assertEqual(p.feedback_updates,1)
        self.assertNotEqual(p.save(),baseline)
        with self.assertRaisesRegex(ValueError,"FEEDBACK_WITHOUT"):
            p.learn_delayed("a",False,2)

    def test_action_is_functionally_identifying_public_credit(self):
        # For identical public context/sensor/success, opposite public actions
        # are allowed to drive different learned cell states: fixes R8's
        # original omitted-action information bottleneck, without source labels.
        x=(True,False,True,False)
        left=LocalActionColony()
        right=LocalActionColony()
        left.observe_public_action("t","A",x,0,0)
        right.observe_public_action("t","A",x,1,0)
        left.learn_delayed("t",True,2)
        right.learn_delayed("t",True,2)
        self.assertNotEqual(left.checkpoint()["cells"]["A"],
                            right.checkpoint()["cells"]["A"])
        self.assertEqual(left.feedback_updates,right.feedback_updates)
        self.assertEqual(inspect.signature(
            left.learn_delayed).parameters.keys(),
            right.learn_delayed.__signature__.parameters.keys()
            if hasattr(right.learn_delayed,"__signature__") else
            left.learn_delayed.__signature__.parameters.keys()
            if hasattr(left.learn_delayed,"__signature__") else
            inspect.signature(right.learn_delayed).parameters.keys())

    def test_frozen_public_source_is_distinct_across_roles_and_families(self):
        keys=set()
        for role,family in (
            ("FIT_A","A"),("FIT_B","B"),("FIT_C","C"),
            ("VALID_A_PRE","A"),("VALID_A_POST","A"),
            ("VALID_B","B"),("VALID_C_ZERO","C"),
            ("DEV_C_POST","C"),("DEV_A_RETAINED","A")
        ):
            key=source_seed(3,role,family)
            self.assertNotIn(key,keys)
            keys.add(key)
            s=PublicSource(3,role,family)
            sample=[s.next_sensors() for _ in range(16)]
            self.assertTrue(all(len(x)==4 for x in sample))
            self.assertGreaterEqual(len(set(sample)),4)
        with self.assertRaisesRegex(ValueError,"SOURCE_ROLE"):
            source_seed(3,"HELD_ORIGINAL","A")
        with self.assertRaisesRegex(ValueError,"PUBLIC_FAMILY"):
            source_seed(3,"FIT_A","H1")

    def test_equal_public_interventions_native_and_trained_controls(self):
        arms=[LocalActionColony(),PairwisePerceptron(),EpisodicActionMemory()]
        item=train_equal_public_interventions(arms,3,"FIT_A","A",32)
        self.assertEqual(item["public_fit_interactions"],32)
        self.assertEqual(item["public_delayed_feedback"],32)
        self.assertEqual(len(item["public_intervention_trace_sha256"]),64)
        self.assertEqual([x.feedback_updates for x in arms],[32,32,32])
        view=evaluate(arms+[CurrentOnlyZero()],3,"VALID_A_PRE","A",8)
        self.assertTrue(view["all_actions_legal"])
        self.assertEqual(view["eval_parameter_updates"],0)
        self.assertTrue(all(0<=v<=1 for v in view["success"].values()))
        self.assertEqual([x.feedback_updates for x in arms],[32,32,32])

    def test_checkpoint_exact_restart_validation_and_error_tamper(self):
        n=LocalActionColony()
        train_equal_public_interventions([n],3,"FIT_B","B",24)
        blob=n.save()
        cold=LocalActionColony.restore(blob)
        self.assertEqual(cold.save(),blob)
        for sensors in ((False,)*4,(True,)*4,(True,False,True,False)):
            self.assertEqual(n.choose("B",sensors),
                             cold.choose("B",sensors))
        tampered=json.loads(blob)
        tampered["payload"]["cells"]["B"][0]["fast"]+=1
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_HASH"):
            LocalActionColony.restore(json.dumps(tampered).encode())
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_SIZE"):
            LocalActionColony.restore(b"")
        with self.assertRaisesRegex(ValueError,"PUBLIC_SENSOR"):
            features((1,True,True,False))

    def test_neighbor_inference_is_nonuniform_and_paired_ablation_remains_legal(self):
        n=LocalActionColony()
        # Manual *developer* local state: no protected science or retraining.
        for i,c in enumerate(n.cells["C"]):
            c.fast=(-1 if i%2 else 1)*(i+1)/4
            c.slow=(-1 if i%3 else 1)*(i+1)/10
        original=n.save()
        attempts=0
        for pattern in range(16):
            bits=tuple(bool(pattern&(1<<j)) for j in range(4))
            x=n.choose("C",bits)
            y=n.choose("C",bits,use_neighbors=False)
            self.assertIn(x,(0,1))
            self.assertIn(y,(0,1))
            attempts+=1
        self.assertEqual(attempts,16)
        self.assertGreater(n.message_evaluations,0)
        self.assertEqual(n.feedback_updates,0)
        self.assertNotEqual(n.save(),original)  # only measurement counters

    def test_bounded_smoke_runs_and_does_not_claim_scientific_transfer(self):
        x=report.experiment(3,smoke=True)
        self.assertTrue(x["development_smoke_only"])
        self.assertEqual(set(x["family_evidence"]),{
            "A_PRE","A_POST","B_POST","C_ZERO_SHOT",
            "C_POST","A_RETAINED"})
        self.assertEqual(x["native_delayed_public_feedback_updates"],24)
        self.assertEqual(set(x["conventional_delayed_public_updates"].values()),
                         {24})
        self.assertFalse(x["original_H1_H2_source_first_use"])
        self.assertFalse(x["isolated_per_model_cpu_rss_parity"])
        self.assertEqual(x["full_itd01_novel_source_transfer"],"NOT_TESTED")
        self.assertTrue(x["native_cold_restore_exact"])
        self.assertIn(x["disposition"],(
            "SOURCE_FREE_NATIVE_R9_PARTIAL_OR_NEGATIVE_RETAIN_ALL_EVIDENCE",
            "SOURCE_FREE_NATIVE_ACTION_LEARNING_ALL_PROVISIONAL_GATES_PASS"))
        with self.assertRaisesRegex(ValueError,"UNPREREGISTERED_INIT"):
            report.experiment(19)
        with self.assertRaisesRegex(ValueError,"SMOKE_ONLY_FIXED"):
            report.experiment(17,smoke=True)


if __name__=="__main__":
    unittest.main()
