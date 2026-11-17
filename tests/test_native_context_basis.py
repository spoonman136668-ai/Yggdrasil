"""Source-free native representation, admission and persistence checks."""
import json
import unittest

from yggdrasil.native_context_basis import NativeContextBasis, canonical, digest
from yggdrasil.public_causal_cells import PublicCausalCells


def fit(model, rows, degree, address=0, retained=False):
    return model.stage_fit(address, rows, digest(canonical(rows)),
                           max_degree=degree, retained=retained)


class NativeContextBasisTests(unittest.TestCase):
    def test_affine_weights_predict_unseen_combinations(self):
        model = NativeContextBasis(3)
        rows = [[x & 7, x >> 3, (x & 1) ^ (x >> 3)] for x in (0, 1, 2, 4, 8)]
        learned = fit(model, rows, 1)
        self.assertEqual(learned.profile_info(0)["rank"], 5)
        for x in range(16):
            self.assertEqual(learned.predict(0, x & 7, x >> 3), (x & 1) ^ (x >> 3))
        self.assertIsNone(model.predict(0, 0, 0))

    def test_composed_pairwise_weights_can_express_three_property_majority(self):
        model = NativeContextBasis(3)
        rows = [[x & 7, x >> 3, int((x & 7).bit_count() >= 2)] for x in range(15)]
        learned = fit(model, rows, 2)
        self.assertEqual(learned.predict(0, 7, 1), 1)
        self.assertEqual(learned.profile_info(0)["feature_count"], 11)
        with self.assertRaisesRegex(ValueError, "MODEL_CLASS_INADEQUATE"):
            fit(model, rows, 1)

    def test_complete_basis_refuses_unidentified_unseen_input(self):
        model = NativeContextBasis(3)
        rows = [[x & 7, x >> 3, x.bit_count() & 1] for x in range(15)]
        learned = fit(model, rows, 4)
        self.assertIsNone(learned.predict(0, 7, 1))
        self.assertEqual(learned.predict(0, 6, 1), 1)

    def test_unknown_property_is_not_imputed_as_zero(self):
        rows = [[x & 7, x >> 3, (x & 1) ^ ((x >> 1) & 1)] for x in range(16)]
        learned = fit(NativeContextBasis(3), rows, 1)
        self.assertIsNone(learned.predict_partial(0, 0, 0, 0))
        self.assertEqual(learned.predict_partial(0, 1, 3, 0), 1)
        with self.assertRaises(ValueError):
            learned.predict_partial(0, 1, 0, 0)

    def test_new_retained_profile_does_not_erase_previous_weights(self):
        rows = [[x & 7, x >> 3, x & 1] for x in range(16)]
        old = fit(NativeContextBasis(3), rows, 2)
        frozen = old.checkpoint()
        new = fit(old, [[x & 7, x >> 3, x >> 3] for x in range(16)], 2, 2, True)
        self.assertEqual(old.checkpoint(), frozen)
        for x in range(16):
            self.assertEqual(old.predict(0, x & 7, x >> 3), new.predict(0, x & 7, x >> 3))
            self.assertEqual(new.predict(2, x & 7, x >> 3, retained=True), x >> 3)

    def test_cold_checkpoint_has_no_training_consequence_table(self):
        rows = [[x & 7, x >> 3, int((x & 7).bit_count() >= 2)] for x in range(16)]
        model = fit(NativeContextBasis(3), rows, 2)
        raw = model.checkpoint()
        cold = NativeContextBasis.restore(raw, digest(raw))
        self.assertEqual(cold.checkpoint(), raw)
        document = json.loads(raw)
        self.assertNotIn("events", document)
        self.assertNotIn("records", document["profiles"][0])
        for x in range(16):
            self.assertEqual(cold.predict(0, x & 7, x >> 3), model.predict(0, x & 7, x >> 3))

    def test_source_kind_pin_and_public_types_reject_without_mutation(self):
        model = NativeContextBasis(3)
        frozen = model.checkpoint()
        rows = [[0, 0, 0]]
        for kwargs in ({"source_kind": "historical_train_QPQ"},
                       {"source_mode": "original_source_first_use"}):
            with self.assertRaisesRegex(ValueError, "GROUNDING_OR_SOURCE_AUTHORITY"):
                model.stage_fit(0, rows, digest(canonical(rows)), **kwargs)
        with self.assertRaises(ValueError):
            model.stage_fit(0, rows, "0" * 64)
        for invalid in ([[True, 0, 0]], [[0, 0, 2]], [[8, 0, 0]]):
            with self.assertRaises(ValueError):
                fit(model, invalid, 2)
        self.assertEqual(model.checkpoint(), frozen)

    def test_repeated_input_is_not_new_identifying_evidence(self):
        model = fit(NativeContextBasis(3), [[0, 0, 1], [0, 0, 1]], 2)
        info = model.profile_info(0)
        self.assertEqual(info["source_records"], 2)
        self.assertEqual(info["unique_inputs"], 1)
        self.assertEqual(info["rank"], 1)
        frozen = model.checkpoint()
        with self.assertRaisesRegex(ValueError, "MODEL_INADEQUATE"):
            fit(model, [[0, 0, 0], [0, 0, 1]], 2)
        self.assertEqual(model.checkpoint(), frozen)

    def test_checkpoint_integrity_flags_and_support_are_verified(self):
        model = fit(NativeContextBasis(3), [[0, 0, 1]], 2)
        raw = model.checkpoint()
        with self.assertRaises(ValueError):
            NativeContextBasis.restore(raw, "0" * 64)
        for key in ("accepted_native", "scientific_pass"):
            doc = json.loads(raw); doc[key] = True
            altered = canonical(doc)
            with self.assertRaises(ValueError):
                NativeContextBasis.restore(altered, digest(altered))
        doc = json.loads(raw); doc["profiles"][0]["support_rows"] = ["0"]
        altered = canonical(doc)
        with self.assertRaises(ValueError):
            NativeContextBasis.restore(altered, digest(altered))

    def test_legacy_public_counter_checkpoint_stays_unchanged(self):
        legacy = PublicCausalCells(); legacy.observe(0, 1, 1)
        frozen = legacy.snapshot()
        fit(NativeContextBasis(), [[0, 0, 0], [1, 1, 1]], 3)
        self.assertEqual(legacy.snapshot(), frozen)
        for bits in (0, 11, True):
            with self.assertRaises(ValueError): NativeContextBasis(bits)


if __name__ == "__main__":
    unittest.main()
