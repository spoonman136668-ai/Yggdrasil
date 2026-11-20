"""Source-free negative controls for real four-JEPA-head retention readout."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

from yggdrasil.native_context_basis import canonical
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


if __name__ == "__main__":
    unittest.main()
