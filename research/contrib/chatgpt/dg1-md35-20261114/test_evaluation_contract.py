"""Mechanical MD35 scoring tests on handwritten toy physics, NOT science.

No reserved MD35 train, validation, transfer or cold seeds or worlds opened.
No model fitting, first use, scientific acceptance, or runner dispatch.
"""
from dataclasses import replace
import copy
import inspect
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from test_models import toy_block
from evaluation_contract import (
    BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED, CONVENTIONAL, EVAL_COHORTS,
    _block_metrics, _check_episode, assert_frozen_checkpoint,
    block_bootstrap, compute_parity_report, harness_only_family_breakdown,
    paired_net_bootstrap, preregistered_headroom_status,
    sha256_json, summarize_unopened_shape_only, verified_checkpoint_digest,
)


class ToyCheckpoint:
    def __init__(self):
        self.parameters = [2.0, 3.0]

    def checkpoint(self):
        return {"schema": "MD35_TEST_STUB_NO_TRAINING", "weights": self.parameters}


class EvalArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toy = toy_block()
        cls.toy_transfer_shape = (cls.toy,) * 96
        cls.toy_cold_shape = (cls.toy,) * 48

    def test_strict_cohort_sizes_and_no_science_claim(self):
        for name, blocks, expected in (
                ("unfamiliar_transfer", self.toy_transfer_shape, 96),
                ("independent_cold", self.toy_cold_shape, 48)):
            with self.subTest(cohort=name):
                r = summarize_unopened_shape_only(blocks, name)
                self.assertEqual((r["blocks"], r["episodes"]),
                                 (expected, expected * 4))
                self.assertTrue(r["source_only_arithmetic"])
                self.assertTrue(r["not_scientific_admission"])
                self.assertEqual(r["retention_causality_claim"], "NOT_TESTED")
                self.assertEqual(
                    r["block_bootstrap_95"]["resamples"], 2000)
                self.assertEqual(len(r["public_block_receipts"]), expected)
                self.assertEqual(r["physically_paid_actions"], expected * 16)
                self.assertAlmostEqual(r["mean_net_utility"],
                                       sum(ep.net_utility for ep in self.toy) / 4)
        with self.assertRaisesRegex(AssertionError, "NOT_FROZEN_HELDOUT"):
            summarize_unopened_shape_only(self.toy_transfer_shape, "train")
        with self.assertRaisesRegex(AssertionError, "UNQUALIFIED_TRAIN"):
            summarize_unopened_shape_only(self.toy_cold_shape,
                                          "unfamiliar_transfer")

    def test_public_metric_counts_physically_paid_real_toy_steps(self):
        m = _block_metrics(self.toy)
        self.assertEqual(m["physically_paid_actions"], 16)
        self.assertEqual(m["paid_diagnostics"], 4)
        self.assertEqual(m["goal_successes"],
                         sum(int(ep.terminal()[3] == 0.98) for ep in self.toy))
        self.assertEqual(m["route1_actions"],
                         sum(ep.route() for ep in self.toy))
        self.assertAlmostEqual(m["first_episode_net"],
                               self.toy[0].net_utility)
        self.assertAlmostEqual(m["last_episode_net"],
                               self.toy[3].net_utility)

    def test_forged_rewards_missing_route_charge_and_free_sensor_fail(self):
        ep = self.toy[0]
        with self.assertRaisesRegex(AssertionError, "IMPOSSIBLE_NET_UTILITY"):
            _check_episode(replace(ep, net_utility=9.0), 0)
        with self.assertRaisesRegex(AssertionError, "NONPUBLIC_OR_BAD_CONTEXT"):
            _check_episode(ep, 1)
        route_index = next(i for i, x in enumerate(ep.events)
                           if x[1] == "route")
        route = ep.events[route_index]
        malicious = list(ep.events)
        malicious[route_index] = (route[0], route[1], route[2],
                                  0.0, route[4])
        with self.assertRaisesRegex(AssertionError, "ROUTE_COST_OMITTED"):
            _check_episode(replace(ep, events=tuple(malicious)), 0)
        actuator_index = next(i for i, x in enumerate(ep.events)
                              if x[1] == "actuator")
        action = ep.events[actuator_index]
        malicious = list(ep.events)
        malicious[actuator_index] = (action[0], action[1], action[2],
                                    action[3], 0)
        with self.assertRaisesRegex(AssertionError, "FREE_PRIVATE_SENSOR"):
            _check_episode(replace(ep, events=tuple(malicious)), 0)
        with self.assertRaisesRegex(AssertionError, "UNVERIFIED_RECEIPT_SHAPE"):
            _check_episode(replace(ep, trace_sha256="madeup"), 0)

    def test_bootstrap_law_blocks_not_individual_episodes(self):
        self.assertEqual(BOOTSTRAP_SEED, 35045)
        self.assertEqual(BOOTSTRAP_RESAMPLES, 2000)
        sample = [0.0, 1.0, 0.5, 0.75]
        a = block_bootstrap(sample)
        b = block_bootstrap(sample)
        self.assertEqual(a, b)
        self.assertEqual(a["block_count"], len(sample))
        self.assertTrue(0 <= a["low95"] <= a["high95"] <= 1)
        self.assertEqual(block_bootstrap([0.42] * 48)["low95"], 0.42)
        with self.assertRaisesRegex(AssertionError, "INVALID_BLOCKS"):
            block_bootstrap([math.nan, 0.5])
        with self.assertRaisesRegex(AssertionError, "INVALID_BLOCKS"):
            block_bootstrap([])

    def test_paired_bootstrap_requires_aligned_harness_private_world_identity(self):
        # Synthetic, nonreserved bookkeeping digests only: this test neither
        # authenticates a real harness nor opens any protected hidden cohort.
        left = tuple(sha256_json({"toy": i, "cohort": "transfer"})
                     for i in range(96))
        diff = paired_net_bootstrap(
            self.toy_transfer_shape, self.toy_transfer_shape,
            "unfamiliar_transfer",
            left_block_commitments=left, right_block_commitments=left)
        self.assertAlmostEqual(diff["mean_paired_delta"], 0)
        self.assertAlmostEqual(diff["block_bootstrap_95"]["low95"], 0)
        self.assertAlmostEqual(diff["block_bootstrap_95"]["high95"], 0)
        self.assertTrue(diff["harness_only_commitments_shape_matched"])
        self.assertFalse(diff["independent_harness_authenticity_verified"])
        self.assertTrue(diff["not_scientific_admission"])
        with self.assertRaisesRegex(AssertionError, "PAIRED_HARNESS_IDENTITY"):
            paired_net_bootstrap(self.toy_transfer_shape,
                                 self.toy_transfer_shape,
                                 "unfamiliar_transfer")
        for corrupted in (
                tuple(reversed(left)), left[1:] + left[:1],
                left[:-1] + (left[0],), left[:-1],
                left[:-1] + ("invalid",),
                left[:-1] + (left[-1].upper(),)):
            with self.subTest(mismatch=corrupted[:2]):
                with self.assertRaisesRegex(
                        AssertionError,
                        "PAIRED_HIDDEN_LAW_BLOCK_MISMATCH|PAIRED_HARNESS_IDENTITY"):
                    paired_net_bootstrap(
                        self.toy_transfer_shape, self.toy_transfer_shape,
                        "unfamiliar_transfer",
                        left_block_commitments=left,
                        right_block_commitments=corrupted)
        # Even identical public contexts and physically valid action receipts
        # do not prove both models faced the same private laws.
        with self.assertRaisesRegex(AssertionError, "UNQUALIFIED_TRAIN"):
            paired_net_bootstrap(self.toy_transfer_shape,
                                 self.toy_cold_shape,
                                 "unfamiliar_transfer",
                                 left_block_commitments=left,
                                 right_block_commitments=left)

    def test_harness_labels_never_become_model_inputs(self):
        # Non-reserved 96-block LABEL-SCHEMA toy fixture; not a score for
        # true braid/inhibitor/crossbridge laws.
        labels = [
            (("braid", "inhibitor", "crossbridge")[i % 3],
             (i // 3) % 4, ((i // 12) % 2) == 1)
            for i in range(96)
        ]
        score = harness_only_family_breakdown(
            self.toy_transfer_shape, labels, "unfamiliar_transfer")
        self.assertEqual(set(score), {"braid", "inhibitor", "crossbridge"})
        self.assertTrue(all(row["blocks"] == 32 for row in score.values()))
        with self.assertRaisesRegex(AssertionError, "PRIVATE_LABEL_SCHEMA"):
            corrupt = labels.copy()
            corrupt[0] = ("relay", 0, False)
            harness_only_family_breakdown(
                self.toy_transfer_shape, corrupt, "unfamiliar_transfer")
        with self.assertRaisesRegex(
                AssertionError, "FROZEN_PRIVATE_LAW_ALLOCATION_DRIFT"):
            corrupt = labels.copy()
            corrupt[0], corrupt[1] = corrupt[1], corrupt[0]
            harness_only_family_breakdown(
                self.toy_transfer_shape, corrupt, "unfamiliar_transfer")

    def test_frozen_headroom_thresholds_cannot_omit_weak_controls(self):
        names = set(CONVENTIONAL)
        self.assertEqual(names, {"bayesian", "recurrent", "model_based_rl"})
        underqualified = {
            name: {"unfamiliar_transfer": 0.0, "independent_cold": -0.1}
            for name in names
        }
        self.assertEqual(
            preregistered_headroom_status(underqualified),
            "CONTROLS_UNDERQUALIFIED_OR_UNIDENTIFIABLE_NO_NATIVE_GATE")
        partial = copy.deepcopy(underqualified)
        partial["bayesian"] = {
            "unfamiliar_transfer": 0.2, "independent_cold": 0.3,
        }
        self.assertEqual(
            preregistered_headroom_status(partial),
            "DEVELOPING_TASK_HEADROOM_ONLY")
        stop = copy.deepcopy(partial)
        stop["recurrent"] = {
            "unfamiliar_transfer": 0.89, "independent_cold": 0.89,
        }
        self.assertEqual(
            preregistered_headroom_status(stop),
            "TRIVIAL_FOR_NOVEL_GAIN_STOP")
        with self.assertRaisesRegex(AssertionError, "INCOMPLETE_STRONG"):
            preregistered_headroom_status({"bayesian": partial["bayesian"]})
        with self.assertRaisesRegex(AssertionError, "INVALID_UNQUALIFIED"):
            invalid = copy.deepcopy(stop)
            invalid["recurrent"]["independent_cold"] = float("nan")
            preregistered_headroom_status(invalid)

    def test_matched_cpu_and_paid_action_claims_are_separate(self):
        rows = {
            "bayesian": {
                "fit_selection_cpu_seconds": 80.0,
                "whole_process_cpu_seconds": 100.0,
                "whole_process_wall_seconds": 115.0,
                "paid_actions": 6144,
                "public_episodes": 1536,
                "available_paid_action_slots": 6144,
            },
            "recurrent": {
                "fit_selection_cpu_seconds": 90.0,
                "whole_process_cpu_seconds": 107.0,
                "whole_process_wall_seconds": 127.0,
                "paid_actions": 6144,
                "public_episodes": 1536,
                "available_paid_action_slots": 6144,
            },
            "model_based_rl": {
                "fit_selection_cpu_seconds": 65.0,
                "whole_process_cpu_seconds": 109.0,
                "whole_process_wall_seconds": 119.0,
                "paid_actions": 6144,
                "public_episodes": 1536,
                "available_paid_action_slots": 6144,
            },
        }
        self.assertTrue(compute_parity_report(rows)
                        ["matched_superiority_claim_permitted"])
        changed = copy.deepcopy(rows)
        changed["recurrent"]["whole_process_cpu_seconds"] = 200.0
        parity = compute_parity_report(changed)
        self.assertFalse(parity["matched_compute"])
        self.assertFalse(parity["matched_superiority_claim_permitted"])
        changed = copy.deepcopy(rows)
        changed["recurrent"]["paid_actions"] = 5400
        result = compute_parity_report(changed)
        self.assertFalse(result["matched_paid_actions"])
        self.assertTrue(result["matched_action_opportunity"])
        self.assertTrue(result["matched_superiority_claim_permitted"])
        changed = copy.deepcopy(rows)
        changed["recurrent"]["public_episodes"] = 1400
        changed["recurrent"]["available_paid_action_slots"] = 5600
        changed["recurrent"]["paid_actions"] = 5600
        unequal = compute_parity_report(changed)
        self.assertFalse(unequal["matched_information"])
        self.assertFalse(unequal["matched_action_opportunity"])
        self.assertFalse(unequal["matched_superiority_claim_permitted"])
        # 900 seconds applies to fitting/selection, not the end-to-end
        # measurement. A legitimate longer full process must stay reportable.
        extended = copy.deepcopy(rows)
        for v in extended.values():
            v["fit_selection_cpu_seconds"] = 890.0
            v["whole_process_cpu_seconds"] = 1050.0
            v["whole_process_wall_seconds"] = 1250.0
        self.assertTrue(compute_parity_report(extended)
                        ["matched_superiority_claim_permitted"])
        with self.assertRaisesRegex(AssertionError, "COMPUTE_OR_PHYSICAL"):
            changed = copy.deepcopy(rows)
            changed["recurrent"]["fit_selection_cpu_seconds"] = 901.0
            compute_parity_report(changed)
        with self.assertRaisesRegex(AssertionError, "COMPUTE_OR_PHYSICAL"):
            changed = copy.deepcopy(rows)
            changed["recurrent"]["fit_selection_cpu_seconds"] = 101.0
            changed["recurrent"]["whole_process_cpu_seconds"] = 100.0
            compute_parity_report(changed)
        with self.assertRaisesRegex(AssertionError, "COMPUTE_RECEIPT_INCOMPLETE"):
            changed = copy.deepcopy(rows)
            del changed["bayesian"]["whole_process_wall_seconds"]
            compute_parity_report(changed)

    def test_equal_legal_opportunity_not_equal_paid_probe_use(self):
        # Identical legally available physical actions, but one policy
        # lawfully declines a diagnostic in a subset of episodes. It must
        # not lose comparability merely for avoiding costlier interventions.
        data = {
            "bayesian": {
                "fit_selection_cpu_seconds": 90.0,
                "whole_process_cpu_seconds": 100.0,
                "whole_process_wall_seconds": 115.0,
                "paid_actions": 6144,
                "available_paid_action_slots": 6144,
                "public_episodes": 1536,
            },
            "recurrent": {
                "fit_selection_cpu_seconds": 91.0,
                "whole_process_cpu_seconds": 104.0,
                "whole_process_wall_seconds": 119.0,
                "paid_actions": 4608,
                "available_paid_action_slots": 6144,
                "public_episodes": 1536,
            },
        }
        scores = compute_parity_report(data)
        self.assertFalse(scores["matched_paid_actions"])
        self.assertTrue(scores["matched_action_opportunity"])
        self.assertTrue(scores["matched_superiority_claim_permitted"])
        for field, value in (
                ("available_paid_action_slots", 6143),
                ("available_paid_action_slots", 6145),
                ("paid_actions", 4607), ("paid_actions", 6145)):
            bad = copy.deepcopy(data)
            bad["bayesian"][field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(
                        AssertionError, "COMPUTE_OR_PHYSICAL_ACTION_INVALID"):
                    compute_parity_report(bad)
        data["recurrent"]["whole_process_cpu_seconds"] = 111.0
        self.assertFalse(compute_parity_report(data)
                         ["matched_superiority_claim_permitted"])

    def test_independent_cold_checkpoint_mutation_detection(self):
        model = ToyCheckpoint()
        digest = verified_checkpoint_digest(model)
        self.assertEqual(len(digest), 64)
        self.assertEqual(assert_frozen_checkpoint(model, digest), digest)
        model.parameters[0] = 9.0
        with self.assertRaisesRegex(AssertionError, "HELDOUT_WEIGHT_MUTATION"):
            assert_frozen_checkpoint(model, digest)
        with self.assertRaisesRegex(AssertionError, "UNPINNED_TRAIN"):
            assert_frozen_checkpoint(model, "not-pinned")
        with self.assertRaises(ValueError):
            sha256_json({"invalid": float("nan")})

    def test_scorer_cannot_generate_or_access_hidden_world(self):
        import evaluation_contract
        source = inspect.getsource(evaluation_contract)
        for forbidden in ("fixture_spec(", "private_allocation(",
                          "PartialRouteWorld(", "world.step(",
                          "privileged_physics_oracle(", "LAWS["):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
