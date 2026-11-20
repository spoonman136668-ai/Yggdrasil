"""Source-free negative controls for receipt custody and runtime qualification."""
import json
import tempfile
import unittest
from pathlib import Path
from receipt_guard import commit_world, read_verified, budget_gate

SHA = "a" * 64


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "worlds.jsonl"

    def put(self, world="pilot:01"):
        return commit_world(self.path, source_sha256=SHA, world_id=world,
                            elapsed_ms=100, result={"score": 0.2, "complete": True})

    def test_reproducible_chain(self):
        first = self.put()
        second = self.put("pilot:02")
        entries = read_verified(self.path, SHA)
        self.assertEqual((entries[0]["entry_sha256"], entries[1]["entry_sha256"]), (first, second))
        self.assertEqual(entries[1]["prev_sha256"], first)

    def test_duplicate_rejected_without_change(self):
        self.put()
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "no replay"):
            self.put()
        self.assertEqual(self.path.read_bytes(), before)

    def test_source_change_rejected(self):
        self.put()
        with self.assertRaisesRegex(ValueError, "source mismatch"):
            read_verified(self.path, "b" * 64)

    def test_mutated_result_rejected(self):
        self.put()
        row = json.loads(self.path.read_text())
        row["result"]["score"] = 0.01
        self.path.write_text(json.dumps(row) + "\n")
        with self.assertRaisesRegex(ValueError, "broken hash"):
            read_verified(self.path, SHA)

    def test_existing_lock_fails_closed(self):
        self.path.with_name("worlds.jsonl.lock").write_text("crash")
        with self.assertRaises(FileExistsError):
            self.put()
        self.assertFalse(self.path.exists())

    def test_partial_temp_does_not_count(self):
        self.path.with_name("worlds.jsonl.tmp").write_text("partial")
        self.assertEqual(read_verified(self.path, SHA), [])
        with self.assertRaises(FileExistsError):
            self.put()

    def test_bad_result_rejected_before_file(self):
        with self.assertRaises(ValueError):
            commit_world(self.path, source_sha256=SHA, world_id="w", elapsed_ms=1,
                         result={"nan": float("nan")})
        self.assertFalse(self.path.exists())

    def test_missing_complete_rejected(self):
        with self.assertRaisesRegex(ValueError, "only complete"):
            commit_world(self.path, source_sha256=SHA, world_id="w", elapsed_ms=1, result={"score": 0.2})
        self.assertFalse(self.path.exists())

    def test_empty_preflight_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid budget"):
            budget_gate({}, 4, 100)

    def test_valid_budget(self):
        result = budget_gate({"A": [1, 2, 2], "B": [3, 4, 5]}, 4, 45)
        self.assertTrue(result["qualified"])
        self.assertEqual(result["projected_seconds"], 42)

    def test_excess_budget_refused(self):
        self.assertFalse(budget_gate({"A": [5, 6, 7]}, 4, 40)["qualified"])

    def test_insufficient_preflight_refused(self):
        with self.assertRaisesRegex(ValueError, "unqualified timing"):
            budget_gate({"A": [1, 2]}, 4, 100)


if __name__ == "__main__":
    unittest.main()
