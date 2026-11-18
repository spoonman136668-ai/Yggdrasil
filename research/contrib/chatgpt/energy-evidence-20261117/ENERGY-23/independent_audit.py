#!/usr/bin/env python3
"""Independent closed-form audit of ENERGY-23. Does not import experiment.py."""
import json, math
from fractions import Fraction as F
from itertools import product
from pathlib import Path
HERE=Path(__file__).resolve().parent
stored=json.loads((HERE/'result.json').read_text())
assert stored['source_prior']==[[7,8],[1,8]]
assert stored['pairs_per_action']==361
# This alternative form directly computes the Bernoulli mutual information from
# joint P(h,y), without the entropy-of-mean minus conditional-entropies formula.
def kl_divergence(p,q):
    return 0.0 if p==0 else float(p)*math.log2(float(p/q))

# Four joint entries above each use P(h) P(y) as denominator.
def alternative_info(old,new):
    w=F(7,8);q=1-w
    p=w*old+q*new
    joint=((w*old,w*p),(w*(1-old),w*(1-p)),(q*new,q*p),(q*(1-new),q*(1-p)))
    return sum(kl_divergence(n,d) for n,d in joint)

prob=[F(v,20) for v in range(1,20)]
pairs=list(product(prob,repeat=2))
exact=[]
for old,new in pairs:
    w=F(7,8);q=1-w;m=w*old+q*new
    var=w*q*(old-new)**2
    exact.append(((var,-abs(m-F(1,2))),alternative_info(old,new),
                  max(w*old,q*new)+max(w*(1-old),q*(1-new))))
violations=0;better=0;max_loss=0.0;matches=0;non_tied_variance=0;checked=0
for a in range(len(pairs)):
    for b in range(len(pairs)):
        if a==b:continue
        checked+=1
        x,y=exact[a],exact[b]
        selected=int(y[0]>x[0]);best=int(y[1]>x[1])
        if x[0]!=y[0]:non_tied_variance+=1
        if abs(x[1]-y[1])<1e-12:continue
        if selected!=best:
            violations+=1
            max_loss=max(max_loss,max(x[1],y[1])-[x[1],y[1]][selected])
        else:matches+=1
assert checked==stored['ordered_two_action_cases_excluding_identical']
assert non_tied_variance==stored['variance_only_non_tied']
assert violations==stored['strict_disagreement_between_source_variance_and_information']
assert matches==stored['matches']
assert abs(max_loss-stored['max_bits_lost_in_case'])<1e-12
x=exact[pairs.index((F(13,20),F(1,10)))];y=exact[pairs.index((F(19,20),F(9,20)))]
assert x[0]>y[0] and x[1]<y[1] and x[2]==F(7,8) and y[2]==F(9,10)
assert abs(x[1]-0.10493318977441203)<1e-12
assert abs(y[1]-0.13271681943975924)<1e-12
print(json.dumps({'audit':'PASS','checked':checked,'reversed_information_choices':violations,
                  'max_bits_lost':max_loss,'source_selects':0,'information_selects':1,
                  'old_prior':[7,8],'novel_prior':[1,8]}))
