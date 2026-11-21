"""Source-free PCER-01 contract tests; no Yggdrasil learning or source action."""
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "research/contrib/chatgpt/PCER-01/pcer01.py"
SPEC = importlib.util.spec_from_file_location("pcer01_candidate", MODULE)
pcer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pcer)


def fixture():
    rows = []
    for i in range(96):
        ident = sha256(f"fixture-pcer-{i:03}".encode()).hexdigest()
        context = (i // 5) % 2
        action = i % 2
        outcome = (i // 3) % 2
        row = {"s1": context, "x1": action, "s2": outcome,
               "x2": (i // 2) % 2, "y": (i // 7) % 2}
        rows.append({"id": ident, "origin": 0, "phase": i // 32,
                     "views": [[context, i % 3], [context, (i+1) % 3]],
                     "row": row, "prediction": {"native": (i * 17113) % 1_000_001}})
    return rows


class Pcer01ContractTests(unittest.TestCase):
    def test_capacity_and_controls(self):
        rows = fixture()
        pcer.validate_trace(rows)
        for arm, expected in (("pcer", 10), ("uniform", 10),
                              ("error", 10), ("full", 50)):
            subset = pcer.pick(rows[:50], arm)
            self.assertEqual(len(subset), expected)
            self.assertEqual(subset, pcer.pick(rows[:50], arm))
            self.assertEqual(len({r["id"] for r in subset}), expected)
            self.assertTrue(all(r in rows[:50] for r in subset))

    def test_scoring_is_labeled_surrogate_not_native(self):
        manifest, report = pcer.analyze(fixture(), "a"*64, "b"*64)
        self.assertEqual(report["active_slot_reduction"], 0.8)
        self.assertEqual(report["arms"]["pcer"], 10)
        self.assertEqual(report["arms"]["full"], 50)
        self.assertEqual(report["scoring"]["return_held"]["rows"], 32)
        self.assertEqual(report["scoring"]["valid"]["rows"], 14)
        self.assertEqual(report["scientific_native_gain"], "UNVERIFIED")
        self.assertEqual(report["unfamiliar_family_transfer"], "UNVERIFIED")
        self.assertTrue(pcer.cold_verify(fixture(), "a"*64, "b"*64, manifest))

    def test_duplication_and_public_shape_fail_closed(self):
        r = fixture()
        r[1]["id"] = r[0]["id"]
        with self.assertRaisesRegex(ValueError, "IDENTITY_OR_DUPLICATE"):
            pcer.validate_trace(r)
        r = fixture()
        r[4]["row"]["s1"] ^= 1
        with self.assertRaisesRegex(ValueError, "CONTEXT_INCONSISTENT"):
            pcer.validate_trace(r)
        r = fixture()
        r[0]["prediction"]["native"] = -1
        with self.assertRaisesRegex(ValueError, "PREDICTION_RANGE"):
            pcer.validate_trace(r)
        r = fixture()
        r[64]["phase"] = 1
        with self.assertRaisesRegex(ValueError, "PHASE_ORDER"):
            pcer.validate_trace(r)

    def test_cold_index_tampering_detected(self):
        r = fixture()
        m, report = pcer.analyze(r, "a"*64, "b"*64)
        m["selected"] = m["selected"][1:] + [r[49]["id"]]
        with self.assertRaisesRegex(ValueError, "COLD_INDEX_DIVERGENCE"):
            pcer.cold_verify(r, "a"*64, "b"*64, m)
        self.assertEqual(report["original_source_mutated"], False)

    def test_no_held_label_in_selector(self):
        a, b = fixture(), fixture()
        for r in b[50:]:
            r["row"]["s2"] ^= 1
        self.assertEqual(
            [x["id"] for x in pcer.pick(a[:50], "pcer")],
            [x["id"] for x in pcer.pick(b[:50], "pcer")])

    def test_pinned_source_lossless_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            source, frozen = p / "source.json", p / "prereg.json"
            raw = pcer.canonical(fixture())
            source.write_bytes(raw)
            frozen.write_bytes(pcer.canonical({
                "experiment_id": "PCER-01",
                "inputs": [{"sha256": pcer.hex_digest(raw)}]}))
            m, result = p / "manifest.json", p / "result.json"
            output = pcer.run(source, frozen, m, result)
            self.assertEqual(pcer.hex_digest(source.read_bytes()), pcer.hex_digest(raw))
            self.assertTrue(pcer.cold_verify(json.loads(source.read_bytes()),
                pcer.hex_digest(raw), pcer.hex_digest(frozen.read_bytes()),
                json.loads(m.read_bytes())))
            self.assertEqual(output, json.loads(result.read_bytes()))
            with self.assertRaisesRegex(ValueError, "OUTPUT_EXISTS"):
                pcer.run(source, frozen, m, result)
            source.write_bytes(raw + b" ")
            with self.assertRaisesRegex(ValueError, "SOURCE_OR_PROTOCOL_PIN"):
                pcer.run(source, frozen, p / "other-manifest", p / "other-result")


if __name__ == "__main__":
    unittest.main()
