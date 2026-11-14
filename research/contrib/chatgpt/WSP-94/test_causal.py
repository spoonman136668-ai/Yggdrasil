"""WSP94 public-only tests, no hidden reserved world first-use."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import HiddenCausalWorld,gf2_rank,ACTIONS,MASK
from weights import (DirectNumeric,FullyTrainedConventional,IndependentSymbolic,
                     WrongActionBinding,PassiveNoIdentity,DeterministicRandom,
                     effect_bits,verify_observation)
from experiment import one_world,evaluate,classify,PROTOCOL

class WSP94CausalTests(unittest.TestCase):
    def test_world_seed_disjointness_no_reserve_on_public(self):
        public=PROTOCOL["scope"]["public_world_seeds"]
        reserved=PROTOCOL["scope"]["reserved_world_seeds"]
        self.assertEqual((len(public),len(reserved)),(10,20))
        self.assertFalse(set(public)&set(reserved))
        self.assertEqual(gf2_rank((1,2,4,8,16)),5)
        self.assertEqual(gf2_rank((1,1,4,8,16)),4)

    def test_true_five_action_probes_and_unseen_compositions(self):
        w=HiddenCausalWorld(94011)
        with self.assertRaises(RuntimeError):
            w.heldout_goals()
        a=tuple(x.as_record() for x in w.probe_once_per_action())
        self.assertEqual(len(a),5)
        self.assertEqual(w.real_probe_action_count,5)
        self.assertTrue(all(set(x)=={"action_id","causal_output_before",
                                    "causal_output_after","nuisance_before",
                                    "nuisance_after"} for x in a))
        self.assertEqual(len({x["action_id"] for x in a}),ACTIONS)
        with self.assertRaises(RuntimeError):
            w.probe_once_per_action()
        g=w.heldout_goals()
        self.assertEqual(len(g),20)
        self.assertEqual(len({(x.start,x.target,x.goal_id) for x in g}),20)
        self.assertTrue(all(x.max_actions==3 for x in g))

    def test_direct_inference_symbolic_and_trained_conventional(self):
        w=HiddenCausalWorld(94012)
        observations=tuple(x.as_record() for x in w.probe_once_per_action())
        direct=DirectNumeric()
        symbolic=IndependentSymbolic()
        for obs in observations:
            direct.observe(obs);symbolic.observe(obs)
        other=FullyTrainedConventional()
        other.fit(observations)
        self.assertEqual(other.fitted_bits(observations),(25,25))
        self.assertEqual(direct.observed,5)
        self.assertEqual(len(direct.weights),5)
        for obs in observations:
            action=obs["action_id"]
            self.assertEqual(direct.effect(action),effect_bits(obs))
            self.assertEqual(other.effect(action),effect_bits(obs))
        for goal in w.heldout_goals():
            request=goal.for_model()
            for m in (direct,other,symbolic):
                p=m.plan(w.action_ids,request["start"],request["target"],3)
                self.assertIsNotNone(p)
                self.assertEqual(w.execute(goal.start,p),goal.target)
        with self.assertRaises(ValueError):
            direct.observe(observations[0])
        self.assertIsNone(direct.plan(tuple(w.action_ids[:-1])+("f"*16,),0,0))

    def test_numeric_cold_restore_corruption_and_observation_schema(self):
        world=HiddenCausalWorld(94013)
        observations=tuple(x.as_record() for x in world.probe_once_per_action())
        d=DirectNumeric()
        for x in observations:d.observe(x)
        snapshot=d.snapshot()
        restored=DirectNumeric.restore(snapshot)
        self.assertEqual(snapshot,restored.snapshot())
        bad=json.loads(snapshot)
        name=next(iter(bad["payload"]["weights"]))
        bad["payload"]["weights"][name][0]=1.0-bad["payload"]["weights"][name][0]
        with self.assertRaises(ValueError):
            DirectNumeric.restore(json.dumps(bad))
        bad_source=dict(observations[0])
        bad_source["hidden_signature"]=7
        with self.assertRaises(ValueError):
            verify_observation(bad_source)
        with self.assertRaises(ValueError):
            verify_observation({**observations[0],"nuisance_after":99})

    def test_independent_negative_ablation_arms(self):
        outcome=one_world(94014)
        self.assertEqual(outcome["intervention_actions_used"],5)
        self.assertEqual(outcome["result_correct"]["direct_numeric"],20)
        self.assertEqual(outcome["result_correct"]["symbolic_exact"],20)
        self.assertEqual(outcome["result_correct"]["conventional_trained"],20)
        self.assertLess(outcome["result_correct"]["shuffled_action"],20)
        self.assertLess(outcome["result_correct"]["passive_no_identity"],20)
        self.assertTrue(outcome["cold_restore"] and outcome["tamper_rejected"])
        self.assertTrue(outcome["unknown_action_abstains"])

    def test_frozen_public_result_accepts_positive_or_negative(self):
        r=classify(evaluate(reserved=False),reserved=False)
        print("WSP94_PUBLIC_RESULT="+json.dumps({
            "classification":r["classification"],
            "criteria":r["checks"],
            "correct":r["correct"],
            "worlds":r["seed_count"],
            "goals":r["goal_questions_total"],
            "interventions":r["actual_intervention_actions_total"],
            "source_bits_fit":r["direct_signature_bits_correct"],
            "ordinary_bits_fit":r["conventional_signature_bits_correct"],
            "cold":r["cold_worlds_restored_exact"],
            "whole_cpu_ns":r["whole_process_cpu_ns"],
            "proofs":[x["predictions_sha256_before_execution"]
                      for x in r["source_and_prediction_receipts"]],
        },sort_keys=True),flush=True)
        self.assertIn(r["classification"],("PUBLIC_CAUSAL_SLOT_FEASIBLE",
                                            "PUBLIC_CAUSAL_SLOT_NEGATIVE"))
        self.assertEqual(r["classification"],
                         "PUBLIC_CAUSAL_SLOT_FEASIBLE" if all(r["checks"].values())
                         else "PUBLIC_CAUSAL_SLOT_NEGATIVE")
        self.assertEqual(r["seed_count"],10)
        self.assertEqual(r["goal_questions_total"],200)

if __name__=="__main__":
    unittest.main()
