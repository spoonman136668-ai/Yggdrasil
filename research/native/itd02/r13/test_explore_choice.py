"""Focused source-only R13 tests: no original-world execution or first-use."""
import unittest

from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, MISSION
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r13.explore_choice import propose_native_action


def public():
    image = [[[1, 0, 0] for _ in range(7)] for _ in range(7)]
    image[3][5] = [5, 0, 0]
    return {"image": image, "direction": 1, "mission": MISSION}


class R13UncertaintyTests(unittest.TestCase):
    def test_native_zero_reward_proposal_selected_feedback_and_cold_restore(self):
        learner = PublicAffordanceCells()
        adapter = DoorKeyPublicAdapter()
        observation = public()
        adapter.reset_public(observation)
        learner.start_session(adapter, "source-only-public-test")

        first = propose_native_action(learner, observation)
        self.assertEqual(first["status"], "SELECT_NATIVE_LEAST_OBSERVED_ACTION")
        self.assertFalse(first["external_fallback"])
        self.assertIn(first["action"], range(7))
        self.assertEqual(learner.samples, 0)

        adapter.submit(first["action"])
        adapter.complete(observation, 0.0, False, False)
        learner.learn_selected(adapter)
        with self.assertRaises(ValueError):
            learner.learn_selected(adapter)
        self.assertEqual(learner.samples, 1)

        second = propose_native_action(learner, observation)
        self.assertEqual(second["status"], "SELECT_NATIVE_LEAST_OBSERVED_ACTION")
        self.assertNotEqual(first["action"], second["action"])

        blob = learner.checkpoint()
        cold = PublicAffordanceCells.restore(blob)
        self.assertEqual(blob, cold.checkpoint())
        self.assertEqual(second, propose_native_action(cold, observation))
        with self.assertRaises(ValueError):
            PublicAffordanceCells.restore(blob + b"0")

    def test_original_positive_reward_priority_and_hidden_input_rejection(self):
        learner = PublicAffordanceCells()
        adapter = DoorKeyPublicAdapter()
        observation = public()
        adapter.reset_public(observation)
        learner.start_session(adapter, "source-only-original-positive")
        adapter.submit(5)
        adapter.complete(observation, 1.0, False, False)
        learner.learn_selected(adapter)

        result = propose_native_action(learner, observation)
        self.assertEqual(result["status"], "SELECT_NATIVE_OBSERVED_POSITIVE_REWARD")
        self.assertEqual(result["action"], 5)
        self.assertEqual(result["learned_context_samples"], 1)

        with self.assertRaises(ValueError):
            propose_native_action(learner, dict(observation, private_agent_pos=[3, 3]))
        with self.assertRaises(ValueError):
            propose_native_action(learner, dict(observation, mission="oracle key coordinate"))
        self.assertEqual(learner.samples, 1)

    def test_context_support_spreads_over_seven_native_actions(self):
        learner = PublicAffordanceCells()
        adapter = DoorKeyPublicAdapter()
        observation = public()
        adapter.reset_public(observation)
        learner.start_session(adapter, "source-only-seven-native-actions")
        seen = set()
        for i in range(7):
            decision = propose_native_action(learner, observation)
            self.assertEqual(decision["status"], "SELECT_NATIVE_LEAST_OBSERVED_ACTION")
            self.assertNotIn(decision["action"], seen)
            seen.add(decision["action"])
            adapter.submit(decision["action"])
            adapter.complete(observation, 0.0, False, False)
            learner.learn_selected(adapter)
            self.assertEqual(learner.samples, i + 1)
        self.assertEqual(seen, set(range(7)))


if __name__ == "__main__":
    unittest.main()
