"""Independent F67 packed public-prefix auditor with early frontier eviction.

Read-only; imports only previously frozen source-independent F62 auditor
and never imports the F67 learned policy, task generator or future labels.
"""
from __future__ import annotations
import hashlib,importlib.util,pathlib
HERE=pathlib.Path(__file__).resolve().parent
PARENT=HERE.parent/"20261015-y-f62"/"audit_public.py"
def gitblob(path):
 b=path.read_bytes();return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
assert gitblob(PARENT)=="383fff0bdd8c8b48fde9538d4e4d768db1c1896f"
spec=importlib.util.spec_from_file_location("f67_independent_f62_codec",PARENT)
import sys
f62=importlib.util.module_from_spec(spec);sys.modules[spec.name]=f62;spec.loader.exec_module(f62)
def _covers(old,new):
 a,b,c=old
 x,y,more=new
 n=len(c)
 return len(more)>n and ((x==a and more[:n]==c) or (y==b and more[-n:]==c))
def _respects_budget(before,after):
 if len(after)>12:return False
 long_count=sum(len(r[2])>=4 for r in after)
 if long_count>8 or len(after)-long_count>4:return False
 for rec in before:
  if len(rec[2])<4 or rec in after:continue
  if not any(_covers(rec,item) for item in after):return False
 return True
def legal_next(before,event):
 # F62's independent public proposals: append / merge / global eviction.
 ordinary=f62.proposals(before,event)
 allowed={before} # causal refusal of current edge, no hidden information
 for candidate in ordinary:
  if _respects_budget(before,candidate):allowed.add(candidate)
  # New F67 action: locally evict one short frontier record even
  # before all twelve global slots are full.
  for i,rec in enumerate(candidate):
   if len(rec[2])>=4:continue
   after=candidate[:i]+candidate[i+1:]
   if _respects_budget(before,after):allowed.add(after)
 return allowed
def verify(public_events,question,prefix_hex):
 assert len(public_events)==len(prefix_hex)==72
 assert all(len(e)==3 for e in public_events)
 assert len(set(tuple(e) for e in public_events))==72
 before=();seen=[];max_bytes=0;checked=0
 for event,snapshot in zip(public_events,prefix_hex):
  assert len(snapshot)<=12,"OVER_CAP"
  after=tuple(f62.decode(value) for value in snapshot)
  assert len(set(after))==len(after),"DUPLICATE_RECORD"
  assert _respects_budget(before,after),"F67_BUDGET_OR_STABLE_PATH_VIOLATION"
  assert after in legal_next(before,tuple(event)),"NONCAUSAL_F67_MEMORY_TRANSITION"
  seen.append(tuple(event))
  for rec in after:
   assert f62.prefix_witness(rec,seen),"UNSEEN_RELATIONAL_EDGE"
   assert f62.encode(rec) in snapshot,"NOT_LOSSLESS_CANONICAL"
   checked+=1
  max_bytes=max(max_bytes,12*len(after))
  before=after
 f62.public_question_witness(public_events,question)
 return dict(prefixes=72,max_payload_bytes=max_bytes,reconstructed_records=checked,
   retained_question_prediction=f62.solve(before,question),
   publicly_grounded_question=True,independent_F3=False)
