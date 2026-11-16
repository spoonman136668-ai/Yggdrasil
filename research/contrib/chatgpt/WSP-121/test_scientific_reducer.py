"""WSP-121 source-free reducer tests, fabricated summaries ONLY.

All 48 world IDs below are labels within deliberately constructed dictionaries;
no graph generator, EvidenceSource, original cohort, or held labels are accessed.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from unittest import TestCase
from unittest.mock import patch

import scientific_reducer as R


def _digest(text):
    return sha256(text.encode()).hexdigest()


def synthetic_rows(platform="ubuntu-latest", correct=None, cost=None):
    correct = correct or {
        "NUMERIC_FAST": 21, "NUMERIC_RESET": 10,
        "SYMBOLIC_TABLE_STRONG": 21, "SYMBOLIC_ENUM": 21,
        "TRAINED_MLP": 20, "NO_UPDATE": 0}
    cost = cost or {
        "NUMERIC_FAST": 3.0, "NUMERIC_RESET": 3.0,
        "SYMBOLIC_TABLE_STRONG": 1.0, "SYMBOLIC_ENUM": 4.0,
        "TRAINED_MLP": 2.0, "NO_UPDATE": 0.2}
    rows = []
    for seed in R.ORIGINAL_FIT_SEEDS + R.ORIGINAL_TRANSFER_SEEDS:
        fit = seed in R.ORIGINAL_FIT_SEEDS
        family = ((seed - 121000) if fit else (seed - 121024)) // 8
        budget = 8 if fit else 4
        receipt = _digest(f"synthetic-only-source-receipt:{seed}")
        env = _digest("synthetic-only-same-platform-environment:"+platform)
        arms = {}
        for name in R.ARMS:
            held_correct = correct[name]
            held_wrong = 0
            base = cost[name]
            arms[name] = {
                "correct": held_correct, "wrong_confident": held_wrong,
                "abstained": 24-held_correct-held_wrong,
                "held": 24, "source_calls": budget,
                "source_sha256": receipt,
                "held_predictions_sha256":
                    _digest(f"synthetic-held-prediction:{seed}:{name}"),
                "environment_sha256": env,
                "cold_ok": True if name in ("NUMERIC_FAST", "NUMERIC_RESET")
                           else None,
                "converged": True if name == "TRAINED_MLP" else None,
                "trained_seeds": [121951,121952,121953]
                                 if name == "TRAINED_MLP" else None,
                "training_accuracy": 1.0 if name == "TRAINED_MLP" else None,
                "training_loss": 0.001 if name == "TRAINED_MLP" else None,
                "model_bytes": 64 if name in ("NUMERIC_FAST", "NUMERIC_RESET")
                               else 10000 if name == "TRAINED_MLP"
                               else 256 if name == "SYMBOLIC_TABLE_STRONG"
                               else 5000 if name == "SYMBOLIC_ENUM"
                               else 0,
                "wall_parts_seconds": {
                    "source": base/4, "train": base/4,
                    "infer": base/4, "cold_restore": base/4},
                "wall_seconds": base,
                "peak_rss_bytes": 120000 + 128*budget,
                "energy_proxy_joules": base * 10.0
            }
        rows.append({
            "seed": seed, "family": family,
            "phase": "fit" if fit else "transfer",
            "platform": platform, "visible_edges": 384,
            "legal_subjects": 40, "held_subjects": 24,
            "held_labels_used_in_training": False,
            "fit_lineage_sha256": _digest(f"synthetic-family-fit:{family}"),
            "arms": arms,
        })
    return rows


class WSP121SourceFreeReducerTests(TestCase):
    def test_48_world_exact_stratified_pairing_and_symbolic_tie(self):
        # This test must not open actual original source.
        import meta_operator
        with patch.object(meta_operator, "original_world",
                          side_effect=AssertionError("primary opened")):
            result = R.reduce_scored_summaries(synthetic_rows())
        self.assertFalse(result["source_accessed_by_reducer"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_admission"])
        self.assertEqual(result["scientific_status"], "UNVERIFIED")
        self.assertEqual(result["development_signal"], "PASS_CANDIDATE")
        self.assertEqual(result["scientific_candidate"],
                         "NO_SUPERIORITY_CANDIDATE")
        self.assertEqual(result["fit_worlds"], 24)
        self.assertEqual(result["transfer_worlds"], 24)
        self.assertEqual(result["total_verified_source_queries"], 288)
        self.assertEqual(result["transfer_held_per_arm"], 576)
        self.assertEqual(result["total_correct"]["NUMERIC_FAST"], 24*21)
        self.assertEqual(result["total_correct"]["SYMBOLIC_TABLE_STRONG"], 24*21)
        self.assertAlmostEqual(result["accuracy"]["NUMERIC_FAST"], 21/24)
        reset = result["paired_accuracy"]["NUMERIC_RESET"]
        self.assertAlmostEqual(reset["mean"], 11/24)
        self.assertGreater(reset["ci95_lower"], 0)
        self.assertEqual(reset["resamples"], 10000)
        self.assertEqual(reset["seed"], 1210)
        self.assertAlmostEqual(
            result["paired_accuracy"]["SYMBOLIC_TABLE_STRONG"]["mean"], 0.0)
        self.assertEqual(result["paired_accuracy"],
                         R.reduce_scored_summaries(synthetic_rows())[
                             "paired_accuracy"])

    def test_fail_closed_incomplete_weak_controls_cost_custody_or_leak(self):
        base = synthetic_rows()
        failures = [base[:-1]]
        duplicate = deepcopy(base)
        duplicate[-1] = deepcopy(duplicate[0])
        failures.append(duplicate)
        for operation in (
            lambda r: r[0].update(seed=121800),
            lambda r: r[0].update(seed=120019),
            lambda r: r[0].update(family=2),
            lambda r: r[0].update(visible_edges=192),
            lambda r: r[0].update(held_labels_used_in_training=True),
            lambda r: r[24].update(fit_lineage_sha256=_digest("wrong")),
            lambda r: r[1]["arms"].pop("SYMBOLIC_TABLE_STRONG"),
            lambda r: r[0]["arms"]["NUMERIC_RESET"].update(source_sha256=_digest("different")),
            lambda r: r[0]["arms"]["NUMERIC_FAST"].update(cold_ok=False),
            lambda r: r[0]["arms"]["TRAINED_MLP"].update(converged=False),
            lambda r: r[0]["arms"]["TRAINED_MLP"].update(trained_seeds=[121951]),
            lambda r: r[0]["arms"]["NUMERIC_FAST"].update(wall_seconds=2.1),
            lambda r: r[0]["arms"]["NUMERIC_FAST"].update(peak_rss_bytes=0),
            lambda r: r[0]["arms"]["NUMERIC_FAST"].update(energy_proxy_joules=None),
            lambda r: r[0]["arms"]["NUMERIC_FAST"].update(
                held_predictions_sha256="not-a-hash"),
            lambda r: r[0]["arms"]["NUMERIC_FAST"].update(correct=25),
            lambda r: r[0]["arms"]["NUMERIC_FAST"].update(
                environment_sha256=_digest("other-machine")),
        ):
            sample = deepcopy(base)
            operation(sample)
            failures.append(sample)
        for i, rows in enumerate(failures):
            with self.subTest(index=i), self.assertRaisesRegex(
                    ValueError, "WSP121_REDUCER_"):
                R.reduce_scored_summaries(rows)

    def test_platform_prediction_mismatch_invalid_even_on_mlp(self):
        linux = synthetic_rows("ubuntu-latest")
        windows = synthetic_rows("windows-2022")
        ok = R.compare_platforms(linux, windows)
        self.assertEqual(ok["status"], "DIAGNOSTIC_PARITY")
        self.assertFalse(ok["scientific_pass"])
        windows[31]["arms"]["TRAINED_MLP"]["held_predictions_sha256"] = _digest(
            "synthetic-cross-platform-mismatch")
        bad = R.compare_platforms(linux, windows)
        self.assertEqual(bad["status"], "INVALID")
        self.assertIn({"seed": 121031, "arm": "TRAINED_MLP",
                       "kind": "PREDICTION_MISMATCH"}, bad["differences"])
        for name in R.ARMS:
            windows[30]["arms"][name]["source_sha256"] = _digest(
                "synthetic-source-platform-mismatch")
        broken = R.compare_platforms(linux, windows)
        self.assertTrue(any(x["kind"] == "SOURCE_MISMATCH"
                            for x in broken["differences"]))

    def test_platform_fit_lineage_divergence_invalid_even_with_hash_parity(self):
        linux = synthetic_rows("ubuntu-latest")
        windows = synthetic_rows("windows-2022")
        # Mutate all family-0 rows so both datasets are internally valid;
        # matching source and prediction hashes cannot establish fit lineage.
        for row in windows:
            if row["family"] == 0:
                row["fit_lineage_sha256"] = _digest("different-synthetic-fit")
        comparison = R.compare_platforms(linux, windows)
        self.assertEqual(comparison["status"], "INVALID")
        self.assertIn({"seed": 121000, "kind": "FIT_LINEAGE_MISMATCH"},
                      comparison["differences"])
        self.assertFalse(comparison["scientific_pass"])

    def test_platform_score_divergence_invalid_even_with_prediction_hash_parity(self):
        linux = synthetic_rows("ubuntu-latest")
        windows = synthetic_rows("windows-2022")
        # Fabricated metadata discrepancy, never actual first-use labels.
        target = windows[25]["arms"]["NUMERIC_FAST"]
        target["correct"] -= 1
        target["abstained"] += 1
        comparison = R.compare_platforms(linux, windows)
        self.assertEqual(comparison["status"], "INVALID")
        self.assertIn({"seed": 121025, "arm": "NUMERIC_FAST",
                       "kind": "SCORE_MISMATCH"}, comparison["differences"])
        self.assertFalse(comparison["scientific_pass"])

    def test_positive_synthetic_science_candidate_still_not_acceptance(self):
        # Artificially favorable data cannot produce SCIENTIFIC_PASS.
        scores = {
            "NUMERIC_FAST": 24, "NUMERIC_RESET": 10,
            "SYMBOLIC_TABLE_STRONG": 20, "SYMBOLIC_ENUM": 21,
            "TRAINED_MLP": 20, "NO_UPDATE": 0}
        a = R.reduce_scored_summaries(synthetic_rows(correct=scores))
        self.assertEqual(a["scientific_candidate"], "ACCURACY_CANDIDATE")
        self.assertFalse(a["scientific_pass"])
        fast = {n: 1.0 for n in R.ARMS}
        fast["SYMBOLIC_TABLE_STRONG"] = 4.0
        fast["TRAINED_MLP"] = 4.0
        tied = {n: 21 for n in R.ARMS}
        tied["NUMERIC_RESET"] = 10
        cost = R.reduce_scored_summaries(synthetic_rows(
            correct=tied, cost=fast))
        self.assertEqual(cost["scientific_candidate"], "COST_CANDIDATE")
        self.assertFalse(cost["scientific_pass"])
