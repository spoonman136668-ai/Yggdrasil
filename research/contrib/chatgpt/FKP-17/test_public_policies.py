"""Public-only FKP-17 relationship and matched-ablation qualification tests.

No held-original worlds, no independent scientific reward, no source-law access.
"""
import unittest
from collections import namedtuple

import public_policies as policy
import source_fixture as source


class PublicPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Source observations generated ONCE, then the exact same immutable
        # public tape is presented to all five arms independently.
        cls.facts = tuple(row for _, _, row in source.foundation_facts())
        cls.arms = {
            name: policy.PublicRelationArm(name).fit_public_foundation(cls.facts)
            for name in policy.ARMS
        }

    def setUp(self):
        for arm in self.arms.values():
            arm.begin_world()

    def test_32768_public_fact_and_capacity_parity(self):
        self.assertEqual(len(self.facts), 32768)
        digest = policy.assert_equal_public_foundation(self.arms.values())
        self.assertEqual(len(digest), 64)
        self.assertEqual(len({arm.foundation_sha256
                              for arm in self.arms.values()}), 1)
        self.assertEqual({arm.received_foundation_count
                          for arm in self.arms.values()}, {32768})
        self.assertEqual({arm.learned_bytes for arm in self.arms.values()},
                         {2 * 8 * 8 * 16 * 4 + 2 * 8 * (8 + 4)})
        self.assertTrue(all(arm.learned_bytes < 1048576
                            for arm in self.arms.values()))

    def test_public_training_observations_only_update_post_action(self):
        seed = source.TRAIN[0]
        actions = source.public_actions(seed, 24)
        actual = source.collect_public(seed, actions)
        state = actual[0].before
        pre = [arm.choose_public(state) for arm in self.arms.values()]
        self.assertTrue(all(type(a) is int and 0 <= a < 8 for a in pre))
        for name, arm in self.arms.items():
            for row in actual:
                arm.observe_public(row)
            self.assertEqual(arm.observed_world_count, 24, name)
            self.assertTrue(type(arm.choose_public(actual[-1].after)) is int)
        self.assertEqual(sum(self.arms["NO_UPDATE"]._world), 0)
        self.assertGreater(sum(self.arms["STRUCTURED"]._world), 0)
        self.assertGreater(sum(self.arms["FLAT"]._world), 0)
        self.assertGreater(sum(self.arms["SHUFFLED"]._world), 0)
        self.assertGreater(sum(self.arms["MINIMAL"]._world), 0)

    def test_minimal_and_no_update_are_real_ablations(self):
        minimal = self.arms["MINIMAL"]
        no_update = self.arms["NO_UPDATE"]
        self.assertEqual(sum(minimal._foundation), 0)
        self.assertGreater(sum(no_update._foundation), 0)
        self.assertEqual(no_update._world_rows, 0)
        seed = source.TRAIN[1]
        row = source.collect_public(seed, (0,))[0]
        p_before = no_update.choose_public(row.before)
        no_update.observe_public(row)
        self.assertEqual(sum(no_update._world), 0)
        self.assertEqual(p_before, no_update.choose_public(row.before))
        self.assertEqual(no_update.observed_world_count, 1)

    def test_each_learner_decision_is_only_preoutcome_public_registers(self):
        row = source.collect_public(source.TRAIN[2], (1,))[0]
        for arm in self.arms.values():
            with self.subTest(arm=arm.variant):
                before = arm.state_receipt()
                decision = arm.choose_public(row.before)
                self.assertEqual(decision, arm.choose_public(row.before))
                self.assertEqual(arm.state_receipt(), before)
                self.assertTrue(0 <= decision < 8)
                for forbidden in (row, {"before": row.before,
                                        "reward": row.reward,
                                        "oracle_returns": [1.] * 8}):
                    with self.assertRaises(ValueError):
                        arm.choose_public(forbidden)

    def test_reject_extra_outcome_and_private_fields(self):
        Extended = namedtuple("Extended", ("before", "action", "after",
                                            "reward", "done", "history",
                                            "future_returns"))
        row = source.collect_public(source.TRAIN[3], (1,))[0]
        bad = Extended(*row, [0.5] * 8)
        for arm in self.arms.values():
            with self.subTest(arm=arm.variant):
                before = arm.state_receipt()
                with self.assertRaises(ValueError):
                    arm.observe_public(bad)
                with self.assertRaises(ValueError):
                    arm.observe_public({"after": row.after, "oracle": [2]})
                self.assertEqual(arm.state_receipt(), before)

    def test_frozen_foundation_and_world_budget_refuse_overrun(self):
        row = source.collect_public(source.TRAIN[4], (2,))[0]
        for arm in self.arms.values():
            with self.assertRaises(ValueError):
                arm.fit_public_foundation((row,))
            with self.assertRaises(ValueError):
                arm._observe(row, foundation=True)
            for _ in range(256):
                arm.observe_public(row)
            self.assertEqual(arm.observed_world_count, 256)
            before = arm.state_receipt()
            with self.assertRaises(ValueError):
                arm.observe_public(row)
            self.assertEqual(arm.state_receipt(), before)

    def test_atomic_count_overflow_rejection(self):
        arm = self.arms["STRUCTURED"]
        row = source.PublicStep((0,) * 8, 0, (0,) * 8, 0.0, False, ())
        arm._world[policy._index(0, 5, 0)] = 65535
        before = arm.state_receipt()
        with self.assertRaises(OverflowError):
            arm.observe_public(row)
        self.assertEqual(arm.state_receipt(), before)
        self.assertEqual(arm.observed_world_count, 0)
        self.assertEqual(arm._world_visits[0], 0)

    def test_shuffled_targets_not_same_readout_as_native(self):
        # The arrays retain exactly the same source facts. Only the target
        # register binding changes at prediction time, not training access.
        original = self.arms["STRUCTURED"]
        shuffled = self.arms["SHUFFLED"]
        self.assertEqual(original._foundation.tolist(),
                         shuffled._foundation.tolist())
        self.assertEqual(original._foundation_visits,
                         shuffled._foundation_visits)
        self.assertEqual(original.foundation_sha256,
                         shuffled.foundation_sha256)
        self.assertNotEqual(original.variant, shuffled.variant)
        state = tuple(range(8))
        for arm in (original, shuffled):
            choice = arm.choose_public(state)
            self.assertIn(choice, range(8))

    def test_no_hidden_causal_source_or_future_available_in_module(self):
        from pathlib import Path
        text = Path(policy.__file__).read_text(encoding="utf-8")
        for forbidden in ("import source_fixture", "from source_fixture",
                          "HELD_DEV", "HELD_TRANSFER", "def eval_held",
                          "open_dev", "import memory_gym"):
            self.assertNotIn(forbidden, text)

    def test_equal_prior_rejects_missing_or_tampered_arm(self):
        arr = list(self.arms.values())
        self.assertEqual(len(policy.assert_equal_public_foundation(arr)), 64)
        with self.assertRaises(ValueError):
            policy.assert_equal_public_foundation(arr[:-1])
        changed = policy.PublicRelationArm("FLAT")
        changed._foundation_rows = 32768
        changed._frozen = True
        swapped = [changed if a.variant == "FLAT" else a for a in arr]
        with self.assertRaises(ValueError):
            policy.assert_equal_public_foundation(swapped)


if __name__ == "__main__":
    unittest.main()
