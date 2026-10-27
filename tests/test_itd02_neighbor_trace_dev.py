"""Isolated v5 native neighbor-conditioned memory structural proof."""
import unittest
from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev,_temporal_public_bits,RING,SCHEMA
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS,ACTION_SITES,OBSERVATIONS,CELLS

class NeighborTraceTests(unittest.TestCase):
    def test_reward_site_traces_react_to_two_neighbor_bits(self):
        self.assertTrue(SCHEMA.endswith("source_only.v6"))
        self.assertEqual(CELLS,8)
        for site in ACTION_SITES:
            readings={}
            for obs in OBSERVATIONS:
                for action in ACTIONS:
                    m=NativeTaskRingBridgeDev()
                    m.start_observation(obs)
                    m.accept_public_transition(action,"Nothing",10,terminal=True)
                    expected=_temporal_public_bits(obs,action,0)
                    value=.125*(2*expected[RING[site][0]]-1)+.125*(2*expected[RING[site][1]]-1)
                    self.assertAlmostEqual(m.cell_trace[site],value)
                    readings[(obs,action)]=value
            self.assertGreater(len(set(readings.values())),1)
    def test_frozen_never_updates_neighbor_state(self):
        m=NativeTaskRingBridgeDev()
        m.start_observation("MRV")
        m.accept_public_transition("Backup","Nothing",10,terminal=True)
        ids=m.model_identities()
        frozen=list(m.cell_trace)
        m.start_frozen_evaluation(ids["native"],ids["memory"])
        m.start_observation("LRV")
        with self.assertRaisesRegex(ValueError,"FITTING_FORBIDDEN"):
            m.accept_public_transition("Backup","Nothing",10,learning=True)
        self.assertEqual(frozen,m.cell_trace)
        m.accept_public_transition("Backup","Nothing",10,learning=False,terminal=True)
        self.assertEqual(frozen,m.cell_trace)

if __name__=="__main__":unittest.main()
