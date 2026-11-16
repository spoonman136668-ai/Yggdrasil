"""F50 evaluator-only source gate; synthetic fixtures, never a DEV target law."""
import unittest
from unittest.mock import patch

import f50_target_evaluator as target
import f50_worlds as world


def fixture_law():
    a, b, c = (world.leaf(i) for i in (0, 1, 2))
    ctx = world.leaf(30)
    lag1 = world.leaf(10)
    lag2 = world.leaf(22)
    core = ("and", ctx, ("and", ("and", a, b), lag2))
    return ("xor", core, ("and", ("not", ctx), ("xor", c, lag1)))


def fixture_inputs(count, offset=0):
    seen = set()
    output = []
    for i in range(offset, offset + count):
        for nonce in range(128):
            episode = world._trajectory("F50/synthetic-evaluator-test-only/v1",
                                        1024, 99991, 0, i, nonce)
            if episode is not None and episode not in seen:
                seen.add(episode)
                output.append(episode)
                break
        else:
            raise AssertionError("synthetic input generation exhausted")
    return tuple(output)


class F50SealedTargetTests(unittest.TestCase):
    def test_frozen_contract_and_no_development_first_use_on_import(self):
        self.assertEqual(target.FROZEN_PREREG_BLOB, world.PREREG_BLOB)
        self.assertEqual(tuple(target.FAMILY), world.DEV_SEEDS)
        self.assertEqual(target.CHECKPOINTS, (16, 32, 64))
        self.assertFalse(hasattr(world, "target_ast"))
        self.assertFalse(hasattr(world, "target_law"))
        with patch.object(target, "_development_law",
                          side_effect=AssertionError("DEV LAW FIRST USE")):
            with self.assertRaisesRegex(target.TargetAdmissionRejected,
                                        "FIRST_USE_BLOCKED"):
                target.PrivateTargetEvaluator.open_development(1024, 4013)
            for seed in (4127, 4159, 163, 167, 173, True):
                with self.assertRaises(world.F50Rejected):
                    target.PrivateTargetEvaluator.open_development(
                        1024, seed, externally_verified_release={})
        self.assertEqual(target._check_release.__name__, "_check_release")
        with self.assertRaises(target.TargetAdmissionRejected):
            target._check_release({"candidate_sha": "0" * 40, "ubuntu_pass": True,
                                   "windows_pass": True, "protocol_blob":
                                   target.FROZEN_PREREG_BLOB,
                                   "operator_first_use": False})

    def test_full_domain_exact_novelty_and_true_intervention_witness(self):
        rule = fixture_law()
        proof = target._admit_exact(1024, rule)
        self.assertTrue(proof["full_domain_exact_nonmembership"])
        self.assertTrue(proof["high_order_context_lag_interaction"])
        self.assertTrue(proof["has_context_contrast"])
        self.assertTrue(proof["has_lagged_contrast"])
        self.assertGreaterEqual(proof["distinct_action_identities"], 3)
        self.assertEqual(proof["target_outcomes_consumed"], 0)
        terms = world.anf(rule)
        for variable in world.dependencies(rule):
            self.assertTrue(target._derivative(terms, variable))
        source = next(x for x in world.source_bank(1024)
                      if world.ast_depth(x) == 2)
        with self.assertRaisesRegex(target.TargetAdmissionRejected,
                                    "EXACT_SOURCE_COLLISION"):
            target._admit_exact(1024, ("not", ("not", source)))
        unconnected = ("not", ("not",
                         ("xor", ("and", world.leaf(30),
                                  ("and", world.leaf(0), world.leaf(20))),
                          ("and", ("not", world.leaf(30)),
                           ("xor", world.leaf(1), world.leaf(2))))))
        with self.assertRaisesRegex(target.TargetAdmissionRejected,
                                    "NO_HIGH_ORDER_COMPOSITION"):
            target._admit_exact(1024, unconnected)
        with self.assertRaisesRegex(target.TargetAdmissionRejected,
                                    "DEPTH_OUT_OF_CONTRACT"):
            target._admit_exact(1024, world.leaf(0))

    def test_fixture_only_no_replay_no_oracle_and_single_aggregate_scoring(self):
        public = fixture_inputs(20)
        heldout = fixture_inputs(7, offset=100)
        with patch.object(target, "_development_law",
                          side_effect=AssertionError("DEV LAW FIRST USE")):
            evaluator = target.PrivateTargetEvaluator.synthetic_fixture(
                1024, fixture_law(), public, heldout)
            self.assertEqual(evaluator.public_candidates(), public)
            self.assertEqual(evaluator.heldout_inputs_for_prediction(), heldout)
            with self.assertRaises(target.TargetAdmissionRejected):
                evaluator.score_once([(0.5, 0.5, 0.5)] * len(heldout))
            for i in range(16):
                bits = evaluator.public_event(i, public[i])
                self.assertEqual(len(bits), 3)
                self.assertTrue(all(x in (0, 1) for x in bits))
                with self.assertRaises(target.TargetAdmissionRejected):
                    evaluator.public_event(i, public[i])
            self.assertEqual(evaluator.public_receipt()["observed_public_bits"], 48)
            with self.assertRaisesRegex(target.TargetAdmissionRejected,
                                        "PROBABILITIES_INVALID"):
                evaluator.score_once([(float("nan"), 0.5, 0.5)] +
                                     [(0.5, 0.5, 0.5)] * (len(heldout) - 1))
            score = evaluator.score_once([(0.5, 0.5, 0.5)] * len(heldout))
            self.assertEqual(score["query_budget"], 16)
            self.assertTrue(score["fixture_only"])
            self.assertEqual(score["scored_clean_bits"], 3 * len(heldout))
            self.assertFalse(score["target_law_disclosed"])
            self.assertFalse(score["scientific_pass"])
            self.assertTrue(0 <= score["clean_heldout_accuracy"] <= 1)
            with self.assertRaises(target.TargetAdmissionRejected):
                evaluator.score_once([(0.5, 0.5, 0.5)] * len(heldout))
            self.assertEqual(evaluator.public_receipt()["scored_checkpoints"], [16])
            self.assertEqual(evaluator.public_receipt()["protected_cohorts_consumed"], 0)
            self.assertFalse(hasattr(evaluator, "target_law"))
            self.assertFalse(hasattr(evaluator, "target_ast"))

    def test_public_heldout_overlap_and_invalid_outcomes_fail_closed(self):
        public = fixture_inputs(3)
        with self.assertRaisesRegex(target.TargetAdmissionRejected,
                                    "PUBLIC_OVERLAP"):
            target.PrivateTargetEvaluator.synthetic_fixture(
                1024, fixture_law(), public, public)
        evaluator = target.PrivateTargetEvaluator.synthetic_fixture(
            1024, fixture_law(), public, fixture_inputs(2, offset=500))
        with self.assertRaises(target.TargetAdmissionRejected):
            evaluator.public_event(0, public[1])
        with self.assertRaises(target.TargetAdmissionRejected):
            evaluator.public_event(-1, public[-1])
        self.assertEqual(evaluator.public_receipt()["public_events_used"], 0)


if __name__ == "__main__":
    unittest.main()
