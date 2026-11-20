"""Source-free controls for archived P0 model-restoration adapter."""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/contrib/chatgpt/CAUSAL-AMALGAM/archive_p0_cold_replay.py"
SPEC = spec_from_file_location("archive_p0_cold_replay_test", SCRIPT)
P0 = module_from_spec(SPEC)
SPEC.loader.exec_module(P0)


class ArchivedP0RestoreControls(unittest.TestCase):
    def test_all_supported_policy_cells_have_deterministic_routing(self):
        for name, expected in P0.MODES.items():
            policy = P0.make_policy(object(), name)
            self.assertEqual(len(policy._evidence), 0 if name == "native" else 20)
            for context in (0, 1):
                views = ((context, 0), (context, 1))
                for first in (0, 1):
                    self.assertEqual(policy.selection(views, first), expected)
                    for state in (0, 1):
                        for second in (0, 1):
                            self.assertEqual(
                                policy.selection(views, first, state, second), expected)

    def test_routing_is_explicitly_artificial_not_model_training(self):
        direct = P0.route_evidence("direct")
        temporal = P0.route_evidence("temporal")
        self.assertEqual(set(direct), set(temporal))
        self.assertTrue(all(type(pair[0]) is Fraction
                            for hist in direct.values() for pair in hist))
        self.assertTrue(all(len(history) == 4 for history in direct.values()))
        self.assertEqual(P0.route_evidence("native"), {})
        with self.assertRaisesRegex(ValueError, "routing fixture"):
            P0.route_evidence("unknown")

    def test_rejects_consumed_selector_trace_tampering_before_any_replay(self):
        import json
        with TemporaryDirectory() as d:
            directory = Path(d)
            trace_dir = directory / "selection-dev-01"
            trace_dir.mkdir()
            (trace_dir / "producer.json").write_text(
                json.dumps({"trace_sha256": "0" * 64}))
            (trace_dir / "audit.json").write_text(
                json.dumps({"development": "DEV_NO_GO"}))
            (trace_dir / "trace.json").write_bytes(b"[]")
            original = P0.HERE
            try:
                P0.HERE = directory
                with self.assertRaisesRegex(ValueError, "TRACE_PIN"):
                    P0.replay_consumed_selector(object(), directory)
            finally:
                P0.HERE = original

    def test_rejects_invalid_consumed_selection_roster_before_replay(self):
        import json
        from yggdrasil.native_context_basis import digest
        with TemporaryDirectory() as d:
            directory = Path(d)
            trace_dir = directory / "selection-dev-01"
            trace_dir.mkdir()
            raw = b"[]"
            (trace_dir / "trace.json").write_bytes(raw)
            (trace_dir / "producer.json").write_text(json.dumps({
                "trace_sha256": digest(raw), "episodes": 96,
                "parent_sha256": "incorrect-original-parent",
            }))
            (trace_dir / "audit.json").write_text(
                json.dumps({"development": "DEV_NO_GO"}))
            original = P0.HERE
            try:
                P0.HERE = directory
                with self.assertRaisesRegex(ValueError, "SELECTOR_PROTOCOL"):
                    P0.replay_consumed_selector(object(), directory)
            finally:
                P0.HERE = original

    def test_frozen_shadow_ordinals_are_phase_boundaries_not_post_result_selected(self):
        self.assertEqual(P0.SHADOW_ORDINALS, (1, 8, 32, 33, 64, 65, 96))
        self.assertEqual([(n - 1) // 32 for n in P0.SHADOW_ORDINALS],
                         [0, 0, 0, 1, 1, 2, 2])

    @staticmethod
    def shadow_fixtures():
        from yggdrasil.native_context_basis import canonical, digest
        # Source-free fabricated scores only; no original-source or model replay.
        rows = []
        for ordinal in P0.SHADOW_ORDINALS:
            heads = {name: {
                "old_brier_drift": 0.0,
                "within_existing_quine_comparison": True,
            } for name in P0.HEAD_NAMES}
            rows.append({
                "ordinal": ordinal,
                "phase": (ordinal - 1) // 32,
                "witness_sha256": digest(canonical([ordinal])),
                "head_guard": {
                    "schema": "yggdrasil.amalgam.four-head-one-witness-advice.v1",
                    "passed": True, "old_ledger_sha256": P0.EXPECTED_LEDGER,
                    "old_witness_count": P0.EXPECTED_EPISODES,
                    "anchor_checkpoint_sha256":
                        "576370a1963158f7dc43099360f491eb6a1e49355448922943b6d484c8",
                    "heads": heads,
                },
            })
        return rows

    def test_shadow_summary_counts_synthetic_head_veto_without_enforcement(self):
        samples = self.shadow_fixtures()
        samples[3]["head_guard"]["heads"]["direct_transition"] = {
            "old_brier_drift": 0.030,
            "within_existing_quine_comparison": False,
        }
        samples[3]["head_guard"]["passed"] = False
        result = P0.summarize_shadow(samples)
        self.assertEqual(result["sample_count"], 7)
        self.assertEqual(result["shadow_head_only_would_veto_count"], 1)
        self.assertEqual(result["shadow_head_only_within_comparison_count"], 6)
        self.assertEqual(result["real_vetoes_enforced"], 0)
        self.assertEqual(result["source_actions"], 0)
        self.assertFalse(result["scientific_pass"])

    def test_shadow_summary_rejects_forged_ordinal_phase_pins_and_status(self):
        import copy
        base = self.shadow_fixtures()
        with self.assertRaisesRegex(ValueError, "SAMPLE_COUNT"):
            P0.summarize_shadow(base[:-1])
        for mutation, error in (
            (lambda a: a[2].update(ordinal=31), "ORDINAL"),
            (lambda a: a[2].update(phase=1), "ORDINAL"),
            (lambda a: a[0]["head_guard"].update(old_ledger_sha256="0" * 64), "CUSTODY"),
            (lambda a: a[0]["head_guard"].update(passed=1), "CUSTODY"),
            (lambda a: a[0]["head_guard"]["heads"]["temporal_transition"].update(
                old_brier_drift=0.021), "CLASSIFICATION"),
            (lambda a: a[0]["head_guard"].update(passed=False), "PASS_MISMATCH"),
        ):
            item = copy.deepcopy(base)
            mutation(item)
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                P0.summarize_shadow(item)

    def test_original_selection_archive_is_a_negative_not_an_improvement(self):
        import json
        folder = P0.HERE / "selection-dev-01"
        original = json.loads((folder / "trace.json").read_bytes())
        self.assertEqual(len(original), 96)
        self.assertTrue(all(event["origin"] == 0 for event in original))
        self.assertEqual([sum(e["phase"] == i for e in original)
                          for i in range(3)], [32, 32, 32])
        audit = json.loads((folder / "audit.json").read_bytes())
        self.assertEqual(audit["development"], "DEV_NO_GO")
        self.assertEqual(audit["specialist_origin_counts"], {"0": 64})

    def test_rejects_wrong_archived_member_bytes(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / "native.json").write_bytes(b"immutable")
            from hashlib import sha256
            good = sha256(b"immutable").hexdigest()
            self.assertEqual(P0.checked(root, "native.json", good), b"immutable")
            with self.assertRaisesRegex(ValueError, "PIN_MISMATCH"):
                P0.checked(root, "native.json", "0" * 64)

    def test_protocol_mismatch_aborts_before_reading_any_archive(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            protocol = root / "bad.json"
            protocol.write_text('{"joint_sha256":"bad"}', encoding="utf-8")
            old = P0.PROTOCOL
            try:
                P0.PROTOCOL = protocol
                with self.assertRaisesRegex(ValueError, "PROTOCOL_PIN_MISMATCH"):
                    P0.run(root)
            finally:
                P0.PROTOCOL = old


if __name__ == "__main__":
    unittest.main()
