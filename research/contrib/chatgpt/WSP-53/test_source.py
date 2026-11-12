"""WSP53 source structural checks; only SELFTEST fixture preparation.

No DEV/PRIMARY generator call, learner fitting, experimental scoring, or
protected scientific first use occurs in this file.
"""
from dataclasses import fields, replace
from hashlib import sha256
import unittest

from source import (A_COUNT, B_COUNT, ENCODINGS, FAMILIES, Observation, _apply,
                    build_world)


class WSP53SourceTests(unittest.TestCase):
    def test_all_fixture_sources_are_deterministic_and_budgeted(self):
        for family in FAMILIES:
            receipts = set()
            for seed in (9901, 9902):
                for encoding in ENCODINGS:
                    with self.subTest(family=family, seed=seed, encoding=encoding):
                        world = build_world(family, "SELFTEST", seed, encoding)
                        copy = build_world(family, "SELFTEST", seed, encoding)
                        self.assertEqual(world, copy)
                        self.assertEqual(world.source_receipt(), copy.source_receipt())
                        world.audit()
                        receipt = world.source_receipt()
                        self.assertEqual(receipt["phase_a"][0], A_COUNT)
                        self.assertEqual(receipt["phase_b"][0], B_COUNT)
                        self.assertEqual(receipt["heldout_a"][0], 48)
                        self.assertEqual(receipt["heldout_b"][0], 84)
                        self.assertEqual(receipt["charged_actions"], 60)
                        self.assertEqual(receipt["charged_resets"], 0)
                        receipts.add(receipt["phase_a"][1])
            self.assertEqual(len(receipts), 6)

    def test_no_semantic_labels_in_observation_interface(self):
        public = {x.name for x in fields(Observation)}
        self.assertEqual(public, {"before", "after", "acoustic_bits",
                                  "action_cost", "reset_cost"})
        for family in FAMILIES:
            world = build_world(family, "SELFTEST", 9901, "permuted")
            for row in world.phase_a + world.phase_b:
                self.assertEqual(set(vars(row)), public)
                self.assertTrue(set(row.acoustic_bits).issubset({"0", "1"}))
                self.assertGreaterEqual(len(row.acoustic_bits), 12)
                self.assertLessEqual(len(row.acoustic_bits), 18)
                self.assertEqual(len(row.before), 16 if
                                 family == "anchored_effect" else 8)
                self.assertEqual(len(row.after), len(row.before))

    def test_independent_anchor_distinguishes_verb_effects(self):
        state = (0,) * 16
        for entity in range(8):
            for destination in range(4):
                outcomes = [_apply("anchored_effect", state, (entity, destination, verb))
                            for verb in range(3)]
                self.assertEqual(len(set(outcomes)), 3)
                # Location-only consequences are not sufficient to attribute
                # both semantic causes; independent orientation is observable.
                self.assertEqual(set(x[8 + entity] for x in outcomes), {0, 1, 2})

    def test_swapping_noncommuting_operators_is_falsifiable(self):
        for seed in (9901, 9902):
            world = build_world("noncommuting_order", "SELFTEST", seed, "identity")
            pairs = world.order_counterworld_audit()
            self.assertGreater(pairs["eligible_pairs"], 0)
            self.assertGreaterEqual(4 * pairs["distinguishable_pairs"],
                                    pairs["eligible_pairs"])
            # Concrete noncommuting causal counterexample independent of codebook.
            self.assertNotEqual(_apply("noncommuting_order", (0,) * 8, (0, 0, 2)),
                                _apply("noncommuting_order", (0,) * 8, (0, 2, 0)))

    def test_unknown_or_protected_source_fails_closed(self):
        for family in FAMILIES:
            with self.assertRaises(PermissionError):
                build_world(family, "PRIMARY", 5101, "identity")
            with self.assertRaises(ValueError):
                build_world(family, "DEV", 9901, "identity")
            with self.assertRaises(ValueError):
                build_world(family, "SELFTEST", True, "identity")
            with self.assertRaises(ValueError):
                build_world(family, "SELFTEST", 9901, "debug")
            with self.assertRaises(ValueError):
                build_world("unknown", "SELFTEST", 9901, "identity")
            with self.assertRaises(ValueError):
                build_world(family, "unregistered", 9901, "identity")

    def test_audit_catches_causal_or_action_receipt_tamper(self):
        for family in FAMILIES:
            world = build_world(family, "SELFTEST", 9902, "rotated")
            event = world.phase_a[0]
            corrupted = replace(event, action_cost=0)
            with self.assertRaises(AssertionError):
                replace(world, phase_a=(corrupted,) + world.phase_a[1:]).audit()
            broken = replace(event, after=event.before)
            if event.after != event.before:
                with self.assertRaises(AssertionError):
                    replace(world, phase_a=(broken,) + world.phase_a[1:]).audit()


if __name__ == "__main__":
    unittest.main()
