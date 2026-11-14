"""MD33 train-only conventional-control safety and fitting checks.

No transfer or cold episode is opened by the focused tests: those cohorts
are reserved for the one-shot frozen evaluation after these tests pass.
"""
import inspect
import json
import math
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "dg1-md32-20261114"))
from synthetic import (LOCK, STARTS, public_teacher_blocks,
                       synthetic_world, structural_split_audit,
                       valid_allocation)
from categorical_controls import (EmpiricalCausalControl,
                                  validate_public_probe)
from recurrent_control import (RecurrentWorldModel, training_arrays)
from evaluate import run_policy
from compositional_relay import canonical, digest


class MD33SyntheticControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train, cls.train_custody = public_teacher_blocks("train")
        cls.validation, cls.val_custody = public_teacher_blocks("validation")

    def test_preregistered_source_and_new_synthetic_splits(self):
        self.assertEqual(LOCK["parent"]["source_sha"],
                         "7551d15cafe9bf028242f009de2218773a7b40ba")
        self.assertEqual(LOCK["status"],
                         "FROZEN_BEFORE_NEW_GENERATOR_BASELINES_OR_OUTCOMES")
        audit = structural_split_audit()
        self.assertTrue(audit["training_transfer_motif_disjoint"])
        self.assertEqual(audit["splits"]["train"]["episodes"], 768)
        self.assertEqual(audit["splits"]["validation"]["episodes"], 192)
        self.assertEqual(audit["splits"]["transfer"]["episodes"], 192)
        self.assertEqual(audit["splits"]["cold"]["episodes"], 96)
        self.assertEqual({x["combinations"] for x in audit["splits"].values()},
                         {24})

    def test_reserved_and_old_science_cohorts_strictly_rejected(self):
        for bad in (True, 9100, 9195, 8301, 8420, 1080001, 2080001,
                    1900001, 2900001, 3900001, 4900001,
                    10999, 11768, 11999, 12192, 12999, 13192, 13999,
                    14096, "11000", -1):
            with self.subTest(seed=bad):
                with self.assertRaisesRegex(
                        AssertionError, "UNAUTHORIZED_OR_OFFICIAL_FIRST_USE_SEED"):
                    synthetic_world(bad)

    def test_all_training_actions_physically_charged_and_public(self):
        self.assertEqual(self.train_custody["charged_actions"], 3072)
        self.assertEqual(self.val_custody["charged_actions"], 768)
        self.assertEqual(len(self.train), 192)
        self.assertEqual(len(self.validation), 48)
        self.assertEqual(len(self.train_custody["public_physical_sha256"]), 64)
        for block in self.train:
            self.assertEqual(len(block), 4)
            for episode in block:
                self.assertEqual(len(episode), 2)
                self.assertEqual(tuple(e[0] for e in episode),
                                 ("encoder", "decoder"))
                self.assertTrue(all(0 <= e[1] < 4 and 0 <= e[2] < 4
                                    for e in episode))

    def test_distinct_bayesian_and_empirical_rl_training(self):
        for mode, alpha in (("bayesian", 1.0), ("empirical_rl", 2.0)):
            model = EmpiricalCausalControl(mode).fit(self.train)
            score = model.validation(self.validation)
            self.assertGreaterEqual(score, 0.0)
            self.assertTrue(math.isfinite(score))
            self.assertEqual(model.fit_examples, 1536)
            self.assertEqual(sum(sum(row) for kind in model.global_counts
                                 for row in kind), 1536)
            self.assertEqual(model.alpha, alpha)
            checkpoint = json.loads(canonical(model.checkpoint()))
            cold = EmpiricalCausalControl.from_checkpoint(checkpoint)
            self.assertEqual(checkpoint, cold.checkpoint())
            self.assertEqual(model.predict("encoder", 0),
                             cold.predict("encoder", 0))

    def test_paid_action_gate_and_memory_recall(self):
        model = EmpiricalCausalControl("bayesian").fit(self.train)
        world = synthetic_world(11000)
        before = world.observe()
        action = {"kind": "diagnostic", "mechanism": "encoder",
                  "channel": before["required_precursor"]}
        with self.assertRaisesRegex(
                AssertionError, "PHYSICALLY_PAID_PROBE"):
            validate_public_probe(before, action, before)
        after, cost, _ = world.step(action)
        observed = validate_public_probe(before, action, after)
        self.assertEqual(cost, -0.08)
        model.observe("encoder", before["required_precursor"], observed)
        prob = model.predict("encoder", before["required_precursor"])
        self.assertEqual(prob[observed], 1.0)
        self.assertFalse(model.should_probe(prob))
        model.begin_block()
        self.assertEqual(model._local, {})

    def test_trained_recurrent_BPTT_full_parameter_updates(self):
        model = RecurrentWorldModel()
        train_arrays = training_arrays(self.train)
        initial = model._loss(*train_arrays)
        model.fit(self.train, self.validation)
        self.assertEqual(model.training_report["trainable_parameters"], 964)
        self.assertEqual(model.training_report["fit_public_probes"], 1536)
        self.assertEqual(model.training_report["validation_public_probes"], 384)
        self.assertGreaterEqual(model.training_report["epochs_completed"], 20)
        self.assertLessEqual(model.training_report["epochs_completed"], 80)
        self.assertLess(model.training_report["final_train_cross_entropy"],
                        initial)
        self.assertTrue(math.isfinite(
            model.training_report["validation_best_cross_entropy"]))
        checkpoint = json.loads(canonical(model.checkpoint()))
        cold = RecurrentWorldModel.from_checkpoint(checkpoint)
        model.begin_block()
        cold.begin_block()
        self.assertEqual(model.predict("encoder", 0),
                         cold.predict("encoder", 0))

    def test_public_physical_evaluation_has_no_free_action(self):
        model = EmpiricalCausalControl("bayesian").fit(self.train)
        world = synthetic_world(11000)
        model.begin_block()
        receipt = run_policy(world, model)
        self.assertEqual(receipt["paid_steps"], len(receipt["trace"]))
        self.assertTrue(2 <= receipt["paid_steps"] <= 4)
        self.assertEqual(
            sum(r["action"]["kind"] == "actuator"
                for r in receipt["trace"]), 2)
        self.assertTrue(all(
            r["reward"] in (-0.08, -0.02, 0.98, -0.52)
            for r in receipt["trace"]))

    def test_public_model_code_contains_no_hidden_world_reads(self):
        for cls in (EmpiricalCausalControl, RecurrentWorldModel):
            source = inspect.getsource(cls)
            for term in ("._spec", "._rewire", "._latched", "fixture_spec(",
                         "valid_allocation(", "._decode(", "world.step(",
                         "synthetic_world("):
                self.assertNotIn(term, source)
        for cohort in ("transfer", "cold"):
            with self.assertRaisesRegex(AssertionError, "NO_HOLDOUT_LEARNING"):
                public_teacher_blocks(cohort)


if __name__ == "__main__":
    unittest.main()
