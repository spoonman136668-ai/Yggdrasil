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
