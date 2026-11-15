"""WSP114 independent exact symbolic and fully fitted conventional controls.

This file never imports native.py or the hidden causal-law oracle. Its feature
enumeration, Boolean elimination and effect propagation are separately authored.
"""
from __future__ import annotations
from hashlib import sha256
from functools import lru_cache
import numpy as np

NMAX=64
LIMIT=1024

@lru_cache(maxsize=64)
def local_grammar(node):
    low=max(0,node-12)
    idx=tuple(range(low,node))
    return tuple((i,) for i in idx)+tuple((i,j)
               for i in idx for j in idx if i<j)

@lru_cache(maxsize=32768)
def _local_word(width,bits):
    result=0
    terms=tuple((i,) for i in range(width))+tuple((i,j)
          for i in range(width) for j in range(i+1,width))
    for k,term in enumerate(terms):
        if all(bits&(1<<v) for v in term):result|=1<<k
    return result

def feature_word(node,after):
    width=min(node,12)
    return _local_word(width,(after>>(node-width))&((1<<width)-1))

def independent_predict(before,action,weights,nodes):
    if type(before)!=int or not 0<=before<1<<nodes or type(action)!=int or not 0<=action<2*nodes:
        raise ValueError("symbolic input out of bounds")
    after=0
    for j in range(nodes):
        if j==action//2:
            b=action&1
        else:
            b=((before>>j)&1)^((weights[j]&feature_word(j,after)).bit_count()&1)
        after|=b<<j
    return after

def independent_solve(rows,variables):
    """Full batch GF(2) elimination, separate from native incremental basis."""
    equations={}
    for raw,value in rows:
        bits=int(raw);rhs=int(value)
        while bits:
            lead=bits.bit_length()-1
            if lead not in equations:
                equations[lead]=(bits,rhs)
                break
            prior,val=equations[lead]
            bits^=prior
            rhs^=val
        if not bits and rhs:raise ValueError("inconsistent symbolic observations")
    result=0
    for lead in sorted(equations):
        row,target=equations[lead]
        result|=(target^((result&row).bit_count()&1))<<lead
    if result>=1<<variables:raise AssertionError("wrong symbolic equation length")
    return result,len(equations)

class IndependentSymbolic:
    def __init__(self,nodes=64):
        self.nodes=nodes
        self.log=[]
        self.coefficients=[0]*nodes
        self.ranks=[0]*nodes
        self.rows=[[] for _ in range(nodes)]
        self._fitted_at=0

    def observe(self,state,action,outcome):
        if type(state)!=int or type(action)!=int or type(outcome)!=int:
            raise ValueError("noninteger symbolic observation")
        if not 0<=state<1<<self.nodes or not 0<=action<self.nodes*2 or not 0<=outcome<1<<self.nodes:
            raise ValueError("invalid symbolic data")
        if ((outcome>>(action//2))&1)!=(action&1):
            raise ValueError("forced bit failed")
        if len(self.log)>=LIMIT or any(s==state and a==action for s,a,_ in self.log):
            raise ValueError("symbolic duplicate or budget")
        self.log.append((state,action,outcome))
        for j in range(self.nodes):
            if j==action//2:continue
            self.rows[j].append((feature_word(j,outcome),
                ((state>>j)&1)^((outcome>>j)&1)))

    def fit(self):
        if self._fitted_at==len(self.log):return
        for node in range(self.nodes):
            self.coefficients[node],self.ranks[node]=independent_solve(
                self.rows[node],len(local_grammar(node)))
        self._fitted_at=len(self.log)

    def choose(self,world):
        step=len(self.log)
        if step>=LIMIT:raise ValueError("symbolic budget")
        last_effect=self.log[-1][2] if self.log else 0
        seen={(s,a) for s,a,_ in self.log}
        candidates=[]
        for i in range(8):
            h=sha256(f"WSP114|SYMBOLIC|v1|{self.nodes}|{world}|{step}|{last_effect}|{i}".encode()).digest()
            s=int.from_bytes(h[:8],"big")&((1<<self.nodes)-1)
            a=int.from_bytes(h[8:10],"big")%(2*self.nodes)
            if (s,a) not in seen:candidates.append((s,a))
        if not candidates:raise ValueError("symbolic candidate collision")
        # Distinct consequence-dependent policy: prefer probing least-used target.
        used=[0]*self.nodes
        for _,a,_ in self.log:used[a//2]+=1
        return min(candidates,key=lambda q:(used[q[1]//2],q[0],q[1]))

    def predict(self,state,action):
        self.fit()
        return independent_predict(state,action,self.coefficients,self.nodes)

class ConvergedRidge:
    """Independent, fully solved L2-regularized nonlinear-feature regression.

    This real-valued ridge model is diagnostic; exact symbolic is stronger and
    is never excluded from the winner selection. No access to hidden weights.
    """
    def __init__(self,nodes=64,l2=1.0):
        self.nodes=nodes
        self.l2=float(l2)
        self.log=[]
        self.weights=[np.zeros(len(local_grammar(j)),dtype=np.float64)
                      for j in range(nodes)]
        self._fitted_at=-1
        self.residuals=[]
        self.rows=[[] for _ in range(nodes)]

    def observe(self,state,action,effect):
        if len(self.log)>=LIMIT or (state,action) in {(s,a) for s,a,_ in self.log}:
            raise ValueError("ridge duplicate or budget")
        if type(effect)!=int or ((effect>>(action//2))&1)!=(action&1):
            raise ValueError("ridge invalid observation")
        self.log.append((state,action,effect))
        for j in range(self.nodes):
            if j==action//2:continue
            self.rows[j].append((feature_word(j,effect),
                ((state>>j)&1)^((effect>>j)&1)))

    def fit(self):
        if self._fitted_at==len(self.log):return
        self.residuals=[]
        for node in range(self.nodes):
            p=len(local_grammar(node))
            if p==0:
                self.weights[node]=np.zeros(0,dtype=np.float64)
                self.residuals.append(0.0)
                continue
            xs=[[int(mask>>k&1) for k in range(p)]
                for mask,_ in self.rows[node]]
            ys=[rhs for _,rhs in self.rows[node]]
            if not xs:
                self.weights[node]=np.zeros(p,dtype=np.float64)
                self.residuals.append(0.0)
                continue
            X=np.asarray(xs,dtype=np.float64)
            Y=np.asarray(ys,dtype=np.float64)
            gram=X.T@X+self.l2*np.eye(p)
            rhs=X.T@Y
            weights=np.linalg.solve(gram,rhs)
            residual=np.linalg.norm(gram@weights-rhs,ord=np.inf)
            if residual>1e-7:raise ValueError("ridge numerical fit not converged")
            self.weights[node]=weights
            self.residuals.append(float(residual))
        self._fitted_at=len(self.log)

    def predict(self,state,action):
        self.fit()
        after=0
        for node in range(self.nodes):
            if node==action//2:
                bit=action&1
            else:
                mask=feature_word(node,after)
                vec=self.weights[node]
                strength=sum(float(vec[k]) for k in range(len(vec)) if mask>>k&1)
                bit=((state>>node)&1)^int(strength>=0.5)
            after|=bit<<node
        return after
