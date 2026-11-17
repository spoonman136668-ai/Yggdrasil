"""Fabricated source-free mechanical checks only: zero WSP148 effects consumed."""
from hashlib import sha256
from pathlib import Path
from unittest import TestCase

import repair as R


def fabricated():
    xs = tuple(sorted(range(64), key=lambda x:
        (sha256(("WSP135|ACTIONS|" + str(x)).encode()).digest(), x))[:32])
    return tuple((x, int((x & 3) == 3) ^ ((x >> 4) & 1)) for x in xs)


class CoordinatedWeightUnit(TestCase):
    def test_01_numerical_bits_and_no_source_import(self):
        self.assertEqual(len(R.MASKS), 64)
        self.assertEqual(len(R.SINGLES), 64)
        self.assertEqual(len(R.PAIRS), 2016)
        self.assertEqual(R.MAX_WRITES, 24)
        code = Path(R.__file__).read_text(encoding="utf8")
        for forbidden in (
            "import source", "from source import", "WSP148|SOURCE|",
            "Custodian", "_truth(", "majority", "MAJ5", "threshold",
        ):
            self.assertNotIn(forbidden, code)
        # Source custody is checked by the pinned pre-source workflow; unit tests
        # must remain source-free even after the independent owner is added.

    def test_02_source_free_exact_fabricated_fit_and_cold(self):
        rows = fabricated()
        for width in (1, 2):
            model = R.program(rows, block_width=width)
            again = R.program(rows, block_width=width)
            for key in ("weights", "edits", "individual_writes",
                        "residual_errors", "has_exact_fit", "block_width",
                        "source_rows_sha256"):
                self.assertEqual(model[key], again[key])
            self.assertTrue(model["has_exact_fit"])
            self.assertLessEqual(model["individual_writes"], 24)
            self.assertTrue(all(R.predict(model, x) == y for x, y in rows))
            self.assertEqual(R.predictions(model), R.predictions(R.restore(model, rows)))

    def test_03_every_write_strictly_reduces_error_and_respects_budget(self):
        rows = fabricated()
        for width in (1, 2):
            model = R.program(rows, block_width=width)
            self.assertEqual(
                sum(len(block) for block, gain, before, after in model["edits"]),
                model["individual_writes"],
            )
            self.assertLessEqual(model["individual_writes"], R.MAX_WRITES)
            for block, gain, before, after in model["edits"]:
                self.assertLessEqual(len(block), width)
                self.assertEqual(len(set(block)), len(block))
                self.assertGreater(gain, 0)
                self.assertEqual(before - after, gain)
                self.assertGreater(before, after)
            if model["edits"]:
                self.assertEqual(model["edits"][-1][3], model["residual_errors"])

    def test_04_validation_and_corrupt_saved_weights_fail_closed(self):
        rows = fabricated()
        invalid = (rows[:-1], rows[:-1] + ((rows[0][0], 1),),
                   rows[:-1] + ((True, 1),), rows[:-1] + ((63, 2),))
        for bad in invalid:
            with self.assertRaises(ValueError):
                R.program(bad)
        for invalid_width in (0, 3, True, "2"):
            with self.assertRaises(ValueError):
                R.program(rows, block_width=invalid_width)
        saved = R.program(rows, block_width=2)
        with self.assertRaises(ValueError):
            R.restore(dict(saved, weights=saved["weights"] ^ 1), rows)
        with self.assertRaises(ValueError):
            R.restore(dict(saved, individual_writes=999), rows)
        with self.assertRaises(ValueError):
            R.restore(dict(saved, source_rows_sha256="wrong"), rows)

    def test_05_no_confident_guess_without_exact_observed_fit(self):
        rows = fabricated()
        m = R.program(rows, block_width=2)
        self.assertEqual(R.predictions(dict(m, has_exact_fit=False)),
                         (None,) * 64)
        with self.assertRaises(ValueError):
            R.predict(m, True)
        with self.assertRaises(ValueError):
            R.predict(m, 64)

    def test_06_zero_function_requires_zero_edits(self):
        rows = tuple((x, 0) for x in range(32))
        for width in (1, 2):
            model = R.program(rows, block_width=width)
            self.assertTrue(model["has_exact_fit"])
            self.assertEqual(model["individual_writes"], 0)
            self.assertEqual(model["weights"], 0)
            self.assertEqual(R.predictions(model), (0,) * 64)
