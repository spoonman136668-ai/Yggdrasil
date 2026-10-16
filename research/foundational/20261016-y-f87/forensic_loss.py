#!/usr/bin/env python3
"""Immutable read-only attribution of exposed F86 negative; no new experiments."""
from __future__ import annotations
import collections,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent
F86_BLOB="8738a5e6a145fbc0f3c2efb2c873c3f8ed1f428e"
PRE_BLOB="e452638551f3c3d58415e70605bb4f39ac3749cc"
def gitblob(p):
 b=p.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,path,sha):
 assert gitblob(path)==sha,(name,"SOURCE_DRIFT")
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 return m
def reachable_prefix(memory,question,codec):
 codes=tuple(2*role+int(direction==-1) for role,direction in question["ops"])
 records=set()
 for r in memory:
  records.add(r);records.add(codec.mirrored(r))
 states={0:{question["start"]}}
 for k in range(len(codes)):
  for node in tuple(states.get(k,())):
   for a,b,seq in records:
    if a==node and k+len(seq)<=len(codes) and tuple(seq)==codes[k:k+len(seq)]:
     states.setdefault(k+len(seq),set()).add(b)
 return max((k for k,v in states.items() if v),default=0)
def signature(mem,question,codec):
 prefix=reachable_prefix(mem,question,codec)
 oriented=set()
 for record in mem:oriented.update((record,codec.mirrored(record)))
 code=2*question["ops"][0][0]+int(question["ops"][0][1]==-1)
 start_access=any(a==question["start"] and codes[0]==code for a,b,codes in oriented)
 return dict(records=len(mem),total_role_steps=sum(len(z[2]) for z in mem),
  composed_records=sum(len(z[2])>1 for z in mem),
  start_accessible=bool(start_access),maximum_role_hops_reachable=prefix)
def evaluate():
 assert gitblob(P/"prereg-forensic.json")==PRE_BLOB
 F86=load("f87_frozen_f86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F86_BLOB)
 F85=F86.load_exact("f87_frozen_f85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f87_frozen_f84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 w=F84.assert_frozen()
 F83=F84.load_f83()
 pack=F83.M.PACK
 records=[]
 for seed in F86.GUARD_SEEDS:
  for family in F86.FAMILIES:
   public,q,meta=F83.M.SOURCE.source(seed,family)
   assert F84.independently_resolve_public(public,q)[0]=={q["answer"]}
   f60=F84.audit_f60(F83,public,q)
   f86,trace,_=F86.online(public,pack,F83.M.F62,True)
   assert F83.M.AUDITOR.verify(public,q,trace)["prefixes"]==72
   p60,_=F85.solve_global(f60,{"start":q["start"],"ops":q["ops"]},pack)
   p86,_=F85.solve_global(f86,{"start":q["start"],"ops":q["ops"]},pack)
   row=dict(seed=seed,family=family,kind=meta["question_type"],regime=meta["arrival_regime"],
    f60_correct=int(p60==q["answer"]),f86_correct=int(p86==q["answer"]),
    f60=signature(f60,q,pack),f86=signature(f86,q,pack))
   records.append(row)
 assert len(records)==32
 lost=[r for r in records if r["f60_correct"] and not r["f86_correct"]]
 assert len(lost)==16
 def aggregate(rows,arm):
  return dict(cases=len(rows),
   start_accessible=sum(r[arm]["start_accessible"] for r in rows),
   full_role_prefix_reachable=sum(r[arm]["maximum_role_hops_reachable"]==(6 if r["kind"]=="crosslink_reach_6_steps" else 4) for r in rows),
   total_role_steps=sum(r[arm]["total_role_steps"] for r in rows),
   multi_step_chunks=sum(r[arm]["composed_records"] for r in rows),
   mean_max_prefix_hops=(sum(r[arm]["maximum_role_hops_reachable"] for r in rows)/len(rows)) if rows else 0)
 return dict(schema="yggdrasil.f87.immutable-f86-loss-attribution.v1",
   status="EXPOSED_ONLY_DESCRIPTIVE",cases=32,f60_correct=sum(r["f60_correct"] for r in records),
   f86_correct=sum(r["f86_correct"] for r in records),f60_correct_f86_lost=16,
   f60_only_case_summary={arm:aggregate(lost,arm) for arm in ("f60","f86")},
   all_case_summary={arm:aggregate(records,arm) for arm in ("f60","f86")},
   no_new_source_cases=True,no_fit=True,no_diag=True,no_original=True,no_policy_update=True,
   accepted_scientific_result=False,rows=records)
if __name__=="__main__":
 assert sys.argv[1:]==["--consumed-f86-only"]
 print(json.dumps(evaluate(),sort_keys=True))
