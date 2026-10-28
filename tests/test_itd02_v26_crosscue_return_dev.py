"""V26 preregistered public-only cross-cue selector boundary tests."""
import json
import unittest

from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v26_crosscue_return_dev import (
    CrossCueReturnRingDev, candidate_vote, WINDOW, CHECKPOINT_BOUND,
)


class V26CrossCueTests(unittest.TestCase):
    @staticmethod
    def source():
        m = SharedContextRingDev(mode="shared")
        m.start_observation("LRV")
        m.accept_first("Backup")
        m.accept_second("GoForward", 1.0)
        return m.checkpoint()

    def test_crosscue_witness_prevents_single_group_spurious_return(self):
        crosscue = [[0.25,0],[0.25,0],[0.25,0],[0.0,1]]
        self.assertEqual(len(crosscue), WINDOW)
        self.assertTrue(candidate_vote(crosscue, True, require_diversity=True))
        self.assertFalse(candidate_vote(crosscue, True, require_diversity=False))
        real = [[0.25,0],[0.25,1],[0.25,0],[-0.05,1]]
        self.assertFalse(candidate_vote(real, True, require_diversity=True))
        late = [[-0.30,0],[-0.30,1],[-0.30,0],[0.0,1]]
        self.assertTrue(candidate_vote(late, False, require_diversity=True))
        self.assertFalse(candidate_vote(real[:3], True))
        self.assertFalse(candidate_vote(late[:3], False))

    def test_public_feedback_source_freeze_cold_restore_and_sealed_readout(self):
        m = CrossCueReturnRingDev(self.source())
        old = m.bank.source_sha
        self.assertFalse(m.use_fast)
        self.assertEqual(m.bank.fast.updates,0)
        for cue in ("LRV","MRV","docked_LRV","docked_MRV"):
            m.start_observation(cue)
            m.accept_first("Backup")
            original=m.checkpoint()
            with self.assertRaises(TypeError):
                m.accept_second("GoForward",1.0,regime="source")
            self.assertEqual(m.checkpoint(),original)
            with self.assertRaises(ValueError):
                m.accept_second("GoForward",float("nan"))
            m.accept_second("GoForward", 1.0)
            self.assertEqual(m.bank.slow.parameters_sha256(),old)
        self.assertEqual(m.bank.target_updates,4)
        self.assertEqual(m.bank.fast.updates,4)
        self.assertLessEqual(len(m.checkpoint()),CHECKPOINT_BOUND)
        self.assertEqual(CrossCueReturnRingDev.restore(m.checkpoint()).checkpoint(),
                         m.checkpoint())
        m.start_frozen_evaluation()
        before=m.parameters_sha256()
        m.start_observation("LRV")
        m.accept_first("Backup")
        saved=m.checkpoint()
        with self.assertRaises(ValueError):
            m.accept_second("GoForward",1.0,learning=True)
        self.assertEqual(m.checkpoint(),saved)
        m.accept_second("GoForward",0.0,learning=False)
        self.assertEqual(m.parameters_sha256(),before)
        self.assertEqual(m.bank.slow.parameters_sha256(),old)

    def test_untrusted_checkpoint_rejected(self):
        m=CrossCueReturnRingDev(self.source())
        raw=m.checkpoint()
        self.assertEqual(CrossCueReturnRingDev.restore(raw).checkpoint(),raw)
        for corrupt in (lambda v:v["body"].__setitem__("recent",[[0.2,1]]),
                        lambda v:v["body"].__setitem__("reactivations",99),
                        lambda v:v["body"]["v24_bank"]["body"]["fast_bank"]["body"]
                                 ["cell_weights"][0].__setitem__(0,99.0)):
            broken=json.loads(raw)
            corrupt(broken)
            with self.assertRaises(ValueError):
                CrossCueReturnRingDev.restore(json.dumps(broken).encode())

if __name__=="__main__":
    unittest.main()
