"""Exact source-law action-confounding diagnostic; no source execution or training.

Only the CKAD-20 *invariant, regime=0* idealized uniform-draw law is covered.
This is analytical population arithmetic, NOT a held-out measurement on the
finite SHA256-derived episodes and NOT the balanced-action selector trial.
The source-side `logged` policy is explicitly NOT a randomized intervention.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "CKAD-20" / "synthetic_world.py"
SOURCE_PIN = "20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
ONE = Fraction(1)
HALF = Fraction(1, 2)
PUBLIC_FLIP = Fraction(1, 4)
LOGGED_MATCH = Fraction(15, 16)
TRANSITION_NOISE = (Fraction(1, 8), Fraction(1, 4))


def require_original_source():
    """Prevent silently applying the calculation to a changed world law."""
    if sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_PIN:
        raise ValueError("Confounding diagnostic source-law pin mismatch")
    return SOURCE_PIN


def conditional_transition(s1, x1, *, logged, logger_match=LOGGED_MATCH,
                           noise_by_hidden=TRANSITION_NOISE):
    """Return P(s2=1|s1,x1) observational or P(s2=1|s1,do(x1)).

    Uniform hidden H, public s1 = H xor E, P(E=1)=1/4.
    If logged, X1 = H xor L with P(L=0)=logger_match.
    Invariant/regime=0: S2 = X1 xor T, P(T=1|H)=(1/8,1/4).
    E,L,T use independent uniform source bytes under the idealized law.
    """
    if (type(s1) is not int or s1 not in (0, 1)
            or type(x1) is not int or x1 not in (0, 1)
            or type(logged) is not bool
            or type(logger_match) is not Fraction
            or not 0 <= logger_match <= 1
            or type(noise_by_hidden) is not tuple
            or len(noise_by_hidden) != 2
            or any(type(p) is not Fraction or not 0 <= p <= 1
                   for p in noise_by_hidden)):
        raise ValueError("Invalid exact binary source-law query")
    weights = []
    for hidden in (0, 1):
        p_public = ONE - PUBLIC_FLIP if s1 == hidden else PUBLIC_FLIP
        p_logged = (logger_match if x1 == hidden
                    else ONE - logger_match) if logged else ONE
        weights.append(HALF * p_public * p_logged)
    normalizer = sum(weights)
    if not normalizer:
        raise ValueError("Conditioning event has zero propensity")
    p_transition_flip = sum(
        w * noise for w, noise in zip(weights, noise_by_hidden, strict=True)
    ) / normalizer
    return p_transition_flip if x1 == 0 else ONE - p_transition_flip


def report():
    """Exact four public cells plus intervention-weighted Brier penalty."""
    require_original_source()
    rows = []
    total_excess = Fraction(0)
    for s1 in (0, 1):
        for x1 in (0, 1):
            causal = conditional_transition(s1, x1, logged=False)
            observational = conditional_transition(s1, x1, logged=True)
            bias = observational - causal
            total_excess += bias * bias / 4
            rows.append({
                "s1": s1, "x1": x1,
                "p_s2_one_do": str(causal),
                "p_s2_one_logged": str(observational),
                "logged_minus_do": str(bias),
                "brier_excess_if_logged_prediction_used_under_do": str(bias * bias),
            })
    return {
        "scope": "CKAD20_invariant_regime0_idealized_independent_uniform_bytes",
        "source_sha256": SOURCE_PIN,
        "rows": rows,
        "balanced_do_queries_excess_brier": str(total_excess),
        "balanced_trial_uses_logged_policy": False,
        "source_episodes_generated": 0,
        "source_actions": 0,
        "scientific_pass": False,
        "deployment": "NONE",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=2, sort_keys=True))
