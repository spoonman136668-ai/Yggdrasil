"""F46 frozen source-free adaptive causal intervention and negative tests."""
import json
from pathlib import Path
import tempfile
import unittest

from f46_active_intervention_dev import (
    F46Rejected, POLICY, SIZES, SEEDS, BUDGETS, MODES, STRATEGIES,
    World, LocalLearner, MLE, Arm, freeze, one_world, run,
)
from f45_context_causal_induction_dev import LocalContextWeights


class TestF46(unittest.TestCase):
    def test_frozen_precode_protocol_and_no_science(self):
        p=freeze()
        self.assertEqual(p["status"],"FROZEN_BEFORE_ANY_F46_CODE_OR_OUTCOME")
        self.assertEqual(p["parent_exact_f45_sha"],
                         "7223f0cb2f3862261906b5640f53751c1a1e3689")
        self.assertEqual(p["new_worlds"]["sizes_high_first"],[64,32,16])
        self.assertEqual(p["new_worlds"]["fresh_development_seeds"],[107,109,113])
        self.assertEqual(p["new_worlds"]["pair_budgets_per_row_mean_high_first"],[24,12,6])
        self.assertTrue(all(p["fences"].values()))

    def test_prereg_tamper_rejected_without_rewriting_file(self):
        baseline=POLICY.read_bytes()
        p=json.loads(baseline)
        p["frozen_metrics"]["frozen_go"][
            "at_b12_native_active_macro_direct_F1_gain_over_strongest_conventional_min"]=0
        with tempfile.TemporaryDirectory() as td:
            edited=Path(td)/"invalid.json"
            edited.write_text(json.dumps(p),encoding="utf-8")
            with self.assertRaisesRegex(F46Rejected,"FROZEN_PRECODE_BLOB_DRIFT"):
                freeze(edited)
        self.assertEqual(POLICY.read_bytes(),baseline)

    def test_frozen_worlds_and_context_sign_laws(self):
        for n in SIZES:
            for seed in SEEDS:
                x,y=World(n,seed),World(n,seed)
                self.assertEqual(x.evaluator_only_truth(),y.evaluator_only_truth())
                self.assertEqual(x.mode,MODES[seed])
                histogram=x.evaluator_degree_histogram()
                self.assertEqual(set(histogram),{"0","1","2","4","8"})
                self.assertEqual(sum(histogram.values()),n)
                self.assertEqual(x.intervene(0,0,1,0),y.intervene(0,0,1,0))
                graph=x.evaluator_only_truth()
                self.assertTrue(all(s!=t and v in (-1,1)
                                    for (c,s,t),v in graph.items()))
                if seed==109:
                    self.assertTrue(all(c==1 for c,s,t in graph))
                if seed==107:
                    self.assertTrue(all(graph[(1,s,t)]==v
                                        for (c,s,t),v in graph.items() if c==0))
                if seed==113:
                    self.assertTrue(all(graph[(1,s,t)]==-v
                                        for (c,s,t),v in graph.items() if c==0))
        for n,seed in ((8,107),(128,107),(64,59),(64,True)):
            with self.subTest(n=n,seed=seed),self.assertRaisesRegex(
                    F46Rejected,"WORLD_NOT_FROZEN"):
                World(n,seed)

    def test_public_actions_and_partial_or_rogue_evidence_rejected(self):
        w=World(16,107)
        for args in ((16,0,0,0),(0,2,0,0),(0,1,2,0),(0,1,0,48)):
            with self.subTest(args=args),self.assertRaisesRegex(
                    F46Rejected,"INVALID_PUBLIC_INTERVENTION"):
                w.intervene(*args)
        m=LocalLearner(16)
        for args in ((0,0,(0,)*15,(1,)*16),(0,0,(0,)*16,(2,)*16),
                     (16,0,(0,)*16,(1,)*16),(0,2,(0,)*16,(1,)*16)):
            with self.subTest(args=args[:2]),self.assertRaisesRegex(
                    F46Rejected,"INCOMPLETE_OR_UNREGISTERED_PUBLIC_PAIR"):
                m.observe_pair(*args)
        self.assertEqual(m.seen,[[0]*16,[0]*16])

    def test_same_observation_native_and_fully_fitted_mle_parity(self):
        w=World(16,107)
        native,mle=LocalLearner(16),MLE(16)
        for s in range(16):
            for c in (0,1):
                for k in range(6):
                    a,b=w.intervene(s,c,0,k),w.intervene(s,c,1,k)
                    native.observe_pair(s,c,a,b)
                    mle.observe_pair(s,c,a,b)
        self.assertEqual(native.inferred(),mle.independent_inferred())
        raw=native.checkpoint()
        self.assertEqual(len(raw),6+4*16+4*16*16+32)
        restored=LocalLearner.restore(raw)
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(restored.inferred(),native.inferred())

    def test_cold_tamper_fails_closed_and_real_interference_isolated(self):
        w=World(16,113)
        n=LocalLearner(16)
        for s in range(16):
            for c in (0,1):
                n.observe_pair(s,c,w.intervene(s,c,0,0),w.intervene(s,c,1,0))
        raw=n.checkpoint()
        for altered in (raw[:-1],raw+b"\x00",
                        raw[:-1]+bytes([raw[-1]^1]),
                        bytes([raw[0]^1])+raw[1:]):
            with self.subTest(length=len(altered)),self.assertRaises(F46Rejected):
                LocalLearner.restore(altered)
        clone=LocalLearner.restore(raw)
        before=(list(clone.weights[:16]),list(clone.weights[16*16:16*16+16]))
        clone.observe_pair(15,1,w.intervene(15,1,0,1),w.intervene(15,1,1,1))
        self.assertEqual(clone.weights[:16],before[0])
        self.assertEqual(clone.weights[16*16:16*16+16],before[1])
        self.assertNotEqual(clone.checkpoint(),raw)

    def test_passive_only_lacks_identifiable_contrast(self):
        w=World(16,109)
        p=LocalContextWeights(16)
        for s in range(16):
            for c in (0,1):
                for k in range(6):
                    p.observe(s,c,0,w.intervene(s,c,0,k))
        self.assertEqual(p.inferred(),{})

    def test_initial_policy_source_coverage_and_equal_fitted_predictions(self):
        w=World(16,107)
        for policy in STRATEGIES:
            arm=Arm(policy,16,107)
            for step in range(32):
                arm.step(w,step)
            if policy in ("native_active","conventional_active","uniform"):
                self.assertEqual({(c,s) for c in (0,1) for s in range(16)},
                                 {(c,s) for c,s,k in arm.visited})
            result=arm.checkpoint_report(w,1)
            self.assertEqual(result["pairs"],32)
            self.assertTrue(result["cold_restore_exact"])
            self.assertTrue(result["real_intervention_held_unrelated_row"])
            self.assertEqual(result["native"],result["fully_fitted_independent_MLE"])

    def test_frozen_high_first_single_world(self):
        records,elapsed=one_world(16,107)
        self.assertGreaterEqual(elapsed,0)
        self.assertEqual([v["mean_repetitions_per_row"] for v in records],[24,12,6])
        for rec in records:
            self.assertEqual(set(rec["policy_results"]),set(STRATEGIES))
            self.assertTrue(rec["native_and_conventional_active_same_choice_history"])
            b=rec["mean_repetitions_per_row"]
            for v in rec["policy_results"].values():
                self.assertEqual(v["pairs"],2*16*b)
                self.assertEqual(v["individual_actions"],4*16*b)
                self.assertEqual(v["public_outcome_bits"],4*16*16*b)
                self.assertTrue(v["cold_restore_exact"])
                self.assertTrue(v["tamper_rejected"])
                self.assertTrue(v["same_stream_independent_MLE_equal"])
                self.assertTrue(v["real_intervention_held_unrelated_row"])

    def test_full_frozen_worlds_and_conventional_no_science(self):
        d=run()
        self.assertEqual(len(d["world_results"]),27)
        self.assertEqual(d["nodes_high_first"],[64,32,16])
        self.assertEqual(d["development_seeds"],[107,109,113])
        self.assertEqual(d["budgets_high_first"],[24,12,6])
        self.assertTrue(d["budgets_and_controls_consistent"])
        self.assertIn(d["classification"],
                      ("DEV_ACTIVE_INTERVENTION_POLICY_GO",
                       "DEV_ACTIVE_INTERVENTION_POLICY_NO_GO"))
        for k in ("hidden_world_graph_to_learner","protected_scientific_first_use",
                  "accepted_Yggdrasil_source_changed","scientific_pass","deployed"):
            self.assertIs(d[k],False)


if __name__=="__main__":
    unittest.main()
