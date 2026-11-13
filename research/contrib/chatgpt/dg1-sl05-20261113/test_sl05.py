import unittest
from sl05 import (
    World,SEEDS,ARMS,FREEZE_SHA,ColdThreeBank,ConventionalHMM3,
    make_arm,restore_arm,one_world,run
)

class ColdRetentionTests(unittest.TestCase):
    def test_physical_actions_are_charged_and_hidden(self):
        w=World(98001,"ABCA")
        s=98001%16
        flips=0
        for step in range(80):
            kind,a,s=w.step(s,step)
            flips += int(kind=="flip")
        self.assertEqual(flips,10)
        self.assertEqual(w.paid,80)
        with self.assertRaises(ValueError):w.step(s,79)
        with self.assertRaises(ValueError):w.audit_truth(0,0,79)

    def test_no_oracle_or_bad_transition_can_be_learned(self):
        for arm in ARMS:
            agent=make_arm(arm)
            with self.assertRaises(TypeError):
                agent.observe(0,0,0,hidden_phase="A")
            with self.assertRaises(ValueError):
                agent.observe(0,0,2)
            self.assertIsNone(agent.predict(0,0))

    def test_memory_custody_and_negative_tamper(self):
        for arm in ARMS:
            agent=make_arm(arm)
            for sample in [(0,0,0),(1,1,1),(2,2,2),(3,3,3)]:
                agent.observe(*sample)
            agent.rest()
            raw=agent.snapshot()
            self.assertEqual(restore_arm(arm,raw).snapshot(),raw)
            self.assertLessEqual(len(raw),8192)
            if arm.startswith(("cold_","three_bank_","conventional_three_bank_")):
                for altered in (raw[:-1],raw+b" ",bytearray(raw),
                                bytes([raw[0]^1])+raw[1:]):
                    with self.assertRaises(ValueError):
                        restore_arm(arm,altered)

    def test_rest_cannot_invent_training_episodes(self):
        for m in (ColdThreeBank(), ConventionalHMM3(replay=True)):
            for event in ((0,0,0),(1,0,1),(2,1,2),(4,2,4)):
                m.observe(*event)
            prior=m.clock
            events=list(m.events)
            m.rest()
            self.assertEqual(m.clock,prior)
            self.assertEqual(m.events,events)

    def test_frozen_recent_long_horizon_compatibility_without_policy_change(self):
        from sl05 import sl04
        agent=sl04.RecentWindow()
        for i in range(70):
            before=i%16
            agent.observe(before,i%4,before)
        raw=agent.snapshot()
        restored=restore_arm("frozen_sl04_recent",raw)
        self.assertEqual(restored.snapshot(),raw)
        self.assertEqual(agent.masks,restored.masks)
        self.assertEqual(agent.observations,70)
        for state in range(16):
            for action in range(4):
                self.assertEqual(agent.predict(state,action),
                                 restored.predict(state,action))
        with self.assertRaises(ValueError):
            restore_arm("frozen_sl04_recent",raw+b" ")

    def test_world_cold_resume_and_audits(self):
        result=one_world(98001,"ABCA")
        self.assertEqual(result["paid_actions"],80)
        self.assertEqual(result["causal_observations"],70)
        self.assertTrue(all(result["cold_restore_at_60"].values()))
        for arm in ARMS:
            self.assertLessEqual(result["snapshot_bytes"][arm]["80"],8192)
            self.assertEqual(set(result["audits"][arm]),{"20","40","60","80"})
            for point in ("20","40","60","80"):
                self.assertEqual(sum(result["audits"][arm][point][metric] for metric in
                                ("correct","wrong_confident","abstained")),64)

    def test_prereg_world_identity(self):
        self.assertEqual(FREEZE_SHA,"10fa5ec7c983b871482b772ec54d7522ec3e3ac5")
        self.assertEqual(len(SEEDS),4)
        self.assertEqual(sum(len(s) for s in SEEDS.values()),32)
        self.assertEqual(len(ARMS),7)

if __name__=="__main__":
    unittest.main()
