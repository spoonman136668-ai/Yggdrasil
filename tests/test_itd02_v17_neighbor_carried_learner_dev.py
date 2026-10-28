"""V17 development-only integrity, locality, cold checkpoint and freezing."""
import json
import math
import unittest

from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CHANNELS, HOPS, RING,
    NeighborCarriedPublicLearnerDev, PUBLIC_CUES,
    neighbor_transport, site_pulses,
)


class NeighborCarriedDevTests(unittest.TestCase):
    def test_real_neighbor_transport_no_direct_global_tuple(self):
        for cue in PUBLIC_CUES:
            for first in ACTIONS:
                pulse = site_pulses(cue, first)
                source, zero = neighbor_transport(pulse, 0)
                full, four = neighbor_transport(pulse, HOPS)
                self.assertEqual(source, pulse)
                self.assertEqual(zero, 0)
                self.assertEqual(four, 8 * 2 * CHANNELS * HOPS)
                self.assertEqual(sum(sum(s) for s in source), 2.0)
                self.assertTrue(all(sum(row) == 2.0 for row in full))
                # At zero hops, reward heads have no direct cue injection.
                self.assertTrue(all(
                    not any(source[s][:4]) for s in ACTION_SITES))
                for site in range(8):
                    self.assertEqual(len(RING[site]), 2)
                    self.assertEqual(set(RING[site]),
                                     {(site - 1) % 8, (site + 1) % 8})
        with self.assertRaises(ValueError):
            neighbor_transport(site_pulses("LRV", "GoForward"), True)
        with self.assertRaises(ValueError):
            site_pulses("SPOOF", "GoForward")
        with self.assertRaises(ValueError):
            site_pulses("LRV", "SPOOF")

    def test_actual_first_action_local_only_and_cold_restore(self):
        m = NeighborCarriedPublicLearnerDev()
        with self.assertRaises(ValueError):
            m.accept_first("Backup")
        with self.assertRaises(ValueError):
            m.start_observation("Nothing")
        m.start_observation("LRV")
        with self.assertRaises(ValueError):
            m.accept_first("Backup", reward=10)
        with self.assertRaises(ValueError):
            m.accept_first("Backup", next_observation="LRV")
        self.assertIsNone(m.first)
        m.accept_first("Backup")
        self.assertEqual(m.first, "Backup")
        self.assertEqual(m.edge_scalar_messages, 448)
        cp = m.checkpoint()
        self.assertEqual(NeighborCarriedPublicLearnerDev.restore(cp).checkpoint(), cp)
        x = m._features("GoForward")
        self.assertEqual(len(x), 8)
        self.assertEqual(x[1 + PUBLIC_CUES.index("LRV")], 1.0)
        self.assertEqual(x[1 + 4 + ACTIONS.index("Backup")], 1.0)
        before = m.parameters_sha256()
        for bad_reward in (float("nan"), float("inf"), -4, 11, True):
            with self.assertRaises(ValueError):
                m.accept_second("GoForward", bad_reward)
            self.assertEqual(m.checkpoint(), cp)
        with self.assertRaises(ValueError):
            m.accept_second("GoForward", 0, terminal=False)
        with self.assertRaises(TypeError):
            m.accept_second("GoForward", 0, hidden_law="private")
        m.accept_second("GoForward", 1.5)
        self.assertNotEqual(m.parameters_sha256(), before)
        self.assertEqual(m.learned_updates, 1)
        self.assertEqual(m.transitions, 2)
        self.assertEqual(m.native_ids, NeighborCarriedPublicLearnerDev().native_ids)
        self.assertTrue(all(
            m.weights[i] == [0.0]*8 for i in (0, 2)))
        raw = m.checkpoint()
        self.assertEqual(NeighborCarriedPublicLearnerDev.restore(raw).checkpoint(), raw)

    def test_frozen_inference_and_checkpoint_tamper_rejection(self):
        m = NeighborCarriedPublicLearnerDev()
        m.start_observation("MRV")
        m.accept_first("TurnAround")
        m.accept_second("Backup", 2.0, learning=True)
        m.start_frozen_evaluation()
        frozen = m.parameters_sha256()
        m.start_observation("docked_LRV")
        m.accept_first("GoForward")
        checkpoint = m.checkpoint()
        restored = NeighborCarriedPublicLearnerDev.restore(checkpoint)
        self.assertEqual(restored.checkpoint(), checkpoint)
        self.assertEqual(restored.local_scores(), m.local_scores())
        self.assertEqual(restored.choose(), m.choose())
        with self.assertRaises(ValueError):
            m.accept_second("Backup", 3.0, learning=True)
        self.assertEqual(m.checkpoint(), checkpoint)
        m.accept_second("Backup", 3.0, learning=False)
        self.assertEqual(m.parameters_sha256(), frozen)
        with self.assertRaises(ValueError):
            m.start_observation("Spoof")
        broken = bytearray(checkpoint)
        broken[len(broken)//2] ^= 1
        with self.assertRaises(ValueError):
            NeighborCarriedPublicLearnerDev.restore(bytes(broken))
        edited = json.loads(checkpoint)
        edited["body"]["native_ids"]["native"] = "0"*64
        with self.assertRaises(ValueError):
            NeighborCarriedPublicLearnerDev.restore(json.dumps(edited).encode())
        edited = json.loads(checkpoint)
        edited["body"]["delivered"][0][0] = 0.5
        with self.assertRaises(ValueError):
            NeighborCarriedPublicLearnerDev.restore(json.dumps(edited).encode())
        restored.weights[0][0] = 2.
        with self.assertRaises(ValueError):
            restored.local_scores()


if __name__ == "__main__":
    unittest.main()
