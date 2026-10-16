"""F63B independent source-validity guard; only unregistered synthetic identities."""
import importlib.util,pathlib,sys,json
P=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("f63b_guard_source",P/"feasible_braid_source.py")
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
def outcomes(edges,question):
 states={question["start"]}
 for role,direction in question["ops"]:
  states={dst for a,r,b in edges if r==role for src,dst in (((a,b),) if direction==1 else ((b,a),)) if src in states}
 return states
invalid=[]
for i in range(16):
 seed=-301-i;family=(-2,-1)[i%2]
 edges,q,_=m.source(seed,family)
 reached=outcomes(edges,q)
 if reached!={q["answer"]}:invalid.append(dict(seed=seed,family=family,reachable=len(reached)))
assert [r["seed"] for r in invalid]==[-314,-315],invalid
print(json.dumps(dict(schema="f63b.synthetic-source-validity.v1",cases=16,
 invalid_cases=invalid,source_validity_pass=False,fit_executed=False,
 heldout_executed=False,approved_for_science=False),sort_keys=True))
