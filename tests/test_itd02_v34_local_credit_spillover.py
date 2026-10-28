"""V34 original native local-credit diagnostic source-only safety tests."""
import unittest
from research.itd02_v34_local_credit_spillover_audit import (
    delta_record, public_native_scores, evaluate_frozen,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev,LEARNED_SCALARS

class V34NativeLocalCreditTests(unittest.TestCase):
    def test_no_reward_learning_during_frozen_readout(self):
        for mode in ("shared","action_partition"):
            m=SharedContextRingDev(mode=mode)
            m.start_observation(PUBLIC_CUES[0])
            m.accept_first(ACTIONS[0])
            m.accept_second(ACTIONS[1],1.0)
            before=m.checkpoint()
            choices=public_native_scores(m)
            self.assertEqual(len(choices),12)
            self.assertTrue(all(len(x)==3 for x in choices))
            self.assertEqual(m.checkpoint(),before)
            self.assertEqual(LEARNED_SCALARS,163)
            self.assertEqual(SharedContextRingDev.restore(before).checkpoint(),before)

    def test_only_actual_selected_public_reward_updates(self):
        shared=SharedContextRingDev(mode="shared")
        partition=SharedContextRingDev(mode="action_partition")
        negative=SharedContextRingDev(mode="shared")
        initial=negative.parameters_sha256()
        for m in (shared,partition,negative):
            m.start_observation(PUBLIC_CUES[0])
            m.accept_first(ACTIONS[0])
        with self.assertRaises(TypeError):
            shared.accept_second(ACTIONS[1],1.0,unselected_outcomes=[0,0,0])
        shared.accept_second(ACTIONS[1],1.0)
        partition.accept_second(ACTIONS[1],1.0)
        negative.accept_second(ACTIONS[1],1.0,learning=False)
        self.assertEqual(negative.parameters_sha256(),initial)
        self.assertEqual(negative.updates,0)
        self.assertEqual(shared.updates,1)
        self.assertEqual(partition.updates,1)
        self.assertNotEqual(shared.parameters_sha256(),initial)

    def test_exact_33_cross_context_spillover_dimension(self):
        from research.itd02_v34_local_credit_spillover_audit import CONTEXTS
        start=[[0.,0.,0.] for _ in CONTEXTS]
        altered=[list(x) for x in start]
        altered[0][0]=0.5
        altered[0][1]=0.25
        altered[1][0]=1.0
        before={"predictions":{"v32_fast":start,"action_partition":start}}
        after={"predictions":{"v32_fast":altered,"action_partition":altered}}
        cue,first=CONTEXTS[0]
        result=delta_record(before,after,(cue,first,ACTIONS[0]))
        self.assertAlmostEqual(result["v32_fast"]["selected_action_prediction_delta"],0.5)
        self.assertEqual(result["v32_fast"]["same_context_other_action_deltas"],[0.25,0.0])
        self.assertEqual(result["v32_fast"]["other_context_abs_delta_sum"],1.0)
        self.assertGreater(result["v32_fast"]["spillover_ratio"],1.99)
        self.assertEqual(result["v32_fast"],result["action_partition"])

    def test_evaluator_only_regret_no_silent_learning(self):
        m=SharedContextRingDev(mode="shared")
        scores=public_native_scores(m)
        before=m.checkpoint()
        d=evaluate_frozen(scores,"U2")
        self.assertEqual(len(d["choices"]),12)
        self.assertGreaterEqual(d["regret"],0.0)
        self.assertEqual(m.checkpoint(),before)

if __name__=="__main__":
    unittest.main()
