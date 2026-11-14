"""DG1-MD31 safe fixture-only negative controls (never scoring seeds)."""
import inspect
import json
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "dg1-md30-20261114"))
from bayesian_control import paid_training_episodes
from native_tournament import PersistentCausalMemory, trained_memory
from structural_catalog import synthetic_world
from structural_rewire import canonical, digest
from change_ledger import PaidChangeLedger, PREREG
from paired_preflight import (ARMS, PREFLIGHT, SEEDS, MODES,
                              identifiability_preflight, paired_bootstrap_lower,
                              run_episode)


class MD31PaidChangeLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sessions, cls.custody = paid_training_episodes()
        cls.hypotheses, cls.memory = trained_memory(cls.sessions, cls.custody)

    @staticmethod
    def fixture_episode(hypotheses, memory, mode="evidence"):
        world = synthetic_world(7301, "braided", rewire=True)
        policy = PaidChangeLedger(hypotheses, memory, mode)
        actions = 0
        while True:
            before = world.observe()
            if before["phase"] == "done":
                break
            action = policy.choose(before)
            after, _, done = world.step(action)
            policy.consume(before, action, after)
            actions += 1
            if done:
                break
        return world.receipt(), policy.audit()

    def test_separate_frozen_source_and_never_used_scoring_cohort(self):
        self.assertEqual(
            PREREG["scope"]["frozen_parent_sha"],
            "70a8e6de35d255ecf834a4ce8ee97650d54f32c7")
        self.assertEqual(PREREG["status"],
                         "FROZEN_PREREG_ONLY_NO_NEW_SOURCE_NO_OUTCOME")
        self.assertEqual((PREFLIGHT[0], PREFLIGHT[-1]), (7301, 7312))
        self.assertEqual((SEEDS[0], SEEDS[-1]), (8301, 8420))
        self.assertEqual(len(SEEDS), 120)
        self.assertTrue(set(PREFLIGHT).isdisjoint(SEEDS))
        self.assertEqual(self.custody["charged_steps"], 1920)
        self.assertEqual(len(self.hypotheses), 768)

    def test_actual_paid_identifying_interventions_no_change_flag(self):
        proof = identifiability_preflight()
        self.assertEqual(proof["fixture_cases"], 12)
        self.assertTrue(proof["all_initial_stage1_public_observations_identical"])
        self.assertTrue(proof["all_paid_internal_diagnostics_distinguish"])
        self.assertEqual(len(proof["preflight_sha256"]), 64)

    def test_gate_changes_memory_only_after_charged_stage_one_receipt(self):
        world = synthetic_world(7301, "braided", rewire=True)
        policy = PaidChangeLedger(self.hypotheses, self.memory)
        while world.observe()["phase"] == 0:
            before = world.observe()
            action = policy.choose(before)
            after, _, _ = world.step(action)
            policy.consume(before, action, after)
        before = world.observe()
        self.assertEqual(before["phase"], 1)
        probe = policy.choose(before)
        self.assertEqual(probe["kind"], "diagnostic")
        self.assertIn(probe["node"], (2, 3, 4))
        with self.assertRaisesRegex(AssertionError,
                                    "GATE_REQUIRES_PAID_PUBLIC_RECEIPT"):
            policy.consume(before, probe, before)
        after, reward, _ = world.step(probe)
        self.assertEqual(reward, -0.05)
        policy.consume(before, probe, after)
        self.assertEqual(policy.paid_gate_count, 1)
        self.assertEqual(policy.parent.paid_actions, len(after["charged_history"]))
        self.assertIn(policy.audit()["bank_decision"], ("stage0", "stage1"))
        self.assertEqual(policy.audit()["phase1_paid_probe"],
                         [probe["node"], probe["value"]])

    def test_same_paid_probe_all_gate_ablations_and_action_caps(self):
        cases = [self.fixture_episode(self.hypotheses, self.memory, mode)
                 for mode in MODES.values()]
        probes = [result["phase1_paid_probe"] for _, result in cases]
        self.assertEqual(probes[0], probes[1])
        self.assertEqual(probes[0], probes[2])
        self.assertEqual(cases[1][1]["bank_decision"], "stage1")
        self.assertEqual(cases[2][1]["bank_decision"], "stage0")
        for receipt, audit in cases:
            self.assertLessEqual(receipt["paid_steps"], 8)
            self.assertEqual(audit["charged_parent_actions"], receipt["paid_steps"])
            self.assertEqual(
                sum(row["action"]["kind"] == "actuator"
                    for row in receipt["trace"]), 2)
            self.assertGreaterEqual(
                sum(row["action"]["kind"] == "diagnostic"
                    for row in receipt["trace"]), 1)

    def test_cold_memory_rehydration_exact_physical_replay(self):
        checkpoint = json.loads(canonical(self.memory.checkpoint()))
        restored = PersistentCausalMemory.from_checkpoint(
            self.hypotheses, checkpoint)
        a = self.fixture_episode(self.hypotheses, self.memory, "evidence")
        b = self.fixture_episode(self.hypotheses, restored, "evidence")
        self.assertEqual(a, b)
        self.assertEqual(digest(checkpoint), digest(restored.checkpoint()))

    def test_frozen_software_never_gets_hidden_graph_or_event_label(self):
        source = inspect.getsource(PaidChangeLedger)
        for prohibited in ("._graph", "._next_graph", "._roots",
                           "synthetic_pair(", "world.step(",
                           ".respond(", "seed", "rewire"):
            self.assertNotIn(prohibited, source)
        self.assertEqual(len(ARMS), 6)
        for seed in (1080001, 2080001, 3080001, 4080001, 1070001,
                     5301, 6301, 7301, 8421):
            with self.assertRaisesRegex(AssertionError,
                                        "UNAUTHORIZED_OR_REUSED_SCIENCE_SEED"):
                run_episode(seed, "evidence_gate", None, None, None)

    def test_frozen_paired_bootstrap_is_deterministic(self):
        self.assertEqual(paired_bootstrap_lower([1] * 120), 1.0)
        self.assertEqual(paired_bootstrap_lower([-0.5] * 120), -0.5)
        with self.assertRaisesRegex(AssertionError, "BAD_PAIRED_BOOTSTRAP_COUNT"):
            paired_bootstrap_lower([0.1] * 119)


if __name__ == "__main__":
    unittest.main()
