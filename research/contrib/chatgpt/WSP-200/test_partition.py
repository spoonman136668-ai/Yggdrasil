"""WSP-204 adversarial structural-intake tests; all genotype rows are fabricated."""
import unittest

from source_free_partition import (SYNTHETIC_DIGEST, admit_synthetic_genotypes,
                                   parse_genotype)
from learner import group_bucket, fit_stage, pair_group

GENE = "FABRICATED_PARTITION"


def row(rid, pseudo, gene=GENE, native="synthetic-native-sequence"):
    return dict(row_id=rid, gene=gene, aa_genotype_pseudo=pseudo,
                aa_genotype_native=native)


def fixture():
    rows = [row("wt", "wt"), row("s1B", "A1C"), row("s2C", "C2D"),
            row("s3B", "F3G")]
    rows += [row("d12", "A1C:C2D"), row("d23", "C2D:F3G"),
             row("d13", "A1C:F3G"), row("missing", "C2E:F3H"),
             row("higher", "A1C:C2D:F3G"), row("stop", "A1*:C2D")]
    return rows


class PartitionAdversarial(unittest.TestCase):
    def test_structural_counts_and_partitions_without_targets(self):
        got = admit_synthetic_genotypes(fixture(), source_digest=SYNTHETIC_DIGEST)
        self.assertEqual(got.counts["observed_rows"], 10)
        self.assertEqual(got.counts["strict_double"], 4)
        self.assertEqual(got.counts["eligible_double"], 3)
        self.assertEqual(got.counts["excluded_missing_parent"], 1)
        self.assertEqual(got.counts["excluded_nonstandard_or_higharity"], 2)
        self.assertEqual(got.counts["source_free_groups"], 3)
        self.assertEqual(sum(got.groups_per_bucket.values()), 3)
        for sample in got.eligible:
            self.assertEqual(group_bucket(sample.group), sample.bucket)
            self.assertEqual(fit_stage(sample.group) if sample.bucket == "FIT" else None,
                             sample.stage)
            self.assertTrue(sample.parent_ids)
            self.assertFalse(hasattr(sample, "brightness"))
            self.assertFalse(hasattr(sample, "target"))

    def test_never_reads_target_column_even_with_poison(self):
        class Poison(dict):
            def __getitem__(self, key):
                if key in ("replicates_mean_brightness", "n_replicates", "total_cell_count"):
                    raise AssertionError("forbidden numerical outcome touched")
                return super().__getitem__(key)
        rows = [Poison(x, replicates_mean_brightness=object(),
                       n_replicates=object(), total_cell_count=object()) for x in fixture()]
        first = admit_synthetic_genotypes(rows, source_digest=SYNTHETIC_DIGEST)
        second = admit_synthetic_genotypes(list(reversed(rows)), source_digest=SYNTHETIC_DIGEST)
        self.assertEqual(first, second)

    def test_standard_aa_zero_based_and_order_invariance(self):
        self.assertEqual((('A',0,'C'),), parse_genotype("A0C"))
        self.assertEqual(parse_genotype("A1C:C2D"), parse_genotype("C2D:A1C"))
        self.assertIsNone(parse_genotype("A01C"))
        self.assertIsNone(parse_genotype("A1A"))
        self.assertIsNone(parse_genotype("A1*:C2D"))
        self.assertIsNone(parse_genotype("A1C:C2D:F3G"))
        with self.assertRaises(ValueError):
            parse_genotype("A1C:A1C")

    def test_reject_duplicate_canonical_genotype(self):
        with self.assertRaisesRegex(ValueError, "duplicate canonical"):
            admit_synthetic_genotypes(fixture() + [row("duplicate", "C2D:A1C")],
                                      source_digest=SYNTHETIC_DIGEST)
        with self.assertRaisesRegex(ValueError, "duplicate.*receipt"):
            admit_synthetic_genotypes(fixture() + [row("d12", "A1C:F3G")],
                                      source_digest=SYNTHETIC_DIGEST)

    def test_reject_reference_and_wildtype_errors(self):
        for rows, message in (
            ([r for r in fixture() if r["row_id"] != "wt"], "wildtype"),
            (fixture() + [row("s1X", "Z1C")], ""),
            (fixture() + [row("s1conflict", "C1D")], "conflicting"),
            (fixture() + [row("wt2", "wt")], "duplicate canonical"),
        ):
            if not message:
                # Nonstandard (Z) is structurally excluded, not a parsed allele.
                got = admit_synthetic_genotypes(rows, source_digest=SYNTHETIC_DIGEST)
                self.assertEqual(got.counts["excluded_nonstandard_or_higharity"], 3)
            else:
                with self.assertRaisesRegex(ValueError, message):
                    admit_synthetic_genotypes(rows, source_digest=SYNTHETIC_DIGEST)

    def test_fail_closed_on_non_fabricated_data_or_digest(self):
        with self.assertRaisesRegex(ValueError, "digest fence"):
            admit_synthetic_genotypes(fixture(), source_digest="0" * 64)
        with self.assertRaisesRegex(ValueError, "not demonstrably synthetic"):
            admit_synthetic_genotypes([row("real", "wt", gene="amacGFP")],
                                      source_digest=SYNTHETIC_DIGEST)
        with self.assertRaisesRegex(ValueError, "native identity"):
            admit_synthetic_genotypes([row("wt", "wt", native="")],
                                      source_digest=SYNTHETIC_DIGEST)

    def test_partition_group_custody_on_unseen_site_pairs(self):
        rows = [row("wt", "wt")]
        for p in range(1, 15):
            rows.append(row(f"s{p}", f"A{p}C"))
        for p in range(1, 15):
            for q in range(p+1, 15):
                rows.append(row(f"d{p}_{q}", f"A{p}C:A{q}C"))
        m = admit_synthetic_genotypes(rows, source_digest=SYNTHETIC_DIGEST)
        groups_by_bucket = {}
        for item in m.eligible:
            groups_by_bucket.setdefault(item.bucket, set()).add(item.group)
            self.assertEqual(item.group, pair_group(GENE,item.mutations[0][1],item.mutations[1][1]))
        names = list(groups_by_bucket)
        for i,a in enumerate(names):
            for b in names[i+1:]:
                self.assertFalse(groups_by_bucket[a] & groups_by_bucket[b])
        self.assertEqual(len(m.eligible), 91)
        self.assertEqual(len(set(x.group for x in m.eligible)), 91)


if __name__ == "__main__":
    unittest.main()
