"""Independent finite known-grammar symbolic Bayesian benchmark for H03.

Takes only public action/reward records. No import/access to H03 world generator,
hidden program, evaluator truth, WSP101 original cohorts, model weights or Qwen.
"""
from __future__ import annotations
from collections import defaultdict

SOURCE_ACTIONS=(63,107,116,14,95,19,37,119,26,121,76,110,35,111,56,62,90,125,50,71,6,83)
HELDOUT_ACTIONS=(1,2,5,8,10,11,13,20,30,31,42,46,48,51,52,61,73,78,79,106,108,114,118,126)
MASKS=tuple(m for m in range(1,128) if 2<=m.bit_count()<=4)
GRAMMAR=tuple((f,m) for f in range(6) for m in MASKS)
assert len(GRAMMAR)==546


def predicted(f,mask,action):
    if (type(f) is not int or not 0<=f<6 or
        type(mask) is not int or mask not in MASKS or
        type(action) is not int or not 1<=action<=127):
        raise ValueError("H03_BAD_CANDIDATE")
    matched=(mask&action).bit_count()
    if f==0:
        return matched&1
    if f==1:
        return int(matched>=2)
    if f==2:
        return int(matched==1)
    if f==3:
        return int(matched>=3)
    if f==4:
        return (matched&1)^int((action&3)==3)
    return int(matched==mask.bit_count())


def checked_source(observations):
    if type(observations) not in (tuple,list) or len(observations)!=len(SOURCE_ACTIONS):
        raise ValueError("H03_SOURCE_LENGTH")
    output=[]
    for i,row in enumerate(observations):
        if type(row) is not tuple or len(row)!=2:
            raise ValueError("H03_SOURCE_ROW")
        action,reported=row
        if type(action) is not int or action!=SOURCE_ACTIONS[i] or (
            type(reported) is not int or reported not in (0,1)
        ):
            raise ValueError("H03_INVALID_PUBLIC_RECORD")
        output.append(row)
    return tuple(output)


class ExactBayes:
    """Exact uniform 546-program posterior with known Bernoulli flip p=1/8."""
    def __init__(self,observations):
        self.observations=checked_source(observations)
        n=len(self.observations)
        self._weights=[]
        for f,m in GRAMMAR:
            incorrect=sum(predicted(f,m,a)!=bit for a,bit in self.observations)
            self._weights.append(7**(n-incorrect))
        self._normalizer=sum(self._weights)
        if self._normalizer<=0:
            raise ValueError("H03_BAD_POSTERIOR")
    def predict(self,action):
        if type(action) is not int or not 1<=action<=127:
            raise ValueError("H03_BAD_HELDOUT_ACTION")
        positive=sum(w for (f,m),w in zip(GRAMMAR,self._weights)
                     if predicted(f,m,action))
        return int(2*positive>self._normalizer)


def prior_predict(action):
    # Exact untrained, matched grammar with no interventions.
    positive=sum(predicted(f,m,action) for f,m in GRAMMAR)
    return int(2*positive>len(GRAMMAR))


def global_alias_audit():
    """No H03 worlds inspected; exhaustive deterministic grammar signatures only."""
    classes=defaultdict(set)
    for f,m in GRAMMAR:
        a=tuple(predicted(f,m,p) for p in SOURCE_ACTIONS)
        held=tuple(predicted(f,m,p) for p in HELDOUT_ACTIONS)
        classes[a].add(held)
    return {"hypotheses":len(GRAMMAR),
            "distinct_source_signatures":len(classes),
            "divergent_heldout_alias_classes":sum(len(held)>1 for held in classes.values())}


def actual_world_query_identifiable(clean_source, clean_heldout):
    """Audit consumes ONLY evaluator-side noiseless rows; not used by ExactBayes."""
    signatures=defaultdict(set)
    for f,m in GRAMMAR:
        sig=tuple(predicted(f,m,p) for p in SOURCE_ACTIONS)
        signatures[sig].add(tuple(predicted(f,m,p) for p in HELDOUT_ACTIONS))
    a=signatures.get(tuple(clean_source),set())
    return bool(a) and a=={tuple(clean_heldout)}
