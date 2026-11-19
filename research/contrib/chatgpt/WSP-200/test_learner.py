"""Independent fabricated-data validation; no published experiment outcomes."""
import hashlib
import math
import unittest

from learner import Learner, Sample, pair_group, group_bucket, fit_stage, _solve_cholesky

DIGEST = "f" * 64  # sentinel only; NOT a claim about GFP input
GENE = "FABRICATED"


def address(pos: int, allele: str) -> str:
    return f"{GENE}\0{pos}\0A\0{allele}"


def stage_fixture(stage: int, count: int = 8) -> list[Sample]:
    groups = [pair_group(GENE, 1, p) for p in range(2, 500)
              if group_bucket(pair_group(GENE, 1, p)) == "FIT"
              and fit_stage(pair_group(GENE, 1, p)) == stage][:count]
    assert len(groups) == count
    out = []
    for i, group in enumerate(groups):
        pos = int(group.rsplit("\0", 1)[1])
        for alt in ("B", "C"):
            # Shared address 1 appears in multiple independent site-pair groups.
            out.append(Sample(f"stage{stage}_{i}_{alt}", group,
                              address(1, "B"), address(pos, alt),
                              (i % 4 - 1.5) if stage == 0 else 50.0 + stage))
    return out


class WSP200SourceFree(unittest.TestCase):
    def test_splits_are_stable_and_disjoint(self):
        found = {x:0 for x in ("FIT", "VALID", "PUBLIC_DEV", "RESERVED_UNTOUCHED")}
        for pos in range(2, 200):
            g = pair_group(GENE, 1, pos)
            found[group_bucket(g)] += 1
        self.assertTrue(all(found.values()))
        self.assertEqual(pair_group(GENE, 9, 2), pair_group(GENE, 2, 9))
        with self.assertRaises(ValueError):
            fit_stage(next(pair_group(GENE, 1, p) for p in range(2, 500)
                           if group_bucket(pair_group(GENE, 1, p)) == "PUBLIC_DEV"))

    def test_ridge_solver_against_known_solution(self):
        sol = _solve_cholesky([[4, 1], [1, 3]], [1, 2])
        self.assertAlmostEqual(sol[0], 1/11)
        self.assertAlmostEqual(sol[1], 7/11)
        with self.assertRaises(ArithmeticError):
            _solve_cholesky([[-1.0]], [1])

    def test_stage_progression_cold_restore_transactionality(self):
        model = Learner(DIGEST)
        b0, b1, b2, b3 = [stage_fixture(k) for k in range(4)]
        with self.assertRaises(ValueError):
            model.advance(1, b1)
        self.assertEqual(model.stage, -1)
        model.advance(0, b0)
        b0_preds = [model.predict(s.left, s.right) for s in b0]
        before = model.checkpoint()
        self.assertEqual(before, Learner.restore(before, DIGEST).checkpoint())
        self.assertEqual(b0_preds, [Learner.restore(before, DIGEST).predict(s.left, s.right) for s in b0])
        with self.assertRaises(ValueError):
            model.advance(1, b0)   # B0 evidence cannot be replayed as B1
        self.assertEqual(before, model.checkpoint())
        model.advance(1, b1)
        self.assertTrue(model.changed_by_stage[-1])
        for stage, batch in ((2,b2),(3,b3)):
            model.advance(stage, batch)
            data = model.checkpoint()
            self.assertEqual(data, Learner.restore(data, DIGEST).checkpoint())
        self.assertEqual(len(model.receipts), 64)
        frozen = model.checkpoint()
        with self.assertRaises(ValueError):
            model.advance(3, b3)
        self.assertEqual(frozen, model.checkpoint())
        with self.assertRaises(ValueError):
            Learner.restore(frozen, "0" * 64)
        with self.assertRaises(ValueError):
            Learner.restore(frozen.replace(b'wsp200.source-free.v1', b'unknown.schema.version'), DIGEST)

    def test_controls_and_no_update(self):
        for mode, rank in (("full_refit",4),("full_refit",8),("always",4),
                           ("surprise",4),("random",4),("no_update",4)):
            with self.subTest(mode=mode, rank=rank):
                learner = Learner(DIGEST, mode, rank)
                learner.advance(0, stage_fixture(0))
                original = learner.weights[address(1, "B")][:]
                learner.advance(1, stage_fixture(1))
                self.assertTrue(math.isfinite(learner.predict(address(1,"B"),address(4,"B"))))
                if mode == "no_update":
                    self.assertEqual(original, learner.weights[address(1, "B")])
                    self.assertEqual([], learner.changed_by_stage[1])
                elif mode == "full_refit":
                    self.assertTrue(learner.convergence[1]["converged"])

    def test_reject_duplicate_nonfinite_and_future_leak(self):
        learner = Learner(DIGEST)
        batch = stage_fixture(0)
        self.assertRaises(ValueError, learner.advance, 0, [batch[0],batch[0]])
        self.assertEqual(-1, learner.stage)
        bad = [Sample(batch[0].sample_id, batch[0].group, batch[0].left, batch[0].right, float('nan'))]
        self.assertRaises(ValueError, learner.advance, 0, bad)
        self.assertEqual(-1, learner.stage)
        self.assertRaises(ValueError, learner.advance, 0, stage_fixture(1))
        self.assertEqual(-1, learner.stage)
        alternate = Sample("other", pair_group("OTHER", 1, 4), "OTHER\0" + "1\0A\0B", "OTHER\0" + "4\0A\0B", 1.0)
        # Mixing protein backgrounds within a learner must not silently happen.
        mixed = [batch[0]] + [alternate]
        self.assertRaises(ValueError, learner.advance, 0, mixed)
        # Invalid group/address linkage is a hard stop.
        wrong = [Sample(batch[0].sample_id, batch[0].group, address(500,"B"), batch[0].right, 1.)]
        self.assertRaises(ValueError, learner.advance, 0, wrong)

    def test_canonical_checkpoint_and_unsupported_modes(self):
        for mode, rank in (("unknown", 4),("contradiction",8),("full_refit",2)):
            self.assertRaises(ValueError, Learner, DIGEST, mode, rank)
        self.assertRaises(ValueError, Learner, "bad")
        model = Learner(DIGEST)
        self.assertEqual(model.checkpoint(), Learner.restore(model.checkpoint(), DIGEST).checkpoint())
        self.assertRaises(ValueError, Learner.restore, model.checkpoint()+b" ", DIGEST)


if __name__ == "__main__":
    unittest.main()
