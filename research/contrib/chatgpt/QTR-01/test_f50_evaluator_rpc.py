"""F50 private evaluator subprocess transport, synthetic fixtures only.

No real F50 development target seed, target AST, target outcomes, or source
checkpoint is accessed. A separate Python interpreter owns the synthetic law.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from hashlib import sha256

import f50_comparison_harness as harness
import f50_evaluator_rpc as rpc


class FixedFixtureArm:
    """Contract stub. NOT a trained source model or real native learner."""

    def __init__(self, pool):
        self.pool = pool
        self.used = []
        self.pending = None
        self.observed_bits = 0
        self.prediction_accesses = 0
        self.optimizer_steps = 0
        self.target_graph_available = False

    def select(self):
        if self.pending is not None:
            raise AssertionError("pending")
        self.pending = len(self.used)
        return self.pending, self.pool[self.pending]

    def observe(self, index, outcome):
        if index != self.pending or len(outcome) != 3:
            raise AssertionError("unauthorized")
        self.used.append(index)
        self.pending = None
        self.observed_bits += 3

    def probabilities(self, episodes):
        self.prediction_accesses += 3 * len(episodes)
        return tuple((0.5, 0.5, 0.5) for _ in episodes)

    def cold_checkpoint(self):
        body = json.dumps(
            {"used": self.used, "observed_bits": self.observed_bits},
            sort_keys=True, separators=(",", ":")).encode("ascii")
        return body + b"." + sha256(body).hexdigest().encode("ascii")

    @staticmethod
    def restore(packet):
        body, tag = packet.rsplit(b".", 1)
        if sha256(body).hexdigest().encode("ascii") != tag:
            raise AssertionError("bad fixture checkpoint")
        class Cold:
            def cold_checkpoint(self):
                return packet
        return Cold()


class F50IsolatedTransportTests(unittest.TestCase):
    def test_separate_interpreter_and_no_dev_mode_or_hidden_rpc_method(self):
        with self.assertRaisesRegex(rpc.TransportRejected, "FIRST_USE"):
            rpc.FixtureEvaluatorClient(mode="development")
        with rpc.FixtureEvaluatorClient() as oracle:
            self.assertNotEqual(oracle.worker_pid, os.getpid())
            self.assertTrue(oracle.public_receipt()["fixture_only"])
            self.assertFalse(hasattr(oracle, "target_ast"))
            self.assertFalse(hasattr(oracle, "target_law"))
            self.assertNotIn("PrivateTargetEvaluator", rpc.__dict__)
            with self.assertRaisesRegex(rpc.TransportRejected, "METHOD_BLOCKED"):
                oracle._rpc("target_ast", {})
            with self.assertRaisesRegex(rpc.TransportRejected, "METHOD_BLOCKED"):
                oracle._rpc("hidden_truth", {})
            self.assertEqual(oracle.public_receipt()["public_events_used"], 0)

    def test_fixture_public_fences_replay_and_sealed_scores_only(self):
        with rpc.FixtureEvaluatorClient() as oracle:
            pool = oracle.public_candidates()
            self.assertEqual(len(pool), 512)
            self.assertEqual(len(set(pool)), 512)
            with self.assertRaisesRegex(rpc.TransportRejected, "DENIED"):
                oracle.heldout_inputs_for_prediction()
            with self.assertRaisesRegex(rpc.TransportRejected, "DENIED"):
                oracle.public_event(1, pool[0])
            self.assertEqual(oracle.public_receipt()["public_events_used"], 0)
            for i in range(16):
                bits = oracle.public_event(i, pool[i])
                self.assertEqual(len(bits), 3)
                self.assertTrue(all(type(v) is int and v in (0, 1)
                                    for v in bits))
            with self.assertRaisesRegex(rpc.TransportRejected, "DENIED"):
                oracle.public_event(0, pool[0])
            heldout = oracle.heldout_inputs_for_prediction()
            self.assertEqual(len(heldout), 512)
            self.assertFalse(set(pool) & set(heldout))
            score = oracle.score_once([(0.5, 0.5, 0.5)] * 512)
            self.assertEqual(score["query_budget"], 16)
            self.assertEqual(score["scored_clean_bits"], 1536)
            self.assertTrue(score["fixture_only"])
            self.assertFalse(score["scientific_pass"])
            self.assertFalse(score["target_law_disclosed"])
            with self.assertRaisesRegex(rpc.TransportRejected, "DENIED"):
                oracle.score_once([(0.5, 0.5, 0.5)] * 512)
            with self.assertRaisesRegex(rpc.TransportRejected, "DENIED"):
                oracle.heldout_inputs_for_prediction()
            self.assertEqual(oracle.public_receipt()["scored_checkpoints"], [16])
            self.assertEqual(oracle.public_receipt()["protected_cohorts_consumed"], 0)

    def test_full_64_query_harness_with_real_cross_process_feedback(self):
        with rpc.FixtureEvaluatorClient() as oracle:
            stub = FixedFixtureArm(oracle.public_candidates())
            result = harness.run_fixture_arm(
                4096, 4013, "uniform", stub, oracle, FixedFixtureArm.restore)
            self.assertEqual([p["budget"] for p in result["checkpoints"]],
                             [16, 32, 64])
            self.assertEqual(result["observed_public_bits"], 192)
            self.assertEqual(result["public_events"], 64)
            self.assertEqual(result["cold_restores"], 3)
            self.assertEqual(result["proposals"], 0)
            self.assertTrue(result["fixture_only"])
            self.assertFalse(result["scientific_pass"])
            self.assertEqual(result["classification"],
                             harness.FIXTURE_CLASSIFICATION)
            receipt = oracle.public_receipt()
            self.assertEqual(receipt["public_events_used"], 64)
            self.assertEqual(receipt["scored_checkpoints"], [16, 32, 64])

    def test_non_fixture_worker_mode_fails_without_creating_dev_world(self):
        invocation = subprocess.run(
            [sys.executable, str(Path(rpc.__file__).resolve()), "--development"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            timeout=20, check=False)
        self.assertNotEqual(invocation.returncode, 0)
        self.assertEqual(invocation.stdout, "")
        self.assertIn("NO_DEV_FIRST_USE", invocation.stderr)
        self.assertNotIn("target_ast", invocation.stderr)
        self.assertNotIn("target_law", invocation.stderr)


if __name__ == "__main__":
    unittest.main()
