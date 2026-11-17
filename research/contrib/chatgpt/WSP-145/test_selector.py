"""WSP145 source-free unit fixtures; no protected/scored source consumed."""
from pathlib import Path
from unittest import TestCase
import selector as P

class SourceFree(TestCase):
    def test_01_fixed_controls(self):
        self.assertEqual(len(P.MASKS),63)
        self.assertEqual(P.H.LEVELS[5],(31,47,55,59,61,62))
        for law in (1,17,272000):
            a=P.fixed_schedule();b=P.random_schedule(law)
            self.assertEqual((len(a),len(b),len(set(a)),len(set(b))),(32,32,32,32))
            self.assertEqual(a[:20],b[:20])
        self.assertNotEqual(P.random_schedule(17),P.random_schedule(18))
    def test_02_adaptive_only_charged_effects(self):
        seen=[]
        def charge(x):
            self.assertNotIn(x,seen);seen.append(x)
            return int((x&31)==31)^((x>>2)&1)
        rows=P.adaptive_schedule(101,charge)
        self.assertEqual(len(rows),32)
        self.assertEqual(tuple(seen),tuple(x for x,y in rows))
        self.assertEqual(tuple(seen[:20]),P.WARM)
        with self.assertRaises(ValueError):P.choose_next(rows,101)
        with self.assertRaises(ValueError):P.adaptive_schedule(2,lambda x:None)
        with self.assertRaises(ValueError):P.adaptive_schedule(True,charge)
        with self.assertRaises(ValueError):P.choose_next(rows[:-1]+((rows[0][0],1),),101)
    def test_03_hidden_future_after_seal(self):
        rows=P.adaptive_schedule(101,lambda x:int((x&31)==31)^((x>>2)&1))
        acts={'fixed':P.fixed_schedule(),'random':P.random_schedule(101),
              'adaptive':tuple(x for x,y in rows)}
        predictions={k:{x:None for x in range(64)} for k in acts}
        held=P.hidden_future_questions(101,acts,predictions)
        self.assertEqual(len(held),8)
        self.assertFalse(set(held)&set().union(*(set(xs) for xs in acts.values())))
        self.assertEqual(held,P.hidden_future_questions(101,acts,predictions))
        with self.assertRaises(ValueError):P.hidden_future_questions(101,acts,{k:{} for k in acts})
        with self.assertRaises(ValueError):P.hidden_future_questions(101,{'fixed':acts['fixed']},predictions)
    def test_04_negative_no_source(self):
        rows=tuple((x,0) for x in P.WARM)
        self.assertEqual(len(P._stage_candidates(rows)),4)
        self.assertNotIn(P.choose_next(rows,17),P.WARM)
        with self.assertRaises(ValueError):P.structural_split(rows,64)
        with self.assertRaises(ValueError):P.choose_next(tuple(reversed(rows)),17)
        text=Path(__file__).with_name('selector.py').read_text(encoding='utf-8')
        self.assertNotIn('import source',text)
        self.assertNotIn('from source import',text)
