"""V18 isolated native-ring engineering integrity and negative controls."""
import json
import unittest

from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    ACTIONS, ACTION_SITES, CHANNELS, INITIAL_GAIN,
    IntermediatePlasticRingDev, forward_local, site_pulses,
)


class V18IntermediatePlasticityTests(unittest.TestCase):
    def test_neighbor_only_delivery_and_actual_selected_action(self):
        gains = [[INITIAL_GAIN] * CHANNELS for _ in range(8)]
        for cue in ("LRV", "MRV", "docked_LRV", "docked_MRV"):
            for first in ACTIONS:
                pulse = site_pulses(cue, first)
                at_zero, _, zero_messages = forward_local(pulse, gains, hops=0)
                at_four, _, message_count = forward_local(pulse, gains, hops=4)
                self.assertEqual(at_zero, pulse)
                self.assertEqual(zero_messages, 0)
                self.assertEqual(message_count, 8 * 2 * CHANNELS * 4)
                self.assertEqual(sum(sum(row) for row in at_zero), 2.0)
                self.assertTrue(any(at_four[s][0] or at_four[s][1] or
                                    at_four[s][2] or at_four[s][3]
                                    for s in ACTION_SITES))
                self.assertFalse(any(any(at_zero[s][:4]) for s in ACTION_SITES))

    def test_intermediate_gains_only_on_trained_arm_and_selected_head(self):
        full = IntermediatePlasticRingDev(plastic_intermediate=True)
        frozen = IntermediatePlasticRingDev(plastic_intermediate=False)
        ids = dict(full.native_ids)
        for model in (full, frozen):
            model.start_observation("LRV")
            with self.assertRaises(ValueError):
                model.accept_first("Backup", reward=10)
            self.assertIsNone(model.first)
            model.accept_first("Backup")
            self.assertEqual(model.first, "Backup")
            self.assertEqual(model.forward_messages, 448)
        before_full = [list(row) for row in full.heads]
        before_frozen = [list(row) for row in frozen.heads]
        full.accept_second("GoForward", 2.0)
        frozen.accept_second("GoForward", 2.0)
        self.assertEqual(full.native_ids, frozen.native_ids)
        self.assertEqual(full.native_ids, ids)
        self.assertEqual(full.credit_messages, 64)
        self.assertEqual(frozen.credit_messages, 0)
        self.assertTrue(any(abs(g-INITIAL_GAIN)>1e-12
                            for i,row in enumerate(full.gains)
                            if i not in ACTION_SITES for g in row))
        self.assertTrue(all(g==INITIAL_GAIN for row in frozen.gains for g in row))
        self.assertEqual(full.heads[0], before_full[0])
        self.assertEqual(full.heads[2], before_full[2])
        self.assertEqual(frozen.heads[0], before_frozen[0])
        self.assertEqual(frozen.heads[2], before_frozen[2])
        self.assertNotEqual(full.heads[1], before_full[1])

    def test_checkpoint_integrity_frozen_behavior_and_no_hidden_fields(self):
        model = IntermediatePlasticRingDev(plastic_intermediate=True)
        with self.assertRaises(ValueError):
            model.accept_first("GoForward")
        with self.assertRaises(ValueError):
            model.start_observation("Nothing")
        model.start_observation("docked_MRV")
        model.accept_first("GoForward")
        snap = model.checkpoint()
        self.assertEqual(IntermediatePlasticRingDev.restore(snap).checkpoint(), snap)
        with self.assertRaises(TypeError):
            model.accept_second("Backup", 1.0, hidden_world="secret")
        with self.assertRaises(ValueError):
            model.accept_second("Backup", float("nan"))
        with self.assertRaises(ValueError):
            model.accept_second("Backup", 1.0, terminal=False)
        self.assertEqual(model.checkpoint(), snap)
        model.accept_second("Backup", 1.0)
        snap = model.checkpoint()
        self.assertEqual(IntermediatePlasticRingDev.restore(snap).checkpoint(), snap)
        model.start_frozen_evaluation()
        identity = model.parameters_sha256()
        model.start_observation("MRV")
        model.accept_first("TurnAround")
        with self.assertRaises(ValueError):
            model.accept_second("GoForward", 1.0, learning=True)
        model.accept_second("GoForward", 1.0, learning=False)
        self.assertEqual(model.parameters_sha256(), identity)
        corrupt = bytearray(snap)
        corrupt[len(corrupt)//2] ^= 1
        with self.assertRaises(ValueError):
            IntermediatePlasticRingDev.restore(bytes(corrupt))
        altered = json.loads(snap)
        altered["body"]["gains"][0][0] = 9.0
        with self.assertRaises(ValueError):
            IntermediatePlasticRingDev.restore(json.dumps(altered).encode())
        restored = IntermediatePlasticRingDev.restore(model.checkpoint())
        restored.heads[1][0] += 1.0
        with self.assertRaises(ValueError):
            restored.checkpoint()


if __name__ == "__main__":
    unittest.main()
