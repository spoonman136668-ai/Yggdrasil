"""RET05 native two-clock credit engineering controls (no source first use).

Only hand-constructed public-shaped mechanical events and previously trained
pinned original native checkpoint bytes are read. No scored RET01-04 replay.
"""
import json
import unittest

from test_native_staged_temporal import original_models, public_fixture
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_staged_credit import (
    StagedCreditReadout, staged_gradient,
)
from yggdrasil.native_staged_score_receipts import StagedScoreReceipts
from yggdrasil.native_temporal_context import LR, DECAY, WIDTH, MAX_WEIGHT


def stages(obj, event):
    ref, views, row = event
    first = obj.begin(ref, views, row["x1"])
    obj.record_transition(ref, row["s2"])
    second = obj.choose_second(ref, row["x2"])
    result = obj.complete(ref, row["y"])
    return first, second, result


class StagedCreditEngineering(unittest.TestCase):
    def test_true_preissued_two_clock_gradient_and_native_continuity(self):
        model = StagedCreditReadout(*original_models())
        ref, views, row = public_fixture(23)
        initial = tuple(model.model.native.weights)
        immutable = model.model.native.reader.archived.checkpoint()
        before_native = model.model.native.reader.checkpoint()
        first = model.begin(ref, views, row["x1"])
        f1 = tuple(model._first_features)
        model.record_transition(ref, row["s2"])
        second = model.choose_second(ref, row["x2"])
        f2 = tuple(model._second_features)
        self.assertEqual(len(f1), WIDTH)
        self.assertEqual(len(f2), WIDTH)
        self.assertEqual(model.model.native.reader.checkpoint(), before_native)
        expected_gradient = staged_gradient(first, second, row["s2"],
                                             row["y"], f1, f2)
        expected = tuple(max(-MAX_WEIGHT, min(MAX_WEIGHT,
            old - LR*(expected_gradient[i] + (DECAY*old if i else 0.0))))
            for i, old in enumerate(initial))
        result = model.complete(ref, row["y"])
        self.assertEqual(tuple(model.model.native.weights), expected)
        self.assertEqual(tuple(model.credit[-1]["gradient"]), expected_gradient)
        self.assertEqual(tuple(model.credit[-1]["readout_before"]), initial)
        self.assertEqual(tuple(model.credit[-1]["readout_after"]), expected)
        self.assertEqual(result["transition"], first)
        self.assertEqual(result["reward"], second)
        self.assertEqual(model.model.native.reader.archived.checkpoint(),
                         immutable)
        self.assertNotEqual(model.model.native.reader.checkpoint(), before_native)
        self.assertEqual(model.credit[-1]["stage_losses"],
                         model.receipts[-1]["losses"])
        self.assertFalse(model.credit[-1]["scientific_pass"])

    def test_difference_from_ret02_postreveal_readout_with_equal_native_basis(self):
        old, new = original_models()
        staged = StagedCreditReadout(old, new)
        original = StagedScoreReceipts(old, new)
        prefix = tuple(staged.model.native.reader.current.original.base.native._ledger)
        for index in (23, 31):
            stages(staged, public_fixture(index))
            stages(original, public_fixture(index))
            self.assertEqual(staged.model.native.reader.checkpoint(),
                             original.model.native.reader.checkpoint())
            self.assertEqual(tuple(staged.model.native.reader.current.original.base.native
                                   ._ledger[:len(prefix)]), prefix)
        self.assertNotEqual(tuple(staged.model.native.weights),
                            tuple(original.model.native.weights))
        self.assertEqual(len(staged.model.native.events), 2)
        self.assertEqual(len(staged.credit), 2)
        self.assertEqual(staged.model.native.reader.archived.checkpoint(),
                         original.model.native.reader.archived.checkpoint())

    def test_issued_probabilities_do_not_depend_on_unknown_reward(self):
        old, new = original_models()
        x = StagedCreditReadout(old, new)
        y = StagedCreditReadout(old, new)
        ref, views, row = public_fixture(13)
        self.assertEqual(x.begin(ref, views, row["x1"]),
                         y.begin(ref, views, row["x1"]))
        x.record_transition(ref, row["s2"])
        y.record_transition(ref, row["s2"])
        self.assertEqual(x.choose_second(ref, row["x2"]),
                         y.choose_second(ref, row["x2"]))
        original = x.model.native.checkpoint()
        self.assertEqual(y.model.native.checkpoint(), original)
        x.complete(ref, 0)
        y.complete(ref, 1)
        self.assertEqual(x.credit[0]["readout_before"],
                         y.credit[0]["readout_before"])
        self.assertNotEqual(x.credit[0]["gradient"],
                            y.credit[0]["gradient"])
        self.assertNotEqual(x.credit[0]["readout_after"],
                            y.credit[0]["readout_after"])

    def test_cold_exact_checkpoint_after_each_public_stage(self):
        old, new = original_models()
        model = StagedCreditReadout(old, new)
        for index in (7, 23):
            ref, views, row = public_fixture(index)
            model.begin(ref, views, row["x1"])
            for stage in ("begin", "transition", "reward"):
                if stage == "transition":
                    model.record_transition(ref, row["s2"])
                if stage == "reward":
                    model.choose_second(ref, row["x2"])
                raw = model.checkpoint()
                cold = StagedCreditReadout.restore(raw, digest(raw), old, new)
                self.assertEqual(cold.checkpoint(), raw)
                self.assertEqual(cold.model.pending, model.model.pending)
                self.assertEqual(cold.credit, model.credit)
            model.complete(ref, row["y"])
            raw = model.checkpoint()
            restored = StagedCreditReadout.restore(raw, digest(raw), old, new)
            self.assertEqual(restored.checkpoint(), raw)
            self.assertEqual(restored.model.native.checkpoint(),
                             model.model.native.checkpoint())
            self.assertEqual(restored.receipts, model.receipts)

    def test_rehashed_ledger_gradient_and_weights_refuse_cold(self):
        old, new = original_models()
        model = StagedCreditReadout(old, new)
        stages(model, public_fixture(23))
        raw = model.checkpoint()
        self.assertEqual(StagedCreditReadout.restore(
            raw, digest(raw), old, new).checkpoint(), raw)
        cases = []
        original = json.loads(raw)
        a = json.loads(raw)
        a["staged_credit"][0]["gradient"][1] += 0.01
        cases.append(a)
        a = json.loads(raw)
        a["staged_credit"][0]["readout_after"][2] = 0.25
        cases.append(a)
        a = json.loads(raw)
        a["ret04_receipts"][0]["losses"]["temporal"]["reward"] = .44
        cases.append(a)
        a = json.loads(raw)
        ret03 = json.loads(a["ret03_ascii"])
        ret02 = json.loads(ret03["native_ascii"])
        ret02["weights"][0] += 0.05
        ret03["native_ascii"] = canonical(ret02).decode("ascii")
        ret03["native_sha256"] = digest(ret03["native_ascii"].encode("ascii"))
        a["ret03_ascii"] = canonical(ret03).decode("ascii")
        a["ret03_sha256"] = digest(a["ret03_ascii"].encode("ascii"))
        cases.append(a)
        for changed in cases:
            altered = canonical(changed)
            self.assertNotEqual(altered, raw)
            with self.assertRaises(ValueError):
                StagedCreditReadout.restore(
                    altered, digest(altered), old, new)
        self.assertEqual(model.checkpoint(), raw)
        self.assertEqual(original["scientific_pass"], False)

    def test_duplicate_out_of_order_invalid_bit_do_not_update(self):
        model = StagedCreditReadout(*original_models())
        ref, views, row = public_fixture(31)
        old = model.checkpoint()
        with self.assertRaises(ValueError):
            model.complete(ref, row["y"])
        self.assertEqual(old, model.checkpoint())
        model.begin(ref, views, row["x1"])
        old = model.checkpoint()
        with self.assertRaises(ValueError):
            model.choose_second(ref, row["x2"])
        self.assertEqual(old, model.checkpoint())
        model.record_transition(ref, row["s2"])
        model.choose_second(ref, row["x2"])
        before = model.checkpoint()
        with self.assertRaises(ValueError):
            model.complete(ref, 2)
        self.assertEqual(before, model.checkpoint())
        model.complete(ref, row["y"])
        done = model.checkpoint()
        with self.assertRaises(ValueError):
            model.begin(ref, views, row["x1"])
        self.assertEqual(done, model.checkpoint())

    def test_history_cumulative_not_reset_and_gradient_is_bounded(self):
        model = StagedCreditReadout(*original_models())
        q = public_fixture(31)
        earlier = model.model.native.features(q[1], q[2])
        for index in (7, 23):
            stages(model, public_fixture(index))
        later = model.model.native.features(q[1], q[2])
        self.assertNotEqual(earlier[7:15], later[7:15])
        self.assertEqual(len(model.model.native.events), 2)
        self.assertTrue(all(-MAX_WEIGHT <= w <= MAX_WEIGHT
                            for w in model.model.native.weights))
        self.assertIsNone(model.model.pending)
        self.assertEqual(len(model.receipts), len(model.credit))
        self.assertTrue(all(x["source_owner_authenticated"] is False
                            for x in model.credit))


if __name__ == "__main__":
    unittest.main()
