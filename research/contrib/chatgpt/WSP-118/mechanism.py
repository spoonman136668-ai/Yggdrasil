"""WSP-118: source-safe factual-coverage threshold for named 3-hop laws.

This is a synthetic observable-information screen, not autonomous creation of a
new causal grammar. WSP-117 only admitted two-hop operators; this fixture
permits assembling three-hop candidates. The exact symbolic control has the
same public data and grammar. No real Wikidata, protected, or held science used.
"""
from __future__ import annotations

from array import array
from dataclasses import dataclass
from hashlib import sha256
import random
import struct

ENTITIES = 64
PREDICATES = 6
TRIPLES = tuple((a,b,c) for a in range(6) for b in range(6) for c in range(6))
SHORT = tuple((a,) for a in range(6)) + tuple((a,b) for a in range(6) for b in range(6))
PUBLIC_SEEDS = tuple(range(118000, 118024))
RESERVED_SCIENCE = tuple(range(118800, 118864))
DENSITIES = (0,16,64,128,192,224,256)
TRAIN_SOURCES = 12
HELD_SOURCES = 24
MIN_EVIDENCE = 3
MAGIC = b"W118"
EDGE_DOMAIN = b"WSP118-DENSITY-v1\x00"


def admit_seed(seed: int):
    if type(seed) is not int or seed not in PUBLIC_SEEDS:
        raise PermissionError("WSP118_ONLY_PUBLIC_FIXTURE_SEED")
    return seed


@dataclass(frozen=True)
class World:
    seed: int
    edges: tuple[tuple[int, ...], ...]
    targets: tuple[tuple[int,int,int], ...]
    sources: tuple[int, ...]

    def actual(self, source: int, law: tuple[int,...]) -> int:
        if not 0 <= source < ENTITIES or any(not 0 <= r < PREDICATES for r in law):
            raise ValueError("WSP118_INVALID_PRIVATE_EVALUATOR_QUERY")
        for r in law:
            source = self.edges[r][source]
        return source

    def public_graph(self, threshold: int):
        if type(threshold) is not int or threshold not in DENSITIES:
            raise ValueError("WSP118_DENSITY_NOT_PREREGISTERED")
        exposed = []
        for r in range(PREDICATES):
            by_source = {}
            for s in range(ENTITIES):
                rank = sha256(EDGE_DOMAIN + struct.pack("<III",self.seed,r,s)).digest()[0]
                if rank < threshold:
                    by_source[s] = self.edges[r][s]
            exposed.append(by_source)
        return tuple(exposed)

    def public_examples(self, law: tuple[int,int,int]):
        # The first 12 entity sources are chosen from the world seed alone.
        return tuple((s,self.actual(s,law)) for s in self.sources[:TRAIN_SOURCES])

    def held_subjects(self):
        return self.sources[TRAIN_SOURCES:TRAIN_SOURCES+HELD_SOURCES]


def new_public_world(seed: int) -> World:
    admit_seed(seed)
    rng = random.Random(seed)
    edges = tuple(tuple(rng.sample(range(ENTITIES), ENTITIES)) for _ in range(PREDICATES))
    def execute(source, law):
        for r in law:
            source = edges[r][source]
        return source
    short_answers = {tuple(execute(s,law) for s in range(ENTITIES)) for law in SHORT}
    laws = list(TRIPLES)
    rng.shuffle(laws)
    long_laws=[]
    for law in laws:
        answers=tuple(execute(s,law) for s in range(ENTITIES))
        if answers not in short_answers and law not in long_laws:
            long_laws.append(law)
        if len(long_laws)==4:
            break
    if len(long_laws)!=4:
        raise AssertionError("WSP118_NO_NEW_LENGTH_THREE_LAWS")
    sources=list(range(ENTITIES))
    rng.shuffle(sources)
    return World(seed,edges,tuple(long_laws),tuple(sources))


def visible_walk(graph,source:int,law:tuple[int,...]):
    if type(source) is not int or not 0 <= source < ENTITIES:
        raise ValueError("WSP118_INVALID_PUBLIC_SUBJECT")
    for rel in law:
        if type(rel) is not int or not 0<=rel<PREDICATES:
            raise ValueError("WSP118_INVALID_PUBLIC_OPERATOR")
        if source not in graph[rel]:
            return None
        source=graph[rel][source]
    return source


def examples_guard(demos):
    if not isinstance(demos,tuple) or not demos or len(demos)>TRAIN_SOURCES:
        raise ValueError("WSP118_INVALID_PUBLIC_DEMONSTRATIONS")
    seen=set()
    for src,dst in demos:
        if type(src) is not int or type(dst) is not int or not (0<=src<ENTITIES and 0<=dst<ENTITIES) or src in seen:
            raise ValueError("WSP118_DUPLICATE_OR_PRIVATE_LABEL")
        seen.add(src)


class NumericTripleWeights:
    """Two 32-bit integer synapses per law: witnessed matches and conflicts."""
    def __init__(self,graph,threshold):
        if type(threshold) is not int or threshold not in DENSITIES:
            raise ValueError("WSP118_INVALID_DENSITY")
        self.graph=graph
        self.threshold=threshold
        self.synapses=array("i",[0])*(len(TRIPLES)*2)
        if self.synapses.itemsize!=4:
            raise RuntimeError("WSP118_NON_32BIT_SIGNED_INT_PLATFORM")
        self.examples=0

    def learn(self,demos):
        examples_guard(demos)
        if self.examples!=0:
            raise ValueError("WSP118_REPEATED_OR_UNCERTAIN_EFFECT_FIT")
        for i,law in enumerate(TRIPLES):
            yes=no=0
            for source,target in demos:
                observed=visible_walk(self.graph,source,law)
                if observed is None:
                    continue
                if observed==target:yes+=1
                else:no+=1
            self.synapses[2*i]=yes
            self.synapses[2*i+1]=no
        self.examples=len(demos)
        return self

    def acceptable(self):
        if self.examples<1:
            raise RuntimeError("WSP118_UNTRAINED")
        return tuple(law for i,law in enumerate(TRIPLES)
                     if self.synapses[2*i]>=MIN_EVIDENCE and self.synapses[2*i+1]==0)

    def law(self):
        possible=self.acceptable()
        return possible[0] if len(possible)==1 else None

    def infer(self,source):
        law=self.law()
        return None if law is None else visible_walk(self.graph,source,law)

    def snapshot(self):
        if len(self.synapses)!=len(TRIPLES)*2:
            raise ValueError("WSP118_MUTATED_CAPACITY")
        raw=MAGIC+struct.pack("<II",self.threshold,self.examples)+struct.pack(
            "<"+str(len(self.synapses))+"i",*self.synapses)
        return raw+sha256(raw).digest()

    @classmethod
    def restore(cls,graph,snapshot:bytes):
        length=4+8+len(TRIPLES)*2*4+32
        if type(snapshot) is not bytes or len(snapshot)!=length or snapshot[:4]!=MAGIC:
            raise ValueError("WSP118_BAD_COLD_SCHEMA")
        if sha256(snapshot[:-32]).digest()!=snapshot[-32:]:
            raise ValueError("WSP118_COLD_TAMPER_REJECTED")
        t,n=struct.unpack("<II",snapshot[4:12])
        if t not in DENSITIES or n<1 or n>TRAIN_SOURCES:
            raise ValueError("WSP118_BAD_COLD_STATE")
        raw=struct.unpack("<"+str(len(TRIPLES)*2)+"i",snapshot[12:-32])
        if any(x<0 or x>n for x in raw):
            raise ValueError("WSP118_COLD_INVALID_COUNTS")
        m=cls(graph,t)
        m.synapses=array("i",raw)
        m.examples=n
        return m


class ExactSymbolicSynthesizer:
    """Independent Python dictionary/set program search on equal public data."""
    def __init__(self,graph):
        self.facts=tuple(dict(x) for x in graph)
        self.solutions=()

    def learn(self,demos):
        examples_guard(demos)
        candidates=[]
        for first in range(PREDICATES):
            for second in range(PREDICATES):
                for third in range(PREDICATES):
                    complete=0
                    violates=False
                    for subject,target in demos:
                        z=self.facts[first].get(subject)
                        if z is None:continue
                        z=self.facts[second].get(z)
                        if z is None:continue
                        z=self.facts[third].get(z)
                        if z is None:continue
                        if z!=target:
                            violates=True
                            break
                        complete+=1
                    if not violates and complete>=MIN_EVIDENCE:
                        candidates.append((first,second,third))
        self.solutions=tuple(candidates)
        return self

    def law(self):
        return self.solutions[0] if len(self.solutions)==1 else None

    def infer(self,source):
        rule=self.law()
        if rule is None:return None
        z=source
        for rel in rule:
            z=self.facts[rel].get(z)
            if z is None:return None
        return z


def short_grammar_control(graph,demos):
    examples_guard(demos)
    options=[]
    for law in SHORT:
        checked=0
        bad=False
        for subject,target in demos:
            z=visible_walk(graph,subject,law)
            if z is None:continue
            if z!=target:
                bad=True;break
            checked+=1
        if not bad and checked>=MIN_EVIDENCE:
            options.append(law)
    return options[0] if len(options)==1 else None


def shuffled_examples(demos,seed:int,law_index:int):
    examples_guard(demos)
    rng=random.Random(seed*257+law_index*109+118)
    outcomes=[y for _,y in demos]
    rng.shuffle(outcomes)
    if outcomes==[y for _,y in demos] and len(outcomes)>1:
        outcomes=outcomes[1:]+outcomes[:1]
    return tuple((s,y) for (s,_),y in zip(demos,outcomes))
