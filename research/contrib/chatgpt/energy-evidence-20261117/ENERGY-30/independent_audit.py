#!/usr/bin/env python3
"""Independent ENERGY-30 audit: regenerate source truths and posterior decisions.

This script does not import experiment.py or parent_source_energy29.py.
A subset of strata receives an independent exact-integer posterior certificate;
all 720 cases receive independent source + posterior + fitted-control checks.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier

HERE=Path(__file__).resolve().parent
R=json.loads((HERE/'scored.json').read_text())
PROTOCOL=json.loads((HERE/'protocol.json').read_text())
FREEZE=json.loads((HERE/'freeze.json').read_text())
sha=lambda path: hashlib.sha256((HERE/path).read_bytes()).hexdigest()
assert sha('experiment.py')==FREEZE['source_sha256']
assert sha('protocol.json')==FREEZE['protocol_sha256']
assert sha('parent_source_energy29.py')==FREEZE['parent_dependency_sha256']
assert R['mode']=='scored' and R['schema']=='yggdrasil.energy30.novelty-versus-noise.v1'
assert R['source_dependency_sha256']==FREEZE['parent_dependency_sha256']
assert PROTOCOL['worlds']==len(R['cases'])==720
assert R['native_checkpoint_tested'] is False and R['deployment']=='NONE'

COUNTS=defaultdict(int)
def assert_check(val,label):
    COUNTS['checks']+=1
    if not val:raise AssertionError(label)

def h(text):return int.from_bytes(hashlib.sha256(text.encode('ascii')).digest(),'big')

N=6;M=(1<<64)-1
supports=[sum(1<<i for i in terms) for d in (1,2,3) for terms in combinations(range(N),d)]
assert len(supports)==41
terms={b:sum(1<<a for a in range(64) if (a&b)==b) for b in supports}
old=[]
for t in combinations(range(6),3):
   triple=sum(1<<k for k in t)
   rest=[i for i in range(6) if i not in t]
   for sign in (0,1):
      for correction in (None,*combinations(rest,2)):
        s=0
        for act in range(64):
            bit=((act&triple).bit_count()&1)^sign
            if correction is not None: bit^=int(all(act&(1<<k) for k in correction))
            s|=bit<<act
        old.append(s)
assert len(old)==160 and len(set(old))==160

all_masks=[];prior=[];degrees=[]
tiers=[1,12,27,60]
for d in range(4):
  for parts in combinations(supports,d):
    m=0
    for p in parts:m^=terms[p]
    all_masks.extend([m,m^M]);degrees.extend([d,d]);prior.extend([tiers[d]/(100*2*math.comb(41,d))]*2)
assert len(all_masks)==23044
Old=np.asarray(old,dtype=np.uint64); All=np.asarray(all_masks,dtype=np.uint64)
OP=np.ones(len(old),dtype=np.float64)/len(old)
NP=np.asarray(prior,dtype=np.float64)
assert abs(float(NP.sum())-1)<1e-12
Bits=np.asarray([[(a>>i)&1 for i in range(6)] for a in range(64)],dtype=np.int8)
X=np.asarray([[(a&p)==p for p in supports] for a in range(64)],dtype=np.float64)


def original_truth(seed,family,index):
  if family=='old':return old[h(f'energy29/oldchoice/{seed}/{index}')%len(old)]
  if family=='novel_in_basis':
    ordered=sorted(supports,key=lambda s:h(f'energy29/newlaw-v1/{seed}/{index}/{s}'))
    for q in range(17):
      ss=ordered[q:q+3]
      if len(ss)!=3:continue
      if not any(x.bit_count()==3 for x in ss):continue
      if not any(x.bit_count()==2 for x in ss):continue
      bits=terms[ss[0]]^terms[ss[1]]^terms[ss[2]]
      if h(f'energy29/newsig-v1/{seed}/{index}')&1:bits^=M
      if bits in old:continue
      return bits
    raise AssertionError('UNSAT_SOURCE_NOVEL')
  variables=sorted(range(6),key=lambda k:h(f'energy29/outsidevar/{seed}/{index}/{k}'))
  if index%2:
    chosen=variables[:5]
    bits=sum(int(sum((a>>v)&1 for v in chosen)>=3)<<a for a in range(64))
  else:
    four=sum(1<<j for j in variables[:4]);two=sum(1<<j for j in variables[4:])
    quartic=sum(int((a&four)==four)<<a for a in range(64))
    bits=quartic^terms[two]^sum(((a>>variables[0])&1)<<a for a in range(64))
  if h(f'energy29/outside_sign/{seed}/{index}')&1:bits^=M
  return bits


def weights(bank,prior,seen,observed):
  diff=np.bitwise_count((bank^np.uint64(observed))&np.uint64(seen)).astype(np.int16)
  w=prior*np.power(3.0,-diff.astype(np.float64))
  return w,float(np.sum(w,dtype=np.float64)),int(np.min(diff))


def choose(bank,w,total,a):
  pm=float(w[(bank & np.uint64(1<<a))!=0].sum(dtype=np.float64))/total
  return int(pm>0.5),pm

# Exact integer posterior over every hypothesis for a case using a common
# denominator for all structural priors; this avoids *any* floating arithmetic.
DEN=math.lcm(160,*(100*2*math.comb(41,k) for k in range(4)))
PRIOR_OLD=DEN//160
PRIOR_NEW=[tiers[d]*DEN//(100*2*math.comb(41,d)) for d in degrees]
assert sum(PRIOR_NEW)==DEN

def cert_case(case,observed,seen12,seen24):
  certificates={}
  for phase,seen in ((12,seen12),(24,seen24)):
    o=[PRIOR_OLD*3**(phase-((m^observed)&seen).bit_count()) for m in old]
    n=[p*3**(phase-((m^observed)&seen).bit_count()) for p,m in zip(PRIOR_NEW,all_masks)]
    so,sn=sum(o),sum(n)
    posterior=Fraction(sn,7*so+sn)
    key='posterior_novel_'+str(phase)
    assert_check(abs(float(posterior)-case[key])<1e-12,'EXACT_POSTERIOR_'+key)
    certificates[phase]=(o,n,so,sn)
  o,n,so,sn=certificates[24]
  for pos,a in enumerate(case['held_actions']):
    on_o=sum(weight for m,weight in zip(old,o) if m&(1<<a))
    on_n=sum(weight for m,weight in zip(all_masks,n) if m&(1<<a))
    assert_check(int(on_o*2>so)==case['predictions']['old_bayes'][pos],'EXACT_OLD_PRED')
    assert_check(int(on_n*2>sn)==case['predictions']['full_anf_bayes'][pos],'EXACT_FULL_PRED')
    assert_check(int(2*(7*on_o+on_n)>7*so+sn)==case['predictions']['soft_mixture'][pos],'EXACT_MIX_PRED')
  COUNTS['exact_integer_case_certificates']+=1

seen_cases=set();first_by_stratum=set();all_records=[];near_zero=defaultdict(int)
for case in R['cases']:
  seed=case['seed'];family=case['family'];index=case['world_index'];corr=case['corruption']
  key=(seed,family,index,corr)
  assert_check(key not in seen_cases,'DUPLICATED_CASE');seen_cases.add(key)
  assert_check(seed in PROTOCOL['seeds'] and family in PROTOCOL['families'] and corr in PROTOCOL['corrupted_training_labels'],'BAD_COHORT')
  truth=original_truth(seed,family,index)
  assert_check(int(case['truth_mask'],16)==truth,'SOURCE_TRUTH')
  order=sorted(range(64),key=lambda a:h(f'energy30/split/{seed}/{family}/{index}/{corr}/{a}'))
  train=order[:24];held=order[24:48];unused=order[48:]
  assert_check(len(set(order))==64 and not(set(train)&set(held)),'SOURCE_SPLIT')
  assert_check(case['train_actions']==train and case['held_actions']==held,'WRONG_SOURCE_SPLIT')
  flips=sorted(range(24),key=lambda i:h(f'energy30/flip/{seed}/{family}/{index}/{corr}/{i}'))[:corr]
  assert_check(case['flipped_positions']==flips,'CORRUPTION_INDICES')
  observed=truth
  for i in flips:observed^=1<<train[i]
  assert_check(case['observed_train']==[(observed>>a)&1 for a in train],'PUBLIC_TRAIN_OBS')
  expected_held=[(truth>>a)&1 for a in held]
  assert_check(case['held_truth']==expected_held,'HELD_TRUTH')
  seen12=sum(1<<a for a in train[:12]);seen24=sum(1<<a for a in train)
  old12,zold12,m12=weights(Old,OP,seen12,observed)
  full12,zfull12,_=weights(All,NP,seen12,observed)
  old24,zold24,m24=weights(Old,OP,seen24,observed)
  full24,zfull24,_=weights(All,NP,seen24,observed)
  assert_check(case['min_old_mismatch12']==m12 and case['min_old_mismatch24']==m24,'MIN_MISMATCH')
  p12=zfull12/(7*zold12+zfull12);p24=zfull24/(7*zold24+zfull24)
  assert_check(abs(p12-case['posterior_novel_12'])<1e-12 and abs(p24-case['posterior_novel_24'])<1e-12,'POSTERIOR_ODDS')
  born_mismatch=m12>=2 or m24>=3
  born_evidence=p12>=0.5 or p24>=0.5
  assert_check(case['birth_mismatch']==born_mismatch and case['birth_evidence']==born_evidence,'BIRTH_GATE')
  for pos,a in enumerate(held):
    pred_o,pm_o=choose(Old,old24,zold24,a)
    pred_f,pm_f=choose(All,full24,zfull24,a)
    conditional=(7*zold24*pm_o+zfull24*pm_f)/(7*zold24+zfull24)
    assert_check(pred_o==case['predictions']['old_bayes'][pos],'OLD_RECON')
    assert_check(pred_f==case['predictions']['full_anf_bayes'][pos],'FULL_RECON')
    assert_check(int(conditional>0.5)==case['predictions']['soft_mixture'][pos],'MIX_RECON')
    assert_check((pred_f if born_mismatch else pred_o)==case['predictions']['mismatch_gate'][pos],'MISMATCH_RECON')
    assert_check((pred_f if born_evidence else pred_o)==case['predictions']['evidence_gate'][pos],'EVIDENCE_RECON')
    if min(abs(pm_o-.5),abs(pm_f-.5),abs(conditional-.5))<1e-9:near_zero['probability']+=1
  labels=np.asarray([((observed>>a)&1)*2-1 for a in train],dtype=np.float64)
  # Independent augmented least squares, instead of scorer's normal equations.
  ft=X[train,:]
  mat=np.vstack([ft,np.eye(ft.shape[1])])
  target=np.concatenate([labels,np.zeros(ft.shape[1])])
  coeff=np.linalg.lstsq(mat,target,rcond=None)[0]
  ridge_scores=X[held,:]@coeff
  for pos,score in enumerate(ridge_scores):
    predicted=int(score>0)
    if predicted!=case['predictions']['conventional_ridge'][pos]:
      assert_check(abs(score)<=1e-8,'MATERIAL_RIDGE_MISMATCH')
      near_zero['ridge_ties']+=1
    else:COUNTS['checks']+=1
    if abs(score)<1e-8:near_zero['ridge_small_margin']+=1
  y=np.asarray([(observed>>a)&1 for a in train],dtype=np.int8)
  tree=DecisionTreeClassifier(max_depth=6,min_samples_leaf=1,random_state=seed)
  tree.fit(Bits[train],y)
  predicted=list(map(int,tree.predict(Bits[held])))
  assert_check(case['predictions']['conventional_tree']==predicted,'TREE_REFIT')
  forest_seed=h(f'energy30/forest/{seed}/{family}/{index}/{corr}')%(2**32)
  forest=ExtraTreesClassifier(n_estimators=31,max_depth=6,min_samples_leaf=1,max_features=None,
       bootstrap=False,n_jobs=1,random_state=forest_seed)
  forest.fit(Bits[train],y)
  predicted=list(map(int,forest.predict(Bits[held])))
  assert_check(case['predictions']['conventional_forest']==predicted,'FOREST_REFIT')
  for arm,preds in case['predictions'].items():
    assert_check(len(preds)==24 and all(type(v)==int and v in (0,1) for v in preds),'OUTPUT_BITS')
    assert_check(case['correct'][arm]==sum(int(x==t) for x,t in zip(preds,expected_held)),'CASE_SCORE')
    COUNTS['prediction_comparisons']+=24
  stratum=(family,corr)
  if stratum not in first_by_stratum:
    first_by_stratum.add(stratum)
    cert_case(case,observed,seen12,seen24)
  all_records.append(case)

assert_check(len(seen_cases)==720 and len(first_by_stratum)==9,'FULL_COVERAGE')
for family in PROTOCOL['families']:
 for corr in PROTOCOL['corrupted_training_labels']:
    name=f'{family}/noise{corr}'
    rows=[c for c in all_records if c['family']==family and c['corruption']==corr]
    recorded=R['summary']['strata'][name]
    assert_check(len(rows)==recorded['cases']==80 and recorded['held_per_arm']==1920,'AGG_COVERAGE')
    for a in ARMS if False else ('old_bayes','mismatch_gate','evidence_gate','soft_mixture','full_anf_bayes','conventional_ridge','conventional_forest','conventional_tree'):
      assert_check(sum(x['correct'][a] for x in rows)==recorded['correct'][a],'AGG_SCORE')
    assert_check(sum(x['birth_mismatch'] for x in rows)==recorded['birth_mismatch'],'AGG_MISMATCH_BIRTH')
    assert_check(sum(x['birth_evidence'] for x in rows)==recorded['birth_evidence'],'AGG_EVIDENCE_BIRTH')

out={'schema':'energy30.independent-audit.v1','status':'PASS' if not near_zero['ridge_ties'] else 'PASS_WITH_ZERO_MARGIN_WARNING',
 'checks':COUNTS['checks'],'prediction_comparisons':COUNTS['prediction_comparisons'],
 'exact_integer_case_certificates':COUNTS['exact_integer_case_certificates'],'source_cases':len(seen_cases),
 'near_zero':dict(near_zero),'frozen_sha256':FREEZE['source_sha256'],
 'scored_sha256':sha('scored.json'),'scientific_pass':False,'deployment':'NONE'}
(HERE/'audit_result.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
