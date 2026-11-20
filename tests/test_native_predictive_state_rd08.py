"""CAP04-RD08 opt-in witnessed history readout provenance, no new science."""
import importlib.util
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_predictive_state_split import PredictiveStateSplit

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research/contrib/chatgpt/YGG-CAP04/rd07_old_query_context.py"
spec = importlib.util.spec_from_file_location("cap04_rd07_reference_rd08", SRC)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)

EXPECTED_RD07 = {
    "cap04-rd04-source-a":
        "7fed6a81dc508ab101e7996c5aea984a7558acef89dc8b487807b65a82b3d361",
    "cap04-rd04-source-b":
        "040e34fea391b1980937968151e6e75fa3afccde9ac8ee2b0651a3f35909e23e",
}


class RD08WitnessedContextReadOnly(unittest.TestCase):
    def test_exact_full_history_matches_independent_rd07_and_cold(self):
        for name in reference.SOURCE_SHA:
            with self.subTest(source=name):
                rows = reference.original_rows(name)
                self.assertEqual(digest(canonical(rows)),
                                 reference.SOURCE_SHA[name])
                learners = reference.learner_modes()
                for i, row in enumerate(rows):
                    for model in learners.values():
                        self.assertEqual(model.count, i)
                        model.observe(row["id"], row["views"],
                                      row["action"], row["s2"], row["y"],
                                      row["post"])
                    if i+1 not in reference.STAGES:
                        continue
                    for mode, model in learners.items():
                        before = model.checkpoint()
                        cold = PredictiveStateSplit.restore(
                            before, digest(before))
                        self.assertEqual(before, cold.checkpoint())
                        for query_index, current in enumerate(rows[:16]):
                            predecessor_id = (
                                rows[query_index-1]["id"]
                                if query_index else None)
                            for stage in ("transition", "residual"):
                                sensor = (None if stage == "transition"
                                          else current["s2"])
                                actual = model.forecast_witnessed_context(
                                    current["id"], current["views"],
                                    current["action"], stage, sensor,
                                    predecessor_id=predecessor_id)
                                replay = cold.forecast_witnessed_context(
                                    current["id"], current["views"],
                                    current["action"], stage, sensor,
                                    predecessor_id=predecessor_id)
                                self.assertEqual(actual, replay)
                                values = reference.pinned_values(
                                    model, rows, query_index)
                                st = (current["views"][0][0],
                                      current["views"][0][1],
                                      current["views"][1][1])
                                feat = model._winner(stage, values)
                                expected = model._estimate(
                                    stage, model._conditioned_state(
                                        stage, st, sensor),
                                    current["action"], values, feat)
                                if (stage == "residual" and
                                        model.reward_mode == "xor" and
                                        sensor == 1):
                                    expected = 1 - expected
                                self.assertEqual(actual, expected)
                            self.assertEqual(
                                reference.frozen_prediction(
                                    model, rows, query_index),
                                model.forecast_witnessed_context(
                                    current["id"], current["views"],
                                    current["action"], "residual",
                                    current["s2"],
                                    predecessor_id=predecessor_id))
                        self.assertEqual(before, model.checkpoint())
                        self.assertEqual(before, cold.checkpoint())

    def test_strict_missing_wrong_and_future_provenance_rejected(self):
        rows = reference.original_rows(next(iter(reference.SOURCE_SHA)))
        model = reference.learner_modes()["direct"]
        for row in rows[:64]:
            model.observe(row["id"], row["views"], row["action"],
                          row["s2"], row["y"], row["post"])
        initial, other = rows[0], rows[4]
        pred = rows[3]["id"]
        def query(**changed):
            values = dict(identifier=other["id"],
                          views=other["views"], chosen=other["action"],
                          stage="residual", witnessed_s2=other["s2"],
                          predecessor_id=pred)
            values.update(changed)
            return model.forecast_witnessed_context(**values)
        start = model.checkpoint()
        self.assertTrue(0 <= query() <= 1)
        for kwargs, code in (
            (dict(identifier="0"*64), "QUERY_WITNESS"),
            (dict(identifier=rows[64]["id"]), "QUERY_WITNESS"),
            (dict(identifier=1), "QUERY_WITNESS"),
            (dict(views=((1-other["views"][0][0],
                          other["views"][0][1]), other["views"][1])),
             "QUERY_PUBLIC_MISMATCH"),
            (dict(chosen=(1-other["action"][0],other["action"][1])),
             "QUERY_PUBLIC_MISMATCH"),
            (dict(stage="bad"), "QUERY_STAGE"),
            (dict(witnessed_s2=1-other["s2"]),
             "QUERY_SENSOR_MISMATCH"),
            (dict(predecessor_id=None), "QUERY_PREDECESSOR"),
            (dict(predecessor_id=rows[2]["id"]), "QUERY_PREDECESSOR"),
            (dict(predecessor_id=other["id"]), "QUERY_PREDECESSOR"),
            (dict(stage="transition",witnessed_s2=other["s2"]),
             "QUERY_EARLY_SENSOR"),
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaisesRegex(ValueError,code):
                    query(**kwargs)
                self.assertEqual(start, model.checkpoint())
        self.assertTrue(0 <= model.forecast_witnessed_context(
            initial["id"],initial["views"],initial["action"],
            "residual",initial["s2"]) <= 1)
        with self.assertRaisesRegex(ValueError,"QUERY_INITIAL_PREDECESSOR"):
            model.forecast_witnessed_context(
                initial["id"],initial["views"],initial["action"],
                "residual",initial["s2"],
                predecessor_id=rows[1]["id"])
        sham=PredictiveStateSplit(reward_mode="direct",sham=True)
        for row in rows[:64]:
            sham.observe(row["id"],row["views"],row["action"],
                         row["s2"],row["y"],row["post"])
        before=sham.checkpoint()
        with self.assertRaisesRegex(ValueError, "WITNESS_SHAM_UNSUPPORTED"):
            sham.forecast_witnessed_context(
                other["id"],other["views"],other["action"],
                "residual",other["s2"],predecessor_id=pred)
        self.assertEqual(before,sham.checkpoint())
        self.assertEqual(start,model.checkpoint())

    def test_original_rd07_metrics_and_receipts_byte_identical(self):
        # This is a retrospective instrument comparison. The two previously
        # consumed synthetic RD04 sources are never reused as new science.
        for name, original_sha in EXPECTED_RD07.items():
            with self.subTest(source=name):
                report=reference.run(name)
                self.assertEqual(report["previous_rd04_verdict"],
                                 "RD04_ENGINEERING_NO_GO")
                self.assertFalse(report["scientific_pass"])
                self.assertEqual(
                    reference.audit(canonical(report))["receipt_sha256"],
                    original_sha)


if __name__ == "__main__":
    unittest.main()
