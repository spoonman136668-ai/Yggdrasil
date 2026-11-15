"""FKP-02 source-only invariants; no protected first-use or model training."""
import importlib
import unittest

source = importlib.import_module("source")


class FKP02SourceTests(unittest.TestCase):
    def test_spec_and_fixed_shape(self):
        self.assertEqual(source.INPUT_BITS, 16)
        self.assertEqual(source.EFFECT_BITS, 4)
        self.assertEqual(source.PUBLIC_PROBES, 64)
        self.assertEqual(source.PAID_PROBES, 16)
        self.assertEqual(source.HELD_PROBES, 128)
        self.assertEqual(len(source.SPEC_SHA256), 64)

    def test_disjoint_cohorts(self):
        self.assertEqual(source.cohort(10000), "foundation")
        self.assertEqual(source.cohort(10255), "foundation")
        self.assertEqual(source.cohort(200), "development")
        self.assertEqual(source.cohort(215), "development")
        self.assertEqual(source.cohort(1000), "primary")
        self.assertEqual(source.cohort(1063), "primary")
        self.assertEqual(source.cohort(2000), "negative")
        self.assertEqual(source.cohort(3015), "retention")
        for invalid in (199, 216, 999, 1064, 9999, 10256, True):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    source.cohort(invalid)

    def test_public_source_actions_and_held_are_distinct(self):
        for seed in (200, 201, 10000, 10001):
            actions, held = source.public_actions(seed)
            self.assertEqual(len(set(actions)), 64)
            self.assertEqual(len(set(held)), 128)
            self.assertFalse(set(actions) & set(held))
            self.assertTrue(all(0 <= x < 65536 for x in actions + held))

    def test_64_source_steps_deterministic(self):
        for seed in (200, 201, 10000):
            one = source.PublicCausalWorld(seed)
            two = source.PublicCausalWorld(seed)
            p = one.public_view()
            self.assertEqual(p, two.public_view())
            self.assertEqual(p.__dataclass_fields__.keys(),
                             {"input_bits", "effect_bits", "allowed_actions",
                              "held_inputs"})
            self.assertEqual([one.observe(x) for x in p.allowed_actions],
                             [two.observe(x) for x in p.allowed_actions])

    def test_protected_worlds_reject_absent_key_before_laws(self):
        for seed in (1000, 1063, 2000, 2015, 3000, 3015):
            with self.subTest(seed=seed):
                with self.assertRaises(PermissionError):
                    source.PublicCausalWorld(seed)
                with self.assertRaises(PermissionError):
                    source.PublicCausalWorld(seed, protected_key=b"short")

    def test_dev_and_foundation_reject_protected_key(self):
        for seed in (200, 10000):
            with self.assertRaises(ValueError):
                source.PublicCausalWorld(seed, protected_key=b"z" * 32)

    def test_genuine_experience_order_and_replay_rejection(self):
        w = source.PublicCausalWorld(200)
        actions = w.public_view().allowed_actions
        with self.assertRaises(PermissionError):
            w.observe(actions[1])
        self.assertIsInstance(w.observe(actions[0]), int)
        with self.assertRaises(PermissionError):
            w.observe(actions[0])
        self.assertIsInstance(w.observe(actions[1]), int)

    def test_inputs_outside_source_public_actions_rejected(self):
        w = source.PublicCausalWorld(200)
        actions = set(w.public_view().allowed_actions)
        missing = next(x for x in range(65536) if x not in actions)
        with self.assertRaises(ValueError):
            w.observe(missing)
        for bad in (-1, 65536, 2.4, True):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    w.observe(bad)

    def test_private_dev_eval_never_primary(self):
        w = source.PublicCausalWorld(202)
        self.assertIn(w.development_only_eval(451), range(16))
        with self.assertRaises(ValueError):
            w.development_only_eval(-1)
        with self.assertRaises(PermissionError):
            source.PublicCausalWorld(10000).development_only_eval(451)

    def test_source_only_preflight(self):
        result = source.source_preflight()
        self.assertTrue(result["dev_only"])
        self.assertTrue(result["protected_data_unopened"])
        self.assertEqual(len(result["manifests"]), 6)
        self.assertTrue(all(x["source_steps"] == 64
                            for x in result["manifests"]))


if __name__ == "__main__":
    unittest.main()
