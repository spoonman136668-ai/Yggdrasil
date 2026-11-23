"""Fail-closed source-free bound for arbitrary four-state intermediate wiring.

Preserves the historical four-grammar development proposer unchanged. This
wrapper never turns a hash-pinned fixture trace into authenticated causal
custody or an executable action. No original-world seeds are consumed.
"""
from composition_wire_dev import _native_signature, propose_two_step_composition


def propose_unrestricted_safe_composition(native, first_action, second_action,
                                          public_traces, query_view):
    """Return a conditional invariant, or abstain when unseen wiring can vary.

    The unrestricted model class permits any of four intermediate states for
    each of four public start states. On an unwitnessed start, every possible
    intermediate remains compatible with prior state-specific observations.
    If second action has both bit outcomes, the result is unidentifiable. Even
    a constant outcome only proves a *conditional fixture-level invariant*.
    """
    provisional = propose_two_step_composition(
        native, first_action, second_action, public_traces, query_view)
    result = dict(provisional)
    result.update({
        "assumption_class": "unrestricted_four_state_mapping",
        "robust_to_unrestricted_wiring": False,
        "authenticated_structural_transition": False,
        "compatible_unrestricted_mapping_count": None,
        "possible_next_bits": [],
    })
    # Grammar mismatch is not evidence of inconsistent real transitions:
    # an unrestricted, state-indexed intermediate mapping can still explain
    # every distinct valid input trace.
    may_continue = provisional["status"] == "HYPOTHESIS" or (
        provisional["status"] == "CONTRADICTION" and
        provisional["reason"] == "NO_SUPPORTED_WIRING")
    if not may_continue:
        return result
    distinct_states = len({tuple(row["public_view"]) for row in public_traces})
    result["compatible_unrestricted_mapping_count"] = 4 ** (4 - distinct_states)
    second_signature = _native_signature(native, second_action)
    # Existing original proposer already enforces a full witnessed signature;
    # retain the defensive fail-closed guard if a malicious callback changes.
    if second_signature is None:
        result["status"] = "ABSTAIN"
        result["reason"] = "PRIMITIVE_NOT_STABLE_ON_READ"
        result["predicted_next_bit"] = None
        result["compatible_unrestricted_mapping_count"] = None
        return result
    possible = sorted(set(second_signature))
    result["possible_next_bits"] = possible
    if len(possible) > 1:
        result["status"] = "ABSTAIN"
        result["reason"] = "UNRESTRICTED_MAPPING_AMBIGUOUS"
        result["predicted_next_bit"] = None
    elif provisional["status"] == "HYPOTHESIS":
        result["status"] = "INVARIANT"
        result["reason"] = "CONDITIONAL_CONSTANT_SECOND_STAGE_NOT_TRANSFER"
        result["predicted_next_bit"] = possible[0]
        result["robust_to_unrestricted_wiring"] = True
    else:
        # A trace outside the supplied grammar is not internally contradictory
        # under arbitrary mapping, but native structural custody is absent.
        result["status"] = "ABSTAIN"
        result["reason"] = "OUTSIDE_FIXED_GRAMMAR_NOT_ADMITTED"
        result["predicted_next_bit"] = None
    return result
