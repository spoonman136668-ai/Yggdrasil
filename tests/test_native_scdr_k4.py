"""Actual native K4 H1 defect repair: source, gauge, negative and cold tests."""
import itertools
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from test_native_causal_witness import train

EDGES=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))


def observe(m,slot,rows,ref="d"):
    return m.observe(slot,rows,digest(canonical(rows)),source_ref=ref*64)


def reported(vertices,flipped=()):
    return [[k,1,vertices[u]^vertices[v]^(k in flipped)]
            for k,(u,v) in enumerate(EDGES)]


class NativeK4SheafRepairTests(unittest.TestCase):
    def test_K4_rank_and_all_six_single_faults_persistent_source_cold(self):
        _,root=train()
        snap=root.checkpoint()
        compiled=[root._compiled[s].checkpoint() for s in (1,2,3)]
        for vertices in itertools.product((0,1),repeat=4):
            clean=[row[2] for row in reported(vertices)]
            for index in range(6):
                learner=observe(root,12,reported(vertices,(index,)))
                first=learner.scdr_k4_defect_repair()
                self.assertEqual(first["d0_rank"],3)
                self.assertEqual(first["h1_dimension"],3)
                self.assertEqual(first["status"],"UNVALIDATED_DEFECT")
                self.assertEqual(first["suspect_edge"],list(EDGES[index]))
                before=learner.checkpoint()
                anchors=[[v,0,vertices[v]] for v in EDGES[index]]
                learner=observe(learner,13,anchors,"e")
                decision=learner.scdr_k4_defect_repair()
                self.assertEqual(decision["status"],"SOURCE_WITNESSED_CORRECTION")
                self.assertTrue(decision["repair_certified"])
                self.assertEqual(decision["repaired_edge_bits"],clean)
                self.assertEqual(decision["observed_edge_bits"][index],1-clean[index])
                self.assertEqual([learner._compiled[k].checkpoint() for k in (1,2,3)],compiled)
                self.assertEqual(learner._source._seen[0],root._source._seen[0])
                cold_raw=learner.checkpoint()
                cold=NativeCumulativeLearner.restore(cold_raw,digest(cold_raw))
                self.assertEqual(cold.scdr_k4_defect_repair(),decision)
                self.assertEqual(cold.checkpoint(),cold_raw)
                self.assertEqual(root.checkpoint(),snap)
                self.assertNotEqual(before,cold_raw)

    def test_clean_world_never_mints_latent_or_corrected_outcome(self):
        _,root=train()
        for vertices in ((0,0,0,0),(1,0,1,0),(1,1,1,1)):
            learner=observe(root,12,reported(vertices))
            p=learner.scdr_k4_defect_repair()
            self.assertEqual(p["syndrome"],[0,0,0])
            self.assertEqual(p["status"],"NO_DEFECT")
            self.assertIsNone(p["suspect_edge"])
            self.assertFalse(p["repair_certified"])
            self.assertEqual(p["observed_edge_bits"],p["repaired_edge_bits"])
            learner=observe(learner,13,[[0,0,vertices[0]],[1,0,vertices[1]]],"a")
            self.assertEqual(learner.scdr_k4_defect_repair()["status"],"NO_DEFECT")

    def test_two_faults_which_alias_one_are_rejected_by_real_anchors(self):
        _,root=train()
        vertices=(0,1,0,1)
        learner=observe(root,12,reported(vertices,(0,1)))
        p=learner.scdr_k4_defect_repair()
        self.assertEqual(p["suspect_edge"],[1,2])
        learner=observe(learner,13,[[1,0,vertices[1]],[2,0,vertices[2]]])
        p=learner.scdr_k4_defect_repair()
        self.assertEqual(p["status"],"REJECTED_BY_ANCHORS")
        self.assertFalse(p["repair_certified"])
        self.assertEqual(p["repaired_edge_bits"],p["observed_edge_bits"])

    def test_two_disjoint_faults_nonlocalizable(self):
        _,root=train()
        vertices=(0,0,1,1)
        learner=observe(root,12,reported(vertices,(0,5)))
        p=learner.scdr_k4_defect_repair()
        self.assertEqual(p["syndrome"],[1,1,1])
        self.assertEqual(p["status"],"NONLOCALIZABLE")
        self.assertFalse(p["repair_certified"])

    def test_wrong_anchors_and_unproven_edges_fail_closed(self):
        _,root=train()
        before=root.checkpoint()
        with self.assertRaises(ValueError):
            root.scdr_k4_defect_repair()
        vertices=(0,0,1,1)
        learner=observe(root,12,reported(vertices,(4,)))
        query=learner.scdr_k4_defect_repair()
        self.assertEqual(query["proposed_vertex_actions"],[[1,0],[3,0]])
        wrong=observe(learner,13,[[0,0,vertices[0]],[2,0,vertices[2]]])
        with self.assertRaises(ValueError):
            wrong.scdr_k4_defect_repair()
        self.assertEqual(root.checkpoint(),before)

    def test_independent_global_gauge_does_not_change_syndrome(self):
        _,root=train()
        for vertices in ((0,0,0,0),(1,1,1,1)):
            m=observe(root,12,reported(vertices,(2,)))
            self.assertEqual(m.scdr_k4_defect_repair()["syndrome"],[0,1,1])


if __name__=="__main__":
    unittest.main()
