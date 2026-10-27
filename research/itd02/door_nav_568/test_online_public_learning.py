"""Independent public transition updates measured against frozen map."""
import unittest
from online_public_learning import PublicOnlineTransitions, LearningPublicLoop
from native_public_loop import PublicWorld

class OnlinePublicLearningTests(unittest.TestCase):
    def test_updates_after_two_identical_owned_consequences(self):
        agent = LearningPublicLoop()
        key = (b"M1-intermediate", 2)
        baseline = dict(agent.model.active_links)
        self.assertEqual(agent.learned.links[key], b"X5-shift")
        first = agent.episode(PublicWorld("A", surprise=True))
        self.assertEqual(agent.learned.links[key], baseline[key])
        second = agent.episode(PublicWorld("B"), recheck=True)
        third = agent.episode(PublicWorld("A"))
        self.assertEqual([first["selected"], second["selected"], third["selected"]],
                         ["snapshot", "active", "snapshot"])
        self.assertEqual(agent.learned.links[key], b"R3-positive")
        self.assertEqual(agent.model.active_links, baseline)
        self.assertEqual(agent.model.archived_links[key], b"R3-positive")
        self.assertGreaterEqual(third["online_changes"], 1)
        self.assertEqual(third["online_examples"], sum(x["actions"] for x in
                         (first, second, third)))
        self.assertLessEqual(third["online_records"], 128)

    def test_conflict_retains_prediction_until_two_supports(self):
        model = PublicOnlineTransitions({(b"xA", 0): b"M"})
        model.observe((b"xA", 0), b"D")
        self.assertEqual(model.links[(b"xA", 0)], b"M")
        model.observe((b"xA", 0), b"M")
        model.observe((b"xA", 0), b"D")
        self.assertEqual(model.links[(b"xA", 0)], b"M")
        model.observe((b"xA", 0), b"D")
        self.assertEqual(model.links[(b"xA", 0)], b"D")
        self.assertEqual(model.examples(), 4)

    def test_capacity_rejects_extra_distinct_public_keys(self):
        model = PublicOnlineTransitions({}, capacity=1)
        model.observe((b"xA", 0), b"M")
        with self.assertRaises(ValueError):
            model.observe((b"xB", 0), b"D")
        self.assertEqual(model.examples(), 1)

    def test_no_model_mutation_when_insufficient_action_budget(self):
        agent = LearningPublicLoop()
        initial = dict(agent.model.active_links)
        result = agent.episode(PublicWorld("A", surprise=True), budget=4)
        self.assertIsNone(result["selected"])
        self.assertEqual(agent.model.active_links, initial)
        self.assertEqual(result["online_examples"], result["actions"])
