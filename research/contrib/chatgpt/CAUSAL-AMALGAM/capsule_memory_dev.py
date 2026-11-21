"""CASP-01 source-free DEV capsule memory; not admitted to NativeCausalAmalgam.

Public two-bit views route to independent numeric causal-rule capsules. Witnesses
are unique and replayed during cold restoration. A local persistent surprise
can activate one action-specific exception without changing other capsules.
No hidden task label, protected source action, controller or production write.
"""
from fractions import Fraction
from hashlib import sha256
from math import gcd
import json

SCHEMA = 'yggdrasil.amalgam.casp01.source-free-capsules.v1'
LIKELIHOOD_MATCH = 15  # observation noise 1/16, fixed before evaluation
SURPRISE_LIMIT = Fraction(1, 8)
REPAIR_STREAK = 3


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def digest(raw):
    return sha256(raw).hexdigest()


def bit(v):
    if type(v) is not int or v not in (0, 1):
        raise ValueError('CASP_BIT')
    return v


def view_key(view):
    if type(view) not in (list, tuple) or len(view) != 2:
        raise ValueError('CASP_PUBLIC_VIEW')
    return tuple(bit(v) for v in view)


def rule_values(action):
    return (0, 1, action, 1 - action)


class CapsuleMemory:
    """Exact-rule local learning and bounded, evidence-triggered exceptions."""

    def __init__(self, max_capsules=4, max_events=256, max_repairs=4):
        if (type(max_capsules) is not int or not 1 <= max_capsules <= 4 or
                type(max_events) is not int or not 1 <= max_events <= 4096 or
                type(max_repairs) is not int or not 0 <= max_repairs <= 8):
            raise ValueError('CASP_LIMITS')
        self.max_capsules = max_capsules
        self.max_events = max_events
        self.max_repairs = max_repairs
        self._cells = {}
        self._records = []
        self._ids = {}

    @staticmethod
    def _cell():
        return {'weights': [1, 1, 1, 1], 'streaks': [0, 0],
                'exceptions': [None, None], 'surprise_last': [None, None], 'total': 0}

    def predict(self, view, action):
        cue = view_key(view)
        action = bit(action)
        cell = self._cells.get(cue)
        if cell is None:
            return Fraction(1, 2)
        exc = cell['exceptions'][action]
        if exc is not None:
            return Fraction(1 + exc[1], 2 + exc[0] + exc[1])
        weights = cell['weights']
        outcomes = rule_values(action)
        numerator = sum(w * (LIKELIHOOD_MATCH if pred else 1)
                        for w, pred in zip(weights, outcomes))
        return Fraction(numerator, 16 * sum(weights))

    def choose_action(self, view):
        return int(self.predict(view, 1) > self.predict(view, 0))

    def observe(self, evidence_id, view, action, outcome):
        if (type(evidence_id) is not str or len(evidence_id) != 64 or
                any(c not in '0123456789abcdef' for c in evidence_id)):
            raise ValueError('CASP_EVIDENCE_PIN')
        cue = view_key(view)
        action, outcome = bit(action), bit(outcome)
        record = [evidence_id, list(cue), action, outcome]
        if evidence_id in self._ids:
            if self._ids[evidence_id] != record:
                raise ValueError('CASP_CONFLICTING_REPLAY')
            return False
        if len(self._records) >= self.max_events:
            raise ValueError('CASP_EVENT_CAPACITY')
        if cue not in self._cells and len(self._cells) >= self.max_capsules:
            raise ValueError('CASP_CAPSULE_CAPACITY')
        cell = self._cells.get(cue)
        if cell is None:
            cell = self._cell()
        prob = self.predict(cue, action)
        surprise = (prob if outcome else 1 - prob) <= SURPRISE_LIMIT
        streak = (cell['streaks'][action] + 1 if cell['surprise_last'][action] == outcome
                  else 1) if surprise else 0
        new_exception = cell['exceptions'][action] is None and streak >= REPAIR_STREAK
        repairs = sum(x is not None for c in self._cells.values()
                      for x in c['exceptions'])
        if new_exception and repairs >= self.max_repairs:
            raise ValueError('CASP_REPAIR_CAPACITY')
        # All validation occurs before changing the learner, including repair cap.
        if cue not in self._cells:
            self._cells[cue] = cell
        cell['streaks'][action] = streak
        cell['surprise_last'][action] = outcome if surprise else None
        if new_exception:
            # Last REPAIR_STREAK surprising outcomes were all the same in this
            # binary likelihood direction because p(actual) was <= 1/8.
            cell['exceptions'][action] = [REPAIR_STREAK if not outcome else 0,
                                          REPAIR_STREAK if outcome else 0]
        elif cell['exceptions'][action] is not None:
            cell['exceptions'][action][outcome] += 1
        weights = [w * (LIKELIHOOD_MATCH if pred == outcome else 1)
                   for w, pred in zip(cell['weights'], rule_values(action))]
        common = gcd(gcd(weights[0], weights[1]), gcd(weights[2], weights[3]))
        cell['weights'] = [w // common for w in weights]
        cell['total'] += 1
        self._records.append(record)
        self._ids[evidence_id] = record
        return True

    def info(self):
        return {'events': len(self._records), 'capsules': len(self._cells),
                'repairs': sum(x is not None for c in self._cells.values()
                               for x in c['exceptions']),
                'max_capsules': self.max_capsules, 'max_events': self.max_events}

    def checkpoint(self):
        return canonical({'schema': SCHEMA, 'limits': [self.max_capsules,
                         self.max_events, self.max_repairs], 'records': self._records,
                         'cells': [list(k) + [v['weights'], v['streaks'],
                                            v['exceptions'], v['surprise_last'], v['total']]
                                   for k, v in sorted(self._cells.items())]})

    @classmethod
    def restore(cls, raw, expected_sha256):
        if (type(raw) is not bytes or type(expected_sha256) is not str or
                digest(raw) != expected_sha256 or len(raw) > 2**20):
            raise ValueError('CASP_CHECKPOINT_PIN')
        try:
            doc = json.loads(raw)
            if set(doc) != {'schema', 'limits', 'records', 'cells'} or doc['schema'] != SCHEMA:
                raise ValueError('CASP_SCHEMA')
            restored = cls(*doc['limits'])
            for evidence_id, cue, action, outcome in doc['records']:
                if not restored.observe(evidence_id, cue, action, outcome):
                    raise ValueError('CASP_REPLAY_DUPLICATE')
            if restored.checkpoint() != raw:
                raise ValueError('CASP_NONCANONICAL_OR_TAMPERED')
        except (KeyError, TypeError, IndexError, json.JSONDecodeError) as err:
            raise ValueError('CASP_CORRUPT_CHECKPOINT') from err
        return restored
