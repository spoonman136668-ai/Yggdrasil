"""Paired interventions and shuffled-credit negative controls."""
import unittest
from paired_interventions import compare, paired_interventions
from eligibility_local_cells import EligibilityLocalCells

class PairedInterventionTests(unittest.TestCase):
    def test_causal_intervention_selects_effective_action(self):
        result = compare()
        self.assertEqual(result["trials_per_arm"], 8)
        self.assertEqual((result["arm0_successes"], result["arm1_successes"]), (8, 0))
        self.assertEqual(result["intervention_effect"], 1)
        self.assertEqual(result["selected_action"], 0)

    def test_reward_shuffling_reverses_credit(self):
        learner = EligibilityLocalCells()
        for _, action, reward in paired_interventions():
            # Falsification: swap reward assignments while preserving public
            # frames and actions. A reward association learner must reverse.
            reversed_reward = 1 - reward
            learner.observe(b"start", [0, 1])
            learner.learn(action, b"middle", 0, False)
            learner.observe(b"middle", [2])
            learner.learn(2, b"goal" if reversed_reward else b"dead_end", reversed_reward, True)
        learner.observe(b"start", [0, 1])
        self.assertEqual(learner.choose(), 1)

if __name__ == "__main__":
    unittest.main()
