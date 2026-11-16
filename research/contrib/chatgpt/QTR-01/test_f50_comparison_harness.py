"""F50 pre-first-use harness: synthetic-only coverage, no DEV target labels."""
from functools import lru_cache
import json
from hashlib import sha256
import math
import unittest

import f50_comparison_harness as harness
import f50_worlds as world


@lru_cache(maxsize=1)
def fixture_pools():
    # Non-DEV namespace, no target AST. Two disjoint 512-trajectory lists.
    occupied = set()
    parts = []
    for partition in ("public", "sealed-fixture"):
        rows = []
        for i in range(512):
            for nonce in range(1000):
                item = world._trajectory(
                    "F50/HARNESS-FIXTURE-INPUTS/v1", 1024, 9191,
                    partition, i, nonce)
                if item is not None and item not in occupied:
                    occupied.add(item)
                    rows.append(item)
                    break
            else:
                raise AssertionError("Synthetic fixture inputs exhausted")
        parts.append(tuple(rows))
    assert len(occupied) == 1024
    return tuple(parts)


class SyntheticOracle:
    """No target law or truth; synthetic public bits and fixed fake score."""

    def __init__(self):
        self.pool, self.heldout = fixture_pools()
        self.events = set()
        self.scored = set()
        self.calls = []

    def public_candidates(self):
        return self.pool

    def public_event(self, index, episode):
        self.calls.append("public")
        if (type(index) is not int or index in self.events
            or not 0 <= index < 512 or episode != self.pool[index]):
            raise AssertionError("fixture query invalid")
        self.events.add(index)
        return (index & 1, (index >> 1) & 1, (index >> 2) & 1)

    def heldout_inputs_for_prediction(self):
        self.calls.append("heldout")
        if len(self.events) not in (16, 32, 64):
            raise AssertionError("fixture evaluator leaked early heldout")
        return self.heldout

    def score_once(self, predictions):
        self.calls.append("score")
        n = len(self.events)
        if (n not in (16, 32, 64) or n in self.scored
            or len(predictions) != 512):
            raise AssertionError("invalid fixture score request")
        self.scored.add(n)
        return {"query_budget": n,
                "clean_heldout_accuracy": 0.5,
                "scored_clean_bits": 1536,
                "fixture_only": True,
                "target_law_disclosed": False,
                "scientific_pass": False}

    def public_receipt(self):
        return {"fixture_only": True,
                "public_events_used": len(self.events),
                "observed_public_bits": len(self.events) * 3,
                "scored_checkpoints": sorted(self.scored),
                "protected_cohorts_consumed": 0}


class DummyArm:
    """Engineering protocol double, not a trained or causal learner."""

    def __init__(self, size, seed, kind):
        self.size, self.seed, self.kind = size, seed, kind
        self.pool = fixture_pools()[0]
        self.used = []
        self.pending = None
        self.observed_bits = 0
        self.proposals = 0
        self.prediction_accesses = 0
        self.optimizer_steps = 0
        self.target_graph_available = False

    def select(self):
        if self.pending is not None:
            raise AssertionError("pending fake query")
        # Deterministic, world-dependent distinct policy order.
        ordinal = len(self.used)
        self.pending = ordinal * 7 % 512
        return self.pending, self.pool[self.pending]

    def observe(self, index, bits):
        if index != self.pending:
            raise AssertionError("fixture wrong index")
        self.used.append(index)
        self.pending = None
        self.observed_bits += 3
        if (self.kind == "native"
            or self.kind == "compositional_grammar_bayes"
            or self.kind.startswith("native_")):
            self.proposals += 2048

    def probabilities(self, episodes):
        self.prediction_accesses += len(episodes) * 3
        return tuple((0.5, 0.5, 0.5) for _ in episodes)

    def cold_checkpoint(self):
        state = {"used": self.used, "observed": self.observed_bits,
                 "proposals": self.proposals,
                 "prediction_accesses": self.prediction_accesses}
        raw = json.dumps(state, sort_keys=True, separators=(",", ":")).encode("ascii")
        return raw + b"." + sha256(raw).hexdigest().encode("ascii")

    @staticmethod
    def restore(packet):
        body, checksum = packet.rsplit(b".", 1)
        if sha256(body).hexdigest().encode("ascii") != checksum:
            raise AssertionError("fixture checksum")
        class Restored:
            def cold_checkpoint(self):
                return packet
        return Restored()


def make_arm(size, seed, kind):
    return DummyArm(size, seed, kind), DummyArm.restore


class F50ComparisonHarnessTests(unittest.TestCase):
    def test_frozen_high_first_nine_worlds_and_all_twelve_arms(self):
        plan = harness.frozen_plan()
        self.assertEqual(len(plan), 9)
        self.assertEqual(plan[:3], ((4096, 4013), (4096, 4057),
                                    (4096, 4099)))
        self.assertEqual(plan[-3:], ((1024, 4013), (1024, 4057),
                                     (1024, 4099)))
        self.assertEqual(len(harness.KINDS), 12)
        self.assertEqual(harness.CHECKPOINTS, (16, 32, 64))
        self.assertEqual(harness.TRAINED_SOURCE_KINDS,
                         ("graph_conditioned_gru",
                          "law_conditioned_set_mlp",
                          "graph_conditioned_logistic"))
        self.assertNotIn("target_ast", harness.__dict__)
        self.assertNotIn("target_law", harness.__dict__)
        self.assertNotIn("PrivateTargetEvaluator", harness.__dict__)
        readiness = harness.describe_readiness()
        self.assertEqual(readiness["development_first_use"], "BLOCKED")
        self.assertFalse(readiness["scientific_pass"])

    def test_incomplete_or_unequal_source_checkpoint_manifest_rejected(self):
        role = {k: {"checkpoint_sha256": "a" * 64,
                    "source_sha": "b" * 40,
                    "source_dataset_sha256": "c" * 64,
                    "prereg_blob": world.PREREG_BLOB}
                for k in harness.TRAINED_SOURCE_KINDS}
        with self.assertRaisesRegex(harness.ComparisonRejected,
                                    "SOURCE_SIZE_ROLE_INCOMPLETE"):
            harness.checkpoint_inventory({4096: role})
        inventory = {s: {k: dict(v) for k, v in role.items()}
                     for s in world.BANK_SIZES}
        identity = harness.checkpoint_inventory(inventory)
        self.assertEqual(set(identity), set(world.BANK_SIZES))
        inventory[2048]["graph_conditioned_logistic"]["source_dataset_sha256"] = "d" * 64
        with self.assertRaisesRegex(harness.ComparisonRejected,
                                    "SOURCE_DATA_PARITY_FAILED"):
            harness.checkpoint_inventory(inventory)
        inventory[2048]["graph_conditioned_logistic"]["source_dataset_sha256"] = "c" * 64
        inventory[1024]["law_conditioned_set_mlp"]["checkpoint_sha256"] = "not_a_sha"
        with self.assertRaisesRegex(harness.ComparisonRejected,
                                    "SOURCE_IDENTITY_UNVERIFIED"):
            harness.checkpoint_inventory(inventory)

    def test_fixture_one_arm_full_64_actions_exact_cold_and_three_checkpoints(self):
        arm, restore = make_arm(4096, 4013, "native")
        oracle = SyntheticOracle()
        result = harness.run_fixture_arm(4096, 4013, "native",
                                         arm, oracle, restore)
        self.assertEqual(result["public_events"], 64)
        self.assertEqual(result["observed_public_bits"], 192)
        self.assertEqual(result["proposals"], 64 * 2048)
        self.assertEqual(result["cold_restores"], 3)
        self.assertEqual([x["budget"] for x in result["checkpoints"]],
                         [16, 32, 64])
        self.assertEqual([x["fixture_accuracy"] for x in result["checkpoints"]],
                         [0.5, 0.5, 0.5])
        self.assertTrue(all(len(x["cold_sha256"]) == 64
                            for x in result["checkpoints"]))
        self.assertEqual(oracle.calls.count("heldout"), 3)
        self.assertEqual(oracle.calls.count("score"), 3)
        self.assertEqual(result["classification"],
                         harness.FIXTURE_CLASSIFICATION)
        self.assertFalse(result["scientific_pass"])

    def test_dev_first_use_is_refused_before_any_public_query(self):
        arm, restore = make_arm(4096, 4013, "native")
        oracle = SyntheticOracle()
        original = oracle.public_receipt
        oracle.public_receipt = lambda: dict(original(), fixture_only=False)
        with self.assertRaisesRegex(harness.ComparisonRejected,
                                    "DEV_FIRST_USE_NOT_AUTHORIZED"):
            harness.run_fixture_arm(4096, 4013, "native", arm, oracle, restore)
        self.assertEqual(oracle.calls, [])
        self.assertEqual(oracle.events, set())
        self.assertEqual(arm.used, [])

    def test_public_pool_replay_cold_and_score_negative_controls(self):
        arm, restore = make_arm(4096, 4013, "uniform")
        oracle = SyntheticOracle()
        arm.pool = tuple(reversed(arm.pool))
        with self.assertRaisesRegex(harness.ComparisonRejected,
                                    "POOL_MISMATCH"):
            harness.run_fixture_arm(4096, 4013, "uniform", arm, oracle, restore)
        arm, restore = make_arm(4096, 4013, "native")
        with self.assertRaisesRegex(harness.ComparisonRejected,
                                    "COLD_NOT_BIT_EXACT"):
            harness.run_fixture_arm(4096, 4013, "native", arm,
                                    SyntheticOracle(),
                                    lambda pkt: type("Wrong", (), {
                                        "cold_checkpoint": lambda self: pkt + b"x"
                                    })())

    def test_all_nine_worlds_twelve_arms_fixture_only(self):
        report = harness.run_fixture_nine_worlds(
            make_arm, lambda size, seed, kind: SyntheticOracle())
        self.assertEqual(report["world_count"], 9)
        self.assertEqual(report["arms_per_world"], 12)
        self.assertEqual(len(report["arm_runs"]), 108)
        self.assertTrue(all(x["public_events"] == 64 for x in report["arm_runs"]))
        self.assertTrue(all(len(x["checkpoints"]) == 3
                            for x in report["arm_runs"]))
        self.assertTrue(all(x["fixture_only"] and not x["scientific_pass"]
                            for x in report["arm_runs"]))
        self.assertEqual(report["development_outcomes_consumed"], 0)
        self.assertEqual(report["protected_cohorts_consumed"], 0)
        self.assertEqual(report["classification"],
                         harness.FIXTURE_CLASSIFICATION)


if __name__ == "__main__":
    unittest.main()
