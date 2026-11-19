"""Deterministic source-free tests for the opt-in, read-only relation proposer."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

RESEARCH = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
SPEC = spec_from_file_location("amalgam_relation_shadow_for_tests", RESEARCH / "relation_shadow.py")
RELATION = module_from_spec(SPEC)
SPEC.loader.exec_module(RELATION)


def row(index, context, first, outcome):
    identifier = sha256(f"shadow-fixture-{index}".encode("ascii")).hexdigest()
    return (identifier, ((context, 0), (context, 1)), first, outcome, 0, 1)


def ledger(relationship, *, contexts=(0, 1, 2), count=40):
    records = []
    for context in contexts:
        for first in (0, 1):
            for j in range(count):
                # Deterministic source-free rule fixtures; not scientific worlds.
                if relationship == "complement":
                    outcome = int(j >= (count * (0.8 if first else 0.2)))
                elif relationship == "equal":
                    outcome = int(j >= count * 0.2)
                elif relationship == "independent":
                    outcome = int(j >= count * (0.5 if first else 0.2))
                else:
                    raise AssertionError("unexpected fixture rule")
                records.append(row(len(records), context, first, outcome))
    return records


class NativeRelationShadowTests(unittest.TestCase):
    def test_complement_rule_across_two_other_contexts(self):
        records = ledger("complement") + [row(10000 + k, 3, 0, int(k >= 6)) for k in range(10)]
        proposed = RELATION.RelationShadow(records).propose(3, 1)
        self.assertGreater(proposed["posterior"]["complement"], 0.95)
        self.assertGreater(proposed["forecast"], 0.55)
        self.assertEqual(proposed["decision_authority"], "NONE_SHADOW_ONLY")
        self.assertEqual(proposed["independent_contrast_contexts"], 3)

    def test_equal_rule_rejects_forced_complement(self):
        records = ledger("equal") + [row(10000 + k, 3, 0, int(k >= 6)) for k in range(10)]
        proposed = RELATION.RelationShadow(records).propose(3, 1)
        self.assertGreater(proposed["posterior"]["equal"], 0.95)
        self.assertLess(proposed["forecast"], 0.6)

    def test_independent_rule_can_win(self):
        records = ledger("independent", count=200) + [row(10000 + k, 3, 0, 0) for k in range(10)]
        p = RELATION.RelationShadow(records).propose(3, 1)
        self.assertGreater(p["posterior"]["independent"], 0.95)
        self.assertAlmostEqual(p["forecast"], 0.5, places=2)

    def test_target_cell_must_be_unobserved(self):
        self.assertIsNone(RELATION.RelationShadow(ledger("complement")).propose(1, 0))

    def test_target_other_action_must_be_witnessed(self):
        self.assertIsNone(RELATION.RelationShadow(ledger("complement")).propose(3, 1))

    def test_at_least_one_other_bidirectional_context(self):
        records = [row(k, k % 3, 0, 0) for k in range(12)]
        self.assertIsNone(RELATION.RelationShadow(records).propose(0, 1))

    def test_replay_order_invariance_for_scores(self):
        records = ledger("complement") + [row(10000 + k, 3, 0, k % 2) for k in range(10)]
        first = RELATION.RelationShadow(records).propose(3, 1)
        reverse = RELATION.RelationShadow(records[::-1]).propose(3, 1)
        for hypothesis in RELATION.HYPOTHESES:
            self.assertAlmostEqual(first["posterior"][hypothesis],
                                   reverse["posterior"][hypothesis], places=13)
        self.assertAlmostEqual(first["forecast"], reverse["forecast"], places=13)

    def test_input_ledger_is_never_modified(self):
        records = ledger("equal")
        original = tuple(records)
        RELATION.RelationShadow(records).propose(2, 0)
        self.assertEqual(tuple(records), original)

    def test_duplicate_witness_fails_closed(self):
        records = ledger("equal")
        with self.assertRaisesRegex(ValueError, "RELATION_DUPLICATE_WITNESS"):
            RELATION.RelationShadow(records + [records[0]])

    def test_conflicting_public_views_fail_closed(self):
        bad = list(row(0, 0, 0, 0))
        bad[1] = ((0, 0), (1, 0))
        with self.assertRaisesRegex(ValueError, "RELATION_PUBLIC_CONTEXT"):
            RELATION.RelationShadow([tuple(bad)])

    def test_nonbinary_or_invalid_receipt_fails_closed(self):
        bad = list(row(0, 0, 0, 0))
        bad[3] = 2
        with self.assertRaisesRegex(ValueError, "RELATION_PUBLIC_BIT_REQUIRED"):
            RELATION.RelationShadow([tuple(bad)])
        bad = list(row(0, 0, 0, 0))
        bad[0] = "not-a-receipt"
        with self.assertRaisesRegex(ValueError, "RELATION_WITNESS_ID"):
            RELATION.RelationShadow([tuple(bad)])

    def test_no_contrast_does_not_leak_prior_as_confident_forecast(self):
        records = [row(k, 0, 0, k % 2) for k in range(12)]
        self.assertIsNone(RELATION.RelationShadow(records).propose(0, 1))


if __name__ == "__main__":
    unittest.main()
