"""V20 local causal-responsibility witness, checkpoint and boundary controls."""
import json
import unittest

from research.itd02_v19_local_credit_causality_audit import (
    reconstructed_prediction,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, ACTION_SITES
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    CELLS, CHANNELS, INITIAL_GAIN, IntermediatePlasticRingDev,
)
from yggdrasil.itd02_v20_causal_credit_dev import (
    ResponsibilityGatedRingDev, SCHEMA,
)


def start(model, cue="LRV", first="Backup"):
    model.start_observation(cue)
    model.accept_first(first)


class V20ResponsibilityGatedTests(unittest.TestCase):
    def test_first_feedback_does_not_move_noncausal_gains(self):
        for cue, first, selected in (
            ("LRV","Backup","GoForward"),
            ("docked_MRV","GoForward","TurnAround"),
            ("MRV","TurnAround","Backup"),
        ):
            m = ResponsibilityGatedRingDev()
            native = dict(m.native_ids)
            start(m, cue, first)
            before = m.checkpoint()
            grad, messages = m.local_gain_responsibilities(selected)
            self.assertEqual(messages, 448)
            self.assertEqual(len(grad), CELLS)
            self.assertTrue(all(len(row) == CHANNELS for row in grad))
            self.assertTrue(all(x == 0 for row in grad for x in row))
            with self.assertRaises(TypeError):
                m.accept_second(selected, 2.0, secret_world="private")
            self.assertEqual(m.checkpoint(), before)
            with self.assertRaises(ValueError):
                m.accept_second(selected, float("nan"))
            self.assertEqual(m.checkpoint(), before)
            before_heads = [list(row) for row in m.heads]
            m.accept_second(selected, 2.0)
            self.assertEqual(m.native_ids, native)
            self.assertTrue(all(v == INITIAL_GAIN for row in m.gains for v in row))
            chosen = ACTIONS.index(selected)
            for idx in range(3):
                if idx == chosen:
                    self.assertNotEqual(m.heads[idx], before_heads[idx])
                else:
                    self.assertEqual(m.heads[idx], before_heads[idx])
            self.assertEqual(m.learned_updates, 1)
            self.assertEqual(m.credit_messages, 448)
            self.assertEqual(
                ResponsibilityGatedRingDev.restore(m.checkpoint()).checkpoint(),
                m.checkpoint())

    def test_adjoint_is_driven_by_trained_head_and_actual_local_path(self):
        m = ResponsibilityGatedRingDev()
        start(m,"LRV","Backup")
        m.accept_second("GoForward",2.0)
        start(m,"LRV","Backup")
        expected = m.scores()[ACTIONS.index("GoForward")]
        self.assertAlmostEqual(reconstructed_prediction(
            m,"LRV","Backup","GoForward",m.gains),expected,places=12)
        local, _ = m.local_gain_responsibilities("GoForward")
        self.assertTrue(any(abs(v)>1e-7 for row in local for v in row))
        for row in local:
            for value in row:
                self.assertLessEqual(abs(value), 1000)
        m.accept_second("GoForward",2.0)
        self.assertTrue(any(
            abs(g-INITIAL_GAIN)>1e-12 for row in m.gains for g in row))
        self.assertEqual(m.native_ids, IntermediatePlasticRingDev().native_ids)

    def test_distinct_schema_frozen_and_corrupted_checkpoint_rejected(self):
        m = ResponsibilityGatedRingDev()
        start(m)
        m.accept_second("GoForward",1.0)
        packet = m.checkpoint()
        self.assertEqual(json.loads(packet)["body"]["schema"],SCHEMA)
        self.assertEqual(ResponsibilityGatedRingDev.restore(packet).checkpoint(),packet)
        with self.assertRaises(ValueError):
            IntermediatePlasticRingDev.restore(packet)
        m.start_frozen_evaluation()
        id_before = m.parameters_sha256()
        start(m,"docked_LRV","TurnAround")
        current = m.checkpoint()
        with self.assertRaises(ValueError):
            m.accept_second("Backup",1.0,learning=True)
        self.assertEqual(current,m.checkpoint())
        m.accept_second("Backup",1.0,learning=False)
        self.assertEqual(id_before,m.parameters_sha256())
        damaged = bytearray(current)
        damaged[len(damaged)//2] ^= 1
        with self.assertRaises(ValueError):
            ResponsibilityGatedRingDev.restore(bytes(damaged))
        spoof = json.loads(current)
        spoof["body"]["gains"][0][0] = 15
        with self.assertRaises(ValueError):
            ResponsibilityGatedRingDev.restore(json.dumps(spoof).encode())
        restored = ResponsibilityGatedRingDev.restore(current)
        restored.gains[0][0] += 0.01
        with self.assertRaises(ValueError):
            restored.checkpoint()


if __name__ == "__main__":
    unittest.main()
