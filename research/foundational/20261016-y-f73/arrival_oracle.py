"""F73 read-only event-order robustness for public memory action reachability.

Offline one-step oracle is unfair/noncompetitive; learns nothing. Every
public event multiset and future postretention task is unchanged. Source and
frozen native legal action space cannot be refit or edited in this audit.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def gitblob(path):
 raw=path.read_bytes();return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
assert gitblob(P/"prereg.json")=="5f5f4546a2c697be9d5238b0742a67d9dc2d06fa"
def load(name,path,expected):
 assert gitblob(path)==expected,(name,"FROZEN_DEPENDENCY_DRIFT")
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
SOURCE=load("f73_frozen_graph_generator",P.parent/"20261016-y-f63c"/"source.py",
 "c04b73306861098eecf55db77b2db486aa918819")
ACTION=load("f73_frozen_native_action_space",P.parent/"20261015-y-f62"/"source_pilot.py",
 "7ed72deca5584d7c0b6562d74456fa7d4bee6712")
AUDIT=load("f73_independent_lossless_causality",P.parent/"20261015-y-f62"/"audit_public.py",
 "383fff0bdd8c8b48fde9538d4e4d768db1c1896f")
PACK=ACTION.codec()
OPTIONS=("original","reverse","even_odd")
def orders(public):
 return {"original":tuple(public),
    "reverse":tuple(reversed(public)),
    "even_odd":tuple(public[::2]+public[1::2])}
def replay(public,q,override=None):
 memory=();before=[];trace=[]
 for i,event in enumerate(public):
  before.append(memory)
  baseline=ACTION._f60_step(memory,event,PACK)
  if override is not None and i==override[0]:
   alternate=override[1]
   options=[c[3] for c in ACTION.actions(memory,event,i,PACK)]
   assert alternate in options and alternate!=baseline
   memory=alternate
  else:memory=baseline
  ACTION._valid_memory(memory,PACK)
  trace.append(tuple(PACK.pack(*record).hex() for record in memory))
 claim=AUDIT.verify(public,q,trace)
 assert claim["prefixes"]==72 and claim["max_payload_bytes"]<=144
 return tuple(before),memory
def evaluate(public,q):
 before,last=replay(public,q)
 correct=int(PACK.solve(last,q)==q["answer"])
 if correct:
  return dict(F60_correct=True,one_step_rescue=False,
    first_rescue_index=None,alternatives_tested=0)
 count=0
 for index in range(72):
  memory=before[index]
  baseline=ACTION._f60_step(memory,public[index],PACK)
  alts=tuple(dict.fromkeys(c[3] for c in ACTION.actions(memory,public[index],index,PACK)
                       if c[3]!=baseline))
  for candidate in alts:
   count+=1
   terminal=ACTION._finish_fixed(candidate,public[index+1:],PACK)
   if PACK.solve(terminal,q)==q["answer"]:
    _prefix,rescued=replay(public,q,(index,candidate))
    assert PACK.solve(rescued,q)==q["answer"]
    return dict(F60_correct=False,one_step_rescue=True,
      first_rescue_index=index,alternatives_tested=count)
 return dict(F60_correct=False,one_step_rescue=False,
    first_rescue_index=None,alternatives_tested=count)
def main():
 result_rows=[]
 for k in range(16):
  seed=-3801-k;family=(-2,-1)[k%2]
  base_public,q,meta=SOURCE.source(seed,family)
  permuted=orders(base_public)
  assert set(permuted)==set(OPTIONS)
  assert all(len(s)==72 and collections.Counter(s)==collections.Counter(base_public)
             and SOURCE.public_witness(s,q)=={q["answer"]} for s in permuted.values())
  for schedule in OPTIONS:
   public=permuted[schedule]
   outcome=evaluate(public,q)
   result_rows.append(dict(seed=seed,family=family,
      question_type=meta["question_type"],arrival_order=schedule,**outcome))
 by_schedule={}
 for schedule in OPTIONS:
  rows=[r for r in result_rows if r["arrival_order"]==schedule]
  fail=[r for r in rows if not r["F60_correct"]]
  hist=collections.Counter(str(r["first_rescue_index"]) for r in fail
                            if r["first_rescue_index"] is not None)
  by_schedule[schedule]=dict(
    cases=len(rows),frozen_F60_correct=sum(r["F60_correct"] for r in rows),
    frozen_F60_failed=len(fail),single_step_rescues=sum(r["one_step_rescue"] for r in fail),
    unrescued_failures=sum(not r["one_step_rescue"] for r in fail),
    legal_candidates_tested=sum(r["alternatives_tested"] for r in fail),
    first_rescue_index_histogram=dict(sorted(hist.items(),key=lambda x:int(x[0]))))
 case_stability=[]
 for k in range(16):
  seed=-3801-k
  items=[r for r in result_rows if r["seed"]==seed]
  case_stability.append(dict(seed=seed,
   kind=items[0]["question_type"],
   frozen_F60_results={r["arrival_order"]:r["F60_correct"] for r in items},
   earliest_rescue_index={r["arrival_order"]:r["first_rescue_index"] for r in items}))
 total_changes=sum(len({r["frozen_F60_results"][s] for s in OPTIONS})>1
                   for r in case_stability)
 out=dict(schema="yggdrasil.f73.public-arrival-order-frozen-oracle.v1",
   stage="READ_ONLY_UNREGISTERED_SYNTHETIC",
   base_case_count=16,orderings_per_case=3,total_public_evaluations=len(result_rows),
   by_schedule=by_schedule,F60_case_outcome_changed_by_order_count=total_changes,
   cases=case_stability,all_event_multisets_unchanged=True,
   independent_full_prefix_causality_pass=True,
   future_question_oracle_noncompetitive=True,
   no_model_trained=True,registered_FIT_train_consumed=False,
   registered_heldout_consumed=False,diagnostics_consumed=False,
   originals_consumed=False,F3=False,optimizer_promotion=False,
   rows=result_rows)
 print(json.dumps(out,sort_keys=True))
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 main()
