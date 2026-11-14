"""MD30 frozen native tournament custody, contradictions, memory, negatives."""
import inspect
import json
import math
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bayesian_control import paid_training_episodes
from native_tournament import (COUNT, LOCK, CausalTournament, MODES,
                               PersistentCausalMemory, evidence_score,
                               trained_memory)
from native_tournament_preflight import ARMS, run_one
from structural_catalog import synthetic_world, TRANSFER_MOTIFS
from structural_rewire import canonical, digest


class NativeCausalTournamentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sessions, cls.receipt = paid_training_episodes()
        cls.hypotheses, cls.memory = trained_memory(cls.sessions, cls.receipt)

    def test_original_scope_and_frozen_preimplementation_lock(self):
        self.assertEqual(LOCK["source_parent_sha"],
                         "1c743ceea619ab1469be5eb511bf508d00275a6b")
        self.assertEqual(LOCK["status"],
                         "FROZEN_BEFORE_CANDIDATE_SOURCE__SYNTHETIC_DEVELOPMENT_ONLY")
        self.assertEqual(LOCK["train"]["phase_bank_keep"], 96)
        self.assertEqual(LOCK["online"]["winner_pool"], 32)
        self.assertEqual(LOCK["evaluation"]["fresh_synthetic_diagnostic_seeds"],
                         [6301, 6360])
        self.assertEqual(len(self.hypotheses), COUNT)
        self.assertEqual(self.receipt["charged_steps"], 1920)

    def test_credit_rule_distinguishes_fitting_and_contradicted_rules(self):
        self.assertEqual(evidence_score([1] * 6, [1] * 6), 6)
        self.assertEqual(evidence_score([0] * 6, [1] * 6), -12)
        self.assertEqual(evidence_score([1, 0, 0, 1, 0, 0],
                                        [1, 0, 0, 1, 1, 0]), 3)
        scores = self.memory.credits
        self.assertEqual(len(scores), 2)
        self.assertTrue(any(a != b for a, b in zip(*scores)))
        self.assertGreater(len(set(scores[0])), 2)
        self.assertGreater(len(set(scores[1])), 2)
        self.assertLessEqual(len(self.memory.global_recovery), 32)

    def test_checkpoint_byte_identical_without_retraining(self):
        chk = json.loads(canonical(self.memory.checkpoint()))
        restored = PersistentCausalMemory.from_checkpoint(
            self.hypotheses, chk)
        self.assertEqual(canonical(chk), canonical(restored.checkpoint()))
        self.assertEqual(self.memory.phase_banks, restored.phase_banks)
        bad = dict(chk, hypotheses_sha256="0" * 64)
        with self.assertRaisesRegex(AssertionError, "COLD_CUSTODY_DRIFT"):
            PersistentCausalMemory.from_checkpoint(self.hypotheses, bad)

    def test_public_paid_diagnostics_and_stage_change(self):
        for mode in MODES:
            world = synthetic_world(6301, "braided", rewire=True)
            learner = CausalTournament(self.hypotheses, self.memory, mode)
            paid = 0
            while True:
                before = world.observe()
                if before["phase"] == "done":
                    break
                action = learner.choose(before)
                self.assertIn(action["node"], before["diagnostic_nodes"]
                              if action["kind"] == "diagnostic" else (0, 1))
                with self.assertRaisesRegex(AssertionError,
                                            "REQUIRES_NEW_PAID_RECEIPT"):
                    learner.consume(before, action, before)
                after, _, done = world.step(action)
                learner.consume(before, action, after)
                paid += 1
                if done:
                    break
            self.assertEqual(learner.phase, 2)
            self.assertLessEqual(paid, 8)
            self.assertEqual(paid, world.receipt()["paid_steps"])
            self.assertLessEqual(sum(
                x["action"]["kind"] == "diagnostic"
                for x in world.receipt()["trace"]), 4)

    def test_cold_replay_same_episode_action_trace(self):
        checkpoint = json.loads(canonical(self.memory.checkpoint()))
        other = PersistentCausalMemory.from_checkpoint(
            self.hypotheses, checkpoint)
        for seed in (6301, 6302):
            before = run_one(seed, ARMS[0], self.hypotheses, self.memory, None)
            after = run_one(seed, ARMS[0], self.hypotheses, other, None)
            self.assertEqual(before, after)
            self.assertIn(before["motif"], TRANSFER_MOTIFS)

    def test_memorized_and_ablated_modes_isolated(self):
        learned = CausalTournament(self.hypotheses, self.memory, "persistent")
        stateless = CausalTournament(self.hypotheses, self.memory, "stateless")
        agnostic = CausalTournament(self.hypotheses, self.memory, "change_agnostic")
        self.assertLessEqual(len(learned.active), 128)
        self.assertEqual(len(stateless.active), COUNT)
        self.assertEqual(agnostic.memory.phase_banks[0],
                         learned.memory.phase_banks[0])
        self.assertNotEqual(learned._score(learned.winners()[0]), 0)
        self.assertEqual(stateless._score(0), 0)

    def test_no_hidden_graph_and_official_seed_first_use(self):
        source = inspect.getsource(CausalTournament)
        for forbidden in ("._graph", "._next_graph", "._roots",
                          "fixture_graph(", "synthetic_pair(",
                          "World.respond(", ".respond("):
            self.assertNotIn(forbidden, source)
        for seed in (1080001, 2080001, 3080001, 4080001):
            with self.assertRaisesRegex(AssertionError, "FIRST_USE_FORBIDDEN"):
                synthetic_world(seed, "braided", rewire=True)
        with self.assertRaisesRegex(AssertionError,
                                    "ONLY_FROZEN_SYNTHETIC_SEEDS"):
            run_one(4080001, ARMS[0], self.hypotheses, self.memory, None)


if __name__ == "__main__":
    unittest.main()
