"""Independent symbolic and fully optimized conventional WSP111 controls.

Both receive the identical million original facts and 3000 observed 3+2
sensory consequences, but no output relation IDs, class count, hidden oracle
or heldout answer labels. A conventional logistic fitter from the qualified
WSP110 control is reused; it receives no access to any hidden law.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import importlib.util
import sys

HERE=Path(__file__).resolve().parent
_SPEC=importlib.util.spec_from_file_location(
    "wsp110_frozen_logistic_only",HERE.parent/"WSP-110"/"controls.py")
if _SPEC is None or _SPEC.loader is None:
    raise ImportError("prior qualified conventional optimizer unavailable")
_PARENT=importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name]=_PARENT
_SPEC.loader.exec_module(_PARENT)
RegularizedLogistic=_PARENT.RegularizedLogistic

N_GROUPS=25000
N_SUPPORT=3000


def _kind(chain):
    a,b,_=chain
    return 4*a+b-4


class IndependentSymbolicInventor:
    def __init__(self):
        self.facts=set()
        self.stage1_positive=defaultdict(lambda:[0,0,0])
        self.stage1_total=defaultdict(int)
        self.stage2_positive=defaultdict(lambda:[0,0])
        self.stage2_total=defaultdict(int)
        self.first_signatures=()
        self.second_signatures=()
        self.derived1=set()
        self.derived2=set()
        self.group_first_rel={}
        self.group_second_rel={}

    def load_facts(self,sources,relations,targets):
        if self.facts:
            raise ValueError("symbolic source facts already loaded")
        self.facts={(int(s),int(r),int(t))
                    for s,r,t in zip(sources,relations,targets)}
        if len(self.facts)!=1_000_000:
            raise ValueError("symbolic requires identical 1m observed input facts")

    def chain(self,group):
        if type(group) is not int or not 0<=group<N_GROUPS:
            raise ValueError("group outside supported fact set")
        s=4*group
        aa=[r for r in range(4) if (s,r,s+1) in self.facts]
        bb=[r for r in range(4,8) if (s+1,r,s+2) in self.facts]
        cc=[r for r in range(10,14) if (s+2,r,s+3) in self.facts]
        if len(aa)!=1 or len(bb)!=1 or len(cc)!=1:
            raise ValueError("symbolic three-edge witness missing")
        return aa[0],bb[0],cc[0]

    def learn_first(self,feedback):
        seen=set()
        for g,e1,e2 in feedback:
            if (type(g) is not int or g in seen or not 0<=g<N_SUPPORT
                    or type(e1) is not int or not 0<=e1<8
                    or type(e2) is not int or not 0<=e2<4):
                raise ValueError("invalid or repeated feedback")
            seen.add(g)
            kind=_kind(self.chain(g))
            self.stage1_total[kind]+=1
            for bit in range(3):
                self.stage1_positive[kind][bit]+=(e1>>bit)&1
        if seen!=set(range(N_SUPPORT)) or set(self.stage1_total)!=set(range(16)):
            raise ValueError("unseen first-effect motif in training")

    def first_signature(self,kind):
        n=self.stage1_total[kind]
        return sum(1<<bit for bit in range(3)
                   if 2*self.stage1_positive[kind][bit]>n)

    def infer_first(self):
        if self.derived1:
            raise ValueError("symbolic first discovery already complete")
        sigs=tuple(self.first_signature(k) for k in range(16))
        self.first_signatures=tuple(sorted(set(sigs)))
        names={sig:32+i for i,sig in enumerate(self.first_signatures)}
        for g in range(N_GROUPS):
            source=4*g
            sig=self.first_signature(_kind(self.chain(g)))
            rid=names[sig]
            fact=(source,rid,source+2)
            self.derived1.add(fact)
            self.group_first_rel[g]=rid
        if len(self.derived1)!=N_GROUPS:
            raise AssertionError("missing symbolic invented first relation facts")

    def learn_second(self,feedback):
        if not self.derived1:
            raise ValueError("second symbolic stage requires invented first facts")
        seen=set()
        for g,e1,e2 in feedback:
            if g in seen or not 0<=g<N_SUPPORT or not 0<=e2<4:
                raise ValueError("invalid second feedback")
            seen.add(g)
            rel=self.group_first_rel[g]
            _,_,third=self.chain(g)
            key=(rel-32,third-10)
            self.stage2_total[key]+=1
            for bit in range(2):
                self.stage2_positive[key][bit]+=(e2>>bit)&1
        if seen!=set(range(N_SUPPORT)):
            raise ValueError("symbolic support missing second intervention")
        expected={(k,c) for k in range(len(self.first_signatures)) for c in range(4)}
        if set(self.stage2_total)!=expected:
            raise ValueError("symbolic second-stage class/type support incomplete")

    def second_signature(self,category:int,last:int):
        key=(category,last)
        n=self.stage2_total[key]
        return sum(1<<bit for bit in range(2)
                   if 2*self.stage2_positive[key][bit]>n)

    def infer_second(self):
        if not self.derived1 or self.derived2:
            raise ValueError("symbolic second discovery not ready")
        signatures={
            self.second_signature(k,c)
            for k in range(len(self.first_signatures)) for c in range(4)
        }
        self.second_signatures=tuple(sorted(signatures))
        names={sig:40+i for i,sig in enumerate(self.second_signatures)}
        for g in range(N_GROUPS):
            s=4*g
            rel=self.group_first_rel[g]
            _,_,c=self.chain(g)
            sig=self.second_signature(rel-32,c-10)
            rid=names[sig]
            self.derived2.add((s,rid,s+3))
            self.group_second_rel[g]=rid
        if len(self.derived2)!=N_GROUPS:
            raise AssertionError("missing symbolic invented second relation facts")

    def predictions(self,group):
        if group not in self.group_second_rel:
            raise ValueError("symbolic generated relation missing")
        return (self.first_signatures[self.group_first_rel[group]-32],
                self.second_signatures[self.group_second_rel[group]-40])


class ConventionalInventor:
    """Five fully trained logistic effect predictors, not rule-count lookups."""

    def __init__(self,symbolic_source:IndependentSymbolicInventor):
        self.source=symbolic_source
        self.head1=[RegularizedLogistic(16) for _ in range(3)]
        self.head2=[]
        self.first_signatures=()
        self.second_signatures=()
        self.derived1=set()
        self.derived2=set()
        self.group_first_rel={}
        self.group_second_rel={}

    def learn_first(self,feedback):
        rows=[_kind(self.source.chain(g)) for g,_,_ in feedback]
        for bit,head in enumerate(self.head1):
            head.fit(rows,[bool(e1&(1<<bit)) for _,e1,_ in feedback])

    def first_signature(self,kind:int):
        return sum(1<<bit for bit,head in enumerate(self.head1)
                   if head.predict(kind))

    def infer_first(self):
        if self.derived1:
            raise ValueError("conventional first knowledge created twice")
        sigs=tuple(self.first_signature(kind) for kind in range(16))
        self.first_signatures=tuple(sorted(set(sigs)))
        categories={sig:32+i for i,sig in enumerate(self.first_signatures)}
        for g in range(N_GROUPS):
            s=4*g
            sig=self.first_signature(_kind(self.source.chain(g)))
            rel=categories[sig]
            self.group_first_rel[g]=rel
            self.derived1.add((s,rel,s+2))
        if len(self.derived1)!=N_GROUPS:
            raise AssertionError("conventional first inferred category missing")

    def learn_second(self,feedback):
        if not self.derived1:
            raise ValueError("conventional second response requires own inferred first types")
        n=len(self.first_signatures)
        rows=[]
        for g,_,_ in feedback:
            _,_,c=self.source.chain(g)
            rows.append((self.group_first_rel[g]-32)*4+c-10)
        self.head2=[RegularizedLogistic(n*4) for _ in range(2)]
        for bit,head in enumerate(self.head2):
            head.fit(rows,[bool(e2&(1<<bit)) for _,_,e2 in feedback])

    def second_signature(self,category:int,last:int):
        kind=category*4+last
        return sum(1<<bit for bit,head in enumerate(self.head2)
                   if head.predict(kind))

    def infer_second(self):
        if not self.head2 or self.derived2:
            raise ValueError("second conventional learned operator unavailable")
        values={
            self.second_signature(k,c)
            for k in range(len(self.first_signatures)) for c in range(4)
        }
        self.second_signatures=tuple(sorted(values))
        names={s:40+i for i,s in enumerate(self.second_signatures)}
        for g in range(N_GROUPS):
            source=4*g
            _,_,c=self.source.chain(g)
            sig=self.second_signature(self.group_first_rel[g]-32,c-10)
            rel=names[sig]
            self.group_second_rel[g]=rel
            self.derived2.add((source,rel,source+3))
        if len(self.derived2)!=N_GROUPS:
            raise AssertionError("conventional second generated facts missing")

    def predictions(self,g):
        if g not in self.group_second_rel:
            raise ValueError("conventional stage2 category missing")
        return (self.first_signatures[self.group_first_rel[g]-32],
                self.second_signatures[self.group_second_rel[g]-40])
