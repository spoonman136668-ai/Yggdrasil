"""NKR-10: deterministic, independent tiny-graph negative and custody checks."""
from __future__ import annotations

from collections import defaultdict
import importlib.util
from pathlib import Path
import unittest

SCRIPT = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/NKR-10/mine_historical.py")
spec = importlib.util.spec_from_file_location("nkr10_historical", SCRIPT)
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)


class FakeReadOnlyImage:
    def __init__(self, rows):
        self.rows = tuple(sorted(rows))

    def __len__(self):
        return len(self.rows)

    def row_at(self, index):
        return self.rows[index]


def source_fixture():
    rows = []
    for s in range(1, 9):
        rows.extend([
            (s, 11, 100 + s),
            (s, 15, 1000 + s),
            (100 + s, 12, 1000 + s),
        ])
    return rows


def independent_exhaustive_reference(rows):
    edges = set(rows)
    outgoing = defaultdict(list)
    direct = defaultdict(set)
    for s, p, o in edges:
        outgoing[s].append((p, o))
        direct[(s, o)].add(p)
    subjects = defaultdict(set)
    for s, p1, y in sorted(edges):
        for p2, z in outgoing.get(y, ()):
            for p3 in direct.get((s, z), set()):
                if p3 not in (p1, p2):
                    subjects[(p3, p1, p2)].add(s)
    return sorted(
        [[*key, len(support)] for key, support in subjects.items()
         if len(support) >= research.MIN_SUPPORT],
        key=lambda x: (-x[3], x[0], x[1], x[2]),
    )


class HistoricalRuleMiningTests(unittest.TestCase):
    def test_independent_exact_witness_and_no_false_admission(self):
        rows = source_fixture()
        source = FakeReadOnlyImage(rows)
        before = source.rows
        actual = research.mine_bounded(source)
        independent = independent_exhaustive_reference(rows)
        self.assertEqual(independent, [[15, 11, 12, 8]])
        self.assertEqual(actual["top_templates_p3_p1_p2_support"], independent)
        self.assertEqual(actual["templates_at_min_support"], 1)
        self.assertEqual(actual["distinct_anchor_subjects"], 16)
        self.assertEqual(source.rows, before)
        self.assertEqual(actual["verified_new_real_world_facts"], 0)
        self.assertEqual(actual["identified_causal_laws"], 0)
        self.assertFalse(actual["scientific_pass"])
        self.assertFalse(actual["native_accepted"])
        self.assertFalse(actual["source_mutated"])

    def test_duplicate_source_rows_do_not_inflate_unique_subject_support(self):
        raw = source_fixture()
        raw.extend([(1, 15, 1001)] * 15)
        result = research.mine_bounded(FakeReadOnlyImage(raw))
        self.assertEqual(result["top_templates_p3_p1_p2_support"],
                         [[15, 11, 12, 8]])
        self.assertEqual(result["sampled_anchor_rows"], len(raw))

    def test_absent_composition_is_not_positive_or_negative_label(self):
        rows = [r for r in source_fixture() if r[1] != 12]
        result = research.mine_bounded(FakeReadOnlyImage(rows))
        self.assertEqual(result["top_templates_p3_p1_p2_support"], [])
        self.assertEqual(result["templates_at_min_support"], 0)
        self.assertFalse(result["absent_edges_are_negatives"])

    def test_first_eight_edges_cap_is_explicit_bias_not_completeness(self):
        rows = []
        for s in range(1, 9):
            for pred in range(1, 9):
                rows.append((s, pred, 20000 + pred * 100 + s))
            rows.extend([(s, 15, 1000 + s),
                         (s, 31, 100 + s),
                         (100 + s, 32, 1000 + s)])
        exhaustive = independent_exhaustive_reference(rows)
        self.assertEqual(exhaustive, [[15, 31, 32, 8]])
        sampled = research.mine_bounded(FakeReadOnlyImage(rows))
        self.assertEqual(sampled["top_templates_p3_p1_p2_support"], [])
        self.assertIn("FIRST_8", sampled["source_sample_bias"])

    def test_invalid_and_malformed_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "NKR10_EMPTY_SOURCE"):
            research.mine_bounded(FakeReadOnlyImage([]))
        with self.assertRaisesRegex(ValueError, "NKR10_WALL_BUDGET_INVALID"):
            research.mine_bounded(FakeReadOnlyImage(source_fixture()),
                                  max_seconds=1000)
        image = FakeReadOnlyImage(source_fixture())
        class Corrupt:
            def __len__(self):
                return len(image)
            def row_at(self, index):
                return (True, 2, 3) if index == 0 else image.row_at(index)
        with self.assertRaisesRegex(ValueError, "NKR10_MALFORMED_QPQ_ROW"):
            research.mine_bounded(Corrupt())

    def test_fixed_striding_is_ordered_no_hidden_sampling_choices(self):
        self.assertEqual(research._sample_indices(1), (0,))
        self.assertEqual(research._sample_indices(4), (0, 1, 2, 3))
        many = research._sample_indices(100000)
        self.assertEqual(len(many), research.MAX_ANCHORS)
        self.assertEqual(many[0], 0)
        self.assertEqual(many[-1], 99999)
        self.assertEqual(len(set(many)), len(many))


if __name__ == "__main__":
    unittest.main()
