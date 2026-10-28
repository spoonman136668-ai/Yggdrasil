"""V31I external exact cold restart envelope for unchanged V31D controller."""
import hashlib,json,math
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES,canonical
from yggdrasil.itd02_v24_protected_dual_memory_dev import ProtectedDualMemoryRingDev
from yggdrasil.itd02_v31d_distinct_return_dev import DistinctReturnRingDev
LIMIT=12288
def pack(m):
 m.bank._guard()
 if m.bank.fast.cue is not None or m.bank.slow.cue is not None:raise ValueError("PENDING_EPISODE")
 body={"schema":"v31i.cold.v1","bank":json.loads(m.bank.checkpoint()),
       "fast":m.fast,"recent":m.recent,"public_history":m.public_history,
       "switches":m.switches}
 raw=canonical(body)
 result=canonical({"body":body,"sha256":hashlib.sha256(raw).hexdigest()})
 if len(result)>LIMIT:raise ValueError("V31I_CHECKPOINT_LIMIT")
 return result
def restore(raw):
 try:
  if type(raw) is not bytes or not 0<len(raw)<=LIMIT:raise ValueError("SIZE")
  env=json.loads(raw);body=env["body"]
  if set(env)!={"body","sha256"} or set(body)!={"schema","bank","fast","recent","public_history","switches"}:raise ValueError("KEYS")
  if body["schema"]!="v31i.cold.v1" or hashlib.sha256(canonical(body)).hexdigest()!=env["sha256"]:raise ValueError("DIGEST")
  bank=ProtectedDualMemoryRingDev.restore(canonical(body["bank"]))
  if bank.fast.cue is not None or bank.slow.cue is not None:raise ValueError("PENDING")
  recent=body["recent"];hist=body["public_history"]
  if type(body["fast"]) is not bool or type(body["switches"]) is not int or not 0<=body["switches"]<=bank.target_updates:raise ValueError("SELECTOR")
  if type(recent) is not list or type(hist) is not list or len(recent)!=len(hist) or len(recent)!=min(3,bank.target_updates):raise ValueError("HISTORY")
  for pair,item in zip(recent,hist):
   if type(pair) is not list or len(pair)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in pair):raise ValueError("RESIDUAL")
   if type(item) is not list or len(item)!=3 or type(item[0]) is not list or len(item[0])!=3 or item[0][0] not in PUBLIC_CUES or any(x not in ACTIONS for x in item[0][1:]) or pair!=item[1:]:raise ValueError("CONTEXT")
  m=DistinctReturnRingDev.__new__(DistinctReturnRingDev)
  m.bank=bank;m.fast=body["fast"];m.recent=[tuple(x) for x in recent]
  m.public_history=[(tuple(x[0]),x[1],x[2]) for x in hist];m.switches=body["switches"]
  if pack(m)!=raw:raise ValueError("NONCANONICAL")
  return m
 except (ValueError,TypeError,KeyError,IndexError,AttributeError) as e:raise ValueError("UNTRUSTED_V31I_CHECKPOINT") from e
