"""F63B synthetic forensic diagnostics; no registered cohort access."""
import importlib.util,pathlib,json,sys,collections
P=pathlib.Path(__file__).resolve().parent
def load(n,path):
 sp=importlib.util.spec_from_file_location(n,path);m=importlib.util.module_from_spec(sp);sys.modules[n]=m;sp.loader.exec_module(m);return m
s=load("f63b_diag_source",P/"feasible_braid_source.py")
f=load("f63b_diag_controls",P.parent/"20261015-y-f62"/"source_pilot.py")
pack=f.codec()
rows=[]
for i in range(16):
 seed=-301-i;family=(-2,-1)[i%2]
 public,q,regime=s.source(seed,family)
 states={q["start"]};widths=[]
 for role,direction in q["ops"]:
  nxt=set()
  for a,r,b in public:
   src,dst=(a,b) if direction==1 else (b,a)
   if r==role and src in states:nxt.add(dst)
  states=nxt;widths.append(len(states))
 baseline=f.controls()[0].online_fixed(public)
 score=pack.solve(baseline,q)
 rows.append(dict(seed=seed,family=family,reachable=len(states),
  answer_unique=(states=={q["answer"]}),branch_widths=widths,
  final_memory_records=len(baseline),
  retained_chains=[len(rec[2]) for rec in baseline],
  baseline_answer_correct=(score==q["answer"])))
print(json.dumps(dict(schema="f63b.synthetic-forensic.v1",registered_fit_executed=False,
 cases=16,uniquely_grounded=sum(x["answer_unique"] for x in rows),
 f60_correct=sum(x["baseline_answer_correct"] for x in rows),
 max_branch_width=max(max(x["branch_widths"]) for x in rows),
 evidence=rows),sort_keys=True))
