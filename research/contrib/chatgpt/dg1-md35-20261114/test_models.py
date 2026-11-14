"""MD35 mechanical controls and negative tests; no reserved seed is opened.

Only hand-constructed MD34 physics fixtures and already-public physical
receipts enter tests. No MD35 train/validation/transfer/cold cohorts, neural
fit, candidate model selection or scientific score is executed here.
"""
import copy
import inspect
import json
import random
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "dg1-md34-20261114"))

from partial_routes import PartialRouteWorld
from public_actions import (EXPLORATION_SEED, PublicEpisode, admit_receipt,
                            explore_episode, require_public_blocks)
from public_policy import choose_route, plan_terminal, route_value, one_public_episode
from bayesian_control import BayesianControl, PARTICLES
from model_based_rl import ModelBasedRL, SWEEPS, ENSEMBLE
from gated_recurrent import (GatedRecurrentControl, HIDDEN, SEEDS,
                             PARAMETER_SHAPES, query_vector,
                             observed_vector, training_arrays)


def toy_world(context):
    # Explicitly handwritten nonreserved fixture: not MD34 fixture_spec(),
    # never a seed, transfer law, or protected test source.
    return PartialRouteWorld({
        "context": context,
        "E": (0, 1, 2, 3),
        "G0": (1, 2, 3, 0),
        "G1": (2, 3, 0, 1),
        "D": (0, 1, 2, 3),
        "offset": 0,
    }, rewire=False)


def toy_block():
    rng = random.Random(EXPLORATION_SEED)
    return tuple(explore_episode(toy_world(i), i, rng) for i in range(4))


class MD35PublicControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.block = toy_block()

    def test_explorer_rotates_paid_bit_and_exact_four_actions(self):
        self.assertEqual(EXPLORATION_SEED, 35049)
        self.assertEqual(toy_block(), self.block)
        self.assertEqual(len(self.block), 4)
        self.assertEqual([ep.diagnostic()[0] for ep in self.block],
                         [0, 1, 1, 2])
        self.assertEqual([ep.diagnostic()[2] for ep in self.block[:3]],
                         [0, 0, 1])
        for i, ep in enumerate(self.block):
            self.assertEqual(ep.context, i)
            self.assertEqual(len(ep.events), 4)
            self.assertEqual(sum(e[1] == "diagnostic" for e in ep.events), 1)
            self.assertEqual(sum(e[3] == -0.09 for e in ep.events), 1)
            self.assertIn(ep.terminal()[3], (-0.52, 0.98))
            self.assertAlmostEqual(sum(e[3] for e in ep.events),
                                   ep.net_utility, places=9)

    def test_public_receipt_integrity_rejects_forged_paid_actions(self):
        world = toy_world(0)
        rng = random.Random(EXPLORATION_SEED)
        ep = explore_episode(world, 0, rng)
        self.assertIsInstance(ep, PublicEpisode)
        raw = world.receipt()
        bad = copy.deepcopy(raw)
        bad["trace"][0]["reward"] = 0.0
        with self.assertRaisesRegex(AssertionError, "TRACE_INTEGRITY"):
            admit_receipt(0, bad)
        bad = copy.deepcopy(raw)
        bad["hidden_law"] = [0, 1, 2, 3]
        with self.assertRaisesRegex(AssertionError, "PRIVATE_OR_FORGED"):
            admit_receipt(0, bad)
        bad = copy.deepcopy(raw)
        bad["charged_diagnostics"] = 0
        with self.assertRaisesRegex(AssertionError, "CHARGE_OR_TERMINAL"):
            admit_receipt(0, bad)
        bad = copy.deepcopy(raw)
        bad["paid_steps"] = 3
        with self.assertRaisesRegex(AssertionError, "TRACE_INTEGRITY"):
            admit_receipt(0, bad)
        bad = copy.deepcopy(raw)
        bad["net_utility"] = 9.9
        with self.assertRaisesRegex(AssertionError, "CHARGE_OR_TERMINAL"):
            admit_receipt(0, bad)

    def test_rejects_nonpublic_episode_metadata_and_bad_block(self):
        for invalid in (None, {"context": 0, "family": "relay"}, 1, "0"):
            with self.assertRaisesRegex(AssertionError, "PRIVATE_METADATA"):
                require_public_blocks(((invalid,) + self.block[1:],))
        with self.assertRaisesRegex(AssertionError, "FOUR_EPISODE"):
            require_public_blocks((self.block[:3],))
        with self.assertRaisesRegex(AssertionError, "UNQUALIFIED_TRAIN"):
            require_public_blocks((self.block,), expected_count=384)

    def test_bayesian_latent_update_and_exact_checkpoint_gate(self):
        m1, m2 = BayesianControl(), BayesianControl()
        self.assertEqual(PARTICLES, 4096)
        for m in (m1, m2):
            with self.assertRaisesRegex(AssertionError, "NOT_TRAINED"):
                m.checkpoint()
            m.begin_block()
        self.assertEqual(m1.predict_target(0, 0), m2.predict_target(0, 0))
        initial = m1.predict_target(0, 0)
        for ep in self.block:
            m1.update(ep)
            m2.update(ep)
        self.assertEqual(m1.predict_target(0, 0), m2.predict_target(0, 0))
        self.assertAlmostEqual(sum(initial), 1.0)
        self.assertAlmostEqual(sum(m1.predict_target(0, 1)), 1.0)
        self.assertEqual(m1._block_episodes, 4)
        with self.assertRaisesRegex(AssertionError, "CONTEXT_OR_BLOCK"):
            m1.update(self.block[0])
        with self.assertRaisesRegex(AssertionError, "COLD_CHECKPOINT"):
            BayesianControl.restore({"schema": "foo"})

    def test_modelbased_rl_consumes_public_replay_not_private_physics(self):
        m = ModelBasedRL()
        self.assertEqual((ENSEMBLE, SWEEPS), (5, 40))
        with self.assertRaisesRegex(AssertionError, "UNTRAINED"):
            m.checkpoint()
        with self.assertRaisesRegex(AssertionError, "BELLMAN_NOT_FITTED"):
            m.plan_route(0)
        m.begin_block()
        for ep in self.block:
            m.update(ep)
        self.assertEqual(m._block_episodes, 4)
        self.assertEqual(m._local_success.sum() + m._local_failure.sum(), 4)
        self.assertEqual(m._local_probe.sum(), 4)
        self.assertAlmostEqual(sum(m.predict_target(0, 0)), 1.0)
        with self.assertRaisesRegex(AssertionError, "PUBLIC_BLOCK"):
            m.update(self.block[0])
        with self.assertRaisesRegex(AssertionError, "COLD_CHECKPOINT"):
            ModelBasedRL.restore({"schema": "wrong"})

    def test_gated64_public_inputs_and_deterministic_forward(self):
        self.assertEqual(HIDDEN, 64)
        self.assertEqual(SEEDS, (35035, 35036, 35037))
        self.assertEqual(sum(np.prod(s) for s in PARAMETER_SHAPES.values()), 17646)
        a, b = GatedRecurrentControl(), GatedRecurrentControl()
        self.assertEqual(a.seed, SEEDS[0])
        for k in PARAMETER_SHAPES:
            self.assertTrue(np.array_equal(a.w[k], b.w[k]))
        payload = training_arrays((self.block, self.block), 2)
        self.assertEqual([x.shape for x in payload],
                         [(2, 16, 22), (2, 16, 26),
                          (2, 16, 2), (2, 16, 2)])
        self.assertEqual(float(payload[3].sum()), 16.0)
        p, cache = a._forward(payload)
        self.assertEqual(p.shape, (2, 16, 2))
        self.assertEqual(len(cache), 16)
        self.assertTrue(np.isfinite(a._loss(payload)))
        a.begin_block()
        self.assertAlmostEqual(sum(a.predict_target(0, 0)), 1.0)
        for ep in self.block:
            a.update(ep)
        self.assertEqual(a._block_episodes, 4)
        with self.assertRaisesRegex(AssertionError, "UNTRAINED_CHECKPOINT"):
            a.checkpoint()
        with self.assertRaisesRegex(AssertionError, "INVALID_COLD_CHECKPOINT"):
            GatedRecurrentControl.restore({})

    def test_bptt_gradient_step_finite_without_real_training(self):
        # One mechanical optimizer step on two handwritten four-episode
        # fixture replays; never fits the frozen source cohort.
        a = GatedRecurrentControl()
        payload = training_arrays((self.block, self.block), 2)
        before = {k: v.copy() for k, v in a.w.items()}
        moment = {k: [np.zeros_like(v), np.zeros_like(v)]
                  for k, v in a.w.items()}
        a._fit_batch(payload, moment, 1)
        self.assertTrue(all(np.isfinite(v).all() for v in a.w.values()))
        self.assertTrue(any(not np.array_equal(before[k], a.w[k])
                            for k in PARAMETER_SHAPES))
        self.assertTrue(np.isfinite(a._loss(payload)))

    def test_terminal_probe_must_improve_physical_net_utility(self):
        self.assertEqual(plan_terminal((0.25, 0.25, 0.25, 0.25)),
                         (True, 0))
        self.assertEqual(plan_terminal((1.0, 0.0, 0.0, 0.0)),
                         (False, 0))
        self.assertEqual(plan_terminal((0.25, 0.25, 0.25, 0.25), 1),
                         (False, 1))
        with self.assertRaisesRegex(AssertionError, "FAKE_PAID"):
            plan_terminal((0.25, 0.25, 0.25, 0.25), 2)
        self.assertGreater(
            route_value((1, 0, 0, 0), 0),
            route_value((1, 0, 0, 0), 1))

    def test_each_untrained_model_uses_only_real_toy_world_actions(self):
        # Engineering-only toy physics. This is not a model comparison or
        # scientific qualification; no protected cohort and no training.
        for cls in (BayesianControl, ModelBasedRL, GatedRecurrentControl):
            with self.subTest(model=cls.__name__):
                model = cls()
                model.begin_block()
                world = toy_world(0)
                # The fitted-Q arm must fail closed if Bellman backups
                # are not trained. The untrained toy mechanics can only be
                # checked through its separate no-diagnostic route policy.
                if cls is ModelBasedRL:
                    with self.assertRaisesRegex(
                            AssertionError, "BELLMAN_NOT_FITTED"):
                        one_public_episode(world, model, expected_context=0)
                    episode = one_public_episode(
                        world, model, expected_context=0,
                        arm="no_diagnostic")
                else:
                    episode = one_public_episode(
                        world, model, expected_context=0)
                receipt = world.receipt()
                self.assertEqual(episode.trace_sha256,
                                 receipt["public_trace_sha256"])
                self.assertEqual(episode.net_utility,
                                 receipt["net_utility"])
                self.assertEqual(len(episode.events),
                                 receipt["paid_steps"])
                self.assertEqual(
                    receipt["charged_diagnostics"],
                    int(episode.diagnostic() is not None))
                self.assertEqual(model._block_episodes, 1)
                self.assertEqual(
                    [e[1] for e in episode.events if e[1] != "diagnostic"],
                    ["actuator", "route", "terminal"])

    def test_no_model_can_read_world_seed_fixture_or_private_law(self):
        for cls in (BayesianControl, ModelBasedRL, GatedRecurrentControl):
            source = inspect.getsource(cls)
            for forbidden in ("fixture_spec(", "private_allocation(",
                              "._spec", "._rewire", "._hidden_",
                              "LAWS[", "world.step(", "synthetic_world("):
                self.assertNotIn(forbidden, source)
        with self.assertRaisesRegex(AssertionError, "UNQUALIFIED_TRAIN"):
            BayesianControl().fit((self.block,))
        with self.assertRaisesRegex(AssertionError, "UNQUALIFIED_TRAIN"):
            ModelBasedRL().fit((self.block,))
        with self.assertRaisesRegex(AssertionError, "UNQUALIFIED_TRAIN"):
            GatedRecurrentControl.train((self.block,), (self.block,))


if __name__ == "__main__":
    unittest.main()
