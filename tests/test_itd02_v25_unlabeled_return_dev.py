"""V25 focused sequential evidence/protected-memory source-only controls."""
import json
import unittest
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v25_unlabeled_return_dev import UnlabeledReturnRingDev

class V25UnlabeledReturnTests(unittest.TestCase):
    def source(self):
        s=SharedContextRingDev()
        s.start_observation("LRV")
        s.accept_first("Backup")
        s.accept_second("GoForward",1.0)
        return s.checkpoint()

    def test_all_feedback_public_and_selected(self):
        m=UnlabeledReturnRingDev(self.source())
        self.assertFalse(m.use_fast)
        original=m.bank.source_sha
        m.start_observation("MRV")
        m.accept_first("GoForward")
        before=m.checkpoint()
        with self.assertRaises(TypeError):
            m.accept_second("Backup",0.5,secret_stage="return")
        with self.assertRaises(ValueError):
            m.accept_second("Backup",float("nan"))
        self.assertEqual(m.checkpoint(),before)
        m.accept_second("Backup",1.0)
        self.assertEqual(m.bank.target_updates,1)
        self.assertEqual(m.bank.fast.updates,1)
        self.assertEqual(m.bank.slow.parameters_sha256(),original)
        self.assertEqual(len(m.recent),1)
        self.assertEqual(
            UnlabeledReturnRingDev.restore(m.checkpoint()).checkpoint(),m.checkpoint())

    def test_selector_requires_three_public_errors_and_retains_source(self):
        m=UnlabeledReturnRingDev(self.source())
        s=m.bank.source_sha
        for i in range(12):
            m.start_observation("LRV")
            m.accept_first("Backup")
            # Legal public outcomes only; no externally told regime.
            m.accept_second("TurnAround",(-1.0 if i%2 else 1.0))
            self.assertLessEqual(len(m.recent),4)
            self.assertTrue(all(v in (-1,0,1) for v in m.recent))
            self.assertEqual(m.bank.slow.parameters_sha256(),s)
        m.start_frozen_evaluation()
        identity=m.parameters_sha256()
        m.start_observation("MRV")
        m.accept_first("GoForward")
        checkpoint=m.checkpoint()
        with self.assertRaises(ValueError):
            m.accept_second("Backup",1.0,learning=True)
        self.assertEqual(m.checkpoint(),checkpoint)
        m.accept_second("Backup",0.0,learning=False)
        self.assertEqual(m.parameters_sha256(),identity)

    def test_cold_checkpoint_provenance_fail_closed(self):
        m=UnlabeledReturnRingDev(self.source())
        good=m.checkpoint()
        self.assertEqual(UnlabeledReturnRingDev.restore(good).checkpoint(),good)
        bad=json.loads(good)
        bad["body"]["recent"]=[1,1,1,1]
        with self.assertRaises(ValueError):
            UnlabeledReturnRingDev.restore(json.dumps(bad).encode())
        bad=json.loads(good)
        bad["body"]["v24_bank"]["body"]["fast_bank"]["body"]["cell_weights"][0][0]=123
        with self.assertRaises(ValueError):
            UnlabeledReturnRingDev.restore(json.dumps(bad).encode())

if __name__=="__main__":
    unittest.main()
