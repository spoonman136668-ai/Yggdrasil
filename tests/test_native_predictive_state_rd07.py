"""RD07 witnessed complete-old-context diagnostic, not novel science."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT/"research/contrib/chatgpt/YGG-CAP04/rd07_old_query_context.py"
spec = importlib.util.spec_from_file_location("cap04_rd07", FILE)
rd07 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd07)


class RD07FixedHistoricalQuery(unittest.TestCase):
    def test_source_identity_and_exact_witnessed_previous_event(self):
        for source in rd07.SOURCE_SHA:
            with self.subTest(source=source):
                rows = rd07.original_rows(source)
                self.assertEqual(len(rows), 256)
                model = rd07.learner_modes()["direct"]
                for event in rows[:64]:
                    model.observe(event["id"], event["views"],
                                  event["action"], event["s2"],
                                  event["y"], event["post"])
                self.assertEqual(rd07.pinned_values(model, rows, 0), None)
                frozen = rd07.pinned_values(model, rows, 2)
                self.assertEqual(frozen["previous_pair"], rows[1]["action"])
                self.assertEqual(frozen["previous_post"], rows[1]["post"])
                self.assertEqual(frozen["previous_reward"], rows[1]["y"])
                self.assertEqual(frozen["previous_pair_post"],
                                 (rows[1]["action"],rows[1]["post"]))
                before = model.checkpoint()
                self.assertTrue(0 <= rd07.frozen_prediction(
                    model, rows, 2) <= 1)
                self.assertEqual(before, model.checkpoint())
                with self.assertRaisesRegex(ValueError, "CLAIMED_PREV_ID"):
                    rd07.pinned_values(model, rows, 2,
                                       claimed_prev_id="0"*64)
                with self.assertRaisesRegex(ValueError,"CLAIMED_PREV_REWARD"):
                    rd07.pinned_values(model, rows, 2,
                                       claimed_prev_reward=1-rows[1]["y"])
                with self.assertRaisesRegex(ValueError,"CLAIMED_SOURCE_ID"):
                    rd07.pinned_values(model, rows, 2, claimed_id="0"*64)
                with self.assertRaisesRegex(ValueError, "OLD_A_QUERY"):
                    rd07.pinned_values(model, rows, 16)
                with self.assertRaisesRegex(ValueError, "NO_PREVIOUS_WITNESS"):
                    rd07.pinned_values(model, rows, 0,
                                       claimed_prev_id=rows[0]["id"])
                forged = list(rows)
                forged[1] = dict(forged[1], y=1-forged[1]["y"])
                with self.assertRaisesRegex(ValueError,
                                            "SOURCE_LEDGER_MISMATCH"):
                    rd07.pinned_values(model, forged, 2)
                with self.assertRaisesRegex(ValueError,
                                            "SOURCE_LEDGER_MISMATCH"):
                    rd07.frozen_prediction(model, forged, 1)
        for invalid in (99917,"99917","cap04-rd04-source-c"):
            with self.assertRaisesRegex(ValueError, "SOURCE_ID"):
                rd07.original_rows(invalid)

    def test_witness_history_not_sham_or_future_and_immutable(self):
        rows = rd07.original_rows(next(iter(rd07.SOURCE_SHA)))
        fake = rd07.learner_modes()["recent32"]
        for event in rows[:64]:
            fake.observe(event["id"], event["views"], event["action"],
                         event["s2"], event["y"], event["post"])
        state = fake.checkpoint()
        with self.assertRaisesRegex(ValueError, "OLD_A_QUERY"):
            rd07.pinned_values(fake, rows, -1)
        with self.assertRaisesRegex(ValueError, "OLD_A_QUERY"):
            rd07.pinned_values(fake, rows, 64)
        fake.sham = True
        with self.assertRaisesRegex(ValueError, "SHAM_LAG_UNSUPPORTED"):
            rd07.frozen_prediction(fake, rows, 5)
        fake.sham = False
        self.assertEqual(state, fake.checkpoint())

    def test_cold_replayed_three_snapshots_and_original_rd04_verdict(self):
        for source in rd07.SOURCE_SHA:
            with self.subTest(source=source):
                result = rd07.run(source)
                self.assertEqual(result["status"], "RD07_RETROSPECTIVE_VALID")
                self.assertEqual(result["previous_rd04_verdict"],
                                 "RD04_ENGINEERING_NO_GO")
                self.assertFalse(result["scientific_pass"])
                self.assertEqual(result["old_probe_count"], 16)
                self.assertEqual(set(result["stages"]),
                                 set(rd07.STAGES.values()))
                for step, stage in rd07.STAGES.items():
                    for mode in rd07.MODES:
                        r = result["stages"][stage][mode]
                        self.assertEqual(r["witnessed_events"], step)
                        self.assertTrue(r["cold_exact"])
                        self.assertGreater(r["checkpoint_bytes"], 0)
                        self.assertLessEqual(
                            r["mismatched_public_history_contexts"],16)
                        self.assertEqual(len(r["checkpoint_sha256"]),64)
                        self.assertLessEqual(
                            r["changed_forecast_with_pinned_context"],16)
                        self.assertTrue(0 <= r["legacy_brier"] <= 1)
                        self.assertTrue(0 <= r["fixed_full_context_brier"] <= 1)
                self.assertEqual(rd07.audit(rd07.canonical(result))["source"],
                                 source)

    def test_forged_old_probe_score_or_retention_scope_fails(self):
        original = rd07.run(next(iter(rd07.SOURCE_SHA)))
        raw = rd07.canonical(original)
        rd07.audit(raw)
        for path, value in (
            (("stages", "b_endpoint", "recent32",
              "fixed_full_context_brier"), -1),
            (("stages", "a_anchor", "direct",
              "mismatched_public_history_contexts"), -1),
            (("functional_readout_drift","recent32","b_endpoint",
              "retrospective_fixed_context_within_old_limit"),False),
            (("previous_rd04_verdict",),"RD04_ENGINEERING_FEASIBLE"),
            (("source",),"cap04-rd04-source-c"),
            (("scientific_pass",),True),
        ):
            with self.subTest(path=path):
                tampered = json.loads(raw)
                cursor = tampered
                for key in path[:-1]:
                    cursor = cursor[key]
                cursor[path[-1]] = value
                with self.assertRaisesRegex(ValueError, "DIAGNOSTIC_INVALID"):
                    rd07.audit(rd07.canonical(tampered))


if __name__ == "__main__":
    unittest.main()
