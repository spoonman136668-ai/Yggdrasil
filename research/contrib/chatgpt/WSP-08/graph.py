"""WSP-08: learned representation depth in a homogeneous numeric neural graph.

PUBLIC SYNTHETIC DEV ONLY. The graph is constructed once from a known bounded
family of one-to-three-hop consequence features. No latent-class label or
environment rule is passed to the circuit. Its G2/G3 plastic synapses choose
the active depth by public prediction contradictions.

All inference and plasticity at RUNTIME use one numeric weighted-threshold
rule and one generic three-factor synaptic OR, not Python task-opcode dispatch.
This DOES NOT generate arbitrary unknown computational primitives.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass

N = 24
INPUT_N = 2*N+3
STATE_START = 1000
SEEDS = tuple(range(12))
MODES = (1,2,3)
PLASTIC_COUNT = N*N + 7*N + 3
MAX_FIXED = 2500
MAX_NODES = 1300
MAX_EDGES = 5000


def validate_state(s: int) -> int:
    if type(s) is not int or not STATE_START <= s < STATE_START+N:
        raise ValueError("WSP08_INVALID_STATE")
    return s


def validate_bit(v: int, label: str) -> int:
    if type(v) is not int or v not in (0,1):
        raise ValueError("WSP08_INVALID_"+label)
    return v


class PublicWorld:
    """Author-visible simulator; it never supplies hidden information to VM."""
    def __init__(self, seed: int, mode: int):
        if type(seed) is not int or seed not in SEEDS or type(mode) is not int or mode not in MODES:
            raise ValueError("WSP08_INVALID_WORLD")
        self.seed,self.mode=seed,mode
        rng=random.Random(seed*8999+101)
        identities=list(range(STATE_START,STATE_START+N))
        rng.shuffle(identities)
        self._mapping={(q,i):identities[3*q+i] for q in range(8) for i in range(3)}
        self._hidden={v:k for k,v in self._mapping.items()}
        self.train=tuple(sorted(self._mapping[q,i] for q in range(8) for i in (0,1)))
        self.test=tuple(sorted(self._mapping[q,2] for q in range(8)))

    def outcome(self,state:int,action:int,*,shift:bool=False)->tuple[int,int,int,int]:
        validate_state(state)
        validate_bit(action,"ACTION")
        if type(shift) is not bool:
            raise ValueError("WSP08_INVALID_SHIFT")
        q,replica=self._hidden[state]
        if action==0:
            result=q&1
            next_class=q//2
        else:
            result=(q>>(self.mode-1))&1
            if shift and replica==2:
                result^=1
            next_class=(q+2)%8
        return (state,action,result,self._mapping[next_class,(replica+1)%3])

    def public_events(self)->tuple[tuple[int,int,int,int],...]:
        return tuple(self.outcome(s,0) for s in range(STATE_START,STATE_START+N))+tuple(self.outcome(s,1) for s in self.train)


@dataclass(frozen=True)
class Graph:
    threshold:tuple[int,...]
    edges:tuple[tuple[int,int,int],...]
    incoming:tuple[tuple[tuple[int,int],...],...]
    start_weights:tuple[int,...]
    plastic_indices:tuple[int,...]
    fixed_indices:tuple[int,...]
    rules:tuple[tuple[int,int,int,int],...]
    reward_node:int
    valid_node:int
    fault_node:int
    depth2_slot:int
    depth3_slot:int
    fault_slot:int
    signature_slots:tuple[int,...]
    successor_slots:tuple[int,...]
    a1_coverage_slots:tuple[int,...]
    graph_sha256:str


class Builder:
    """Compile a numeric network ONCE; the host never calls this on observation."""
    def __init__(self):
        self.threshold=[0]*INPUT_N
        self.edges:list[tuple[int,int,int]]=[]
        self.weights:list[int]=[]
        self.plastic_idx:list[int]=[]
        self.fixed_idx:list[int]=[]
        self.rules:list[tuple[int,int,int,int]]=[]
        self.pos=self.parameter(1)
        self.neg=self.parameter(-1)

    def parameter(self, initial:int=0, *,plastic:bool=False)->int:
        if type(initial) is not int or (plastic and initial!=0):
            raise ValueError("WSP08_COMPILER_WEIGHT_INVALID")
        idx=len(self.weights)
        self.weights.append(initial)
        (self.plastic_idx if plastic else self.fixed_idx).append(idx)
        return idx

    def neuron(self, links:tuple[tuple[int,int],...], cutoff:int)->int:
        dest=len(self.threshold)
        if type(cutoff) is not int:
            raise ValueError("WSP08_NONINTEGER_THRESHOLD")
        self.threshold.append(cutoff)
        for src,weight in links:
            if not 0<=src<dest or not 0<=weight<len(self.weights):
                raise ValueError("WSP08_CYCLIC_GRAPH")
            self.edges.append((dest,src,weight))
        return dest

    def gate(self, sources:tuple[int,...],cutoff:int)->int:
        return self.neuron(tuple((src,self.pos) for src in sources),cutoff)

    def AND(self,*nodes:int)->int:
        return self.gate(nodes,len(nodes))

    def OR(self,*nodes:int)->int:
        return self.gate(nodes,1)

    def NOT(self,node:int)->int:
        return self.neuron(((node,self.neg),),0)

    def XOR(self,x:int,y:int)->int:
        return self.OR(self.AND(x,self.NOT(y)),self.AND(self.NOT(x),y))

    def EQ(self,x:int,y:int)->int:
        return self.NOT(self.XOR(x,y))

    def memory(self,inputs:tuple[int,...],coeffs:tuple[int,...])->int:
        return self.neuron(tuple(zip(inputs,coeffs)),1)

    def plastic(self,slot:int,pre:int,post:int,mod:int)->None:
        if slot not in self.plastic_idx:
            raise ValueError("WSP08_COMPILER_PLASTIC_OUTSIDE_MEMORY")
        self.rules.append((slot,pre,post,mod))


def build_graph()->Graph:
    b=Builder()
    positions=tuple(range(N))
    next_positions=tuple(range(N,2*N))
    action,reward,one=2*N,2*N+1,2*N+2

    # All persistent information is encoded in numeric synaptic slots.
    T=tuple(tuple(b.parameter(plastic=True) for _ in positions) for _ in positions)
    R0=tuple(b.parameter(plastic=True) for _ in positions)
    C0=tuple(b.parameter(plastic=True) for _ in positions)
    A1=tuple(b.parameter(plastic=True) for _ in positions)
    AC=tuple(b.parameter(plastic=True) for _ in positions)
    B1=tuple(b.parameter(plastic=True) for _ in positions)
    B2=tuple(b.parameter(plastic=True) for _ in positions)
    B3=tuple(b.parameter(plastic=True) for _ in positions)
    G2,G3,F=(b.parameter(plastic=True) for _ in range(3))

    succ1=tuple(b.memory(positions,T[i]) for i in positions)
    succ2=tuple(b.memory(succ1,T[i]) for i in positions)
    bits=(b.memory(positions,R0),
          b.memory(succ1,R0),
          b.memory(succ2,R0))
    cover=(b.memory(positions,C0),
           b.memory(succ1,C0),
           b.memory(succ2,C0))
    g2=b.neuron(((one,G2),),1)
    g3=b.neuron(((one,G3),),1)
    fault=b.neuron(((one,F),),1)
    ready=b.AND(*cover)
    safe=b.NOT(fault)

    # Read learned action1 memories and the three encoded training signatures.
    ac=tuple(b.neuron(((one,AC[j]),),1) for j in positions)
    label=tuple(b.neuron(((one,A1[j]),),1) for j in positions)
    stored=tuple(tuple(b.neuron(((one,group[j]),),1) for j in positions)
                 for group in (B1,B2,B3))
    eq=tuple(tuple(b.EQ(bits[k],stored[k][j]) for j in positions)
             for k in range(3))

    n_g2,n_g3=b.NOT(g2),b.NOT(g3)
    matches=[]
    contrast1=[]
    contrast2=[]
    contrast3=[]
    pos_matches=[]
    neg_matches=[]
    for j in positions:
        # For structural growth, compare NEW public outcomes against OLD
        # training signatures, independent of current active depth.
        mismatch=b.XOR(label[j],reward)
        common=b.AND(ac[j],mismatch)
        first=b.AND(common,eq[0][j])
        second=b.AND(first,eq[1][j])
        third=b.AND(second,eq[2][j])
        contrast1.append(first)
        contrast2.append(second)
        contrast3.append(third)

        selected=b.AND(ac[j],eq[0][j],
                       b.OR(n_g2,eq[1][j]),
                       b.OR(n_g3,eq[2][j]))
        matches.append(selected)
        pos_matches.append(b.AND(selected,label[j]))
        neg_matches.append(b.AND(selected,b.NOT(label[j])))
    conflict1=b.OR(*contrast1)
    conflict2=b.OR(*contrast2)
    conflict3=b.OR(*contrast3)
    positive=b.OR(*pos_matches)
    negative=b.OR(*neg_matches)
    unambiguous=b.XOR(positive,negative)
    valid=b.AND(ready,unambiguous,safe)

    # Detect incorrect repeated action0 observations numerically.
    known_a0=cover[0]
    transition_matches=b.OR(*(
        b.AND(succ1[j],next_positions[j]) for j in positions))
    transition_error=b.NOT(transition_matches)
    reward_error=b.XOR(bits[0],reward)
    action0=b.NOT(action)
    bad_action0=b.AND(action0,known_a0,
                      b.OR(transition_error,reward_error))
    missing=b.AND(action,b.NOT(ready))
    bad_new=b.AND(action,conflict3)
    contradiction=b.OR(bad_action0,missing,bad_new)
    permit=b.AND(safe,b.NOT(contradiction))
    learn0=b.AND(action0,permit,b.NOT(known_a0))
    # At action1 observation, store ALL three *publicly derivable*
    # consequence bits, while only depth switches activated by conflict.
    current_ac=b.memory(positions,AC)
    learn1=b.AND(action,permit,ready,b.NOT(current_ac))

    for i in positions:
        for j in positions:
            b.plastic(T[i][j],positions[j],next_positions[i],learn0)
    for j in positions:
        b.plastic(R0[j],positions[j],reward,learn0)
        b.plastic(C0[j],positions[j],one,learn0)
        b.plastic(A1[j],positions[j],reward,learn1)
        b.plastic(AC[j],positions[j],one,learn1)
        for group,bit in zip((B1,B2,B3),bits):
            b.plastic(group[j],positions[j],bit,learn1)
    b.plastic(G2,one,one,b.AND(action,conflict1,ready,safe))
    b.plastic(G3,one,one,b.AND(action,conflict2,ready,safe))
    b.plastic(F,one,one,contradiction)

    if (len(b.plastic_idx)!=PLASTIC_COUNT or
        len(b.rules)!=PLASTIC_COUNT or
        len(set(v[0] for v in b.rules))!=PLASTIC_COUNT or
        len(b.fixed_idx)>MAX_FIXED or
        len(b.threshold)>MAX_NODES or
        len(b.edges)>MAX_EDGES):
        raise ValueError(
            "WSP08_GRAPH_BUDGET_EXCEEDED "+
            str((len(b.fixed_idx),len(b.plastic_idx),len(b.threshold),len(b.edges))))
    incoming=[[] for _ in b.threshold]
    for dst,src,slot in b.edges:
        incoming[dst].append((src,slot))
    plan={"schema":"wsp08.compiled-synaptic-structure.v1",
          "threshold":b.threshold,"edges":b.edges,
          "fixed":[[i,b.weights[i]] for i in b.fixed_idx],
          "plastic":b.plastic_idx,"rules":b.rules,
          "outputs":[positive,valid,fault],"growth":[G2,G3]}
    digest=hashlib.sha256(json.dumps(plan,sort_keys=True,
                      separators=(",",":")).encode("ascii")).hexdigest()
    return Graph(tuple(b.threshold),tuple(b.edges),
                 tuple(tuple(x) for x in incoming),tuple(b.weights),
                 tuple(b.plastic_idx),tuple(b.fixed_idx),tuple(b.rules),
                 positive,valid,fault,G2,G3,F,
                 tuple(B1)+tuple(B2)+tuple(B3),
                 tuple(v for row in T for v in row),
                 tuple(AC),digest)


SPEC=build_graph()


class UniformVM:
    """One numeric threshold kernel and one local plastic synapse write kernel."""
    @staticmethod
    def evaluate(spec:Graph,weights:list[int],inputs:tuple[int,...])->list[int]:
        if (len(weights)!=len(spec.start_weights) or
            len(inputs)!=INPUT_N or
            any(type(x) is not int or x not in (0,1) for x in inputs)):
            raise ValueError("WSP08_VM_INPUT_INVALID")
        activity=list(inputs)+[0]*(len(spec.threshold)-INPUT_N)
        for node in range(INPUT_N,len(spec.threshold)):
            score=sum(weights[slot]*activity[src]
                      for src,slot in spec.incoming[node])
            activity[node]=int(score>=spec.threshold[node])
        return activity

    @staticmethod
    def update(spec:Graph,weights:list[int],activity:list[int])->None:
        for slot,pre,post,mod in spec.rules:
            weights[slot]=int(bool(
                weights[slot] or (activity[pre] and activity[post] and activity[mod])))


def encode(state:int,action:int=0,reward:int=0,
           successor:int|None=None)->tuple[int,...]:
    validate_state(state)
    if successor is None:
        successor=state
    validate_state(successor)
    validate_bit(action,"ACTION")
    validate_bit(reward,"REWARD")
    return (tuple(int(j==state-STATE_START) for j in range(N))+
            tuple(int(j==successor-STATE_START) for j in range(N))+
            (action,reward,1))


class GrowingSynapseCircuit:
    MAGIC=b"WSP8"
    GRADIENT_STEPS=0

    def __init__(self):
        self.weights=list(SPEC.start_weights)

    def observe(self,state:int,action:int,reward:int,successor:int)->None:
        activity=UniformVM.evaluate(SPEC,self.weights,
                                     encode(state,action,reward,successor))
        UniformVM.update(SPEC,self.weights,activity)

    def predict_a1(self,state:int)->int|None:
        a=UniformVM.evaluate(SPEC,self.weights,encode(state))
        return a[SPEC.reward_node] if a[SPEC.valid_node] else None

    @property
    def depth(self)->int:
        # Diagnostic only, not the inference pathway.
        return 1+self.weights[SPEC.depth2_slot]+self.weights[SPEC.depth3_slot]

    @property
    def fault(self)->int:
        return self.weights[SPEC.fault_slot]

    def active_plastic(self)->int:
        return sum(self.weights[slot]!=0 for slot in SPEC.plastic_indices)

    def programmed_sha256(self)->str:
        return hashlib.sha256(json.dumps(
            self.weights,separators=(",",":")).encode("ascii")).hexdigest()

    def snapshot(self)->bytes:
        raw=json.dumps({"schema":"wsp08.numeric-representation-state.v1",
                        "graph_sha256":SPEC.graph_sha256,
                        "weights":self.weights},
                       sort_keys=True,separators=(",",":")).encode("ascii")
        if len(raw)>16384:
            raise ValueError("WSP08_CHECKPOINT_TOO_LARGE")
        p=self.MAGIC+len(raw).to_bytes(4,"big")+raw
        return p+hashlib.sha256(p).digest()

    @classmethod
    def restore(cls,data:bytes)->"GrowingSynapseCircuit":
        if (type(data) is not bytes or len(data)<42 or len(data)>16424 or
            data[:4]!=cls.MAGIC or
            int.from_bytes(data[4:8],"big")!=len(data)-40 or
            hashlib.sha256(data[:-32]).digest()!=data[-32:]):
            raise ValueError("WSP08_CHECKPOINT_REJECTED")
        try:
            obj=json.loads(data[8:-32].decode("ascii"))
            if (type(obj) is not dict or set(obj)!=
                {"schema","graph_sha256","weights"} or
                obj["schema"]!="wsp08.numeric-representation-state.v1" or
                obj["graph_sha256"]!=SPEC.graph_sha256 or
                type(obj["weights"]) is not list or
                len(obj["weights"])!=len(SPEC.start_weights)):
                raise ValueError("BAD_SCHEMA")
            w=obj["weights"]
            if (any(type(x) is not int for x in w) or
                any(w[i]!=SPEC.start_weights[i] for i in SPEC.fixed_indices) or
                any(w[i] not in (0,1) for i in SPEC.plastic_indices)):
                raise ValueError("BAD_WEIGHT")
            m=cls()
            m.weights=w[:]
            if m.snapshot()!=data:
                raise ValueError("BAD_CANONICAL")
            return m
        except (ValueError,TypeError,KeyError,UnicodeError,OverflowError):
            raise ValueError("WSP08_CHECKPOINT_REJECTED") from None
