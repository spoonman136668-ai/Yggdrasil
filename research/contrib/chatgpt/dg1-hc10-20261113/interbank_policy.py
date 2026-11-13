"""HC10: source-blind discriminating probes for immutable HC09 dual banks.

Uses public model version-space masks only, no hidden graph/phase/source
oracle, and no evaluator data. Actual physical flips are charged by runner.
"""
from __future__ import annotations
from fractions import Fraction
from pathlib import Path
import importlib.util

SOURCE=Path(__file__).resolve().parents[1]/"dg1-hc09-20261113"/"model.py"
spec=importlib.util.spec_from_file_location("frozen_hc09_context_cells",SOURCE)
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def probability(mask,state):
    zeros,ones=base.counts(mask,state)
    return Fraction(ones,zeros+ones) if zeros+ones else None


def interbank_delta(model,state,action):
    base.valid_state(state)
    base.valid_action(action)
    if len(model.banks)<2: return Fraction(0)
    p=probability(model.banks[0][action],state)
    q=probability(model.banks[1][action],state)
    if p is None or q is None: return Fraction(0)
    return abs(p-q)


def choose(model,state,used_flips,cap):
    """Choose 1 actually charged (causal/flip, index) without mutating model."""
    base.valid_state(state)
    if any(type(x) is not int for x in (used_flips,cap)) or not 0<=used_flips<=cap<=8:
        raise ValueError("HC10_BAD_PHYSICAL_BUDGET")
    if len(model.banks)==2:
        vals=[interbank_delta(model,state,a) for a in range(4)]
        if max(vals)>0:
            return "causal", max(range(4),key=lambda a:(vals[a],-a))
        if used_flips<cap:
            future=[max(interbank_delta(model,state^(1<<bit),a)
                        for a in range(4)) for bit in range(4)]
            if max(future)>0:
                return "flip",max(range(4),key=lambda j:(future[j],-j))
    return model.choose(state,used_flips,cap)
