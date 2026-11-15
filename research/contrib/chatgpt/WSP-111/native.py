"""Directly programmed sparse factual and *invented* relation-category weights.

Input memory has one million uint64 addresses with float32 presence weights.
No output relation labels/types are hardcoded except a reserved numerical
namespace: first generated class keys begin at 32, second at 40. The actual
classes, number of classes and their meanings are INVENTED from observed
intervention effects. The evaluator's hidden oracle is never imported.
"""
from __future__ import annotations
from hashlib import sha256
import json
import numpy as np

NODE_BITS=22
REL_BITS=6
SHIFT=NODE_BITS+REL_BITS
DEST_MASK=(1<<NODE_BITS)-1
REL_MASK=(1<<REL_BITS)-1
N_FACTS=1_000_000
N_GROUPS=25_000
N_SUPPORT=3_000

def key_one(source:int,relation:int,target:int)->np.uint64:
    if (min(source,relation,target)<0 or source>=1<<NODE_BITS
            or target>=1<<NODE_BITS or relation>=1<<REL_BITS):
        raise ValueError("relational parameter address out of bounds")
    return np.uint64((source<<SHIFT)|(relation<<NODE_BITS)|target)

def key_many(sources,relations,targets)->np.ndarray:
    s=np.asarray(sources,dtype=np.uint64)
    r=np.asarray(relations,dtype=np.uint64)
    t=np.asarray(targets,dtype=np.uint64)
    if not(len(s)==len(r)==len(t)):
        raise ValueError("fact tuple arrays require equal size")
    if np.any(s>=1<<NODE_BITS) or np.any(t>=1<<NODE_BITS) or np.any(r>=1<<REL_BITS):
        raise ValueError("fact key cannot be encoded")
    return (s<<np.uint64(SHIFT))|(r<<np.uint64(NODE_BITS))|t

def decode(k:int)->tuple[int,int,int]:
    return k>>SHIFT,(k>>NODE_BITS)&REL_MASK,k&DEST_MASK

def effect_signature(probs)->int:
    return sum(1<<bit for bit,prob in enumerate(probs) if float(prob)>0.5)

class NativeRelationInventor:
    def __init__(self):
        self.original_keys=None
        self.original_weights=None
        self.operator1=None
        self.operator2=None
        self.first_signatures=None
        self.second_signatures=None
        self.derived1=np.empty(0,dtype=np.uint64)
        self.derived2=np.empty(0,dtype=np.uint64)

    def program_original(self,sources,relations,targets):
        if self.original_keys is not None:
            raise ValueError("original knowledge can only be programmed once")
        keys=key_many(sources,relations,targets)
        if len(keys)!=N_FACTS:
            raise ValueError("original store requires all 1m unique facts")
        keys=np.sort(keys)
        if np.any(keys[1:]<=keys[:-1]):
            raise ValueError("duplicate source key")
        self.original_keys=keys
        self.original_weights=np.ones(N_FACTS,dtype=np.float32)

    def original_sha256(self):
        if self.original_keys is None:
            raise ValueError("source weights not initialized")
        h=sha256()
        h.update(self.original_keys.tobytes())
        h.update(self.original_weights.tobytes())
        return h.hexdigest()

    def _original_outgoing(self,source:int)->tuple[int,int]:
        lower=np.uint64(source)<<np.uint64(SHIFT)
        at=int(np.searchsorted(self.original_keys,lower))
        if at>=N_FACTS or self.original_weights[at]!=1:
            raise ValueError("missing original native source weight")
        s,r,t=decode(int(self.original_keys[at]))
        if s!=source:
            raise ValueError("source identity has no original edge")
        return r,t

    def chain(self,group:int)->tuple[int,int,int]:
        if type(group) is not int or not 0<=group<N_GROUPS:
            raise ValueError("unregistered chain")
        source=4*group
        a,mid=self._original_outgoing(source)
        b,last=self._original_outgoing(mid)
        c,target=self._original_outgoing(last)
        if (mid,last,target)!=(source+1,source+2,source+3) or not (
                0<=a<=3 and 4<=b<=7 and 10<=c<=13):
            raise ValueError("missing actual three-edge native witness")
        return a,b,c

    def program_first_operator(self,feedback):
        if self.operator1 is not None:
            raise ValueError("first operator already programmed")
        positive=np.zeros((16,3),dtype=np.int32)
        totals=np.zeros(16,dtype=np.int32)
        seen=set()
        for g,e1,e2 in feedback:
            if (type(g) is not int or not 0<=g<N_SUPPORT or g in seen
                    or type(e1) is not int or not 0<=e1<8
                    or type(e2) is not int or not 0<=e2<4):
                raise ValueError("invalid observed training effect")
            seen.add(g)
            a,b,_=self.chain(g)
            kind=4*a+b-4
            totals[kind]+=1
            for bit in range(3):
                positive[kind,bit]+=(e1>>bit)&1
        if seen!=set(range(N_SUPPORT)) or np.any(totals==0):
            raise ValueError("first sensory support incomplete")
        self.operator1=((positive+1)/(totals[:,None]+2)).astype(np.float32)

    def infer_first(self):
        if self.operator1 is None or self.derived1.size:
            raise ValueError("first operator absent or discovery already performed")
        kind_signatures=tuple(effect_signature(self.operator1[k]) for k in range(16))
        self.first_signatures=tuple(sorted(set(kind_signatures)))
        if not 2<=len(self.first_signatures)<=8:
            raise AssertionError("no discriminable invented first-stage categories")
        rel_ids={s:32+i for i,s in enumerate(self.first_signatures)}
        generated=[]
        for g in range(N_GROUPS):
            a,b,_=self.chain(g)
            sig=kind_signatures[4*a+b-4]
            generated.append(key_one(4*g,rel_ids[sig],4*g+2))
        self.derived1=np.asarray(sorted(generated),dtype=np.uint64)
        if len(self.derived1)!=N_GROUPS or np.any(self.derived1[1:]<=self.derived1[:-1]):
            raise AssertionError("first discovered fact keys not unique")

    def first_relation(self,group:int)->tuple[int,int]:
        """Read invented relation category from PERSISTED numeric weights."""
        if not 0<=group<N_GROUPS or self.first_signatures is None:
            raise ValueError("no invented relation available")
        source=4*group
        at=int(np.searchsorted(self.derived1,np.uint64(source)<<np.uint64(SHIFT)))
        if at>=len(self.derived1):
            raise ValueError("missing derived first-stage relation")
        s,r,t=decode(int(self.derived1[at]))
        if s!=source or t!=source+2 or not 32<=r<32+len(self.first_signatures):
            raise ValueError("invalid first-stage stored type")
        return r,self.first_signatures[r-32]

    def program_second_operator(self,feedback):
        if self.operator2 is not None or not len(self.derived1):
            raise ValueError("second operator not ready or already programmed")
        k=len(self.first_signatures)
        positives=np.zeros((k,4,2),dtype=np.int32)
        totals=np.zeros((k,4),dtype=np.int32)
        seen=set()
        for group,e1,e2 in feedback:
            if type(group) is not int or not 0<=group<N_SUPPORT or group in seen:
                raise ValueError("replayed or unauthorized second-stage effect")
            if type(e1) is not int or not 0<=e1<8 or type(e2) is not int or not 0<=e2<4:
                raise ValueError("second-stage sensor observations malformed")
            seen.add(group)
            rel,sig=self.first_relation(group)
            _,_,c=self.chain(group)
            category=rel-32
            totals[category,c-10]+=1
            for bit in range(2):
                positives[category,c-10,bit]+=(e2>>bit)&1
        if seen!=set(range(N_SUPPORT)) or np.any(totals==0):
            raise ValueError("unknown categorical third-relation response not identifiable")
        self.operator2=((positives+1)/(totals[:,:,None]+2)).astype(np.float32)

    def infer_second(self):
        if self.operator2 is None or self.derived2.size:
            raise ValueError("second operator absent or already induced")
        kinds=tuple(effect_signature(self.operator2[category,c])
            for category in range(len(self.first_signatures)) for c in range(4))
        self.second_signatures=tuple(sorted(set(kinds)))
        if not 2<=len(self.second_signatures)<=4:
            raise AssertionError("no meaningful second response categories")
        rel_ids={sig:40+i for i,sig in enumerate(self.second_signatures)}
        generated=[]
        for g in range(N_GROUPS):
            first_rel,_=self.first_relation(g)
            _,_,third=self.chain(g)
            predicted=effect_signature(self.operator2[first_rel-32,third-10])
            generated.append(key_one(4*g,rel_ids[predicted],4*g+3))
        self.derived2=np.asarray(sorted(generated),dtype=np.uint64)
        if len(self.derived2)!=N_GROUPS or np.any(self.derived2[1:]<=self.derived2[:-1]):
            raise AssertionError("second invented fact weights not unique")

    def predictions(self,group:int)->tuple[int,int]:
        first_rel,first_signature=self.first_relation(group)
        if self.second_signatures is None:
            raise ValueError("second-stage knowledge not written")
        source=4*group
        at=int(np.searchsorted(self.derived2,np.uint64(source)<<np.uint64(SHIFT)))
        if at>=len(self.derived2):
            raise ValueError("missing stored second class relation")
        s,r,t=decode(int(self.derived2[at]))
        if s!=source or t!=source+3 or not 40<=r<40+len(self.second_signatures):
            raise ValueError("corrupted second invented relation")
        return first_signature,self.second_signatures[r-40]

    def checkpoint(self):
        if self.second_signatures is None or not len(self.derived2):
            raise ValueError("cold save must follow both discovery rounds")
        parts={
            "original_keys":self.original_keys.tobytes(),
            "original_weights":self.original_weights.tobytes(),
            "operator1":self.operator1.tobytes(),
            "operator2":self.operator2.tobytes(),
            "derived1":self.derived1.tobytes(),
            "derived2":self.derived2.tobytes(),
        }
        maps={"first":list(self.first_signatures),"second":list(self.second_signatures)}
        return {"schema":"wsp111.native-invented-relation-weights.v1",
                "maps":maps,"parts":parts,
                "sha256":self._digest(parts,maps)}

    @staticmethod
    def _digest(parts,maps):
        h=sha256(json.dumps(maps,sort_keys=True,separators=(",",":")).encode("ascii"))
        for key in sorted(parts):
            h.update(key.encode("ascii"))
            h.update(len(parts[key]).to_bytes(8,"little"))
            h.update(parts[key])
        return h.hexdigest()

    @classmethod
    def cold_restore(cls,state):
        if state.get("schema")!="wsp111.native-invented-relation-weights.v1":
            raise ValueError("invalid saved native relation schema")
        parts,maps=state["parts"],state["maps"]
        if cls._digest(parts,maps)!=state.get("sha256"):
            raise ValueError("invented relation memory tampered")
        m=cls()
        m.original_keys=np.frombuffer(parts["original_keys"],dtype=np.uint64).copy()
        m.original_weights=np.frombuffer(parts["original_weights"],dtype=np.float32).copy()
        m.operator1=np.frombuffer(parts["operator1"],dtype=np.float32).copy().reshape((16,3))
        m.first_signatures=tuple(maps["first"])
        m.operator2=np.frombuffer(parts["operator2"],dtype=np.float32).copy().reshape((len(m.first_signatures),4,2))
        m.second_signatures=tuple(maps["second"])
        m.derived1=np.frombuffer(parts["derived1"],dtype=np.uint64).copy()
        m.derived2=np.frombuffer(parts["derived2"],dtype=np.uint64).copy()
        if (len(m.original_keys)!=N_FACTS or len(m.original_weights)!=N_FACTS
                or len(m.derived1)!=N_GROUPS or len(m.derived2)!=N_GROUPS
                or np.any(m.original_keys[1:]<=m.original_keys[:-1])
                or np.any(m.derived1[1:]<=m.derived1[:-1])
                or np.any(m.derived2[1:]<=m.derived2[:-1])
                or not np.all(m.original_weights==1)
                or not np.all((m.operator1>0)&(m.operator1<1))
                or not np.all((m.operator2>0)&(m.operator2<1))
                or not 2<=len(m.first_signatures)<=8 or not 2<=len(m.second_signatures)<=4
                or tuple(sorted(set(m.first_signatures)))!=m.first_signatures
                or tuple(sorted(set(m.second_signatures)))!=m.second_signatures):
            raise ValueError("malformed native relational weight snapshot")
        return m
