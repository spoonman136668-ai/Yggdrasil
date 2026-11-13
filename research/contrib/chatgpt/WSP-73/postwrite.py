"""WSP73 action-specific post-write confidence calibration, frozen before test.

This module receives only a cold numerical neural model and 32 physically
charged C observations. It never modifies model weights or consults the
source/oracle. A short, source-blind audit marks a public action trusted only
when >=3 charged examples elicited confident predictions AND all were true.

Matched-coverage selection is evaluator-only on PUBLIC input identities:
the global neural-score and seeded-random controls each select the same m
already-baseline-confident inputs as the candidate in that world's 64-input
domain, without seeing physical outcome labels. This cannot be deployed as
a precomputed unknown-world per-source threshold; it is only a fair risk/
coverage diagnostic on frozen heldout inputs.
"""
from __future__ import annotations
from hashlib import sha256
from random import Random
from itertools import product
from math import isfinite

STATES=tuple(product((0,1),repeat=4))
ACTIONS=tuple(range(4))
CALIBRATION_CHARGES=32
BASE_MARGIN=0.27
BASE_LEVERAGE=2.0
LEVERAGE_PENALTY=0.02
MIN_ACCEPTED_PER_ACTION=3


def public_check(state,action):
    if type(state) is not tuple or state not in STATES or (
            type(action) is not int or action not in ACTIONS):
        raise ValueError("invalid public input/action")
    return state


def score_from_numeric_weights(weight_model,state,action):
    public_check(state,action)
    raw,leverage=weight_model.model._raw_and_leverage(state,action)
    if not all(isfinite(v) for v in raw) or not isfinite(leverage):
        raise ValueError("nonfinite learned numerical predictor")
    return min(abs(v-0.5) for v in raw)-LEVERAGE_PENALTY*leverage


class PhysicalPostWriteAuditor:
    """All calibration data come from real independently charged actions."""

    def __init__(self,weight_model):
        self.model=weight_model
        self.accepted=[0]*4
        self.errors=[0]*4
        self.trusted=[False]*4
        self.calibrated=False
        self.paid_calibration_actions=0

    def calibrate(self,rows):
        if self.calibrated or type(rows) not in (list,tuple) or len(rows)!=32:
            raise ValueError("must reserve exactly 32 physical C observations")
        for state,action,observed in rows:
            public_check(state,action)
            public_check(observed,action)
            predicted=self.model.predict(state,action)
            if predicted is not None:
                self.accepted[action]+=1
                self.errors[action]+=int(predicted!=observed)
        self.trusted=[self.accepted[a]>=MIN_ACCEPTED_PER_ACTION and
                      self.errors[a]==0 for a in ACTIONS]
        self.paid_calibration_actions=len(rows)
        self.calibrated=True

    def predict(self,state,action):
        public_check(state,action)
        if not self.calibrated:
            raise ValueError("physical C audit is not complete")
        base=self.model.predict(state,action)
        return base if self.trusted[action] else None

    def precommitted_receipt(self):
        if not self.calibrated:
            raise ValueError("cannot use unaudited confidence")
        return {
            "calibration_charges":self.paid_calibration_actions,
            "original_confident_per_action":list(self.accepted),
            "original_wrong_confident_per_action":list(self.errors),
            "trusted_public_actions":list(self.trusted),
            "trusted_action_count":sum(self.trusted)
        }


def matched_coverage_views(auditor,seed):
    """Offline unlabeled public-domain risk-coverage comparison.

    All selected inputs MUST be originally accepted by the same frozen
    neural numeric model and every selection has EXACT same cardinality.
    No source labels enter rankings, cutoff, tie breaks or control pools.
    """
    if not auditor.calibrated or type(seed) is not int:
        raise ValueError("unqualified postwrite audit")
    public_inputs=[(s,a) for s in STATES for a in ACTIONS]
    gated=[(s,a) for s,a in public_inputs
           if auditor.predict(s,a) is not None]
    baseline=[(s,a) for s,a in public_inputs
              if auditor.model.predict(s,a) is not None]
    m=len(gated)
    if not set(gated).issubset(set(baseline)):
        raise AssertionError("postwrite gate fabricated new predictions")
    rank=sorted(baseline,key=lambda x:(
        -score_from_numeric_weights(auditor.model,*x),x[0],x[1]))
    neural=rank[:m]
    rng=Random(int.from_bytes(sha256(
        f"WSP73|equal-coverage-random|{seed}".encode("ascii")).digest(),
        "big"))
    rand=tuple(sorted(rng.sample(baseline,m))) if m else tuple()
    assert len(gated)==len(neural)==len(rand)==m
    assert all(x in baseline for x in neural+list(rand))
    return {
        "gate":tuple(gated),
        "global_score":tuple(neural),
        "random":tuple(rand),
        "base_confident":len(baseline),
        "matched_count":m
    }


def selected_predictor(weight_model,selected):
    selected_set=set(selected)
    if len(selected_set)!=len(selected):
        raise ValueError("selection duplicates")
    for s,a in selected_set:
        public_check(s,a)
        if weight_model.predict(s,a) is None:
            raise ValueError("selected an unconfident base numeric prediction")
    def predict(state,action):
        public_check(state,action)
        return weight_model.predict(state,action) if (
            state,action) in selected_set else None
    return predict
