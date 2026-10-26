"""Source-free public-interface engineering checks, NOT Shuttle trials."""
import copy
import hashlib
import json
import subprocess
import sys
import unittest

from yggdrasil.itd02_local_ring_memory_dev import (
    ACTIONS, ACTION_SITES, CELLS, NativeRingMemoryDev, OBSERVATIONS,
    OBS_SITES, ROUNDS, _local_exchange, _public_pulse,
)


def walk_two_observations(model, history, *, reward=None, action=None, training=True):
    model.reset_episode()
    model.advance(history)
    model.feedback("TurnAround", 0., learning=training)
    model.advance("Nothing")
    choice = model.choose()
    if reward is not None:
        model.feedback(action, reward, learning=training, terminal=True)
    else:
        model.feedback(choice, 0., learning=False, terminal=True)
    return choice


class LocalRingDevTests(unittest.TestCase):
    def test_source_only_contract_shape_and_neighbor_hops(self):
        self.assertEqual(CELLS, 8)
        self.assertEqual(ROUNDS, 2)
        self.assertEqual(sorted(OBS_SITES + ACTION_SITES), list(range(CELLS)))
        self.assertEqual(len(OBSERVATIONS), 5)
        self.assertEqual(len(ACTIONS), 3)
        signal = [0.] * CELLS
        signal[0] = 1.
        for radius in range(ROUNDS + 1):
            propagated = _local_exchange(signal, radius)
            for site in range(CELLS):
                ring_distance = min(site, CELLS - site)
                self.assertEqual(propagated[site] > 0, ring_distance <= radius)
            self.assertAlmostEqual(sum(propagated), 1.)
        with self.assertRaises(ValueError):
            _local_exchange(signal, rounds=ROUNDS + 1)

    def test_frozen_action_can_depend_on_observed_history(self):
        model = NativeRingMemoryDev()
        # Synthetic public-only rewards. This is deliberately NOT a world:
        # no source dynamics, state, probabilities, episodes or oracle policy.
        history_rewards = (("LRV", "GoForward", 1.),
                           ("LRV", "Backup", -1.),
                           ("docked_LRV", "GoForward", -1.),
                           ("docked_LRV", "Backup", 1.))
        initial_sha = model.parameter_sha256()
        for _ in range(220):
            for observation, action, reward in history_rewards:
                walk_two_observations(model, observation, reward=reward, action=action)
        self.assertNotEqual(initial_sha, model.parameter_sha256())
        self.assertTrue(any(abs(g - 1.) > 1e-7 for g in model.gates),
                        "history retention must receive learned reward credit")
        self.assertEqual(model.updates, 1760)
        digest = model.parameter_sha256()
        payload = model.checkpoint()
        self.assertLess(len(payload), 8192)
        model.start_frozen_evaluation(digest)
        self.assertEqual(walk_two_observations(model, "LRV", training=False), "GoForward")
        self.assertEqual(walk_two_observations(model, "docked_LRV", training=False), "Backup")
        self.assertEqual(model.parameter_sha256(), digest)
        restored = NativeRingMemoryDev.restore(payload)
        restored.start_frozen_evaluation(digest)
        self.assertEqual(walk_two_observations(restored, "LRV", training=False), "GoForward")
        self.assertEqual(walk_two_observations(restored, "docked_LRV", training=False), "Backup")
        self.assertEqual(restored.parameter_sha256(), digest)

    def test_history_ablation_and_opposite_reward_credit(self):
        def fit(go_forward_for):
            model = NativeRingMemoryDev()
            for _ in range(220):
                for history in ("LRV", "docked_LRV"):
                    for action in ("GoForward", "Backup"):
                        good = "GoForward" if history == go_forward_for else "Backup"
                        reward = 1. if action == good else -1.
                        walk_two_observations(model, history,
                                              action=action, reward=reward)
            model.start_frozen_evaluation(model.parameter_sha256())
            return model

        a = fit("LRV")
        b = fit("docked_LRV")
        self.assertEqual(walk_two_observations(a, "LRV", training=False), "GoForward")
        self.assertEqual(walk_two_observations(a, "docked_LRV", training=False), "Backup")
        self.assertEqual(walk_two_observations(b, "LRV", training=False), "Backup")
        self.assertEqual(walk_two_observations(b, "docked_LRV", training=False), "GoForward")
        # Remove historical observation: both runs now have exactly the same
        # public input and initial memory, so the two answers must coincide.
        a.reset_episode()
        a.advance("Nothing")
        sole = a.choose()
        a.feedback(sole, 0., learning=False, terminal=True)
        a.reset_episode()
        a.advance("Nothing")
        self.assertEqual(a.choose(), sole)
        a.feedback(sole, 0., learning=False, terminal=True)
        self.assertIn(sole, ACTIONS)

    def test_reset_clears_history_not_learned_parameters(self):
        m = NativeRingMemoryDev()
        m.advance("LRV")
        m.feedback("TurnAround", 0.)
        self.assertTrue(any(m.memory))
        pre = m.parameter_sha256()
        m.reset_episode()
        self.assertEqual(m.memory, [0.] * CELLS)
        self.assertEqual(m.parameter_sha256(), pre)

    def test_no_private_hidden_fields_or_accidental_fitting(self):
        m = NativeRingMemoryDev()
        for bad in ("hidden_state", "u_wind", "", None, ["LRV"], {"obs": "LRV"}):
            with self.assertRaises(ValueError):
                m.advance(bad)
        self.assertEqual(m.updates, 0)
        m.advance("LRV")
        with self.assertRaises(ValueError):
            m.advance("MRV")
        for action, reward in (("Jump", 0.), ("Backup", float("nan")), ("Backup", True)):
            with self.assertRaises(ValueError):
                m.feedback(action, reward)
        self.assertTrue(m.pending)
        m.feedback("Backup", 1.)
        m.start_frozen_evaluation(m.parameter_sha256())
        m.advance("MRV")
        frozen = m.parameter_sha256()
        with self.assertRaisesRegex(ValueError, "FITTING_FORBIDDEN"):
            m.feedback("Backup", 1.)
        self.assertEqual(m.parameter_sha256(), frozen)
        m.feedback("Backup", 0., learning=False, terminal=True)

    def test_snapshot_tampering_denied_and_midtrial_cold_restore(self):
        m = NativeRingMemoryDev()
        m.advance("MRV")
        m.feedback("GoForward", 1.)
        m.advance("Nothing")
        digest = m.parameter_sha256()
        snap = m.checkpoint()
        restored = NativeRingMemoryDev.restore(snap)
        self.assertTrue(restored.pending)
        self.assertEqual(m.q_values(), restored.q_values())
        self.assertEqual(digest, restored.parameter_sha256())
        corrupt = json.loads(snap)
        corrupt["body"]["gates"][0] = 4.
        with self.assertRaisesRegex(ValueError, "UNTRUSTED"):
            NativeRingMemoryDev.restore(json.dumps(corrupt).encode())
        with self.assertRaisesRegex(ValueError, "UNTRUSTED"):
            NativeRingMemoryDev.restore(b"{}")
        program = """
import json, sys
from yggdrasil.itd02_local_ring_memory_dev import NativeRingMemoryDev
m=NativeRingMemoryDev.restore(sys.stdin.buffer.read())
print(json.dumps({"action":m.choose(),"sha":m.parameter_sha256(),"pending":m.pending}))
"""
        run = subprocess.run([sys.executable, "-B", "-c", program], input=snap,
                             capture_output=True, timeout=15, check=True)
        data = json.loads(run.stdout)
        self.assertEqual(data["sha"], digest)
        self.assertTrue(data["pending"])
        self.assertEqual(data["action"], m.choose())


if __name__ == "__main__":
    unittest.main()
