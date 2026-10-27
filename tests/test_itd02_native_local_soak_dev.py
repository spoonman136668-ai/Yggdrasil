"""OS-process native learning soak, explicitly SOURCE-FREE.

Real subprocesses, original eight-cell learner, separate cold restarts.
NO published original Shuttle action. NO scientific acceptance.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from yggdrasil.itd02_public_source_journal_dev import (
    inspect_custody, load_verified_native_model,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "itd02_native_local_soak_dev.py"


def invoke(path, *extra):
    return subprocess.run([
        sys.executable, "-B", str(SCRIPT), "--root", str(path),
        "--episodes", "3", "--steps", "4", *extra],
        cwd=ROOT, capture_output=True, text=True, timeout=90, check=False)


class OfflineNativeSoakTests(unittest.TestCase):
    def test_multiple_cold_processes_learn_and_checkpoint_without_original(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / "soak"
            outcome = invoke(root)
            self.assertEqual(outcome.returncode, 0, outcome.stderr[-1200:])
            result = json.loads(
                (root / "source-free-metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "SOURCE_FREE_ENGINEERING_ONLY")
            self.assertFalse(result["retail_pc_qualified"])
            self.assertFalse(result["protected_first_use"])
            self.assertEqual(result["original_source_episodes"], 0)
            self.assertEqual(result["episodes"], 3)
            self.assertEqual(result["total_native_interactions"], 12)
            self.assertEqual(result["cold_process_restarts"], 2)
            self.assertEqual(len(result["per_episode"]), 3)
            if result["total_child_cpu_ns"] is not None:
                self.assertGreater(result["total_child_cpu_ns"], 0)
            # An OS timer may be too coarse for a tiny episode. A measured
            # zero is never emitted as truthful CPU consumption.
            self.assertGreater(result["journal_and_checkpoint_bytes"], 0)
            self.assertIsNone(result["process_tree_peak_rss_bytes"])
            self.assertIsNone(result["power_joules"])
            self.assertTrue(result["native_parameter_identity_changed"])
            for i, row in enumerate(result["per_episode"]):
                self.assertEqual(row["mode"], "SOURCE_FREE_TOY_ONLY_NO_ORIGINAL_WORLD")
                self.assertEqual(row["native_transitions"], (i + 1) * 4)
                d = root / "episodes" / f"{i:03d}"
                receipt = inspect_custody(
                    d, expected_source_sha256=result["source_free_fixture_sha256"])
                self.assertTrue(receipt["checkpoint_verified"])
                cold = load_verified_native_model(
                    d, expected_source_sha256=result["source_free_fixture_sha256"])
                self.assertEqual(cold.model_identities(), row["native_after"])
                if i:
                    self.assertEqual(row["native_before"],
                                     result["per_episode"][i-1]["native_after"])
            self.assertEqual(result["per_episode"][-1]["native_transitions"], 12)
            previous = (root / "episodes" / "000" / "public-events.jsonl").read_bytes()
            rejected = invoke(root)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("SOURCE_FREE_FRESH_RUN_ROOT_REQUIRED", rejected.stderr)
            self.assertEqual(previous, (
                root / "episodes" / "000" / "public-events.jsonl").read_bytes())

    def test_hard_os_child_exit_leaves_quarantine_no_automatic_replay(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / "crashed"
            outcome = invoke(root, "--crash-episode", "1")
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("SOURCE_FREE_CHILD_STOPPED_WITHOUT_REPLAY",
                          outcome.stderr)
            source_sha = __import__("hashlib").sha256(
                b"itd02-yggdrasil-source-free-offline-soak-v1").hexdigest()
            good = inspect_custody(
                root / "episodes" / "000",
                expected_source_sha256=source_sha)
            bad = inspect_custody(
                root / "episodes" / "001",
                expected_source_sha256=source_sha)
            self.assertEqual(good["status"], "COMMITTED")
            self.assertEqual(bad["status"], "QUARANTINE")
            self.assertEqual(bad["steps"], 0)
            self.assertFalse((root / "source-free-metrics.json").exists())
            self.assertFalse((root / "episodes" / "002").exists())
            with self.assertRaisesRegex(ValueError, "COLD_RESTORE_NOT_COMMITTED"):
                load_verified_native_model(
                    root / "episodes" / "001",
                    expected_source_sha256=source_sha)
            again = invoke(root)
            self.assertNotEqual(again.returncode, 0)
            self.assertIn("SOURCE_FREE_FRESH_RUN_ROOT_REQUIRED", again.stderr)

    def test_invalid_budgets_never_start_source(self):
        with tempfile.TemporaryDirectory() as scratch:
            d = Path(scratch) / "bad"
            out = invoke(d, "--episodes", "26")
            self.assertNotEqual(out.returncode, 0)
            self.assertFalse(d.exists())


if __name__ == "__main__":
    unittest.main()
