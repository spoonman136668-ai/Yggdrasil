"""V35 native action-conditioned source-only safety and evaluation controls."""
import itertools
import unittest

from research.itd02_v35_action_conditioned_local_basis_audit import (
    WORLDS,MODES,reward_law,frozen_snapshot,make_model,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev,LEARNED_SCALARS
from yggdrasil.itd02_v35_action_conditioned_ring_dev import (
    LocalActionConditionedRingDev,BASIS_RULE,SCHEMA,
)

class V35LocalActionBasisTests(unittest.TestCase):
    def test_original_learning_count_and_immutable_parent(self):
        self.assertEqual(LEARNED_SCALARS,163)
        m=LocalActionConditionedRingDev()
        self.assertEqual(m.mode,"shared")
        self.assertEqual(m.updates,0)
        self.assertEqual(len(m.cell_weights),8)
        self.assertTrue(all(len(row)==20 for row in m.cell_weights))
        self.assertEqual(len(m.action_biases),3)
        self.assertIn("existing_original_four_hop_action_credit",BASIS_RULE)
        self.assertIn("action_conditioned",SCHEMA)

    def test_action_conditioned_features_differ_without_new_weights(self):
        m=LocalActionConditionedRingDev()
        m.start_observation(PUBLIC_CUES[0])
        m.accept_first(ACTIONS[1])
        first=m.checkpoint()
        m._output_action=ACTIONS[0]
        f0=m._features()
        m._output_action=ACTIONS[2]
        f2=m._features()
        m._output_action=None
        self.assertTrue(any(abs(f0[c][i]-f2[c][i])>1e-12
                            for c in range(8) for i in range(8,20)))
        self.assertEqual(first,m.checkpoint())
        for a in ACTIONS:
            self.assertIsInstance(m.score(a),float)
        m.accept_second(ACTIONS[2],2.0)
        self.assertEqual(m.updates,1)
        self.assertNotEqual(m.parameters_sha256(),
                            LocalActionConditionedRingDev().parameters_sha256())

    def test_integrity_restore_roundtrip_and_wrong_schema(self):
        m=LocalActionConditionedRingDev()
        m.start_observation(PUBLIC_CUES[1]);m.accept_first(ACTIONS[2])
        m.accept_second(ACTIONS[1],1.3)
        cp=m.checkpoint()
        self.assertLessEqual(len(cp),12288)
        self.assertEqual(LocalActionConditionedRingDev.restore(cp).checkpoint(),cp)
        with self.assertRaises(ValueError):
            LocalActionConditionedRingDev.restore(cp[:-1]+b'x')
        with self.assertRaises(ValueError):
            LocalActionConditionedRingDev.restore(SharedContextRingDev().checkpoint())
        # Reject direct original-native interpretation of V35 schema.
        with self.assertRaises(ValueError):
            SharedContextRingDev.restore(cp)

    def test_freeze_does_not_learn_and_no_world_privilege(self):
        m=LocalActionConditionedRingDev()
        cp=m.checkpoint()
        record=frozen_snapshot(m,"v35_novelty","D1")
        self.assertEqual(len(record["frozen_predictions"]),12)
        self.assertEqual(len(record["policy"]),12)
        self.assertEqual(m.checkpoint(),cp)
        m.start_frozen_evaluation()
        m.start_observation(PUBLIC_CUES[0]);m.accept_first(ACTIONS[0])
        with self.assertRaises(ValueError):
            m.accept_second(ACTIONS[0],2.0)
        with self.assertRaises(TypeError):
            m.accept_second(ACTIONS[0],2.0,world="D1")
        m.accept_second(ACTIONS[0],0.0,learning=False)
        self.assertEqual(m.updates,0)

    def test_worlds_predeclared_differ_and_no_oracle_to_learner(self):
        cases=list(itertools.product(PUBLIC_CUES,ACTIONS,ACTIONS))
        self.assertEqual(len(cases),36)
        maps=[tuple(reward_law(w,case) for case in cases) for w in WORLDS]
        self.assertEqual(len(set(maps)),3)
        self.assertTrue(all(-3.0<=y<=9.0 for values in maps for y in values))
        self.assertEqual(len(MODES),7)
        with self.assertRaises(ValueError):
            reward_law("D4",cases[0])

if __name__=="__main__":
    unittest.main()
