"""DEV-only planner over *witnessed* external-action fixture readouts.

This adapter consumes NativeEpisodeExperience's existing passive fixture
readout. It never calls observe(), maps IDs to x1/x2, estimates an unseen
outcome, or changes the normal native planner. It is an exact-lookup control,
not evidence of generalization or an authenticated intervention.
"""

MAX_ACTIONS = 32


def fixture_only_plan(native, view, external_action_ids, desired_outcome):
    """Return the least matching ID, or abstain if any candidate is unknown.

    All candidates must be fully witnessed at the native interface. A None
    result also covers a known candidate set without a matching outcome.
    """
    if (type(view) is not tuple or len(view) != 2 or
            any(type(bit) is not int or bit not in (0, 1) for bit in view)):
        raise ValueError("WSCM_PLAN_VIEW")
    if type(desired_outcome) is not int or desired_outcome not in (0, 1):
        raise ValueError("WSCM_PLAN_TARGET")
    if (type(external_action_ids) is not tuple or
            not 1 <= len(external_action_ids) <= MAX_ACTIONS or
            any(type(action) is not int or not 0 <= action < 2**31
                for action in external_action_ids) or
            len(set(external_action_ids)) != len(external_action_ids)):
        raise ValueError("WSCM_PLAN_ACTIONS")
    results = []
    for action in external_action_ids:
        outcome = native.observed_external_fixture_value(view, action)
        if outcome is None:
            return None
        if type(outcome) is not int or outcome not in (0, 1):
            raise ValueError("WSCM_PLAN_INVALID_READOUT")
        results.append((action, outcome))
    return min((action for action, observed in results
                if observed == desired_outcome), default=None)
