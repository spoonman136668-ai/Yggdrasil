"""WSP95 public-only engineering and scientific classification tests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import NoisyWorld,N_ACTIONS,N_CHANNELS,N_CAUSAL
from weights import (DirectCounts,SymbolicHistogram,FullyTrainedLogistic,
                     WrongActionAssociation,plan_from_estimates,validate_record)
from experiment import (get_policy_observations,original_world,evaluate,
                        classify,PROTOCOL)

class TestWSP95(unittest.TestCase):
    def test_frozen_original_world_cohorts_disjoint(self):
        public=PROTOCOL["world"]["public_seeds"]
        reserved=PROTOCOL["world"]["reserved_dev_seeds"]
        self.assertEqual((len(public),len(reserved)),(12,20))
        self.assertFalse(set(public)&set(reserved))
        w=NoisyWorld(public[0])
        self.assertEqual((len(w.actions),len(w.actual_causal_channels())),(6,5))
        self.assertEqual(len(w.goals()),35)
        self.assertEqual(
            tuple((g.index,g.start,g.target) for g in w.goals()),
            tuple((g.index,g.start,g.target) for g in NoisyWorld(public[0]).goals()))

    def test_paired_real_probes_unlabeled_nuisance(self):
        w=NoisyWorld(95011)
        source=w.probe(w.actions[0],0)
        self.assertEqual(source,w.probe(w.actions[0],0))
        self.assertEqual(set(source),
                         {"action_id","probe_index","sensor_before","sensor_after"})
        validate_record(source)
        with self.assertRaises(ValueError):
            w.probe("unregistered",0)
        with self.assertRaises(ValueError):
            w.probe(w.actions[0],30)

    def test_identical_30_action_budgets_across_policies(self):
        w=NoisyWorld(95012)
        active,oa=get_policy_observations(w,"active")
        uniform,ou=get_policy_observations(w,"uniform")
        random,orr=get_policy_observations(w,"random")
        self.assertEqual((len(oa),len(ou),len(orr)),(30,30,30))
        self.assertTrue(all(v==5 for v in active.n.values()))
        self.assertTrue(all(v==5 for v in uniform.n.values()))
        self.assertEqual(sum(random.n.values()),30)
        pooled={(r["action_id"],r["probe_index"]):(
                 r["sensor_before"],r["sensor_after"]) for r in oa}
        self.assertTrue(all(pooled[(r["action_id"],r["probe_index"])]==
             (r["sensor_before"],r["sensor_after"]) for r in ou))
        for r in orr:
            key=(r["action_id"],r["probe_index"])
            if key in pooled:
                self.assertEqual(pooled[key],
                                 (r["sensor_before"],r["sensor_after"]))

    def test_weights_preserve_source_counts_and_no_uncertain_replay(self):
        w=NoisyWorld(95013)
        m=DirectCounts(w.actions)
        obs=w.probe(m.choose_action(),0)
        m.observe(obs)
        with self.assertRaises(ValueError):
            m.observe(obs)
        self.assertEqual(m.interventions,1)
        self.assertEqual(sum(m.n.values()),1)
        self.assertEqual(len(m.stable_channels()),5)
        snapshot=m.snapshot()
        self.assertEqual(DirectCounts.restore(snapshot).snapshot(),snapshot)
        changed=json.loads(snapshot)
        a=next(iter(changed["payload"]["counts"]))
        changed["payload"]["counts"][a][0]+=1
        with self.assertRaises(ValueError):
            DirectCounts.restore(json.dumps(changed))
        unknown="f"*16
        while unknown in w.actions:unknown="e"*16
        self.assertIsNone(m.plan(w.actions[:-1]+(unknown,),0,1))

    def test_strong_conventional_and_symbolic_same_observed_data(self):
        w=NoisyWorld(95014)
        m,rows=get_policy_observations(w,"active")
        symbolic=SymbolicHistogram(w.actions)
        for row in rows:symbolic.observe(row)
        self.assertEqual(m.stable_channels(),symbolic.stable())
        self.assertEqual(m.effects(),symbolic.effects())
        conventional=FullyTrainedLogistic(w.actions)
        conventional.fit(rows)
        self.assertEqual(conventional.records,30)
        self.assertEqual(len(conventional.effects()),6)
        for goal in w.goals():
            a=m.plan(w.actions,goal.start,goal.target)
            b=symbolic.plan(w.actions,goal.start,goal.target)
            self.assertEqual(a,b)
        wrong=WrongActionAssociation(m)
        self.assertNotEqual(wrong.effects_map,m.effects())

    def test_original_public_first_use_classifies_without_retuning(self):
        report=classify(evaluate(reserved=False),reserved=False)
        print("WSP95_PUBLIC_RESULT="+json.dumps({
            "classification":report["classification"],
            "checks":report["checks"],
            "correct":report["correct"],
            "worlds":report["world_count"],
            "goals":report["goals"],
            "actions_by_policy":report["observed_interventions"],
            "direct_true_effect_bits_correct":report["direct_true_effect_bits_correct"],
            "conventional_true_effect_bits_correct":report["conventional_true_effect_bits_correct"],
            "stable_channel_worlds":report["causal_channel_maps_correct"],
            "cold":report["cold_exact_count"],
            "cpu_ns":report["whole_process_cpu_ns"],
            "source_frozen_predictions_hashes":[
                x["pre_outcome_predictions_sha256"] for x in report["world_receipts"]],
        },sort_keys=True),flush=True)
        expected=(PROTOCOL["frozen"]["positive_public"] if all(report["checks"].values())
                  else PROTOCOL["frozen"]["negative_public"])
        self.assertEqual(report["classification"],expected)
        self.assertEqual(report["world_count"],12)
        self.assertEqual(report["goals"],420)
        self.assertEqual(report["correct"]["independent_symbolic"],
                         report["correct"]["direct_active"])
        self.assertEqual(report["correct"]["oracle_ceiling"],420)

if __name__=="__main__":
    unittest.main()
