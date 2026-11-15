"""WSP-117 source-safe relation identifiability fixture.

Tests only an inspectable synthetic algebra of unknown relation composition.
Not real Wikidata discovery, no protected source, no trained intelligence.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import random
import struct

RELATIONS=6
CANDIDATES=RELATIONS*RELATIONS
ENTITIES=64
PUBLIC_SEEDS=tuple(range(117000,117008))
PROTECTED_SEEDS=tuple(range(117800,117864))

def gated_seed(seed):
    if type(seed) is not int or seed not in PUBLIC_SEEDS:
        raise PermissionError("WSP117_PROTECTED_OR_UNREGISTERED_SOURCE")
    return seed

@dataclass(frozen=True)
class World:
    seed:int
    edges:tuple[tuple[int,...],...]

    def after(self,src:int,rel:int)->int:
        if type(src) is not int or type(rel) is not int or not 0<=src<ENTITIES or not 0<=rel<RELATIONS:
            raise ValueError("WSP117_INVALID_PUBLIC_FACT")
        return self.edges[rel][src]

    def compose(self,src:int,rel0:int,rel1:int)->int:
        return self.after(self.after(src,rel0),rel1)

    def visible_edges_sha256(self)->str:
        h=sha256()
        for rel in self.edges:
            for obj in rel:h.update(struct.pack("<I",obj))
        return h.hexdigest()

def world(seed:int)->World:
    gated_seed(seed)
    rng=random.Random(seed)
    edges=[]
    for _ in range(RELATIONS):
        perm=list(range(ENTITIES))
        rng.shuffle(perm)
        edges.append(perm)
    # Force two primitive relation laws to agree at the one public
    # intermediate node. They still disagree elsewhere (a valid ambiguity).
    middle=edges[0][0]
    j=edges[5].index(edges[4][middle])
    edges[5][middle],edges[5][j]=edges[5][j],edges[5][middle]
    assert edges[5][middle]==edges[4][middle]
    assert edges[5]!=edges[4]
    return World(seed,tuple(tuple(x) for x in edges))

def evidence(w:World,operator:tuple[int,int],sources:tuple[int,...]):
    if type(operator) is not tuple or len(operator)!=2 or any(type(x) is not int or not 0<=x<RELATIONS for x in operator):
        raise ValueError("WSP117_OPERATOR")
    if not sources or len(set(sources))!=len(sources) or any(type(x) is not int or not 0<=x<ENTITIES for x in sources):
        raise ValueError("WSP117_DEMONSTRATION")
    return tuple((s,w.compose(s,*operator)) for s in sources)

def legal_operators(w:World,demos:tuple[tuple[int,int],...]):
    if not demos:raise ValueError("WSP117_UNOBSERVED_TARGET")
    if len(set(s for s,_ in demos))!=len(demos):
        raise ValueError("WSP117_DUPLICATE_SOURCE_EXAMPLE")
    for s,o in demos:
        if type(s) is not int or type(o) is not int or not 0<=s<ENTITIES or not 0<=o<ENTITIES:
            raise ValueError("WSP117_PUBLIC_DEMONSTRATION")
    return tuple((a,b) for a in range(RELATIONS) for b in range(RELATIONS)
                 if all(w.compose(s,a,b)==o for s,o in demos))


class NumericDirectRelations:
    """36 directly programmed int32 contradiction counters, no gradients."""
    MAGIC=b"W117"
    def __init__(self):
        import numpy as np
        self.w=np.zeros((RELATIONS,RELATIONS),dtype=np.int32)
        self.observations=0

    def learn(self,w:World,demos):
        valid=legal_operators(w,demos)
        valid=set(valid)
        for a in range(RELATIONS):
            for b in range(RELATIONS):
                if (a,b) not in valid:self.w[a,b]+=1
        self.observations+=len(demos)
        return self

    def hypotheses(self):
        min_count=int(self.w.min())
        return tuple((a,b) for a in range(RELATIONS) for b in range(RELATIONS)
                     if int(self.w[a,b])==min_count)

    def predict(self,w:World,src:int):
        options=self.hypotheses()
        if len(options)!=1:return None
        return w.compose(src,*options[0])

    def cold(self):
        raw=self.MAGIC+struct.pack("<I",self.observations)+self.w.astype("<i4").tobytes()
        return raw+sha256(raw).digest()

    @classmethod
    def restore(cls,data:bytes):
        import numpy as np
        if type(data) is not bytes or len(data)!=4+4+CANDIDATES*4+32 or data[:4]!=cls.MAGIC:
            raise ValueError("WSP117_COLD_SCHEMA")
        if sha256(data[:-32]).digest()!=data[-32:]:
            raise ValueError("WSP117_TAMPER")
        x=cls()
        x.observations=struct.unpack("<I",data[4:8])[0]
        x.w=np.frombuffer(data[8:-32],dtype="<i4").astype(np.int32,copy=True).reshape(RELATIONS,RELATIONS)
        if int(x.w.min())<0 or x.observations>ENTITIES*PUBLIC_SEEDS.__len__()*RELATIONS:
            raise ValueError("WSP117_NUMERIC_CAPACITY")
        return x


class IndependentExactSymbolic:
    """Independent exact strong control over identical public facts."""
    def __init__(self,w:World,demos):
        self.possible=legal_operators(w,demos)

    def predict(self,w:World,src:int):
        if len(self.possible)!=1:return None
        a,b=self.possible[0]
        return w.after(w.after(src,a),b)


def find_identifiable_demonstrations(w,op,*,max_observations=12):
    """Public fit-only heuristic, never uses unseen target labels."""
    observations=[]
    for src in range(ENTITIES):
        observations.append((src,w.compose(src,*op)))
        if len(legal_operators(w,tuple(observations)))==1:
            return tuple(observations)
        if len(observations)>=max_observations:break
    return tuple(observations)
