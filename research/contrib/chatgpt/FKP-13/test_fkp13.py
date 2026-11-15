"""FKP-13 fixture-only engineering checks. NEVER reset original DEV source."""
from __future__ import annotations
import hashlib
import random
import sys
from pathlib import Path
import unittest
from unittest import mock

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import cohorts
import controller
from model import DirectMemory,brier
from baselines import train_all
# Parent FKP12 also has run_dev.py; load THIS test target by exact filename.
import importlib.util
_spec=importlib.util.spec_from_file_location("fkp13_run_dev",HERE/"run_dev.py")
run_dev=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_dev)


def fake_episode(offset=0,n=10):
    x=[];y=[]
    for j in range(n):
        image=np.full((16,16,3),((j+offset)*31)%255,dtype=np.uint8)
        a=((j+offset)%3,(j+1)%3)
        x.append(cohorts.source12.input_feature(image,a,j%3))
        y.append((j+offset)%3)
    return {"x":np.stack(x).astype(np.float32),"y":np.asarray(y,dtype=np.int64)}

class TestFKP13(unittest.TestCase):
    def test_disjoint_prospective_custody_and_no_protected_source(self):
        self.assertEqual(cohorts.SOURCE_SHA,"a94f2b60d1769ea44df3226561488768e1dff9f4")
        self.assertEqual((len(cohorts.TRAIN),len(cohorts.VALIDATE),len(cohorts.DEV)),(48,16,24))
        self.assertTrue(set(cohorts.TRAIN).isdisjoint(cohorts.VALIDATE))
        self.assertTrue(set(cohorts.TRAIN).isdisjoint(cohorts.DEV))
        self.assertTrue(set(cohorts.VALIDATE).isdisjoint(cohorts.DEV))
        self.assertTrue(set(cohorts.DEV).isdisjoint(cohorts.TRANSFER))
        self.assertEqual(cohorts.OPTIONS,{"reward_fall_off":-0.05,"max_steps":512})
        self.assertEqual(len(controller.ARMS),9)
        for forbidden in (971300,971500,971600,973600,1900,True):
            with self.subTest(seed=forbidden),self.assertRaises((ValueError,PermissionError)):
                cohorts.cohort(forbidden)
        with self.assertRaises(PermissionError):cohorts.cohort(cohorts.DEV[0])
        self.assertEqual(cohorts.cohort(cohorts.DEV[0],dev=True),"DEV")
        with self.assertRaises(PermissionError):cohorts.collect(tuple(cohorts.DEV),None)
        with self.assertRaises(PermissionError):cohorts.collect(tuple(cohorts.TRANSFER),None)

    def test_public_actions_are_bounded_and_reproducible(self):
        for pol in cohorts.POLICIES:
            def trace():
                rng=cohorts.policy_rng(cohorts.TRAIN[0],pol)
                macro=None;output=[]
                for t in range(35):
                    a=cohorts.public_policy(rng,pol,t,macro)
                    macro=a;output.append(a)
                return output
            a=trace()
            self.assertEqual(a,trace())
            self.assertTrue(all(len(x)==2 and all(0<=v<3 for v in x) for x in a))
            if pol=="macro8":
                self.assertEqual(len(set(a[0:8])),1)
                self.assertEqual(len(set(a[8:16])),1)
        with self.assertRaises(ValueError):
            cohorts.public_policy(random.Random(1),"macro8",512)

    def test_candidate_features_match_parent_public_source_exactly(self):
        im=np.full((16,24,3),177,dtype=np.uint8)
        feat=controller.candidates(im,2)
        self.assertEqual(feat.shape,(9,204))
        for idx in range(9):
            expect=cohorts.source12.input_feature(im,(idx//3,idx%3),2)
            self.assertTrue(np.array_equal(feat[idx],expect))
        with self.assertRaises(ValueError):controller.candidates(im,7)

    def test_direct_online_and_conventional_count_atomic_cumulative_memory(self):
        train=[fake_episode(1),fake_episode(3)]
        direct=DirectMemory().fit(train)
        counts=DirectMemory(two_hash=False).fit(train)
        shuffled=DirectMemory().fit(train,shuffle_labels=True)
        torch,learned,selection=train_all(train,train)
        p=controller.Controller("DIRECT_ONLINE",direct,counts,learned,shuffled,torch)
        q=controller.Controller("COUNT_ONLINE",direct,counts,learned,shuffled,torch)
        fixed=controller.Controller("DIRECT_FROZEN",direct,counts,learned,shuffled,torch)
        p.new_world();q.new_world()
        a=controller.candidates(np.full((16,16,3),23,dtype=np.uint8),1)
        pp,branches=p.estimate(a)
        idx=controller.choose_index(pp,controller.arm_rng(cohorts.TRAIN[0],"DIRECT_ONLINE"))
        old=p.memory.snapshot()
        p.observed(a,idx,branches,2)
        q.observed(a,idx,None,2)
        self.assertNotEqual(p.memory.snapshot(),old)
        self.assertEqual(fixed.memory.snapshot(),direct.snapshot())
        self.assertNotEqual(q.memory.snapshot(),counts.snapshot())
        self.assertEqual(p.cold(a),hashlib.sha256(p.memory.snapshot()).hexdigest())
        self.assertIsInstance(q.cold(a),str)
        self.assertEqual(p.memory.weights.nbytes,49152)
        self.assertEqual(q.memory.weights.nbytes,49152)
        self.assertTrue(np.isfinite(p.estimate(a)[0]).all())

    def test_fully_trained_recurrent_closedloop_online_update(self):
        train=[fake_episode(0),fake_episode(2)]
        torch,learned,selection=train_all(train,train)
        for kind in ("GRU","MLP","LOGISTIC"):
            self.assertEqual(selection[kind]["full_epochs_per_seed"],24)
            self.assertEqual(selection[kind]["seeds_trained"],[1212,3434])
        direct=DirectMemory().fit(train)
        counts=DirectMemory(two_hash=False).fit(train)
        shuffled=DirectMemory().fit(train,shuffle_labels=True)
        c=controller.Controller("GRU_ONLINE",direct,counts,learned,shuffled,torch)
        c.new_world()
        f=controller.candidates(np.full((16,16,3),111,dtype=np.uint8),1)
        for j in range(16):
            prob,branches=c.estimate(f)
            self.assertEqual(prob.shape,(9,3))
            self.assertTrue(np.allclose(prob.sum(axis=1),1))
            c.observed(f,j%9,branches,j%3)
        self.assertEqual(c.learning_updates,1)
        self.assertIsNone(c.current_hidden)
        frozen=controller.Controller("GRU_FROZEN",direct,counts,learned,shuffled,torch)
        prob,_=frozen.estimate(f)
        self.assertTrue(np.isfinite(prob).all())

    def test_source_safe_mocked_closed_loop_intervention(self):
        class FakeEnv:
            def __init__(self):self.actions=0;self.closed=False
            def close(self):self.closed=True
        env=FakeEnv()
        frame=np.full((16,16,3),64,dtype=np.uint8)
        def source_step(e,a):
            e.actions+=1
            return frame,(0.1 if e.actions==2 else -0.05 if e.actions==4 else 0.0),e.actions==5,False
        fake_seed=cohorts.TRAIN[0]
        direct=DirectMemory().fit([fake_episode(0)])
        counts=DirectMemory(two_hash=False).fit([fake_episode(0)])
        shuffled=DirectMemory().fit([fake_episode(2)])
        torch,learned,_=train_all([fake_episode(0)],[fake_episode(3)])
        c=controller.Controller("DIRECT_ONLINE",direct,counts,learned,shuffled,torch)
        with mock.patch.object(cohorts,"DEV",(fake_seed,)),mock.patch.object(
            cohorts,"new_env",return_value=(env,frame)),mock.patch.object(
            cohorts,"real_step",side_effect=source_step):
            result=run_dev.play(fake_seed,c,None)
        self.assertEqual(result["steps"],5)
        self.assertEqual(result["positive_progress"],1)
        self.assertEqual(result["negative_events"],1)
        self.assertEqual(result["goals_from_public_rewards"],0)
        self.assertEqual(c.total_source_observations,5)
        self.assertTrue(env.closed)

    def test_private_source_absent_and_statistic_strongest_reselection(self):
        text=(HERE/"run_dev.py").read_text()+(HERE/"cohorts.py").read_text()
        import ast
        parsed=ast.parse(text)
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=="unwrapped"
                             for n in ast.walk(parsed)))
        self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=="info"
                             for n in ast.walk(parsed)))
        self.assertNotIn("debug_rgb_array",text)
        rows=[{"seed":s,"arm":arm,"return":float(i%3)}
              for i,s in enumerate(cohorts.DEV) for arm in controller.ARMS]
        strongest,gain,ci,means=run_dev.paired_gain(rows)
        self.assertIn(strongest,controller.ARMS)
        self.assertNotEqual(strongest,"DIRECT_ONLINE")
        self.assertEqual(len(ci),2)
        self.assertEqual(len(means),9)

if __name__=="__main__":unittest.main()
