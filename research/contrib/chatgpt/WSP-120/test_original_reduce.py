"""Source-free original aggregator gate fixtures; no original first-use."""
from unittest import TestCase
from tempfile import TemporaryDirectory
import json
from pathlib import Path
from unittest.mock import patch
import original_reduce as R


class ReadOnlyOriginalReducerTests(TestCase):
    def test_no_read_when_missing_artifacts(self):
        import structural_growth as S
        with TemporaryDirectory() as d, patch.object(
                S, "source_safe_world",
                side_effect=AssertionError("original source accessed")):
            with self.assertRaises(FileNotFoundError):
                R.reduce_original(d)

    def test_fixed_expected_cohort(self):
        self.assertEqual((len(R.SEEDS), len(R.TIERS),
                          len(R.EXPOSURES), len(R.PLATFORMS)),
                         (24, 3, 5, 2))
        self.assertTrue(set(R.SEEDS).isdisjoint(range(120800, 120864)))
