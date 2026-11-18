#!/usr/bin/env python3
"""Independent exact-rational audit of ENERGY-19, no imports from experiment.py."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
r = json.loads((ROOT/'scored.json').read_text())
freeze = json.loads((ROOT/'freeze.json').read_text())
checks = 0
for filename, want in freeze['source_sha256'].items():
    assert sha256((ROOT/filename).read_bytes()).hexdigest() == want
    checks += 1
p = r['predeclared_primary']
assert p['expected_action'] == 0 and p['single_witness_action'] == 1 and p['marginalized_energy_action'] == 0;checks+=3
assert p['expected_values'] == ['3/5','9/20'];checks+=1
assert p['best_successful_path_probabilities'] == ['3/10','9/20'];checks+=1
assert p['single_witness_regret'] == '3/20';checks+=1
# Completely separate enumeration with integer count parameters, dividing by 10 at the end.
all_count=0;eligible=0;wrong=0;max_loss=Fraction(0);sum_loss=Fraction(0)
for a,b,c,d in product(range(6), repeat=4):
    all_count += 1
    # p(state)=1/2, p(reward|state) is an integer multiple of 1/5.
    ev0,ev1=Fraction(a+b,10),Fraction(c+d,10)
    success0,success1=max(a,b),max(c,d)
    if ev0==ev1 or success0==success1:
        continue
    eligible+=1
    exact_action = 0 if ev0>ev1 else 1
    witness_action = 0 if success0>success1 else 1
    if exact_action != witness_action:
        wrong+=1
        loss=abs(ev0-ev1)
        max_loss=max(max_loss,loss)
        sum_loss+=loss
    checks+=4
reported = r['grid']
assert all_count == reported['evaluated'] == 1296;checks+=1
assert eligible == reported['strict_decisions'] == 930;checks+=1
assert wrong == reported['wrong_single_witness'] == 60;checks+=1
assert str(max_loss)==reported['max_regret']=='3/10';checks+=1
assert str(sum_loss)==reported['sum_regret']=='42/5';checks+=1
assert reported['marginalized_energy_mismatches']==0;checks+=1
assert r['training']=='NONE' and r['scientific_pass'] is False;checks+=2
out={'gate':'ENERGY-19','result':'PASS_EXACT_MATH','checked_assertions':checks,'worlds_enumerated':all_count,'strict_worlds':eligible,'wrong_witness':wrong,'correct_marginalization':True,'freeze_sha256':freeze['source_sha256'],'scored_sha256':sha256((ROOT/'scored.json').read_bytes()).hexdigest(),'caveat':'Audit was written after scoring; primary experiment and prereg were frozen before score; no scientific first-use.'}
(ROOT/'audit_result.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
print(json.dumps(out))
