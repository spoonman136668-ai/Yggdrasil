"""V37 exact local margin-credit public-only, cold restore and nonlearning tests."""
import itertools
import unittest

from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES
from yggdrasil.itd02_v22_shared_context_ring_dev import (
    SharedContextRingDev,LEARNED_SCALARS,EDGE_SIGNAL_PER_PASS,
)
from yggdrasil.itd02_v37_public_pairwise_credit_dev import (
    PublicPairwiseCreditRingDev,SCHEMA,MARGIN,STEP_RATE,MAX_REWARD_GAP,
)
from research.itd02_v37_public_pairwise_credit_audit import (
    reward,snapshot,negative,WORLDS,MODES
)

class V37MarginCreditTests(unittest.TestCase):
    def test_only_original_163_weights_eight_original_cells_four_hop(self):
        m=PublicPairwiseCreditRingDev()
        self.assertEqual(LEARNED_SCALARS,163)
        self.assertEqual(len(m.cell_weights),8)
        self.assertTrue(all(len(row)==20 for row in m.cell_weights))
        self.assertEqual(len(m.action_biases),3)
        self.assertEqual((MARGIN,STEP_RATE,MAX_REWARD_GAP),(0.25,0.30,1.5))
        self.assertIn("pairwise",SCHEMA)

    def test_selected_reward_can_update_margin_with_rival_prediction_only(self):
        # With all scores tied at zero, take original ACTIONS[0], y=+3:
        # positive rule intentionally uses rival model prediction zero.
        m=PublicPairwiseCreditRingDev()
        m.start_observation(PUBLIC_CUES[0])
        m.accept_first(ACTIONS[1])
        m.accept_second(ACTIONS[0],3.0)
        self.assertEqual(m.updates,1)
        self.assertEqual(m.margin_updates,1)
        self.assertEqual(m.margin_edge_messages,EDGE_SIGNAL_PER_PASS)
        self.assertEqual(m.reverse_credit_messages,EDGE_SIGNAL_PER_PASS)
        cp=m.checkpoint()
        self.assertLessEqual(len(cp),12288)
        self.assertEqual(PublicPairwiseCreditRingDev.restore(cp).checkpoint(),cp)
        with self.assertRaises(ValueError):
            PublicPairwiseCreditRingDev.restore(cp[:-1]+b"X")
        with self.assertRaises(ValueError):
            PublicPairwiseCreditRingDev.restore(SharedContextRingDev().checkpoint())
        with self.assertRaises(ValueError):
            SharedContextRingDev.restore(cp)

    def test_negative_reward_and_no_learning(self):
        m=PublicPairwiseCreditRingDev()
        sha=m.parameters_sha256()
        m.start_observation(PUBLIC_CUES[1])
        m.accept_first(ACTIONS[1])
        m.accept_second(ACTIONS[1],-1.5,learning=False)
        self.assertEqual(m.parameters_sha256(),sha)
        self.assertEqual(m.margin_updates,0)
        self.assertEqual(m.updates,0)
        self.assertEqual(m.margin_edge_messages,0)
        # Fully cold negative control uses no extra model-facing family label.
        actual=[{"selected_public":[PUBLIC_CUES[0],ACTIONS[0],ACTIONS[0]],
                 "selected_reward":1.0}]*15
        self.assertTrue(negative(actual)["unchanged"])

    def test_frozen_clone_readout_and_full_reward_isolation(self):
        m=PublicPairwiseCreditRingDev()
        cp=m.checkpoint()
        results=snapshot(m,"v37_novelty","F2")
        self.assertEqual(len(results["scores"]),12)
        self.assertEqual(len(results["actions"]),12)
        self.assertEqual(m.checkpoint(),cp)
        m.start_frozen_evaluation()
        m.start_observation(PUBLIC_CUES[0]);m.accept_first(ACTIONS[0])
        with self.assertRaises(ValueError):
            m.accept_second(ACTIONS[0],2.0)
        with self.assertRaises(TypeError):
            m.accept_second(ACTIONS[0],2.0,world="F1")
        m.accept_second(ACTIONS[0],0.0,learning=False)
        self.assertEqual(m.updates,0)

    def test_frozen_three_world_tables_are_distinct(self):
        cases=list(itertools.product(PUBLIC_CUES,ACTIONS,ACTIONS))
        self.assertEqual(len(cases),36)
        matrices=[tuple(reward(w,x) for x in cases) for w in WORLDS]
        self.assertEqual(len(set(matrices)),3)
        self.assertTrue(all(-3<=y<=9 for matrix in matrices for y in matrix))
        self.assertEqual(len(MODES),7)
        with self.assertRaises(ValueError):
            reward("F4",cases[0])

if __name__=="__main__":
    unittest.main()
