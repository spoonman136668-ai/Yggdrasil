"""Generic source-blind local causal memory and independently coded Bayes.

Neither learner imports the generator, enumerates a family of causal laws,
reads hidden labels, or receives alternative action outcomes.
"""
from __future__ import annotations
from hashlib import sha256
import struct

CONTEXTS = 128
ACTIONS = 8
MAX_ROWS = 2048
FIELDS = ('context', 'action', 'reward', 'history')
PRIOR_FIELDS = ('context', 'action')


def _validate(row):
    if tuple(getattr(row, '_fields', ())) != FIELDS:
        raise ValueError('SFI04_PUBLIC_EVENT_ONLY')
    if type(row.context) is not int or not 0 <= row.context < CONTEXTS:
        raise ValueError('SFI04_CONTEXT')
    if type(row.action) is not int or not 0 <= row.action < ACTIONS:
        raise ValueError('SFI04_ACTION')
    if type(row.reward) is not int or row.reward not in (-1, 0, 1):
        raise ValueError('SFI04_REWARD')
    if type(row.history) is not tuple or len(row.history) > 2:
        raise ValueError('SFI04_HISTORY')
    for x in row.history:
        if tuple(getattr(x, '_fields', ())) != PRIOR_FIELDS:
            raise ValueError('SFI04_HISTORY_SCHEMA')
        if type(x.context) is not int or not 0 <= x.context < CONTEXTS:
            raise ValueError('SFI04_HISTORY_CONTEXT')
        if type(x.action) is not int or not 0 <= x.action < ACTIONS:
            raise ValueError('SFI04_HISTORY_ACTION')
    if (len(row.history) < 2) != (row.reward == 0):
        raise ValueError('SFI04_DELAYED_FEEDBACK')
    return row.history[0] if len(row.history) == 2 else None


class DirectWeights:
    logical_bytes = 128

    def __init__(self):
        self.masks = bytearray([255] * CONTEXTS)
        self.rows = 0
        self.digest = sha256()
        self.observed = set()

    def observe(self, row):
        if self.rows >= MAX_ROWS:
            raise ValueError('SFI04_BUDGET')
        credit = _validate(row)
        if credit is not None:
            before = self.masks[credit.context]
            proposed = ((1 << credit.action) if row.reward == 1
                        else before & ~(1 << credit.action))
            proposed &= before
            if not proposed:
                raise ValueError('SFI04_CONTRADICTION')
        self.digest.update(struct.pack('<BBb', row.context, row.action, row.reward))
        self.rows += 1
        if credit is not None:
            self.masks[credit.context] = proposed
            self.observed.add(credit.context)

    def choose(self, context):
        if type(context) is not int or not 0 <= context < CONTEXTS:
            raise ValueError('SFI04_CHOOSE_CONTEXT')
        mask = self.masks[context]
        return next(a for a in range(ACTIONS) if (mask >> a) & 1)

    def checkpoint(self):
        return bytes(self.masks)

    def restore(self, saved):
        if type(saved) is not bytes or len(saved) != CONTEXTS or any(v == 0 for v in saved):
            raise ValueError('SFI04_CHECKPOINT_INVALID')
        self.masks = bytearray(saved)

    def receipt(self):
        return sha256(b'SFI04-DIRECT-v1' + self.masks + self.digest.digest() +
                      self.rows.to_bytes(4, 'little')).hexdigest()


class ExactBayes:
    """Independent uniform categorical posterior with hard likelihoods."""
    logical_bytes_limit = 8192

    def __init__(self):
        self.posterior = [[1] * ACTIONS for _ in range(CONTEXTS)]
        self.rows = 0
        self.observed = set()

    def observe(self, row):
        if self.rows >= MAX_ROWS:
            raise ValueError('SFI04_BAYES_BUDGET')
        credited = _validate(row)
        if credited is not None:
            old = self.posterior[credited.context]
            update = [int(v and ((i == credited.action) == (row.reward == 1)))
                      for i, v in enumerate(old)]
            if not any(update):
                raise ValueError('SFI04_BAYES_CONTRADICTION')
            self.posterior[credited.context] = update
            self.observed.add(credited.context)
        self.rows += 1

    def choose(self, context):
        if type(context) is not int or not 0 <= context < CONTEXTS:
            raise ValueError('SFI04_BAYES_CHOOSE_CONTEXT')
        return max(range(ACTIONS), key=lambda a: (self.posterior[context][a], -a))


class ShuffledCredit(DirectWeights):
    def observe(self, row):
        credit = _validate(row)
        if credit is not None:
            # Keep all other evidence identical, but assign reward to
            # another context. Never access a private source label.
            from collections import namedtuple
            Public = namedtuple('Public', FIELDS)
            Attempt = namedtuple('Attempt', PRIOR_FIELDS)
            altered = Public(row.context, row.action, row.reward,
                             (Attempt((credit.context + 1) % CONTEXTS, credit.action),
                              Attempt(row.history[1].context, row.history[1].action)))
            try:
                super().observe(altered)
            except ValueError as e:
                if 'CONTRADICTION' not in str(e):
                    raise
                # A corrupted causal assignment makes its own table
                # inconsistent. Preserve the negative without fake repair.
                self.rows += 1
        else:
            super().observe(row)


class NoUpdate:
    def observe(self, row):
        _validate(row)

    def choose(self, context):
        if type(context) is not int or not 0 <= context < CONTEXTS:
            raise ValueError('SFI04_NO_UPDATE_CONTEXT')
        return 0
