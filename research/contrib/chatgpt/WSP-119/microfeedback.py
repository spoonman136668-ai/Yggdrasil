"""WSP-119 public-only, independently grounded internal microfeedback.

Every hypothesis ranks possible next public evidence requests WITHOUT its
answers, then updates local numeric contradiction/support weights ONLY AFTER
an external toy-world consequence is revealed. Not self-rewarding or science.
"""
from __future__ import annotations

from array import array
from collections import Counter
from hashlib import sha256
import random
import struct
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"WSP-118"))
import mechanism as M

PUBLIC_SEEDS=tuple(range(119000,119024))
RESERVED_SCIENCE=tuple(range(119800,119864))
TIERS=(64,128,192,256)
EXPOSURES=(0,1,2,3,4,6,8,12)
MAX_SOURCE_CALLS=12
ARM_NAMES=("DIRECT_ACTIVE","DIRECT_PASSIVE","DIRECT_NO_UPDATE","SYMBOLIC_ACTIVE")
MAGIC=b"W119"


def source_safe_world(seed:int):
    if type(seed) is not int or seed not in PUBLIC_SEEDS:
        raise PermissionError("WSP119_ONLY_PUBLIC_SYNTHETIC_SEEDS")
    rng=random.Random(seed)
    edges=tuple(tuple(rng.sample(range(M.ENTITIES),M.ENTITIES))
                for _ in range(M.PREDICATES))
    def execute(s,law):
        for rel in law:s=edges[rel][s]
        return s
    short={tuple(execute(s,rule) for s in range(M.ENTITIES))
           for rule in M.SHORT}
    programs=list(M.TRIPLES)
    rng.shuffle(programs)
    laws=[]
    for rule in programs:
        if tuple(execute(s,rule) for s in range(M.ENTITIES)) not in short:
            laws.append(rule)
            if len(laws)==4:break
    if len(laws)!=4:raise AssertionError("WSP119_BAD_LAW_GENERATION")
    sources=list(range(M.ENTITIES))
    rng.shuffle(sources)
    return M.World(seed,edges,tuple(laws),tuple(sources))


def inquiry_pool(world:M.World):
    return tuple(world.sources[:40])


def held_subjects(world:M.World):
    return tuple(world.sources[40:])


def _gini_score(graph,lawset,subject):
    """Gini of predicted public outcomes, NO actual hidden target access."""
    counts=Counter(M.visible_walk(graph,subject,law) for law in lawset)
    n=sum(counts.values())
    return n*n-sum(k*k for k in counts.values())


def choose_discriminating_source(graph,lawset,available):
    if not available:raise ValueError("WSP119_NO_UNUSED_INQUIRIES")
    # Stable tie ordering. The world source permutation has NO target labels.
    return max(sorted(available),key=lambda s:_gini_score(graph,lawset,s))


class EvidenceSource:
    """Environment result revealed only once the chosen legal action executes."""
    def __init__(self,world,hidden_law):
        if hidden_law not in world.targets:
            raise ValueError("WSP119_SOURCE_LAW_CUSTODY")
        self._world=world
        self._law=hidden_law
        self.allowed=set(inquiry_pool(world))
        self.used=set()
        self.receipt=sha256()

    @property
    def count(self):return len(self.used)

    def query(self,subject):
        if type(subject) is not int or subject not in self.allowed:
            raise PermissionError("WSP119_HELD_OR_UNREGISTERED_QUERY_DENIED")
        if subject in self.used or len(self.used)>=MAX_SOURCE_CALLS:
            raise PermissionError("WSP119_REPLAY_OR_BUDGET_DENIED")
        self.used.add(subject)
        result=self._world.actual(subject,self._law)
        self.receipt.update(struct.pack("<II",subject,result))
        return result


class NumericFeedback:
    """Bounded native-style, no-gradient signed integer microfeedback weights."""
    def __init__(self,graph,active=True,updates=True):
        self.graph=graph
        self.active=bool(active)
        self.updates=bool(updates)
        self.w=array("i",[0])*(len(M.TRIPLES)*2)
        if self.w.itemsize!=4:raise RuntimeError("WSP119_PLATFORM_NOT_INT32")
        self.count=0
        self.total_error_events=0
        self.seen=set()

    def candidates(self):
        return tuple(law for i,law in enumerate(M.TRIPLES) if self.w[2*i+1]==0)

    def choose(self,pool):
        avail=tuple(s for s in pool if s not in self.seen)
        if not avail:raise ValueError("WSP119_ALL_CANDIDATE_SUBJECTS_USED")
        return (choose_discriminating_source(self.graph,self.candidates(),avail)
                if self.active else avail[0])

    def observe(self,subject,verified_outcome):
        if type(subject) is not int or type(verified_outcome) is not int or not 0<=verified_outcome<M.ENTITIES:
            raise ValueError("WSP119_VERIFIED_SOURCE_RESULT_REQUIRED")
        if subject in self.seen:
            raise ValueError("WSP119_NONIDEMPOTENT_UPDATE_DENIED")
        if self.count>=MAX_SOURCE_CALLS:
            raise ValueError("WSP119_SOURCE_BUDGET")
        self.seen.add(subject)
        self.count+=1
        if not self.updates:return 0
        rejected=0
        for i,law in enumerate(M.TRIPLES):
            predicted=M.visible_walk(self.graph,subject,law)
            if predicted is None:continue
            j=2*i+(0 if predicted==verified_outcome else 1)
            if self.w[j]>=2**31-2:raise OverflowError("WSP119_INT32_SATURATION")
            if predicted!=verified_outcome and self.w[2*i+1]==0:
                rejected+=1
            self.w[j]+=1
        self.total_error_events+=rejected
        return rejected

    def law(self):
        possibilities=[rule for i,rule in enumerate(M.TRIPLES)
                       if self.w[2*i]>=3 and self.w[2*i+1]==0]
        return possibilities[0] if len(possibilities)==1 else None

    def infer(self,subject):
        law=self.law()
        return None if law is None else M.visible_walk(self.graph,subject,law)

    def snapshot(self):
        binary=MAGIC+struct.pack("<I",self.count)+struct.pack(
            "<"+str(len(self.w))+"i",*self.w)
        return binary+sha256(binary).digest()

    @classmethod
    def restore(cls,graph,bytestr):
        expected=4+4+len(M.TRIPLES)*2*4+32
        if type(bytestr) is not bytes or len(bytestr)!=expected or bytestr[:4]!=MAGIC:
            raise ValueError("WSP119_COLD_SCHEMA")
        if sha256(bytestr[:-32]).digest()!=bytestr[-32:]:
            raise ValueError("WSP119_COLD_TAMPER")
        count=struct.unpack("<I",bytestr[4:8])[0]
        scores=struct.unpack("<"+str(len(M.TRIPLES)*2)+"i",bytestr[8:-32])
        if count>MAX_SOURCE_CALLS or any(x<0 or x>count for x in scores):
            raise ValueError("WSP119_COLD_INVALID_WEIGHTS")
        m=cls(graph)
        m.w=array("i",scores)
        m.count=count
        # Source-query ledger and which subjects were used are EXTERNAL;
        # the snapshot only seals learned numeric synapses, not full agent state.
        return m


class IndependentSymbolicFeedback:
    """Equal-input active control using set elimination, not numeric weights."""
    def __init__(self,graph):
        self.graph=tuple(dict(edges) for edges in graph)
        self.observed=[]
        self.seen=set()

    def _trace(self,s,law):
        for relation in law:
            s=self.graph[relation].get(s)
            if s is None:return None
        return s

    def candidates(self):
        options=[]
        for a in range(M.PREDICATES):
            for b in range(M.PREDICATES):
                for c in range(M.PREDICATES):
                    law=(a,b,c)
                    if all(self._trace(s,law) in (None,o) for s,o in self.observed):
                        options.append(law)
        return tuple(options)

    def choose(self,pool):
        available=tuple(s for s in pool if s not in self.seen)
        if not available:raise ValueError("WSP119_NO_INQUIRIES")
        programs=self.candidates()
        def symbolic_gini(s):
            choices=Counter(self._trace(s,law) for law in programs)
            n=sum(choices.values())
            return n*n-sum(k*k for k in choices.values())
        return max(sorted(available),key=symbolic_gini)

    def observe(self,subject,outcome):
        if subject in self.seen or len(self.observed)>=MAX_SOURCE_CALLS:
            raise ValueError("WSP119_SYMBOLIC_REPLAY_OR_BUDGET")
        if type(subject) is not int or type(outcome) is not int or not 0<=outcome<M.ENTITIES:
            raise ValueError("WSP119_SYMBOLIC_PUBLIC_OBSERVATION")
        self.seen.add(subject)
        self.observed.append((subject,outcome))

    def law(self):
        solutions=[]
        for law in self.candidates():
            support=sum(self._trace(s,law)==o
                        for s,o in self.observed
                        if self._trace(s,law) is not None)
            if support>=3:solutions.append(law)
        return solutions[0] if len(solutions)==1 else None

    def infer(self,subject):
        law=self.law()
        return None if law is None else self._trace(subject,law)
