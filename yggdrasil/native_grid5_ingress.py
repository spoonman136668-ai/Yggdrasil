"""WSCM grid5 development-only public intervention receipt validator.

Stateless and source-free: no environment step, memory update, role map, planner,
source-owner admission, or real-world authenticity is conveyed by a hash.
Intended to guard a future *existing-native-memory* intake, not replace it.
"""
import hashlib
import json

SCHEMA = 'yggdrasil.wscm.grid5-public-fixture.dev.v1'
SOURCE_MODE = 'engineering_fixture_only'
SIDE = 9
ACTIONS = 5
HORIZON = 50
MAX_RECEIPT_BYTES = 2048
MAX_BATCH = 256
REQUEST_FIELDS = frozenset(('episode_id', 'step_index', 'public_state', 'public_action'))
RECEIPT_FIELDS = REQUEST_FIELDS | frozenset((
    'schema', 'source_mode', 'source_id', 'next_state', 'reward',
    'terminated', 'truncated',
))


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


def pinned(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def public_state(value):
    if (type(value) is not list or len(value) != 2 or
        any(type(c) is not int or c < 0 or c >= SIDE for c in value)):
        raise ValueError('GRID5_STATE')
    return tuple(value)


def public_request(value):
    if type(value) is not dict or value.keys() != REQUEST_FIELDS:
        raise ValueError('GRID5_REQUEST_FIELDS')
    if not pinned(value['episode_id']):
        raise ValueError('GRID5_EPISODE_PIN')
    step = value['step_index']
    action = value['public_action']
    if type(step) is not int or not 0 <= step < HORIZON:
        raise ValueError('GRID5_STEP')
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError('GRID5_ACTION')
    return (value['episode_id'], step, public_state(value['public_state']), action)


def accept_fixture_receipt(request, raw, expected_sha256):
    """Validate exactly a public witness and return an immutable observable tuple.

    Tuple order: (source_id, episode_id, step, state, action, next_state,
                  reward, terminated, truncated, receipt_sha256).
    Bytes and all nested fields are validated before any data is returned.
    """
    expected = public_request(request)
    if (type(raw) is not bytes or not 0 < len(raw) <= MAX_RECEIPT_BYTES
        or not pinned(expected_sha256)
        or hashlib.sha256(raw).hexdigest() != expected_sha256):
        raise ValueError('GRID5_RECEIPT_PIN')
    try:
        data = json.loads(raw.decode('ascii'), object_pairs_hook=_unique)
        if (type(data) is not dict or data.keys() != RECEIPT_FIELDS
            or data['schema'] != SCHEMA or data['source_mode'] != SOURCE_MODE
            or not pinned(data['source_id']) or canonical(data) != raw):
            raise ValueError('GRID5_RECEIPT_SCHEMA')
        if public_request({key: data[key] for key in REQUEST_FIELDS}) != expected:
            raise ValueError('GRID5_REQUEST_RECEIPT_MISMATCH')
        successor = public_state(data['next_state'])
        state = expected[2]
        if abs(state[0] - successor[0]) + abs(state[1] - successor[1]) > 1:
            raise ValueError('GRID5_IMPOSSIBLE_MOVE')
        if type(data['reward']) is not int or data['reward'] not in (0, 1):
            raise ValueError('GRID5_REWARD')
        terminated = data['terminated']
        truncated = data['truncated']
        if (type(terminated) is not bool or type(truncated) is not bool
            or terminated is not truncated
            or terminated is not (expected[1] == HORIZON - 1)):
            raise ValueError('GRID5_TERMINAL')
    except (TypeError, KeyError, ValueError, UnicodeError, RecursionError, OverflowError) as e:
        raise ValueError('GRID5_RECEIPT_REJECTED') from e
    return (data['source_id'], expected[0], expected[1], expected[2],
            expected[3], successor, data['reward'], terminated, truncated,
            expected_sha256)


def _unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('GRID5_DUPLICATE_KEY')
        obj[key] = value
    return obj


def validate_public_batch(items):
    """Check strict sequential continuity, uniqueness and source-free replay safety.

    `items` is a *list* of triples (request, raw bytes, expected_sha256).
    No data is persisted and no hidden environment state is consulted.
    """
    if type(items) is not list or not 0 < len(items) <= MAX_BATCH:
        raise ValueError('GRID5_BATCH_CAPACITY')
    events = []
    seen_receipt_ids = set()
    closed_episodes = set()
    current_episode = None
    previous = None
    for item in items:
        if type(item) is not tuple or len(item) != 3:
            raise ValueError('GRID5_BATCH_ELEMENT')
        event = accept_fixture_receipt(*item)
        source_id, episode_id, step, state, action, successor, reward, end, trunc, _ = event
        if source_id in seen_receipt_ids:
            raise ValueError('GRID5_SOURCE_REPLAY')
        seen_receipt_ids.add(source_id)
        if episode_id != current_episode:
            if episode_id in closed_episodes or step != 0 or state != (0, 0):
                raise ValueError('GRID5_EPISODE_REENTRY_OR_RESET')
            if previous is not None:
                if previous[7] is not True:
                    raise ValueError('GRID5_PREMATURE_RESET')
                closed_episodes.add(current_episode)
            current_episode = episode_id
        elif (previous is None or previous[7] is True or
              step != previous[2] + 1 or state != previous[5]):
            raise ValueError('GRID5_SEQUENCE_DRIFT')
        events.append(event)
        previous = event
    return tuple(events)
