"""Algebraic MR32-P tests; no episode or scientific cohort is executed."""
from __future__ import annotations

import unittest

from counterfactual_shapley import (
    COALITION_COUNT,
    DENOMINATOR,
    PLAYER_COUNT,
    Q16,
    CoalitionContractError,
    exact_shapley_numerators,
    leave_one_out_q16_credits,
    shapley_q16_credits,
    uniform_q16_credits,
)


def game(function):
    return {mask: int(function(mask)) for mask in range(COALITION_COUNT)}


class ShapleyAlgebraTests(unittest.TestCase):
    IDS = (50, 10, 70, 20, 60, 30, 40)

    def test_additive_game_returns_exact_player_effects(self):
        weights = (-3, 4, 2, -1, 5, 0, -2)
        values = game(
            lambda mask: 7 + sum(
                weights[i] for i in range(PLAYER_COUNT) if mask & (1 << i)
            )
        )
        numerators, delta = exact_shapley_numerators(self.IDS, values)
        self.assertEqual(delta, sum(weights))
        self.assertEqual(
            numerators,
            tuple(weight * DENOMINATOR for weight in weights),
        )
        credits, _, _ = shapley_q16_credits(self.IDS, values)
        self.assertEqual(credits, tuple(weight * Q16 for weight in weights))

    def test_pure_two_player_synergy_splits_credit_equally(self):
        values = game(lambda mask: int((mask & 0b11) == 0b11))
        credits, numerators, delta = shapley_q16_credits(self.IDS, values)
        self.assertEqual(delta, 1)
        self.assertEqual(numerators[0], DENOMINATOR // 2)
        self.assertEqual(numerators[1], DENOMINATOR // 2)
        self.assertEqual(credits[0], Q16 // 2)
        self.assertEqual(credits[1], Q16 // 2)
        self.assertEqual(credits[2:], (0, 0, 0, 0, 0))

    def test_seven_way_synergy_allocates_q16_remainder_by_immutable_id(self):
        values = game(lambda mask: int(mask == COALITION_COUNT - 1))
        credits, numerators, delta = shapley_q16_credits(self.IDS, values)
        self.assertEqual(delta, 1)
        self.assertEqual(numerators, (DENOMINATOR // 7,) * PLAYER_COUNT)
        self.assertEqual(sum(credits), Q16)
        base, remainder = divmod(Q16, PLAYER_COUNT)
        self.assertEqual(remainder, 2)
        expected = [base] * PLAYER_COUNT
        for index in (1, 3):  # smallest immutable IDs are 10 and 20
            expected[index] += 1
        self.assertEqual(credits, tuple(expected))

    def test_interchangeable_redundant_memories_split_shared_credit(self):
        values = game(lambda mask: int(bool(mask & 0b11)))
        credits, numerators, delta = shapley_q16_credits(self.IDS, values)
        self.assertEqual(delta, 1)
        self.assertEqual(numerators[0], DENOMINATOR // 2)
        self.assertEqual(numerators[1], DENOMINATOR // 2)
        self.assertEqual(credits[:2], (Q16 // 2, Q16 // 2))
        # Each single leave-one-out marginal is zero in a redundant pair.
        loo = leave_one_out_q16_credits(self.IDS, values)
        self.assertEqual(loo[:2], (0, 0))

    def test_harmful_memory_receives_negative_credit(self):
        # Player 0 suppresses the otherwise successful terminal task.
        values = game(lambda mask: int(not (mask & 1)))
        credits, numerators, delta = shapley_q16_credits(self.IDS, values)
        self.assertEqual(delta, -1)
        self.assertEqual(credits, (-Q16, 0, 0, 0, 0, 0, 0))
        self.assertEqual(numerators, (-DENOMINATOR, 0, 0, 0, 0, 0, 0))

    def test_null_players_receive_exactly_zero(self):
        values = game(lambda mask: int((mask & 0b11) == 0b11))
        credits, numerators, _ = shapley_q16_credits(self.IDS, values)
        self.assertEqual(credits[2:], (0, 0, 0, 0, 0))
        self.assertEqual(numerators[2:], (0, 0, 0, 0, 0))

    def test_order_permutation_preserves_credit_attached_to_player_id(self):
        original = game(lambda mask: int(
            bool(mask & 0b001) and (mask & 0b110) != 0
        ))
        original_credits, _, _ = shapley_q16_credits(self.IDS, original)
        expected_by_id = dict(zip(self.IDS, original_credits))

        order = (6, 2, 4, 0, 5, 1, 3)
        permuted_ids = tuple(self.IDS[index] for index in order)
        permuted_values = {}
        for new_mask in range(COALITION_COUNT):
            old_mask = 0
            for new_index, old_index in enumerate(order):
                if new_mask & (1 << new_index):
                    old_mask |= 1 << old_index
            permuted_values[new_mask] = original[old_mask]

        permuted_credits, _, _ = shapley_q16_credits(
            permuted_ids, permuted_values
        )
        self.assertEqual(dict(zip(permuted_ids, permuted_credits)), expected_by_id)

    def test_negative_q16_remainder_is_conserved(self):
        values = game(lambda mask: int(mask == 0))
        credits, _, delta = shapley_q16_credits(self.IDS, values)
        self.assertEqual(delta, -1)
        self.assertEqual(sum(credits), -Q16)
        base, remainder = divmod(-Q16, PLAYER_COUNT)
        self.assertEqual(remainder, 5)
        expected = [base] * PLAYER_COUNT
        for index in (1, 3, 5, 6, 0):
            expected[index] += 1
        self.assertEqual(credits, tuple(expected))

    def test_uniform_control_conserves_positive_and_negative_episode_delta(self):
        positive = game(lambda mask: int(mask == COALITION_COUNT - 1))
        negative = game(lambda mask: int(mask == 0))
        self.assertEqual(sum(uniform_q16_credits(self.IDS, positive)), Q16)
        self.assertEqual(sum(uniform_q16_credits(self.IDS, negative)), -Q16)

    def test_leave_one_out_control_is_raw_and_can_overcount_synergy(self):
        values = game(lambda mask: int((mask & 0b11) == 0b11))
        credits = leave_one_out_q16_credits(self.IDS, values)
        self.assertEqual(credits[:2], (Q16, Q16))
        self.assertEqual(sum(credits), 2 * Q16)

    def test_complete_coalition_table_is_required(self):
        values = game(lambda mask: int(mask == 0))
        del values[13]
        with self.assertRaisesRegex(CoalitionContractError, "COALITION_MASK_SET_MISMATCH"):
            shapley_q16_credits(self.IDS, values)

    def test_extra_coalition_mask_is_rejected(self):
        values = game(lambda mask: int(mask == 0))
        values[COALITION_COUNT] = 0
        with self.assertRaisesRegex(CoalitionContractError, "COALITION_MASK_SET_MISMATCH"):
            shapley_q16_credits(self.IDS, values)

    def test_duplicate_player_ids_are_rejected(self):
        values = game(lambda mask: int(mask == 0))
        ids = (1, 2, 3, 4, 5, 6, 1)
        with self.assertRaisesRegex(CoalitionContractError, "PLAYER_IDS_NOT_UNIQUE"):
            shapley_q16_credits(ids, values)

    def test_boolean_or_noninteger_terminal_values_are_rejected(self):
        values = game(lambda mask: int(mask == 0))
        values[0] = True
        with self.assertRaisesRegex(CoalitionContractError, "COALITION_VALUE_MUST_BE_INTEGER"):
            shapley_q16_credits(self.IDS, values)

        values[0] = 0.5
        with self.assertRaisesRegex(CoalitionContractError, "COALITION_VALUE_MUST_BE_INTEGER"):
            shapley_q16_credits(self.IDS, values)

    def test_wrong_player_count_is_rejected(self):
        values = game(lambda mask: int(mask == 0))
        with self.assertRaisesRegex(CoalitionContractError, "PLAYER_COUNT_MUST_BE_SEVEN"):
            shapley_q16_credits(self.IDS[:-1], values)


if __name__ == "__main__":
    unittest.main()
