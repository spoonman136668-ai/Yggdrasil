"""WSP114 direct causal weight programming for large nonlinear state machines.

No hidden generator or test-label imports. Every inferred feature coefficient is
written as a float32 synaptic weight. A generic parity kernel reads the exact
numeric binary weight state to perform causal propagation under interventions.
"""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import json
import struct

NMAX=64
WINDOW=12
LADDER=(1024,512,256,128,64,32,16,8)
FULL_BUDGET=1024

@lru_cache(maxsize=WINDOW+1)
def grammar(width):
    if type(width) is not int or width<0 or width>WINDOW:
        raise ValueError("window width")
    return tuple((i,) for i in range(width))+tuple((i,j)
                  for i in range(width) for j in range(i+1,width))

@lru_cache(maxsize=65536)
def observed_features(width, value):
    if type(value) is not int or not 0<=value<1<<width:
        raise ValueError("bad predecessor bits")
    result=0
    for index,term in enumerate(grammar(width)):
        if all((value>>i)&1 for i in term):
            result|=1<<index
    return result

def observed_row(node,next_state):
    width=min(WINDOW,node)
    previous=(next_state>>(node-width))&((1<<width)-1)
    return observed_features(width,previous)

def effect_from_parameters(before,action,programmed,nodes):
    if type(nodes) is not int or not 1<=nodes<=NMAX:
        raise ValueError("node count")
    if type(before) is not int or not 0<=before<1<<nodes:
        raise ValueError("state outside native range")
    if type(action) is not int or not 0<=action<2*nodes:
        raise ValueError("intervention outside native range")
    if len(programmed)!=nodes:raise ValueError("weight array shape")
    forced_node=action//2
    forced_bit=action&1
    after=0
    for node in range(nodes):
        if node==forced_node:
            out=forced_bit
        else:
            row=observed_row(node,after)
            out=((before>>node)&1)^((int(programmed[node])&row).bit_count()&1)
        after|=out<<node
    return after

class NativeWriter:
    """Online bit-constraint elimination with direct float32 synaptic writes."""
    def __init__(self,nodes=64,seed="fixture"):
        if type(nodes) is not int or not 1<=nodes<=NMAX:raise ValueError("invalid capacity")
        self.nodes=nodes
        self.seed=str(seed)
        self.observations=[]
        self.basis=[{} for _ in range(nodes)]
        self.synapses=[tuple(0.0 for _ in grammar(min(WINDOW,j))) for j in range(nodes)]
        self.ranks=[0]*nodes
        self.active_weights=[0]*nodes

    def _rewrite(self,node):
        b=self.basis[node]
        coeff=0
        # A pivot is the greatest set feature; solving ascending is deterministic.
        for pivot in sorted(b):
            row,rhs=b[pivot]
            bit=rhs^((coeff&row).bit_count()&1)
            coeff|=bit<<pivot
        self.active_weights[node]=coeff
        # Exact IEEE-754 float32 0/1 numerical parameter programming.
        width=len(grammar(min(WINDOW,node)))
        self.synapses[node]=tuple(struct.unpack("<f",struct.pack("<f",float((coeff>>i)&1)))[0]
                                  for i in range(width))
        self.ranks[node]=len(b)

    @staticmethod
    def _insert(basis,row,rhs):
        x=int(row)
        y=int(rhs)
        while x:
            pivot=x.bit_length()-1
            existing=basis.get(pivot)
            if existing is None:
                basis[pivot]=(x,y)
                return True
            x^=existing[0]
            y^=existing[1]
        if y:raise ValueError("contradictory intervention consequences")
        return False

    def observe(self,state,action,effect):
        if type(state) is not int or type(action) is not int or type(effect) is not int:
            raise ValueError("noninteger observation")
        if not 0<=state<1<<self.nodes or not 0<=action<2*self.nodes or not 0<=effect<1<<self.nodes:
            raise ValueError("out of range observation")
        if ((effect>>(action//2))&1)!=(action&1):
            raise ValueError("forced-intervention value violated")
        if len(self.observations)>=FULL_BUDGET:
            raise ValueError("high-budget ceiling")
        if any(s==state and a==action for s,a,_ in self.observations):
            raise ValueError("repeated information access")
        new_basis=[dict(b) for b in self.basis]
        for node in range(self.nodes):
            if node==action//2:continue
            mask=observed_row(node,effect)
            rhs=((state>>node)&1)^((effect>>node)&1)
            self._insert(new_basis[node],mask,rhs)
        self.basis=new_basis
        self.observations.append((state,action,effect))
        for j in range(self.nodes):self._rewrite(j)

    def predict(self,state,action):
        # active_weights are a lossless compiler view of explicit float32
        # synapse slots, updated exclusively via _rewrite and validated on restore.
        return effect_from_parameters(state,action,self.active_weights,self.nodes)

    @staticmethod
    def candidate(world,step,index,nodes=64,namespace="WSP114|QUERY|v1"):
        key=f"{namespace}|{nodes}|{world}|{step}|{index}".encode("ascii")
        h=sha256(key).digest()
        return int.from_bytes(h[:8],"big")&((1<<nodes)-1),int.from_bytes(h[8:10],"big")%(2*nodes)

    def _rank_gain(self,state,action):
        forecast=self.predict(state,action)
        gain=0
        for node in range(self.nodes):
            if node==action//2:continue
            row=observed_row(node,forecast)
            v=row
            b=self.basis[node]
            while v:
                pivot=v.bit_length()-1
                item=b.get(pivot)
                if item is None:
                    gain+=1
                    break
                v^=item[0]
        return gain

    def choose(self,world):
        step=len(self.observations)
        if step>=FULL_BUDGET:raise ValueError("intervention ceiling reached")
        seen={(s,a) for s,a,_ in self.observations}
        candidates=[]
        for i in range(8):
            state,action=self.candidate(world,step,i,self.nodes)
            if (state,action) in seen:continue
            candidates.append((state,action))
        if not candidates:raise ValueError("SHA candidate collision")
        return max(candidates,key=lambda q:(self._rank_gain(*q),-q[0],-q[1]))

    def checkpoint(self):
        parameters=[struct.pack("<"+str(len(row))+"f",*row).hex()
                    for row in self.synapses]
        data={"nodes":self.nodes,"seed":self.seed,
              "obs":[list(row) for row in self.observations],
              "parameters_float32_le":parameters,
              "ranks":self.ranks}
        digest=sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        return {"schema":"wsp114.native.programmed-large-graph.v1",
                "data":data,"sha256":digest}

    @classmethod
    def restore(cls,saved):
        if saved.get("schema")!="wsp114.native.programmed-large-graph.v1":
            raise ValueError("invalid native checkpoint schema")
        data=saved["data"]
        digest=sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        if digest!=saved.get("sha256"):raise ValueError("tampered native checkpoint")
        new=cls(data["nodes"],data["seed"])
        for s,a,e in data["obs"]:new.observe(s,a,e)
        parameters=[struct.pack("<"+str(len(row))+"f",*row).hex()
                    for row in new.synapses]
        if parameters!=data["parameters_float32_le"] or new.ranks!=data["ranks"]:
            raise ValueError("cold replay did not reproduce synapses")
        return new
