"""V22 source-only local learning boundaries and negative sharing controls."""
import json
import unittest

from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, PUBLIC_CUES, ACTION_SITES, RING,
)
from yggdrasil.itd02_v22_shared_context_ring_dev import (
    CELLS, EDGE_SIGNAL_PER_PASS, HEAD_FEATURES, LEARNED_SCALARS,
    SOURCE_SIGNAL_PER_PASS, SharedContextRingDev, _mix_scalars,
)


class V22SharedContextTests(unittest.TestCase):
    def test_scalar_hops_only_real_original_edges(self):
        self.assertEqual(LEARNED_SCALARS, 163)
        for cell in range(CELLS):
            self.assertEqual(set(RING[cell]),
                             {(cell-1)%CELLS, (cell+1)%CELLS})
            seed = [0.0]*CELLS
            seed[cell] = 1.0
            raw, count0 = _mix_scalars(seed, 0)
            once, count1 = _mix_scalars(seed, 1)
            four, count4 = _mix_scalars(seed, 4)
            self.assertEqual(raw, seed)
            self.assertEqual(count0, 0)
            self.assertEqual(count1, 2*CELLS)
            self.assertEqual(count4, EDGE_SIGNAL_PER_PASS)
            self.assertTrue(all(v >= 0 for v in four))
            self.assertAlmostEqual(sum(four), 1., places=12)
            for far in range(CELLS):
                if far not in (cell, (cell-1)%CELLS, (cell+1)%CELLS):
                    self.assertEqual(once[far], 0.0)
        with self.assertRaises(ValueError):
            _mix_scalars([0.0]*CELLS, True)
        with self.assertRaises(ValueError):
            _mix_scalars([0.0]*(CELLS-1), 3)

    def test_two_actual_actions_share_cell_weights_but_not_action_biases(self):
        shared = SharedContextRingDev(mode="shared")
        partition = SharedContextRingDev(mode="action_partition")
        self.assertEqual(shared.native_ids, partition.native_ids)
        for model in (shared, partition):
            self.assertEqual(len(model.cell_weights)*HEAD_FEATURES+3,163)
            self.assertTrue(callable(model.score))
            model.start_observation("LRV")
            with self.assertRaises(ValueError):
                model.accept_first("Backup", reward=1)
            model.accept_first("Backup")
            self.assertEqual(model.forward_input_messages, SOURCE_SIGNAL_PER_PASS)
            before = model.parameters_sha256()
            biases = list(model.action_biases)
            model.accept_second("GoForward", 2.0)
            self.assertNotEqual(before, model.parameters_sha256())
            self.assertEqual(model.action_biases[0], biases[0])
            self.assertEqual(model.action_biases[2], biases[2])
            self.assertNotEqual(model.action_biases[1], biases[1])
            self.assertEqual(model.updates,1)
            self.assertEqual(model.reverse_credit_messages,EDGE_SIGNAL_PER_PASS)
            old = [list(row) for row in model.cell_weights]
            biases = list(model.action_biases)
            model.start_observation("MRV")
            model.accept_first("TurnAround")
            model.accept_second("Backup", -1.5)
            self.assertEqual(model.action_biases[0],biases[0])
            self.assertEqual(model.action_biases[1],biases[1])
            self.assertNotEqual(model.action_biases[2],biases[2])
            changed = [i for i in range(CELLS)
                       if model.cell_weights[i] != old[i]]
            if model.mode == "shared":
                self.assertTrue(any(i % 3 != 2 for i in changed))
            else:
                self.assertTrue(changed)
                self.assertTrue(all(i % 3 == 2 for i in changed))
            self.assertEqual(model.updates,2)
            checkpoint = model.checkpoint()
            self.assertEqual(
                SharedContextRingDev.restore(checkpoint).checkpoint(),
                checkpoint)

    def test_no_hidden_input_frozen_and_corruption_rejected(self):
        with self.assertRaises(ValueError):
            SharedContextRingDev(mode="central_pool")
        m=SharedContextRingDev()
        with self.assertRaises(ValueError):
            m.accept_first("GoForward")
        with self.assertRaises(ValueError):
            m.start_observation("Nothing")
        m.start_observation("docked_MRV")
        m.accept_first("GoForward")
        before=m.checkpoint()
        with self.assertRaises(TypeError):
            m.accept_second("Backup", 1.0, hidden_law="private")
        with self.assertRaises(ValueError):
            m.accept_second("Backup", float("nan"))
        self.assertEqual(before,m.checkpoint())
        m.accept_second("Backup", 1.0)
        raw=m.checkpoint()
        self.assertLessEqual(len(raw),8192)
        self.assertEqual(
            SharedContextRingDev.restore(raw).checkpoint(),raw)
        m.start_frozen_evaluation()
        params=m.parameters_sha256()
        m.start_observation("MRV")
        m.accept_first("TurnAround")
        pending=m.checkpoint()
        with self.assertRaises(ValueError):
            m.accept_second("Backup", 1.0, learning=True)
        self.assertEqual(m.checkpoint(), pending)
        m.accept_second("Backup", 1.0, learning=False)
        self.assertEqual(m.parameters_sha256(),params)
        broken=bytearray(pending)
        broken[len(broken)//2]^=1
        with self.assertRaises(ValueError):
            SharedContextRingDev.restore(bytes(broken))
        spoof=json.loads(pending)
        spoof["body"]["cell_weights"][0][0]=999.0
        with self.assertRaises(ValueError):
            SharedContextRingDev.restore(json.dumps(spoof).encode())
        clone=SharedContextRingDev.restore(pending)
        clone.cell_weights[0][0]+=0.1
        with self.assertRaises(ValueError):
            clone.checkpoint()


if __name__ == "__main__":
    unittest.main()
