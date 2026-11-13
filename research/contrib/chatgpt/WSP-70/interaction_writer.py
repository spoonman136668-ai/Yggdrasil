"""Directly imprint action-conditioned reusable interaction ReLU neurons.

WSP70 is source-blind. All candidate hidden feature weights are numerical
action-gated 2/3-literal conjunctions over PUBLIC binary sensor bits. Their
candidate grammar is explicitly prewired. Selection correlates their
activations with residuals from ONLY charged physical observations; no
simulator/oracle physics, symbolic rule compiler, or test results are used.

The resulting hidden weights, biases, numerical readout and posterior
covariance run as a neural network without storing the selected identities
or physical training ledger in the inference snapshot.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import combinations,product
from pathlib import Path
from random import Random
import sys

_PARENT=Path(__file__).resolve().parents[1]/"WSP-69"
sys.path.insert(0,str(_PARENT))
from growing_neural import (
    FeatureGrowthNeural, inputs, MAX_NEW, NEW_PER_PHASE, RIDGE
)


def features_dictionary():
    candidates=[]
    for action in range(4):
        for width in (2,3):
            for subset in combinations(range(4),width):
                for bits in product((0,1),repeat=width):
                    candidates.append((action,tuple(zip(subset,bits))))
    result=tuple(candidates)
    if len(result)!=224 or len(set(result))!=224:
        raise AssertionError("precommitted action/interactions grammar changed")
    return result


DICTIONARY=features_dictionary()


def neural_conjunction_weights(key):
    """All-literals-and-public-action indicator encoded as one ReLU unit."""
    action,literals=key
    if type(action) is not int or action not in range(4):
        raise ValueError("bad action context")
    if type(literals) is not tuple or len(literals) not in (2,3):
        raise ValueError("bad interaction count")
    sensor_indices=[j for j,bit in literals]
    if (sensor_indices!=sorted(set(sensor_indices)) or
            any(type(j) is not int or j not in range(4) or
                type(bit) is not int or bit not in (0,1)
                for j,bit in literals)):
        raise ValueError("bad signed literal")
    weights=[0.0]*8
    negatives=0
    for bit,expected in literals:
        if expected:
            weights[bit]=1.0
        else:
            weights[bit]=-1.0
            negatives+=1
    weights[4+action]=1.0
    bias=float(negatives-len(literals))
    return weights,bias


def activation(key,state,action):
    w,b=neural_conjunction_weights(key)
    x=inputs(state,action)
    return max(0.0,sum(a*z for a,z in zip(w,x))+b)


class ReusableInteractionNeural(FeatureGrowthNeural):
    """WSP69 covariance/readout writer with WSP70 data-selected true hidden weights."""

    def __init__(self,policy="residual",seed=0):
        super().__init__(policy=policy,seed=seed)
        self.random=Random(int.from_bytes(
            sha256(f"WSP70|candidate-selection|{seed}".encode("ascii")).digest(),"big"))

    def _rank_candidates(self):
        existing=set(self.centers)
        evidence=[]
        for before,action,after in self.ledger:
            raw=self.raw(before,action)
            evidence.append((before,action,tuple(after[i]-raw[i] for i in range(4))))
        eligible=[]
        if self.policy=="random":
            # Random control never computes or reads outcome residuals.
            # It only checks whether a candidate was activated by a public
            # physically charged INPUT, with no knowledge of its label.
            for key in DICTIONARY:
                if key not in existing and any(
                    activation(key,before,action)>0.5
                    for before,action,after in self.ledger
                ):
                    eligible.append((0.0,key))
            return eligible
        for key in DICTIONARY:
            if key in existing:
                continue
            active=[residual for before,action,residual in evidence
                    if activation(key,before,action)>0.5]
            if not active:
                continue
            n=len(active)
            correlation=[sum(e[i] for e in active) for i in range(4)]
            score=sum(z*z for z in correlation)/(RIDGE+n)
            eligible.append((score,key))
        if not eligible:
            raise ValueError("no activated training-only feature candidate")
        return eligible

    def grow(self):
        if self.charged_actions not in (48,96) or self.growth_rounds>=2:
            raise ValueError("frozen neural feature-growth milestone violated")
        scored=self._rank_candidates()
        eligible=tuple(key for value,key in scored)
        k=min(NEW_PER_PHASE, len(eligible))
        if self.policy=="residual":
            selected=tuple(key for value,key in
                           sorted(scored,key=lambda z:(-z[0],z[1]))[:k])
        else:
            # Same candidate grammar and same number of trained hidden units,
            # but random selection does NOT access next-state residual scores.
            selected=tuple(sorted(self.random.sample(list(eligible),k)))
        for key in selected:
            weights,bias=neural_conjunction_weights(key)
            self.hidden_weights.append(weights)
            self.hidden_biases.append(bias)
            self.centers.append(key)
        self.growth_rounds+=1
        # Build executable neural coefficients from 100% charged PUBLIC data.
        self._init_readout()
        for before,action,after in self.ledger:
            self._learn_row(before,action,after)
        return len(selected)

    def selected_feature_ids(self):
        """Training receipt only; NOT part of stored model inference."""
        return tuple(self.centers)

    def changed_hidden(self,other):
        return len(self.hidden_weights)>len(other.hidden_weights) or (
            self.hidden_weights!=other.hidden_weights)
