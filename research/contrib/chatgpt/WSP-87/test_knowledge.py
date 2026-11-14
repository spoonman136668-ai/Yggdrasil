"""Focused structural fixtures do not instantiate reserved WSP87 DEV worlds."""
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from weights import NumericKnowledge
from independent_graph import SymbolicGraph
from experiment import FIXTURE_SEEDS, DEV_SEEDS, classify, single_world
from world import make_world, oracle


class NumericKnowledgeTests(unittest.TestCase):
    def test_two_hop_only_through_observed_weights(self):
        model = NumericKnowledge()
        model.observe("unknown-relation", "α", "β")
        model.observe("unknown-relation", "β", "γ")
        self.assertTrue(model.predict("unknown-relation", "α", "γ", 2))
        self.assertFalse(model.predict("unknown-relation", "α", "γ", 1))
        self.assertFalse(model.predict("unknown-relation", "γ", "α", 2))
        self.assertIsNone(model.predict("unknown-relation", "δ", "γ", 2))
        self.assertEqual(len(model.entities), 3)
        self.assertEqual(len(model.weights["unknown-relation"]), 3)

    def test_no_retraction_of_ungrounded_names(self):
        model = NumericKnowledge()
        with self.assertRaises(ValueError):
            model.observe("r", "a", "b", False)
        model.observe("r", "a", "b")
        model.observe("r", "a", "b", False)
        self.assertFalse(model.predict("r", "a", "b", 1))
        with self.assertRaises(ValueError):
            model.observe("r", "a", "b", "false")

    def test_delta_update_preserves_independent_facts(self):
        model = NumericKnowledge()
        model.observe("r", "A", "B")
        model.observe("r", "B", "C")
        model.observe("q", "A", "B")
        previous = model.snapshot()
        self.assertTrue(model.predict("r", "A", "C", 2))
        model.observe("r", "B", "C", False)
        model.observe("r", "B", "D")
        self.assertFalse(model.predict("r", "A", "C", 2))
        self.assertTrue(model.predict("r", "A", "D", 2))
        self.assertTrue(model.predict("q", "A", "B", 1))
        self.assertTrue(NumericKnowledge.restore(previous).predict("r", "A", "C", 2))

    def test_cold_restore_and_corrupted_weight_rejection(self):
        model = NumericKnowledge()
        model.observe("r", "a", "b")
        model.observe("r", "b", "c")
        original = model.snapshot()
        self.assertEqual(NumericKnowledge.restore(original).snapshot(), original)
        bad = json.loads(original)
        bad["payload"]["weights"]["r"][0][1] = 0.0
        with self.assertRaises(ValueError):
            NumericKnowledge.restore(json.dumps(bad))

    def test_known_unknown_and_input_validation(self):
        model = NumericKnowledge()
        with self.assertRaises(ValueError):
            model.observe("", "a", "b")
        model.observe("r", "a", "b")
        with self.assertRaises(ValueError):
            model.predict("r", "a", "b", 3)
        self.assertIsNone(model.predict("unknown", "a", "b", 1))
        self.assertIsNone(model.predict("r", "a", "unseen", 2))

    def test_independent_symbolic_agrees_on_update(self):
        numeric, symbolic = NumericKnowledge(), SymbolicGraph()
        edits = [("r", "A", "B", True),
                 ("r", "B", "C", True),
                 ("r", "A", "B", False),
                 ("r", "A", "D", True)]
        for row in edits:
            numeric.observe(*row)
            symbolic.observe(*row)
        for a in ("A", "B", "C", "D"):
            for b in ("A", "B", "C", "D"):
                for hops in (1, 2):
                    self.assertEqual(numeric.predict("r", a, b, hops),
                                     symbolic.predict("r", a, b, hops))

    def test_public_world_generation_and_edges(self):
        world = make_world(FIXTURE_SEEDS[0])
        self.assertEqual(len(world.stage_a), 22)
        self.assertEqual(len(world.stage_b), 23)
        self.assertEqual(len(world.entities_b), 16)
        self.assertEqual(len(world.relations_b), 3)
        self.assertEqual(len(world.truth_a), 22)
        for observation in world.stage_a:
            self.assertTrue(oracle(world.truth_a, observation.relation,
                                   observation.source, observation.target, 1))
        for observation in world.stage_b:
            self.assertEqual(oracle(world.truth_b, observation.relation,
                                    observation.source, observation.target, 1),
                             observation.present)

    def test_unregistered_fixtures_do_not_use_dev_seeds(self):
        self.assertTrue(set(FIXTURE_SEEDS).isdisjoint(DEV_SEEDS))
        results = [single_world(seed) for seed in FIXTURE_SEEDS]
        status = classify(results, dev=False)
        self.assertEqual(status["classification"], "DEV_SUBSTRATE_FEASIBLE")
        self.assertTrue(all(status["checks"].values()))
        self.assertTrue(all(r["symbolic_parity"] for r in results))
        self.assertEqual(status["stageA_correct"], status["stageA_total"])
        self.assertEqual(status["stageB_correct"], status["stageB_total"])
        self.assertGreaterEqual(status["novel_true_two_hop_correct"], 20)
        self.assertFalse(status["language_or_general_intelligence_proven"])

    def test_numeric_inference_has_no_source_or_model_imports(self):
        code = (HERE / "weights.py").read_text("utf-8")
        graph = (HERE / "independent_graph.py").read_text("utf-8")
        self.assertNotIn("from world import", code)
        self.assertNotIn("from weights import", graph)
        self.assertNotIn("tokenizer", code)
        self.assertNotIn("torch", code)


if __name__ == "__main__":
    unittest.main()
