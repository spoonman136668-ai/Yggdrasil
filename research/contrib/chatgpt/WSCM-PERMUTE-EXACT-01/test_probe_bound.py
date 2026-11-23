"""Independent full-enumeration verification of the bounded exact control."""
import collections
import itertools
import unittest

import probe_bound as b


def independent_step(pos, role):
    # Independently reconstructed state update from original source semantics.
    deltas = ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0))
    dx, dy = deltas[role]
    return tuple(max(0, min(8, a + d)) for a, d in zip(pos, (dx, dy)))


def run_policy(hidden_perm, first=(0,0), cap=7):
    pos = first
    remaining = set(range(120))
    history = []
    for time in range(cap):
        if len(remaining) == 1:
            break
        mask = sum(1 << i for i in remaining)
        public_action = b.policy_action(mask, pos, cap-time)
        if public_action is None:
            raise AssertionError((time, pos, len(remaining), history))
        newpos = independent_step(pos, hidden_perm[public_action])
        remaining = {j for j in remaining
                     if independent_step(pos, b.PERMS[j][public_action]) == newpos}
        history.append((public_action, pos, newpos))
        pos = newpos
    return remaining, history


class OriginalSourceSemanticsTests(unittest.TestCase):
    def test_source_movement_semantics_interior_and_boundary(self):
        for role in range(5):
            self.assertEqual(b.next_position((4,4),role),independent_step((4,4),role))
            self.assertEqual(b.next_position((0,0),role),independent_step((0,0),role))
            self.assertEqual(b.next_position((8,8),role),independent_step((8,8),role))

    def test_rejects_invalid_public_actions(self):
        for bad in (-1, 5, True, False, 0.0, '2'):
            with self.assertRaises(ValueError):
                b.outcome_masks((0,0),bad)
        for pos in ((-1,0), (9,0), [0,0], (True,0)):
            with self.assertRaises(ValueError):
                b.next_position(pos,0)

    def test_corner_first_outcome_partition(self):
        sizes = collections.Counter(mask.bit_count() for _,mask in b.outcome_masks((0,0),0))
        self.assertEqual(sizes, {24:2,72:1})
        self.assertEqual(sum(size*count for size,count in sizes.items()),120)

    def test_120_permutations_and_corner_one_state_full_table_alias(self):
        self.assertEqual(len(b.PERMS),120)
        signature = collections.Counter(tuple(independent_step((0,0),p[a]) for a in range(5))
                                        for p in b.PERMS)
        self.assertEqual(len(signature),20)
        self.assertEqual(set(signature.values()),{6})

    def test_corner_six_impossible_seven_possible(self):
        self.assertFalse(b.feasible(b.FULL,(0,0),6))
        self.assertTrue(b.feasible(b.FULL,(0,0),7))

    def test_interior_three_impossible_four_possible(self):
        self.assertFalse(b.feasible(b.FULL,(4,4),3))
        self.assertTrue(b.feasible(b.FULL,(4,4),4))

    def test_optimized_policy_replay_all_120_without_hidden_role_leak(self):
        total = b.min_total_cost(b.FULL,(0,0),7)
        depths=collections.Counter()
        for true_idx, permutation in enumerate(b.PERMS):
            final_set,path = run_policy(permutation)
            self.assertEqual(final_set,{true_idx}, (true_idx,path))
            self.assertLessEqual(len(path),7)
            depths[len(path)]+=1
        self.assertEqual(sum(depth*count for depth,count in depths.items()),total)
        self.assertEqual(sum(depths.values()),120)

    def test_no_information_at_corner_is_not_labeled_no_op(self):
        # Three roles produce no displacement at the corner, not just the no-op.
        alias=[r for r in range(5) if independent_step((0,0),r)==(0,0)]
        self.assertEqual(alias,[1,3,4])

    def test_outcome_partition_covers_every_hypothesis_once(self):
        for start in ((0,0),(4,4),(8,8)):
            for action in range(5):
                parts=b.outcome_masks(start,action)
                self.assertEqual(sum(mask.bit_count() for _,mask in parts),120)
                self.assertEqual(sum(mask for _,mask in parts),b.FULL)

if __name__=='__main__':
    unittest.main()
