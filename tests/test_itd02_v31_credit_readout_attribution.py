"""V31 frozen readout, local credit, and nonlearning public-action safety."""
import unittest

from research.itd02_v29_observational_equivalence_audit import selected_map
from research.itd02_v31_credit_readout_attribution_audit import readout
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev


class V31CreditAttributionTests(unittest.TestCase):
    @staticmethod
    def trained_source():
        m=SharedContextRingDev(mode="shared")
        m.start_observation(PUBLIC_CUES[0])
        m.accept_first(ACTIONS[0])
        m.accept_second(ACTIONS[1],1.0)
        return m.checkpoint()

    def test_unmodified_readout_and_expected_action_count(self):
        m=CalibratedReturnRingDev(self.trained_source())
        cp=m.checkpoint()
        observed,mapping=selected_map()
        self.assertEqual(len(observed),12)
        result=readout(m,"A",mapping)
        self.assertEqual(set(result["regret"]),{"active","fast","source"})
        self.assertEqual(len(result["trace"]),12)
        self.assertEqual(len(result["actions"]["active"]),12)
        self.assertEqual(m.checkpoint(),cp)
        self.assertEqual(
            CalibratedReturnRingDev.restore(cp).checkpoint(),cp)

    def test_real_selected_reward_changes_only_fast_native_weights(self):
        source=self.trained_source()
        learner=CalibratedReturnRingDev(source)
        nolearn=CalibratedReturnRingDev(source)
        frozen=learner.bank.source_sha
        fast=learner.bank.fast.parameters_sha256()
        for m in (learner,nolearn):
            m.start_observation(PUBLIC_CUES[0])
            m.accept_first(ACTIONS[0])
        with self.assertRaises(TypeError):
            learner.accept_second(ACTIONS[1],1.0,regime="B")
        learner.accept_second(ACTIONS[1],1.0)
        nolearn.accept_second(ACTIONS[1],1.0,learning=False)
        self.assertEqual(learner.bank.slow.parameters_sha256(),frozen)
        self.assertEqual(nolearn.bank.slow.parameters_sha256(),frozen)
        self.assertNotEqual(learner.bank.fast.parameters_sha256(),fast)
        self.assertEqual(nolearn.bank.fast.parameters_sha256(),fast)
        self.assertEqual(learner.bank.fast.updates,1)
        self.assertEqual(nolearn.bank.fast.updates,0)
        self.assertEqual(
            CalibratedReturnRingDev.restore(learner.checkpoint()).checkpoint(),
            learner.checkpoint())

    def test_invalid_terminal_reward_fails_closed(self):
        m=CalibratedReturnRingDev(self.trained_source())
        m.start_observation(PUBLIC_CUES[0])
        m.accept_first(ACTIONS[0])
        cp=m.checkpoint()
        with self.assertRaises(ValueError):
            m.accept_second(ACTIONS[1],float("nan"))
        self.assertEqual(cp,m.checkpoint())


if __name__=="__main__":
    unittest.main()
