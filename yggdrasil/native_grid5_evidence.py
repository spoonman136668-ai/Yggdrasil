"""WSCM public grid5 fixture evidence, carried by ONE native episode learner.

This is a bounded, immutable development-only evidence component. It is NOT a
causal law learner, original-world credential, separate planner or source actor.
"""
import hashlib
import json

from yggdrasil.native_grid5_ingress import (
    SCHEMA as RECEIPT_SCHEMA, SOURCE_MODE, MAX_BATCH,
    public_state, public_request, accept_fixture_receipt, canonical, pinned, _unique,
)

SCHEMA = 'yggdrasil.wscm.grid5-evidence.dev.v1'
MAX_CHECKPOINT_BYTES = 128 * 1024


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


class NativeGrid5Evidence:
    """Immutable source-free witness ledger; only observed state/action successors.

    An instance is always held inside NativeEpisodeExperience in the integrated
    variant. This stand-alone type is evidence serialization, not a learner.
    """
    __slots__ = ('_rows', '_source_ids')

    def __init__(self):
        self._rows = ()
        self._source_ids = {}

    def observe_public_receipt(self, request, raw, expected_sha256):
        row = accept_fixture_receipt(request, raw, expected_sha256)
        source_id, episode_id, step, before, action, after, reward, term, trunc, pin = row
        previous = self._source_ids.get(source_id)
        if previous is not None:
            _require(previous == row, 'GRID5_SOURCE_REPLAY_CONFLICT')
            return self
        _require(len(self._rows) < MAX_BATCH, 'GRID5_EVENT_CAPACITY')
        if not self._rows:
            _require(step == 0 and before == (0, 0), 'GRID5_INITIAL_PUBLIC_RESET')
        else:
            last = self._rows[-1]
            if episode_id == last[1]:
                _require(not last[7] and step == last[2] + 1 and before == last[5],
                         'GRID5_EPISODE_DRIFT')
            else:
                _require(last[7] and step == 0 and before == (0, 0) and
                         episode_id not in {old[1] for old in self._rows},
                         'GRID5_EPISODE_REENTRY')
        staged = type(self)()
        staged._rows = self._rows + (row,)
        staged._source_ids = {**self._source_ids, source_id: row}
        staged.checkpoint()
        return staged

    def public_forecast(self, state, action, *, episode_id):
        """Exact SAME-EPISODE public witness; never reuse an unknown new law.

        Hidden action permutations may change between episodes. Query callers
        must explicitly identify their active public episode; neither a prior
        episode nor an implicit last-seen ID supplies transferable knowledge.
        """
        state = public_state(state)
        if type(action) is not int or not 0 <= action < 5:
            raise ValueError('GRID5_ACTION')
        if not pinned(episode_id):
            raise ValueError('GRID5_EPISODE_PIN')
        answers = {r[5] for r in self._rows
                   if r[1] == episode_id and r[3] == state and r[4] == action}
        return list(next(iter(answers))) if len(answers) == 1 else None

    def public_plan(self, state, *, episode_id):
        """Same-episode coverage proposal only, NOT action-role learning.

        Future episodes may present a different hidden action permutation.
        The caller must supply an explicit public episode ID, and all counts
        and witnessed outcomes remain isolated to that episode.
        """
        state = public_state(state)
        if not pinned(episode_id):
            raise ValueError('GRID5_EPISODE_PIN')
        counts = tuple(sum(r[1] == episode_id and r[3] == state and r[4] == a
                           for r in self._rows) for a in range(5))
        action = min(range(5), key=lambda a: (counts[a], a))
        return {
            'source_mode': SOURCE_MODE,
            'public_action': action,
            'observed_next_state': self.public_forecast(
                list(state), action, episode_id=episode_id),
            'witness_count': counts[action],
        }

    def checkpoint(self):
        obj = {
            'schema': SCHEMA, 'source_mode': SOURCE_MODE,
            'records': [
                [source_id, episode, step, list(before), action, list(after), reward,
                 term, trunc, pin]
                for source_id, episode, step, before, action, after, reward, term, trunc, pin
                in self._rows
            ],
            'native_accepted': False, 'scientific_pass': False,
        }
        raw = canonical(obj)
        _require(len(raw) <= MAX_CHECKPOINT_BYTES, 'GRID5_CHECKPOINT_CAPACITY')
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        _require(type(raw) is bytes and 0 < len(raw) <= MAX_CHECKPOINT_BYTES and
                 pinned(expected_sha256) and hashlib.sha256(raw).hexdigest() == expected_sha256,
                 'GRID5_CHECKPOINT_PIN')
        try:
            obj = json.loads(raw.decode('ascii'), object_pairs_hook=_unique)
            _require(type(obj) is dict and set(obj) == {
                'schema', 'source_mode', 'records', 'native_accepted', 'scientific_pass'
            } and obj['schema'] == SCHEMA and obj['source_mode'] == SOURCE_MODE
                and obj['native_accepted'] is False and obj['scientific_pass'] is False
                and type(obj['records']) is list and 0 < len(obj['records']) <= MAX_BATCH
                and raw == canonical(obj), 'GRID5_CHECKPOINT_SCHEMA')
            result = cls()
            for entry in obj['records']:
                _require(type(entry) is list and len(entry) == 10,
                         'GRID5_CHECKPOINT_ROW')
                sid, episode, step, before, action, after, reward, term, trunc, pin = entry
                request = {'episode_id': episode, 'step_index': step,
                           'public_state': before, 'public_action': action}
                public_request(request)
                _require(pinned(sid) and pinned(pin), 'GRID5_CHECKPOINT_ROW_PIN')
                receipt = canonical({
                    **request, 'schema': RECEIPT_SCHEMA, 'source_mode': SOURCE_MODE,
                    'source_id': sid, 'next_state': after, 'reward': reward,
                    'terminated': term, 'truncated': trunc,
                })
                _require(hashlib.sha256(receipt).hexdigest() == pin,
                         'GRID5_CHECKPOINT_RECEIPT_DRIFT')
                result = result.observe_public_receipt(request, receipt, pin)
            _require(result.checkpoint() == raw, 'GRID5_CHECKPOINT_REPLAY')
            return result
        except (ValueError, KeyError, TypeError, UnicodeError, OverflowError,
                RecursionError, IndexError) as e:
            raise ValueError('GRID5_CHECKPOINT_REJECTED') from e
