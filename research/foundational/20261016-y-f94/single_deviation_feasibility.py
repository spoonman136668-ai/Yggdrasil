#!/usr/bin/env python3
"""F94 consumed-guard native memory feasibility, NOT a causal policy.

Every deviation is evaluated with retrospective future events, question, and
answer. Do not import this evaluator into F62.actions or an online controller.
"""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parent
PREREG_BLOB="5a2d524963aa9a572ad3282c23449bd01a0926d9"
F93_BLOB="b70af0a91ecc16d8a173b7245b007b646fed8ad6"
EXPOSED_SEEDS=range(-6041,-6057,-1)
FAMILIES=(-2,-1)
PERIODS=("early","middle","late")

def gitblob(path):
 raw=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def load_exact(name,path,expected):
 assert gitblob(path)==expected,("F94_FROZEN_SOURCE_DRIFT",name,str(path))
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
 return m

def period(index):
 assert 0<=index<72
 return PERIODS[index//24]

def admissible_overlap(baseline,alternative):
 return sum(record in baseline for record in alternative)>=min(10,max(0,len(baseline)-1))

def evaluate_case(public,question,metadata,F62,F85,F84,codec):
 """A query/answer/future-aware OFFLINE oracle on historical events only."""
 assert len(public)==72 and all(len(e)==3 for e in public)
 assert F84.independently_resolve_public(public,question)[0]==frozenset({question["answer"]})
 qonly={"start":question["start"],"ops":question["ops"]}
 memory=()
 rows=[]
 f60_final=F62._finish_fixed(memory,public,codec)
 base_prediction,base_cost=F85.solve_global(f60_final,qonly,codec)
 assert base_prediction is None or base_prediction==question["answer"]
 assert not base_cost["resource_cap_triggered"]
 baseline_right=bool(base_prediction==question["answer"])
 stats={key:dict(actions=0,rescue_actions=0,harm_actions=0,
                 safe_overlap_actions=0,safe_overlap_rescue=0,safe_overlap_harm=0)
        for key in PERIODS}
 for index,event in enumerate(public):
  after_F60=F62._f60_step(memory,event,codec)
  legal=F62.actions(memory,event,index,codec)
  assert sum(action[3]==after_F60 for action in legal)==1,"F94_F60_NATIVE_PARITY"
  F62._valid_memory(after_F60,codec)
  count_here=0
  successes_here=0
  risks_here=0
  period_stats=stats[period(index)]
  for action in legal:
   after=action[3]
   if after==after_F60:
    continue
   F62._valid_memory(after,codec)
   assert len(after)*12<=144
   terminal=F62._finish_fixed(after,public[index+1:],codec)
   F62._valid_memory(terminal,codec)
   prediction,cost=F85.solve_global(terminal,qonly,codec)
   assert not cost["resource_cap_triggered"],"F94_F85_COUNTERFACTUAL_CAP"
   assert cost["persistent_memory_bytes"]<=144
   assert prediction is None or prediction==question["answer"],"F94_FALSE_PUBLIC_OUTPUT"
   correct=prediction==question["answer"]
   rescue=bool(not baseline_right and correct)
   harm=bool(baseline_right and not correct)
   safe=admissible_overlap(after_F60,after)
   count_here+=1
   successes_here+=int(rescue)
   risks_here+=int(harm)
   period_stats["actions"]+=1
   period_stats["rescue_actions"]+=int(rescue)
   period_stats["harm_actions"]+=int(harm)
   period_stats["safe_overlap_actions"]+=int(safe)
   period_stats["safe_overlap_rescue"]+=int(safe and rescue)
   period_stats["safe_overlap_harm"]+=int(safe and harm)
  rows.append(dict(index=index,period=period(index),alternatives=count_here,
                    rescue_actions=successes_here,harm_actions=risks_here))
  memory=after_F60
 assert memory==f60_final
 assert len(rows)==72
 return dict(seed=metadata["seed"],family=metadata["family"],
   regime=metadata["arrival_regime"],kind=metadata["question_type"],
   f60_correct=int(baseline_right),
   alternatives=sum(v["actions"] for v in stats.values()),
   one_step_rescue=int(any(v["rescue_actions"]>0 for v in stats.values())),
   one_step_harm=int(any(v["harm_actions"]>0 for v in stats.values())),
   safe_overlap_rescue=int(any(v["safe_overlap_rescue"]>0 for v in stats.values())),
   safe_overlap_harm=int(any(v["safe_overlap_harm"]>0 for v in stats.values())),
   by_period=stats,
   prefix_activity=rows)

def summarize(rows):
 return dict(
  cases=len(rows),
  f60_correct=sum(r["f60_correct"] for r in rows),
  total_native_counterfactuals=sum(r["alternatives"] for r in rows),
  f60_failed_cases_with_one_step_rescue=sum(not r["f60_correct"] and r["one_step_rescue"] for r in rows),
  f60_correct_cases_with_harmful_alternative=sum(r["f60_correct"] and r["one_step_harm"] for r in rows),
  f60_failed_cases_with_safe_overlap_rescue=sum(not r["f60_correct"] and r["safe_overlap_rescue"] for r in rows),
  f60_correct_cases_with_safe_overlap_harm=sum(r["f60_correct"] and r["safe_overlap_harm"] for r in rows),
  by_period={p:{key:sum(r["by_period"][p][key] for r in rows)
                for key in ("actions","rescue_actions","harm_actions",
                            "safe_overlap_actions","safe_overlap_rescue","safe_overlap_harm")}
             for p in PERIODS})

def run():
 assert gitblob(P/"prereg.json")==PREREG_BLOB,"F94_PREREG_DRIFT"
 plan=json.loads((P/"prereg.json").read_text())
 assert plan["stage"]=="FROZEN_PRECODE_ALREADY_CONSUMED_F93B_GUARD_ONLY"
 assert plan["data"]["seed_start"]==-6041 and plan["data"]["cases"]==32
 F93=load_exact("f94_frozen_f93",ROOT/"20261016-y-f93b"/"role_grammar.py",F93_BLOB)
 F92=F93.load("f94_frozen_f92",ROOT/"20261016-y-f92"/"dense_path_credit.py",F93.F92_BLOB)
 F91=F92.load("f94_frozen_f91",ROOT/"20261016-y-f91"/"conservative_credit.py",F92.F91_BLOB)
 F90=F91.loader("f94_frozen_f90",ROOT/"20261016-y-f90"/"temporal_credit.py",F91.F90_BLOB)
 F89=F90.load_checked("f94_frozen_f89",ROOT/"20261016-y-f89r"/"graded_exchange.py",F90.F89R_METHOD_BLOB)
 F88=F89.load_exact("f94_frozen_f88",ROOT/"20261016-y-f88"/"frontier.py",F89.F88_BLOB)
 F87=F88.load_exact("f94_frozen_f87",ROOT/"20261016-y-f87b"/"bridge_reserve.py",F88.F87B_BLOB)
 F86=F87.load("f94_frozen_f86",ROOT/"20261016-y-f86"/"queryblind_retention.py",F87.F86_SHA)
 F85=F86.load_exact("f94_frozen_f85",ROOT/"20261016-y-f85"/"global_solver.py",F86.F85_METHOD_BLOB)
 F84=F85.checked_loader("f94_frozen_f84",ROOT/"20261016-y-f84"/"forensic_reachability.py",F85.F84_SHA)
 F83=F84.load_f83()
 weights=F84.assert_frozen()
 codec=F83.M.PACK;F62=F83.M.F62
 cases=[]
 for seed in EXPOSED_SEEDS:
  for family in FAMILIES:
   public,q,metadata=F83.M.SOURCE.source(seed,family)
   assert metadata["question_type"] in ("crosslink_reach_6_steps","within_component_4_steps")
   identity={**metadata,"seed":seed,"family":family}
   row=evaluate_case(public,q,identity,F62,F85,F84,codec)
   cases.append(row)
 assert len(cases)==32
 six=[r for r in cases if r["kind"]=="crosslink_reach_6_steps"]
 four=[r for r in cases if r["kind"]=="within_component_4_steps"]
 assert len(six)==8 and len(four)==24
 overall=summarize(cases)
 six_report=summarize(six)
 four_report=summarize(four)
 return dict(
  schema="yggdrasil.f94.exposed-native-single-deviation-feasibility.v1",
  stage="EXPOSED_ONLY_HINDSIGHT_NOT_CAUSAL_POLICY",
  classification=("retrospective_one_step_native_rescue_possible_only"
                  if six_report["f60_failed_cases_with_one_step_rescue"]>0
                  else "no_one_step_native_rescue_on_consumed_guard_only"),
  cases=32,public_prefixes_examined=32*72,
  all_native_legal_candidates_enumerated=True,
  overall=overall,six_step=six_report,four_step=four_report,
  by_arrival_regime={reg:summarize([r for r in cases if r["regime"]==reg])
                     for reg in ("original","local_rotate4")},
  offline_hindsight_uses_future_question_answer=True,
  valid_online_policy_established=False,
  no_multi_deviation_claim=True,
  native_action_budget_bytes=144,
  no_protected_FIT=True,no_DIAG=True,no_original=True,no_F3=True,
  no_model_fitting=True,no_optimizer_promotion=True,
  scientific_accepted=False,
  rows=cases)
if __name__=="__main__":
 if sys.argv[1:]!=["--consumed-f93b-guard-only"]:
  raise SystemExit("F94 is retrospective only; cannot generate scientific first use")
 print(json.dumps(run(),sort_keys=True))
