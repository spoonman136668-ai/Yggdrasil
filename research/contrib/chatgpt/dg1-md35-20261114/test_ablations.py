"""MD35 preregistered negative arms, hand-constructed physics only.

Checks physical charges and that across-episode memory ablation actually
removes intervention learning. No MD35 reserved seed or trained comparator
is accessed; the toy predictor is explicitly NOT a scientific result.
"""
import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "dg1-md34-20261114"))

from partial_routes import PartialRouteWorld
from ablations import ResetMemoryEachEpisode
from bayesian_control import BayesianControl
from public_policy import one_public_episode, four_episode_block, plan_terminal, route_value


def toy_world(context):
    return PartialRouteWorld({
        "context": context, "E": (0, 1, 2, 3),
        "G0": (1, 2, 3, 0), "G1": (2, 3, 0, 1),
        "D": (0, 1, 2, 3), "offset": 0,
    }, rewire=False)


class ToyPredictor:
    """Unfitted deterministic policy stub, never a learning baseline."""
    def __init__(self):
        self.received = []
        self.block_resets = 0

    def checkpoint(self):
        return {"schema": "toy-test-stub-not-trained"}

    def begin_block(self):
        self.received = []
        self.block_resets += 1

    def predict_target(self, context, route):
        return ((0.10, 0.10, 0.10, 0.70) if route == 0 else
                (0.01, 0.90, 0.04, 0.05))

    def update(self, episode):
        self.received.append(episode)


class MD35AblationTests(unittest.TestCase):
    def test_no_diagnostic_has_only_three_charged_steps(self):
        for context in range(4):
            control = ToyPredictor()
            control.begin_block()
            # Each independent toy world is a fresh episode.
            ep = one_public_episode(toy_world(context), control,
                                    expected_context=context,
                                    arm="no_diagnostic")
            self.assertEqual(len(ep.events), 3)
            self.assertIsNone(ep.diagnostic())
            self.assertEqual(ep.route(), 1)
            self.assertEqual(sum(e[1] == "terminal" for e in ep.events), 1)
            self.assertEqual(len(control.received), 1)

    def test_no_route_alternative_charges_its_probe(self):
        control = ToyPredictor()
        control.begin_block()
        ep = one_public_episode(toy_world(0), control,
                                expected_context=0,
                                arm="route0_only")
        self.assertEqual(ep.route(), 0)
        self.assertEqual(len(ep.events), 4)
        self.assertEqual(ep.diagnostic()[3], -0.09)
        self.assertEqual(ep.diagnostic()[0], 2)

    def test_rejects_unregistered_negative_policy_arm(self):
        control = ToyPredictor()
        control.begin_block()
        with self.assertRaisesRegex(AssertionError, "INVALID_ABLATION_MODE"):
            one_public_episode(toy_world(0), control,
                               expected_context=0, arm="free_oracle")
        with self.assertRaisesRegex(AssertionError, "INVALID_ABLATION_MODE"):
            one_public_episode(toy_world(0), control,
                               expected_context=0, arm=123)

    def test_reset_memory_prevents_public_feedback_without_forging_receipts(self):
        base = ToyPredictor()
        arm = ResetMemoryEachEpisode(base)
        blocks = [toy_world(i) for i in range(4)]
        episodes = four_episode_block(blocks, arm)
        self.assertEqual(len(episodes), 4)
        self.assertEqual([e.context for e in episodes], list(range(4)))
        self.assertEqual(base.received, [])  # no episode outcome was learned
        self.assertEqual(base.block_resets, 5)  # start + 4 erasures
        self.assertEqual(arm._position, 4)
        self.assertEqual(arm.checkpoint()["schema"],
                         "md35.episode-memory-reset-negative.v1")
        self.assertEqual(sum(ep.diagnostic() is not None for ep in episodes), 0)
        with self.assertRaisesRegex(AssertionError, "PUBLIC_EPISODE_ORDER"):
            arm.update(episodes[0])

    def test_normal_trained_arm_retains_prior_episode_receipts(self):
        base = ToyPredictor()
        episodes = four_episode_block([toy_world(i) for i in range(4)], base)
        self.assertEqual(len(base.received), 4)
        self.assertEqual(base.received, list(episodes))
        self.assertEqual(base.block_resets, 1)

    def test_predictive_distribution_and_route_reject_nan_and_infinity(self):
        for bad in (
            (float("nan"), 0.0, 0.0, 1.0),
            (float("inf"), 0.0, 0.0, 1.0),
            (float("-inf"), 0.0, 0.0, 1.0),
            (1.1, 0.0, 0.0, -0.1),
            (0.25, 0.25, 0.25, True),
        ):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(
                        AssertionError, "INVALID_PREDICTIVE_DISTRIBUTION"):
                    plan_terminal(bad)
        for invalid_route in (2, -1, False, "0"):
            with self.subTest(route=invalid_route):
                with self.assertRaisesRegex(
                        AssertionError, "INVALID_PHYSICAL_ROUTE"):
                    route_value((0.25, 0.25, 0.25, 0.25), invalid_route)

    def test_bayesian_cold_checkpoint_rejects_nonfinite_statistics(self):
        fake = {
            "schema": "md35.bayes-4096-public-latent.v1",
            "particle_seed": 35031, "particle_cap": 4096,
            "dirichlet_alpha": 1.0, "fitted_public_episodes": 1536,
            "training_target_mode": "charged_real",
            "success": [[[0.0] * 4 for _ in range(2)] for _ in range(4)],
            "failure": [[[0.0] * 4 for _ in range(2)] for _ in range(4)],
            "probe": [[[0.0] * 2 for _ in range(4)] for _ in range(3)],
        }
        # A structurally valid but untrained schema fixture may be restored
        # solely to exercise the data-integrity interface.
        self.assertEqual(BayesianControl.restore(copy.deepcopy(fake))
                         .checkpoint(), fake)
        for key in ("success", "failure", "probe"):
            for invalid in (float("inf"), float("-inf"), float("nan"), -1.0):
                bad = copy.deepcopy(fake)
                bad[key][0][0][0] = invalid
                with self.subTest(key=key, invalid=repr(invalid)):
                    with self.assertRaisesRegex(
                            AssertionError, "COLD_COUNTS_INVALID"):
                        BayesianControl.restore(bad)


if __name__ == "__main__":
    unittest.main()
