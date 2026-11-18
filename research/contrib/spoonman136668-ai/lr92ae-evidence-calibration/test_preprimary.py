"""Focused structural tests only; never generate or score frozen evaluation seeds."""
import hashlib, json
from pathlib import Path
import numpy as np
from lr92ae_run import block_actions, bin_ece, eval_arm, future_world, BUDGETS
import lr92ad_run as prev

P=Path(__file__).resolve().parent

def test_parent_exact_identity():
    assert hashlib.sha256((P/'lr92ad_run.py').read_bytes()).hexdigest() == '32171291d945f7aedca941890b4137caef648a455bbb34a9c2478e3e36087b47'

def test_block_balance():
    a=block_actions(np.random.default_rng(2),1,256)
    for n in BUDGETS:
        assert all(np.bincount(a[:n,1],minlength=4)==n//4)
        assert all(a[:n,0]==1)

def test_world_structural_local_not_primary_seed():
    w=future_world(np.random.default_rng(3),0)
    assert len(w['fit0'])==112 and len(w['fit1'])==256 and len(w['valid'])==256
    assert len(w['truth'])==8 and w['base_id']>=8
    assert len(w['fit1_y'])==256 and len(w['fit0_y'])==112

def test_ece_perfect():
    e,b=bin_ece([(1,1)]*4 + [(0,0)]*4)
    assert e==0 and sum(t['n'] for t in b)==8

def test_ece_miss():
    e,b=bin_ece([(.9,0)]*5)
    assert abs(e-.9)<1e-12

def test_acceptance_uses_fitting_only():
    fit=np.array([[0,i%4] for i in range(40)])
    truth=np.zeros(8,dtype=np.uint8)
    table=truth.copy()
    valid=np.array([[1,i%4] for i in range(32)])
    a=eval_arm(table,.999,fit,np.zeros(40,dtype=np.uint8),valid,np.zeros(32,dtype=np.uint8),truth)
    b=eval_arm(table,.999,fit,np.zeros(40,dtype=np.uint8),valid,np.ones(32,dtype=np.uint8),truth)
    assert a['accepted']==b['accepted'] and a['fit_misfit_p']==b['fit_misfit_p']
    assert a['exact_accepted']==b['exact_accepted']
    assert a['correct_validation']!=b['correct_validation']

def test_no_primary_output():
    assert not (P/'primary_result.json').exists()
