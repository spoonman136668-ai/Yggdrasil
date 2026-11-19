"""RET02 source-only temporal-context native engineering negatives.

All additional actions here are hand-authored PUBLIC-SHAPED mechanical
fixtures, not protected source episodes, scored science or original-world
first-use. Original RET01 previously consumed development seeds are NOT run.
"""
import hashlib
import json
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_temporal_context import (
    NativeTemporalContextReadout, MAX_NEW_EVENTS, WIDTH
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research" / "contrib" / "chatgpt"


def models(seed=14071):
    old = json.loads((BASE/"YGG-JEPA2-03"/f"seed-{seed}-state.json").read_bytes())
    new = json.loads((BASE/"YGG-JEPA2-04"/f"seed-{seed}-state.json").read_bytes())
    archive = old["state_ascii"].encode("ascii")
    live = new["checkpoint_ascii"].encode("ascii")
    assert digest(archive) == old["state_sha256"]
    assert digest(live) == new["checkpoint_sha256"]
    return archive, live


def mechanical(index):
    views = ((index & 1, (index >> 1) & 1),
             (index & 1, (index >> 2) & 1))
    row = {"s1": views[0][0], "x1": (index >> 1) & 1,
           "s2": (index >> 2) & 1, "x2": (index >> 3) & 1,
           "y": (index >> 4) & 1}
    identifier = hashlib.sha256(
        f"RET02-PUBLIC-SHAPED-UNIT-MECHANICS-{index}".encode()
    ).hexdigest()
    return identifier, views, row


class TemporalContextEngineering(unittest.TestCase):
    def test_forecast_is_pure_and_features_exclude_current_answers(self):
        bank = NativeTemporalContextReadout(*models())
        e = mechanical(7)
        old_native = bank.reader.current.checkpoint()
        old_archive = bank.reader.archived.checkpoint()
        old = bank.checkpoint()
        x = bank.features(e[1], e[2])
        other = dict(e[2])
        other["s2"] ^= 1
        other["y"] ^= 1
        self.assertEqual(x, bank.features(e[1], other))
        self.assertEqual(len(x), WIDTH)
        a = bank.forecast(e[1], e[2])
        self.assertTrue(0 <= a["weight_archived"] <= 1)
        self.assertEqual(set(a), {
            "archive", "live", "ret01_gate", "temporal", "weight_archived"})
        self.assertEqual(bank.reader.current.checkpoint(), old_native)
        self.assertEqual(bank.reader.archived.checkpoint(), old_archive)
        self.assertEqual(bank.checkpoint(), old)

    def test_training_only_after_admission_retains_original_weights(self):
        old, latest = models()
        bank = NativeTemporalContextReadout(old, latest)
        init_archive = bank.reader.archived.checkpoint()
        init_ledger = tuple(bank.reader.current.original.base.native._ledger)
        initial_weights = tuple(bank.weights)
        for index in (7, 23, 31):
            event = mechanical(index)
            scored = bank.forecast(event[1], event[2])
            observed = bank.observe(*event)
            self.assertEqual(observed, scored)
        self.assertEqual(len(bank.events), 3)
        self.assertEqual(
            tuple(bank.reader.current.original.base.native._ledger[:len(init_ledger)]),
            init_ledger)
        self.assertEqual(
            len(bank.reader.current.original.base.native._ledger),
            len(init_ledger)+3)
        self.assertEqual(bank.reader.archived.checkpoint(), init_archive)
        self.assertNotEqual(tuple(bank.weights), initial_weights)
        self.assertTrue(all(-8 <= w <= 8 for w in bank.weights))
        self.assertFalse(json.loads(bank.checkpoint())["scientific_pass"])

    def test_history_is_strictly_past_and_no_history_ablation_is_real(self):
        bank = NativeTemporalContextReadout(*models())
        a, b = mechanical(7), mechanical(23)
        baseline = bank.features(b[1], b[2])
        self.assertEqual(baseline, bank.features(b[1], b[2], no_history=True))
        bank.observe(*a)
        history = bank.features(b[1], b[2])
        no_hist = bank.features(b[1], b[2], no_history=True)
        self.assertNotEqual(history[7:15], no_hist[7:15])
        self.assertEqual(no_hist[7:15], (0.0,)*8)
        self.assertEqual(history[:7], no_hist[:7])
        self.assertEqual(history[15:], no_hist[15:])
        old = bank.checkpoint()
        bank.forecast(b[1], b[2], no_history=True)
        self.assertEqual(bank.checkpoint(), old)

    def test_duplicate_conflict_and_old_consumed_source_fail_closed(self):
        bank = NativeTemporalContextReadout(*models())
        e = mechanical(5)
        bank.observe(*e)
        before = bank.checkpoint()
        self.assertIsNone(bank.observe(*e))
        self.assertEqual(bank.checkpoint(), before)
        incompatible = dict(e[2])
        incompatible["y"] ^= 1
        with self.assertRaises(ValueError):
            bank.observe(e[0], e[1], incompatible)
        self.assertEqual(bank.checkpoint(), before)
        bad_id = ("x" * 64)
        with self.assertRaises(ValueError):
            bank.observe(bad_id, e[1], e[2])
        self.assertEqual(bank.checkpoint(), before)
        previous = bank.reader.current.original.base.native._ledger[0]
        old_id, old_views, x1, s2, x2, y = previous
        old_row = {"s1": old_views[0][0], "x1": x1,
                   "s2": s2, "x2": x2, "y": y}
        with self.assertRaises(ValueError):
            bank.observe(old_id, old_views, old_row)
        self.assertEqual(bank.checkpoint(), before)

    def test_cold_replay_exact_and_hash_tampering_rejected(self):
        old, live = models()
        bank = NativeTemporalContextReadout(old, live)
        for index in (7, 23):
            bank.observe(*mechanical(index))
        raw = bank.checkpoint()
        cold = NativeTemporalContextReadout.restore(raw, digest(raw), old, live)
        self.assertEqual(cold.checkpoint(), raw)
        q = mechanical(31)
        self.assertEqual(cold.forecast(q[1], q[2]),
                         bank.forecast(q[1], q[2]))
        tampered = json.loads(raw)
        tampered["weights"][2] = 0.125
        forged = canonical(tampered)
        with self.assertRaises(ValueError):
            NativeTemporalContextReadout.restore(
                forged, digest(forged), old, live)
        tampered = json.loads(raw)
        tampered["events"][0]["row"]["y"] ^= 1
        forged = canonical(tampered)
        with self.assertRaises(ValueError):
            NativeTemporalContextReadout.restore(
                forged, digest(forged), old, live)
        with self.assertRaises(ValueError):
            NativeTemporalContextReadout.restore(raw, "0"*64, old, live)

    def test_event_budget_is_checked_before_witness_or_weight_mutation(self):
        bank = NativeTemporalContextReadout(*models())
        original = bank.reader.current.checkpoint()
        weights = tuple(bank.weights)
        bank.events = [{"source_id": "0"*64}]*MAX_NEW_EVENTS
        # This deliberately corrupts only a throwaway in-memory fixture
        # to test the cap. It is never serialized or admitted to the native
        # source ledger; a valid new identity must fail before any update.
        with self.assertRaises(ValueError):
            bank.observe(*mechanical(77))
        self.assertEqual(bank.reader.current.checkpoint(), original)
        self.assertEqual(tuple(bank.weights), weights)


if __name__ == "__main__":
    unittest.main()
