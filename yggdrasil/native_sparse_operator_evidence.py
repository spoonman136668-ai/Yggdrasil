"""Bounded four-public-bit structural hypothesis evidence (DEV only).

Owned by NativeEpisodeExperience as a passive optional fixture plane.
No hidden role, truth-law, source-actor, native counter update or Genome write.
A unanimous finite-grammar forecast is NOT a source-certified causal law.
"""
import hashlib
import itertools
import json

SCHEMA = 'yggdrasil.wscm.sparse-operator-evidence.dev.v1'
RECEIPT_SCHEMA = 'yggdrasil.wscm.sparse-public-fixture.dev.v1'
SOURCE_MODE = 'engineering_fixture_only'
MAX_EVENTS = 256
MAX_ACTIONS = 32
MAX_BYTES = 65536
MAX_RECEIPT_BYTES = 2048
STATES = tuple(itertools.product((0, 1), repeat=4))


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def _pin(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _request(value):
    if type(value) is not dict or set(value) != {'public_view', 'external_action_id'}:
        raise ValueError('SPARSE_PUBLIC_REQUEST')
    view, action = value['public_view'], value['external_action_id']
    if (type(view) is not list or len(view) != 4 or
        any(type(b) is not int or b not in (0, 1) for b in view) or
        type(action) is not int or not 0 <= action < 2**31):
        raise ValueError('SPARSE_PUBLIC_REQUEST')
    return tuple(view), action


def _row(raw, expected_sha256):
    if (type(raw) is not bytes or not 0 < len(raw) <= MAX_RECEIPT_BYTES or
        not _pin(expected_sha256) or hashlib.sha256(raw).hexdigest() != expected_sha256):
        raise ValueError('SPARSE_RECEIPT_PIN')
    try:
        obj = json.loads(raw.decode('ascii'))
        if (type(obj) is not dict or set(obj) != {'schema', 'source_mode', 'source_id',
            'public_view', 'external_action_id', 'outcome'} or
            obj['schema'] != RECEIPT_SCHEMA or obj['source_mode'] != SOURCE_MODE or
            not _pin(obj['source_id']) or type(obj['outcome']) is not int or
            obj['outcome'] not in (0, 1) or _canonical(obj) != raw):
            raise ValueError('SPARSE_FIXTURE_ONLY')
        view, action = _request({'public_view': obj['public_view'],
                                 'external_action_id': obj['external_action_id']})
    except (TypeError, KeyError, ValueError, UnicodeError, RecursionError) as exc:
        raise ValueError('SPARSE_FIXTURE_ONLY') from exc
    return (obj['source_id'], action, view, obj['outcome'], expected_sha256)


def _models():
    return tuple((parents, truth) for k in (0, 1, 2)
                 for parents in itertools.combinations(range(4), k)
                 for truth in itertools.product((0, 1), repeat=2**k))


MODELS = _models()  # 114 functions of at most two of four public variables.
assert len(MODELS) == 114


def _eval(model, view):
    parents, truth = model
    index = 0
    for p in parents:
        index = (index << 1) | view[p]
    return truth[index]


class NativeSparseOperatorEvidence:
    """Immutable witnessed input/output rows in the single native learner."""
    __slots__ = ('_rows', '_sources')

    def __init__(self):
        self._rows = ()
        self._sources = {}

    def observe_public_receipt(self, request, raw, expected_sha256):
        view, action = _request(request)
        row = _row(raw, expected_sha256)
        if row[1:3] != (action, view):
            raise ValueError('SPARSE_RECEIPT_MISMATCH')
        previous = self._sources.get(row[0])
        if previous is not None:
            if previous != row:
                raise ValueError('SPARSE_REPLAY_CONFLICT')
            return self
        if len(self._rows) >= MAX_EVENTS:
            raise ValueError('SPARSE_EVENT_CAPACITY')
        if action not in {r[1] for r in self._rows} and len({r[1] for r in self._rows}) >= MAX_ACTIONS:
            raise ValueError('SPARSE_ACTION_CAPACITY')
        next_state = type(self)()
        next_state._rows = self._rows + (row,)
        next_state._sources = {**self._sources, row[0]: row}
        next_state.checkpoint()
        return next_state

    def forecast(self, public_view, external_action_id):
        view, action = _request({'public_view': public_view,
                                 'external_action_id': external_action_id})
        evidence = [(v, outcome) for _, a, v, outcome, _ in self._rows if a == action]
        outcome = dict(source_mode=SOURCE_MODE, action_authorized=False,
                       scientific_gain_verified=False, hypothesis_count=0,
                       predicted_outcome=None)
        if not evidence:
            return dict(outcome, status='ABSTAIN', reason='NO_WITNESS')
        observed = {}
        for v, y in evidence:
            observed.setdefault(v, set()).add(y)
        if any(len(ys) != 1 for ys in observed.values()):
            return dict(outcome, status='CONTRADICTION', reason='CONFLICTING_WITNESSES')
        compatible = [m for m in MODELS if all(_eval(m, v) == y for v, y in evidence)]
        if not compatible:
            return dict(outcome, status='OUT_OF_GRAMMAR', reason='NO_SPARSE_LAW')
        predictions = {_eval(m, view) for m in compatible}
        if len(predictions) > 1:
            return dict(outcome, status='ABSTAIN', reason='DISAGREEMENT',
                        hypothesis_count=len(compatible))
        return dict(outcome, status='HYPOTHESIS_WITHIN_GRAMMAR',
                    reason='FINITE_GRAMMAR_UNANIMOUS', hypothesis_count=len(compatible),
                    predicted_outcome=next(iter(predictions)))

    def checkpoint(self):
        document = {'schema': SCHEMA, 'source_mode': SOURCE_MODE,
                    'records': [[sid, a, list(v), y, pin] for sid, a, v, y, pin in self._rows]}
        raw = _canonical(document)
        if len(raw) > MAX_BYTES:
            raise ValueError('SPARSE_CHECKPOINT_CAPACITY')
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        if (type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES or
            not _pin(expected_sha256) or hashlib.sha256(raw).hexdigest() != expected_sha256):
            raise ValueError('SPARSE_CHECKPOINT_PIN')
        try:
            obj = json.loads(raw.decode('ascii'))
            if (type(obj) is not dict or set(obj) != {'schema', 'source_mode', 'records'} or
                obj['schema'] != SCHEMA or obj['source_mode'] != SOURCE_MODE or
                type(obj['records']) is not list or len(obj['records']) > MAX_EVENTS or
                _canonical(obj) != raw):
                raise ValueError('SPARSE_CHECKPOINT_SCHEMA')
            restored = cls()
            for row in obj['records']:
                if type(row) is not list or len(row) != 5:
                    raise ValueError('SPARSE_CHECKPOINT_RECORD')
                sid, action, view, outcome, pin = row
                if not _pin(sid) or not _pin(pin) or sid in restored._sources:
                    raise ValueError('SPARSE_CHECKPOINT_SOURCE')
                canonical = _canonical({'schema': RECEIPT_SCHEMA, 'source_mode': SOURCE_MODE,
                                        'source_id': sid, 'public_view': view,
                                        'external_action_id': action, 'outcome': outcome})
                staged = restored.observe_public_receipt(
                    {'public_view': view, 'external_action_id': action}, canonical, pin)
                restored = staged
            if restored.checkpoint() != raw:
                raise ValueError('SPARSE_CHECKPOINT_REPLAY')
            return restored
        except (KeyError, TypeError, ValueError, UnicodeError, RecursionError) as exc:
            raise ValueError('SPARSE_CHECKPOINT_REJECTED') from exc
