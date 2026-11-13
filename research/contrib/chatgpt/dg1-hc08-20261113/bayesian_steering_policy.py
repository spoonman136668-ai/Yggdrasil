"""HC08 independent Bayesian Shannon-entropy steering policy.

No import of candidate steering policy or its entropy helpers. Uses the
separately implemented original HC07 Bayesian causal graph learner.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"dg1-hc07-20261113"/"bayesian_graph_control.py"
_spec=importlib.util.spec_from_file_location("hc07_original_bayesian_graph",BASE)
bayes=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bayes)


def decide_bayesian(model, state, used_flips, allowed_flips):
    bayes.valid_state(state)
    if (type(used_flips) is not int or type(allowed_flips) is not int or
        not 0<=used_flips<=allowed_flips<=8):
        raise ValueError("HC08_BAYES_BAD_ACTUATOR_BUDGET")
    available=[bayes.shannon(model.posterior_masks[a],state) for a in range(4)]
    if max(available)>0:
        return ("causal",max(range(4),key=lambda a:(available[a],-a)))
    if used_flips<allowed_flips:
        potentials=[]
        for bit in range(4):
            target=state^(1<<bit)
            future=sum(bayes.shannon(model.posterior_masks[a],target)
                       for a in range(4))
            potentials.append(future)
        return ("flip",max(range(4),key=lambda bit:(potentials[bit],-bit)))
    return ("causal",0)
