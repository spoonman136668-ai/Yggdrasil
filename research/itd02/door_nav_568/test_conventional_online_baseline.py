import unittest
from conventional_online_baseline import TabularOnlineBaseline
from online_public_learning import PublicOnlineTransitions

class ConventionalComparisonTests(unittest.TestCase):
    def test_matched_novel_successor_learning(self):
        for successor in (b"N7-novel", b"Q9-unfamiliar"):
            key = (b"M1-intermediate", 2)
            native = PublicOnlineTransitions({key: b"X5-shift"})
            conventional = TabularOnlineBaseline()
            for _ in range(2):
                native.observe(key, successor)
                conventional.observe(key, successor)
            self.assertEqual(native.links[key], successor)
            self.assertEqual(conventional.predict(key), successor)
            self.assertEqual(native.examples(), conventional.examples)

    def test_single_observation_requires_corroboration(self):
        key = (b"M1-intermediate", 2)
        conventional = TabularOnlineBaseline()
        conventional.observe(key, b"N7-novel")
        self.assertIsNone(conventional.predict(key))
