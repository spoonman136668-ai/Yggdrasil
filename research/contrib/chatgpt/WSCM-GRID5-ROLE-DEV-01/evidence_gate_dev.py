"""Research-only corroboration filter for provisional Grid5 translations.

This is not a causal identification test or an action selector. It never adds
training observations or invokes the environment; all evidence is drawn from
the existing immutable source-free native Grid5 ledger. The preregistered
public_learned_delta_forecast and public_plan methods remain unchanged.
"""

from yggdrasil.native_grid5_evidence import NativeGrid5Evidence


def corroborated_delta_forecast(evidence, state, action, *, episode_id):
    """Require two differently located same-episode witnessed interventions.

    One witnessed transition supplies a candidate displacement; a *later*,
    independently identified receipt from a different predecessor must agree.
    This is corroboration within the same fixture family, NOT evidence that an
    arbitrary unseen structural law is identified. Never authorize a planner.
    """
    if type(evidence) is not NativeGrid5Evidence:
        raise TypeError('GRID5_EVIDENCE_TYPE')
    # Native call validates the state, action and episode pin. Preserve its
    # status, including contradiction, without changing the frozen readout.
    base = evidence.public_learned_delta_forecast(state, action, episode_id=episode_id)
    rows = tuple(row for row in evidence._rows
                 if row[1] == episode_id and row[4] == action)
    informative = tuple(row for row in rows
                        if all(0 < coordinate < 8 for coordinate in row[5]))
    unique_states = len({row[3] for row in informative})
    result = {
        'source_mode': base['source_mode'],
        'status': 'ABSTAIN',
        'base_status': base['status'],
        'hypothesis_family': 'two_distinct_state_delta_corroboration_dev',
        'informative_witnesses': len(informative),
        'distinct_predecessor_states': unique_states,
        'predicted_next_state': None,
        'planner_authorized': False,
        'scientific_gain_verified': False,
    }
    if base['status'] == 'CONTRADICTION':
        result['status'] = 'CONTRADICTION'
        return result
    if base['status'] != 'HYPOTHESIS':
        return result
    # A query at an observed predecessor is witness lookup, not transfer.
    if any(row[3] == tuple(state) for row in rows):
        return result
    if unique_states < 2:
        return result
    # Source IDs differ due to the native ledger's replay/conflict contract;
    # the second distinct-predecessor observation must occur later in time.
    first = informative[0]
    corroborators = tuple(row for row in informative[1:]
                          if row[0] != first[0] and row[2] > first[2]
                          and row[3] != first[3])
    if not corroborators:
        return result
    delta = tuple(first[5][i] - first[3][i] for i in (0, 1))
    if not any(tuple(row[5][i] - row[3][i] for i in (0, 1)) == delta
               for row in corroborators):
        result['status'] = 'CONTRADICTION'
        return result
    result['status'] = 'HYPOTHESIS'
    result['predicted_next_state'] = base['predicted_next_state']
    return result
