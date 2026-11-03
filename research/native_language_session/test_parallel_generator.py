"""Engineering byte-field checks. Interventions are not learned transfer."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from research.native_language_session.parallel_generator import NativeParallelGenerator, canonical, decode, digest

EXAMPLES = [{"input": "aaaa", "response": "aA"}, {"input": "zzzz", "response": "bB"}]


class NativeGeneratorTests(unittest.TestCase):
    def test_variable_length_utf8_fields(self):
        examples = [{"input": "aaaa", "response": "é"}, {"input": "zzzz", "response": "A"}]
        m = NativeParallelGenerator.train(examples)
        self.assertEqual(m.length["kind"], "native")
        restored = NativeParallelGenerator.restore(m.checkpoint())
        for x in examples:
            result = restored.generate(x["input"])
            self.assertTrue(result["valid_output"])
            self.assertEqual(result["response"], x["response"])
            self.assertEqual(result["predicted_length"], len(x["response"].encode("utf-8")))

    def test_native_fields_fit_engineering_pairs_and_restore(self):
        m = NativeParallelGenerator.train(EXAMPLES)
        raw = m.checkpoint()
        self.assertNotIn(b'"responses"', raw)
        self.assertNotIn(b'"aA"', raw)
        self.assertTrue(any(x["kind"] == "native" for x in m.fields))
        for x in EXAMPLES:
            result = m.generate(x["input"])
            self.assertEqual(result["response"], x["response"])
            self.assertFalse(result["whole_response_bank"])
            self.assertTrue(result["seen_training_response"])
            self.assertFalse(result["language_proof"])
        self.assertEqual(raw, m.checkpoint())
        restored = NativeParallelGenerator.restore(raw)
        self.assertEqual(raw, restored.checkpoint())
        self.assertEqual(m.generate("aaaa"), restored.generate("aaaa"))

    def test_mechanical_intervention_is_not_learned_novelty(self):
        m = NativeParallelGenerator.train(EXAMPLES)
        m.fields[0] = {"kind": "constant", "value": 0}
        result = m.generate("aaaa")
        self.assertEqual(result["response"], "`A")
        self.assertFalse(result["seen_training_response"])
        # This deliberate field intervention demonstrates assembly only.
        self.assertFalse(result["language_proof"])
        for bit in range(8):
            m.fields[bit] = {"kind": "constant", "value": 1}
        bad = m.generate("aaaa")
        self.assertFalse(bad["valid_output"])
        self.assertIsNone(bad["response"])
        self.assertEqual(bad["raw_hex"], "ff41")

    def test_invalid_training_and_foreign_checkpoint(self):
        for examples in ([], [{"input": "x", "response": "same"}] * 2,
                         [dict(EXAMPLES[0], response="x" * 17), EXAMPLES[1]]):
            with self.assertRaises(ValueError):
                NativeParallelGenerator.train(examples)
        m = NativeParallelGenerator.train(EXAMPLES)
        doc = decode(m.checkpoint())
        doc["payload"]["selector_blob"] = "foreign"
        doc["sha256"] = digest(doc["payload"])
        with self.assertRaises(ValueError):
            NativeParallelGenerator.restore(canonical(doc))
        doc = decode(m.checkpoint())
        doc["payload"]["fields"][0] = {"kind": "constant", "value": 7}
        doc["sha256"] = digest(doc["payload"])
        with self.assertRaises(ValueError):
            NativeParallelGenerator.restore(canonical(doc))
        with self.assertRaises(ValueError):
            NativeParallelGenerator.restore(m.checkpoint() + b"{}")

    def test_fresh_process_checkpoint_and_generation_parity(self):
        m = NativeParallelGenerator.train(EXAMPLES)
        root = Path(__file__).resolve().parents[2]
        env = {k: v for k, v in os.environ.items() if k in ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE")}
        env["PYTHONPATH"] = str(root)
        req = [{"op": "restore", "checkpoint": decode(m.checkpoint())}, {"op": "generate", "input": "aaaa"}, {"op": "checkpoint"}]
        p = subprocess.run([sys.executable, "-B", "-m", "research.native_language_session.parallel_generator"],
            input=b"\n".join(canonical(x) for x in req) + b"\n", cwd=root, env=env, capture_output=True, timeout=30, check=True)
        rows = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertTrue(all(x["ok"] for x in rows), rows)
        self.assertEqual(rows[1]["result"], m.generate("aaaa"))
        self.assertEqual(rows[2]["result"]["checkpoint"], decode(m.checkpoint()))


if __name__ == "__main__":
    unittest.main()
