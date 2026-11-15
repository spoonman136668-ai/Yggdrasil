"""F50 Bayesian arms: synthetic public actions only; no development target use."""
import json
from hashlib import sha256
import unittest
from unittest.mock import patch

import f50_bayesian_controls as b
import f50_public_corpus as p
import f50_worlds as w


class F50BayesianSourceOnlyTests(unittest.TestCase):
    def test_contract_source_parity_and_protected_fences(self):
        self.assertEqual(b.KINDS, ("exact_source_bank_bayes",
                                    "compositional_grammar_bayes"))
        self.assertEqual(b.PROPOSALS, 2048)
        self.assertEqual(b.MAX_QUERIES, 64)
        for seed in (4127, 4159, 163, 167, 173, True):
            with self.assertRaises(w.F50Rejected):
                b.BayesianPublicArm(1024, seed, b.KINDS[0])
        with self.assertRaises(b.BayesianRejected):
            b.BayesianPublicArm(1024, 4013, "oracle")
        self.assertNotIn("target_ast", b.__dict__)
        self.assertNotIn("sealed_heldout_inputs_for_evaluator_only", b.__dict__)
        with patch.object(w, "sealed_heldout_inputs_for_evaluator_only",
                          side_effect=AssertionError("sealed target accessed")):
            a = b.BayesianPublicArm(1024, 4013, b.KINDS[0])
            c = b.BayesianPublicArm(1024, 4013, b.KINDS[1])
            self.assertEqual(p.assert_equal_source_access(a.corpus, c.corpus),
                             a.source_graph_sha)
            self.assertEqual(len(a.rules), a.corpus.fit_count)
            self.assertEqual(len(c.rules), 64)
            self.assertEqual(a.observed_bits, 0)
            self.assertFalse(a.target_graph_available)
            self.assertFalse(c.target_graph_available)

    def test_synthetic_feedback_cold_and_no_target_access(self):
        for kind in b.KINDS:
            with self.subTest(kind=kind):
                with patch.object(w, "sealed_heldout_inputs_for_evaluator_only",
                                  side_effect=AssertionError("sealed target accessed")):
                    arm = b.BayesianPublicArm(1024, 4013, kind)
                    i, episode = arm.select()
                    with self.assertRaises(b.BayesianRejected):
                        arm.select()
                    with self.assertRaises(b.BayesianRejected):
                        arm.observe((i + 1) % 512, (1, 0, 1))
                    with self.assertRaises(p.PublicSourceRejected):
                        arm.observe(i, (True, 0, 1))
                    arm.observe(i, (1, 0, 1))  # Synthetic fixture, NOT a target law.
                    self.assertEqual(arm.observed_bits, 3)
                    self.assertEqual(arm.optimizer_steps, 0)
                    self.assertEqual(arm.proposals, 0 if kind == b.KINDS[0] else 2048)
                    self.assertTrue(all(0.1 - 1e-9 <= x <= 0.9 + 1e-9
                                        for x in arm.probability(episode)))
                    packet = arm.cold_checkpoint()
                    restored = b.BayesianPublicArm.restore(packet)
                    self.assertEqual(restored.cold_checkpoint(), packet)
                    self.assertEqual(restored.probability(episode), arm.probability(episode))
                    with self.assertRaises(b.BayesianRejected):
                        b.BayesianPublicArm.restore(packet[:-1] + bytes([packet[-1] ^ 1]))
                    body, _ = packet.rsplit(b".", 1)
                    forged = json.loads(body)
                    forged["source_graph_sha"] = "f" * 64
                    raw = json.dumps(forged, sort_keys=True,
                                     separators=(",", ":")).encode("ascii")
                    with self.assertRaises(b.BayesianRejected):
                        b.BayesianPublicArm.restore(
                            raw + b"." + sha256(raw).hexdigest().encode("ascii"))


if __name__ == "__main__":
    unittest.main()
