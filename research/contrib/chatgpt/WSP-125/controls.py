"""Exact independent symbolic version-space and frozen negative controls.

Enumerates ALL permitted 8-bit 3..6 supports on both axes and all nonzero
three-bit deltas. Bitset operations reduce the huge hypothesis space without
borrowing the direct numerical learner's representation or update rules.
No source oracle imports.
"""
from __future__ import annotations
from functools import lru_cache
import random

MASKS=tuple(mask for mask in range(256) if 3<=mask.bit_count()<=6)
N=len(MASKS)
COUNT=N*N*7
UNIVERSE=(1<<COUNT)-1


@lru_cache(maxsize=1)
def _delta_masks():
    result=[]
    length=(COUNT+7)//8
    for delta_idx in range(7):
        buf=bytearray(length)
        for pair_id in range(N*N):
            bit=pair_id*7+delta_idx
            buf[bit//8] |= 1<<(bit%8)
        result.append(int.from_bytes(buf,"little"))
    return tuple(result)


@lru_cache(maxsize=64)
def _hit_mask(left,right):
    if (type(left) is not int or type(right) is not int or
            not 0<=left<8 or not 0<=right<8):
        raise ValueError("WSP125_SYMBOLIC_BAD_PAIR")
    buf=bytearray((COUNT+7)//8)
    l_indices=[i for i,m in enumerate(MASKS) if (m>>left)&1]
    r_indices=[i for i,m in enumerate(MASKS) if (m>>right)&1]
    for li in l_indices:
        for ri in r_indices:
            bit=(li*N+ri)*7
            index=bit//8
            pair=127 << (bit%8)
            buf[index] |= pair&255
            if index+1<len(buf):
                buf[index+1] |= (pair>>8)&255
    return int.from_bytes(buf,"little")


class ExactSymbolicSupports:
    def __init__(self):
        self.post={}
        self.seen=set()
        self.rows={}

    def observe(self,view,event):
        if (getattr(view,"cohort",None)!="fit" or
                view.seed!=125900+view.law_id or
                event.seed!=view.seed or
                event.law_id!=view.law_id or
                type(event.subject) is not int or event.subject not in view.legal or
                (event.left,event.right)!=view.pair(event.subject) or
                type(event.effect) is not int or not 0<=event.effect<8 or
                type(event.receipt_sha256) is not str or
                len(event.receipt_sha256)!=64):
            raise ValueError("WSP125_SYMBOLIC_UNTRUSTED_SOURCE")
        key=(view.seed,event.subject)
        if key in self.seen:
            raise ValueError("WSP125_SYMBOLIC_DUPLICATE")
        a,b=event.left,event.right
        residual=event.effect^(a^b)
        candidate=self.post.get(view.law_id,UNIVERSE)
        hit=_hit_mask(a,b)
        if residual==0:
            candidate &= UNIVERSE^hit
        else:
            candidate &= hit&_delta_masks()[residual-1]
        if not candidate:
            raise ValueError("WSP125_SYMBOLIC_NO_CAUSAL_EXPLANATION")
        self.post[view.law_id]=candidate
        self.seen.add(key)
        self.rows.setdefault(view.law_id,[]).append(
            [view.seed,event.subject,a,b,event.effect,event.receipt_sha256])

    def infer_pair(self,law_id,left,right):
        if (type(law_id) is not int or not 0<=law_id<128 or
                type(left) is not int or not 0<=left<8 or
                type(right) is not int or not 0<=right<8):
            raise ValueError("WSP125_SYMBOLIC_BAD_PUBLIC_QUERY")
        state=self.post.get(law_id,UNIVERSE)
        positive=state&_hit_mask(left,right)
        if not positive:
            return left^right
        if positive!=state:
            return None
        for d,mask in enumerate(_delta_masks(),1):
            if positive&mask==positive:
                return (left^right)^d
        return None

    def infer(self,view,subject):
        return self.infer_pair(view.law_id,*view.pair(subject))

    def remaining(self,law_id):
        return self.post.get(law_id,UNIVERSE).bit_count()


class FixedBaseline:
    def observe(self,view,event):
        return None

    def infer(self,view,subject):
        a,b=view.pair(subject)
        return a^b


class NoUpdate:
    def observe(self,view,event):
        return None

    def infer(self,view,subject):
        return None


def passive_sequence(view):
    if getattr(view,"cohort",None)!="fit":
        raise PermissionError("WSP125_PASSIVE_ONLY_FIT")
    rng=random.Random(125777+view.law_id*31)
    actions=list(view.legal)
    rng.shuffle(actions)
    return tuple(actions[:32])
