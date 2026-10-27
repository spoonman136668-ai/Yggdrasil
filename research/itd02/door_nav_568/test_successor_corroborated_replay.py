"""Source-free public successor corroboration and common-mode attack tests."""
import unittest
from successor_corroborated_replay import SuccessorCorroboratedReplay

PROBES = ((b"xB-train", 1), (b"yA-train", 1))

def reward_for(regime, frame, action):
    correct = (1 if frame[1:2] == b"A" else 0) if regime == "A" else (1 if frame[:1] == b"x" else 0)
    return int(action == correct)

def fit(agent, regime):
    for x in (b"x", b"y"):
        for y in (b"A", b"B"):
            for action in (0, 1):
                frame = x+y+b"-train"
                agent.observe(frame, [0, 1])
                agent.learn(action, regime.encode()+b":"+frame,
                            reward_for(regime, frame, action), True)

def build():
    agent = SuccessorCorroboratedReplay()
    fit(agent, "A")
    agent.archive()
    fit(agent, "B")
    agent.start_probe()
    return agent

def probe(agent, reported_reward_regime, public_successor_regime):
    for frame, action in PROBES:
        agent.observe(frame, [0, 1])
        agent.learn(action, public_successor_regime.encode()+b":"+frame,
                    reward_for(reported_reward_regime, frame, action), True)
    return agent.restore_with_corrob()

class SuccessorCorroborationTests(unittest.TestCase):
    def test_clean_return_restores(self):
        agent = build()
        self.assertTrue(probe(agent, "A", "A"))
        self.assertFalse(agent.learner.probe_active)

    def test_corrupted_reward_with_stable_successor_refused(self):
        agent = build()
        self.assertFalse(probe(agent, "A", "B"))
        self.assertFalse(agent.learner.probe_active)

    def test_joint_reward_and_successor_corruption_still_fools(self):
        agent = build()
        self.assertTrue(probe(agent, "A", "A"))
        # This is indistinguishable from a genuine return without an
        # additional independent source. Do not claim unconditional safety.

    def test_uncorroborated_successor_refuses(self):
        agent = build()
        self.assertFalse(probe(agent, "A", "unknown"))

    def test_cannot_reuse_same_public_action_twice(self):
        agent = build()
        for _ in range(2):
            frame, action = PROBES[0]
            agent.observe(frame, [0, 1])
            agent.learn(action, b"A:"+frame, reward_for("A", frame, action), True)
        self.assertFalse(agent.restore_with_corrob())

if __name__ == "__main__":
    unittest.main()
