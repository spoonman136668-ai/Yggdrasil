"""RET03 source-only *staged* public causal timing contracts.

Uses manually constructed public-shaped bytes only. Not a protected
original-world first-use, fresh evaluation cohort or scientific score.
"""
import hashlib
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_staged_temporal import StagedTemporalReadout
from yggdrasil.native_temporal_context import NativeTemporalContextReadout

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "contrib" / "chatgpt"


def original_models():
    old = json.loads((BASE/"YGG-JEPA2-03"/"seed-14071-state.json").read_bytes())
    new = json.loads((BASE/"YGG-JEPA2-04"/"seed-14071-state.json").read_bytes())
    archive = old["state_ascii"].encode("ascii")
    live = new["checkpoint_ascii"].encode("ascii")
    assert digest(archive) == old["state_sha256"]
    assert digest(live) == new["checkpoint_sha256"]
    return archive, live


def public_fixture(index):
    views = ((index & 1, (index >> 1) & 1),
             (index & 1, (index >> 2) & 1))
    row = {"s1": views[0][0], "x1": (index >> 1) & 1,
           "s2": (index >> 2) & 1, "x2": (index >> 3) & 1,
           "y": (index >> 4) & 1}
    ref = hashlib.sha256(
        f"RET03-SOURCE-FREE-PUBLIC-SHAPE-{index}".encode("ascii")
    ).hexdigest()
    return ref, views, row


def run_stages(model, item):
    ref, views, row = item
    first = model.begin(ref, views, row["x1"])
    model.record_transition(ref, row["s2"])
    second = model.choose_second(ref, row["x2"])
    result = model.complete(ref, row["y"])
    assert result == {"transition": first, "reward": second}
    return result


class StagedTemporalEngineering(unittest.TestCase):
    def test_two_actions_strict_order_and_predict_then_learn(self):
        archive, live = original_models()
        model = StagedTemporalReadout(archive, live)
        initial_native = model.native.reader.current.checkpoint()
        initial_archive = model.native.reader.archived.checkpoint()
        initial_weights = tuple(model.native.weights)
        ref, views, row = public_fixture(23)
        first = model.begin(ref, views, row["x1"])
        self.assertEqual(set(first), {
            "archive", "live", "temporal", "archive_weight"})
        self.assertTrue(0 <= first["temporal"] <= 1)
        self.assertEqual(model.native.reader.current.checkpoint(), initial_native)
        self.assertEqual(tuple(model.native.weights), initial_weights)
        model.record_transition(ref, row["s2"])
        self.assertEqual(model.native.reader.current.checkpoint(), initial_native)
        second = model.choose_second(ref, row["x2"])
        self.assertTrue(0 <= second["temporal"] <= 1)
        self.assertEqual(model.native.reader.current.checkpoint(), initial_native)
        output = model.complete(ref, row["y"])
        self.assertEqual(output, {"transition": first, "reward": second})
        self.assertEqual(len(model.native.events), 1)
        self.assertEqual(model.native.reader.archived.checkpoint(),
                         initial_archive)
        self.assertNotEqual(model.native.reader.current.checkpoint(),
                            initial_native)
        self.assertIsNone(model.pending)
        self.assertFalse(json.loads(model.checkpoint())["scientific_pass"])

    def test_reward_never_entered_first_forecast_and_y_never_second(self):
        archive, live = original_models()
        item = public_fixture(13)
        ref, views, row = item
        a = StagedTemporalReadout(archive, live)
        b = StagedTemporalReadout(archive, live)
        # The first-stage call has NO fields for future s2, x2 or y.
        first = a.begin(ref, views, row["x1"])
        self.assertEqual(first, b.begin(ref, views, row["x1"]))
        a.record_transition(ref, 0)
        b.record_transition(ref, 1)
        pred_a = a.choose_second(ref, row["x2"])
        pred_b = b.choose_second(ref, row["x2"])
        self.assertTrue(all(0 <= x <= 1 for x in
                            (pred_a["temporal"], pred_b["temporal"])))
        # The unknown second-step reward is nowhere in the prior API.
        before = a.checkpoint()
        a.complete(ref, 0)
        self.assertNotEqual(before, a.checkpoint())
        self.assertEqual(first, b.pending["transition"])
        self.assertEqual(pred_b, b.pending["reward"])

    def test_existing_cumulative_model_identical_to_full_row_update(self):
        archive, live = original_models()
        staged = StagedTemporalReadout(archive, live)
        original = NativeTemporalContextReadout(archive, live)
        initial_prefix = tuple(staged.native.reader.current.original.base.native._ledger)
        for index in (13, 23):
            item = public_fixture(index)
            run_stages(staged, item)
            original.observe(*item)
            self.assertEqual(staged.native.checkpoint(), original.checkpoint())
            self.assertEqual(tuple(staged.native.weights),
                             tuple(original.weights))
        self.assertEqual(tuple(staged.native.reader.current.original.base.native
                               ._ledger[:len(initial_prefix)]), initial_prefix)

    def test_exact_cold_resume_after_each_public_phase(self):
        archive, live = original_models()
        staged = StagedTemporalReadout(archive, live)
        e = public_fixture(7)
        ref, views, row = e
        for phase in ("first", "transition", "second"):
            if phase == "first":
                staged.begin(ref, views, row["x1"])
            elif phase == "transition":
                staged.record_transition(ref, row["s2"])
            else:
                staged.choose_second(ref, row["x2"])
            raw = staged.checkpoint()
            cold = StagedTemporalReadout.restore(raw, digest(raw),
                                                 archive, live)
            self.assertEqual(cold.checkpoint(), raw)
            self.assertEqual(cold.pending, staged.pending)
        staged.complete(ref, row["y"])
        final_raw = staged.checkpoint()
        cold = StagedTemporalReadout.restore(final_raw,digest(final_raw),
                                            archive, live)
        self.assertEqual(cold.checkpoint(), final_raw)
        self.assertEqual(cold.native.reader.current.checkpoint(),
                         staged.native.reader.current.checkpoint())

    def test_out_of_order_and_duplicate_replay_leave_custody_intact(self):
        model = StagedTemporalReadout(*original_models())
        ref, views, row = public_fixture(31)
        old = model.checkpoint()
        with self.assertRaises(ValueError):
            model.record_transition(ref, row["s2"])
        with self.assertRaises(ValueError):
            model.choose_second(ref, row["x2"])
        with self.assertRaises(ValueError):
            model.complete(ref, row["y"])
        self.assertEqual(model.checkpoint(), old)
        model.begin(ref, views, row["x1"])
        first = model.checkpoint()
        with self.assertRaises(ValueError):
            model.begin(ref, views, row["x1"])
        with self.assertRaises(ValueError):
            model.choose_second(ref, row["x2"])
        with self.assertRaises(ValueError):
            model.record_transition(ref, 2)
        self.assertEqual(model.checkpoint(), first)
        model.record_transition(ref, row["s2"])
        with self.assertRaises(ValueError):
            model.record_transition(ref, row["s2"])
        model.choose_second(ref, row["x2"])
        second = model.checkpoint()
        with self.assertRaises(ValueError):
            model.complete(ref, 2)
        with self.assertRaises(ValueError):
            model.complete("0"*64, row["y"])
        self.assertEqual(model.checkpoint(), second)
        model.complete(ref, row["y"])
        final = model.checkpoint()
        with self.assertRaises(ValueError):
            model.begin(ref, views, row["x1"])
        self.assertEqual(model.checkpoint(), final)

    def test_rehashed_forged_pending_and_weights_fail_cold_replay(self):
        archive, live = original_models()
        model = StagedTemporalReadout(archive, live)
        ref, views, row = public_fixture(23)
        model.begin(ref, views, row["x1"])
        model.record_transition(ref, row["s2"])
        model.choose_second(ref, row["x2"])
        raw = model.checkpoint()
        forged = json.loads(raw)
        forged["pending"]["reward"]["temporal"] = 0.1234
        bad = canonical(forged)
        with self.assertRaises(ValueError):
            StagedTemporalReadout.restore(bad, digest(bad), archive, live)
        forged = json.loads(raw)
        forged["pending"]["observed_s2"] ^= 1
        bad = canonical(forged)
        with self.assertRaises(ValueError):
            StagedTemporalReadout.restore(bad, digest(bad), archive, live)
        forged = json.loads(raw)
        forged["native_ascii"] = forged["native_ascii"] + " "
        forged["native_sha256"] = digest(forged["native_ascii"].encode("ascii"))
        bad = canonical(forged)
        with self.assertRaises(ValueError):
            StagedTemporalReadout.restore(bad, digest(bad), archive, live)

    def test_after_observation_history_changes_readout_without_reset(self):
        model = StagedTemporalReadout(*original_models())
        second_item = public_fixture(31)
        before = model.native.features(second_item[1], second_item[2])
        run_stages(model, public_fixture(13))
        after = model.native.features(second_item[1], second_item[2])
        self.assertNotEqual(before[7:15], after[7:15])
        self.assertEqual(after[7:15],
                         model.native.features(second_item[1],
                                               second_item[2])[7:15])
        self.assertEqual(len(model.native.events), 1)
        self.assertIsNone(model.pending)


if __name__ == "__main__":
    unittest.main()
