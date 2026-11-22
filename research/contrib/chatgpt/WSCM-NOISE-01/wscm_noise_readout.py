"""WSCM-NOISE-01: read-only, fixture-only noisy return-role posterior (DEV).

This is exact Bayesian model averaging over all sixteen four-view binary
functions. It is deliberately NOT a new native learner, source authenticator,
or evidence of advantage over an equally informed exact Bayesian control.
"""
import hashlib
import json
import math

SOURCE_SCHEMA = 'yggdrasil.wscm.external-action-evidence.dev.v1'
RECEIPT_SCHEMA = 'yggdrasil.wscm.public-action-fixture.dev.v1'
SOURCE_MODE = 'engineering_fixture_only'
RESULT_SCHEMA = 'yggdrasil.wscm.noise-role-readout.dev.v1'
STATES = ((0, 0), (0, 1), (1, 0), (1, 1))
FUNCTIONS = tuple(tuple((f >> (3 - i)) & 1 for i in range(4)) for f in range(16))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def pin(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def checked_id(value):
    require(type(value) is int and 0 <= value < 2**31, 'WSCM_ACTION_ID')
    return value


def read_fixture(raw, expected_sha):
    """Validate fixture byte integrity; a SHA is NOT intervention authenticity."""
    require(type(raw) is bytes and 0 < len(raw) <= 65536 and pin(expected_sha)
            and sha256(raw) == expected_sha, 'WSCM_FIXTURE_PIN')
    try:
        obj = json.loads(raw.decode('ascii'))
        require(type(obj) is dict and set(obj) == {'schema', 'source_mode', 'records'}
                and obj['schema'] == SOURCE_SCHEMA and obj['source_mode'] == SOURCE_MODE
                and type(obj['records']) is list and len(obj['records']) <= 256
                and canonical(obj) == raw, 'WSCM_FIXTURE_SCHEMA')
        ids, actions, rows = set(), set(), []
        for entry in obj['records']:
            require(type(entry) is list and len(entry) == 5, 'WSCM_FIXTURE_ROW')
            sid, action, view, result, receipt_pin = entry
            checked_id(action)
            require(pin(sid) and sid not in ids and pin(receipt_pin)
                    and type(view) is list and len(view) == 2
                    and all(type(x) is int and x in (0, 1) for x in view)
                    and type(result) is int and result in (0, 1), 'WSCM_FIXTURE_ROW')
            receipt = {'schema': RECEIPT_SCHEMA, 'source_mode': SOURCE_MODE,
                       'source_id': sid, 'external_action_id': action,
                       'public_view': view, 'outcome': result}
            require(sha256(canonical(receipt)) == receipt_pin, 'WSCM_FIXTURE_RECEIPT')
            ids.add(sid)
            actions.add(action)
            rows.append((sid, action, STATES.index(tuple(view)), result, receipt_pin))
        require(len(actions) <= 16, 'WSCM_ACTION_CAPACITY')
        return tuple(rows)
    except (ValueError, TypeError, UnicodeError, KeyError, RecursionError) as exc:
        raise ValueError('WSCM_FIXTURE_REJECTED') from exc


def _normalize(logs):
    m = max(logs)
    weights = [math.exp(x - m) for x in logs]
    total = sum(weights)
    return tuple(w / total for w in weights)


def evaluate(raw, expected_sha, old_id, new_id, *, noise=0.1, reuse_prior=0.5):
    """Full 16-function posterior; unknown function always retains prior mass.

    The old ID's function posterior is learned from its public observations.
    The new ID prior mixes reuse of that posterior with a uniform open-world
    16-function prior. Both likelihoods use the exact same public witnesses.
    """
    checked_id(old_id)
    checked_id(new_id)
    require(old_id != new_id, 'WSCM_SAME_ACTION_ID')
    require(type(noise) is float and 0.0 < noise < 0.5
            and type(reuse_prior) is float and 0.0 < reuse_prior < 1.0,
            'WSCM_PRIOR_RANGE')
    rows = read_fixture(raw, expected_sha)
    old = [(state, outcome) for _, action, state, outcome, _ in rows if action == old_id]
    new = [(state, outcome) for _, action, state, outcome, _ in rows if action == new_id]
    def loglike(samples):
        return tuple(sum(math.log(1.0 - noise) if f[s] == o else math.log(noise)
                         for s, o in samples) for f in FUNCTIONS)
    p_old = _normalize(loglike(old))
    mixed = tuple(reuse_prior * p + (1.0 - reuse_prior) / 16.0 for p in p_old)
    l_new = loglike(new)
    p_new = _normalize(tuple(math.log(p) + ll for p, ll in zip(mixed, l_new)))
    # Marginalize the latent 'reuse old function' indicator, not an oracle label.
    m = max(l_new)
    scaled_new = tuple(math.exp(x - m) for x in l_new)
    reuse_num = reuse_prior * sum(a * b for a, b in zip(p_old, scaled_new))
    novel_num = (1.0 - reuse_prior) * sum(scaled_new) / 16.0
    p_reuse = reuse_num / (reuse_num + novel_num)
    predictions = tuple(sum(p * f[state] for p, f in zip(p_new, FUNCTIONS))
                        for state in range(4))
    # Probabilistic readout, not a certificate: conservatively abstain on role
    # binding unless both reuse and specific function are at least 95% likely.
    certified = p_reuse >= 0.95 and max(p_new) >= 0.95
    return {'schema': RESULT_SCHEMA, 'source_mode': SOURCE_MODE,
            'old_witnesses': len(old), 'new_witnesses': len(new),
            'reuse_probability': p_reuse,
            'maximum_function_probability': max(p_new),
            'probability_one_by_view': predictions,
            'provisional_role_binding': certified,
            'scientific_pass': False, 'native_accepted': False}
