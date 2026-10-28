"""V24 frozen source source-only negative controls and staged sparse feedback."""
import json
import unittest

from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v24_protected_dual_memory_dev import (
    ProtectedDualMemoryRingDev,CHECKPOINT_BOUND,STORED_SCALARS,
)


class V24ProtectedDualTests(unittest.TestCase):
    @staticmethod
    def source():
        s=SharedContextRingDev(mode="shared")
        s.start_observation("LRV")
        s.accept_first("Backup")
        s.accept_second("GoForward",1.0)
        return s.checkpoint()

    def test_source_frozen_fast_learns_selected_action_only(self):
        m=ProtectedDualMemoryRingDev(self.source())
        self.assertEqual(STORED_SCALARS,326)
        self.assertFalse(m.gate_fast)
        source_sha=m.source_sha
        self.assertEqual(m.fast.updates,0)
        m.start_observation("MRV")
        with self.assertRaises(ValueError):
            m.accept_first("Backup",reward=2)
        m.accept_first("Backup")
        biases=list(m.fast.action_biases)
        before=m.checkpoint()
        with self.assertRaises(TypeError):
            m.accept_second("GoForward",1.0,private_family="unseen")
        self.assertEqual(m.checkpoint(),before)
        with self.assertRaises(ValueError):
            m.accept_second("GoForward",float("nan"))
        self.assertEqual(m.checkpoint(),before)
        m.accept_second("GoForward",2.0)
        self.assertEqual(m.fast.updates,1)
        self.assertEqual(m.slow.updates,1)
        self.assertEqual(m.source_sha,source_sha)
        self.assertEqual(m.slow.parameters_sha256(),source_sha)
        self.assertEqual(m.fast.action_biases[0],biases[0])
        self.assertNotEqual(m.fast.action_biases[1],biases[1])
        self.assertEqual(m.fast.action_biases[2],biases[2])
        self.assertEqual(m.target_updates,1)
        self.assertEqual(m.gate_fast,m.fast_loss<=m.slow_loss)
        raw=m.checkpoint()
        self.assertLessEqual(len(raw),CHECKPOINT_BOUND)
        self.assertEqual(ProtectedDualMemoryRingDev.restore(raw).checkpoint(),raw)

    def test_selector_is_prospective_and_no_source_write(self):
        m=ProtectedDualMemoryRingDev(self.source())
        sha=m.source_sha
        m.start_observation("docked_LRV")
        m.accept_first("TurnAround")
        slow=m.source_score("Backup")
        fast=m.fast_score("Backup")
        self.assertEqual(m.score("Backup"),slow)
        self.assertEqual(m.slow_loss,0.0)
        self.assertEqual(m.fast_loss,0.0)
        m.accept_second("Backup",3.0)
        self.assertAlmostEqual(m.slow_loss,abs(3-slow),places=12)
        self.assertAlmostEqual(m.fast_loss,abs(3-fast),places=12)
        self.assertEqual(m.gate_fast,abs(3-fast)<=abs(3-slow))
        self.assertEqual(m.slow.parameters_sha256(),sha)
        raw=m.checkpoint()
        m.start_frozen_evaluation()
        frozen_sha=m.parameters_sha256()
        m.start_observation("LRV")
        m.accept_first("GoForward")
        with self.assertRaises(ValueError):
            m.accept_second("TurnAround",1.0,learning=True)
        m.accept_second("TurnAround",0.0,learning=False)
        self.assertEqual(m.parameters_sha256(),frozen_sha)
        self.assertEqual(m.slow.parameters_sha256(),sha)
        self.assertEqual(ProtectedDualMemoryRingDev.restore(raw).checkpoint(),raw)

    def test_checkpoint_tampering_rejected_and_source_not_empty(self):
        with self.assertRaises(ValueError):
            ProtectedDualMemoryRingDev(SharedContextRingDev().checkpoint())
        m=ProtectedDualMemoryRingDev(self.source())
        raw=m.checkpoint()
        mutated=bytearray(raw)
        mutated[len(mutated)//2]^=1
        with self.assertRaises(ValueError):
            ProtectedDualMemoryRingDev.restore(bytes(mutated))
        spoof=json.loads(raw)
        spoof["body"]["source_bank"]["body"]["cell_weights"][0][0]=9.0
        with self.assertRaises(ValueError):
            ProtectedDualMemoryRingDev.restore(json.dumps(spoof).encode())
        other=json.loads(raw)
        other["body"]["target_updates"]=100
        with self.assertRaises(ValueError):
            ProtectedDualMemoryRingDev.restore(json.dumps(other).encode())
        m.start_observation("MRV")
        m.accept_first("Backup")
        raw_pending=m.checkpoint()
        self.assertEqual(
            ProtectedDualMemoryRingDev.restore(raw_pending).checkpoint(),raw_pending)


if __name__=="__main__":
    unittest.main()
