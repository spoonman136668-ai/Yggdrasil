"""Learned information-seeking probes: selection, coverage and negatives."""
import unittest
from causal_probe_planner import CausalProbePlanner
from selected_causal_probe_audit import run
from two_hop_evidence_audit import build

class LearnedProbePlannerTests(unittest.TestCase):
    def test_selects_independent_public_chains_and_disregards_distractors(self):
        agent = build()
        starts = [(b"uQ-unrelated", (0, 1)),
                  (b"xB-training", (0, 1)),
                  (b"xA-training", (0, 1))]
        pair = CausalProbePlanner().select_pair(
            agent.active_links, agent.archived_links, starts)
        self.assertIsNotNone(pair)
        self.assertEqual({p[0][0] for p in pair},
                         {b"xA-training", b"xB-training"})
        self.assertTrue(all(agent.active_links[first] ==
                            agent.archived_links[first] == middle
                            for first, middle, second in pair))
        self.assertTrue(all(agent.active_links[second] !=
                            agent.archived_links[second]
                            for first, middle, second in pair))

    def test_clean_environments_and_permutation(self):
        data = run()
        for name, expected in (("A_return", "snapshot"),
                               ("B_continues", "active"),
                               ("permuted_start_order", "snapshot")):
            row = data[name]
            self.assertTrue(row["admitted"])
            self.assertEqual(row["selected"], expected)
            self.assertEqual(row["physical_interventions"], 4)
            self.assertEqual(row["two_action_probes"], 2)
            self.assertLessEqual(row["stored_fit_examples"], 256)
        self.assertEqual(data["A_return"]["chosen_first_frames"],
                         data["permuted_start_order"]["chosen_first_frames"])

    def test_correlated_sensor_failure_is_not_concealed(self):
        row = run()["A_with_corrupted_successors"]
        self.assertTrue(row["admitted"])
        self.assertNotEqual(row["selected"], row["expected"])

    def test_no_disagreement_abstains(self):
        agent = build()
        planner = CausalProbePlanner()
        self.assertIsNone(planner.select_pair(
            agent.archived_links, agent.archived_links,
            [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]))
        with self.assertRaises(ValueError):
            CausalProbePlanner(max_candidates=1)

    def test_audit_determinism(self):
        self.assertEqual(run(), run())

if __name__ == "__main__":
    unittest.main()
