"""WSP-207: fabricated-only asinh target and one-shot leak rejection."""
import math
import unittest

from learner import Learner, group_bucket, fit_stage, pair_group
from source_free_partition import SYNTHETIC_DIGEST, admit_synthetic_genotypes
from source_free_targets import SyntheticOneLook, asinh_interaction, group_weighted_rmse


GENE = "FABRICATED_TARGETS"


def fixture():
    rows = [dict(row_id="wt", gene=GENE,
                 aa_genotype_pseudo="wt", aa_genotype_native="wt")]
    labels = {"wt": 2.0}
    positions = []
    stages = {i:0 for i in range(4)}
    protected = {"PUBLIC_DEV":0, "RESERVED_UNTOUCHED":0}
    for pos in range(2, 1000):
        group = pair_group(GENE, 1, pos)
        bucket = group_bucket(group)
        if bucket == "FIT":
            st = fit_stage(group)
            if stages[st] >= 2:
                continue
            stages[st] += 1
        elif bucket in protected:
            if protected[bucket] >= 2:
                continue
            protected[bucket] += 1
        else:
            continue
        positions.append((pos, bucket))
        if all(n == 2 for n in stages.values()) and all(n == 2 for n in protected.values()):
            break
    assert len(positions) == 12
    rows.append(dict(row_id="s1", gene=GENE,
                     aa_genotype_pseudo="A1C", aa_genotype_native="A1C"))
    labels["s1"] = 1.5
    for p, bucket in positions:
        rows.append(dict(row_id=f"s{p}", gene=GENE,
                         aa_genotype_pseudo=f"A{p}C", aa_genotype_native=f"A{p}C"))
        rows.append(dict(row_id=f"d{p}", gene=GENE,
                         aa_genotype_pseudo=f"A1C:A{p}C", aa_genotype_native=f"A1C:A{p}C"))
        labels[f"s{p}"] = 1.0+p/1000
        labels[f"d{p}"] = 3.0+(p%17)/7
    return admit_synthetic_genotypes(rows, source_digest=SYNTHETIC_DIGEST), labels


class SyntheticTargetCustody(unittest.TestCase):
    def test_interaction_exact_and_numerical_fail_closed(self):
        expected = math.asinh(8.)-math.asinh(5.)-math.asinh(3.)+math.asinh(2.)
        self.assertEqual(expected, asinh_interaction(8.,5.,3.,2.))
        for vals in ((float("nan"), 2.,1.,1.), (1.,float("inf"),1.,1.),
                     (1.,2.,None,1.), (1.,2.,1.,True)):
            with self.assertRaises(ValueError):
                asinh_interaction(*vals)

    def test_future_stage_and_held_never_accessed_before_release(self):
        manifest, values = fixture()
        held_ids = {r.row_id for r in manifest.eligible if r.bucket != "FIT"}
        class Trap(dict):
            def __getitem__(self, key):
                if key in held_ids:
                    raise AssertionError("held/reserved label leaked into FIT")
                return super().__getitem__(key)
        gate = SyntheticOneLook(manifest, "wt", Trap(values),
                                source_digest=SYNTHETIC_DIGEST)
        with self.assertRaises(ValueError):
            gate.fit_stage(1)
        for stage in range(4):
            batch = gate.fit_stage(stage)
            self.assertEqual(2, len(batch))
            with self.assertRaises(ValueError):
                gate.fit_stage(stage)
            if stage < 3:
                with self.assertRaises(ValueError):
                    gate.public_dev_once()
        with self.assertRaises(AssertionError):
            gate.public_dev_once()
        self.assertTrue(gate.invalid)
        with self.assertRaises(ValueError):
            gate.public_dev_once()

    def test_only_one_held_look_and_no_reserved_values(self):
        manifest, vals = fixture()
        reserve_ids = {r.row_id for r in manifest.eligible if r.bucket == "RESERVED_UNTOUCHED"}
        class Trap(dict):
            def __getitem__(self, key):
                if key in reserve_ids:
                    raise AssertionError("reserved brightness touched")
                return super().__getitem__(key)
        gate = SyntheticOneLook(manifest, "wt", Trap(vals),
                                source_digest=SYNTHETIC_DIGEST)
        model = Learner(SYNTHETIC_DIGEST)
        for stage in range(4):
            model.advance(stage, gate.fit_stage(stage))
        held = gate.public_dev_once()
        self.assertEqual(2, len(held))
        self.assertTrue(math.isfinite(group_weighted_rmse(
            held, model.predict, model.mean, model.sd)))
        with self.assertRaises(ValueError):
            gate.public_dev_once()
        with self.assertRaises(ValueError):
            gate.fit_stage(3)

    def test_invalid_fit_label_cannot_be_silently_excluded_or_replayed(self):
        manifest, labels = fixture()
        bad = dict(labels)
        first = next(r for r in manifest.eligible if r.bucket == "FIT" and r.stage == 0)
        bad[first.row_id] = float("nan")
        gate = SyntheticOneLook(manifest, "wt", bad, source_digest=SYNTHETIC_DIGEST)
        with self.assertRaises(ValueError):
            gate.fit_stage(0)
        self.assertTrue(gate.invalid)
        with self.assertRaises(ValueError):
            gate.fit_stage(0)
        with self.assertRaises(ValueError):
            gate.public_dev_once()

    def test_fake_identity_restriction_and_group_equal_weight(self):
        manifest, labels = fixture()
        with self.assertRaises(ValueError):
            SyntheticOneLook(manifest, "wt", labels, source_digest="0"*64)
        from learner import Sample
        held = [Sample("a", "group1", "a", "b", 0),
                Sample("b", "group1", "a", "b", 0),
                Sample("c", "group2", "a", "b", 2)]
        expected = math.sqrt((0+4)/2)
        self.assertAlmostEqual(expected, group_weighted_rmse(
            held, lambda a,b:0, 0, 1))


if __name__ == "__main__":
    unittest.main()
