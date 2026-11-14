"""WSP96 source schemas, randomized intervention, cold memory, public-only checks."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import HiddenConfoundedWorld,rank_gf2,OBS_COUNT,DO_PER_ACTION
from weights import (DirectDoWeights,ConventionalLogistic,IndependentSymbolic,
                     ObservationalNaive,WrongActionAssociation,
                     DeterministicRandomPlan,validate_source,choose_plan)
from experiment import evaluate,classify,SPEC,world_result

class TestWSP96(unittest.TestCase):
    def test_preregistered_worlds_are_distinct(self):
        p=SPEC["source"]
        self.assertEqual((len(p["public_seeds"]),len(p["reserved_dev_seeds"])),(12,20))
        self.assertFalse(set(p["public_seeds"])&set(p["reserved_dev_seeds"]))
        self.assertEqual(rank_gf2((1,2,4,8,16)),5)
        self.assertEqual(rank_gf2((1,1,4,8,16)),4)

    def test_hidden_common_cause_changes_assignment_and_sensor(self):
        world=HiddenConfoundedWorld(7)
        do=world.randomized_interventions()
        logged=world.biased_observational_log()
        self.assertEqual((len(do),len(logged)),(144,144))
        self.assertEqual(len(world.actions),6)
        self.assertEqual(len(set(world.actions)),6)
        self.assertEqual(sum(x["action_id"]==world.control_id for x in do),24)
        self.assertEqual(set(do[0]),{"action_id","trial","observed_outcome"})
        self.assertEqual(set(logged[0]),{"action_id","trial","observed_outcome"})
        self.assertNotEqual(do,logged)
        for row in do+logged:validate_source(row)
        for goal in world.goals():
            self.assertEqual(len(goal.request()),3)
        audit=world.audit_after_scoring()
        self.assertEqual(audit["hidden_mask"].bit_count() if "hidden_mask" in audit
                         else audit["latent_mask"].bit_count(),2)
        self.assertGreater(audit["observed_prevalence_u_favorite"],
                           audit["observed_prevalence_u_others"])

    def test_numeric_program_cold_restore_and_replay(self):
        world=HiddenConfoundedWorld(8)
        raw=world.randomized_interventions()
        model=DirectDoWeights(world.actions)
        for record in raw:model.observe(record)
        self.assertEqual(model.seen,OBS_COUNT)
        self.assertTrue(all(x==DO_PER_ACTION for x in model.n.values()))
        with self.assertRaises(ValueError):model.observe(raw[0])
        snap=model.snapshot()
        restored=DirectDoWeights.restore(snap)
        self.assertEqual(restored.snapshot(),snap)
        for goal in world.goals():
            request=goal.request()
            self.assertEqual(
                restored.plan(world.actions,request["start"],request["target"]),
                model.plan(world.actions,request["start"],request["target"]))
        bad=json.loads(snap)
        bad["body"]["ones"][world.actions[0]][0]+=1
        with self.assertRaises(ValueError):
            DirectDoWeights.restore(json.dumps(bad))
        outsider="f"*16
        while outsider in world.actions:outsider="e"*16
        self.assertIsNone(restored.plan(world.actions[:-1]+(outsider,),0,1))

    def test_all_comparators_get_same_do_data(self):
        world=HiddenConfoundedWorld(9)
        do=world.randomized_interventions()
        c=DirectDoWeights(world.actions)
        sym=IndependentSymbolic(world.actions)
        for row in do:c.observe(row);sym.observe(row)
        ordinary=ConventionalLogistic(world.actions)
        ordinary.fit(do)
        self.assertEqual(ordinary.training_examples,144)
        self.assertEqual(c.effects(),sym.effects())
        self.assertEqual(c.effects(),ordinary.effects())
        for g in world.goals():
            request=g.request()
            self.assertEqual(c.plan(world.actions,request["start"],request["target"]),
                             sym.plan(world.actions,request["start"],request["target"]))
        wrong=WrongActionAssociation(c,world.control_id)
        self.assertNotEqual(wrong.map,c.effects())

    def test_observational_control_is_distinct_and_blinded(self):
        world=HiddenConfoundedWorld(10)
        logged=world.biased_observational_log()
        naive=ObservationalNaive(world.actions)
        for row in logged:naive.observe(row)
        self.assertEqual(len(naive.seen_trials),144)
        self.assertEqual(sum(naive.n.values()),144)
        self.assertNotIn("latent_mask",logged[0])
        self.assertNotIn("u",logged[0])
        with self.assertRaises(ValueError):naive.observe(logged[0])

    def test_original_public_checks_are_not_positive_only(self):
        report=classify(evaluate(reserved=False),reserved=False)
        print("WSP96_PUBLIC_FIXTURE="+json.dumps({
            "classification":report["classification"],
            "checks":report["checks"],
            "scores":report["correct"],
            "worlds":report["worlds"],"goals":report["goals"],
            "interventions":report["real_randomized_do_interventions"],
            "observational_records":report["passively_logged_observations"],
            "causal_assignment_shift_worlds":report["latent_action_assignment_shift_worlds"],
            "naive_misbinding_worlds":report["naive_favorite_misbound_worlds"],
            "effect_bits":report["true_do_effect_bits_correct"],
            "cold":report["cold_world_restored"],
            "cpu_ns":report["whole_process_cpu_ns"],
            "source_and_prediction_sha256":[r["plans_sha256_before_scoring"] for r in report["world_receipts"]],
        },sort_keys=True),flush=True)
        self.assertEqual(report["worlds"],12)
        self.assertEqual(report["goals"],240)
        expected=(SPEC["frozen"]["public_positive"] if all(report["checks"].values())
                  else SPEC["frozen"]["public_negative"])
        self.assertEqual(report["classification"],expected)

if __name__=="__main__":
    unittest.main()
