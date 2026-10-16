"""F63B synthetic-only source feasibility with frozen online controls."""
import importlib.util,pathlib,json,sys
P=pathlib.Path(__file__).resolve().parent
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
src=load("f63b_structural_source",P/"feasible_braid_source.py")
f=load("f63b_frozen_controls",P.parent/"20261015-y-f62"/"source_pilot.py")
f60,f59,f58,f61=f.controls()
packing=f.codec()
def witness(edges,question):
 states={question["start"]}
 for role,direction in question["ops"]:
  nxt=set()
  for a,r,b in edges:
   if r==role:
    start,end=(a,b) if direction==1 else (b,a)
    if start in states:nxt.add(end)
  states=nxt
 return states=={question["answer"]}
rows=[]
for i in range(16):
 seed=-301-i
 fam=(-2,-1)[i%2]
 public,q,regime=src.source(seed,fam)
 assert len(public)==72 and len(set(public))==72
 independent=witness(public,q)
 control={
  "F60":f60.online_fixed(public),
  "F59":f59.fixed_deferred_component_buffer(public),
  "F58":f58.frontier_online(public),
  "F61":f61.learned_online(public,f.F61_WEIGHTS)[0]}
 scores={k:int(packing.solve(v,q)==q["answer"]) for k,v in control.items()}
 rows.append(dict(seed=seed,family=fam,witness=int(independent),scores=scores,regime=regime))
f60_correct=sum(r["scores"]["F60"] for r in rows)
witness_correct=sum(r["witness"] for r in rows)
print(json.dumps(dict(schema="f63b.synthetic-feasibility.v1",stage="SYNTHETIC_ONLY",
  cases=len(rows),f60_correct=f60_correct,witness_correct=witness_correct,
  f60_fraction=f60_correct/len(rows),witness_fraction=witness_correct/len(rows),
  frozen_threshold_f60=0.25,frozen_threshold_witness=0.85,
  passed_f60=f60_correct/len(rows)>=0.25,
  passed_witness=witness_correct/len(rows)>=0.85,
  source_scientifically_qualified=False,registered_fit_executed=False,
  heldout_executed=False,original_executed=False,rows=rows),sort_keys=True))
