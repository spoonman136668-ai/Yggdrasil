"""Illustrative, source-free law-isomorphism and public action-ID contracts.

This is a static preflight NEGATIVE CONTROL, not a scored training cohort.
No learner must import the harness-internal role map or function definitions.
"""
from itertools import product

BITS = tuple(product((0, 1), repeat=2))
ROLES = tuple(range(4))
# Illustrative function families only. NEVER use as protected held evidence.
FUNCTIONS = {
    "A": (lambda p, q: p, lambda p, q: q,
          lambda p, q: p ^ q, lambda p, q: p & q),
    "B": (lambda p, q: p, lambda p, q: q,
          lambda p, q: p | q, lambda p, q: 1 - (p & q)),
    "C": (lambda p, q: p, lambda p, q: q,
          lambda p, q: 1 - (p ^ q), lambda p, q: (1 - p) | q),
}
# IDs are deliberately different across phases. The role assignments are
# harness-only truth for static source-free contract validation.
ID_TO_ROLE = {
    "A_train": {1301: 0, 22007: 1, 4179: 2, 30011: 3},
    "B_shift": {2117: 3, 49531: 0, 16389: 2, 3509: 1},
    "A_return": {48011: 2, 6007: 3, 27179: 0, 12347: 1},
    "C_composition": {1029: 1, 31037: 0, 5459: 3, 22917: 2},
}
PHASE_LAW = {
    "A_train": "A", "B_shift": "B", "A_return": "A",
    "C_composition": "C",
}


def signature(law, role):
    """Complete public-input truth vector, used for static audit only."""
    if law not in FUNCTIONS or role not in ROLES:
        raise ValueError("UNKNOWN_LAW_OR_ROLE")
    return tuple(FUNCTIONS[law][role](*state) for state in BITS)


def canonical_law(law):
    """ID/permutation invariant multiset; unequal means no role renaming works."""
    return tuple(sorted(signature(law, r) for r in ROLES))


def public_request(phase, state, external_id):
    """Model-visible request contains no hidden role, mapping, or law name."""
    if phase not in ID_TO_ROLE or type(external_id) is not int or external_id not in ID_TO_ROLE[phase]:
        raise ValueError("UNKNOWN_PUBLIC_ACTION")
    if type(state) is not tuple or len(state) != 2 or any(type(x) is not int or x not in (0, 1) for x in state):
        raise ValueError("INVALID_PUBLIC_STATE")
    return {"public_view": list(state), "external_action_id": external_id}


def validate_learner_request(request):
    """Fail closed on harness metadata in a learner-facing public request.

    This checks the object boundary only; it does NOT provide process isolation
    from a learner that imports harness-private symbols in this module.
    """
    if (type(request) is not dict or set(request) != {"public_view", "external_action_id"}
            or type(request["external_action_id"]) is not int
            or type(request["public_view"]) is not list or len(request["public_view"]) != 2
            or any(type(bit) is not int or bit not in (0, 1) for bit in request["public_view"])):
        raise ValueError("LEARNER_REQUEST_LEAK_OR_INVALID")
    return {"public_view": request["public_view"][:],
            "external_action_id": request["external_action_id"]}


def engineering_only_outcome(phase, state, external_id):
    """Harness-only truth, not a permissible learner lookup or protected result."""
    request = public_request(phase, state, external_id)
    del request
    role = ID_TO_ROLE[phase][external_id]
    return FUNCTIONS[PHASE_LAW[phase]][role](*state)


def audit_static_contract():
    """Fail closed if any phase or family is merely an action-ID relabel."""
    ids = [id_ for mapping in ID_TO_ROLE.values() for id_ in mapping]
    if len(set(ids)) != 16:
        raise ValueError("ACTION_ID_REUSE")
    for mapping in ID_TO_ROLE.values():
        if sorted(mapping.values()) != list(ROLES):
            raise ValueError("ROLE_NOT_BIJECTIVE")
    for law in FUNCTIONS:
        for role in ROLES:
            if any(type(value) is not int or value not in (0, 1)
                   for value in signature(law, role)):
                raise ValueError("NONBINARY_CAUSAL_FUNCTION")
    if len({canonical_law(k) for k in FUNCTIONS}) != len(FUNCTIONS):
        raise ValueError("LAWS_ISOMORPHIC_UNDER_ROLE_PERMUTATION")
    expected = {"A_train": "A", "B_shift": "B", "A_return": "A", "C_composition": "C"}
    if PHASE_LAW != expected or set(ID_TO_ROLE) != set(expected):
        raise ValueError("PHASE_LAW_CONTRACT")
    if canonical_law("A") != canonical_law(PHASE_LAW["A_return"]):
        raise ValueError("A_RETURN_IS_NOT_A")
    return True
