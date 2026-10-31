"""Real focused tests for public native-cell learning, retention and controls.

These are DEV checks of a simple fixed-budget comparator, not a scientific
first-use experiment. There are no hidden labels, paid APIs or source claims.
"""
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells


class NativeCausalCellsTests(unittest.TestCase):
    def test_untrained_or_single_arm_abstains(self):
        cells = PublicCausalCells()
        self.assertIsNone(cells.choose(0))
        cells.observe(0, 1, 1)
        self.assertIsNone(cells.choose(0))
        self.assertIsNone(cells.choose(0, retained=True))

    def test_learns_from_public_interventions_and_changes_decision(self):
        cells = PublicCausalCells()
        for _ in range(4):
            cells.observe(0, 0, 1)
            cells.observe(0, 1, 0)
        self.assertEqual(cells.choose(0), 0)
        for _ in range(9):
            cells.observe(0, 0, 0)
            cells.observe(0, 1, 1)
        self.assertEqual(cells.choose(0), 1)
        self.assertIsNone(cells.choose(1))

    def test_retained_and_active_addresses_remain_independent(self):
        cells = PublicCausalCells()
        for _ in range(10):
            cells.observe(0, 0, 1)
            cells.observe(0, 1, 0)
            cells.observe(0, 0, 0, retained=True)
            cells.observe(0, 1, 1, retained=True)
        self.assertEqual(cells.choose(0), 0)
        self.assertEqual(cells.choose(0, retained=True), 1)
        self.assertIsNone(cells.choose(8, retained=True))
        self.assertIsNone(cells.choose(6))

    def test_checkpoint_survives_restart_and_equal_subsequent_experience(self):
        original = PublicCausalCells()
        for index in range(7):
            for _ in range(3):
                original.observe(index, 0, 1)
                original.observe(index, 1, 0)
        for index in range(9):
            original.observe(index, 0, 0, retained=True)
            original.observe(index, 1, 1, retained=True)
        snapshot = original.snapshot()
        self.assertEqual(len(snapshot), 164)
        resumed = PublicCausalCells.restore(snapshot)
        self.assertEqual(resumed.snapshot(), snapshot)
        for index in range(7):
            for cells in (original, resumed):
                cells.observe(index, 0, 0)
                cells.observe(index, 1, 1)
        self.assertEqual(original.snapshot(), resumed.snapshot())

    def test_invalid_observations_do_not_change_memory(self):
        cells = PublicCausalCells()
        prior = cells.snapshot()
        bad = [
            (-1, 0, 0, False), (7, 0, 0, False),
            (9, 0, 0, True), (0, 2, 0, False),
            (0, 0, -1, False), (True, 0, 0, False),
            (0, True, 0, False), (0, 0, True, False),
            (0, 0, 1, 1),
        ]
        for address, action, outcome, retained in bad:
            with self.subTest(case=(address, action, outcome, retained)):
                with self.assertRaises(ValueError):
                    cells.observe(address, action, outcome, retained=retained)
                self.assertEqual(cells.snapshot(), prior)
        with self.assertRaises(ValueError):
            cells.choose(9, retained=True)

    def test_checkpoint_tamper_truncation_and_type_rejected(self):
        cells = PublicCausalCells()
        cells.observe(1, 0, 1)
        original = cells.snapshot()
        wrong = bytearray(original)
        wrong[10] ^= 1
        for data in (
            bytes(wrong),
            original[:-1],
            b"ABCD" + original[4:],
            bytearray(original),
        ):
            with self.subTest(candidate_type=type(data), size=len(data)):
                with self.assertRaises(ValueError):
                    PublicCausalCells.restore(data)
        self.assertEqual(cells.snapshot(), original)

    def test_saturating_counter_never_grows_or_wraps(self):
        cells = PublicCausalCells()
        cells._counts[0][0][1] = 65535
        prior = len(cells.snapshot())
        for _ in range(30):
            cells.observe(0, 0, 1)
        self.assertEqual(cells._counts[0][0][1], 65535)
        self.assertEqual(len(cells.snapshot()), prior)
        self.assertEqual(cells.LEARNED_BYTES, 128)
        self.assertEqual(cells.ACTIVE_SLOTS, 7)
        self.assertEqual(cells.RETAINED_SLOTS, 9)

    def test_equal_evidence_has_no_unjustified_preference(self):
        cells = PublicCausalCells()
        for _ in range(5):
            cells.observe(2, 0, 0)
            cells.observe(2, 1, 0)
        self.assertIsNone(cells.choose(2))



class CostAwarePublicCellTests(unittest.TestCase):
    """Development-only public-cost chooser verification; no original-world use."""

    def test_requires_observations_of_both_arms(self):
        c = PublicCausalCells()
        self.assertIsNone(c.choose_with_public_costs(0, 0, 0))
        c.observe(0, 0, 1)
        self.assertIsNone(c.choose_with_public_costs(0, 0, 0))

    def test_zero_cost_matches_original_for_public_counts(self):
        for retained in (False, True):
            c = PublicCausalCells()
            self.assertEqual(c.choose_with_public_costs(0, 0, 0, retained=retained),
                             c.choose(0, retained=retained))
            for action, outcome in ((0, 1), (1, 0), (0, 1), (1, 0)):
                c.observe(0, action, outcome, retained=retained)
            self.assertEqual(c.choose_with_public_costs(0, 0, 0, retained=retained),
                             c.choose(0, retained=retained))
            self.assertEqual(c.choose_with_public_costs(0, 7, 7, retained=retained),
                             c.choose(0, retained=retained))

    def test_cost_reverses_success_only_choice(self):
        c = PublicCausalCells()
        for outcome in (1, 1, 1, 1, 1):
            c.observe(0, 0, outcome)
        for outcome in (1, 1, 1, 0, 0):
            c.observe(0, 1, outcome)
        self.assertEqual(c.choose(0), 0)
        self.assertEqual(c.choose_with_public_costs(0, 8, 0, reward_value=10), 1)

    def test_exact_public_net_tie_abstains(self):
        c = PublicCausalCells()
        for outcome in (1, 0):
            c.observe(0, 0, outcome)
            c.observe(0, 1, outcome)
        self.assertIsNone(c.choose_with_public_costs(0, 2, 2, reward_value=10))
        self.assertEqual(c.choose_with_public_costs(0, 2, 3, reward_value=10), 0)

    def test_public_reward_units_change_choice(self):
        c = PublicCausalCells()
        for outcome in (1, 1, 1, 1, 0):
            c.observe(0, 0, outcome)
        for outcome in (1, 0, 0, 0, 0):
            c.observe(0, 1, outcome)
        self.assertEqual(c.choose_with_public_costs(0, 2, 0, reward_value=1), 1)
        self.assertEqual(c.choose_with_public_costs(0, 2, 0, reward_value=10), 0)

    def test_all_invalid_public_costs_rejected_without_mutation(self):
        c = PublicCausalCells()
        checkpoint = c.snapshot()
        for value in (-1, 65536, True, False, 2.0, "1", None):
            for which in (0, 1):
                costs = (value, 0) if which == 0 else (0, value)
                with self.subTest(value=value, which=which):
                    with self.assertRaises(ValueError):
                        c.choose_with_public_costs(0, *costs)
                    self.assertEqual(c.snapshot(), checkpoint)

    def test_invalid_reward_flags_and_addresses_rejected(self):
        c = PublicCausalCells()
        checkpoint = c.snapshot()
        for reward in (0, 65536, True, 1.5, "1", None):
            with self.subTest(reward=reward):
                with self.assertRaises(ValueError):
                    c.choose_with_public_costs(0, 0, 0, reward_value=reward)
        for address, retained in ((-1, False), (7, False), (9, True),
                                  (True, False), (0, 0)):
            with self.subTest(address=address, retained=retained):
                with self.assertRaises(ValueError):
                    c.choose_with_public_costs(address, 0, 0, retained=retained)
        self.assertEqual(c.snapshot(), checkpoint)

    def test_active_retained_and_cold_restore_independent(self):
        c = PublicCausalCells()
        for _ in range(4):
            c.observe(0, 0, 1)
            c.observe(0, 1, 0)
            c.observe(0, 0, 0, retained=True)
            c.observe(0, 1, 1, retained=True)
        checkpoint = c.snapshot()
        self.assertEqual(len(checkpoint), 164)
        copy = PublicCausalCells.restore(checkpoint)
        for model in (c, copy):
            self.assertEqual(model.choose_with_public_costs(0, 0, 0), 0)
            self.assertEqual(model.choose_with_public_costs(0, 0, 0, retained=True), 1)
            self.assertIsNone(model.choose_with_public_costs(1, 0, 0, retained=True))
            self.assertEqual(model.snapshot(), checkpoint)

    def test_counter_saturation_does_not_change_checkpoint(self):
        c = PublicCausalCells()
        c._counts[0][0] = [0, 65535]
        c._counts[0][1] = [65535, 0]
        before = c.snapshot()
        self.assertEqual(c.choose_with_public_costs(0, 0, 0), 0)
        self.assertEqual(c.choose_with_public_costs(0, 65535, 0), 1)
        self.assertEqual(c.snapshot(), before)

    def test_10000_seeded_cases_match_independent_fraction_oracle(self):
        from fractions import Fraction
        from random import Random

        rng = Random(20261030)
        c = PublicCausalCells()
        for case in range(10000):
            a = [rng.randrange(0, 65536), rng.randrange(0, 65536)]
            b = [rng.randrange(0, 65536), rng.randrange(0, 65536)]
            reward = rng.randrange(1, 65536)
            cost0 = rng.randrange(0, 65536)
            cost1 = rng.randrange(0, 65536)
            c._counts[0][0] = a
            c._counts[0][1] = b
            left_count, right_count = sum(a), sum(b)
            if left_count == 0 or right_count == 0:
                expect = None
            else:
                left = Fraction(a[1] * reward, left_count) - cost0
                right = Fraction(b[1] * reward, right_count) - cost1
                expect = None if left == right else 0 if left > right else 1
            prior = c.snapshot() if case % 2000 == 0 else None
            self.assertEqual(
                c.choose_with_public_costs(0, cost0, cost1, reward_value=reward),
                expect, msg=f"public oracle mismatch case={case}")
            if prior is not None:
                self.assertEqual(c.snapshot(), prior)



if __name__ == "__main__":
    unittest.main()
