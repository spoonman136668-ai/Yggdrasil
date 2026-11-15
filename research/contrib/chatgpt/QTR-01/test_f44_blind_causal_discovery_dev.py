"""F44 source-free intervention-learning DEV and fail-closed controls."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from f44_blind_causal_discovery_dev import (
    InvalidF44, PREREG, BUDGETS, SIZES, SEEDS, CausalWorld,
    LocalBinding, FullyFittedBernoulli, freeze, do_world, run, twohop,
)


class F44BlindInterventionDEV(unittest.TestCase):
    def test_exact_prereg_frozen_before_execution(self):
        p=freeze()
        self.assertEqual(p["worlds"]["scales_nodes_high_to_low"],[64,32,16])
        self.assertEqual(p["worlds"]["development_seeds"],[11,29,47])
        self.assertEqual(p["worlds"]["high_first_readout_replicates_per_arm"],[24,12,6])
        self.assertEqual(p["exact_parent_F43"],"8f49febe7a83d13c6db9083deb0007f33bc28316")
        self.assertTrue(all(p["protected_fences"].values()))

    def test_tampered_frozen_threshold_fails_before_first_use(self):
        original=PREREG.read_bytes()
        p=json.loads(original)
        p["frozen_evaluation"]["thresholds"]["at_max_replicates_direct_recall_min"]=0.0
        with tempfile.TemporaryDirectory() as td:
            before=PREREG.read_bytes()
            try:
                PREREG.write_text(json.dumps(p),encoding="utf-8")
                with self.assertRaisesRegex(InvalidF44,"PREREG_BLOB_CHANGED"):
                    freeze()
            finally:
                PREREG.write_bytes(before)
        self.assertEqual(PREREG.read_bytes(),original)

    def test_deterministic_hidden_signed_graph_generation(self):
        for n in SIZES:
            for seed in SEEDS:
                a,b=CausalWorld(n,seed),CausalWorld(n,seed)
                truth=a.truth_for_scoring_only()
                self.assertEqual(truth,b.truth_for_scoring_only())
                self.assertEqual(len(truth),2*n)
                for s in range(n):
                    row=[v for (source,target),v in truth.items() if source==s]
                    self.assertEqual(sorted(row),[-1,1])
                    self.assertTrue(all(s!=t for s0,t in truth if s0==s))
                self.assertEqual(a.intervene(0,1,0),b.intervene(0,1,0))
                self.assertEqual(len(a.intervene(0,1,0)),n)

    def test_unregistered_worlds_rejected(self):
        for n,seed in [(8,11),(128,11),(64,19),(64,True)]:
            with self.subTest(n=n,seed=seed),self.assertRaises(InvalidF44):
                CausalWorld(n,seed)
        world=CausalWorld(16,11)
        for args in [(0,2,0),(16,0,0),(0,0,24),(-1,1,0)]:
            with self.subTest(args=args),self.assertRaises(InvalidF44):
                world.intervene(*args)

    def test_actual_public_action_learning_is_not_supplied_graph(self):
        w=CausalWorld(16,11)
        m=LocalBinding(16)
        baseline=FullyFittedBernoulli(16)
        for s in range(16):
            for repetition in range(6):
                for action in (0,1):
                    outcomes=w.intervene(s,action,repetition)
                    m.observe(s,action,outcomes)
                    baseline.observe(s,action,outcomes)
        self.assertEqual(m.inferred(),baseline.inferred())
        self.assertEqual(len(m.snapshot()),6+4*16+2*16*16+32)
        self.assertEqual(m.inferred(),LocalBinding.restore(m.snapshot()).inferred())
        self.assertNotEqual(m.inferred(),w.truth_for_scoring_only())  # low-budget limits

    def test_passive_only_and_wrong_action_inputs_are_rejected(self):
        w=CausalWorld(16,11)
        m=LocalBinding(16)
        for s in range(16):
            for rep in range(6):
                m.observe(s,0,w.intervene(s,0,rep))
        self.assertEqual(m.inferred(),{})
        before=m.snapshot()
        for source,action,vector in [(16,0,(0,)*16),(0,2,(0,)*16),
                                     (0,1,(0,)*15),(0,1,(2,)*16)]:
            with self.subTest(source=source,action=action),self.assertRaises(InvalidF44):
                m.observe(source,action,vector)
        self.assertEqual(m.snapshot(),before)

    def test_snapshot_tamper_and_cold_interference(self):
        w=CausalWorld(16,11)
        m=LocalBinding(16)
        for s in range(16):
            for a in (0,1):
                m.observe(s,a,w.intervene(s,a,0))
        saved=m.snapshot()
        self.assertEqual(saved,LocalBinding.restore(saved).snapshot())
        for sample in (saved[:-1],saved+b"\x00",saved[:-1]+bytes((saved[-1]^1,))):
            with self.assertRaises(InvalidF44):
                LocalBinding.restore(sample)
        other=LocalBinding.restore(saved)
        row0=other.weights[:16]
        other.observe(15,1,w.intervene(15,1,1))
        self.assertEqual(other.weights[:16],row0)
        self.assertNotEqual(other.snapshot(),saved)

    def test_twohop_signed_composition_excludes_ambiguous(self):
        synthetic={(0,1):1,(1,2):-1,(0,3):-1,(3,2):1}
        paths,ambiguous=twohop(synthetic,16)
        self.assertNotIn((0,2),paths)
        self.assertIn((0,2),ambiguous)
        self.assertEqual(paths,{})

    def test_high_first_intervention_stages_share_world(self):
        for b in BUDGETS:
            out=do_world(16,11,b)
            self.assertEqual(out["public_interventions"],2*16*b)
            self.assertEqual(out["public_binary_outcomes"],2*16*16*b)
            self.assertEqual(out["true_signed_edges"],32)
            self.assertTrue(out["cold_exact"])
            self.assertTrue(out["tampered_cold_rejected"])
            self.assertTrue(out["passive_control_abstained"])
            self.assertTrue(out["other_source_row_unmodified_after_interference"])
            self.assertTrue(out["same_statistic_control_predictions_identical"])
            self.assertEqual(out["native"]["direct"],out["fully_fitted_conventional"]["direct"])
            self.assertEqual(out["native"]["twohop"],out["fully_fitted_conventional"]["twohop"])
            self.assertLess(out["wrong_source_permutation"]["direct"]["f1"],
                            out["native"]["direct"]["f1"])
            self.assertTrue(out["native_checkpoint_sha256"])

    def test_full_frozen_breadth_and_null_advantage_report(self):
        result=run()
        self.assertEqual(result["high_first_budget_order"],list(BUDGETS))
        self.assertEqual(result["scale_order"],list(SIZES))
        self.assertEqual(result["seeds"],list(SEEDS))
        self.assertEqual(len(result["world_results"]),27)
        self.assertIn(result["classification"],(
            "DEV_CAUSAL_EDGE_INDUCTION_GO","DEV_CAUSAL_EDGE_INDUCTION_NO_GO"))
        self.assertIs(result["exact_hidden_graph_supplied_to_learner"],False)
        self.assertIs(result["prospective_protected_world_first_use"],False)
        self.assertIs(result["accepted_native_model_source_changed"],False)
        self.assertIs(result["native_scientific_advantage"],False)
        self.assertIs(result["scientific_pass"],False)
        self.assertIs(result["deployment"],False)
        self.assertTrue(all(r["same_statistic_control_predictions_identical"]
                            for r in result["world_results"]))
        self.assertTrue(all(r["cold_exact"] for r in result["world_results"]))


if __name__=="__main__":
    unittest.main()
