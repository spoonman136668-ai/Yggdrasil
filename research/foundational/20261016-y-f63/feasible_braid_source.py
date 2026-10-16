"""F63B new synthetic-only four-chain public braiding design.

Registered training/validation/diagnostic/original seeds are forbidden here.
"""
from __future__ import annotations
import random,sys,json
def source(seed,family):
 if seed>=0 or family not in (-2,-1):
  raise ValueError("UNAUTHORIZED_REGISTERED_SOURCE_IDENTITY")
 rng=random.Random(seed*43991+family*63007)
 used=set()
 def fresh():
  while True:
   n=rng.randrange(1000,1500000000)
   if n not in used: used.add(n);return n
 paths=[]
 for k in range(4):
  nodes=[fresh() for _ in range(9)]
  if nodes[0]>nodes[-1]:nodes.reverse()
  roles=[];edges=[]
  for j in range(8):
   role=rng.randrange(4)
   direction=1 if rng.random()<.5 else -1
   a,b=nodes[j:j+2]
   edges.append((a,role,b) if direction==1 else (b,role,a))
   roles.append((role,direction))
  paths.append((nodes,roles,edges))
 # Visible braiding: additional public edges connect otherwise distinct
 # path intermediates. A different edge role prevents target shortcut.
 braid=[(paths[0][0][4],(paths[0][1][4][0]+2)%4,paths[1][0][4]),
        (paths[2][0][4],(paths[2][1][4][0]+2)%4,paths[3][0][4])]
 noise=[]
 for k in range(38):
  a=fresh();b=fresh()
  noise.append((a,rng.randrange(4),b))
 assert len(noise)+len(braid)+sum(len(p[2]) for p in paths)==72
 if family==-2:
  stream=[]
  for p in paths:stream.extend(p[2][::2])
  stream+=noise[:20]+braid
  for p in paths:stream.extend(p[2][1::2])
  stream+=noise[20:]
 else:
  stream=[e for p in paths for e in p[2]]+braid+noise
  rng.shuffle(stream)
 assert len(stream)==len(set(stream))==72
 chosen=paths[0]
 q={"start":chosen[0][0],"ops":chosen[1][:4],"answer":chosen[0][4]}
 return tuple(stream),q,"four_path_public_braided_crosslinks"
if __name__=="__main__":
 assert sys.argv[1:]==["--synthetic-only"]
 for seed,family in ((-301,-2),(-302,-1)):
  e,q,_=source(seed,family)
  assert len(e)==72 and q["start"]!=q["answer"]
 print(json.dumps({"stage":"SYNTHETIC_ONLY","protected_cohort_executed":False,"new_structure":"four_path_public_braided_crosslinks"},sort_keys=True))
