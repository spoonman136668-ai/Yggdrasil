"""Read-only independently structured LR-92AB audit; never execute primary runner."""
import collections, hashlib, json, math, pathlib
import numpy as np
from scipy.stats import binom
from scipy.special import logsumexp
P=pathlib.Path(__file__).resolve().parent
r=json.loads((P/'result.json').read_text());p=json.loads((P/'prereg.json').read_text())
prior=np.array(p['memory_input']['prior_distribution'],dtype=float)
uniform=np.ones(16)/16
scrambled=prior[::-1]
tables=np.array([[i>>j&1 for j in range(4)] for i in range(16)],dtype=int)
assert hashlib.sha256((P/'lr92ab_run.py').read_bytes()).hexdigest()==p['code_sha256']==r['source_sha256']
assert hashlib.sha256((P/'prereg.json').read_bytes()).hexdigest()==r['prereg_sha256']
assert hashlib.sha256(prior.tobytes()).hexdigest()==p['memory_input']['prior_float64_sha256']
assert len(r['rows'])==80 and dict(collections.Counter(x['group'] for x in r['rows']))==p['cohort']
assert r['seed']==p['frozen_design']['seeds'][0]
counts=collections.defaultdict(lambda:{'stationary_exact':0,'false_constructions':0,'foreign_null_accept':0,'accepted':0,'accuracy':[]})
field_checks=0
for row in r['rows']:
 s=np.asarray(row['fit_states'],dtype=int); y=np.asarray(row['fit_labels'],dtype=int)
 v=np.asarray(row['valid_states'],dtype=int); z=np.asarray(row['valid_labels'],dtype=int)
 assert len(s)==len(y)==144 and len(v)==len(z)==288
 assert set(s)==set(v)=={0,1,2,3} and set(y)<={0,1} and set(z)<={0,1}
 for n in (36,48,72,96,120,144):
  assert (np.bincount(s[:n],minlength=4)==n//4).all()
 assert (np.bincount(v,minlength=4)==72).all();field_checks+=8
 def independent_log_evidence(pr,xx,yy):
  counts=np.zeros((4,2),dtype=int)
  for state,label in zip(xx,yy):counts[state,label]+=1
  logp=[]
  for i,table in enumerate(tables):
   v=math.log(pr[i]);v+=sum(counts[j,table[j]]*math.log(.65)+counts[j,1-table[j]]*math.log(.35) for j in range(4));logp.append(v)
  return np.array(logp)
 bf=logsumexp(independent_log_evidence(prior,s[:36],y[:36]))-logsumexp(independent_log_evidence(uniform,s[:36],y[:36]))
 assert abs(bf-row['log_bayes_factor_36'])<1e-10
 assert row['gate_used_memory']==(bf>=math.log(2))
 for name,out in row['results'].items():
  chosen=row['choices'][name]
  tab=np.asarray(chosen['table'],dtype=int); assert tab.shape==(4,)
  if name in ('fixed_memory','fixed_uniform','fixed_scrambled','evidence_gate','random_gate'):
   pr={'fixed_memory':prior,'fixed_uniform':uniform,'fixed_scrambled':scrambled,
       'evidence_gate':prior if row['gate_used_memory'] else uniform,
       'random_gate':prior if row['random_used_memory'] else uniform}[name]
   lw=independent_log_evidence(pr,s,y)
   norm=lw-logsumexp(lw);q=np.exp(norm);ix=int(np.argmax(q))
   # Equivalent maximizers can differ at exact floating-point ties.
   recorded=chosen['hypothesis']
   assert lw[recorded] >= np.max(lw)-1e-10
   assert np.array_equal(tables[recorded],tab)
   assert abs(q[recorded]-chosen['posterior'])<1e-9
   field_checks+=3
  wrong=int(np.count_nonzero(tab[v]!=z))
  vp=float(binom.sf(wrong-1,len(v),.35))
  accepted=(chosen['posterior'] is None or chosen['posterior']>=.9) and vp>.01
  exact=row['group']=='stationary' and accepted and np.array_equal(tab,tables[row['truth_table']])
  assert abs(vp-out['validation_p'])<1e-10
  assert out['accepted']==accepted and out['exact']==exact and out['false']==(accepted and not exact)
  acc=float(np.mean(tab[v]==z));assert abs(out['validation_accuracy']-acc)<1e-12
  c=counts[name];c['stationary_exact']+=exact;c['false_constructions']+=accepted and not exact;c['accepted']+=accepted
  c['foreign_null_accept']+=accepted and row['group'] in ('foreign','null');c['accuracy'].append(acc)
  field_checks+=6
for name,c in counts.items():
 s=r['summary'][name]
 for metric in ('stationary_exact','false_constructions','foreign_null_accept','accepted'):assert c[metric]==s[metric]
 assert abs(float(np.mean(c['accuracy']))-s['validation_accuracy'])<1e-12
 assert s['n_fit']==11520 and s['n_validation']==23040
 field_checks+=6
c=r['summary'];g=c['evidence_gate'];u=c['fixed_uniform'];m=c['fixed_memory'];rand=c['random_gate']
recomputed={'gate_exact_ge_uniform_plus_3':g['stationary_exact']>=u['stationary_exact']+3,
'gate_exact_ge_memory':g['stationary_exact']>=m['stationary_exact'],
'gate_false_le_uniform':g['false_constructions']<=u['false_constructions'],
'gate_foreign_null_accept_zero':g['foreign_null_accept']==0,
'gate_exact_gt_random':g['stationary_exact']>rand['stationary_exact'],
'gate_validation_accuracy_ge_uniform':g['validation_accuracy']>=u['validation_accuracy']}
assert recomputed==r['go_checks'] and r['development_go']==all(recomputed.values())
assert r['gate_uses_memory_count']==sum(row['gate_used_memory'] for row in r['rows'])
a={'schema':'lr92ab.readonly-independent-audit.v1','status':'PASS','field_checks':field_checks,'primary_result_sha256':hashlib.sha256((P/'result.json').read_bytes()).hexdigest(),
'prereg_sha256':r['prereg_sha256'],'runner_sha256':r['source_sha256'],'decision':'DEVELOPMENT_NO_GO' if not r['development_go'] else 'DEVELOPMENT_GO',
'unmatched_control_warning':'Conventional controls do not have Bayesian posterior acceptance thresholds; comparisons descriptive only.',
'official_science':'UNVERIFIED','native_training':False,'first_use_reserved_consumed':0}
(P/'audit.json').write_text(json.dumps(a,sort_keys=True,indent=2)+'\n')
print(json.dumps(a,indent=2))
