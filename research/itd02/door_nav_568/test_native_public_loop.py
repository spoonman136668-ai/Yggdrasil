import unittest
from native_public_loop import NativePublicLoop, PublicWorld

class LoopTests(unittest.TestCase):
    def test_three_sessions(self):
        agent = NativePublicLoop()
        one = agent.episode(PublicWorld('A', surprise=True))
        two = agent.episode(PublicWorld('B'), recheck=True)
        three = agent.episode(PublicWorld('A'))
        self.assertEqual((one['selected'], two['selected'], three['selected']), ('snapshot', 'active', 'snapshot'))

    def test_bounded_unknown_outcome(self):
        agent = NativePublicLoop()
        outcome = agent.episode(PublicWorld('A', surprise=True), budget=4)
        self.assertIsNone(outcome['selected'])
        self.assertEqual(outcome['actions'], 4)

    def test_session_accounting(self):
        agent = NativePublicLoop()
        first = agent.episode(PublicWorld('A', surprise=True))
        second = agent.episode(PublicWorld('B'), recheck=True)
        third = agent.episode(PublicWorld('A'))
        self.assertEqual(second['rechecks'], 1)
        self.assertEqual(second['exceptions'], 0)
        self.assertEqual((first['actions'], second['actions'], third['actions']), (5, 5, 4))
        self.assertEqual([x['confirmed'] for x in (first, second, third)], [2, 2, 2])
