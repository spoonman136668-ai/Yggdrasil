import itertools
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_sparse_hypothesis import NativeSparseHypothesis
from yggdrasil.native_prior_hypothesis import input_order


def view(labels):
    rows=[[x&7,x>>3,y] for x,y in enumerate(labels)]
    v=NativeContextAccumulator(3).stage_update(0,rows,digest(canonical(rows)),max_degree=4)
    return v.checkpoint()


class SparseNativeTests(unittest.TestCase):
    def test_exact_small_space_minimum_matches_independent_exhaustive_control(self):
        labels=[(x&1)^((x>>1)&1) for x in range(16)]
        raw=view(labels);m,cost=NativeSparseHypothesis.fit_checkpoint(raw,digest(raw))
        fit=sorted(range(16),key=input_order)[:12]
        def predicts(terms,x):return sum((x&t)==t for t in terms)%2
        feasible=[terms for k in range(3) for terms in itertools.combinations(range(16),k)
                  if all(predicts(terms,x)==labels[x] for x in fit)]
        self.assertEqual(m.info()['active_weights'],min(map(len,feasible)))
        self.assertTrue(m.eligible)
        self.assertEqual([m.predict_provisional(x&7,x>>3) for x in range(16)],labels)
        self.assertEqual(cost['solver_status'],0)

    def test_calibration_never_enters_fit_or_triggers_another_search(self):
        order=sorted(range(16),key=input_order);labels=[0]*16
        for x in order[12:]:labels[x]=1
        raw=view(labels);m,_=NativeSparseHypothesis.fit_checkpoint(raw,digest(raw))
        self.assertEqual(m.info()['active_weights'],0)
        self.assertEqual(m.info()['calibration_errors'],4)
        self.assertFalse(m.eligible)

    def test_timeout_is_negative_and_discards_uncertified_incumbent(self):
        raw=view([x&1 for x in range(16)])
        with patch('scipy.optimize.milp',return_value=SimpleNamespace(status=1,x=[1.]*28)):
            m,_=NativeSparseHypothesis.fit_checkpoint(raw,digest(raw))
        self.assertFalse(m.eligible);self.assertEqual(m.info()['active_weights'],0)
        self.assertTrue(all(m.predict_provisional(x&7,x>>3) is None for x in range(16)))

    def test_invalid_optimal_solver_output_rejected(self):
        raw=view([x&1 for x in range(16)])
        with patch('scipy.optimize.milp',return_value=SimpleNamespace(status=0,x=[0.5]*28)):
            with self.assertRaises(ValueError):NativeSparseHypothesis.fit_checkpoint(raw,digest(raw))

    def test_native_checkpoint_restores_and_reads_without_solver_import(self):
        raw=view([x&1 for x in range(16)]);m,_=NativeSparseHypothesis.fit_checkpoint(raw,digest(raw))
        raw=m.checkpoint()
        script='''import sys,json
sys.modules['scipy']=None
from yggdrasil.native_sparse_hypothesis import NativeSparseHypothesis
from yggdrasil.native_context_basis import digest
raw=json.load(sys.stdin).encode('ascii');m=NativeSparseHypothesis.restore(raw,digest(raw))
print(json.dumps([m.predict_provisional(x&7,x>>3) for x in range(16)]))
'''
        p=subprocess.run([sys.executable,'-B','-c',script],input=json.dumps(raw.decode('ascii')),
            text=True,capture_output=True,check=True,timeout=20)
        self.assertEqual(json.loads(p.stdout),[x&1 for x in range(16)])

    def test_checkpoint_join_flags_and_invalid_inputs_fail_closed(self):
        raw=view([x&1 for x in range(16)]);m,_=NativeSparseHypothesis.fit_checkpoint(raw,digest(raw))
        raw=m.checkpoint();self.assertEqual(NativeSparseHypothesis.restore(raw,digest(raw)).checkpoint(),raw)
        for key,value in (('eligible',False),('active_weights',8),('rule','other')):
            d=json.loads(raw);d['info'][key]=value;bad=canonical(d)
            with self.assertRaises(ValueError):NativeSparseHypothesis.restore(bad,digest(bad))
        for c,a in ((True,0),(8,0),(0,True),(0,2)):
            with self.assertRaises(ValueError):m.predict_provisional(c,a)
        with self.assertRaises(ValueError):NativeSparseHypothesis.restore(raw,'0'*64)


if __name__=='__main__':unittest.main()
