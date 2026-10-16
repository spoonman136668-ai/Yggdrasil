"""F63A synthetic-only unchanged-control compatibility gate."""
import importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
s=load("f63a_new_public_source",P/"replacement_source.py")
a=load("f63a_new_public_auditor",P/"audit_replacement_public.py")
f=load("f63a_old_controls",P.parent/"20261015-y-f62"/"source_pilot.py")
packing=f.codec()
cases=[]
for seed,family in ((-201,-2),(-202,-1),(-203,-2),(-204,-1),(-205,-2),(-206,-1),(-207,-2),(-208,-1)):
 public,q,_=s.source(seed,family)
 a.verify(public,q)
 controls=f.historical_controls_public(public,packing)
 scores={name:int(packing.solve(records,q)==q["answer"]) for name,records in controls.items()}
 cases.append({"seed":seed,"family":family,"scores":scores})
fixed=sum(x["scores"]["F60_exact_source_fixed_online"] for x in cases)
witness=sum(x["scores"]["offline_full_public_graph_extra_work_noncompetitive"] for x in cases)
print(json.dumps({"schema":"f63a.synthetic.control-compatibility.v1","cases":len(cases),
 "f60_correct":fixed,"extra_work_correct":witness,
 "registered_fit_executed":False,"scientific_feasibility_qualified":False,
 "heldout_executed":False,"results":cases},sort_keys=True))
