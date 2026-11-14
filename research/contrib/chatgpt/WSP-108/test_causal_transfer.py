"""WSP108 independent source-free *fixture only* DEV tests.

Fixture world seeds 51001 and 51002 are disjoint from the preregistered
FIT (11001..11012) and TRANSFER (21001..21012) first-evaluation cohorts.
No tests open masked transfer query labels, older protected datasets, or
the real knowledge graph.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from world import (
    FIT_SEEDS, TRANSFER_SEEDS, KINDS,
    hidden_law, support_evidence, support_scene, query_scene,
    path_features, oracle,
)
from learners import NumericRuleWeights, SymbolicRuleControl, ConventionalLogistic
from experiment import train_world, predict_all_arms

FIXTURE_SEEDS = (51001, 51002)


class TestCausalWorldAndLearners(unittest.TestCase):
    def test_fixture_cohort_disjoint_from_frozen_dev(self):
        self.assertTrue(set(FIXTURE_SEEDS).isdisjoint(FIT_SEEDS + TRANSFER_SEEDS))
        self.assertTrue(set(FIT_SEEDS).isdisjoint(TRANSFER_SEEDS))
        self.assertEqual(len(FIT_SEEDS), 12)
        self.assertEqual(len(TRANSFER_SEEDS), 12)
        self.assertEqual(len(hidden_law(FIXTURE_SEEDS[0])), 4)

    def test_identifiable_singleton_action_feedback_and_negative(self):
        for seed in FIXTURE_SEEDS:
            seen = []
            for i, (scene, before, after, observed) in enumerate(
                    support_evidence(seed)):
                self.assertEqual(sum(before), 0)
                self.assertEqual(scene.add, True)
                self.assertIs(observed, oracle(seed, scene.after(),
                                               scene.source, scene.target))
                if i < 9:
                    self.assertEqual(sum(after), 1)
                    self.assertEqual(after.index(1), i)
                else:
                    self.assertEqual(sum(after), 0)
                    self.assertFalse(observed)
                seen.append(scene.source)
            self.assertEqual(len(seen), len(set(seen)))

    def test_numeric_programming_and_symbolic_agree_on_fixture_actions(self):
        for seed in FIXTURE_SEEDS:
            context = f"world-{seed}"
            numeric, symbolic = NumericRuleWeights(), SymbolicRuleControl()
            for i, (_, _before, after, observed) in enumerate(support_evidence(seed)):
                numeric.program(context, after, observed)
                if i < 9:
                    symbolic.observe(context, KINDS[i], observed)
            self.assertTrue(numeric.complete(context))
            self.assertTrue(symbolic.complete(context))
            self.assertEqual(sorted(float(x) for x in numeric.weights[context].flat),
                             [0.] * 5 + [1.] * 4)
            for i in range(64):
                scene = query_scene(seed, i)
                for edges in (scene.before, scene.after()):
                    features = path_features(edges, scene.source, scene.target)
                    target = oracle(seed, edges, scene.source, scene.target)
                    self.assertEqual(numeric.predict(context, features), target)
                    self.assertEqual(symbolic.predict_edges(
                        context, edges, scene.source, scene.target), target)

    def test_fully_fit_convex_conventional_and_strong_maxpool(self):
        for seed in FIXTURE_SEEDS:
            context = f"world-{seed}"
            observations = tuple((after, label) for _, _, after, label in
                                 support_evidence(seed))
            model = ConventionalLogistic()
            model.fit(context, observations)
            self.assertEqual(model.diagnostics[context]["support_accuracy"], 1.0)
            self.assertLessEqual(
                model.diagnostics[context]["gradient_inf_norm"], 1e-9)
            for scene_index in range(64):
                scene = query_scene(seed, scene_index)
                for edges in (scene.before, scene.after()):
                    features = path_features(edges, scene.source, scene.target)
                    self.assertEqual(model.predict(context, features, max_pool=True),
                                     oracle(seed, edges, scene.source, scene.target))
            self.assertTrue(np.array_equal(
                model.coefficients[context],
                model.cold_copy().coefficients[context]))

    def test_interference_cold_restore_and_tamper_negative(self):
        memory = NumericRuleWeights()
        for seed in FIXTURE_SEEDS:
            context = f"world-{seed}"
            for _, _, f, observed in support_evidence(seed):
                memory.program(context, f, observed)
        snapshot = memory.snapshot()
        restored = NumericRuleWeights.restore(snapshot)
        for seed in FIXTURE_SEEDS:
            scene = query_scene(seed, 11)
            f = path_features(scene.after(), scene.source, scene.target)
            self.assertEqual(memory.predict(f"world-{seed}", f),
                             restored.predict(f"world-{seed}", f))
        edited = json.loads(snapshot)
        edited["payload"][f"world-{FIXTURE_SEEDS[0]}"]["weights"][0][0] = 3.
        with self.assertRaises(ValueError):
            NumericRuleWeights.restore(json.dumps(edited))
        with self.assertRaises(ValueError):
            NumericRuleWeights.restore(json.dumps({"schema":"other"}))

    def test_contradictory_outcome_and_nonidentifiable_support_rejected(self):
        model = NumericRuleWeights()
        f = (1, 0, 0, 0, 0, 0, 0, 0, 0)
        model.program("world-fixture", f, True)
        with self.assertRaises(ValueError):
            model.program("world-fixture", f, False)
        with self.assertRaises(ValueError):
            model.program("world-fixture", (1,) * 9, True)
        with self.assertRaises(ValueError):
            model.program("world-fixture", (0,) * 9, True)
        with self.assertRaises(ValueError):
            model.predict("world-fixture", f)

    def test_observed_graph_intervention_with_novel_entities(self):
        names = set()
        for seed in FIXTURE_SEEDS:
            adds, removes = 0, 0
            for i in range(64):
                scene = query_scene(seed, i)
                before = path_features(scene.before, scene.source, scene.target)
                after = path_features(scene.after(), scene.source, scene.target)
                self.assertEqual(len(before), 9)
                self.assertEqual(len(after), 9)
                self.assertNotEqual(before, after)
                self.assertEqual(scene.action in scene.before, not scene.add)
                self.assertEqual(scene.action in scene.after(), scene.add)
                self.assertNotIn(scene.source, names)
                self.assertNotIn(scene.target, names)
                names.update((scene.source, scene.target))
                adds += int(scene.add)
                removes += int(not scene.add)
            self.assertGreater(adds, 5)
            self.assertGreater(removes, 5)

    def test_negative_no_feedback_and_rotated_feedback_not_oracle(self):
        seed = FIXTURE_SEEDS[0]
        context = f"world-{seed}"
        model = NumericRuleWeights()
        labels = [observed for _, _, _, observed in support_evidence(seed)[:9]]
        for i, (_, _, f, _) in enumerate(support_evidence(seed)[:9]):
            model.program(context, f, labels[(i+1)%9])
        mismatch = 0
        for i in range(64):
            scene = query_scene(seed, i)
            f = path_features(scene.after(), scene.source, scene.target)
            mismatch += int(model.predict(context, f) != oracle(
                seed, scene.after(), scene.source, scene.target))
        self.assertGreater(mismatch, 0)

    def test_harness_uses_identical_observations_for_each_arm(self):
        seed = FIXTURE_SEEDS[1]
        numeric = NumericRuleWeights()
        symbolic = SymbolicRuleControl()
        conventional = ConventionalLogistic()
        rotated = NumericRuleWeights()
        training = train_world(seed, numeric, symbolic, conventional, rotated)
        self.assertEqual(training["observed_support_actions"], 10)
        self.assertEqual(training["observed_singleton_actions"], 9)
        self.assertLessEqual(training["conventional_gradient_inf_norm"], 1e-9)
        scene = query_scene(seed, 3)
        a = predict_all_arms(seed, scene, numeric, symbolic, conventional, rotated)
        b = predict_all_arms(seed, scene, numeric, symbolic,
                             conventional.cold_copy(), rotated)
        self.assertEqual(a, b)
        self.assertEqual(a["before"]["numeric_direct"],
                         a["before"]["symbolic_exact"])
        self.assertEqual(a["after"]["numeric_direct"],
                         a["after"]["symbolic_exact"])


if __name__ == "__main__":
    unittest.main()
