"""WSP52 source/audit tests. SELFTEST only: no DEV/PRIMARY world is sampled."""
import unittest
from source import build_world, ENCODINGS, identifiability_warning, _apply


class SourceTests(unittest.TestCase):
    def test_reproducible_and_source_counts(self):
        for encoding in ENCODINGS:
            a = build_world("SELFTEST", 9001, encoding)
            b = build_world("SELFTEST", 9001, encoding)
            self.assertEqual(a, b)
            a.audit()
            receipt = a.source_receipt()
            self.assertEqual((receipt["train_a_count"], receipt["train_b_count"]), (36, 6))
            self.assertEqual((receipt["heldout_a_count"], receipt["heldout_b_count"]), (60, 90))
            self.assertEqual(receipt["exposed_actions"], 42)
            self.assertEqual(receipt["exposed_resets"], 0)

    def test_encoding_and_seed_separation(self):
        worlds = [build_world("SELFTEST", seed, encoding)
                  for seed in (9001, 9002) for encoding in ENCODINGS]
        self.assertEqual(len({w.source_receipt()["train_a_sha256"] for w in worlds}), 6)
        for world in worlds:
            self.assertNotEqual(world._orders[0], world._orders[1])

    def test_no_learner_labels_in_observations(self):
        world = build_world("SELFTEST", 9002, "rotated")
        for row in world.phase_a + world.phase_b:
            self.assertEqual(set(vars(row)), {"before", "acoustic_bits", "after", "action_cost", "reset_cost"})
            self.assertEqual(len(row.before), 8)
            self.assertTrue(set(row.acoustic_bits) <= {"0", "1"})

    def test_protected_cohort_fails_closed(self):
        with self.assertRaises(PermissionError):
            build_world("PRIMARY", 1201, "identity")
        with self.assertRaises(ValueError):
            build_world("DEV", 9001, "identity")
        with self.assertRaises(ValueError):
            build_world("SELFTEST", 1201, "identity")

    def test_observational_nonidentifiability(self):
        before = (0, 0, 0, 0, 0, 0, 0, 0)
        for entity in range(8):
            self.assertEqual(_apply(before, (entity, 0, 1)),
                             _apply(before, (entity, 1, 0)))
            self.assertEqual(_apply(before, (entity, 1, 2)),
                             _apply(before, (entity, 2, 1)))
        self.assertIn("not uniquely identifiable", identifiability_warning())


if __name__ == "__main__":
    unittest.main()
