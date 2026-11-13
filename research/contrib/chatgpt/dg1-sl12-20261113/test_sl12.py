"""DG1-SL12 prereg, paid physical A-B-A-B, custody and retrieval negatives."""
import json
import unittest
from pathlib import Path
from sl12 import (
    ARMS, AUDITS, COLD, COHORTS, FLIPS, FREEZE, MATCHED,
    ArchiveMemory, World, choose, genuine_returns, learner, one_world,
    sl09, trial,
)


class SL12Tests(unittest.TestCase):
    def test_frozen_registration_custody(self):
        p=json.loads((Path(__file__).parent/"prereg.json").read_text())
        self.assertEqual(FREEZE,"33f6cf977890033fa71398006d52a9808ce2e109")
        self.assertEqual(p["status"],"FROZEN_BEFORE_IMPLEMENTATION_AND_OUTCOME")
        self.assertEqual(len(ARMS),6)
        self.assertEqual(sum(map(len,COHORTS.values())),32)
        self.assertEqual(AUDITS,(40,44,56,60,64,72,80))
        self.assertEqual(COLD,(37,57,73))
        self.assertTrue(all(x not in (20,40,60) for x in COLD))
        self.assertEqual(p["budgets"]["total_paid_steps"],15360)
        self.assertEqual(p["budgets"]["total_causal_observations"],13440)

    def test_world_physical_budget_and_private_phase(self):
        for cohort,seeds in COHORTS.items():
            w=World(seeds[0],cohort)
            state=seeds[0]%16
            counts={"flip":0,"causal":0}
            for step in range(80):
                chosen=(step%4 if step>=40 and step not in FLIPS else None)
                kind,act,nxt=w.step(state,step,chosen)
                counts[kind]+=1
                self.assertIn(nxt,(state,state^(1<<act)))
                state=nxt
            self.assertEqual(counts,{"flip":10,"causal":70})
            self.assertEqual(w.paid,80)
            with self.assertRaises(ValueError):
                w.step(state,79,0)
            with self.assertRaises(ValueError):
                w.audit_truth(0,0,79)
        with self.assertRaises(ValueError):
            World(104001,"ABAB")
        w=World(105001,"ABAB")
        with self.assertRaises(ValueError):
            w.step(0,0,0)
        with self.assertRaises(ValueError):
            w.step(0,40)
        with self.assertRaises(TypeError):
            ArchiveMemory().observe(0,0,0,hidden_phase="A")

    def test_checkpoint_tamper_and_cold_prediction_parity(self):
        for allow in (True,False):
            x=ArchiveMemory(allow)
            for n in range(15):
                state=n%16
                x.observe(state,n%4,state)
            raw=x.snapshot()
            y=ArchiveMemory.restore(raw)
            self.assertEqual(y.snapshot(),raw)
            self.assertEqual(
                [x.predict(s,a) for s in range(16) for a in range(4)],
                [y.predict(s,a) for s in range(16) for a in range(4)],
            )
            for damaged in (raw[:-1],raw+b" ",
                            bytes([raw[0]^1])+raw[1:]):
                with self.assertRaises(ValueError):
                    ArchiveMemory.restore(damaged)
            self.assertLessEqual(len(raw),8192)

    def test_genuine_archive_requires_populated_previous_bank(self):
        x=ArchiveMemory(True)
        for i in range(15):
            x.observe(0,0,0)
        self.assertFalse(any(t[3] for t in x.transitions))
        self.assertEqual(len(x.model.banks),1)
        self.assertEqual(x.model.switches,0)
        with self.assertRaises(ValueError):
            x.observe(0,0,2)
        with self.assertRaises(ValueError):
            choose(x,0,37,"probe")
        with self.assertRaises(ValueError):
            choose(x,0,62,"probe")
        with self.assertRaises(ValueError):
            choose(learner("sl11_on_probe"),0,40,"probe")
        with self.assertRaises(ValueError):
            learner("not-an-arm")

    def test_no_archive_arm_never_reactivates(self):
        x=ArchiveMemory(False)
        for n in range(70):
            state=n%16
            x.observe(state,n%4,state^(1<<(n%4)) if n%3==0 else state)
        self.assertFalse(any(t[3] for t in x.transitions))
        self.assertEqual(x.causal_events,70)
        with self.assertRaises(ValueError):
            x.observe(0,0,0)
        self.assertLessEqual(len(x.snapshot()),8192)

    def test_all_six_arms_charged_replay_cold_and_audit(self):
        w=one_world(105001,"ABAB")
        self.assertEqual(set(w["arms"]),set(ARMS))
        arms=w["arms"]
        self.assertEqual(
            len({arms[a]["trace_sha256"] for a in MATCHED}),1)
        self.assertEqual(
            len({z["trace_first40_sha256"]
                 for z in arms.values()}),1)
        for a,z in arms.items():
            self.assertEqual(z["charged_steps"],80,a)
            self.assertEqual(z["flips"],10,a)
            self.assertEqual(z["causal_observations"],70,a)
            self.assertEqual(len(z["cold_snapshot_bytes"]),3,a)
            self.assertLessEqual(max(z["cold_snapshot_bytes"]+
                                     [z["final_snapshot_bytes"]]),8192,a)
            self.assertEqual(sum(z["prequential"].values()),70)
            for step in AUDITS:
                v=z["audits"][str(step)]
                self.assertEqual(sum(v[k] for k in
                    ("correct","wrong_confident","abstained")),64,a)
        self.assertFalse(any(t["archived_reuse"] for t in
            arms["no_archive_on_probe"]["memory_transitions"]))
        signs=genuine_returns(w)
        self.assertEqual(set(signs),{"A2","B2","falseC"})

    def test_replay_injection_rejected(self):
        with self.assertRaises(ValueError):
            trial(105001,"ABAB","archive_probe","replay",
                  replay_plan=[None])
        fake=[None]*80
        fake[40]=0
        fake[46]=1
        with self.assertRaises(ValueError):
            trial(105001,"ABAB","no_archive_on_probe","replay",
                  replay_plan=fake)


if __name__=="__main__":
    unittest.main()
