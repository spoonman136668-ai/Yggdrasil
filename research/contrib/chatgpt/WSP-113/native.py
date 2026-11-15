"""WSP-113: local numerical causal-graph synapse programming.

No hidden evaluator imports. The six directly written float32 coefficients
store edges in an acyclic four-node XOR intervention graph.
"""
from __future__ import annotations
from hashlib import sha256
import json
import struct

EDGES=((0,1),(0,2),(1,2),(0,3),(1,3),(2,3))
BUDGET=8
SUPPORT=tuple((state,action) for state in range(8) for action in range(8))
EIDX={edge:i for i,edge in enumerate(EDGES)}

def valid_query(state,action):
    if type(state) is not int or not 0<=state<16:
        raise ValueError("state out of range")
    if type(action) is not int or not 0<=action<8:
        raise ValueError("do-intervention out of range")

def transition_with_edges(state,action,weights):
    """Generic four-node causal-sweep kernel; graph resides in numerical weights."""
    valid_query(state,action)
    if len(weights)!=6:raise ValueError("expected six native synapses")
    forced_node=action//2
    forced_value=action%2
    new=0
    for j in range(4):
        if j==forced_node:
            v=forced_value
        else:
            v=(state>>j)&1
            for i in range(j):
                v ^= int(bool(weights[EIDX[(i,j)]]) and bool((new>>i)&1))
        new|=v<<j
    return new

def _solve(rows,width):
    """GF(2) causal equations; free coefficients deterministically zero."""
    basis={}
    for mask,rhs in rows:
        a=int(mask);b=int(rhs)
        while a:
            pivot=a.bit_length()-1
            if pivot not in basis:
                basis[pivot]=(a,b)
                break
            col,val=basis[pivot]
            a^=col
            b^=val
        if a==0 and b:raise ValueError("contradictory observed causal effects")
    solution=0
    for pivot in sorted(basis):
        row,rhs=basis[pivot]
        value=rhs^((solution&row).bit_count()&1)
        solution|=value<<pivot
    if solution>=1<<width:raise AssertionError("constraint width")
    return solution,len(basis)

class DirectCausalWriter:
    """Eight-intervention graph discovery with six direct numeric edge writes."""
    def __init__(self):
        self.observations=[]
        self.synapses=[0.0]*len(EDGES)
        self.ranks=[0,0,0,0]
        self.equations=[[],[],[],[]]

    @property
    def programmed_bytes(self):
        return struct.pack("<6f",*self.synapses)

    def predict(self,state,action):
        return transition_with_edges(state,action,self.synapses)

    def _reconstruct(self):
        equations=[[] for _ in range(4)]
        for state,action,effect in self.observations:
            node=action//2
            if ((effect>>node)&1)!=(action%2):
                raise ValueError("intervention target did not take forced value")
            for child in range(4):
                if child==node:continue
                parents=sum(((effect>>i)&1)<<i for i in range(child))
                rhs=((effect>>child)&1)^((state>>child)&1)
                equations[child].append((parents,rhs))
        new=[]
        ranks=[0]*4
        for child in range(4):
            coefficients,ranks[child]=_solve(equations[child],child)
            new.extend(float((coefficients>>parent)&1) for parent in range(child))
        if len(new)!=6:raise AssertionError("six edges required")
        self.synapses=[struct.unpack("<f",struct.pack("<f",w))[0] for w in new]
        self.ranks=ranks
        self.equations=equations

    def observe(self,state,action,effect):
        valid_query(state,action)
        if type(effect) is not int or not 0<=effect<16:
            raise ValueError("bad observed next state")
        if not (state,action) in SUPPORT:
            raise ValueError("original transfer observation outside support")
        if len(self.observations)>=BUDGET:
            raise ValueError("causal intervention budget exhausted")
        if (state,action) in ((s,a) for s,a,_ in self.observations):
            raise ValueError("duplicate intervention")
        self.observations.append((state,action,effect))
        try:self._reconstruct()
        except BaseException:
            self.observations.pop()
            self._reconstruct()
            raise

    def choose(self):
        if len(self.observations)>=BUDGET:
            raise ValueError("causal intervention budget exhausted")
        seen={(s,a) for s,a,_ in self.observations}
        def gain(pair):
            s,a=pair
            nxt=self.predict(s,a)
            score=0
            for j in range(1,4):
                if j==a//2:continue
                row=sum(((nxt>>i)&1)<<i for i in range(j))
                rhs=((nxt>>j)&1)^((s>>j)&1)
                _,new_rank=_solve(self.equations[j]+[(row,rhs)],j)
                if new_rank>self.ranks[j]:score+=new_rank-self.ranks[j]
            return score
        # Deterministic tie break chooses smallest state/action.
        return max((v for v in SUPPORT if v not in seen),
                   key=lambda v:(gain(v),-v[0],-v[1]))

    def triple(self,state,actions):
        current=state
        states=[]
        for action in actions:
            current=self.predict(current,action)
            states.append(current)
        return tuple(states)

    def checkpoint(self):
        fields={"observations":[list(x) for x in self.observations],
                "weights_le_f32":self.programmed_bytes.hex(),
                "ranks":self.ranks}
        blob=json.dumps(fields,sort_keys=True,separators=(",",":")).encode()
        return {"schema":"wsp113.direct-causal-synapses.v1",
                "fields":fields,"sha256":sha256(blob).hexdigest()}

    @classmethod
    def restore(cls,payload):
        if payload.get("schema")!="wsp113.direct-causal-synapses.v1":
            raise ValueError("unsupported native memory")
        fields=payload["fields"]
        digest=sha256(json.dumps(fields,sort_keys=True,
                   separators=(",",":")).encode()).hexdigest()
        if payload.get("sha256")!=digest:raise ValueError("altered memory seal")
        new=cls()
        for s,a,v in fields["observations"]:new.observe(s,a,v)
        if (new.programmed_bytes.hex()!=fields["weights_le_f32"] or
            new.ranks!=fields["ranks"]):
            raise ValueError("causal memory replay mismatch")
        return new
