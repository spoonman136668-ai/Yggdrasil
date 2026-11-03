"""Engineering fixtures only: no language or scientific original evaluation."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from research.native_language_session.runtime import NativeSession, canonical, digest
from research.native.itd01.r7.native_cells import Colony


class NativeSessionTests(unittest.TestCase):
    def trained(self):
        s = NativeSession()
        for i in range(12):
            sensors = (i % 2 == 0, i % 3 == 0, i % 2 == 1, False)
            q = s.predict("A", sensors)
            s.feedback(q["query_id"], sensors[2], 2)
        return s

    def test_complete_native_state_roundtrip(self):
        s = self.trained()
        raw = s.checkpoint()
        self.assertNotEqual(s.native.checkpoint(), Colony().checkpoint())
        r = NativeSession.restore(raw)
        self.assertEqual(raw, r.checkpoint())
        self.assertEqual(s.native.checkpoint(), r.native.checkpoint())
        for sensors in ((True, False, True, False), (False, True, False, True)):
            self.assertEqual(s.native.predict("A", sensors), r.native.predict("A", sensors))

    def test_feedback_requires_exact_pending_selection_once(self):
        s = NativeSession()
        before = s.native.checkpoint()
        with self.assertRaises(ValueError):
            s.feedback("absent", True, 2)
        q = s.predict("A", (True, False, True, False))
        for key, delay, outcome in (("wrong", 2, True), (q["query_id"], 1, True),
                                    (q["query_id"], 2, 1)):
            with self.assertRaises(ValueError):
                s.feedback(key, outcome, delay)
            self.assertEqual(before, s.native.checkpoint())
        with self.assertRaises(ValueError):
            s.checkpoint()
        s.feedback(q["query_id"], True, 2)
        after = s.checkpoint()
        with self.assertRaises(ValueError):
            s.feedback(q["query_id"], True, 2)
        self.assertEqual(after, s.checkpoint())

    def test_corruption_foreign_source_and_nonfinite_denied(self):
        s = self.trained()
        value = json.loads(s.checkpoint())
        value["sha256"] = "bad"
        with self.assertRaises(ValueError):
            NativeSession.restore(canonical(value))
        value = json.loads(s.checkpoint())
        value["payload"]["source_blob"] = "a" * 40
        value["sha256"] = digest(value["payload"])
        with self.assertRaises(ValueError):
            NativeSession.restore(canonical(value))
        with self.assertRaises(ValueError):
            NativeSession.restore(b'{"payload":NaN,"sha256":""}')

    def test_resigned_inconsistent_native_counters_denied(self):
        value = json.loads(self.trained().checkpoint())
        native = value["payload"]["native"]
        native["payload"]["neighbor_messages"] += 1
        native["sha256"] = digest(native["payload"])
        value["sha256"] = digest(value["payload"])
        with self.assertRaises(ValueError):
            NativeSession.restore(canonical(value))

    def test_real_fresh_process_restore(self):
        s = self.trained()
        expected = s.native.predict("A", (True, False, True, False))
        requests = [{"op": "restore", "checkpoint": json.loads(s.checkpoint())},
                    {"op": "predict", "context": "A", "sensors": [True, False, True, False]}]
        root = Path(__file__).resolve().parents[2]
        env = {k: v for k, v in os.environ.items() if k in (
            "PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE")}
        env["PYTHONPATH"] = str(root)
        result = subprocess.run([sys.executable, "-B", "-m", "research.native_language_session.runtime"],
            input=b"\n".join(canonical(x) for x in requests) + b"\n", cwd=root,
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=True)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertTrue(all(row["ok"] for row in rows))
        self.assertFalse(rows[-1]["language_capability"])
        self.assertEqual(rows[-1]["result"]["prediction"], expected)

    def test_cli_rejects_ambiguous_input_and_second_restore(self):
        root = Path(__file__).resolve().parents[2]
        checkpoint = json.loads(NativeSession().checkpoint())
        requests = [canonical({"op": "restore", "checkpoint": checkpoint}),
                    canonical({"op": "restore", "checkpoint": checkpoint}),
                    b'{"op":"checkpoint","op":"predict"}']
        p = subprocess.run([sys.executable, "-B", "-m", "research.native_language_session.runtime"],
            input=b"\n".join(requests) + b"\n", cwd=root,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=True)
        self.assertEqual([json.loads(x)["ok"] for x in p.stdout.splitlines()], [True, False, False])


if __name__ == "__main__":
    unittest.main()
