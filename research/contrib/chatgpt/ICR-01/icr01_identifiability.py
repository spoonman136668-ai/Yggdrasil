"""ICR-01 source-free identifiability preflight.

This is an EXACT MATHEMATICAL COUNTEREXAMPLE, not a scientific or native
learning trial. Two directed causal graphs have identical observational joint
distributions but distinguishable source-public intervention consequences.

Models:
  A: X ~ Bernoulli(1/2), Y = X xor N
  B: Y ~ Bernoulli(1/2), X = Y xor N
where N ~ Bernoulli(1/10), independent of the exogenous root.
Only public X,Y observations and explicitly charged do() consequences qualify.
"""
from fractions import Fraction as F

NOISE = F(1,10)
MODELS = ("X_CAUSES_Y", "Y_CAUSES_X")
RESEARCH_ONLY = True

def _bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("ICR01_PUBLIC_BINARY_BIT_REQUIRED")
    return value

def observational_joint(model, x, y, *, noise=NOISE):
    if model not in MODELS:
        raise ValueError("ICR01_UNLISTED_GRAPH")
    _bit(x); _bit(y)
    if not F(0) <= noise <= F(1):
        raise ValueError("ICR01_BAD_NOISE")
    return F(1,2) * ((1-noise) if x == y else noise)

def intervention_outcome_one(model, intervention_variable, value, *, noise=NOISE):
    """P(other_variable=1 | do(variable=value)); never observational condition."""
    if model not in MODELS or intervention_variable not in ("X","Y"):
        raise ValueError("ICR01_BAD_PUBLIC_INTERVENTION")
    _bit(value)
    if not F(0) <= noise <= F(1):
        raise ValueError("ICR01_BAD_NOISE")
    if (model == "X_CAUSES_Y" and intervention_variable == "X") or (
            model == "Y_CAUSES_X" and intervention_variable == "Y"):
        return noise if value == 0 else 1-noise
    return F(1,2)

def observational_likelihood(model, public_pairs, *, noise=NOISE):
    likelihood = F(1)
    for row in public_pairs:
        if type(row) not in (list,tuple) or len(row) != 2:
            raise ValueError("ICR01_PUBLIC_PAIR_REQUIRED")
        likelihood *= observational_joint(model,row[0],row[1],noise=noise)
    return likelihood

def identifiability_certificate(*, noise=NOISE):
    public_rows = [(x,y) for x in (0,1) for y in (0,1)]
    joint_a = tuple(observational_joint(MODELS[0],x,y,noise=noise) for x,y in public_rows)
    joint_b = tuple(observational_joint(MODELS[1],x,y,noise=noise) for x,y in public_rows)
    if joint_a != joint_b or sum(joint_a) != F(1):
        raise AssertionError("OBSERVATIONAL_EQUIVALENCE_FAIL")
    pa = intervention_outcome_one(MODELS[0],"X",0,noise=noise)
    pb = intervention_outcome_one(MODELS[1],"X",0,noise=noise)
    return {
        "schema": "yggdrasil.icr01.source-free-identifiability.v1",
        "source_first_use": False, "native_executed": False,
        "scientific_gain_verified": False,
        "joint_probability_xy_order_00_01_10_11": [str(x) for x in joint_a],
        "observational_equivalence_exact": True,
        "observational_bayes_factor_for_every_possible_tape": "1",
        "P_Y1_given_do_X0_model_A": str(pa),
        "P_Y1_given_do_X0_model_B": str(pb),
        "interventional_total_variation_gap": str(abs(pa-pb)),
        "source_observation_actions_consumed": 0,
        "identifiability_without_do": "NO",
        "identifiability_with_charged_do": "IN_PRINCIPLE_IF_SOURCE_SUPPORTS",
        "claim": "Necessity of distinct source-witnessed interventional evidence; NOT demonstration of learned native graph discovery"
    }
