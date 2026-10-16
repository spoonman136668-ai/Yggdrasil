"""F66B frozen-model read-only memory retention forensic on exposed synthetics.

Recovers complete public path only AFTER retention to evaluate true fragment
coverage. Offline reconstruction never enters the online frozen policy.
"""
from __future__ import annotations
import hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def blob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,expected):
 assert blob(path)==expected,(name,"BLOB_DRIFT")
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
r=json.loads((P/"f66b_frozen_receipt.json").read_text())
MODEL=load("f66b_frozen_forensic_model",P/"two_head_continuation.py",r["online_blob"])
PACK=MODEL.PACK
weights=tuple(r["frozen_int8_weights"])
def true_paths(public,q):
 paths={(q["start"],)}
 for role,direction in q["ops"]:
  next_paths=set()
  for path in paths:
   at=path[-1]
   for a,rr,b in public:
    if rr!=role:continue
    src,dst=(a,b) if direction==1 else (b,a)
    if at==src:next_paths.add(path+(dst,))
  paths=next_paths
 return tuple(p for p in paths if p[-1]==q["answer"])
def flip(rec):
 a,b,c=rec
 return b,a,tuple(x^1 for x in reversed(c))
def support(mem,paths,q):
 codes=tuple(2*role+(direction==-1) for role,direction in q["ops"])
 supporting=set()
 for p in paths:
  for at in range(len(codes)):
   for end in range(at+1,min(len(codes),at+6)+1):
    supporting.add((p[at],p[end],codes[at:end]))
 valid=[rec for rec in mem if rec in supporting or flip(rec) in supporting]
 return dict(records=len(mem),max_record_hops=max((len(x[2]) for x in mem),default=0),
    multi_hop=sum(len(x[2])>=2 for x in mem),
    long_records=sum(len(x[2])>=4 for x in mem),
    truly_relevant_records=len(valid),
    relevant_encoded_hops=sum(len(x[2]) for x in valid))
f60=MODEL.ACTION.controls()[0]
results=[]
for i in range(24):
 seed=-2401-i;family=(-2,-1)[i%2]
 public,q,meta=MODEL.SOURCE.source(seed,family)
 paths=true_paths(public,q)
 assert len(paths)==1,("PUBLIC_GRAPH_NOT_UNIQUE",seed)
 learned,trace,merges=MODEL.online(public,weights,True)
 ablated,trace_abl,ab_merges=MODEL.online(public,weights,True,False)
 fixed=f60.online_fixed(public)
 row=dict(seed=seed,family=family,kind=meta["question_type"],
   learned_correct=int(PACK.solve(learned,q)==q["answer"]),
   ablation_correct=int(PACK.solve(ablated,q)==q["answer"]),
   frozen_F60_correct=int(PACK.solve(fixed,q)==q["answer"]),
   learned_merges=merges,ablation_merges=ab_merges,
   learned=support(learned,paths,q),ablation=support(ablated,paths,q),
   frozen_F60=support(fixed,paths,q))
 results.append(row)
out=dict(schema="yggdrasil.f66b.exposed-synthetic-retention-forensics.v1",
  cases=len(results),by_kind={
    kind:{label:sum(r[label] for r in results if r["kind"]==kind)
         for label in ("learned_correct","ablation_correct","frozen_F60_correct")}
    for kind in sorted({r["kind"] for r in results})},
  trained_merges=sum(r["learned_merges"] for r in results),
  learned_final_true_fragments=sum(r["learned"]["truly_relevant_records"] for r in results),
  baseline_final_true_fragments=sum(r["frozen_F60"]["truly_relevant_records"] for r in results),
  learned_final_long_records=sum(r["learned"]["long_records"] for r in results),
  baseline_final_long_records=sum(r["frozen_F60"]["long_records"] for r in results),
  registered_fit_read=False,heldout_read=False,model_modified=False,policy_promotion=False,
  rows=results)
print(json.dumps(out,sort_keys=True))
