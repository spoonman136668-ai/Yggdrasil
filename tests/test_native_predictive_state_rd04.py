"""RD04 frozen source-free recent32 router research tests; not science."""
import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_predictive_state_split import (
    PredictiveStateSplit, RECENT_WINDOW, RECENT_LOG_GATE,
    SCHEMA, SCHEMA_DIRECT, SCHEMA_RECENT32, FEATURES,
)

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/YGG-CAP04/rd04_engineering.py")
spec = importlib.util.spec_from_file_location("rd04_frozen", SOURCE)
rd04 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd04)


class RD04RecentHistoryResearch(unittest.TestCase):
    def test_precommitted_source_clock_and_identifiability(self):
        self.assertEqual((RECENT_WINDOW, RECENT_LOG_GATE), (32, 2.5))
        self.assertEqual(rd04.N, 256)
        self.assertEqual(len(rd04.SOURCE_IDS), 2)
        for name in rd04.SOURCE_IDS:
            with self.subTest(name=name):
                rows = rd04.source(name)
                self.assertEqual(len(rows), 256)
                self.assertEqual(len({r["id"] for r in rows}), 256)
                coverage = rd04.identifiability(rows)
                self.assertEqual(coverage["ordered_prior_current_pairs"], 16)
                self.assertGreaterEqual(
                    coverage["contrasting_public_cells"], 4)
                previous = (0, 0)
                for i, row in enumerate(rows):
                    expect = ((row["s2"] ^ previous[
                        int(name == rd04.SOURCE_IDS[1])])
                        if 64 <= i < 192 else row["s2"])
                    self.assertEqual(row["y"], expect)
                    self.assertEqual(row["post"][1], row["s2"])
                    if i:
                        post = rows[i - 1]["post"]
                        self.assertEqual(row["views"],
                                         ((post[0], post[1]),
                                          (post[1], post[2])))
                    previous = row["action"]
        for protected in ("99917", "cap04-rd04-source-c", 99917):
            with self.assertRaisesRegex(ValueError, "SOURCE_ID"):
                rd04.source(protected)

    def test_old_schema_modes_and_exact_recent_cold_replay(self):
        x = PredictiveStateSplit()
        d = PredictiveStateSplit(reward_mode="direct")
        r = PredictiveStateSplit(
            reward_mode="direct", routing_mode="recent32")
        self.assertEqual(
            x.checkpoint(),
            canonical({"schema": SCHEMA, "sham": False, "events": []}))
        self.assertEqual(
            d.checkpoint(),
            canonical({"schema": SCHEMA_DIRECT, "sham": False,
                       "reward_mode": "direct", "events": []}))
        self.assertEqual(
            r.checkpoint(),
            canonical({"schema": SCHEMA_RECENT32, "sham": False,
                       "reward_mode": "direct", "routing_mode": "recent32",
                       "events": []}))
        for bad_reward, bad_router in (
                ("xor", "recent32"), ("direct", "bad"), ("direct", 1),
                ("direct", None)):
            with self.assertRaisesRegex(ValueError, "ROUTING_MODE"):
                PredictiveStateSplit(reward_mode=bad_reward,
                                     routing_mode=bad_router)
        for event in rd04.source(rd04.SOURCE_IDS[0])[:48]:
            args = (event["id"], event["views"], event["action"],
                    event["s2"], event["y"], event["post"])
            for model in (x, d, r):
                model.observe(*args)
        for f in FEATURES:
            self.assertLessEqual(len(r._recent_gains["residual"][f]), 32)
            self.assertEqual(len(r._recent_gains["residual"][f]), 32)
        for model in (x, d, r):
            raw = model.checkpoint()
            cold = PredictiveStateSplit.restore(raw, digest(raw))
            self.assertEqual(raw, cold.checkpoint())
            self.assertEqual(cold.routing_mode, model.routing_mode)
            for event in rd04.source(rd04.SOURCE_IDS[0])[:2]:
                self.assertEqual(
                    cold.forecast(event["views"], event["action"],
                                  "residual", event["s2"]),
                    model.forecast(event["views"], event["action"],
                                   "residual", event["s2"]))
            self.assertEqual(raw, model.checkpoint())
        bad = json.loads(r.checkpoint())
        bad["routing_mode"] = "cumulative"
        with self.assertRaisesRegex(ValueError, "COLD_REJECTED"):
            raw = canonical(bad)
            PredictiveStateSplit.restore(raw, digest(raw))
        bad = json.loads(r.checkpoint())
        bad["schema"] = SCHEMA_DIRECT
        with self.assertRaisesRegex(ValueError, "COLD_REJECTED"):
            raw = canonical(bad)
            PredictiveStateSplit.restore(raw, digest(raw))

    def test_frozen_two_source_full_prequential_comparison(self):
        for name in rd04.SOURCE_IDS:
            with self.subTest(name=name):
                report = rd04.run(name)
                checked = rd04.audit(canonical(report))
                self.assertEqual(checked["events"], 256)
                self.assertFalse(checked["scientific_pass"])
                self.assertFalse(report["accepted_native_modified"])
                self.assertEqual(report["source"], name)
                self.assertEqual(report["original_source_actions"], 0)
                self.assertEqual(report["status"], rd04.decide(
                    report["phase_metrics"], report["snapshots"])[0])
                self.assertIn(report["status"],
                              ("RD04_ENGINEERING_NO_GO",
                               "RD04_ENGINEERING_FEASIBLE"))
                for stage, n in (("a_anchor", 64), ("b_endpoint", 192),
                                 ("a_return_endpoint", 256)):
                    for model in rd04.MODEL_NAMES:
                        self.assertEqual(
                            report["snapshots"][stage]["models"][model]["events"],
                            n)
                for phase, (a, b) in rd04.PHASES.items():
                    self.assertEqual(
                        sum(report["phase_metrics"][phase]["recent32"]
                            ["feature_count"].values()), b - a)

    def test_negative_receipt_tamper_is_rejected(self):
        report = rd04.run(rd04.SOURCE_IDS[0])
        raw = canonical(report)
        self.assertEqual(rd04.audit(raw)["source"], rd04.SOURCE_IDS[0])
        changes = (
            ("rows", 3, "y"),
            ("phase_metrics", "pooled", "recent32", "two_stage"),
            ("phase_metrics", "novel", "recent32", "feature_count",
             "previous_pair"),
        )
        for path in changes:
            with self.subTest(path=path):
                altered = json.loads(raw)
                node = altered
                for key in path[:-1]:
                    node = node[key]
                old = node[path[-1]]
                node[path[-1]] = (old ^ 1) if type(old) is int else (old + .01)
                with self.assertRaisesRegex(ValueError, "AUDIT_REJECTED"):
                    rd04.audit(canonical(altered))


if __name__ == "__main__":
    unittest.main()
