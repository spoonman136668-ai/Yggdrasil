"""CVH02: public-only choose/observe adapter for existing CVH01 earned memory.

No upstream source, constructor, reset, do, private evaluator or training label.
A source policy may be reused across completed episodes, but not an unclosed
budget-exhausted episode. An unobserved selected action may never be replayed.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'CVH-01'
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))
from earned_memory import EarnedReturnMemory, FIELDS, _slot, _canonical

SCHEMA = 'yggdrasil.cvh02.source-blind-public-policy.v1'
MAX_EPISODE_ROWS = 32


def _event(row):
    if tuple(getattr(row, '_fields', ())) != FIELDS:
        raise ValueError('CVH02_PUBLIC_FIELDS_ONLY')
    b, a, r, n, done, truncated = row
    if any(type(x) is not int or x not in (0, 1) for x in (b, a, r, n)):
        raise ValueError('CVH02_PUBLIC_BINARY_EVENT')
    if type(done) is not bool or type(truncated) is not bool or (done and truncated):
        raise ValueError('CVH02_PUBLIC_TERMINATION')
    return [b, a, r, n, done, truncated]


class PublicEarnedPolicy:
    """Source-facing policy; none of its methods can invoke an environment."""
    def __init__(self, min_support=2):
        if type(min_support) is not int or not 1 <= min_support <= 100:
            raise ValueError('CVH02_INVALID_SUPPORT')
        self.memory = EarnedReturnMemory()
        self.attempts = [0] * 36
        self.episode_history = []
        self.outstanding = None
        self.min_support = min_support

    def choose(self, state, history):
        if type(state) is not int or state not in (0, 1):
            raise ValueError('CVH02_NONPUBLIC_STATE')
        if type(history) is not tuple:
            raise ValueError('CVH02_PUBLIC_HISTORY_TUPLE')
        if self.outstanding is not None:
            raise ValueError('CVH02_UNOBSERVED_ACTION_IN_FLIGHT')
        actual = [_event(row) for row in history]
        if actual != self.episode_history:
            raise ValueError('CVH02_HISTORY_DRIFT_OR_UNCLOSED_EPISODE')
        if len(actual) >= MAX_EPISODE_ROWS:
            raise ValueError('CVH02_EPISODE_BUDGET_REQUIRES_EXTERNAL_CLOSURE')
        if self.memory.previous_after is not None and state != self.memory.previous_after:
            raise ValueError('CVH02_PUBLIC_CONTINUITY_MISMATCH')
        if self.memory.previous_after is None and actual:
            raise ValueError('CVH02_INTERNAL_EPISODE_BOUNDARY')
        pa, pr = self.memory.prev_action, self.memory.prev_reward
        selected = self.memory.choose_supported(state, pa, pr, self.min_support)
        if selected is None:
            k0 = _slot(pa, pr, state, 0)
            k1 = _slot(pa, pr, state, 1)
            selected = 0 if self.attempts[k0] <= self.attempts[k1] else 1
        self.outstanding = (state, selected)
        return selected

    def observe(self, row):
        event = _event(row)
        if self.outstanding is None or event[0:2] != list(self.outstanding):
            raise ValueError('CVH02_UNEXPECTED_SOURCE_OUTCOME')
        if len(self.episode_history) >= MAX_EPISODE_ROWS:
            raise ValueError('CVH02_BUDGET_EXCEEDED')
        # Memory validates the public consequence and commits atomic return data.
        # No source call or uncertain-effect replay on failure.
        pa, pr = self.memory.prev_action, self.memory.prev_reward
        slot = _slot(pa, pr, event[0], event[1])
        if self.attempts[slot] >= 1000000:
            raise ValueError('CVH02_ATTEMPT_LIMIT')
        self.memory.observe(row)
        self.attempts[slot] += 1
        if event[4] or event[5]:
            self.episode_history = []
        else:
            self.episode_history.append(event)
        self.outstanding = None

    def snapshot(self):
        if self.outstanding is not None:
            raise ValueError('CVH02_UNCONFIRMED_ACTION_CANNOT_SNAPSHOT')
        state = {
            'schema': SCHEMA,
            'minimum_support': self.min_support,
            'memory_json': self.memory.snapshot().decode('ascii'),
            'attempts': self.attempts,
            'episode_history': self.episode_history,
        }
        return _canonical({'payload': state, 'sha256': sha256(_canonical(state)).hexdigest()})

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not 0 < len(raw) < 20000:
            raise ValueError('CVH02_BAD_COLD_BYTES')
        try:
            d = json.loads(raw)
            if type(d) is not dict or set(d) != {'payload', 'sha256'}:
                raise ValueError('CVH02_COLD_ENVELOPE')
            p = d['payload']
            if type(p) is not dict or set(p) != {'schema', 'minimum_support', 'memory_json', 'attempts', 'episode_history'}:
                raise ValueError('CVH02_COLD_SCHEMA')
            if _canonical(d) != raw or sha256(_canonical(p)).hexdigest() != d['sha256'] or p['schema'] != SCHEMA:
                raise ValueError('CVH02_COLD_INTEGRITY')
            m = EarnedReturnMemory.restore(p['memory_json'].encode('ascii'))
            counts = p['attempts']
            hist = p['episode_history']
            if type(counts) is not list or len(counts) != 36 or any(type(x) is not int or not 0 <= x <= 1000000 for x in counts):
                raise ValueError('CVH02_COLD_ATTEMPTS')
            if type(hist) is not list or len(hist) >= MAX_EPISODE_ROWS or any(type(e) is not list or len(e) != 6 or any(type(x) is not int or x not in (0,1) for x in e[:4]) or any(type(x) is not bool for x in e[4:]) or e[4] or e[5] for e in hist):
                raise ValueError('CVH02_COLD_HISTORY')
            if (bool(hist) != (m.previous_after is not None) or
                (hist and (hist[-1][3] != m.previous_after or hist[-1][1] != m.prev_action or hist[-1][2] != m.prev_reward)) or
                sum(counts) != m.seen):
                raise ValueError('CVH02_COLD_CUSTODY')
            result = cls(p['minimum_support'])
            result.memory = m
            result.attempts = counts[:]
            result.episode_history = [e[:] for e in hist]
            if result.snapshot() != raw:
                raise ValueError('CVH02_COLD_NONCANONICAL')
            return result
        except (TypeError, ValueError, KeyError, UnicodeError, AttributeError) as e:
            raise ValueError('CVH02_COLD_REJECTED') from e
