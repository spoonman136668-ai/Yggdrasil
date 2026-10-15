"""Y-F50 independent row-level audit of bounded prospective TRAIN-only evidence."""
import json,math,sys
def audit(path,prereg):
 d=json.load(open(path));p=json.load(open(prereg))
 t=p['train'];v=p['diagnostic'];mem=p['memory']
 # Frozen prereg controls plus ONE stronger public-tag-only control added
 # in source before the original run. Auditing its presence is stricter,
 # never an authorization to remove or weaken registered controls.
 declared=p['controls']
 arms=declared[:-1]+['public_tag_only']+[declared[-1]]
 assert len(arms)==len(set(arms))
 assert set(d['scores'])==set(arms)
 assert d['schema']=='yggdrasil.f50.learned-online-retention.trainonly.v1'
 assert d['stage']=='DISJOINT_TRAIN_ONLY_MEMORY_NO_PRIMARY_ORIGINAL'
 assert d['fit_seeds']==t['seeds'] and d['fit_families']==t['families']
 assert d['diagnostic_seeds']==v['seeds'] and d['diagnostic_families']==v['families']
 assert set(d['fit_families']).isdisjoint(d['diagnostic_families'])
 assert d['training_examples']==4096
 assert len(d['rows'])==d['cases']==v['expected_streams']==64
 assert d['events_per_stream']==mem['events_per_stream']==64
 assert d['memory_capacity_edges']==mem['stored_edges_max']==12
 assert d['future_question_hidden_until_retention_complete']
 assert d['proposed_original_seeds_NOT_RESERVED']==p['prospective_original_NOT_RESERVED']['seeds']
 assert len(d['weights'])==6
 assert not d['source_independent_F3'] and not d['original_executed']
 assert not d['native_576_bytes_residency_qualified']
 assert not d['accepted_ref_mutation'] and d['paid_api_calls']==0
 counted={a:0 for a in arms};seen=set()
 for r in d['rows']:
  key=r['seed'],r['family']
  assert key not in seen;seen.add(key)
  assert 511100<=r['seed']<511116 and r['family'] in v['families']
  assert len(r['public_events'])==64
  assert len(r['future_query']['chain'])==3
  assert set(r['results'])==set(arms)
  assert set(r['retained_event_indices'])==set(arms)-{'private_future_query_oracle_unfair'}
  for a,indices in r['retained_event_indices'].items():
   assert len(indices)==12 and len(set(indices))==12
   assert all(isinstance(i,int) and 0<=i<64 for i in indices)
   held=[r['public_events'][i] for i in indices]
   at=r['future_query']['start'];valid=True
   for role,direction in r['future_query']['chain']:
    choice=[e for e in held if e[1]==role and (e[0] if direction==1 else e[2])==at]
    if len(choice)!=1:valid=False;break
    at=choice[0][2] if direction==1 else choice[0][0]
   assert r['results'][a]==int(valid and at==r['truth_answer'])
  assert r['results']['private_future_query_oracle_unfair']==1
  for a in arms:
   assert r['results'][a] in (0,1)
   counted[a]+=r['results'][a]
 assert len(seen)==64
 for a in arms:
  assert d['scores'][a]['correct']==counted[a]
  assert d['scores'][a]['total']==64
  assert math.isclose(d['scores'][a]['accuracy'],counted[a]/64,abs_tol=1e-12)
 for f in v['families']:
  sub=[r for r in d['rows'] if r['family']==f]
  assert len(sub)==16
  for a in arms:
   assert d['by_family'][str(f)][a]==sum(r['results'][a] for r in sub)
 fair=arms[1:-1];best=max(fair,key=lambda a:counted[a])
 gain=(counted['learned_retention']-counted[best])/64
 nonreg=all(d['by_family'][str(f)]['learned_retention']>=max(
   d['by_family'][str(f)][a] for a in fair) for f in v['families'])
 passed=gain>=p['thresholds']['gain_over_strongest_fair'] and nonreg
 assert d['strongest_fair_control']==best
 assert math.isclose(d['candidate_gain'],gain,abs_tol=1e-12)
 assert d['per_family_nondegradation']==nonreg and d['frozen_criterion_met']==passed
 assert d['verdict']==('TRAIN_ONLY_LEARNED_MEMORY_SUPPORTED' if passed else
                       'TRAIN_ONLY_LEARNED_MEMORY_NEGATIVE')
 print('Y_F50',d['verdict'],'correct',counted,'gain',gain,'family_guard',nonreg)
if __name__=='__main__':
 assert len(sys.argv)==3
 audit(sys.argv[1],sys.argv[2])
