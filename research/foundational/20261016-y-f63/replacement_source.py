"""F63A replacement relationship source: NO registered FIT generation.

Independent structural design: two braided role-path routes, shared hub
joins, public reversible closures, and mixed orderings. This module is
synthetic engineering only. Protected replacement seeds are denied.
"""
from __future__ import annotations
import random,json,sys
FIT=range(791000,791016)
FAMILIES=(1520,1521,1522,1523)
def source(seed,family):
 if seed in FIT or seed in range(791100,791116) or seed in range(792000,792016):
  raise ValueError("F63A protected cohort use requires separate first-use authority")
 if seed>=0 or family not in (-2,-1):
  raise ValueError("synthetic engineering identities only")
 rng=random.Random(seed*19109+family*311+63001)
 used=set()
 def node():
  while True:
   x=rng.randrange(1000,1500000000)
   if x not in used:
    used.add(x);return x
 # Two disjoint eight-edge answer paths sharing a public intermediate hub.
 hub=node()
 chains=[]
 for k in range(2):
  ns=[node() for _ in range(9)]
  ns[4]=hub
  edges=[]
  roles=[]
  for j in range(8):
   role=(j+k*2)%4
   a,b=ns[j:j+2]
   direction=1 if rng.random()<.5 else -1
   edges.append((a,role,b) if direction==1 else (b,role,a))
   roles.append((role,direction))
  chains.append((tuple(ns),tuple(roles),tuple(edges)))
 # Explicit closure witnesses: public edges join to shared hub, with
 # reversed orientation and independent role codes.
 bridge=[]
 for k in range(8):
  leaf=node()
  role=(k+1)%4
  bridge.append((hub,role,leaf) if k%2 else (leaf,role,hub))
 distractors=[]
 for k in range(48):
  a=node();b=node()
  distractors.append((a,k%4,b))
 core=[e for p in chains for e in p[2]]
 # 16 core + 8 hub + 48 independent edges = 72 public arrivals.
 assert len(core)+len(bridge)+len(distractors)==72
 if family==-2:
  stream=core[:8:2]+bridge[:4]+distractors[:20]+core[8::2]+bridge[4:]+core[1:8:2]+core[9::2]+distractors[20:]
 else:
  stream=core+bridge+distractors
  rng.shuffle(stream)
 assert len(stream)==72 and len(set(stream))==72
 picked=chains[0]
 question=dict(start=picked[0][0],ops=picked[1][:4],answer=picked[0][4])
 return tuple(stream),question,"braided_shared_hub_with_public_closure"
def smoke():
 for seed,family in ((-201,-2),(-202,-1)):
  public,q,regime=source(seed,family)
  assert len(public)==72 and regime.startswith("braided")
  assert q["start"]!=q["answer"]
 for seed in (791000,791008,791100,792000):
  try:source(seed,-2)
  except ValueError:pass
  else:raise AssertionError("protected cohort dispatch")
 return dict(schema="yggdrasil.f63a.new-structure-synthetic.v1",
   stage="SYNTHETIC_ONLY",structural_design="braided_shared_hub",
   registered_fit_executed=False,validation_executed=False,
   originals_executed=False,independent_F3=False)
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 print(json.dumps(smoke(),sort_keys=True))
