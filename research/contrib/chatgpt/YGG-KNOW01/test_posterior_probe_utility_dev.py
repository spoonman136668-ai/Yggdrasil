"""KNOW19 frozen research-only source, native, retention and negative controls."""
import unittest
from posterior_probe_utility_dev import (
    TRAIN_A, TRAIN_B, HELD, SEEDS, ROLES, Facts,
    source_rows, subject, object_id, probe_patterns, public_pattern,
    candidates, consequence, disclosed_feedback, private_training_role,
    training_rows, pack_context, symbolic_fit, tree_fit, select_query, evaluate,
    prove,
)


class Know19Tests(unittest.TestCase):
    def test_frozen_source_and_seed_separation(self):
        self.assertEqual((TRAIN_A, TRAIN_B, HELD),
                         (3119, 3251, (3371, 3463, 3593)))
        self.assertEqual(len(set(SEEDS)), 5)
        self.assertTrue(set(SEEDS).isdisjoint(
            (1301, 1403, 1601, 1709, 1801,
             2111, 2221, 2333, 2441, 2551)))
        for seed in SEEDS:
            self.assertEqual(set(probe_patterns(seed)), set(range(16)))
            rows = source_rows(seed)
            self.assertEqual(len(rows), 64)
            self.assertEqual(len({q for q, p, o in rows}), 16)
            self.assertEqual(len({o for q, p, o in rows}), 8)
            self.assertEqual(source_rows(seed), rows)
            self.assertTrue(all(0 <= v < 2**32
                                for row in rows for v in row))

    def test_public_graph_is_same_for_all_private_roles(self):
        facts = Facts()
        for seed in SEEDS:
            before = tuple(public_pattern(facts, seed, e) for e in range(16))
            self.assertEqual(before, probe_patterns(seed))
            for role in ROLES:
                self.assertEqual(before, tuple(public_pattern(facts, seed, e)
                                               for e in range(16)))

    def test_one_world_post_action_label_including_singletons(self):
        for mask, pattern, action in (
            (15, 1, 1), (15, 7, 1),
            (15, 3, 1), (15, 3, 0),
            (15, 0, 1), (3, 1, 1),
            (3, 3, 1),
        ):
            for role in candidates(mask):
                witnessed = consequence(action, pattern, role)
                label, remaining = disclosed_feedback(
                    mask, pattern, action, witnessed)
                self.assertIn(role, candidates(remaining))
                self.assertEqual(label, int(action == 1 and 0 <
                    (pattern & mask).bit_count() < mask.bit_count()))
        for role in ROLES:
            label, remaining = disclosed_feedback(
                15, 1, 1, consequence(1, 1, role))
            self.assertEqual(label, 1)
            self.assertIn(remaining.bit_count(), (1, 3))

    def test_disjoint_candidate_contexts_genuine_new_b_inputs(self):
        f = Facts()
        a, b = training_rows(f, TRAIN_A), training_rows(f, TRAIN_B)
        self.assertEqual((len(a), len(b)), (160, 192))
        self.assertFalse({(x, act) for x, act, y in a} &
                         {(x, act) for x, act, y in b})
        self.assertEqual(len({(x, act) for x, act, y in a+b}), 352)
        self.assertTrue(all(candidates(x >> 4) for x, act, y in a+b))
        self.assertTrue(all(y in (0, 1) for x, act, y in a+b))
        for seed, rows in ((TRAIN_A, a), (TRAIN_B, b)):
            for x, act, observed_label in rows:
                mask, pattern = x >> 4, x & 15
                role = private_training_role(seed, mask, pattern, act)
                output = consequence(act, pattern, role)
                self.assertEqual(disclosed_feedback(mask, pattern, act, output)[0],
                                 observed_label)

    def test_two_fully_trained_baselines_have_same_labels(self):
        f = Facts()
        rows = training_rows(f, TRAIN_A) + training_rows(f, TRAIN_B)
        symbolic, tree = symbolic_fit(rows), tree_fit(rows)
        self.assertTrue(all(symbolic(x, act) == y and tree(x, act) == y
                            for x, act, y in rows))
        self.assertIsNone(symbolic(0, 0))

    def test_source_forgery_conflicts_and_invalid_types_abstain(self):
        f = Facts()
        seed = HELD[0]
        pattern = public_pattern(f, seed, 0)
        q = subject(seed, 0)
        o = object_id(0, pattern & 1)
        f.rows[seed].remove((q, 981, o))
        with self.assertRaisesRegex(ValueError, "MISSING_CONFLICTING"):
            public_pattern(f, seed, 0)
        f.rows[seed].add((q, 981, o))
        f.rows[seed].add((q, 981, object_id(0, 1-(pattern & 1))))
        with self.assertRaisesRegex(ValueError, "MISSING_CONFLICTING"):
            public_pattern(f, seed, 0)
        with self.assertRaisesRegex(ValueError, "MISSING_CONFLICTING"):
            public_pattern(Facts(mode="claimed_owner"), seed, 0)
        with self.assertRaisesRegex(ValueError, "MISSING_CONFLICTING"):
            public_pattern(Facts(provenance="self_signed"), seed, 0)
        for bad in (True, -1, 16):
            with self.assertRaises(ValueError):
                pack_context(15, bad)
        with self.assertRaises(ValueError):
            consequence(True, 1, 0)

    def test_role_independent_policy_and_two_action_cap(self):
        f = Facts()
        for seed in HELD:
            for role in ROLES:
                result = evaluate(f, seed, role, "oracle")
                self.assertLessEqual(result["witnessed_actions"], 2)
                self.assertIn(result["selected"], (None, role))
                self.assertEqual(evaluate(f, seed, role, "zero")["witnessed_actions"], 0)
                self.assertIsNone(evaluate(f, seed, role, "passive")["selected"])
        self.assertIsNone(select_query(f, HELD[0], ROLES, set(),
                                       lambda ctx, a: None))

    def test_native_checkpoint_replay_and_primary_frozen_scoring(self):
        # The original native fitter lives exclusively on pinned Amalgam source.
        # Focused checkouts must not import an unowned copy; compatibility CI
        # runs prove() with the original SHA-pinned source in a temp namespace.
        try:
            import yggdrasil.native_context_accumulator
        except ModuleNotFoundError as exc:
            if exc.name == 'yggdrasil.native_context_accumulator':
                self.skipTest('KNOW19 native qualification runs against pinned Amalgam archive')
            raise
        result = prove()  # one deterministic synthetic trial; never owner source
        self.assertEqual(result["prereg_commit"],
                         "dfd1dd6c536c25e9fdaf99884ee9973b86fce16b")
        self.assertEqual((result["train_A_actions"],
                          result["train_B_actions"]), (160, 192))
        self.assertEqual(result["training_witnessed_actions"], 352)
        self.assertEqual(result["new_B_public_input_cells"], 192)
        self.assertEqual(result["old_A_predictions_changed"], 0)
        self.assertIn(result["engineering_gate"], ("PASS", "FAIL"))
        self.assertEqual(result["scientific_gate"],
                         "DEV_NO_GO_SYNTHETIC_AND_STRONGEST_CONTROL")
        self.assertFalse(result["accepted_checkpoint_changed"])
        self.assertFalse(result["original_world_first_use"])
        for control in ("native", "refit", "symbolic", "tree",
                        "oracle", "random", "passive", "zero"):
            self.assertEqual(set(result["held"][control]),
                             {"correct", "actions", "remaining_candidates",
                              "posterior_entropy_bits"})
        self.assertEqual(result["singleton_1v3_diagnostic"]
                         ["zero_action_abstentions"], 0)


if __name__ == "__main__":
    unittest.main()
