"""WSP-206 exact-state adjacency acceleration equivalence on fabricated data.

All controls use the same source-free observations.  The legacy reference is
intentionally O(addresses * observations) and not a second learner proposal.
"""
from __future__ import annotations
import math
import time
import unittest

from learner import Learner, Sample, LAMBDA, _solve_cholesky, fit_stage, group_bucket, pair_group


class LegacyFullScanLearner(Learner):
    """Pre-optimization sweep from WSP-201, preserved as a parity oracle."""

    def _sweep(self, active: set[str]) -> None:
        assert self.mean is not None and self.sd is not None
        for addr in sorted(active):
            mat = [[0.0] * self.rank for _ in range(self.rank)]
            rhs = [0.0] * self.rank
            for i in range(self.rank):
                mat[i][i] = LAMBDA
            for obs in self.samples:
                if addr != obs.left and addr != obs.right:
                    continue
                other = obs.right if addr == obs.left else obs.left
                features = self.weights[other]
                target = (obs.target-self.mean)/self.sd
                for i in range(self.rank):
                    rhs[i] += target*features[i]
                    for j in range(self.rank):
                        mat[i][j] += features[i]*features[j]
            self.weights[addr] = _solve_cholesky(mat, rhs)
            self.solves += 1


DIGEST = "f" * 64
GENE = "FABRICATED_INDEX"


def batches(count_per_stage: int = 60) -> list[list[Sample]]:
    all_batches: list[list[Sample]] = []
    for stage in range(4):
        groups = [pair_group(GENE, i, j) for i in range(1, 90)
                  for j in range(i+1, 90) if
                  group_bucket(pair_group(GENE, i, j)) == "FIT" and
                  fit_stage(pair_group(GENE, i, j)) == stage][:count_per_stage]
        assert len(groups) == count_per_stage
        batch: list[Sample] = []
        for group in groups:
            _, pos1, pos2 = group.split("\0")
            for allele in ("C", "D"):
                left = f"{GENE}\0{pos1}\0A\0{allele}"
                right = f"{GENE}\0{pos2}\0A\0{allele}"
                value = float((((int(pos1)*7+int(pos2)*11+(allele == "D")*5) % 17)-8)/3)
                batch.append(Sample(f"{stage}_{pos1}_{pos2}_{allele}",
                                    group, left, right, value))
        all_batches.append(batch)
    return all_batches


class IndexedSweepEquivalence(unittest.TestCase):
    def test_exact_byte_parity_all_stages_and_controls(self):
        data = batches(12)
        for mode, rank in (("contradiction",4),("full_refit",4),
                           ("full_refit",8),("always",4),
                           ("surprise",4),("random",4),("no_update",4),
                           ("shuffled_negative",4)):
            with self.subTest(mode=mode, rank=rank):
                old = LegacyFullScanLearner(DIGEST, mode, rank)
                indexed = Learner(DIGEST, mode, rank)
                candidate = Learner(DIGEST, "contradiction")
                for stage, batch in enumerate(data):
                    match = None
                    if stage and mode in ("surprise", "random"):
                        candidate.advance(stage, batch)
                        match = len(candidate.changed_by_stage[-1])
                    elif stage == 0 and mode in ("surprise", "random"):
                        candidate.advance(stage, batch)
                    kwargs = {"reference_write_count":match} if match is not None else (
                        {"reference_write_count":0} if stage and mode in ("surprise","random") else {})
                    old.advance(stage, batch, **kwargs)
                    indexed.advance(stage, batch, **kwargs)
                    self.assertEqual(old.checkpoint(), indexed.checkpoint())
                    self.assertEqual(old.solves, indexed.solves)
                    self.assertTrue(math.isfinite(old._objective()))

    def test_indexed_sweep_does_not_change_predictions(self):
        data = batches(10)[0]
        old, indexed = LegacyFullScanLearner(DIGEST), Learner(DIGEST)
        old.advance(0, data)
        indexed.advance(0, list(reversed(data)))
        self.assertEqual(old.checkpoint(), indexed.checkpoint())
        for left, right in ((a.left, b.right) for a in data[:5] for b in data[5:10]):
            self.assertEqual(old.predict(left, right), indexed.predict(left, right))

    def test_timed_dev_probe_printed_only_not_hard_speed_gate(self):
        # Reports relative engineering time on fabricated group structure.
        # Never interpret this as the frozen original-data >=2x cost result.
        sample = batches(40)
        result = {}
        for name, cls in (("legacy_scan", LegacyFullScanLearner),
                          ("indexed_scan", Learner)):
            model = cls(DIGEST, "contradiction")
            t0 = time.perf_counter_ns()
            for stage, stage_rows in enumerate(sample):
                model.advance(stage, stage_rows)
            result[name] = (time.perf_counter_ns()-t0, model.checkpoint())
        self.assertEqual(result["legacy_scan"][1], result["indexed_scan"][1])
        print("WSP206_SOURCE_FREE_DEV_INDEX_SPEED_RATIO=" +
              format(result["legacy_scan"][0]/result["indexed_scan"][0], ".4f"))


if __name__ == "__main__":
    unittest.main()
