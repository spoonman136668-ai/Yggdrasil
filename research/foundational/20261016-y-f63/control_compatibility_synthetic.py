"""F63A topology-independent synthetic controls. Frozen code stays unchanged."""
import importlib.util,json,pathlib,sys
P=pathlib.Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
s=load("f63a_new_public_source",P/"replacement_source.py")
a=load("f63a_new_public_auditor",P/"audit_replacement_public.py")
f=load("f63a_old_controls",P.parent/"20261015-y-f62"/"source_pilot.py")
packing=f.codec()
f60,f59,f58,f61=f.controls()
def independent_public_witness(public,question):
 states={question["start"]}
 for role,direction in question["ops"]:
  following=set()
  for x,r,y in public:
   if r==role:
    src,dst=(x,y) if direction==1 else (y,x)
    if src in states: following.add(dst)
  states=following
 return int(states=={question["answer"]})
cases=[]
for seed,family in ((-201,-2),(-202,-1),(-203,-2),(-204,-1),(-205,-2),(-206,-1),(-207,-2),(-208,-1)):
 public,q,_=s.source(seed,family)
 a.verify(public,q)
 # Each original implementation is called directly, without F62's
 # topology-specific wrapper or frozen F60 offline path assertion.
 controls={
  "F60_exact_source_fixed_online":f60.online_fixed(public),
  "F59_exact_source_deferred":f59.fixed_deferred_component_buffer(public),
  "F58_exact_source_frontier":f58.frontier_online(public),
  "F61_frozen_learned_policy_no_refit":f61.learned_online(public,f.F61_WEIGHTS)[0],
 }
 scores={name:int(packing.solve(records,q)==q["answer"]) for name,records in controls.items()}
 scores["independent_public_graph_witness_extra_work"]=independent_public_witness(public,q)
 cases.append({"seed":seed,"family":family,"scores":scores})
fixed=sum(x["scores"]["F60_exact_source_fixed_online"] for x in cases)
witness=sum(x["scores"]["independent_public_graph_witness_extra_work"] for x in cases)
print(json.dumps({"schema":"f63a.synthetic.control-compatibility.v2","cases":len(cases),
 "f60_correct":fixed,"extra_work_correct":witness,
 "registered_fit_executed":False,"scientific_feasibility_qualified":False,
 "heldout_executed":False,"results":cases},sort_keys=True))
