"""V32 opt-in public-only source surprise, negative controls and custody."""
import unittest
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v32_source_surprise_probation_dev import (
    SourceSurpriseProbationDev,SOURCE_SURPRISE,RETURN_MARGIN,RETURN_STREAK)

class V32SourceProbationTests(unittest.TestCase):
    @staticmethod
    def source():
        m=SharedContextRingDev(mode="shared")
        m.start_observation(PUBLIC_CUES[0])
        m.accept_first(ACTIONS[0])
        m.accept_second(ACTIONS[1],0.5)
        return m.checkpoint()

    def test_public_source_surprise_triggers_fast_protects_source(self):
        m=SourceSurpriseProbationDev(self.source())
        source_sha=m.bank.source_sha
        m.start_observation(PUBLIC_CUES[0])
        m.accept_first(ACTIONS[0])
        prior=m.source_score(ACTIONS[1])
        observed=prior+SOURCE_SURPRISE+0.5
        m.accept_second(ACTIONS[1],observed)
        self.assertTrue(m.use_fast)
        self.assertEqual(m.events,1)
        self.assertEqual(m.switches,1)
        self.assertEqual(m.bank.target_updates,1)
        self.assertEqual(m.bank.slow.parameters_sha256(),source_sha)
        raw=m.checkpoint()
        self.assertEqual(SourceSurpriseProbationDev.restore(raw).checkpoint(),raw)
        with self.assertRaises(ValueError):
            SourceSurpriseProbationDev.restore(raw[:-1]+b'0')

    def test_nonlearning_readout_does_not_switch_or_update(self):
        m=SourceSurpriseProbationDev(self.source())
        sha=m.bank.fast.parameters_sha256()
        m.start_observation(PUBLIC_CUES[0])
        m.accept_first(ACTIONS[0])
        m.accept_second(ACTIONS[1],3.0,learning=False)
        self.assertFalse(m.use_fast)
        self.assertEqual(m.events,0)
        self.assertEqual(m.bank.fast.parameters_sha256(),sha)
        self.assertEqual(m.bank.target_updates,0)

    def test_frozen_readout_rejects_training_and_hidden_world(self):
        m=SourceSurpriseProbationDev(self.source())
        m.start_frozen_evaluation()
        m.start_observation(PUBLIC_CUES[1])
        m.accept_first(ACTIONS[2])
        with self.assertRaises(ValueError):
            m.accept_second(ACTIONS[0],1.0)
        with self.assertRaises(TypeError):
            m.accept_second(ACTIONS[0],1.0,regime="source")
        m.accept_second(ACTIONS[0],0.0,learning=False)
        self.assertFalse(m.use_fast)

    def test_invalid_reward_fail_closed(self):
        m=SourceSurpriseProbationDev(self.source())
        m.start_observation(PUBLIC_CUES[1])
        m.accept_first(ACTIONS[2])
        before=m.checkpoint()
        with self.assertRaises(ValueError):
            m.accept_second(ACTIONS[2],float("nan"))
        self.assertEqual(m.checkpoint(),before)
        self.assertEqual(RETURN_MARGIN,0.20)
        self.assertEqual(RETURN_STREAK,2)

if __name__=="__main__":
    unittest.main()
