#!/usr/bin/env python3
"""ENERGY-41 signed-gradient semantic invariant probe. PASS means defect reproduced."""
import experiment as e
import json
from pathlib import Path
counts={"comparisons":0,"nonzero_mismatches":0,"all_opposites":0}
first=None
for seed in (8407,8423,8431):
 for c in e.train_cases(seed):
  got=e.structured_examples([c])
  for vertex in range(c["n"]):
   direct=[0.,0.,0.]
   for edge in c["edges"]:
    i,j,obs,g=edge
    if vertex not in (i,j):continue
    old=e.violations(edge,c["truth"])
    direct[g]+=1 if old==0 else -1
   for g,d in enumerate(direct):
    src=float(got[vertex,g])
    counts["comparisons"]+=1
    counts["nonzero_mismatches"]+=int(src!=d)
    counts["all_opposites"]+=int(src==-d)
    if src!=d and first is None:first={"seed":seed,"family":c["family"],"vertex":vertex,"group":g,"source_delta":src,"direct_delta":d}
assert counts=={"comparisons":2880,"nonzero_mismatches":2217,"all_opposites":2880},counts
assert first=={"seed":8407,"family":"erdos","vertex":0,"group":0,"source_delta":-2.0,"direct_delta":2.0}
print(json.dumps({"status":"FAIL_IMPLEMENTATION_INVARIANT","counts":counts,"first":first,"science":"INVALID"},sort_keys=True))
