#!/usr/bin/env python3
"""ENERGY-27 independent exact posterior/action reconstruction.

Written after frozen scoring. Does not import experiment.py. Derives hypothesis
posterior with exact fractions; score implementation used floating log weights.
"""
import hashlib,itertools,json,math
from fractions import Fraction as Q
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
j=json.loads((HERE/'scored.json').read_text());protocol=json.loads((HERE/'protocol.json').read_text());freeze=json.loads((HERE/'freeze.json').read_text())
for n,k in [('experiment.py','source_sha256'),('protocol.json','protocol_sha256')]:
 assert hashlib.sha256((HERE/n).read_bytes()).hexdigest()==freeze[k],f'{n} drift'
assert j['source_sha256']==freeze['source_sha256']
assert j['classification']=='DEVELOPMENT_NO_GO' and not j['scientific_pass'] and not j['native_checkpoint_executed']
assert len(j['cases'])==720 and j['seeds']==protocol['primary_seeds'] and protocol['training_budget']==6
A=list(itertools.product((0,1),repeat=5));H=[(a,s) for a in itertools.combinations(range(5),3) for s in (0,1)]
truth=[[((sum(x[k] for k in parents)%2)^sign) for x in A] for parents,sign in H]
assert len(H)==20 and len(A)==32

def dig(*items):return hashlib.sha256('/'.join(map(str,items)).encode('ascii')).digest()

def rate(x,regime):
 if regime=='homogeneous':return Q(1,10)
 return Q(1,50) if A[x][0]==0 else Q(7,20)

def hb(p):
 p=float(p)
 return 0 if p in (0,1) else -p*math.log2(p)-(1-p)*math.log2(1-p)

def action_choice(w,remain,regime,method,seed,hidden,t):
 if method=='uniform_random':return remain[int.from_bytes(dig('energy27/random-v2',seed,regime,t)[:8],'big')%len(remain)]
 ranked=[]
 for x in remain:
  e=rate(x,regime); q=sum((weight*truth[h][x] for h,weight in enumerate(w)),Q(0))
  mu=e+(1-2*e)*q
  variance=(1-2*e)**2*q*(1-q)
  mutual=hb(mu)-hb(e)
  ranked.append((x,float(variance) if method=='variance' else mutual,abs(float(mu)-.5)))
 best=max(row[1] for row in ranked)
 candidates=[row for row in ranked if row[1]>=best-1e-12]
 nearest=min(row[2] for row in candidates)
 return min(row[0] for row in candidates if row[2]<=nearest+1e-12)

counts={a:0 for a in ('variance','information_gain','uniform_random')}
regimes=protocol['regimes'].keys();totals={regime:{arm:{'correct':0,'identified':0,'map':0,'ridge':0,'brier_sum':0.0,'cases':0} for arm in counts} for regime in regimes}
audit_checks=0
tie_diagnostics={regime:{arm:{'exact_held_ties':0,'source_score_correct':0,'exact_choose_zero_correct':0,'exact_choose_zero_map':0,'source_map_ties':0,'ridge_near_ties':0,'min_possible_correct':0,'max_possible_correct':0} for arm in counts} for regime in regimes}
all_selection_gaps=[]
cubic_features=[]
for x in A:
 row=[1.0]+[2*b-1 for b in x]
 row.extend(math.prod(2*x[k]-1 for k in combo) for combo in itertools.combinations(range(5),3))
 cubic_features.append(row)
features=np.asarray(cubic_features,dtype=float)
for c in j['cases']:
 seed=int(c['seed']);rule=int(c['hidden_rule']);regime=c['regime'];arm=c['arm'];
 assert seed in freeze['primary_seeds'] and rule in range(20) and regime in regimes and arm in counts
 held=sorted(range(32),key=lambda x:dig('energy27/holdout-v1',seed,x))[:8]
 assert held==c['held_actions'] and len(c['observations'])==6
 remain=sorted(set(range(32))-set(held))
 w=[Q(1,20)]*20
 xs=[];ys=[]
 for t,obs in enumerate(c['observations']):
  x=int(obs['action']); y=int(obs['observed_y']);e=rate(x,regime)
  assert obs['step']==t and x in remain and y in (0,1)
  assert abs(float(e)-obs['noise_rate'])<1e-15
  selected=action_choice(w,remain,regime,arm,seed,rule,t)
  assert selected==x, f'action mismatch {seed}/{rule}/{regime}/{arm}/{t}: {selected} != {x}'
  u=int.from_bytes(dig('energy27/noise-v1',seed,rule,regime,t)[:8],'big')
  actual=truth[rule][x]^(u*e.denominator < (1<<64)*e.numerator)
  assert actual==y, 'source outcome mismatch'
  probs=[(1-e) if truth[h][x]==y else e for h in range(20)]
  w=[a*b for a,b in zip(w,probs)]; norm=sum(w);w=[a/norm for a in w]
  xs.append(x);ys.append(y);remain.remove(x)
  audit_checks+=6
 preds=[sum((w[h]*truth[h][x] for h in range(20)),Q(0)) for x in held]
 original_probs=c['held_soft_prob']
 assert all(abs(float(x)-z)<2e-12 for x,z in zip(preds,original_probs)), 'posterior predictive drift'
 assert all(abs(float(x)-z)<2e-12 for x,z in zip(w,c['posterior'])), 'exact posterior drift'
 targets=[truth[rule][x] for x in held]
 assert targets==c['held_truth']
 exact_ties=[i for i,p in enumerate(preds) if p==Q(1,2)]
 definite_correct=sum(int(p>Q(1,2))==y for p,y in zip(preds,targets) if p!=Q(1,2))
 correct=definite_correct+sum(targets[i]==0 for i in exact_ties)
 assert correct==c['correct'], 'stable exact tie policy mismatch'
 dia=tie_diagnostics[regime][arm]
 dia['exact_held_ties']+=len(exact_ties)
 dia['source_score_correct']+=c['correct']
 dia['exact_choose_zero_correct']+=correct
 dia['min_possible_correct']+=definite_correct
 dia['max_possible_correct']+=definite_correct+len(exact_ties)
 # Floating scorer may break exact posterior ties in MAP selection.
 champion=int(c['identified_rule'])
 top=max(w)
 assert w[champion]==top, 'scorer selected suboptimal model'
 assert champion==next(h for h in range(20) if w[h]==top), 'stable MAP tie selection mismatch'
 dia['source_map_ties']+=int(sum(q==top for q in w)>1)
 mapcorrect=sum(truth[champion][x]==y for x,y in zip(held,targets))
 assert mapcorrect==c['map_correct']
 assert int(champion==rule)==c['true_rule_identified']
 loss=sum((p-t)**2 for p,t in zip(preds,targets))/8
 assert abs(float(loss)-c['brier'])<1e-12
 # Fit the conventional baseline by independent augmented least-squares instead
 # of the scored normal-equation solver. Soft scores must match except roundoff.
 F=features[xs];Y=2*np.asarray(ys,dtype=float)-1
 F_aug=np.concatenate([F, np.sqrt(.25)*np.eye(16)],axis=0)
 Y_aug=np.concatenate([Y,np.zeros(16)],axis=0)
 beta=np.linalg.lstsq(F_aug,Y_aug,rcond=None)[0]
 ridge=np.clip((features[held]@beta+1)/2,0,1)
 assert np.max(abs(ridge-np.array(c['held_ridge_prob'])))<2e-10, 'ridge cross-solver drift'
 ridgecorrect=sum(int(z>0.5+1e-12)==y for z,y in zip(ridge,targets))
 assert ridgecorrect==c['ridge_correct'], 'ridge refit accuracy mismatch'
 dia['ridge_near_ties']+=int(np.min(np.abs(ridge-.5))<=1e-10)
 totals[regime][arm]['correct']+=c['correct']
 totals[regime][arm]['identified']+=champion==rule
 totals[regime][arm]['map']+=mapcorrect
 totals[regime][arm]['ridge']+=c['ridge_correct']
 totals[regime][arm]['brier_sum']+=float(loss)
 totals[regime][arm]['cases']+=1
 counts[arm]+=1;audit_checks+=36

for regime in regimes:
 for arm in counts:
  scored=j['totals'][regime][arm];t=totals[regime][arm]
  assert t['correct']==scored['held_correct']
  assert t['identified']==scored['true_rule_identified']
  assert t['map']==scored['map_correct']
  assert t['ridge']==scored['ridge_correct']
  assert abs(t['brier_sum']/t['cases']-scored['mean_brier'])<1e-12
  assert t['cases']*8==scored['held_total']
  audit_checks+=6
assert all(n==240 for n in counts.values())
# Source-grounded impossibility: with homogeneous symmetric noise, mutual
# information is H_b(e+(1-2e)*q)-H_b(e), and disagreement variance is
# (1-2e)^2*q*(1-q). Both have the same maxima over q in [0,1].
for denom in (8,16,32):
 for i in range(denom+1):
  q=Q(i,denom);e=Q(1,10);m=e+(1-2*e)*q
  v=(1-2*e)**2*q*(1-q)
  assert v>=0 and hb(m)-hb(e)>=-1e-12
  audit_checks+=1
assert j['homogeneous_variance_and_eig_action_sequence_matches']==120
assert j['heterogeneous_action_sequence_disagreements']==0
assert j['heterogeneous_gain']==0
assert j['frozen_gate_pass'] is False
result={'schema':'energy27.independent-audit.v1','status':'PASS','checks':audit_checks,
        'source_sha256':freeze['source_sha256'],'protocol_sha256':freeze['protocol_sha256'],
        'worlds':240,'case_records':len(j['cases']),'witnessed_interventions':len(j['cases'])*6,
        'held_source_truths':len(j['cases'])*8,'posterior_method':'exact rational product then normalization',
        'source_method':'independent SHA256 outcomes and rule enumeration',
        'conventional_control':'augmented least squares independent of scorer normal equations',
        'homogeneous_paired_action_sequences':120,'heterogeneous_paired_action_sequences':120,
        'tie_diagnostics':tie_diagnostics,'information_gain_improvement':0,'scientific_pass':False,'deployment':'NONE'}
(HERE/'audit_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
