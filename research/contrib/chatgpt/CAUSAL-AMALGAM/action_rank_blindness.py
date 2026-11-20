"""Source-free hidden-family action information: oracle versus public policy.

The source-family conditional outcome laws and prior are evaluator-only
declarations.  This tool cannot establish public predecision equivalence or
authentic source ownership: the caller supplies an *assumption* that public
initial observations are identical across families.  It does not train models,
sample worlds, run first use, select actions or accept any source authority.
"""
from fractions import Fraction
import re

from action_identifiability_audit import _fraction, _js_binary, require

FAMILY_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")


def audit_hidden_family_first_probe(families, *, identical_public_prefix):
    """Compare regime information under hidden versus oracle-known family.

    R in {old,new} is uniform and independent of hidden F; family weights sum
    to one.  For blind action a, P(Y|R,a) is *marginalized over F first*, then
    JS is computed.  Oracle information is E_F(max_a JS(P(Y|R,a,F))).
    These are different information sets, not competing trained policies.

    Only the FIRST choice with the declared identical public prefix is covered;
    later legitimate observations may allow adaptation.  A successful report is
    an illustrative evaluator bound, not a source-qualification certificate.
    """
    require(identical_public_prefix is True, "PUBLIC_PREFIX_NOT_PROVEN_BY_THIS_TOOL")
    require(type(families) is list and 2 <= len(families) <= 16,
            "HIDDEN_FAMILY_LIST")
    seen = set()
    sum_w = Fraction(0)
    old_marginal = [Fraction(0), Fraction(0)]
    new_marginal = [Fraction(0), Fraction(0)]
    conditional_oracle = 0.0
    family_information = []
    winners = set()

    for entry in families:
        require(type(entry) is dict and set(entry) == {
            "family_id", "prior", "old", "new"}, "FAMILY_SCHEMA")
        identifier = entry["family_id"]
        require(type(identifier) is str and FAMILY_ID.fullmatch(identifier)
                is not None and identifier not in seen, "FAMILY_ID")
        seen.add(identifier)
        weight = _fraction(entry["prior"])
        require(0 < weight <= 1, "FAMILY_PRIOR")
        sum_w += weight
        old = entry["old"]
        new = entry["new"]
        require(type(old) is list and type(new) is list and
                len(old) == len(new) == 2, "BINARY_PROBE_LAW")
        p = [_fraction(v) for v in old]
        q = [_fraction(v) for v in new]
        for a in (0, 1):
            old_marginal[a] += weight * p[a]
            new_marginal[a] += weight * q[a]
        info = [_js_binary(p[a], q[a]) for a in (0, 1)]
        winner = None if abs(info[0] - info[1]) < 1e-12 else (
            0 if info[0] > info[1] else 1)
        if winner is not None:
            winners.add(winner)
        conditional_oracle += float(weight) * max(info)
        family_information.append({
            "family_id": identifier,
            "evaluator_only_action_information_nats": info,
            "evaluator_only_best_action": winner,
        })

    require(sum_w == 1, "FAMILY_PRIORS_NOT_NORMALIZED")
    blind_info = [_js_binary(old_marginal[a], new_marginal[a])
                  for a in (0, 1)]
    blind_tie = abs(blind_info[0] - blind_info[1]) < 1e-12
    best_blind = max(blind_info)
    return {
        "schema": "yggdrasil.amalgam.hidden-family-first-probe.v1",
        "family_count": len(families),
        "conditional_oracle_information_nats": conditional_oracle,
        "blind_action_information_nats": blind_info,
        "blind_best_first_action": (
            None if blind_tie else 0 if blind_info[0] > blind_info[1] else 1),
        "blind_first_action_information_gap_nats": (
            abs(blind_info[0] - blind_info[1])),
        "blind_optimal_information_nats": best_blind,
        "oracle_information_advantage_nats": conditional_oracle - best_blind,
        "oracle_action_rank_reverses": winners == {0, 1},
        "oracle_family_information": family_information,
        "public_prefix_equivalence_independently_verified": False,
        "source_identity_authenticated": False,
        "learner_causal_action_selection_improved": False,
        "source_actions": 0,
        "training_updates": 0,
        "first_use_allowed": False,
        "scientific_pass": False,
        "decision_authority": "NONE_EVALUATOR_DESIGN_ONLY",
        "scope": "SINGLE_BLIND_FIRST_PROBE_REGIME_INFORMATION_NOT_FUTURE_CONTROL",
    }
