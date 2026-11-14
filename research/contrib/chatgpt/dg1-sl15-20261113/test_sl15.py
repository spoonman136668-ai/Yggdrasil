"""DG1-SL15 engineering preflight; no registered scientific world is stepped."""
import json
import unittest
from pathlib import Path

from sl15 import (ARMS, AUDITS, COLD, COHORTS, FREEZE, PAIRED,
                  ModuleDNA, World, learner, trial)
import sl15
p = sl15.p


class SL15PreFirstUse(unittest.TestCase):
    def test_frozen_science_registration(self):
        d = json.loads((Path(__file__).parent / "prereg.json").read_text())
        self.assertEqual(FREEZE,
                         "54c6a289e2c4b862a026550624d0a6e585cade40")
        self.assertEqual(d["status"],
                         "FROZEN_BEFORE_IMPLEMENTATION_AND_FIRST_SCIENTIFIC_USE")
        self.assertEqual(d["budgets"]["total_charged_steps"], 18432)
        self.assertEqual(d["budgets"]["total_causal_observations"], 14784)
        self.assertEqual(d["budgets"]["total_input_perturbations"], 3648)
        self.assertEqual(len(ARMS), 6)
        self.assertEqual(len(PAIRED), 5)
        self.assertEqual(sum(map(len, COHORTS.values())), 32)
        self.assertEqual(AUDITS, (24,48,54,72,78,96))
        self.assertEqual(COLD, (43,67,89))
        self.assertNotEqual(
            set(sum((list(v) for v in COHORTS.values()),[])),
            set(sum((list(v) for v in p.COHORTS.values()),[])),
        )

    def test_module_is_action_local_and_nontoken(self):
        m = ModuleDNA()
        for a in range(3):
            self.assertEqual(m.predict(0,a), 0)
        for i in range(21):
            a = i % 3
            x = (i*5) % 8
            m.observe(x,a,p.gate(0,p.pair(x,a)))
        self.assertEqual(m.causal_events,21)
        self.assertEqual(sum(s["n"] for mod in m.modules
                             for s in mod["slots"]),21)
        self.assertEqual(m.choose(3,48),m.choose(3,48))
        self.assertIn(m.choose(3,48),range(3))
        self.assertEqual(len(m.modules),3)

    def test_cached_rule_refresh_matches_full_minimization(self):
        m = ModuleDNA()
        for i in range(77):
            a = i % 3
            x = (i*3+1) % 8
            m.observe(x,a,p.gate(3,p.pair(x,a)))
            for mod in m.modules:
                for slot in mod["slots"]:
                    ranking=sorted(range(6),key=lambda k:(slot["err"][k],k))
                    self.assertEqual((slot["best"],slot["second"]),
                                     tuple(ranking[:2]))
        with self.assertRaises(ValueError):
            m.observe(0,0,1)

    def test_cold_memory_tamper_rejected_and_prediction_parity(self):
        for enabled in (True,False):
            m=ModuleDNA(enabled)
            for i in range(35):
                a=i%3
                x=(i*7+2)%8
                m.observe(x,a,(i//3)%2)
            cold=m.snapshot()
            clone=ModuleDNA.restore(cold)
            self.assertEqual(cold,clone.snapshot())
            self.assertLessEqual(len(cold),8192)
            self.assertEqual(
                [m.predict(x,a) for x in range(8) for a in range(3)],
                [clone.predict(x,a) for x in range(8) for a in range(3)]
            )
            for corrupt in (cold[:-1],cold+b" ",
                            bytes([cold[0]^1])+cold[1:]):
                with self.assertRaises(ValueError):
                    ModuleDNA.restore(corrupt)

    def test_retrieval_disabled_cannot_log_reuse(self):
        m=ModuleDNA(False)
        for t in range(77):
            a=t%3
            x=(t//3)%8
            changed=p.gate(3 if t>=26 and t<52 else 0,p.pair(x,a))
            m.observe(x,a,changed)
        self.assertFalse(any(t[4] for t in m.transitions))
        self.assertEqual(m.causal_events,77)

    def test_negative_no_oracle_no_uncharged_interventions(self):
        m=ModuleDNA()
        with self.assertRaises(TypeError):
            m.observe(0,0,1,hidden_context="A")
        with self.assertRaises(ValueError):
            m.observe(0,0,2)
        with self.assertRaises(ValueError):
            m.observe(8,0,1)
        with self.assertRaises(ValueError):
            m.observe(0,3,1)
        with self.assertRaises(ValueError):
            m.choose(0,49)
        with self.assertRaises(ValueError):
            m.choose(0,47)
        with self.assertRaises(ValueError):
            World(107001,"ABAB")
        with self.assertRaises(ValueError):
            World(108001,"not-a-cohort")
        with self.assertRaises(ValueError):
            learner("outside-registered-arm")
        with self.assertRaises(ValueError):
            trial(108001,"ABAB","module_active","diagnostic",[])
        with self.assertRaises(ValueError):
            trial(108001,"ABAB","module_active","replay",[None]*96)

    def test_same_paid_event_stream_deterministic_model_output(self):
        def feed():
            m=ModuleDNA()
            for i in range(77):
                a=i%3
                x=(i*11)%8
                changed=p.gate(3 if 25<=i<50 else 0,p.pair(x,a))
                m.observe(x,a,changed)
            return m
        a,b=feed(),feed()
        self.assertEqual(a.snapshot(),b.snapshot())
        self.assertEqual(a.transitions,b.transitions)
        self.assertEqual(
            [a.predict(x,j) for x in range(8) for j in range(3)],
            [b.predict(x,j) for x in range(8) for j in range(3)]
        )


if __name__ == "__main__":
    unittest.main()
