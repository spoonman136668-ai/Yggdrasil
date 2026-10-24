"""R6 native source-owned episodic local causal associations for six-bit worlds.

All operators are acquired ONLY through actual public before/action/after
examples; no simulator secrets, oracle rules, or hidden heldout target. The
affine hypothesis is an explicitly provided inductive bias and a fitted GF2
conventional solver MUST be considered equivalent until proven otherwise.
"""
import hashlib
import json

BITS=6
INPUTS=(0,1,2,4,8,16,32)
SCHEMA="yggdrasil.itd02.r6.local-causal-action-composition-v1"

def serialize(obj):
 return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

class LocalCausalComposer:
 def __init__(self):
  self.worlds={}
  self.observations=0

 def learn(self,world,action,before,after):
  if (type(world)is not str or not world or len(world)>64 or
      type(action)is not int or action not in (0,1,2) or
      type(before)is not int or before not in INPUTS or
      type(after)is not int or not 0<=after<64):
   raise ValueError("R6_INVALID_PUBLIC_CAUSAL_EXPERIENCE")
  rows=self.worlds.setdefault(world,{"0":{},"1":{},"2":{}})
  cell=rows[str(action)]
  if str(before) in cell:raise ValueError("R6_DUPLICATE_SOURCE_EXPERIENCE")
  cell[str(before)]=after
  self.observations+=1

 def _predict_step(self,world,action,state):
  if (type(state)is not int or not 0<=state<64 or
      type(action)is not int or action not in (0,1,2)):
   raise ValueError("R6_INVALID_PUBLIC_ACTION_OR_STATE")
  cell=self.worlds.get(world,{}).get(str(action),{})
  if set(cell)!={str(x) for x in INPUTS}:
   raise ValueError("R6_NOT_ENOUGH_PUBLIC_CAUSAL_INFORMATION")
  bias=cell["0"]
  outcome=bias
  for bit in range(6):
   if state&(1<<bit):
    outcome^=(cell[str(1<<bit)]^bias)
  return outcome

 def predict(self,world,start,actions):
  if type(actions)not in (tuple,list) or not 1<=len(actions)<=16:
   raise ValueError("R6_INVALID_PUBLIC_COMPOSITION")
  state=start
  for action in actions:
   state=self._predict_step(world,action,state)
  return state

 def snapshot(self):
  if (self.observations!=sum(len(c) for world in self.worlds.values() for c in world.values()) or
      self.observations>50000 or len(self.worlds)>100):
   raise ValueError("R6_INVALID_CAUSAL_SOURCE_CUSTODY")
  d={"schema":SCHEMA,"worlds":self.worlds,"observations":self.observations}
  payload=serialize(d)
  if len(payload)>131072:raise ValueError("R6_CHECKPOINT_OVERFLOW")
  return serialize({"payload":d,"sha256":hashlib.sha256(payload).hexdigest()})

 @classmethod
 def restore(cls,raw):
  if type(raw)is not bytes or not 0<len(raw)<=131072:
   raise ValueError("R6_CHECKPOINT_INVALID_SIZE")
  try:
   d=json.loads(raw)
   if set(d)!={"payload","sha256"}:raise ValueError("R6_CHECKPOINT_ENVELOPE")
   p=d["payload"]
   if (set(p)!={"schema","worlds","observations"} or p["schema"]!=SCHEMA or
       hashlib.sha256(serialize(p)).hexdigest()!=d["sha256"] or
       type(p["worlds"])is not dict or len(p["worlds"])>100 or
       type(p["observations"])is not int or not 0<=p["observations"]<=50000):
    raise ValueError("R6_CHECKPOINT_AUTH")
   candidate=cls()
   for world,arms in p["worlds"].items():
    if (type(world)is not str or not world or len(world)>64 or
        type(arms)is not dict or set(arms)!={"0","1","2"}):
     raise ValueError("R6_WORLD_STRUCTURE")
    for action,states in arms.items():
     if type(states)is not dict:raise ValueError("R6_SOURCE_ROWS")
     for inp,val in states.items():
      if (inp not in {str(x) for x in INPUTS} or
          type(val)is not int or not 0<=val<64):
       raise ValueError("R6_SOURCE_ROW_CORRUPT")
      candidate.learn(world,int(action),int(inp),val)
   if candidate.observations!=p["observations"]:
    raise ValueError("R6_SOURCE_EVENT_COUNT_DRIFT")
   return candidate
  except (ValueError,TypeError,KeyError,OverflowError) as e:
   raise ValueError("R6_CHECKPOINT_UNTRUSTED") from e
