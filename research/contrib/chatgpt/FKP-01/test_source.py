"""FKP-01 source-only tests: public development fixtures only, no protected science."""

import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "fkp01_source", Path(__file__).with_name("source.py")
)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class FKP01SourceTests(unittest.TestCase):
    def test_source_spec_stable(self):
        self.assertEqual(source.STATES, 128)
        self.assertEqual(source.PRIMITIVES, 16)
        self.assertEqual(source.ACTIONS, 16)
        self.assertEqual(len(source.SPEC_SHA256), 64)

    def test_development_source_deterministic(self):
        w1 = source.PublicCausalWorld(200)
        w2 = source.PublicCausalWorld(200)
        self.assertEqual(w1.public_view(), w2.public_view())
        self.assertEqual(w1.public_action_experiences(),
                         w2.public_action_experiences())

    def test_public_data_cannot_expose_private_operator(self):
        w = source.PublicCausalWorld(201)
        view = w.public_view()
        self.assertEqual(view._fields, ("relation_maps", "intervention_inputs"))
        self.assertFalse(hasattr(view, "private_law"))
        self.assertFalse(hasattr(view, "seed"))
        self.assertEqual(len(view.relation_maps) * source.STATES, 2048)

    def test_heldout_excludes_every_paid_action(self):
        w = source.PublicCausalWorld(202)
        train = set(w.public_view().intervention_inputs)
        held = set(w.previously_unobserved_inputs())
        self.assertEqual(len(train), 16)
        self.assertEqual(len(held), 112)
        self.assertFalse(train & held)
        self.assertEqual(train | held, set(range(128)))

    def test_original_development_preflight(self):
        result = source.development_source_audit()
        self.assertTrue(result["dev_only"])
        self.assertFalse(result["protected_labels_opened"])
        self.assertEqual(len(result["fixtures"]), 4)
        self.assertTrue(all(item["paid_action_count"] == 16
                            for item in result["fixtures"]))

    def test_distinct_sources_and_single_action_effect(self):
        a = source.PublicCausalWorld(200)
        b = source.PublicCausalWorld(203)
        self.assertNotEqual(a.public_view().relation_maps,
                            b.public_view().relation_maps)
        self.assertTrue(all(0 <= y < 128 for _, y in
                            a.public_action_experiences()))

    def test_no_unregistered_seed(self):
        with self.assertRaises(ValueError):
            source.PublicCausalWorld(999)
        with self.assertRaises(ValueError):
            source.PublicCausalWorld(True)
        with self.assertRaises(ValueError):
            source.PublicCausalWorld(99)

    def test_protected_worlds_require_private_owner_key(self):
        # All these fail BEFORE sampling source-private law or consequences.
        for seed in (1000, 1063, 2000, 2015, 3000, 3015):
            with self.subTest(seed=seed):
                with self.assertRaises(PermissionError):
                    source.PublicCausalWorld(seed)
                with self.assertRaises(PermissionError):
                    source.PublicCausalWorld(seed, protected_key=b"short")

    def test_development_world_rejects_owner_key(self):
        with self.assertRaises(ValueError):
            source.PublicCausalWorld(200, protected_key=b"0" * 32)

    def test_invalid_action_rejected(self):
        w = source.PublicCausalWorld(200)
        for bad in (-1, 128, 1.2, True):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    w.observe(bad)


if __name__ == "__main__":
    unittest.main()
