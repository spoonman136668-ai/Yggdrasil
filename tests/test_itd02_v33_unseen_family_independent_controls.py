"""V33 prospective independently choosing controls and frozen toy-law invariants."""
import itertools
import unittest

from research.itd02_v33_unseen_family_independent_controls_audit import (
    WORLDS,MODES,law,clone_policy,assess,chooser_for,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v32_source_surprise_probation_dev import SourceSurpriseProbationDev


class V33HeldoutControlTests(unittest.TestCase):
    def test_new_evaluator_laws_have_distinct_fixed_truth_tables(self):
        all_cases=list(itertools.product(PUBLIC_CUES,ACTIONS,ACTIONS))
        self.assertEqual(len(all_cases),36)
        mats=[]
        for world in WORLDS:
            values=[law(world,c) for c in all_cases]
            self.assertEqual(len(values),36)
            self.assertTrue(all(-3.0<=y<=10.0 for y in values))
            mats.append(tuple(values))
        self.assertEqual(len(set(mats)),4)
        with self.assertRaises(ValueError):
            law("private_future_world",all_cases[0])

    def test_independent_chooser_modes_and_public_inputs_only(self):
        self.assertEqual(len(MODES),7)
        for mode in MODES:
            p=chooser_for(mode)
            self.assertEqual(p.events,0)
            p.observe_selected(PUBLIC_CUES[0],ACTIONS[0],ACTIONS[1])
            chosen=p.select(PUBLIC_CUES[0],ACTIONS[0],[1.0,2.0,3.0])
            self.assertIn(chosen,ACTIONS)
            with self.assertRaises(TypeError):
                p.select(PUBLIC_CUES[0],ACTIONS[0],[1,2,3],world="U2")
        r=chooser_for("v32_random")
        s=chooser_for("v32_random")
        self.assertEqual(
            [r.select(PUBLIC_CUES[0],ACTIONS[0],[0,0,0]) for _ in range(8)],
            [s.select(PUBLIC_CUES[0],ACTIONS[0],[0,0,0]) for _ in range(8)])

    def test_source_snapshot_cannot_leak_unselected_reward_to_live(self):
        original=SharedContextRingDev(mode="shared")
        original.start_observation(PUBLIC_CUES[0])
        original.accept_first(ACTIONS[0])
        original.accept_second(ACTIONS[2],0.8)
        m=SourceSurpriseProbationDev(original.checkpoint())
        cp=m.checkpoint()
        choices=clone_policy(m,"v32_novelty")
        self.assertEqual(len(choices),12)
        self.assertEqual(len(assess("U1",choices)["detail"]),12)
        self.assertEqual(m.checkpoint(),cp)
        self.assertEqual(m.bank.slow.parameters_sha256(),m.bank.source_sha)


if __name__=="__main__":
    unittest.main()
