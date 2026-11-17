"""Only source-free mathematical fixtures; no original or new source opened."""
from pathlib import Path
from unittest import TestCase
import selector as P

class NoSourceGate(TestCase):
    def test_policy_geometry(self):
        self.assertEqual((len(P.MASKS),len(P.LOW),len(P.HIGH)),(63,22,6))
        self.assertEqual(P.HIGH,(31,47,55,59,61,62))
        self.assertEqual(len(P.FIXED),32)
        self.assertEqual(P.WARM,P.FIXED[:20])
        self.assertEqual(len(P.POLICIES),4)
        for law in (1,17,282000):
            self.assertEqual(len(P.random_schedule(law)),32)
            self.assertEqual(P.random_schedule(law)[:20],P.WARM)
    def test_challenger_uses_only_own_paid_rows(self):
        rows=tuple((x,(int((x&31)==31)^((x>>2)&1))) for x in P.WARM)
        programs,overflow=P.challenger_hypotheses(rows)
        self.assertIsInstance(programs,tuple)
        self.assertIsInstance(overflow,bool)
        self.assertNotIn(P.choose_next(rows,111),P.WARM)
        self.assertEqual(P.choose_next(rows,111),P.choose_next(rows,111))
        with self.assertRaises(ValueError):P.choose_next(tuple(reversed(rows)),111)
        with self.assertRaises(ValueError):P.choose_next(rows,True)
        with self.assertRaises(ValueError):P.choose_next(rows+tuple((x,0) for x in P.FIXED[20:32]),111)
    def test_schedule_and_postseal(self):
        seen=[]
        def observer(x):
            self.assertNotIn(x,seen)
            seen.append(x)
            return int((x&31)==31)^((x>>2)&1)
        falsifier=P.falsifier_schedule(111,observer)
        self.assertEqual(len(falsifier),32)
        self.assertEqual(tuple(seen),tuple(x for x,y in falsifier))
        baseline=P.parent_adaptive_schedule(111,lambda x:int((x&31)==31)^((x>>2)&1))
        acts={'fixed':P.fixed_schedule(),'random':P.random_schedule(111),
              'baseline_adaptive':tuple(x for x,y in baseline),
              'falsifier':tuple(x for x,y in falsifier)}
        preds={name:{x:None for x in range(64)} for name in acts}
        held=P.hidden_future_questions(111,acts,preds)
        self.assertEqual(len(held),8)
        self.assertFalse(set(held)&set().union(*(set(v) for v in acts.values())))
        with self.assertRaises(ValueError):P.hidden_future_questions(111,acts,{'fixed':preds['fixed']})
        with self.assertRaises(ValueError):P.hidden_future_questions(111,acts,{k:{} for k in acts})
        with self.assertRaises(ValueError):P.falsifier_schedule(111,lambda x:None)
        self.assertNotIn('import source',Path(__file__).with_name('selector.py').read_text())
