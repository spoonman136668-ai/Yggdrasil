"""WSP120 original result custody: synthetic summaries only, never world reads."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import original_reduce as R


def fake_parts(folder, *, tamper=False):
    # Original seed numbers are *labels*, not generated or accessed worlds.
    for platform in R.PLATFORMS:
        for shard in range(R.SHARDS):
            rows = []
            for seed in R.SEEDS[shard::R.SHARDS]:
                for tier in R.TIERS:
                    for family in (0, 1, 2):
                        for exp in R.EXPOSURES:
                            arms = {}
                            for name, count in (
                                ("NUMERIC_GROW_ACTIVE", 17 if exp else 0),
                                ("NUMERIC_GROW_PASSIVE", 11 if exp else 0),
                                ("NUMERIC_FIXED3", 10 if exp else 0),
                                ("SYMBOLIC_ACTIVE", 19 if exp else 0),
                                ("NO_UPDATE", 0),
                            ):
                                receipt_key = ("passive" if name in
                                    ("NUMERIC_GROW_PASSIVE", "NUMERIC_FIXED3",
                                     "NO_UPDATE") else name)
                                receipt = sha256(
                                    f"{seed}/{tier}/{family}/{exp}/{receipt_key}"
                                    .encode()).hexdigest()
                                arms[name] = {
                                    "correct": count, "wrong_confident": 0,
                                    "abstained": 24 - count, "held": 24,
                                    "predictions": [1] * count +
                                                   [None] * (24 - count),
                                    "source_calls": exp,
                                    "source_sha256": receipt,
                                    "cold_ok": None if name == "SYMBOLIC_ACTIVE"
                                               else True,
                                    "numeric_bytes": 0,
                                    "law_declared": False,
                                    "full_function_identified": False,
                                }
                            if exp == 32:
                                arms["TRAINED_GRU_PASSIVE"] = {
                                    "correct": 12, "wrong_confident": 12,
                                    "abstained": 0, "held": 24,
                                    "predictions": [1] * 12 + [2] * 12,
                                    "source_calls": 32, "converged": True,
                                }
                            rows.append({
                                "seed": seed, "tier": tier, "family": family,
                                "exposure": exp, "arms": arms,
                            })
            doc = {
                "schema": "wsp120.original-public-shard.v1",
                "first_use": True, "native_model_modified": False,
                "protected_source_opened": False, "platform": platform,
                "shard": shard, "seed_list": list(R.SEEDS[shard::R.SHARDS]),
                "source_sha": "science-precommitted-candidate-fixture",
                "rows": rows,
            }
            if tamper and platform == "Windows" and shard == 0:
                doc["rows"][0]["arms"]["NUMERIC_FIXED3"]["correct"] = 1
            (Path(folder) / f"result-{platform}-{shard}.json").write_text(
                json.dumps(doc))


class OriginalAggregationFixtureTests(TestCase):
    def test_complete_paired_world_scoring_is_source_free(self):
        import structural_growth as S
        with TemporaryDirectory() as d, patch.object(
                S, "source_safe_world",
                side_effect=AssertionError("original cohort opened")):
            fake_parts(d)
            report = R.reduce_original(d)
            self.assertEqual(report["world_tasks_per_platform"], 216)
            self.assertEqual(report["cross_platform_numeric_source_differences"], 0)
            self.assertEqual(report["cross_platform_gru_prediction_differences"], 0)
            self.assertFalse(report["scientific_pass"])
            self.assertEqual(report["development_classification"],
                             "DEVELOPMENT_SIGNAL")
            self.assertEqual(report["full_32call_gru_nonconverged_cases"], 0)

    def test_cross_os_tamper_rejected_without_source_reads(self):
        with TemporaryDirectory() as d:
            fake_parts(d, tamper=True)
            with self.assertRaisesRegex(ValueError,
                                        "WSP120_ORIGINAL_INVALID_"):
                R.reduce_original(d)
