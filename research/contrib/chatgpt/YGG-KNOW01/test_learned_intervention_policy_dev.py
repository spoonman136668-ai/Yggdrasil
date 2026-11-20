"""KNOW17: no-original-source training/transfer protocol and controls."""
import unittest
from fractions import Fraction
from learned_intervention_policy_dev import (
    SEEDS, TRAIN, TRANSFER, ROLES, PROBE, HELD, PREDS,
    patterns, subject, object_id, source_rows, public_bits, balanced,
    outcome, update, training_rows, symbolic_utility, tree_utility,
    policy_query, attempt
)


class SourceDouble:
    def __init__(self, *, tamper=False, mode="engineering_fixture_only"):
        self.rows = {(q, p, o) for seed in SEEDS
                     for q, p, o, witness in source_rows(seed)}
        self.mode = mode
        self.tamper = tamper

    def fact(self, q, p, o):
        present = (q, p, o) in self.rows
        return {
            "classification": (
                "DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
                if present else "UNKNOWN_ABSTAIN"),
            "witnessed": present,
            "source_mode": self.mode,
            "source_provenance": (
                "SELF_ASSERTED_REAL" if self.tamper
                else "SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED"),
            "native_accepted": False,
            "verified_new_real_knowledge": False,
            "can_write_causal_consequence": False
        }


class TestKnow17(unittest.TestCase):
    def test_fixed_split_and_nonreused_know16_seeds(self):
        self.assertEqual(TRAIN, (1301, 1403))
        self.assertEqual(TRANSFER, (1601, 1709, 1801))
        self.assertEqual(len(set(SEEDS)), 5)
        self.assertTrue({401, 509, 617}.isdisjoint(SEEDS))

    def test_source_role_independent_identifiers_and_marginals(self):
        for seed in SEEDS:
            rows = source_rows(seed)
            self.assertEqual(len(rows), 136)
            self.assertEqual(len({q for q, p, o, w in rows}), 34)
            self.assertEqual(len({o for q, p, o, w in rows}), 8)
            for role in ROLES:
                self.assertEqual(rows, source_rows(seed))
                self.assertEqual(sum((v >> role) & 1
                                     for v in patterns(seed)), 17)
            self.assertEqual(sorted(patterns(seed)[:16]), list(range(16)))
            self.assertEqual(sorted(patterns(seed)[18:]), list(range(16)))

    def test_strict_source_abstention(self):
        facts = SourceDouble()
        q = subject(TRAIN[0], 0)
        bits = public_bits(facts, TRAIN[0], 0)
        self.assertEqual(len(bits), 4)
        role = 0
        facts.rows.remove((q, PREDS[role], object_id(role, bits[role])))
        with self.assertRaisesRegex(ValueError, "SOURCE_FACT_ABSTAIN"):
            public_bits(facts, TRAIN[0], 0)
        facts.rows.add((q, PREDS[role], object_id(role, bits[role])))
        facts.rows.add((q, PREDS[role], object_id(role, 1-bits[role])))
        with self.assertRaisesRegex(ValueError, "SOURCE_FACT_ABSTAIN"):
            public_bits(facts, TRAIN[0], 0)
        with self.assertRaisesRegex(ValueError, "SOURCE_FACT_ABSTAIN"):
            public_bits(SourceDouble(tamper=True), TRAIN[0], 0)
        with self.assertRaisesRegex(ValueError, "SOURCE_FACT_ABSTAIN"):
            public_bits(SourceDouble(mode="claimed_owner"), TRAIN[0], 0)

    def test_utility_labels_derived_only_after_witness(self):
        src = SourceDouble()
        A, B = training_rows(src, TRAIN[0]), training_rows(src, TRAIN[1])
        self.assertEqual((len(A), len(B)), (16, 20))
        for row in A+B:
            c, action, utility = row
            self.assertEqual(utility, c*action)
        self.assertEqual({(c, a) for c, a, y in A+B},
                         {(0,0),(0,1),(1,0),(1,1)})

    def test_matched_exact_symbolic_and_conventional_fits(self):
        src = SourceDouble()
        fit = training_rows(src, TRAIN[0])+training_rows(src, TRAIN[1])
        symbolic = symbolic_utility(fit)
        tree = tree_utility(fit)
        for c in (0,1):
            for a in (0,1):
                self.assertEqual(symbolic[c,a], Fraction(c*a))
                self.assertEqual(tree(c,a), Fraction(c*a))

    def test_two_step_held_policy_matches_oracle_and_symbolic(self):
        src=SourceDouble()
        fit=training_rows(src,TRAIN[0])+training_rows(src,TRAIN[1])
        table=symbolic_utility(fit)
        for seed in TRANSFER:
            for role in ROLES:
                learned=attempt(src,seed,role,lambda c,a:table[c,a])
                analytic=attempt(src,seed,role,"oracle")
                self.assertEqual(learned["selected"],role)
                self.assertEqual(learned,analytic)
                self.assertEqual(learned["action_count"],2)
                self.assertIsNone(attempt(src,seed,role,"zero")["selected"])
                self.assertIsNone(attempt(src,seed,role,"passive")["selected"])

    def test_source_only_cannot_identify_hidden_role(self):
        src=SourceDouble()
        for seed in TRANSFER:
            source_graph=source_rows(seed)
            for secret in ROLES:
                self.assertEqual(source_graph,source_rows(seed))
                self.assertEqual(len(ROLES),4)

    def test_public_candidate_partition_balanced_feature(self):
        src=SourceDouble();seed=TRANSFER[0]
        patterns_now={p:patterns(seed).index(p) for p in range(16)}
        self.assertEqual(balanced(public_bits(src,seed,patterns_now[3]),ROLES),1)
        self.assertEqual(balanced(public_bits(src,seed,patterns_now[0]),ROLES),0)
        self.assertEqual(update((0,0,1,1),ROLES,1,0),(0,1))
        self.assertEqual(update((0,0,1,1),ROLES,0,0),ROLES)

    def test_missing_source_is_not_silently_utilized(self):
        src=SourceDouble(mode="claimed_real")
        with self.assertRaisesRegex(ValueError,"SOURCE_FACT_ABSTAIN"):
            policy_query(src,TRANSFER[0],ROLES,set(),
                         lambda c,a:Fraction(c*a))

    def test_cold_learner_interface_not_accepted_owner(self):
        import learned_intervention_policy_dev as m
        for forbidden in ("activate", "merge", "deploy", "schedule",
                          "write_canonical", "observe_experience",
                          "owner_controller", "automatic_promotion"):
            self.assertFalse(hasattr(m,forbidden))

    def test_inputs_reject_invalid_bool_identifiers(self):
        for invalid in (True,-1,34):
            with self.assertRaises(ValueError):
                subject(SEEDS[0],invalid)
        for invalid in (True,-1,2):
            with self.assertRaises(ValueError):
                outcome(invalid,0)


if __name__ == "__main__":
    unittest.main()
