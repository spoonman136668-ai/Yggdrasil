"""F93B: frozen F92 consumed-only legal one-action rescue attribution.

This is an UNFAIR RETROSPECTIVE causal oracle for 12 ALREADY CONSUMED
six-step cases, never an online deployed F92 policy or scientific holdout.
F92 source, weights, native actions, public graph and F85 solver stay frozen.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
R=P.parent
def blob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
EXPECTED_PREREG="4da2180b3ec78c1659e8a9b6045c15490472cbac"
F93A_BLOB="86ebbbbf56791a2a10e0e311d25d0a4cb4e69289"
F92_BLOB="7fdaf5d24866c347275c2ffa3aec7dfeaed6ac5b"
POLICY_BLOB="6a94f730baefe008a21f7286416f3163835ed93e"
assert blob(P/"prereg.json")==EXPECTED_PREREG
def load(name,path,sha):
 assert blob(path)==sha,("F93B_EXACT_SOURCE_DRIFT",name)
 s=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(s);sys.modules[name]=mod;s.loader.exec_module(mod)
 return mod
F93A=load("f93b_frozen_F93A",R/"20261016-y-f93a"/"forensic_probabilities.py",F93A_BLOB)
F92=load("f93b_frozen_F92",R/"20261016-y-f92"/"dense_path_credit.py",F92_BLOB)
F91=F92.load("f93b_frozen_F91",R/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
F90=F91.loader("f93b_frozen_F90",R/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
F89=F90.load_checked("f93b_frozen_F89",R/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
F88=F89.load_exact("f93b_frozen_F88",R/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
F87=F88.load_exact("f93b_frozen_F87",R/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
F86=F87.load("f93b_frozen_F86",R/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
F85=F86.load_exact("f93b_frozen_F85",R/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
F84=F85.checked_loader("f93b_frozen_F84",R/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
F83=F84.load_f83()
pack=F83.M.PACK
native=F83.M.F62
assert blob(R/"20261016-y-f92"/"frozen-policy.json")==POLICY_BLOB
receipt=json.loads((R/"20261016-y-f92"/"frozen-policy.json").read_text())
benefit=tuple(receipt["benefit_weights"])
harm=tuple(receipt["harm_weights"])
assert hashlib.sha256(bytes(x%256 for x in benefit+harm)).hexdigest()==receipt["weights_sha256"]
def f85_correct(state,q):
 answer,receipt=F85.solve_global(state,{"start":q["start"],"ops":q["ops"]},pack)
 assert not receipt["resource_cap_triggered"] and receipt["persistent_memory_bytes"]<=144
 assert answer is None or answer==q["answer"],"PRIVATE_ANSWER_LEAK_OR_INVALID_PUBLIC_GRAPH"
 return answer==q["answer"]
def baseline_prefix(public,q):
 memory=()
 before=[]
 trace=[]
 for index,event in enumerate(public):
  before.append(memory)
  memory=native._f60_step(memory,event,pack)
  native._valid_memory(memory,pack)
  trace.append(tuple(pack.pack(*r).hex() for r in memory))
 audit=F83.M.AUDITOR.verify(public,q,trace)
 assert audit["prefixes"]==72 and audit["max_payload_bytes"]<=144
 return before,memory
def independently_prove_rescue(public,q,index,after):
 memory=()
 trace=[]
 for i,event in enumerate(public):
  expected=native._f60_step(memory,event,pack)
  if i==index:
   choices=[c[3] for c in native.actions(memory,event,i,pack)]
   assert after!=expected and after in choices,"UNAUTHORIZED_OFFLINE_STATE"
   memory=after
  else:memory=expected
  native._valid_memory(memory,pack)
  trace.append(tuple(pack.pack(*r).hex() for r in memory))
 proof=F83.M.AUDITOR.verify(public,q,trace)
 assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
 assert f85_correct(memory,q),"FALSE_RESCUE"
def examine(public,q,meta,seed,family,cohort):
 before,end=baseline_prefix(public,q)
 assert not f85_correct(end,q),"F93B_CROSS_LINK_ALREADY_SOLVED_BY_F60"
 m92,t92,stats=F92.online(public,benefit,harm,pack,native,F91,True)
 assert stats["interventions"]==0 and m92==end
 assert F83.M.AUDITOR.verify(public,q,t92)["prefixes"]==72
 counts=collections.Counter()
 wins=collections.Counter()
 first=None
 first_eligible=None
 first_late=None
 one_proved=False
 for index,event in enumerate(public):
  old=before[index]
  baseline=native._f60_step(old,event,pack)
  options=native.actions(old,event,index,pack)
  matching=[z for z in options if z[3]==baseline]
  assert len(matching)==1
  seen=set()
  for action in options:
   after=action[3]
   if after==baseline or after in seen:continue
   seen.add(after);counts["native_nonbaseline"]+=1
   later=index>=24
   if later:counts["F92_time_eligible"]+=1
   overlap=False;passed=False
   if later:
    required=min(10,max(0,len(baseline)-1))
    overlap=sum(rec in baseline for rec in after)>=required
    if overlap:
     counts["late_overlap"]+=1
     vec=F91.vector(matching[0][4],action[4])
     positive=F91.score(benefit,vec)
     harmful=F91.score(harm,vec)
     passed=positive>=.68 and harmful<=.18 and positive-harmful>=.50
     if passed:counts["passed_all_frozen_F92_gates"]+=1
   terminal=native._finish_fixed(after,public[index+1:],pack)
   if f85_correct(terminal,q):
    wins["all"]+=1
    if index<24:wins["early"]+=1
    else:
     wins["late"]+=1
     if overlap:
      wins["late_overlap"]+=1
      if passed:wins["late_all_F92_gates"]+=1
    if first is None:
     first=index
     independently_prove_rescue(public,q,index,after)
     one_proved=True
    if index>=24 and first_late is None:first_late=index
    if index>=24 and overlap and first_eligible is None:first_eligible=index
 assert one_proved==(first is not None)
 return dict(cohort=cohort,seed=seed,family=family,
   regime=meta["arrival_regime"],kind=meta["question_type"],
   candidates=dict(counts),rescuing_actions=dict(wins),
   earliest_any_index=first,earliest_late_index=first_late,
   earliest_F92_time_and_overlap_index=first_eligible,
   one_verified_causal_72_prefix_rescue=one_proved,
   frozen_F92_zero_interventions=True)
def main():
 cases=[]
 for cohort,seeds in (("validation",range(-5921,-5929,-1)),
                      ("guard",range(-5941,-5957,-1))):
  for seed in seeds:
   for family in (-2,-1):
    public,q,meta=F83.M.SOURCE.source(seed,family)
    assert F84.independently_resolve_public(public,q)[0]==frozenset({q["answer"]})
    if meta["question_type"]!="crosslink_reach_6_steps":continue
    cases.append(examine(public,q,meta,seed,family,cohort))
 assert len(cases)==12
 global_counts=collections.Counter()
 global_wins=collections.Counter()
 for r in cases:
  global_counts.update(r["candidates"])
  global_wins.update(r["rescuing_actions"])
 def summarize(rows):
  return dict(cases=len(rows),
   any_native_one_step_rescuable=sum(r["earliest_any_index"] is not None for r in rows),
   late_index_ge24_rescuable=sum(r["earliest_late_index"] is not None for r in rows),
   late_with_record_overlap_rescuable=sum(
    r["earliest_F92_time_and_overlap_index"] is not None for r in rows),
   verified_causal_rescue_traces=sum(r["one_verified_causal_72_prefix_rescue"] for r in rows),
   native_candidates=sum(r["candidates"].get("native_nonbaseline",0) for r in rows),
   earliest_rescue_indices=[r["earliest_any_index"] for r in rows])
 out=dict(schema="yggdrasil.f93b.retired-f92-native-rescue-attribution.v1",
  stage="ALREADY_CONSUMED_F92_COHORTS_ONLY_NONCOMPETITIVE_RETROSPECTIVE",
  total_cases=len(cases),totals=summarize(cases),
  by_cohort={n:summarize([r for r in cases if r["cohort"]==n])
             for n in ("validation","guard")},
  by_arrival={n:summarize([r for r in cases if r["regime"]==n])
             for n in ("original","local_rotate4")},
  candidate_gates=dict(global_counts),rescue_gate_counts=dict(global_wins),
  exact_72_prefix_independent_audit=True,
  frozen_F92_has_zero_interventions=True,
  F92_weights_or_thresholds_changed=False,
  no_model_fitted=True,no_new_source_used=True,no_protected_originals=True,
  consumed_cases_NEVER_reusable_as_independent_holdout=True,
  F3=False,science_accepted=False,optimizer_promotion=False,
  controller_mutation=False,rows=cases)
 print(json.dumps(out,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--already-consumed-F92-only"]
 main()
