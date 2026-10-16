#!/usr/bin/env python3
"""F87B preregistered native bridge retention on fresh negative synthetic guard.

Unlike F86, F87B retains exact F60 behavior except for public two-frontier
bridge events; it reserves the raw bridge by choosing an existing F62 legal
action. No question, future event, label, model fit, or protected source is
available to the online decision.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parent
PREREG_SHA="12de0e3e045c7361195732d0aec5b42e7c44f4d9"
F86_SHA="8738a5e6a145fbc0f3c2efb2c873c3f8ed1f428e"
GUARD=range(-5321,-5337,-1)
FAMILIES=(-2,-1)
def gitblob(p):
 b=p.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,p,blob):
 assert gitblob(p)==blob,("F87_FROZEN_PARENT_DRIFT",str(p))
 spec=importlib.util.spec_from_file_location(name,p)
 x=importlib.util.module_from_spec(spec);sys.modules[name]=x;spec.loader.exec_module(x)
 return x
def bridge_detect(memory,event):
 a,_,b=event
 left=[i for i,r in enumerate(memory) if a in r[:2]]
 right=[i for i,r in enumerate(memory) if b in r[:2]]
 return any(i!=j for i in left for j in right)
def decision(memory,event,index,pack,F62):
 baseline=F62._f60_step(memory,event,pack)
 choices=F62.actions(memory,event,index,pack)
 legal={x[3] for x in choices}
 assert baseline in legal,"F60_NATIVE_ACTION_PARITY_DRIFT"
 incoming=pack.edge_record(event)
 triggered=bridge_detect(memory,event) and incoming not in baseline
 if not triggered:return baseline,False,False
 candidates=[x for x in choices if incoming in x[3]]
 if not candidates:return baseline,True,False
 def rank(item):
  after=item[3]
  return (sum(x in baseline for x in after),sum(x in memory for x in after))
 n=max(range(len(candidates)),key=lambda i:(rank(candidates[i]),-i))
 result=candidates[n][3]
 F62._valid_memory(result,pack)
 assert result in legal and incoming in result
 return result,True,result!=baseline
def online(public,pack,F62,trace=False):
 assert len(public)==72 and all(len(e)==3 for e in public)
 memory=()
 snapshots=[]
 trigger_count=0
 override_count=0
 for index,event in enumerate(public):
  memory,triggered,override=decision(memory,event,index,pack,F62)
  trigger_count+=int(triggered)
  override_count+=int(override)
  F62._valid_memory(memory,pack)
  if trace:
   snapshots.append(tuple(pack.pack(*r).hex() for r in memory))
 if trace:return memory,tuple(snapshots),dict(triggers=trigger_count,overrides=override_count)
 return memory
def run():
 assert gitblob(P/"prereg.json")==PREREG_SHA,"F87_PRECODE_IDENTITY_DRIFT"
 cfg=json.loads((P/"prereg.json").read_text())
 assert cfg["cohorts"]["guard"]=={"start":-5321,"stop_exclusive":-5337,"step":-1}
 assert cfg["stage"]=="FROZEN_PRECODE_SYNTHETIC_GUARD_ONLY"
 F86=load("f87b_frozen_F86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F86_SHA)
 F85=F86.load_exact("f87b_frozen_F85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f87b_frozen_F84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83()
 frozen=F84.assert_frozen()
 pack=F83.M.PACK
 F62=F83.M.F62
 rows=[]
 for seed in GUARD:
  for family in FAMILIES:
   public,q,meta=F83.M.SOURCE.source(seed,family)
   unique,_=F84.independently_resolve_public(public,q)
   assert unique=={q["answer"]}
   f60=F84.audit_f60(F83,public,q)
   f83,trace83,_=F83.online(public,frozen,True,True)
   assert F83.M.AUDITOR.verify(public,q,trace83)["prefixes"]==72
   f86,trace86,_=F86.online(public,pack,F62,True)
   assert F83.M.AUDITOR.verify(public,q,trace86)["prefixes"]==72
   f87,trace87,flags=online(public,pack,F62,True)
   certificate=F83.M.AUDITOR.verify(public,q,trace87)
   assert certificate["prefixes"]==72 and certificate["max_payload_bytes"]<=144
   row=dict(seed=seed,family=family,regime=meta["arrival_regime"],kind=meta["question_type"],
    triggers=flags["triggers"],overrides=flags["overrides"],max_bytes=certificate["max_payload_bytes"])
   for name,state in (("f60",f60),("f83",f83),("f86",f86),("f87",f87)):
    pred,work=F85.solve_global(state,{"start":q["start"],"ops":q["ops"]},pack)
    assert pred in (None,q["answer"]),"F87_GRAPH_INVALID_OUTPUT"
    assert not work["resource_cap_triggered"] and work["persistent_memory_bytes"]<=144
    row[name+"_correct"]=int(pred==q["answer"])
   row["f87_original_solver_correct"]=int(pack.solve(f87,q)==q["answer"])
   rows.append(row)
 assert len(rows)==32
 by={}
 for regime in ("original","local_rotate4"):
  by[regime]={}
  for kind in ("within_component_4_steps","crosslink_reach_6_steps"):
   selected=[r for r in rows if r["regime"]==regime and r["kind"]==kind]
   assert selected
   by[regime][kind]=dict(cases=len(selected),
    correct={arm:sum(r[arm+"_correct"] for r in selected)
             for arm in ("f60","f83","f86","f87")},
    f87_rescued=sum(not r["f60_correct"] and r["f87_correct"] for r in selected),
    f87_regressed=sum(r["f60_correct"] and not r["f87_correct"] for r in selected),
    override_events=sum(r["overrides"] for r in selected))
 six=[r for r in rows if r["kind"]=="crosslink_reach_6_steps"]
 rescue6=sum(not r["f60_correct"] and r["f87_correct"] for r in six)
 regressed=sum(r["f60_correct"] and not r["f87_correct"] for r in rows)
 total_overrides=sum(r["overrides"] for r in rows)
 supported=(rescue6>0 and regressed==0)
 return dict(schema="yggdrasil.f87b.frozen-frontier-bridge.synthetic-guard.v1",
  classification="synthetic_mechanism_supported" if supported else "synthetic_negative",
  stage="DISJOINT_NEGATIVE_SYNTHETIC_GUARD",cases=len(rows),six_step_cases=len(six),
  scores={arm:sum(r[arm+"_correct"] for r in rows) for arm in ("f60","f83","f86","f87")},
  six_step_rescues=rescue6,regressions_from_F60=regressed,
  bridge_trigger_events=sum(r["triggers"] for r in rows),
  bridge_override_events=total_overrides,by_regime_and_kind=by,
  no_query_in_online_interface=True,no_training=True,all_online_prefixes_verified=True,
  max_persistent_memory_bytes=max(r["max_bytes"] for r in rows),
  no_registered_FIT=True,no_DIAG=True,no_original=True,no_F3=True,
  optimizer_promotion=False,scientific_qualified=False,rows=rows)
if __name__=="__main__":
 if sys.argv[1:]!=["--frozen-negative-synthetic-only"]:
  raise SystemExit("F87B prohibits training and protected first-use")
 print(json.dumps(run(),sort_keys=True))
