"""Public-only FKP-17 first-order temporal expressivity and negatives."""
import unittest
from collections import namedtuple

from temporal_probe import TemporalRewardProbe, ACTIONS, MAX_STEPS

Step = namedtuple("Step", ("before", "action", "after", "reward", "done", "history"))
Prior = namedtuple("Prior", ("before", "action", "reward", "after", "done"))
STATE = (8,) * 8


def history(prior_action):
    return (Prior(STATE, prior_action, 0.0, STATE, False),)


def event(prior_action, action, reward):
    return Step(STATE, action, STATE, reward, False, history(prior_action))


class TemporalResearchProbeTests(unittest.TestCase):
    def trained(self):
        probe = TemporalRewardProbe()
        # Matched 8 public outcomes: both actions have aggregate mean zero.
        for _ in range(2):
            for prior_action in (0, 1):
                for action in (0, 1):
                    probe.observe_public(event(prior_action, action,
                                              1.0 if prior_action == action else -1.0))
        return probe

    def test_first_order_context_changes_decision(self):
        model = self.trained()
        saved = model.state_receipt()
        self.assertEqual(model.choose_public(STATE, history(0)), 0)
        self.assertEqual(model.choose_public(STATE, history(1)), 1)
        self.assertEqual(saved, model.state_receipt())
        self.assertEqual(model.LEARNED_BYTES, 768)

    def test_missing_evidence_abstains(self):
        model = TemporalRewardProbe()
        self.assertIsNone(model.choose_public(STATE, history(0)))
        model.observe_public(event(0, 0, 1.0))
        self.assertIsNone(model.choose_public(STATE, history(0)))
        self.assertIsNone(model.choose_public(STATE, ()))

    def test_cannot_learn_two_step_history(self):
        model = self.trained()
        a = (Prior(STATE, 0, 0.0, STATE, False),) + history(1)
        b = (Prior(STATE, 1, 0.0, STATE, False),) + history(1)
        self.assertEqual(model.choose_public(STATE, a), model.choose_public(STATE, b))
        self.assertEqual(model.choose_public(STATE, a), 1)

    def test_strict_public_fields_no_mutation(self):
        model = self.trained()
        before = model.state_receipt()
        Extended = namedtuple("Extended", Step._fields + ("oracle",))
        bad = Extended(STATE, 0, STATE, 1., False, history(0), [1.] * ACTIONS)
        with self.assertRaises(ValueError):
            model.observe_public(bad)
        with self.assertRaises(ValueError):
            model.observe_public(event(0, True, 1.0))
        with self.assertRaises(ValueError):
            model.observe_public(Step(STATE, 0, STATE, 1.0, False,
                                            (Prior(STATE, 1, 0., (0,) * 8, False),)))
        self.assertEqual(before, model.state_receipt())

    def test_budget_atomicity_and_reset(self):
        model = self.trained()
        row = event(0, 0, 1.0)
        for _ in range(MAX_STEPS - 8):
            model.observe_public(row)
        digest = model.state_receipt()
        with self.assertRaises(ValueError):
            model.observe_public(row)
        self.assertEqual(digest, model.state_receipt())
        model.begin_world()
        self.assertIsNone(model.choose_public(STATE, history(0)))

    def test_conventional_first_order_count_control_ties(self):
        model = self.trained()
        # A standard Markov conditional-count control with exactly the same
        # public records makes the same decisions. This is NOT novel advantage.
        rewards = {(p, a): [1.0 if p == a else -1.0] * 2
                   for p in (0, 1) for a in (0, 1)}
        for p in (0, 1):
            control = max((sum(v) / len(v), -a) for (q, a), v in rewards.items()
                          if p == q)[1] * -1
            self.assertEqual(model.choose_public(STATE, history(p)), control)


if __name__ == "__main__":
    unittest.main()
