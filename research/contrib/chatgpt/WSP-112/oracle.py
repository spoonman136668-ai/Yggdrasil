"""Evaluator-only hidden WSP112 environment: NEVER imported by learner/fixtures.

An intervention resets a 2-bit state, applies a 2-bit action and returns a
2-bit next-state consequence, determined by an unknown Boolean law.
"""
from __future__ import annotations
from hashlib import sha256
from core import MONOMIALS,FEATURES

def label(split,world,degree,x,seed='v1'):
    if split not in ('train','transfer') or type(world)!=int or type(x)!=int or type(degree)!=int:
        raise ValueError("unregistered causal environment")
    if not(0<=x<16 and 1<=degree<=4):raise ValueError("world bounds")
    coeff=[]
    for out in range(2):
        row=[]
        for mask in MONOMIALS:
            if mask.bit_count()>degree:
                row.append(0);continue
            h=sha256(f'WSP112|LAW|{seed}|{split}|{world}|{out}|{mask}'.encode('ascii')).digest()
            row.append(h[0]&1)
        coeff.append(row)
    if not any(coeff[b][j] for b in range(2) for j,m in enumerate(MONOMIALS)
               if m.bit_count()==degree):
        idx=min(j for j,m in enumerate(MONOMIALS) if m.bit_count()==degree)
        coeff[0][idx]=1
    y=[]
    for b in range(2):
        y.append(sum(int(FEATURES[x,j])*coeff[b][j] for j in range(16))%2)
    return y[0]+2*y[1]

def training_tables(seed='v1'):
    return [[[int(label('train',g,1 if g<256 else 2,x,seed)>>b)&1
              for b in range(2)] for x in range(16)] for g in range(512)]

def transfer_degree(group):
    if type(group)!=int or not 0<=group<256:raise ValueError("group bounds")
    return 3 if group<128 else 4
