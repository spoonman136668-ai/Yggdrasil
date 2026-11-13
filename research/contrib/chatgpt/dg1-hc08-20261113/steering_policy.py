"""HC08 candidate: physical controllability-aware causal action selection.

Source-blind. Uses the original HC07 affine rule masks unchanged. A bit flip is
a real *charged* exogenous do-intervention, NOT causal-physics learning.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

HC07=Path(__file__).resolve().parents[1]/"dg1-hc07-20261113"/"affine_cells.py"
_spec=importlib.util.spec_from_file_location("hc07_frozen_affine",HC07)
base=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def choose_intervention(model, public_state, flip_count, flip_limit):
    """Return (kind, index), with no model mutation or hidden-world inputs."""
    base.state_checked(public_state)
    if type(flip_count) is not int or type(flip_limit) is not int or not 0<=flip_count<=flip_limit<=8:
        raise ValueError("HC08_BAD_INTERVENTION_BUDGET")
    current=[base.gini(model.surviving[a],public_state) for a in range(4)]
    maximum=max(current)
    if maximum:
        return ("causal",max(range(4),key=lambda a:(current[a],-a)))
    if flip_count<flip_limit:
        scores=[]
        for bit in range(4):
            next_state=public_state^(1<<bit)
            scores.append(sum(base.gini(model.surviving[a],next_state)
                              for a in range(4)))
        # Even if all scores are zero, physically moving to a different
        # state is permitted but charged. No assumption of success.
        return ("flip",max(range(4),key=lambda bit:(scores[bit],-bit)))
    return ("causal",0)
