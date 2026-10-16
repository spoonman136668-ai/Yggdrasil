"""F67A question-blind public-graph junction teacher; SYNTHETIC ONLY.

Unlike the F66B path-length scalar teacher, this identifies genuine
9+9 corridor junction edges from the full public graph for offline
training labels. Online decisions remain the exact frozen F67A policy.
"""
from __future__ import annotations
import hashlib,importlib.util,json,math,pathlib,sys
from collections import defaultdict
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 data=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
assert blob(P/"train_method_precode.json")=="31a50ef4976b20e59416f00b3364f350bfa7f371"
assert blob(P/"causal_memory.py")=="b370396b3c3571be2c01ab2b33effef14f248eef"
spec=importlib.util.spec_from_file_location("f67a_immutable_causal_memory",P/"causal_memory.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
def full_public_bridge_edges(public):
 assert len(public)==72 and len(set(public))==72
 graph=defaultdict(list)
 for i,(a,_r,b) in enumerate(public):
  graph[a].append((b,i));graph[b].append((a,i))
 result=[]
 visited=set()
 for root in graph:
  if root in visited:continue
  todo=[root];component={root};indices=set()
  while todo:
   u=todo.pop()
   for v,i in graph[u]:
    indices.add(i)
    if v not in component:component.add(v);todo.append(v)
  visited.update(component)
  if (len(component),len(indices))!=(18,17):continue
  for edge_i in indices:
   a,_role,b=public[edge_i]
   reachable={a};queue=[a]
   while queue:
    node=queue.pop()
    for nxt,j in graph[node]:
     if j==edge_i:continue
     if nxt not in reachable:reachable.add(nxt);queue.append(nxt)
   if b not in reachable and len(reachable)==9 and len(component-reachable)==9:
    result.append(tuple(public[edge_i]))
 assert len(result)==2,("PUBLIC_9X9_JUNCTION_SOURCE_INVALID",len(result))
 return frozenset(result)
def utility(records,bridge_public_edges,future):
 bridge_records={m.PACK.edge_record(edge) for edge in bridge_public_edges}
 ends={node for a,b,_codes in records for node in (a,b)}
 incidence={}
 for a,_role,b in future:
  incidence[a]=incidence.get(a,0)+1;incidence[b]=incidence.get(b,0)+1
 hops=sum(min(len(rec[2]),4)**2 for rec in records)
 true_bridge=sum(int(rec in bridge_records) for rec in records)
 attachment=sum(incidence.get(n,0) for n in ends)
 singleton=sum(int(len(rec[2])==1) for rec in records)
 return .4*hops/16+2.0*true_bridge+.5*attachment/24-.1*singleton/12
def train_case(public):
 known=full_public_bridge_edges(public)
 labels=[]
 baseline=()
 for i,event in enumerate(public):
  options=m.ACTION.actions(baseline,event,i,m.PACK)
  f60=m.ACTION._f60_step(baseline,event,m.PACK)
  baseline_features=None
  for action,_old,drop,after,_old_features in options:
   if after==f60:
    baseline_features=m.features(baseline,event,i,action,drop,after)
    break
  assert baseline_features is not None
  u0=utility(f60,known,public[i+1:])
  for action,_old,drop,after,_orig in options:
   if after==f60:continue
   feat=m.features(baseline,event,i,action,drop,after)
   diff=tuple(f-b for f,b in zip(feat,baseline_features))
   label=max(-1,min(1,utility(after,known,public[i+1:])-u0))
   if any(abs(x)>1e-10 for x in diff):
    labels.append((diff,label))
  baseline=f60
 return labels,known
def train(publics):
 samples=[];positive=negative=0;positive_bridge_labels=0
 for public in publics:
  case,bridges=train_case(public)
  samples.extend(case)
  positive+=sum(int(y>1e-8) for _x,y in case)
  negative+=sum(int(y< -1e-8) for _x,y in case)
  positive_bridge_labels+=len(bridges)
 assert positive>0 and negative>0 and positive_bridge_labels==2*len(publics),"F67A_STRUCTURAL_TEACHER_NO_SIGNAL"
 w=[0.0]*m.PARAMS
 for _ in range(3):
  for x,y in samples:
   pred=math.tanh(sum(wi*xi for wi,xi in zip(w,x)))
   error=y-pred
   for j,v in enumerate(x):
    w[j]+=.02*error*v
 result=tuple(max(-127,min(127,round(v*16))) for v in w)
 return result,dict(total_examples=len(samples),positive_credit=positive,
   negative_credit=negative,true_junction_edges=positive_bridge_labels)
def synthetic_smoke():
 training=[]
 for k in range(8):
  public,q,_meta=m.SOURCE.source(-2501-k,(-2,-1)[k%2])
  training.append(public)
 weights,counts=train(training)
 checks=[]
 for k in range(8):
  seed=-2511-k;family=(-2,-1)[k%2]
  public,q,meta=m.SOURCE.source(seed,family)
  junctions=full_public_bridge_edges(public)
  fitted,trace,activity=m.online(public,weights,True,True)
  disabled,trace_ab,act_ab=m.online(public,weights,True,False)
  assert m.AUDITOR.verify(public,q,trace)["prefixes"]==72
  assert m.AUDITOR.verify(public,q,trace_ab)["prefixes"]==72
  bridges={m.PACK.edge_record(edge) for edge in junctions}
  retention=sum(int(record in bridges) for record in fitted)
  control_retention=sum(int(record in bridges) for record in disabled)
  checks.append(dict(seed=seed,kind=meta["question_type"],
    chosen_merges=activity["chosen_merges"],
    true_junction_edges_retained=retention,
    ablation_junction_edges_retained=control_retention,
    learned_correct=int(m.PACK.solve(fitted,q)==q["answer"]),
    ablation_correct=int(m.PACK.solve(disabled,q)==q["answer"])))
 totals=dict(
  merges=sum(c["chosen_merges"] for c in checks),
  preserved_true_junctions=sum(c["true_junction_edges_retained"] for c in checks),
  ablation_preserved_junctions=sum(c["ablation_junction_edges_retained"] for c in checks),
  correct=sum(c["learned_correct"] for c in checks),
  ablation_correct=sum(c["ablation_correct"] for c in checks))
 passed=bool(totals["merges"]>0 and totals["preserved_true_junctions"]>0 and
   (totals["correct"]>totals["ablation_correct"] or
    totals["preserved_true_junctions"]>totals["ablation_preserved_junctions"]))
 out=dict(schema="yggdrasil.f67a.structural-supervision.synthetic.v1",
   stage="SYNTHETIC_ONLY",train_cases=8,independent_guards=8,
   int8_provisional_weights=list(weights),counts=counts,observed=totals,
   prefit_model_qualification_pass=passed,
   scientific_superiority_qualified=False,
   fit_train_executed=False,validation_executed=False,diagnostic_executed=False,
   original_executed=False,F3=False,optimizer_promotion=False,
   independent_causal_trace_pass=True,checks=checks)
 print(json.dumps(out,sort_keys=True))
 if not passed:raise AssertionError("F67A_LEARNED_STRUCTURAL_JUNCTION_SYNTHETIC_GATE_BLOCKED")
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 synthetic_smoke()
