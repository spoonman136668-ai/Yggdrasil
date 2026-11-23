"""WSCM sparse public-operator hypothesis screen (source-free DEV only).

Pure readout from *caller-supplied* public witness rows; never an action actor,
source-authentication mechanism, integrated native learner or Genome writer.
The fixed <=2-parent Boolean grammar is a hypothesis class, not discovered physics.
No prediction is certified outside this grammar; novel three-way laws may fool it.
"""
from itertools import combinations, product

SOURCE_MODE = 'engineering_fixture_only'
INPUT_BITS = 4
MAX_ACTIONS = 32
MAX_ROWS = 256
MAX_CANDIDATES = 114
STATES = tuple(product((0, 1), repeat=INPUT_BITS))


def _bits(value):
    if type(value) not in (list, tuple) or len(value) != INPUT_BITS or any(
            type(bit) is not int or bit not in (0, 1) for bit in value):
        raise ValueError('WSCM_PUBLIC_VIEW')
    return tuple(value)


def _action(value):
    if type(value) is not int or not 0 <= value < 2**31:
        raise ValueError('WSCM_PUBLIC_ACTION')
    return value


def _id(value):
    if type(value) is not str or len(value) != 64 or any(
            c not in '0123456789abcdef' for c in value):
        raise ValueError('WSCM_SOURCE_ID')
    return value


def _validate(rows):
    if type(rows) not in (list, tuple) or len(rows) > MAX_ROWS:
        raise ValueError('WSCM_EVENT_CAP')
    seen = set()
    actions = set()
    output = []
    for row in rows:
        if type(row) is not dict or set(row) != {
                'source_mode', 'source_id', 'external_action_id',
                'public_view', 'outcome'} or row['source_mode'] != SOURCE_MODE:
            raise ValueError('WSCM_FIXTURE_ONLY')
        uid = _id(row['source_id'])
        if uid in seen:
            raise ValueError('WSCM_REPLAY_ID')
        seen.add(uid)
        action = _action(row['external_action_id'])
        actions.add(action)
        if len(actions) > MAX_ACTIONS:
            raise ValueError('WSCM_ACTION_CAP')
        view = _bits(row['public_view'])
        if type(row['outcome']) is not int or row['outcome'] not in (0, 1):
            raise ValueError('WSCM_OUTCOME')
        output.append((action, view, row['outcome']))
    return tuple(output)


def _models():
    """Enumerate all Boolean functions with <=2 public parents and no oracle."""
    models = []
    for count in (0, 1, 2):
        for parents in combinations(range(INPUT_BITS), count):
            for values in product((0, 1), repeat=2**count):
                models.append((parents, values))
    assert len(models) == MAX_CANDIDATES
    return tuple(models)


MODELS = _models()


def _evaluate(model, view):
    parents, table = model
    index = 0
    for p in parents:
        index = (index << 1) | view[p]
    return table[index]


def analyze(rows, external_action_id, query_view):
    """Conservative prediction over ALL compatible sparse operators.

    A unanimous output is HYPOTHESIS_WITHIN_GRAMMAR, not causal truth.
    Missing evidence or disagreement remains ABSTAIN, including any new ID.
    """
    action = _action(external_action_id)
    query = _bits(query_view)
    events = _validate(rows)
    witnesses = [(view, outcome) for a, view, outcome in events if a == action]
    if not witnesses:
        return dict(status='ABSTAIN', reason='NO_WITNESS', hypothesis_count=0,
                    predicted_outcome=None, action_authorized=False,
                    scientific_gain_verified=False)
    by_view = {}
    for view, outcome in witnesses:
        by_view.setdefault(view, set()).add(outcome)
    if any(len(outcomes) != 1 for outcomes in by_view.values()):
        return dict(status='CONTRADICTION', reason='CONFLICTING_PUBLIC_WITNESS',
                    hypothesis_count=0, predicted_outcome=None,
                    action_authorized=False, scientific_gain_verified=False)
    survivors = [m for m in MODELS if all(_evaluate(m, view) == outcome
                                         for view, outcome in witnesses)]
    if not survivors:
        return dict(status='OUT_OF_GRAMMAR', reason='NO_SPARSE_LAW',
                    hypothesis_count=0, predicted_outcome=None,
                    action_authorized=False, scientific_gain_verified=False)
    forecast = {_evaluate(m, query) for m in survivors}
    unanimous = len(forecast) == 1
    return dict(status='HYPOTHESIS_WITHIN_GRAMMAR' if unanimous else 'ABSTAIN',
                reason='UNANIMOUS_SPARSE_HYPOTHESES' if unanimous else 'UNRESOLVED_LAWS',
                hypothesis_count=len(survivors),
                parent_sets=len({m[0] for m in survivors}),
                predicted_outcome=next(iter(forecast)) if unanimous else None,
                witnessed_query=query in by_view,
                action_authorized=False, scientific_gain_verified=False)


def propose_public_probe(rows, external_action_id):
    """Rank an unobserved PUBLIC query by disagreement, proposal only.

    The source has no authenticated reachability/cost/intervention contract.
    No external action is called. No claimed real charge or information gain.
    """
    action = _action(external_action_id)
    events = _validate(rows)
    witnesses = [(view, outcome) for a, view, outcome in events if a == action]
    if not witnesses:
        return {'status': 'ABSTAIN', 'reason': 'NO_WITNESS', 'action_authorized': False}
    by_view = {}
    for view, outcome in witnesses:
        by_view.setdefault(view, set()).add(outcome)
    if any(len(v) != 1 for v in by_view.values()):
        return {'status': 'ABSTAIN', 'reason': 'CONTRADICTION', 'action_authorized': False}
    survivors = [m for m in MODELS if all(_evaluate(m, view) == outcome
                                         for view, outcome in witnesses)]
    if not survivors:
        return {'status': 'ABSTAIN', 'reason': 'OUT_OF_GRAMMAR', 'action_authorized': False}
    scored = []
    for state in STATES:
        if state in by_view:
            continue
        ones = sum(_evaluate(m, state) for m in survivors)
        zeros = len(survivors) - ones
        if ones and zeros:
            scored.append((min(ones, zeros), state))
    if not scored:
        return {'status': 'ABSTAIN', 'reason': 'NO_DISAGREEMENT', 'action_authorized': False}
    _, chosen = max(scored, key=lambda item: (item[0], tuple(-b for b in item[1])))
    return {'status': 'PROPOSED_UNCHARGED_HYPOTHETICAL', 'public_view': chosen,
            'external_action_id': action, 'hypothesis_count': len(survivors),
            'reachability_authenticated': False, 'charge_authenticated': False,
            'action_authorized': False, 'scientific_gain_verified': False}
