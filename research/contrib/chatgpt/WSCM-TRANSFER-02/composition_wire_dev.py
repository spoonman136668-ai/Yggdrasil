"""WSCM-TRANSFER-02: bounded SOURCE-FREE two-action wiring diagnostic.

Inputs are fully witnessed native fixture signatures and caller-provided public
intermediate-view traces. Caller traces are not source-authenticated chain
receipts, even if their individual primitive effects are in native memory.
This pure readout never learns into native state or authorizes an action.
"""

WIRES = ("output_then_x", "output_then_y", "x_then_output", "y_then_output")
STATES = ((0, 0), (0, 1), (1, 0), (1, 1))


def _require(ok, reason):
    if not ok:
        raise ValueError(reason)


def _view(raw):
    _require(type(raw) is list and len(raw) == 2 and
             all(type(bit) is int and bit in (0, 1) for bit in raw),
             "WSCM_COMPOSE_PUBLIC_VIEW")
    return tuple(raw)


def _action(raw):
    _require(type(raw) is int and 0 <= raw < 2**31, "WSCM_COMPOSE_ACTION")
    return raw


def _pin(raw):
    return type(raw) is str and len(raw) == 64 and all(c in "0123456789abcdef" for c in raw)


def _wire(name, state, output):
    x, y = state
    return {
        "output_then_x": (output, x),
        "output_then_y": (output, y),
        "x_then_output": (x, output),
        "y_then_output": (y, output),
    }[name]


def _predict(signature, state):
    return signature[2 * state[0] + state[1]]


def _native_signature(native, action):
    # The actual native public method refuses missing or conflicting identity
    # evidence. Do not parse private rows or accept a supplied truth table.
    values = tuple(native.observed_external_fixture_value(state, action) for state in STATES)
    _require(all(value is None or (type(value) is int and value in (0, 1))
                 for value in values), "WSCM_COMPOSE_NATIVE_RESULT")
    return values if all(value is not None for value in values) else None


def _result(status, *, reason, matches=(), prediction=None, witnesses=0):
    return {
        "source_mode": "engineering_fixture_only",
        "status": status,
        "reason": reason,
        "compatible_wirings": list(matches),
        "structural_witnesses": witnesses,
        "predicted_next_bit": prediction,
        "provisional_hypothesis_only": True,
        "structural_chain_authenticated": False,
        "action_authorized": False,
        "native_state_updated": False,
        "scientific_gain_verified": False,
    }


def propose_two_step_composition(native, first_action, second_action,
                                 public_traces, query_view, *,
                                 allow_functional_consensus=False):
    """Infer a *provisional* two-stage wiring from public fixture traces.

    Each trace has source_id, public_view, first_outcome, second_public_view,
    second_outcome. The fixed four-wiring grammar is supplied in code: THIS
    DOES NOT DISCOVER AN ARBITRARY NEW CAUSAL GRAPH. Individual native action
    signatures were previously fully witnessed. Any equivalent conventional
    symbolic engine given this same grammar/data can make the same prediction.
    """
    _require(type(allow_functional_consensus) is bool,
             "WSCM_COMPOSE_CONSENSUS_FLAG")
    first = _action(first_action)
    second = _action(second_action)
    _require(first != second, "WSCM_COMPOSE_IDENTICAL_ACTIONS")
    query = _view(query_view)
    _require(type(public_traces) is tuple and len(public_traces) <= 16,
             "WSCM_COMPOSE_TRACE_CAPACITY")
    _require(callable(getattr(native, "observed_external_fixture_value", None)),
             "WSCM_COMPOSE_NATIVE_INTERFACE")
    first_sig = _native_signature(native, first)
    second_sig = _native_signature(native, second)
    if first_sig is None or second_sig is None:
        return _result("ABSTAIN", reason="PRIMITIVE_NOT_FULLY_WITNESSED")
    if not public_traces:
        return _result("ABSTAIN", reason="NO_STRUCTURAL_TRACES")
    rows = []
    seen_sources = set()
    seen_states = {}
    for row in public_traces:
        _require(type(row) is dict and set(row) == {
            "source_id", "public_view", "first_outcome",
            "second_public_view", "second_outcome"}, "WSCM_COMPOSE_TRACE_FIELDS")
        source_id = row["source_id"]
        _require(_pin(source_id) and source_id not in seen_sources,
                 "WSCM_COMPOSE_TRACE_ID")
        seen_sources.add(source_id)
        start = _view(row["public_view"])
        middle = _view(row["second_public_view"])
        first_value = row["first_outcome"]
        second_value = row["second_outcome"]
        _require(type(first_value) is int and first_value in (0, 1) and
                 type(second_value) is int and second_value in (0, 1),
                 "WSCM_COMPOSE_TRACE_OUTCOME")
        _require(_predict(first_sig, start) == first_value and
                 _predict(second_sig, middle) == second_value,
                 "WSCM_COMPOSE_PRIMITIVE_MISMATCH")
        if start in seen_states and seen_states[start] != (first_value, middle, second_value):
            return _result("CONTRADICTION", reason="CONFLICTING_STRUCTURAL_TRACES",
                           witnesses=len(rows) + 1)
        seen_states[start] = (first_value, middle, second_value)
        rows.append((start, first_value, middle))
    if query in seen_states:
        return _result("ABSTAIN", reason="EXACT_STRUCTURAL_TRACE_WITNESSED",
                       witnesses=len(rows))
    if len(seen_states) < 2:
        return _result("ABSTAIN", reason="INSUFFICIENT_DISTINCT_STRUCTURAL_SUPPORT",
                       witnesses=len(rows))
    fits = tuple(name for name in WIRES if all(
        _wire(name, state, first_value) == middle
        for state, first_value, middle in rows))
    if not fits:
        return _result("CONTRADICTION", reason="NO_SUPPORTED_WIRING",
                       witnesses=len(rows))
    if len(fits) != 1:
        if not allow_functional_consensus:
            return _result("ABSTAIN", reason="AMBIGUOUS_WIRING",
                           matches=fits, witnesses=len(rows))
        # Matching wiring identity is NOT necessary for a common outcome.
        # This forecast is valid only conditional on the supplied four-wire
        # grammar and fully witnessed public primitive truth tables.
        first_value = _predict(first_sig, query)
        outputs = {_predict(second_sig, _wire(wire, query, first_value))
                   for wire in fits}
        if len(outputs) != 1:
            return _result("ABSTAIN", reason="AMBIGUOUS_FUNCTIONAL_OUTCOME",
                           matches=fits, witnesses=len(rows))
        return _result("HYPOTHESIS", reason="SOURCE_FREE_FUNCTIONAL_CONSENSUS",
                       matches=fits, prediction=next(iter(outputs)),
                       witnesses=len(rows))
    intermediate = _wire(fits[0], query, _predict(first_sig, query))
    return _result("HYPOTHESIS", reason="SOURCE_FREE_FIXED_GRAMMAR_COMPOSITION",
                   matches=fits, prediction=_predict(second_sig, intermediate),
                   witnesses=len(rows))
