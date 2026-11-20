"""DWSA-02 negative controls: weight-only, trained archived donor, no model import."""
from __future__ import annotations

import hashlib
import math
import os
from pathlib import Path
import struct
import tempfile
import unittest

from dwsa02 import (
    BODY_BYTES, DIMS, MAGIC, NATIVE_BYTES, PARAMETER_FLOATS,
    ZIP_SHA, algebraic_route, compile_routes, gauge, read_archive,
    restore, run_dev, sha, validate_head,
)


class DWSA02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("DWSA02_ARCHIVE_ZIP")
        if not value:
            raise unittest.SkipTest("requires explicit existing archived ZIP path")
        cls.path = Path(value)
        cls.state, cls.heads = read_archive(cls.path)

    def test_custody_and_four_real_training_heads(self):
        self.assertEqual(sha(self.path.read_bytes()), ZIP_SHA)
        self.assertEqual(tuple(len(h["encoder"][0]) for h in self.heads), DIMS)
        self.assertEqual(tuple(h["steps"] for h in self.heads), (2109,)*4)

    def test_exact_capacity_cold_roundtrip_and_repeat(self):
        raw = compile_routes(self.heads)
        self.assertEqual(len(raw), NATIVE_BYTES)
        self.assertEqual(raw, compile_routes(self.heads))
        self.assertEqual(len(restore(raw)), 4)
        self.assertEqual(sum(len(row) for row in restore(raw)), 200)
        self.assertEqual(PARAMETER_FLOATS*8, 6976)
        for _ in range(3):
            self.assertEqual(restore(bytes(raw)), restore(raw))

    def test_gauge_permutations_and_hidden_sign_flips(self):
        for i, head in enumerate(self.heads):
            target = algebraic_route(head)
            for seed in (101, 202, 303):
                candidate = gauge(head, seed)
                self.assertEqual(candidate["steps"], 2109)
                self.assertLessEqual(max(abs(a-b) for a,b in
                                    zip(target, algebraic_route(candidate))), 1e-12,
                                     (i, seed))

    def test_quantization_is_bounded_and_no_better_than_exact_oracle(self):
        raw = compile_routes(self.heads)
        got = restore(raw)
        scales = struct.unpack(">4d", raw[9:41])
        for i, head in enumerate(self.heads):
            for actual, reference in zip(got[i], algebraic_route(head)):
                self.assertLessEqual(abs(actual-reference), scales[i]/2 + 1e-12)
        self.assertEqual(restore(raw), restore(raw))

    def test_reject_bad_checkpoint_checksum_and_length(self):
        raw = compile_routes(self.heads)
        corrupt = bytearray(raw)
        corrupt[41] ^= 1
        with self.assertRaises(ValueError):
            restore(bytes(corrupt))
        with self.assertRaises(ValueError):
            restore(raw[:-1])
        with self.assertRaises(ValueError):
            restore(b"")

    def test_reject_resigned_padding_and_nonfinite_scale(self):
        raw = compile_routes(self.heads)
        for damage in ("padding", "scale", "magic", "dimension"):
            blob = bytearray(raw[:BODY_BYTES])
            if damage == "padding":
                blob[241] = 1
            elif damage == "scale":
                struct.pack_into(">d", blob, 9, float("nan"))
            elif damage == "magic":
                blob[0] = ord("X")
            else:
                blob[5] = 9
            joined = bytes(blob) + hashlib.sha256(blob).digest()
            with self.subTest(damage=damage), self.assertRaises(ValueError):
                restore(joined)

    def test_reject_invalid_head_steps_shapes_and_numbers(self):
        source = self.heads[0]
        variations = []
        for k,v in (("steps",0), ("kind","reward"),
                    ("encoder",source["encoder"][:-1]),
                    ("encoder_bias",source["encoder_bias"][:-1]),
                    ("predictor",source["predictor"][:-1]),
                    ("predictor_bias",source["predictor_bias"][:-1])):
            variations.append({**source, k:v})
        bad_float = {**source, "encoder": [list(v) for v in source["encoder"]]}
        bad_float["encoder"][0][0] = float("nan")
        variations.append(bad_float)
        for candidate in variations:
            with self.subTest(keys=tuple(candidate)), self.assertRaises(ValueError):
                validate_head(candidate, 3, "transition")

    def test_archive_tamper_rejected_before_parsing(self):
        raw = bytearray(self.path.read_bytes())
        raw[0] ^= 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.zip"
            path.write_bytes(raw)
            with self.assertRaises(ValueError):
                read_archive(path)

    def test_precommitted_full_mechanical_diagnostic(self):
        report = run_dev(self.path)
        self.assertEqual(report["donor_forward_calls"], 0)
        self.assertEqual(report["donor_training_steps_executed"], 0)
        self.assertEqual(report["gauge_cases"], 12)
        self.assertTrue(report["quantization_bound_pass"])
        self.assertTrue(report["ordinary_uniform_int8_product_control_ties"])
        self.assertEqual(report["engineering"], "LOCAL_STATIC_DEV_PASS")
        self.assertEqual(report["scientific"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
