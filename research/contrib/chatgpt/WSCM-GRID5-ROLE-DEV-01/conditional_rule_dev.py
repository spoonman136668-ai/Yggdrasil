"""WSCM source-free conditional-transition hypothesis readout (DEV ONLY).

Consumes publicly witnessed, already-admitted same-episode native Grid5 rows.
It does NOT authenticate origin, identify unknown causal laws universally, train
native banks, mutate checkpoints, or authorize actions. No world is stepped.
"""

FAMILY = 'observed_two_parity_branches_dev'


def _query(state, action, episode_id):
    if (type(state) is not list or len(state) != 2 or
            any(type(v) is not int or not 0 <= v <= 8 for v in state)):
        raise ValueError('WSCM_CONDITIONAL_STATE')
    if type(action) is not int or not 0 <= action < 5:
        raise ValueError('WSCM_CONDITIONAL_ACTION')
    if (type(episode_id) is not str or len(episode_id) != 64 or
            any(c not in '0123456789abcdef' for c in episode_id)):
        raise ValueError('WSCM_CONDITIONAL_EPISODE_PIN')
    return tuple(state)


def _result(status, rows, *, axis=None, prediction=None, reason=None):
    return {
        'source_mode': 'engineering_fixture_only',
        'hypothesis_family': FAMILY,
        'status': status,
        'split_axis': axis,
        'witnesses': len(rows),
        'predicted_next_state': prediction,
        'reason': reason,
        'planner_authorized': False,
        'scientific_gain_verified': False,
    }


def _infer_from_native_rows(native_rows, state, action, *, episode_id):
    """Pure bounded diagnostic for original NativeGrid5Evidence._rows format.

    The caller must supply the original receipt-validated ledger. A row tuple is
    NOT a source-authenticity proof by itself. Even a unique fitting rule is
    merely a provisional hypothesis over this fixed two-feature grammar.
    """
    before_query = _query(state, action, episode_id)
    if type(native_rows) is not tuple or len(native_rows) > 256:
        raise ValueError('WSCM_CONDITIONAL_LEDGER')
    selected = []
    for row in native_rows:
        if type(row) is not tuple or len(row) != 10:
            raise ValueError('WSCM_CONDITIONAL_LEDGER')
        if row[1] == episode_id and row[4] == action:
            selected.append((row[0], row[3], row[5]))
    if not selected:
        return _result('ABSTAIN', selected, reason='NO_WITNESSES')
    witnessed = {}
    for source_id, predecessor, successor in selected:
        if (type(source_id) is not str or len(source_id) != 64 or
                type(predecessor) is not tuple or len(predecessor) != 2 or
                type(successor) is not tuple or len(successor) != 2):
            raise ValueError('WSCM_CONDITIONAL_LEDGER')
        witnessed.setdefault(predecessor, set()).add(successor)
    if any(len(successors) > 1 for successors in witnessed.values()):
        return _result('CONTRADICTION', selected, reason='SAME_STATE_CONFLICT')
    # Never repackage exact witnesses as new inferential coverage.
    if before_query in witnessed:
        return _result('ABSTAIN', selected, reason='EXACT_WITNESS_EXISTS')
    informative = [(before, after, tuple(after[d] - before[d] for d in (0, 1)))
                   for _, before, after in selected
                   if all(0 < v < 8 for v in after)]
    if len({r[0] for r in informative}) < 4:
        return _result('ABSTAIN', selected, reason='INSUFFICIENT_BRANCH_SUPPORT')
    candidates = []
    for axis in (0, 1):
        grouped = {0: {}, 1: {}}
        for before, after, delta in informative:
            grouped[before[axis] % 2].setdefault(before, set()).add(delta)
        if any(len(grouped[p]) < 2 or
               len({delta for deltas in grouped[p].values() for delta in deltas}) != 1
               for p in (0, 1)):
            continue
        deltas = {p: next(iter(next(iter(grouped[p].values())))) for p in (0, 1)}
        if deltas[0] == deltas[1]:
            continue  # No evidence of a conditional effect.
        # Every other witness must agree when its predicted successor is interior.
        if any(all(0 < before[d] + deltas[before[axis] % 2][d] < 8 for d in (0, 1))
               and tuple(before[d] + deltas[before[axis] % 2][d] for d in (0, 1)) != after
               for _, before, after in selected):
            continue
        candidates.append((axis, deltas))
    if len(candidates) != 1:
        return _result('ABSTAIN', selected,
                       reason='AMBIGUOUS_GRAMMAR' if candidates else 'NO_FITTING_SPLIT')
    axis, deltas = candidates[0]
    delta = deltas[before_query[axis] % 2]
    successor = tuple(before_query[d] + delta[d] for d in (0, 1))
    if not all(0 < v < 8 for v in before_query + successor):
        return _result('ABSTAIN', selected, reason='UNSUPPORTED_BOUNDARY')
    return _result('HYPOTHESIS', selected, axis=axis, prediction=list(successor),
                   reason='CONDITIONAL_FIT_NOT_CAUSAL_CERTIFICATE')


def conditional_delta_forecast(evidence, state, action, *, episode_id):
    """Opt-in native-evidence wrapper; no default-plan wiring or state mutation."""
    from yggdrasil.native_grid5_evidence import NativeGrid5Evidence
    if type(evidence) is not NativeGrid5Evidence:
        raise TypeError('WSCM_CONDITIONAL_NATIVE_EVIDENCE_REQUIRED')
    return _infer_from_native_rows(evidence._rows, state, action, episode_id=episode_id)

