"""F63B counterfactual diagnostics on UNREGISTERED negative-seed cases only."""
import importlib.util,pathlib,json,sys
P=pathlib.Path(__file__).resolve().parent
def load(n,path):
 s=importlib.util.spec_from_file_location(n,path);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
src=load("f63b_cf_src",P/"feasible_braid_source.py")
f=load("f63b_cf_old",P.parent/"20261015-y-f62"/"source_pilot.py")
pack=f.codec()
rows=[]
for idx in range(16):
 seed=-301-idx;family=(-2,-1)[idx%2]
 public,q,_=src.source(seed,family)
 fixed=f.controls()[0].online_fixed(public)
 first=f.controls()[0].online_fixed(public[:36])
 second=f.controls()[0].online_fixed(public[36:])
 reversed_public=tuple(reversed(public))
 inverted=f.controls()[0].online_fixed(reversed_public)
 offline_edges=f.controls()[0].online_fixed(tuple(sorted(public)))
 all_public_edges=tuple(pack.edge_record(e) for e in public)
 rows.append(dict(seed=seed,family=family,
 fixed=int(pack.solve(fixed,q)==q["answer"]),
 inverted_order=int(pack.solve(inverted,q)==q["answer"]),
 sorted_order=int(pack.solve(offline_edges,q)==q["answer"]),
 first_half=int(pack.solve(first,q)==q["answer"]),
 second_half=int(pack.solve(second,q)==q["answer"]),
 full_unbounded_single_edges=int(pack.solve(all_public_edges,q)==q["answer"]),
 bounded_records=len(fixed)))
print(json.dumps(dict(schema="f63b.synthetic-counterfactual.v1",cases=len(rows),
 registered_fit_executed=False,original_executed=False,
 totals={k:sum(r[k] for r in rows) for k in ("fixed","inverted_order","sorted_order","first_half","second_half","full_unbounded_single_edges")},rows=rows),sort_keys=True))
