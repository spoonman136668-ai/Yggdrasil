"""Source-free negative controls for real four-JEPA-head retention readout."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
SPEC = spec_from_file_location("four_head_retention", HERE / "four_head_retention.py")
AUDIT = module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def events(count=24):
    return tuple(
        (f"historical-{i}", ((i % 2, 0), (i % 2, 1)), i % 2, 1, i % 2, 1)
        for i in range(count)
    )


def heads():
    return (ActionLatentSpecialist("transition"),
            ActionLatentSpecialist("reward"),
            TemporalLatentSpecialist("transition"),
            TemporalLatentSpecialist("reward"))


class FakeNative:
    def __init__(self, ledger):
        self._ledger = ledger

    def _episode_reader(self):
        return self

    def experience_context_forecast(self, view, first, *tail):
        # No source simulation; fixed mock native probability for Quine.
        return 0.5


class FakeCore:
    """Test-only source-free object using the real four JEPA head classes."""
    def __init__(self, ledger, source_heads=None):
        self.native = FakeNative(tuple(ledger))
        self._heads = heads() if source_heads is None else tuple(source_heads)

    def checkpoint(self):
        return canonical({
            "ledger": self.native._ledger,
            "heads": [(h.as_data() if hasattr(h, "as_data") else h.data())
                      for h in self._heads],
        })

    def clone(self, ledger=None):
        return FakeCore(self.native._ledger if ledger is None else ledger,
                        tuple(h.clone() for h in self._heads))

    def observe_experience(self, identifier, views, row, *,
                           source_sha256, packet_sha256):
        if packet_sha256 != digest(canonical([identifier, views, row])):
            raise ValueError("source packet mismatch")
        event = (identifier, views, row["x1"], row["s2"], row["x2"], row["y"])
        existing = self.native._ledger
        if any(old[0] == identifier for old in existing):
            if event not in existing:
                raise ValueError("conflicting witnessed event")
            return self
        return self.clone(existing + (event,))


class FourHeadRetentionControls(unittest.TestCase):
    def setUp(self):
        self.anchor = FakeCore(events())
        # One explicitly artificial newer public witness, never a source-world action.
        later = ("new-24", ((0, 0), (0, 1)), 0, 1, 0, 1)
        self.successor = self.anchor.clone(events() + (later,))

    def test_real_head_classes_all_four_unchanged(self):
        result = AUDIT.audit_old_heads(self.anchor, self.successor,
                                       self.successor.clone())
        self.assertEqual(tuple(result["heads"]), AUDIT.HEAD_NAMES)
        self.assertEqual(result["disposition"],
                         "HISTORICAL_HEAD_RETENTION_WITHIN_COMPARISON")
        self.assertEqual(result["old_witness_count"], 24)
        self.assertEqual(result["continuation_witness_count"], 1)
        self.assertEqual(result["original_world_actions"], 0)
        self.assertFalse(result["scientific_pass"])
        self.assertTrue(all(x["old_brier_drift"] == 0
                            for x in result["heads"].values()))

    def test_dormant_reward_head_regression_detected_with_same_native(self):
        bad = self.successor.clone()
        bad._heads[1].predictor_bias = [-3.0, 3.0]
        self.assertEqual(bad.native._ledger, self.successor.native._ledger)
        report = AUDIT.audit_old_heads(self.anchor, bad, bad.clone())
        self.assertFalse(report["heads"]["direct_reward"]
                         ["within_existing_quine_comparison"])
        self.assertEqual(report["disposition"],
                         "HISTORICAL_HEAD_RETENTION_EXCEEDS_COMPARISON")
        self.assertEqual(report["heads"]["direct_transition"]["old_brier_drift"], 0)

    def test_temporal_head_regression_detected_with_same_native(self):
        bad = self.successor.clone()
        bad._heads[3].predictor_bias = [-3.0, 3.0]
        report = AUDIT.audit_old_heads(self.anchor, bad, bad.clone())
        self.assertGreater(report["heads"]["temporal_reward"]["old_brier_drift"], .02)
        self.assertEqual(report["heads"]["direct_reward"]["old_brier_drift"], 0)

    def test_historical_prefix_forgery_rejected(self):
        modified = list(self.successor.native._ledger)
        modified[0] = ("forged",) + modified[0][1:]
        forged = self.anchor.clone(tuple(modified))
        with self.assertRaisesRegex(ValueError, "HISTORICAL_PREFIX"):
            AUDIT.audit_old_heads(self.anchor, forged, forged.clone())

    def test_cold_restore_head_tampering_rejected(self):
        different = self.successor.clone()
        different._heads[0].predictor_bias[0] += .25
        with self.assertRaisesRegex(ValueError, "COLD_CHECKPOINT_MISMATCH"):
            AUDIT.audit_old_heads(self.anchor, self.successor, different)

    def test_wrong_head_order_and_bad_label_rejected(self):
        wrong_order = self.successor.clone()
        wrong_order._heads = wrong_order._heads[2:] + wrong_order._heads[:2]
        with self.assertRaisesRegex(ValueError, "HEAD_IDENTITY"):
            AUDIT.audit_old_heads(self.anchor, wrong_order, wrong_order)
        bad_ledger = list(self.anchor.native._ledger)
        bad_ledger[0] = bad_ledger[0][:-1] + ("1",)
        broken = FakeCore(tuple(bad_ledger))
        with self.assertRaisesRegex(ValueError, "PUBLIC_EVENT"):
            AUDIT.audit_old_heads(broken, self.successor, self.successor)

    def test_zero_old_history_not_accepted_as_retention(self):
        empty = FakeCore(())
        with self.assertRaisesRegex(ValueError, "OLD_WITNESS_LIMIT"):
            AUDIT.audit_old_heads(empty, self.successor, self.successor.clone())

    def test_one_witness_retention_accepts_unchanged_trained_heads(self):
        report = AUDIT.assess_one_witness_head_update(
            self.anchor, self.anchor, self.successor)
        self.assertTrue(report["passed"])
        self.assertEqual(report["old_witness_count"], 24)
        self.assertEqual(tuple(report["heads"]), AUDIT.HEAD_NAMES)
        self.assertEqual(report["candidate_checkpoint_sha256"],
                         digest(self.successor.checkpoint()))
        self.assertFalse(report["scientific_pass"])

    def test_one_witness_dormant_transition_drift_fails_with_native_unchanged(self):
        bad = self.successor.clone()
        bad._heads[0].predictor_bias = [-3.0, 3.0]
        report = AUDIT.assess_one_witness_head_update(self.anchor, self.anchor, bad)
        self.assertFalse(report["passed"])
        self.assertGreater(report["heads"]["direct_transition"]["old_brier_drift"],
                           AUDIT.MAX_COMPARISON_DRIFT)
        self.assertEqual(report["heads"]["direct_reward"]["old_brier_drift"], 0)

    def test_head_veto_uses_existing_quine_charged_receipt(self):
        from importlib.util import module_from_spec, spec_from_file_location
        from tempfile import TemporaryDirectory
        spec = spec_from_file_location(
            "quine_head_veto", HERE / "quine_retention.py")
        quine = module_from_spec(spec)
        spec.loader.exec_module(quine)
        anchor = self.anchor
        manifest = quine.select_quines(
            anchor, {"fixture-A": (0, 12), "fixture-B": (12, 24)})
        pin = digest(canonical(manifest))
        after = self.successor.clone()
        after._heads[0].predictor_bias = [-3.0, 3.0]
        selected, report = quine.assess_update(
            anchor, anchor, after, manifest, pin, protect_dormant_heads=True)
        self.assertIs(selected, anchor)
        self.assertEqual(report["status"], "VETO_SHARED_STATE_OVERWRITE")
        self.assertFalse(report["dormant_head_retention"]["passed"])
        default, original = quine.assess_update(anchor, anchor, after, manifest, pin)
        self.assertIs(default, after)
        self.assertNotIn("dormant_head_retention", original)
        accepted, ok = quine.assess_update(
            anchor, anchor, self.successor, manifest, pin,
            protect_dormant_heads=True)
        self.assertIs(accepted, self.successor)
        self.assertTrue(ok["dormant_head_retention"]["passed"])

        class InjectedDrift(FakeCore):
            def observe_experience(self, identifier, views, row, *,
                                   source_sha256, packet_sha256):
                proposed = super().observe_experience(
                    identifier, views, row, source_sha256=source_sha256,
                    packet_sha256=packet_sha256)
                proposed._heads[0].predictor_bias = [-3.0, 3.0]
                return proposed

        current = InjectedDrift(anchor.native._ledger,
                                tuple(h.clone() for h in anchor._heads))
        identifier, views, x1, s2, x2, y = self.successor.native._ledger[-1]
        row = {"s1": views[0][0], "x1": x1, "s2": s2, "x2": x2, "y": y}
        kwargs = dict(
            source_sha256="source-free-fixture",
            packet_sha256=digest(canonical([identifier, views, row])),
            protect_dormant_heads=True)
        with self.assertRaisesRegex(RuntimeError, "VETO_REQUIRES_DURABLE"):
            quine.guarded_observe(anchor, current, manifest, pin,
                                  identifier, views, row, **kwargs)
        with self.assertRaisesRegex(RuntimeError, "NOT_ACKNOWLEDGED"):
            quine.guarded_observe(anchor, current, manifest, pin,
                                  identifier, views, row,
                                  on_veto=lambda *_: "not-the-receipt", **kwargs)
        receipts = []
        def acknowledged(content, receipt_sha):
            receipts.append((content, receipt_sha))
            return receipt_sha
        kept, veto = quine.guarded_observe(
            anchor, current, manifest, pin, identifier, views, row,
            on_veto=acknowledged, **kwargs)
        self.assertIs(kept, current)
        self.assertEqual(veto["status"], "VETO_SHARED_STATE_OVERWRITE")
        self.assertEqual(len(receipts), 1)
        self.assertFalse(veto["active_model_contains_rejected_witness"])
        self.assertEqual(len(current.native._ledger), 24)

    def test_bad_head_guard_flag_or_wrong_model_fails_closed(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("quine_head_invalid", HERE / "quine_retention.py")
        quine = module_from_spec(spec)
        spec.loader.exec_module(quine)
        manifest = quine.select_quines(
            self.anchor, {"fixture-A": (0, 12), "fixture-B": (12, 24)})
        pin = digest(canonical(manifest))
        with self.assertRaisesRegex(ValueError, "HEAD4_GUARD_FLAG"):
            quine.assess_update(
                self.anchor, self.anchor, self.successor, manifest, pin,
                protect_dormant_heads=1)
        untyped = self.successor.clone()
        untyped._heads = tuple()
        with self.assertRaisesRegex(ValueError, "HEAD4_HEAD_IDENTITY"):
            quine.assess_update(
                self.anchor, self.anchor, untyped, manifest, pin,
                protect_dormant_heads=True)

    def test_one_witness_forgery_and_multi_event_disallowed(self):
        shifted = list(self.successor.native._ledger)
        shifted[0] = ("old-forged",) + shifted[0][1:]
        with self.assertRaisesRegex(ValueError, "HISTORICAL_PREFIX"):
            AUDIT.assess_one_witness_head_update(
                self.anchor, self.anchor, self.anchor.clone(shifted))
        doubled = self.anchor.clone(self.successor.native._ledger
                                    + (("second", ((0, 0), (0, 1)), 0, 1, 0, 1),))
        with self.assertRaisesRegex(ValueError, "EXACTLY_ONE"):
            AUDIT.assess_one_witness_head_update(
                self.anchor, self.anchor, doubled)


if __name__ == "__main__":
    unittest.main()
