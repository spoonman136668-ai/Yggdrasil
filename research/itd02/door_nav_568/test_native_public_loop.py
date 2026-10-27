import unittest
from native_public_loop import NativePublicLoop, PublicWorld

class LoopTests(unittest.TestCase):
    def test_three_sessions(self):
        agent = NativePublicLoop()
        one = agent.episode(PublicWorld('A', surprise=True))
        two = agent.episode(PublicWorld('B'), recheck=True)
        three = agent.episode(PublicWorld('A'))
        self.assertEqual((one['selected'], two['selected'], three['selected']), ('snapshot', 'active', 'snapshot'))
