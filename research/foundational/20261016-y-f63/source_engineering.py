"""F63 engineering-only public path reliability prototype. Never dispatches FIT."""
from __future__ import annotations
import hashlib, importlib.util, pathlib, sys
HERE=pathlib.Path(__file__).resolve().parent
PARENT=HERE.parent/"20261015-y-f62"
FROZEN={"source_pilot.py":"7ed72deca5584d7c0b6562d74456fa7d4bee6712",
        "audit_public.py":"383fff0bdd8c8b48fde9538d4e4d768db1c1896f"}
def blob(path):
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def load(name,filename):
 path=PARENT/filename
 assert blob(path)==FROZEN[filename]
 sp=importlib.util.spec_from_file_location(name,path)
 obj=importlib.util.module_from_spec(sp);sys.modules[name]=obj;sp.loader.exec_module(obj)
 return obj
def reliability_features(public_prefix,record):
 """Only public causal support, no question or hidden tag."""
 a,b,codes=record
 assert len(codes)<=6 and len(public_prefix)<=72
 if not codes:return (0,0,0,0)
 reachable={a};support=0
 for code in codes:
  role,direction=code//2,code%2
  next_nodes=set()
  for x,r,y in public_prefix:
   if r!=role:continue
   start,end=(y,x) if direction else (x,y)
   if start in reachable: next_nodes.add(end);support+=1
  reachable=next_nodes
  if not reachable:break
 return (int(b in reachable),min(support,16),len(reachable),len(codes))
def select(public,packing,weights=(1,1,0,0),allow_reliability=True):
 """Bounded online selection; distinct from F62's downstream-action reward."""
 assert len(weights)==4 and all(isinstance(w,int) and -127<=w<=127 for w in weights)
 retained=();trace=[];seen=[]
 for i,event in enumerate(public):
  assert len(event)==3
  seen.append(event)
  choices=packing.candidates(list(retained),packing.edge_record(event))
  append=packing.edge_record(event)
  eligible=[(None,append)]
  eligible += [(at,c) for at,c in choices if 1<len(c[2])<=6 and c[0]!=c[1]]
  scored=[]
  for at,rec in eligible:
   feat=reliability_features(seen,rec)
   score=sum(w*f for w,f in zip(weights,feat)) if allow_reliability else len(rec[2])
   prior=tuple(x for j,x in enumerate(retained) if j!=at)
   trial=prior+(rec,)
   if len(trial)>12:
    drop=min(range(len(trial)),key=lambda j:(len(trial[j][2]),j))
    trial=tuple(x for j,x in enumerate(trial) if j!=drop)
   scored.append((score,-len(trial),-len(scored),trial))
  retained=max(scored)[3]
  assert len(retained)<=12
  trace.append(tuple(packing.pack(*r).hex() for r in retained))
 return retained,tuple(trace)
def synthetic_preflight():
 f62=load("f63_f62_frozen","source_pilot.py")
 auditor=load("f63_independent_public","audit_public.py")
 packing=f62.codec()
 for seed,family in ((-71,-2),(-72,-1)):
  tagged,question,_,_=f62._construct(seed,family)
  public=tuple(r[:3] for r in tagged)
  for enabled in (True,False):
   retained,trace=select(public,packing,allow_reliability=enabled)
   result=auditor.verify(public,question,trace)
   assert result["prefixes"]==72 and result["max_payload_bytes"]<=144
   assert len(retained)<=12
 return "F63_SYNTHETIC_ONLY_PASS"
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(synthetic_preflight())
