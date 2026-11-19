"""RET04 two-clock score/custody tests on unscored public-shaped fixtures.

These are strictly mechanical tests, NOT original physical source action,
new scientific training, prospective model comparison or owner admission.
"""
import json
import unittest

from test_native_staged_temporal import original_models, public_fixture
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_staged_temporal import StagedTemporalReadout
from yggdrasil.native_staged_score_receipts import StagedScoreReceipts


def stages(model, event):
    ref, views, row = event
    before = model.begin(ref, views, row["x1"])
    model.record_transition(ref, row["s2"])
    after = model.choose_second(ref, row["x2"])
    output = model.complete(ref, row["y"])
    return before, after, output


class StagedScoreReceiptsEngineering(unittest.TestCase):
    def test_score_exactly_preissued_stage_predictions_not_updated_forecast(self):
        model = StagedScoreReceipts(*original_models())
        first, second, output = stages(model, public_fixture(23))
        self.assertEqual(output["transition"], first)
        self.assertEqual(output["reward"], second)
        record, = model.receipts
        self.assertEqual(record["transition_forecast"], first)
        self.assertEqual(record["reward_forecast"], second)
        self.assertEqual(record["observed_s2"], public_fixture(23)[2]["s2"])
        self.assertEqual(record["observed_y"], public_fixture(23)[2]["y"])
        for arm in ("archive", "live", "temporal"):
            delta1 = first[arm] - record["observed_s2"]
            delta2 = second[arm] - record["observed_y"]
            loss1, loss2 = delta1*delta1, delta2*delta2
            self.assertEqual(record["losses"][arm], {
                "transition": loss1, "reward": loss2,
                "staged_brier": (loss1 + loss2)/2})
            self.assertEqual(output["losses"][arm],
                             record["losses"][arm])
        self.assertNotEqual(record["native_before_sha256"],
                            record["native_after_sha256"])
        self.assertFalse(record["scientific_pass"])
        self.assertFalse(record["source_owner_authenticated"])

    def test_one_native_model_and_original_training_updates_identical(self):
        archive, latest = original_models()
        target = StagedScoreReceipts(archive, latest)
        control = StagedTemporalReadout(archive, latest)
        original = tuple(control.native.reader.current.original.base.native._ledger)
        immutable = target.model.native.reader.archived.checkpoint()
        for idx in (23, 31):
            ref, views, row = public_fixture(idx)
            forecast = target.begin(ref, views, row["x1"])
            control.begin(ref, views, row["x1"])
            self.assertEqual(target.model.native.checkpoint(),
                             control.native.checkpoint())
            target.record_transition(ref, row["s2"])
            control.record_transition(ref, row["s2"])
            self.assertEqual(target.model.native.checkpoint(),
                             control.native.checkpoint())
            second = target.choose_second(ref, row["x2"])
            control.choose_second(ref, row["x2"])
            self.assertEqual(target.model.native.checkpoint(),
                             control.native.checkpoint())
            result = target.complete(ref, row["y"])
            control.complete(ref, row["y"])
            self.assertEqual(result["transition"], forecast)
            self.assertEqual(result["reward"], second)
            self.assertEqual(target.model.checkpoint(), control.checkpoint())
            self.assertEqual(tuple(target.model.native.reader.current.original.base.native
                                   ._ledger[:len(original)]), original)
            self.assertEqual(target.model.native.reader.archived.checkpoint(),
                             immutable)
        self.assertEqual(len(target.receipts), 2)

    def test_unseen_reward_cannot_change_earlier_issued_forecast(self):
        archive, latest = original_models()
        a, b = StagedScoreReceipts(archive,latest),StagedScoreReceipts(archive,latest)
        ref, views, row = public_fixture(13)
        first = a.begin(ref,views,row["x1"])
        self.assertEqual(first,b.begin(ref,views,row["x1"]))
        a.record_transition(ref,row["s2"])
        b.record_transition(ref,row["s2"])
        second = a.choose_second(ref,row["x2"])
        self.assertEqual(second,b.choose_second(ref,row["x2"]))
        old_native = a.model.native.checkpoint()
        self.assertEqual(old_native,b.model.native.checkpoint())
        out_a = a.complete(ref,0)
        out_b = b.complete(ref,1)
        self.assertEqual(out_a["transition"],out_b["transition"])
        self.assertEqual(out_a["reward"],out_b["reward"])
        self.assertNotEqual(a.receipts[0]["losses"],b.receipts[0]["losses"])
        self.assertEqual(len(a.receipts),1)
        self.assertEqual(len(b.receipts),1)

    def test_pending_cold_restore_every_stage_and_complete_replay(self):
        archive, latest = original_models()
        model = StagedScoreReceipts(archive,latest)
        for idx in (7, 23):
            ref, views, row = public_fixture(idx)
            model.begin(ref,views,row["x1"])
            for target_stage in ("first","transition","second"):
                if target_stage=="transition":
                    model.record_transition(ref,row["s2"])
                if target_stage=="second":
                    model.choose_second(ref,row["x2"])
                raw = model.checkpoint()
                cold = StagedScoreReceipts.restore(raw,digest(raw),
                                                   archive,latest)
                self.assertEqual(cold.checkpoint(),raw)
                self.assertEqual(cold.model.pending,model.model.pending)
                self.assertEqual(cold.receipts,model.receipts)
            model.complete(ref,row["y"])
            raw = model.checkpoint()
            cold = StagedScoreReceipts.restore(raw,digest(raw),
                                               archive,latest)
            self.assertEqual(cold.checkpoint(),raw)
            self.assertEqual(cold.model.native.checkpoint(),
                             model.model.native.checkpoint())

    def test_rehashed_scores_and_rehashed_stage_forecast_fail_replay(self):
        archive, latest = original_models()
        model = StagedScoreReceipts(archive,latest)
        stages(model,public_fixture(23))
        raw = model.checkpoint()
        self.assertEqual(StagedScoreReceipts.restore(raw,digest(raw),
                                                     archive,latest).checkpoint(),raw)
        altered = json.loads(raw)
        altered["receipts"][0]["losses"]["temporal"]["staged_brier"]=.123
        new = canonical(altered)
        with self.assertRaises(ValueError):
            StagedScoreReceipts.restore(new,digest(new),archive,latest)
        altered = json.loads(raw)
        altered["receipts"][0]["transition_forecast"]["live"]=.875
        new = canonical(altered)
        with self.assertRaises(ValueError):
            StagedScoreReceipts.restore(new,digest(new),archive,latest)
        altered = json.loads(raw)
        altered["ret03_ascii"] += " "
        altered["ret03_sha256"]=digest(altered["ret03_ascii"].encode("ascii"))
        new = canonical(altered)
        with self.assertRaises(ValueError):
            StagedScoreReceipts.restore(new,digest(new),archive,latest)

    def test_rehashed_forged_pending_source_is_rejected(self):
        archive, latest = original_models()
        model = StagedScoreReceipts(archive,latest)
        ref,views,row = public_fixture(7)
        model.begin(ref,views,row["x1"])
        raw = model.checkpoint()
        changed = json.loads(raw)
        inside = json.loads(changed["ret03_ascii"])
        inside["pending"]["transition"]["archive"] = .75
        changed["ret03_ascii"] = canonical(inside).decode("ascii")
        changed["ret03_sha256"]=digest(changed["ret03_ascii"].encode("ascii"))
        forged=canonical(changed)
        with self.assertRaises(ValueError):
            StagedScoreReceipts.restore(forged,digest(forged),archive,latest)

    def test_out_of_order_terminal_and_repeat_have_no_native_side_effect(self):
        model = StagedScoreReceipts(*original_models())
        ref,views,row=public_fixture(31)
        old=model.checkpoint()
        with self.assertRaises(ValueError):
            model.complete(ref,row["y"])
        self.assertEqual(model.checkpoint(),old)
        model.begin(ref,views,row["x1"])
        with self.assertRaises(ValueError):
            model.complete(ref,row["y"])
        model.record_transition(ref,row["s2"])
        with self.assertRaises(ValueError):
            model.complete(ref,row["y"])
        model.choose_second(ref,row["x2"])
        before=model.checkpoint()
        with self.assertRaises(ValueError):
            model.complete(ref,2)
        self.assertEqual(model.checkpoint(),before)
        model.complete(ref,row["y"])
        done=model.checkpoint()
        with self.assertRaises(ValueError):
            model.begin(ref,views,row["x1"])
        self.assertEqual(model.checkpoint(),done)
        self.assertEqual(len(model.receipts),1)


if __name__ == "__main__":
    unittest.main()
