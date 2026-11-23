"""Source-free public-witness-derived alternative-law probe proposals (DEV).

A finite x-parity rule grammar supplies the *hypothesis class*, not the truth:
one observed branch may be fitted and the unobserved branch retains all five
cardinal/stay alternatives. Neither a source world nor a planner is called.
This is an uncertainty representation, not unfamiliar causal-law learning.
"""
import importlib.util
from pathlib import Path

from yggdrasil.native_grid5_evidence import NativeGrid5Evidence
from yggdrasil.native_grid5_ingress import pinned, public_state

_GRAMMAR = ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0))
_SPEC = importlib.util.spec_from_file_location(
    'wscm_discrimination_preflight_dev',
    Path(__file__).with_name('discrimination_preflight_dev.py'))
_RANKER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_RANKER)


def _out(status, reason, count, *, rank=None):
    result = {
        'status': status,
        'reason': reason,
        'source_mode': 'engineering_fixture_only',
        'hypothesis_family': 'public_x_parity_five_displacements_dev',
        'candidate_laws_derived_from_public_witnesses': True,
        'true_law_oracle_supplied': False,
        'ranker_received_explicit_derived_tables': rank is not None,
        'compatible_hypotheses': count,
        'candidate_id': None,
        'charged_units_if_executed': None,
        'disagreeing_pairs': 0,
        'action_authorized': False,
        'scientific_gain_verified': False,
    }
    if rank is not None:
        result.update(status=rank['status'],
                      candidate_id=rank['candidate_id'],
                      charged_units_if_executed=rank['charged_units_if_executed'],
                      disagreeing_pairs=rank['disagreeing_pairs'])
    return result


def propose_public_version_space_probe(evidence, candidates, action, *,
                                      episode_id, remaining_charge_units):
    """Use only original same-episode receipt rows; no action execution.

    Candidates are *offline hypothetical queries*. Travel charges and alleged
    reachability are caller supplied; neither is source authenticated.
    """
    if type(evidence) is not NativeGrid5Evidence:
        raise TypeError('WSCM_PUBLIC_NATIVE_EVIDENCE_REQUIRED')
    if type(action) is not int or not 0 <= action < 5:
        raise ValueError('WSCM_PUBLIC_ACTION')
    if not pinned(episode_id):
        raise ValueError('WSCM_PUBLIC_EPISODE')
    if (type(remaining_charge_units) is not int
            or not 0 <= remaining_charge_units <= 10):
        raise ValueError('WSCM_PUBLIC_BUDGET')
    if type(candidates) is not list or not 0 < len(candidates) <= 16:
        raise ValueError('WSCM_PUBLIC_CANDIDATES')
    seen_ids = set()
    for c in candidates:
        if (type(c) is not dict or set(c) != {
                'id', 'state', 'action', 'travel_charge', 'intervention_charge'}
                or type(c['id']) is not str or not c['id'] or len(c['id']) > 64
                or c['id'] in seen_ids or type(c['action']) is not int
                or c['action'] != action
                or type(c['travel_charge']) is not int
                or not 0 <= c['travel_charge'] <= 10
                or type(c['intervention_charge']) is not int
                or not 1 <= c['intervention_charge'] <= 10):
            raise ValueError('WSCM_PUBLIC_CANDIDATE')
        seen_ids.add(c['id'])
        public_state(c['state'])
    rows = tuple(row for row in evidence._rows
                 if row[1] == episode_id and row[4] == action)
    if not rows:
        return _out('ABSTAIN', 'NO_WITNESSES', 0)
    witnessed = {}
    support = {0: set(), 1: set()}
    for row in rows:
        before, after = row[3], row[5]
        witnessed.setdefault(before, set()).add(after)
        if all(0 < coordinate < 8 for coordinate in after):
            delta = tuple(after[d] - before[d] for d in (0, 1))
            if delta not in _GRAMMAR:
                return _out('CONTRADICTION', 'OUTSIDE_GRAMMAR', 0)
            support[before[0] % 2].add(delta)
    if any(len(v) > 1 for v in witnessed.values()):
        return _out('CONTRADICTION', 'IDENTICAL_STATE_CONFLICT', 0)
    if any(len(x) > 1 for x in support.values()):
        return _out('CONTRADICTION', 'PARITY_EFFECT_CONFLICT', 0)
    if not any(support.values()):
        return _out('ABSTAIN', 'NO_INTERIOR_SUPPORT', 0)
    options = [tuple(support[p]) if support[p] else _GRAMMAR for p in (0, 1)]
    viable = []
    for even in options[0]:
        for odd in options[1]:
            chosen = (even, odd)
            # Reject candidate laws contradicted by a public witness whenever
            # its predicted outcome is wholly interior. Never assume clipping.
            if any(
                all(0 < before[d] + chosen[before[0] % 2][d] < 8
                    for d in (0, 1))
                and tuple(before[d] + chosen[before[0] % 2][d]
                          for d in (0, 1)) != after
                for _, _, _, before, _, after, *_ in rows
            ):
                continue
            viable.append(chosen)
    if not viable:
        return _out('CONTRADICTION', 'NO_COMPATIBLE_LAW', 0)
    # This grammar contains <=5 laws once at least one parity has support.
    if len(viable) > 5:
        raise ValueError('WSCM_PUBLIC_VERSION_CAPACITY')
    if len(viable) < 2:
        return _out('ABSTAIN', 'NO_DISAGREEMENT', len(viable))
    valid = []
    for c in candidates:
        before = tuple(c['state'])
        if (before in witnessed or not all(0 < d < 8 for d in before)):
            continue
        effects = [tuple(before[d] + law[before[0] % 2][d]
                         for d in (0, 1)) for law in viable]
        if not all(all(0 < d < 8 for d in effect) for effect in effects):
            continue
        valid.append((c, effects))
    if not valid:
        return _out('ABSTAIN', 'NO_SUPPORTED_QUERY', len(viable))
    # Pass ALL alternative laws and ALL valid query outcomes to the existing
    # offline ranker. A partial or hand-selected subset would be oracle bias.
    hyps = [
        {'id': 'public-version-%d' % i,
         'predictions': {c['id']: list(effects[i]) for c, effects in valid}}
        for i in range(len(viable))
    ]
    rank = _RANKER.propose_probe(
        [c for c, _ in valid], hyps,
        remaining_charge_units=remaining_charge_units)
    return _out(rank['status'], 'OFFLINE_DISAGREEMENT_ONLY',
                len(viable), rank=rank)
