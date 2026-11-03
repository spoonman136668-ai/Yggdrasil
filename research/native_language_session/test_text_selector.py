"""Invented component inputs; no scientific language-accuracy claim."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from research.native_language_session.runtime import NativeSession, canonical, digest
from research.native_language_session.text_selector import NativeTextSelector

EXAMPLES = [{"input": "aaaa", "response": "amber"}, {"input": "zzzz", "response": "violet"}]


class NativeTextTests(unittest.TestCase):
    def test_native_learning_and_readonly_scores(self):
        model = NativeTextSelector.train(EXAMPLES)
        raw = model.checkpoint()
        scores = model.predict("aaaa")
        self.assertIn(scores["response"], model.responses)
        self.assertFalse(scores["novel_string_generation"])
        self.assertTrue(all(bank.sequence == 16 for bank in model.banks))
        for bank in model.banks:
            self.assertNotEqual(bank.native.checkpoint(), NativeSession().native.checkpoint())
        untrained = NativeTextSelector.train(EXAMPLES)
        untrained.banks = [NativeSession() for _ in untrained.responses]
        self.assertNotEqual(scores["native_scores"], untrained.predict("aaaa")["native_scores"])
        self.assertEqual(raw, model.checkpoint())

    def test_complete_state_and_fresh_process(self):
        model = NativeTextSelector.train(EXAMPLES)
        raw = model.checkpoint()
        restored = NativeTextSelector.restore(raw)
        self.assertEqual(raw, restored.checkpoint())
        self.assertEqual(model.predict("aaaa"), restored.predict("aaaa"))
        root = Path(__file__).resolve().parents[2]
        env = {k: v for k, v in os.environ.items() if k in ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE")}
        env["PYTHONPATH"] = str(root)
        req = [{"op": "restore", "checkpoint": json.loads(raw)}, {"op": "predict", "input": "aaaa"}, {"op": "checkpoint"}]
        result = subprocess.run([sys.executable, "-B", "-m", "research.native_language_session.text_selector"],
            input=b"\n".join(canonical(x) for x in req) + b"\n", cwd=root, env=env,
            capture_output=True, timeout=20, check=True)
        rows = [json.loads(x) for x in result.stdout.splitlines()]
        self.assertTrue(all(x["ok"] for x in rows), rows)
        self.assertEqual(rows[1]["result"], model.predict("aaaa"))
        self.assertEqual(rows[2]["result"]["checkpoint"], json.loads(raw))

    def test_invalid_and_corrupt_inputs(self):
        for examples in ([], [{"input": "x", "response": "a"}] * 2,
                         [dict(EXAMPLES[0], input="x" * 257), EXAMPLES[1]]):
            with self.assertRaises(ValueError):
                NativeTextSelector.train(examples)
        model = NativeTextSelector.train(EXAMPLES)
        before = model.checkpoint()
        with self.assertRaises(ValueError):
            model.predict("")
        self.assertEqual(before, model.checkpoint())
        doc = json.loads(before)
        doc["payload"]["source_blob"] = "foreign"
        doc["sha256"] = digest(doc["payload"])
        with self.assertRaises(ValueError):
            NativeTextSelector.restore(canonical(doc))
        with self.assertRaises(ValueError):
            NativeTextSelector.restore(before + b"{}")


if __name__ == "__main__":
    unittest.main()
