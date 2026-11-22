"""NKR-18 mechanical checks. Does not run the primary multi-scale screen."""
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import struct
import unittest

from yggdrasil.native_relation_memory import NativeRelationMemory, NativeRelationReadout
from yggdrasil.public_causal_cells import PublicCausalCells


def predict_signature(signature, x, action):
    # Independent explicit form, not native feature-row implementation.
    return ((signature & 1) ^ ((x & ((signature >> 1) & 15)).bit_count() & 1)
            ^ (action & (((signature >> 5) & 1)
                         ^ ((x & (signature >> 6)).bit_count() & 1))))


def make(signature=731, contexts=(0, 1, 2, 4, 8)):
    bank = NativeRelationMemory()
    for x in contexts:
        for a in (0, 1):
            bank.observe_public(0, x, a, predict_signature(signature, x, a),
                                f"mechanics:{x}:{a}")
    return bank


def packed(doc):
    raw = json.dumps(doc, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    return raw, hashlib.sha256(raw).hexdigest()


class CompactKnowledgeTests(unittest.TestCase):
    def test_all_1024_native_affine_signatures_full_cold_parity(self):
        # Exhaustive coefficient-space unit check, not new source science.
        for signature in range(1024):
            bank = make(signature)
            out = bank.compact_inference()
            cold = NativeRelationReadout(out.checkpoint(), out.checkpoint_sha256)
            for x in range(16):
                for a in (0, 1):
                    self.assertEqual(cold.predict(0, x, a), predict_signature(signature, x, a))
            self.assertEqual(out.training_checkpoint_sha256,
                             hashlib.sha256(bank.checkpoint()).hexdigest())

    def test_partial_support_abstains_without_observed_record_lookup(self):
        for contexts in ((), (0,), (0, 1), (0, 1, 2, 4)):
            bank = make(contexts=contexts)
            out = bank.compact_inference()
            for x in range(16):
                for a in (0, 1):
                    self.assertEqual(out.predict(0, x, a), bank.predict(0, x, a))
            doc = json.loads(out.checkpoint())
            self.assertEqual(set(doc), {"schema", "training_checkpoint_sha256",
                                      "support_rows", "weights_float32_le",
                                      "accepted_native", "scientific_pass"})
            for absent in ("_events", "_exceptions", "observe_public", "restore"):
                self.assertFalse(hasattr(out, absent))
            self.assertNotIn("mechanics:", out.checkpoint().decode())

    def test_exception_export_rejects_atomically(self):
        bank = make()
        bank.observe_public_verified(0, 3, 0, 1 - bank.predict(0, 3, 0), "public-exception")
        before = bank.checkpoint()
        with self.assertRaisesRegex(ValueError, "CANNOT_DROP_VERIFIED_EXCEPTIONS"):
            bank.compact_inference()
        self.assertEqual(bank.checkpoint(), before)

    def test_bad_byte_pin_size_schema_and_types(self):
        out = make().compact_inference()
        raw, pin = out.checkpoint(), out.checkpoint_sha256
        for data, digest in ((raw, "0" * 64), (raw[:-1], pin), (bytearray(raw), pin),
                             (b"x" * 16385, pin), (b"{}", hashlib.sha256(b"{}").hexdigest())):
            with self.subTest(data_type=type(data), length=len(data)):
                with self.assertRaises(ValueError):
                    NativeRelationReadout(data, digest)
        edits = [
            ("accepted_native", True), ("scientific_pass", True),
            ("training_checkpoint_sha256", "x" * 64),
            ("support_rows", []), ("weights_float32_le", []),
        ]
        for field, value in edits:
            doc = json.loads(raw)
            doc[field] = value
            with self.assertRaises(ValueError):
                NativeRelationReadout(*packed(doc))
        for rows in ([True], [1024], [1, 1], [1, 2], [0], [-1]):
            doc = json.loads(raw)
            doc["support_rows"][0] = rows
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                NativeRelationReadout(*packed(doc))
        for coefficients in ("f" * 80, "0" * 79, " " * 80,
                             struct.pack("<10f", -0.0, *([0.0] * 9)).hex(),
                             struct.pack("<10f", 2.0, *([0.0] * 9)).hex()):
            doc = json.loads(raw)
            doc["weights_float32_le"][0] = coefficients
            with self.assertRaises(ValueError):
                NativeRelationReadout(*packed(doc))

    def test_strict_native_addresses_and_queries(self):
        out = make().compact_inference()
        for addr, x, a, retained in ((7, 0, 0, False), (9, 0, 0, True),
                                    (0, True, 0, False), (0, 16, 0, False),
                                    (0, 0, True, False), (0, 0, 0, 1)):
            with self.assertRaises(ValueError):
                out.predict(addr, x, a, retained=retained)
        self.assertIsNone(out.predict(8, 15, 1, retained=True))

    def test_weight_lesion_changes_predictions_support_unchanged(self):
        out = make().compact_inference()
        doc = json.loads(out.checkpoint())
        doc["weights_float32_le"] = ["0" * 80] * 16
        ablated = NativeRelationReadout(*packed(doc))
        self.assertTrue(any(out.predict(0, x, a) != ablated.predict(0, x, a)
                            for x in range(16) for a in (0, 1)))
        self.assertEqual(json.loads(ablated.checkpoint())["support_rows"], doc["support_rows"])

    def test_controls_fit_training_and_process_has_no_labels(self):
        path = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/NKR-18/experiment.py"
        spec = importlib.util.spec_from_file_location("nkr18_unit_helpers", path)
        exp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exp)
        # Complete known XOR unit fixture: fully grown CART must fit zero-gain splits.
        rows = [(f"unit:{x}:{a}", x, a, ((x & 3).bit_count() & 1) ^ a)
                for x in range(16) for a in (0, 1)]
        tree = exp.fit_cart(rows)
        for _, x, a, y in rows:
            self.assertEqual(exp.predict_cart(tree, x, a), y)
            self.assertEqual(exp.nearest(rows, x, a), y)
        out = make().compact_inference()
        queries = [(0, x, a) for x in range(16) for a in (0, 1)]
        self.assertEqual(exp.isolated_inference(out, queries),
                         [out.predict(0, x, a) for _, x, a in queries])
        source = inspect.getsource(NativeRelationReadout.predict)
        for forbidden in ("_events", "_exceptions", "open(", "source", "environment"):
            self.assertNotIn(forbidden, source)

    def test_existing_trainer_bytes_legacy_and_cross_slot_nonmutation(self):
        bank = make()
        before = bank.checkpoint()
        legacy = PublicCausalCells().snapshot()
        out = bank.compact_inference()
        self.assertEqual(bank.checkpoint(), before)
        for x in (0, 1, 2, 4, 8):
            for a in (0, 1):
                bank.observe_public(8, x, a, 1 - predict_signature(731, x, a),
                                    f"later:{x}:{a}", retained=True)
        later = bank.compact_inference()
        for x in range(16):
            for a in (0, 1):
                self.assertEqual(out.predict(0, x, a), later.predict(0, x, a))
        self.assertEqual(PublicCausalCells().snapshot(), legacy)
        self.assertEqual(len(legacy), 164)


if __name__ == "__main__":
    unittest.main()
