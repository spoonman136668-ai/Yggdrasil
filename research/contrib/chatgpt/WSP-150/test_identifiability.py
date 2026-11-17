"""WSP150 source-free exhaustive algebraic proof and fabricated split controls."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest import TestCase
import identifiability as I


def fake_rows(seed):
    contexts = sorted(range(64), key=lambda x: (
        sha256(f'WSP150|FABRICATED|{seed}|{x}'.encode()).digest(), x))[:32]
    return tuple((x, sha256(f'WSP150|FAKE-EFFECT|{seed}|{x}'.encode()).digest()[0] & 1)
                 for x in contexts)


class SourceFreeVersionSpace(TestCase):
    def test_01_complete_basis_rank_64(self):
        self.assertEqual(I.gf2_rank(tuple(I.features(x) for x in range(64))), 64)
        self.assertEqual(I.gf2_rank(tuple(I.features(x) for x in range(32))), 32)

    def test_02_all_4096_spike_target_checks(self):
        for q in range(64):
            delta = I.spike_weights(q)
            self.assertEqual(delta.bit_count(), 1 << (6 - q.bit_count()))
            for x in range(64):
                self.assertEqual(I.readout(delta, x), int(x == q))

    def test_03_all_128_indistinguishable_fabricated_held_witnesses(self):
        for seed in range(4):
            rows = fake_rows(seed)
            observed = {x for x, _ in rows}
            self.assertEqual(len(observed), 32)
            baseline = I.fit_observed(rows)
            self.assertTrue(all(I.readout(baseline, x) == y for x, y in rows))
            for q in sorted(set(range(64)) - observed):
                a, b = I.witness(rows, q)
                self.assertEqual(a, baseline)
                self.assertNotEqual(I.readout(a, q), I.readout(b, q))
                for x in range(64):
                    self.assertEqual(I.readout(a, x) ^ I.readout(b, x), int(x == q))

    def test_04_independent_complete_truth_inverse(self):
        for seed in range(4):
            truth = tuple(sha256(f'WSP150|INVERSE-FAKE|{seed}|{x}'.encode()).digest()[0] & 1
                          for x in range(64))
            w = I.inverse_truth_table(truth)
            self.assertEqual(tuple(I.readout(w, x) for x in range(64)), truth)

    def test_05_invalid_negative_controls(self):
        for bad in (-1, 64, True, 0.5, '3'):
            with self.assertRaises(ValueError): I.features(bad)
            with self.assertRaises(ValueError): I.spike_weights(bad)
        for bad in (-1, 1 << 64, True, 2.0, '1'):
            with self.assertRaises(ValueError): I.readout(bad, 0)
        r = fake_rows(0)
        for bad in (r[:-1], r[:-1] + ((r[0][0], 1),),
                    r[:-1] + ((True, 0),), r[:-1] + ((64, 0),)):
            with self.assertRaises(ValueError): I.fit_observed(bad)
        with self.assertRaises(ValueError): I.witness(r, r[0][0])
        with self.assertRaises(ValueError): I.inverse_truth_table((0,)*63)
        corrupted = I.spike_weights(0) ^ 1
        self.assertNotEqual(tuple(I.readout(corrupted, x) for x in range(64)),
                            tuple(int(x == 0) for x in range(64)))

    def test_06_exact_wsp149_basis_parity_if_checkout(self):
        sibling = Path(__file__).resolve().parents[1] / 'WSP-149' / 'exact_weights.py'
        if not sibling.exists():
            self.skipTest('Pinned WSP149 source requires full repository checkout')
        spec = spec_from_file_location('_wsp150_pinned_wsp149_exact', sibling)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        for x in range(64):
            self.assertEqual(I.features(x), mod._features(x))
        for seed in range(4):
            rows = fake_rows(seed)
            fit = mod.fit(rows)
            self.assertEqual(fit['rank'], 32)
            self.assertTrue(all(mod.predict(fit, x) == y for x,y in rows))
            for q in set(range(64))-{x for x,y in rows}:
                alt = fit['weights'] ^ I.spike_weights(q)
                self.assertNotEqual(I.readout(fit['weights'], q), I.readout(alt, q))
                self.assertTrue(all(I.readout(alt, x)==y for x,y in rows))

    def test_07_source_isolation(self):
        source=Path(I.__file__).read_text(encoding='utf8')
        for forbidden in ('import source', 'from source import', 'WSP149|SOURCE|',
                          'WSP149|HELD|', 'OwnerPostCommit', '_truth('):
            self.assertNotIn(forbidden, source)
