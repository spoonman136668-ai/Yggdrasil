"""F45 source-free causal context/unknown degree negative and regression tests."""
import json
from pathlib import Path
import tempfile
import unittest

from f45_context_causal_induction_dev import (
    PREREG, FullyFittedMLE, LocalContextWeights,
    MODES, RejectedF45, REPS, SEEDS, SIZES, ContextWorld,
    PATTERNS, preflight, experiment, run, two_step_graph,
)


class F45FrozenCausalWorlds(unittest.TestCase):
    def test_frozen_prereg_precedes_code(self):
        p=preflight()
        self.assertEqual(p["status"],"FROZEN_PRE_CODE_PRE_RESULTS")
        self.assertEqual(p["source_parent_sha"],
                         "a654c7efd30c5ebe32b38f944e819a9c899317a4")
        self.assertEqual(p["worlds"]["sizes_high_first"],list(SIZES))
        self.assertEqual(p["worlds"]["seeds"],list(SEEDS))
        self.assertEqual(p["worlds"]["repetitions_high_first"],list(REPS))
        self.assertTrue(all(p["fences"].values()))

    def test_frozen_threshold_drift_rejected_without_modifying_source(self):
        doc=json.loads(PREREG.read_text(encoding="utf-8"))
        doc["evaluation"]["thresholds"]["highest_budget_macro_direct_F1_min"]=0
        with tempfile.TemporaryDirectory() as tmp:
            temp=Path(tmp)/"changed_prereg.json"
            temp.write_text(json.dumps(doc),encoding="utf-8")
            with self.assertRaisesRegex(RejectedF45,"FROZEN_PRECODE_MANIFEST_DRIFT"):
                preflight(temp)

    def test_each_world_has_hidden_variable_degree_without_leak(self):
        for n in SIZES:
            for seed in SEEDS:
                w=ContextWorld(n,seed)
                twin=ContextWorld(n,seed)
                self.assertEqual(w.mode,MODES[seed])
                self.assertEqual(w.evaluator_only_truth(),twin.evaluator_only_truth())
                degrees=w.evaluator_degree_histogram()
                self.assertEqual(sum(degrees.values()),n)
                self.assertEqual(set(degrees),{"0","1","2","4","8"})
                self.assertEqual(w.public_intervention(0,0,1,0),
                                 twin.public_intervention(0,0,1,0))
                self.assertEqual(len(w.public_intervention(0,1,0,0)),n)
                for (c,s,t),direction in w.evaluator_only_truth().items():
                    self.assertNotEqual(s,t)
                    self.assertIn(direction,(-1,1))
                if seed==71:
                    self.assertTrue(all(c==1 for c,s,t in w.evaluator_only_truth()))
                if seed==83:
                    truth=w.evaluator_only_truth()
                    self.assertTrue(truth)
                    self.assertTrue(all(truth[(1,s,t)]==-sign
                        for (c,s,t),sign in truth.items() if c==0))
                if seed==59:
                    truth=w.evaluator_only_truth()
                    self.assertTrue(all(truth[(1,s,t)]==sign
                        for (c,s,t),sign in truth.items() if c==0))

    def test_only_frozen_worlds_and_public_actions(self):
        for n,seed in ((8,59),(128,59),(64,91),(64,True)):
            with self.subTest(n=n,seed=seed), self.assertRaisesRegex(
                    RejectedF45,"WORLD_NOT_PREDECLARED"):
                ContextWorld(n,seed)
        world=ContextWorld(16,59)
        for args in ((16,0,1,0),(0,2,1,0),(0,1,2,0),(0,1,1,24)):
            with self.subTest(args=args),self.assertRaisesRegex(
                    RejectedF45,"INTERVENTION_NOT_IN_FROZEN_DOMAIN"):
                world.public_intervention(*args)

    def test_public_interventions_only_and_equal_information(self):
        world=ContextWorld(16,83)
        native=LocalContextWeights(16)
        control=FullyFittedMLE(16)
        for s in range(16):
            for context in (0,1):
                for rep in range(6):
                    for action in (0,1):
                        y=world.public_intervention(s,context,action,rep)
                        native.observe(s,context,action,y)
                        control.observe(s,context,action,y)
        self.assertEqual(native.inferred(),control.inferred())
        self.assertEqual(native.checkpoint(),
                         LocalContextWeights.restore(native.checkpoint()).checkpoint())
        self.assertEqual(len(native.checkpoint()),6+8*16+4*16*16+32)
        self.assertIn((1,1),PATTERNS)
        self.assertIn((0,1),PATTERNS)
        self.assertIn((1,-1),PATTERNS)

    def test_passive_contrast_and_invalid_observations(self):
        world=ContextWorld(16,59)
        native=LocalContextWeights(16)
        for s in range(16):
            for c in (0,1):
                for rep in range(3):
                    native.observe(s,c,0,world.public_intervention(s,c,0,rep))
        self.assertEqual(native.inferred(),{})
        source_checkpoint=native.checkpoint()
        for arguments in ((16,0,0,(0,)*16),(0,2,0,(0,)*16),
                          (0,0,2,(0,)*16),(0,0,1,(0,)*15),
                          (0,0,1,(2,)*16),(0,0,1,tuple([True]*16))):
            with self.subTest(args=arguments[:3]),self.assertRaisesRegex(
                    RejectedF45,"INVALID_PUBLIC_EVIDENCE"):
                native.observe(*arguments)
        self.assertEqual(native.checkpoint(),source_checkpoint)

    def test_cold_rejects_corruption_and_unknown_sizes(self):
        world=ContextWorld(16,71)
        native=LocalContextWeights(16)
        for s in range(16):
            for c in (0,1):
                for action in (0,1):
                    native.observe(s,c,action,world.public_intervention(s,c,action,0))
        raw=native.checkpoint()
        for corrupt in (raw[:-1],raw+b"\x00",raw[:-1]+bytes([raw[-1]^1]),
                        bytes([raw[0]^1])+raw[1:]):
            with self.subTest(length=len(corrupt)),self.assertRaises(RejectedF45):
                LocalContextWeights.restore(corrupt)
        for n in (0,8,128,True):
            with self.subTest(size=n),self.assertRaisesRegex(
                    RejectedF45,"UNREGISTERED_LOCAL_SIZE"):
                LocalContextWeights(n)

    def test_twohop_truth_excludes_ambiguous_paths(self):
        edges={(0,0,1):1,(0,1,2):-1,(0,0,3):-1,(0,3,2):1}
        results,excluded=two_step_graph(edges,16)
        self.assertIn((0,0,2),excluded)
        self.assertNotIn((0,0,2),results)

    def test_true_action_interference_and_cold_retention(self):
        sample=experiment(16,59,6)
        self.assertTrue(sample["genuine_intervention_held_other_source_rows"])
        self.assertGreater(sample["genuine_public_events_after_row_checkpoint"],0)
        self.assertTrue(sample["cold_checkpoint_exact"])
        self.assertTrue(sample["tampered_checkpoint_rejected"])
        self.assertTrue(sample["passive_abstained"])
        self.assertTrue(sample["same_information_independent_MLE_predictions_equal"])
        self.assertEqual(sample["native"]["direct"],
                         sample["fully_fitted_independent_MLE"]["direct"])
        self.assertEqual(sample["native"]["twohop"],
                         sample["fully_fitted_independent_MLE"]["twohop"])
        self.assertEqual(sample["actual_public_interventions"],4*16*6)
        self.assertEqual(sample["public_observed_outcome_bits"],4*16*16*6)

    def test_whole_frozen_high_first_comparison_and_no_science(self):
        data=run()
        self.assertEqual(data["scales_high_first"],[64,32,16])
        self.assertEqual(data["seeds"],[59,71,83])
        self.assertEqual(data["budgets_high_first"],[24,12,6])
        self.assertEqual(len(data["world_results"]),27)
        self.assertIn(data["classification"],(
            "DEV_CONTEXTUAL_CAUSAL_INDUCTION_GO",
            "DEV_CONTEXTUAL_CAUSAL_INDUCTION_NO_GO"))
        for entry in data["world_results"]:
            self.assertTrue(entry["cold_checkpoint_exact"])
            self.assertTrue(entry["tampered_checkpoint_rejected"])
            self.assertTrue(entry["genuine_intervention_held_other_source_rows"])
            self.assertTrue(entry["passive_abstained"])
            self.assertTrue(entry["same_information_independent_MLE_predictions_equal"])
            self.assertEqual(entry["native"]["direct"],
                             entry["fully_fitted_independent_MLE"]["direct"])
        for field in ("hidden_graph_given_to_native","protected_first_use_consumed",
                      "accepted_model_edited","native_superiority_proven",
                      "scientific_pass","deployed"):
            self.assertIs(data[field],False)


if __name__=="__main__":
    unittest.main()
