"""Negative controls and fixed-footprint checks for DWSA-01."""
from __future__ import annotations

import hashlib
import unittest

from dwsa import (
    CHECKPOINT_BYTES, INPUT_BITS, SEEDS, SOURCE_BYTES,
    NativeRouter, compile_weight_only, decision, gauge_variant,
    oracle_scores, run_frozen_development, shuffled_route_sham,
    synthetic_artifact,
)


class DWSA01Tests(unittest.TestCase):
    def test_exact_independent_spec_all_seeds(self) -> None:
        for seed in SEEDS:
            donor, laws = synthetic_artifact(seed)
            native = compile_weight_only(donor)
            with self.subTest(seed=seed):
                self.assertEqual(len(native.snapshot()), CHECKPOINT_BYTES)
                self.assertGreaterEqual(SOURCE_BYTES / CHECKPOINT_BYTES, 10)
                self.assertEqual(NativeRouter.restore(native.snapshot()).snapshot(),
                                 native.snapshot())
            for bits in range(1 << INPUT_BITS):
                expected = oracle_scores(laws, bits)
                self.assertEqual(native.score(bits), expected)
                self.assertEqual(native.choose(bits), decision(expected))

    def test_valid_symmetries_three_variants_each(self) -> None:
        for seed in SEEDS:
            donor, laws = synthetic_artifact(seed)
            for variant in (1, 2, 3):
                native = compile_weight_only(gauge_variant(donor, seed, variant))
                for bits in range(1 << INPUT_BITS):
                    self.assertEqual(native.score(bits), oracle_scores(laws, bits))

    def test_route_sham_is_not_causally_invariant(self) -> None:
        donor, laws = synthetic_artifact(SEEDS[0])
        sham = compile_weight_only(shuffled_route_sham(donor))
        disagreement = sum(
            sham.score(bits) != oracle_scores(laws, bits)
            for bits in range(1 << INPUT_BITS)
        )
        self.assertGreater(disagreement, 0)

    def test_invalid_donor_shapes_and_schema_rejected(self) -> None:
        donor, _ = synthetic_artifact(SEEDS[0])
        for invalid in (
            None,
            {},
            {"hidden": [], "bias": [], "readout": [[], []]},
            {**donor, "unknown": 1},
            {**donor, "hidden": donor["hidden"] + donor["hidden"][:5],
             "bias": donor["bias"] + donor["bias"][:5],
             "readout": [ch + ch[:5] for ch in donor["readout"]]},
            {**donor, "readout": [donor["readout"][0]]},
        ):
            with self.subTest(invalid=str(invalid)[:50]):
                with self.assertRaises(ValueError):
                    compile_weight_only(invalid)

    def test_unsupported_motifs_and_forged_bias_rejected(self) -> None:
        donor, _ = synthetic_artifact(SEEDS[0])
        mixed = {"hidden": [r[:] for r in donor["hidden"]],
                 "bias": donor["bias"][:],
                 "readout": [ch[:] for ch in donor["readout"]]}
        nonzero = next(i for i, v in enumerate(mixed["hidden"][0]) if v)
        mixed["hidden"][0][nonzero] *= 1.5
        with self.assertRaises(ValueError):
            compile_weight_only(mixed)

        donor2, _ = synthetic_artifact(SEEDS[0])
        donor2["bias"][0] += 1.0
        with self.assertRaises(ValueError):
            compile_weight_only(donor2)

        donor3, _ = synthetic_artifact(SEEDS[0])
        donor3["readout"][0][0] += 0.125
        with self.assertRaises(ValueError):
            compile_weight_only(donor3)

    def test_tamper_and_semantically_invalid_resigned_checkpoint_rejected(self) -> None:
        donor, _ = synthetic_artifact(SEEDS[0])
        original = compile_weight_only(donor).snapshot()
        corrupt = bytearray(original)
        corrupt[5] ^= 1
        with self.assertRaises(ValueError):
            NativeRouter.restore(bytes(corrupt))
        count_corrupt = bytearray(original[:-32])
        count_corrupt[4] = 17
        rehashed = bytes(count_corrupt) + hashlib.sha256(count_corrupt).digest()
        with self.assertRaises(ValueError):
            NativeRouter.restore(rehashed)
        padded = bytearray(original[:-32])
        padded[5 + 12 * 4] = 1
        rehashed_pad = bytes(padded) + hashlib.sha256(padded).digest()
        with self.assertRaises(ValueError):
            NativeRouter.restore(rehashed_pad)
        with self.assertRaises(ValueError):
            NativeRouter.restore(original[:-1])

    def test_inputs_fail_closed(self) -> None:
        donor, _ = synthetic_artifact(SEEDS[0])
        router = compile_weight_only(donor)
        for invalid in (-1, 1 << INPUT_BITS, True, 1.5, "1", None):
            with self.assertRaises(ValueError):
                router.score(invalid)

    def test_frozen_development_counts(self) -> None:
        result = run_frozen_development()
        self.assertEqual(result["tested_cases"], 3072)
        self.assertEqual(result["score_exact_cases"], 3072)
        self.assertEqual(result["choice_exact_cases"], 3072)
        self.assertEqual(result["cold_restores"], 3)
        self.assertEqual(result["donor_forward_calls"], 0)
        self.assertEqual(result["independent_exact_control_gap"], 0)


if __name__ == "__main__":
    unittest.main()
