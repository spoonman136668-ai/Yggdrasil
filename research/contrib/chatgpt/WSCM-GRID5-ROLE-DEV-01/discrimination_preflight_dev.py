"""Offline WSCM discriminator proposal: explicit hypotheses, no source actions.

This is an *oracle-information upper-bound* for DEV contract validation:
all supplied candidate laws are known to the caller. It does not learn laws,
prove public reachability, authenticate receipt IDs, or authorize interventions.
No native model, ledger, checkpoint, or planner is imported or changed.
"""
from fractions import Fraction

SCHEMA = 'yggdrasil.wscm.discrimination-preflight.dev.v1'


def _nat(value, minimum=0):
    return type(value) is int and value >= minimum


def _coordinate(value):
    return (type(value) is list and len(value) == 2
            and all(_nat(x) and x < 9 for x in value))


def propose_probe(candidates, hypotheses, *, remaining_charge_units):
    """Rank a known disagreement per total charge; never request an env step.

    Each hypothesis must explicitly provide its prediction for every candidate.
    Missing predictions cannot be treated as disagreements. All costs are
    caller-supplied and therefore NOT a verified reachability or owner lease.
    The candidate set itself can be constructed only from public FIT evidence
    in any future scientific test; this DEV helper cannot enforce that custody.
    """
    if (type(candidates) is not list or not 0 < len(candidates) <= 16
            or type(hypotheses) is not list or not 2 <= len(hypotheses) <= 8
            or not _nat(remaining_charge_units) or remaining_charge_units > 10):
        raise ValueError('DISCRIMINATION_BOUNDS')
    ids = set()
    for item in candidates:
        if (type(item) is not dict or set(item) != {
                'id', 'state', 'action', 'travel_charge', 'intervention_charge'}
                or type(item['id']) is not str or not item['id']
                or len(item['id']) > 64 or item['id'] in ids
                or not _coordinate(item['state'])
                or not _nat(item['action']) or item['action'] >= 5
                or not _nat(item['travel_charge']) or item['travel_charge'] > 10
                or not _nat(item['intervention_charge'], minimum=1)
                or item['intervention_charge'] > 10):
            raise ValueError('DISCRIMINATION_CANDIDATE')
        ids.add(item['id'])
    names = set()
    for h in hypotheses:
        if (type(h) is not dict or set(h) != {'id', 'predictions'}
                or type(h['id']) is not str or not h['id']
                or len(h['id']) > 64 or h['id'] in names
                or type(h['predictions']) is not dict
                or set(h['predictions']) != ids
                or any(not _coordinate(p) for p in h['predictions'].values())):
            raise ValueError('DISCRIMINATION_HYPOTHESIS')
        names.add(h['id'])
    result = {
        'schema': SCHEMA,
        'status': 'ABSTAIN',
        'candidate_id': None,
        'charged_units_if_executed': None,
        'disagreeing_pairs': 0,
        'total_hypothesis_pairs': len(hypotheses) * (len(hypotheses) - 1) // 2,
        'source_mode': 'engineering_fixture_only',
        'oracle_hypotheses_supplied': True,
        'action_authorized': False,
        'scientific_gain_verified': False,
    }
    informative = []
    for candidate in candidates:
        outcomes = [tuple(h['predictions'][candidate['id']]) for h in hypotheses]
        disagree = sum(outcomes[i] != outcomes[j]
                       for i in range(len(outcomes)) for j in range(i + 1, len(outcomes)))
        if not disagree:
            continue
        cost = candidate['travel_charge'] + candidate['intervention_charge']
        informative.append((candidate['id'], cost, disagree))
    if not informative:
        return result
    affordable = [row for row in informative if row[1] <= remaining_charge_units]
    if not affordable:
        result['status'] = 'BUDGET_EXHAUSTED'
        return result
    # Exact rational priority: disagreement per whole-probe charge, then
    # absolute disagreement, then less charge, finally canonical ID.
    best = sorted(affordable,
                  key=lambda row: (-Fraction(row[2], row[1]), -row[2], row[1], row[0]))[0]
    result.update(status='PROPOSAL_ONLY', candidate_id=best[0],
                  charged_units_if_executed=best[1], disagreeing_pairs=best[2])
    return result
