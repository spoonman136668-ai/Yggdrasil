"""Engineering-only, non-primary fixtures for Y2-CCE01.

Official synthetic benchmark seeds and heldout episodes are not used here.
Run: python -m unittest discover -s research/contrib/chatgpt/y2-cce01 -p test_cce01.py -v
"""

import hashlib
import json
import unittest

from cce01 import (CausalContractEcology, CountModel, MAX_EVENTS,
                   validate_event)


class CCE01Contracts(unittest.TestCase):
    @staticmethod
    def hand_fixture(positive=True):
        # Eight exhaustive public feature/action combinations, each repeated
        # in fixed order; this is not an official random/heldout science run.
        for _ in range(12):
            for x0 in (0, 1):
                for x1 in (0, 1):
                    for action in (0, 1):
                        yield (x0, x1), action, (action ^ x0 if positive else action)

    def test_initially_agnostic_without_oracle(self):
        cce = CausalContractEcology()
        for bits in ((0, 0), (0, 1), (1, 0), (1, 1)):
            for action in (0, 1):
                self.assertEqual(0.5, cce.predict(bits, action))
        self.assertIsNone(cce.selected_feature)
        self.assertEqual(0, cce.events)

    def test_hand_fixture_admits_only_relevant_feature(self):
        cce = CausalContractEcology()
        for bits, action, outcome in self.hand_fixture(positive=True):
            cce.observe(bits, action, outcome)
        self.assertEqual(0, cce.selected_feature)
        self.assertIsNotNone(cce.selection_step)
        self.assertGreaterEqual(cce.selection_step, 48)
        self.assertEqual(96, cce.events)
        self.assertGreater(cce.predict((1, 0), 0), 0.5)
        self.assertLess(cce.predict((0, 1), 0), 0.5)

    def test_negative_fixture_does_not_split(self):
        cce = CausalContractEcology()
        for bits, action, outcome in self.hand_fixture(positive=False):
            cce.observe(bits, action, outcome)
        self.assertIsNone(cce.selected_feature)
        self.assertGreater(cce.predict((1, 0), 1), 0.9)
        self.assertLess(cce.predict((0, 1), 0), 0.1)

    def test_checkpoint_roundtrip_and_tamper_detection(self):
        cce = CausalContractEcology()
        for event in self.hand_fixture():
            cce.observe(*event)
        packed = cce.snapshot()
        other = CausalContractEcology.restore(packed)
        self.assertEqual(cce.events, other.events)
        self.assertEqual(cce.selected_feature, other.selected_feature)
        self.assertEqual(packed, other.snapshot())
        for x0 in (0, 1):
            for x1 in (0, 1):
                for arm in (0, 1):
                    self.assertEqual(cce.predict((x0, x1), arm),
                                     other.predict((x0, x1), arm))
        damaged = bytearray(packed)
        damaged[-1] ^= 1
        with self.assertRaises(ValueError):
            CausalContractEcology.restore(bytes(damaged))

    def test_semantically_forged_checkpoint_rejected(self):
        cce = CausalContractEcology()
        cce.observe((0, 1), 0, 0)
        parts = cce.snapshot().split(b".", 2)
        state = json.loads(parts[2])
        state["events"] += 1
        body = json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
        forged = b"CCE01." + hashlib.sha256(body).hexdigest().encode() + b"." + body
        with self.assertRaises(ValueError):
            CausalContractEcology.restore(forged)

    def test_rejects_public_data_errors_before_learning(self):
        cce = CausalContractEcology()
        wrong = [
            ((True, 0), 1, 1), ((0,), 1, 0), ((0, 1), True, 0),
            ((0, 1), 0, 2), ((0, 1), 0, None),
            ((0, "1"), 1, 1),
        ]
        for event in wrong:
            with self.subTest(event=event), self.assertRaises(ValueError):
                cce.observe(*event)
        self.assertEqual(0, cce.events)
        self.assertEqual(0, cce.pooled.events)

    def test_bounded_capacity_and_public_only_context(self):
        for features in ((0, 0), (2,), ("0",)):
            with self.assertRaises(ValueError):
                CountModel(features)
        model = CountModel((0, 1))
        model.events = MAX_EVENTS
        with self.assertRaises(ValueError):
            model.observe((0, 1), 1, 1)
        self.assertEqual(MAX_EVENTS, model.events)
        with self.assertRaises(ValueError):
            validate_event((0, 1, 1), 0)

    def test_false_feature_never_supplied_to_selector(self):
        cce = CausalContractEcology()
        self.assertEqual([(0,), (1,)], [cell.features for cell in cce.candidates])
        self.assertEqual((), cce.pooled.features)
        self.assertEqual(3, len((cce.pooled, *cce.candidates)))


if __name__ == "__main__":
    unittest.main()
