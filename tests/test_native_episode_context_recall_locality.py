"""Developer diagnostic of readout routing; no source world or model training.

Reproduction target: Yggdrasil PR #1278 SHA
86264b41a08d49f558418c0fba367f3a2636befa,
yggdrasil/native_episode_experience.py blob 5a18b00a4c4131526e71f51d63dfd9eb9471c81e.

The tests intentionally record a present limitation. Passing is NOT a repair.
"""
from fractions import Fraction
import unittest

from yggdrasil.native_episode_experience import NativeEpisodeExperience


class FixedPublicExpert:
    """A fake, frozen expert: correct for its public view only."""

    def __init__(self, supported_view):
        self.supported_view = supported_view

    def forecast(self, view, first, next_state=None, second=None):
        if type(view) is not tuple or len(view) != 2:
            raise ValueError("BAD_PUBLIC_VIEW")
        return Fraction(9, 10) if view == self.supported_view else Fraction(1, 10)


def pinned_two_expert_readout():
    memory = NativeEpisodeExperience()
    old_expert = FixedPublicExpert((0, 0))
    new_expert = FixedPublicExpert((1, 1))
    # Set ONLY the already-defined readout fields; no training, ledger writes,
    # pseudo-world actions, owner flags, or checkpoint fabrication.
    memory._context_start = 2
    memory._context_models = (
        (0, 1, "a" * 64, old_expert),
        (1, 2, "b" * 64, new_expert),
    )
    memory._context_weights = (Fraction(99, 100), Fraction(1, 100))
    return memory, old_expert, new_expert


class NativeContextRecallLocalityDiagnostic(unittest.TestCase):
    def test_global_first_stage_weights_ignore_requested_public_context(self):
        memory, _, _ = pinned_two_expert_readout()
        self.assertEqual(
            memory._context_weights_for((0, 0), 0, None),
            memory._context_weights_for((1, 1), 0, None),
        )
        self.assertEqual(
            memory._context_weights_for((0, 0), 0, None),
            (Fraction(99, 100), Fraction(1, 100)),
        )

    def test_historical_expert_intact_but_global_mixture_suppresses_it(self):
        memory, old_expert, new_expert = pinned_two_expert_readout()
        before = memory._context_weights
        self.assertEqual(old_expert.forecast((0, 0), 0), Fraction(9, 10))
        self.assertEqual(new_expert.forecast((1, 1), 0), Fraction(9, 10))
        self.assertEqual(memory.context_forecast((0, 0), 0), Fraction(223, 250))
        self.assertEqual(memory.context_forecast((1, 1), 0), Fraction(27, 250))
        self.assertLess(memory.context_forecast((1, 1), 0), Fraction(1, 2))
        self.assertEqual(memory._context_weights, before)
        # Hypothetical y=1 Brier values, NOT empirical native learner scores.
        mixture = memory.context_forecast((1, 1), 0)
        retained = new_expert.forecast((1, 1), 0)
        self.assertEqual((1 - mixture) ** 2, Fraction(198916, 250000))
        self.assertEqual((1 - retained) ** 2, Fraction(1, 100))

    def test_transition_observation_can_reweight_terminal_but_not_first_stage(self):
        memory, _, _ = pinned_two_expert_readout()
        prior = memory._context_weights
        terminal_conditioned = memory._context_weights_for((1, 1), 0, 1)
        self.assertGreater(terminal_conditioned[1], prior[1])
        self.assertEqual(memory._context_weights_for((1, 1), 0, None), prior)
        self.assertEqual(memory._context_weights, prior)


if __name__ == "__main__":
    unittest.main()
