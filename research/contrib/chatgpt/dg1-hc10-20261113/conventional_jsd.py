"""Separately implemented conventional Jensen-Shannon context discrimination.

Uses frozen HC09 ConventionalContextModel only. Never imports HC10 candidate
interbank policy, and never receives true source regimes or causal labels.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
from math import log2

PATH=Path(__file__).resolve().parents[1]/"dg1-hc09-20261113"/"conventional_control.py"
spec=importlib.util.spec_from_file_location("frozen_hc09_conventional_context",PATH)
control=importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


def bernoulli_entropy(p):
    if p<=0 or p>=1: return 0.0
    return -p*log2(p)-(1-p)*log2(1-p)


def jsd(model,state,action):
    control.assert_public(state,action)
    if len(model.contexts)<2:return 0.0
    x0,x1=control.posterior_counts(model.contexts[0][action],state)
    y0,y1=control.posterior_counts(model.contexts[1][action],state)
    if not (x0+x1) or not (y0+y1):return 0.0
    p=x1/(x0+x1);q=y1/(y0+y1)
    # Equal prior context probability: JS(P,Q)=H((P+Q)/2)-(H(P)+H(Q))/2.
    v=bernoulli_entropy((p+q)/2)-(bernoulli_entropy(p)+bernoulli_entropy(q))/2
    return max(0.0,v)


def choose(model,state,used_flips,cap):
    control.assert_public(state)
    if any(type(v) is not int for v in (used_flips,cap)) or not 0<=used_flips<=cap<=8:
        raise ValueError("HC10_CONVENTIONAL_BUDGET")
    if len(model.contexts)==2:
        scores=[jsd(model,state,a) for a in range(4)]
        if max(scores)>1e-14:
            return "causal",max(range(4),key=lambda a:(scores[a],-a))
        if used_flips<cap:
            after=[max(jsd(model,state^(1<<j),a) for a in range(4))
                   for j in range(4)]
            if max(after)>1e-14:
                return "flip",max(range(4),key=lambda bit:(after[bit],-bit))
    return model.choose(state,used_flips,cap)
