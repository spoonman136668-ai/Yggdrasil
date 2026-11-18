"""Focused source-negative controls for the frozen CKAD21 dual-memory reader."""
import importlib.util
from itertools import product
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ckad21_campaign',HERE/'campaign.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sample(source, n=16):
    out=[]
    for index in range(n):
        view=((index%2,0),(index%2,1))
        first=(index//2)%2
        state=first^(index%2) if source=='early' else first
        second=(index//3)%2
        reward=second^state if source=='early' else second
        out.append([m.digest(m.canonical([source,index])),view,first,state,second,reward])
    return out


class CKAD21FalsifiableTests(unittest.TestCase):
    def setUp(self):
        self.early=m.FittedTable(sample('early'),0)
        self.late=m.FittedTable(sample('late'),0)

    def test_bayesian_joint_and_consequence_identity(self):
        self.assertEqual(m.check_formula(self.early,self.late),32)
        for view in product(m.BITS,repeat=2):
            for first,state,second in product(m.BITS,repeat=3):
                x=m.mixture_joint(self.early,self.late,view,first,state,second)
                y=m.independent_joint(self.early,self.late,view,first,state,second)
                self.assertEqual(x,y)

    def test_valid_bounded_plans_and_swap_invariance(self):
        for view in product(m.BITS,repeat=2):
            for adaptive in (False,True):
                p=m.mixture_plan(self.early,self.late,view,adaptive=adaptive)
                self.assertEqual(p,m.mixture_plan(self.late,self.early,view,adaptive=adaptive))
                self.assertIn(p['first_action'],m.BITS)
                self.assertEqual(len(p['second_actions']),2)
                self.assertTrue(all(len(b)==2 and all(a in m.BITS for a in b)
                                    for b in p['second_actions']))

    def test_invalid_public_input_denied(self):
        with self.assertRaises(ValueError):
            self.early.transition_p((0,True),0)
        with self.assertRaises(ValueError):
            self.early.transition_p((0,1),2)
        with self.assertRaises(ValueError):
            self.early.terminal_p((0,1),0,2,0)

    def test_frozen_training_episode_identities(self):
        rows=[]
        for cohort,n in (('train-0',64),('train-1',64),('train-2',96)):
            for j in range(n):
                rows.append([m.expected_event_id(cohort,101,j),[[0,0],[0,0]],0,0,0,0])
        early,late=m.verify_public_witnesses(rows,101)
        self.assertEqual((len(early),len(late)),(64,96))
        corrupted=[r.copy() for r in rows]
        corrupted[90][0]=m.expected_event_id('eval-2',101,90)
        with self.assertRaises(ValueError):
            m.verify_public_witnesses(corrupted,101)
        duplicate=[r.copy() for r in rows]
        duplicate[223][0]=duplicate[222][0]
        with self.assertRaises(ValueError):
            m.verify_public_witnesses(duplicate,101)

    def test_retention_policy_never_mutates_training_tables(self):
        original=(dict(self.early.transition),dict(self.early.terminal),
                  dict(self.late.transition),dict(self.late.terminal))
        for view in product(m.BITS,repeat=2):
            for adaptive in (False,True):
                m.mixture_plan(self.early,self.late,view,adaptive=adaptive)
        self.assertEqual(original,(dict(self.early.transition),dict(self.early.terminal),
                                   dict(self.late.transition),dict(self.late.terminal)))


if __name__=='__main__':
    unittest.main()
