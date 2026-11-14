"""MD30 frozen structural-composition PRE-FIRST-USE negative controls."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from structural_catalog import (
    DIAGNOSTIC_NODES, SYNTHETIC_SEEDS, TOPOLOGIES,
    TRAIN_MOTIFS, TRANSFER_MOTIFS, _distinguishing_probes,
    preflight_distribution, synthetic_pair, synthetic_world, topology_manifest,
)
from structural_rewire import canonical, reference_enumerate


class MD30StructuralDistribution(unittest.TestCase):
    def test_source_locked_train_transfer_topology_hashes(self):
        audit = topology_manifest()
        self.assertEqual(audit["train"], ["chain", "fork", "collider"])
        self.assertEqual(audit["transfer"],
                         ["braided", "crossfork", "doublecollider"])
        self.assertEqual(
            audit["all_structure_sha256"],
            "24696dddb4c7e0b5f100112eb67c715ac981efe053d5dbe91f3785e36d1119ac",
        )
        self.assertEqual(len(set(audit["topology_sha256"].values())), 6)
        self.assertEqual(set(TRAIN_MOTIFS) & set(TRANSFER_MOTIFS), set())
        self.assertEqual(len(TOPOLOGIES), 6)

    def test_only_synthetic_fixture_seeds_can_construct_world(self):
        for seed in (1080001, 1080768, 2080001, 2080128,
                     3080001, 3080064, 4080001, 4080256, 1070001):
            with self.assertRaisesRegex(AssertionError, "FIRST_USE_FORBIDDEN"):
                synthetic_pair(seed, "braided")
        for bad in (True, "1201", -1, 1000000):
            with self.assertRaises(Exception):
                synthetic_pair(bad, "chain")
        with self.assertRaises(ValueError):
            synthetic_pair(1201, "not-a-motif")

    def test_all_synthetic_pairs_physically_real_and_internally_identifiable(self):
        for motif in TRAIN_MOTIFS + TRANSFER_MOTIFS:
            for seed in SYNTHETIC_SEEDS:
                first, second = synthetic_pair(seed, motif)
                self.assertNotEqual(first.fingerprint(), second.fingerprint())
                self.assertNotEqual(tuple(n.parents for n in first.nodes),
                                    tuple(n.parents for n in second.nodes))
                self.assertTrue(any(a.gate != b.gate for a, b
                                    in zip(first.nodes, second.nodes)))
                self.assertEqual(first.respond((0, 0)), second.respond((0, 0)))
                self.assertEqual(first.respond((0, 0)), (0,) * 6)
                self.assertTrue(_distinguishing_probes(first, second))
                for graph in (first, second):
                    for roots in ((0, 0), (1, 0), (0, 1)):
                        self.assertEqual(graph.respond(roots),
                                         reference_enumerate(graph, roots))

    def test_no_root_actuator_preview_in_transfer_public_menu(self):
        world = synthetic_world(1201, "braided", rewire=True)
        baseline = world.observe()
        self.assertEqual(baseline["diagnostic_nodes"], [2, 3, 4])
        self.assertNotIn("motif", canonical(baseline))
        self.assertNotIn("graph", canonical(baseline))
        self.assertNotIn("seed", canonical(baseline))
        for root in (0, 1):
            with self.assertRaisesRegex(AssertionError, "DIAGNOSTIC_CAP_OR_NODE"):
                world.step({"kind": "diagnostic", "node": root, "value": 1})
            self.assertEqual(world.observe(), baseline)

    def test_paid_internal_probe_and_structural_rewire_custody(self):
        for motif in TRANSFER_MOTIFS:
            first, second = synthetic_pair(1201, motif)
            diagnostic = _distinguishing_probes(first, second)[0]
            world = synthetic_world(1201, motif, rewire=True)
            initial = world.observe()
            self.assertEqual(initial["sensor_vector"], [0] * 6)
            _, r1, done = world.step({"kind": "actuator", "node": 0, "value": 0})
            self.assertFalse(done)
            self.assertEqual(r1, -0.52)
            self.assertEqual(world.observe()["sensor_vector"], [0] * 6)
            next_obs, probe_reward, _ = world.step(
                {"kind": "diagnostic", "node": diagnostic[0], "value": diagnostic[1]})
            self.assertEqual(probe_reward, -0.05)
            self.assertEqual(next_obs["sensor_vector"],
                             list(second.respond((0, 0), diagnostic)))
            self.assertNotEqual(next_obs["sensor_vector"],
                                list(first.respond((0, 0), diagnostic)))
            _, _, done = world.step({"kind": "actuator", "node": 0, "value": 0})
            self.assertTrue(done)
            receipt = world.receipt()
            self.assertEqual(receipt["paid_steps"], 3)
            self.assertEqual([row["action"]["kind"] for row in receipt["trace"]],
                             ["actuator", "diagnostic", "actuator"])

    def test_exact_cold_replay_no_learning(self):
        for motif in TRANSFER_MOTIFS:
            sha = []
            for _ in range(2):
                world = synthetic_world(1248, motif, rewire=True)
                world.step({"kind": "diagnostic", "node": 2, "value": 1})
                world.step({"kind": "actuator", "node": 0, "value": 1})
                world.step({"kind": "diagnostic", "node": 3, "value": 1})
                world.step({"kind": "actuator", "node": 1, "value": 1})
                sha.append(world.receipt()["physical_sha256"])
            self.assertEqual(sha[0], sha[1])

    def test_distribution_headroom_gate_not_policy_score(self):
        result = preflight_distribution()
        self.assertFalse(result["registered_first_use"])
        self.assertEqual(result["seed_range"], [1201, 1248])
        for motif in TRAIN_MOTIFS + TRANSFER_MOTIFS:
            audit = result["motifs"][motif]
            self.assertEqual(audit["synthetic_pairs"], 48)
            self.assertGreaterEqual(audit["distinct_hidden_graphs"], 8)
            self.assertGreaterEqual(audit["distinct_first_internal_probes"], 2)
            self.assertGreaterEqual(audit["oracle_blind_utility_headroom"], 0.35)
            self.assertEqual(audit["actuator_a_wins"] + audit["actuator_b_wins"], 48)


if __name__ == "__main__":
    unittest.main()
