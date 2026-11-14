"""MD35 pre-execution negative controls. No synthetic cohort is opened."""
import copy
import inspect
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from custody import (BLOCK_SIZES, FAMILIES, LOCK, SPLITS, private_allocation,
                     require_first_use_clearance, split_preflight)


class MD35CustodyTests(unittest.TestCase):
    def test_frozen_split_arithmetic_without_model_or_world(self):
        preflight = split_preflight()
        self.assertEqual(preflight["status"], "ALLOCATION_ONLY_NOT_FIRST_USE")
        self.assertEqual(preflight["worlds_instantiated"], 0)
        self.assertEqual(preflight["physical_actions"], 0)
        self.assertFalse(preflight["training_executed"])
        self.assertFalse(preflight["transfer_opened"])
        self.assertFalse(preflight["cold_opened"])
        self.assertEqual(preflight, split_preflight())
        self.assertEqual({k: v["episodes"] for k, v in
                          preflight["splits"].items()}, {
            "train": 1536, "validation": 384,
            "unfamiliar_transfer": 384, "independent_cold": 192,
        })
        self.assertEqual({k: v["repetitions_per_combination"]
                          for k, v in preflight["splits"].items()}, {
            "train": 16, "validation": 4,
            "unfamiliar_transfer": 4, "independent_cold": 2,
        })
        self.assertEqual(len(preflight["allocation_sha256"]), 64)

    def test_allocation_exact_law_blocks_only_harness_receives_private(self):
        for name, spec in SPLITS.items():
            first, last = spec["first"], spec["last"]
            self.assertEqual(last - first + 1, BLOCK_SIZES[name] * 4)
            first_rows = [private_allocation(first + i) for i in range(4)]
            self.assertEqual([r["context"] for r in first_rows],
                             [0, 1, 2, 3])
            self.assertTrue(all(r["family"] == FAMILIES[name][0]
                                for r in first_rows))
            self.assertEqual(private_allocation(last)["cohort"], name)
        self.assertEqual(set(FAMILIES["train"]) &
                         set(FAMILIES["unfamiliar_transfer"]), set())

    def test_no_adjacent_fixture_or_official_seeds_can_enter(self):
        for seed in (None, False, True, 15000, 15095, 11000, 14095,
                     1900001, 2900001, 3900001, 4900001, -1,
                     60999, 62536, 62999, 63384, 63999, 64384,
                     64999, 65192, "61000", 61000.0):
            with self.subTest(seed=seed):
                with self.assertRaisesRegex(
                        AssertionError, "UNALLOCATED_OR_PROTECTED_COHORT"):
                    private_allocation(seed)

    def test_collision_or_changed_source_allocation_fails_closed(self):
        saved = SPLITS["train"]
        try:
            bad = copy.deepcopy(saved)
            bad["last"] += 4
            SPLITS["train"] = bad
            with self.assertRaisesRegex(AssertionError, "ALLOCATION_CHANGED"):
                split_preflight()
            bad = copy.deepcopy(saved)
            bad["families"] = ["relay", "braid", "collider"]
            SPLITS["train"] = bad
            with self.assertRaisesRegex(AssertionError, "ALLOCATION_CHANGED"):
                split_preflight()
        finally:
            SPLITS["train"] = saved
        self.assertEqual(split_preflight()["physical_actions"], 0)

    def test_ledger_and_first_use_cannot_be_unlocked_by_argument(self):
        for args in ((), (True,), ({"verified": True},),
                     ({"authorized": True, "ledger_collision": False},)):
            with self.subTest(args=args):
                with self.assertRaisesRegex(
                    PermissionError, "FIRST_USE_NOT_VERIFIED"):
                    require_first_use_clearance(*args)
        with self.assertRaisesRegex(PermissionError, "FIRST_USE_NOT_VERIFIED"):
            require_first_use_clearance(
                seed=61000, authority="owner-approved", ledger="safe")

    def test_no_world_generation_or_protected_evaluation_in_preflight(self):
        source = inspect.getsource(sys.modules["custody"])
        for forbidden in ("PartialRouteWorld", "fixture_spec(",
                          "privileged_physics_oracle(", "world.step(",
                          "torch.save(", "numpy.random", "eval_holdout("):
            self.assertNotIn(forbidden, source)
        self.assertEqual(LOCK["parent"]["exact_parent_sha"],
                         "cd031504130732617e9ce55ee0da5476f559f59e")
        self.assertEqual(LOCK["scope"]["merge"], False)
        self.assertFalse(LOCK["scope"]["deployment"])


if __name__ == "__main__":
    unittest.main()
