"""ACE03 engineering prototype: bounded public-context sequential readouts.

Not a native learner, context-discovery mechanism, or scored experiment.
The caller supplies observable context keys; unknown keys abstain.
"""
import hashlib
import itertools
import math
import struct

PAIRS = tuple(itertools.combinations(range(9), 2))
WARMUP = 128
GATE = 128
LIMIT = 65535
MARGIN = .003
MAGIC = b'ACE03AC1'
HEADER = struct.Struct('<8sHQ')
ROW = struct.Struct('<HHh36i25d4d')
KINDS = ('pool', 'pair', 'dense', 'compose')


def sigmoid(z):
    return 1 / (1 + math.exp(-max(-32., min(32., z))))


def features(pattern, pair):
    x = tuple(2 * ((pattern >> i) & 1) - 1 for i in range(9))
    if pair < 0:
        return (1, *x), (), ()
    i, j = PAIRS[pair]
    t = x[i] * x[j]
    return (1, *x), (1, x[i], x[j], t), (1, *x, t)


def fit_step(w, x, y, age):
    p = sigmoid(sum(a * b for a, b in zip(w, x)))
    step = .125 / math.sqrt(1 + age / 256) * (y - p)
    return [max(-32., min(32., a + step * b)) for a, b in zip(w, x)]


class State:
    def __init__(self):
        self.n, self.ones, self.pair = 0, 0, -1
        self.corr = [0] * 36
        self.w = [0.] * 25  # dense (10), pair (4), compose (11)
        self.loss = [0.] * 4

    def forecasts(self, pattern):
        dense, pair, compose = features(pattern, self.pair)
        pool = (self.ones + 1) / (self.n + 2)
        d = sigmoid(sum(a * b for a, b in zip(self.w[:10], dense)))
        if self.pair < 0:
            return pool, pool, d, pool
        p = sigmoid(sum(a * b for a, b in zip(self.w[10:14], pair)))
        c = sigmoid(sum(a * b for a, b in zip(self.w[14:], compose)))
        return pool, p, d, c

    def choice(self):
        age = self.n - WARMUP
        if age < GATE:
            return 0
        best = min(self.loss)
        return next(i for i, loss in enumerate(self.loss)
                    if loss <= best + MARGIN * age)

    def update(self, pattern, y):
        if self.n == LIMIT:
            raise OverflowError('context counter capacity exhausted')
        dense, pair, compose = features(pattern, self.pair)
        if self.n < WARMUP:
            x = dense[1:]
            self.corr = [c + (2*y-1)*x[i]*x[j]
                         for c, (i, j) in zip(self.corr, PAIRS)]
        else:
            self.loss = [s + (p-y)**2 for s, p in
                         zip(self.loss, self.forecasts(pattern))]
            age = self.n - WARMUP
            self.w[10:14] = fit_step(self.w[10:14], pair, y, age)
            self.w[14:] = fit_step(self.w[14:], compose, y, age)
        self.w[:10] = fit_step(self.w[:10], dense, y, self.n)
        self.n += 1
        self.ones += y
        if self.n == WARMUP:
            self.pair = max(range(36), key=lambda i: abs(self.corr[i]))

    def pack(self):
        return ROW.pack(self.n, self.ones, self.pair, *self.corr, *self.w, *self.loss)

    @classmethod
    def unpack(cls, raw):
        n, ones, pair, *v = ROW.unpack(raw)
        corr, w, loss = v[:36], v[36:61], v[61:]
        age = max(0, n-WARMUP)
        if (ones > n or any(abs(c) > min(n, WARMUP) for c in corr)
                or pair != (-1 if n < WARMUP else max(range(36), key=lambda i: abs(corr[i])))
                or any(not math.isfinite(x) or abs(x) > 32 for x in w)
                or any(not math.isfinite(x) or not 0 <= x <= age for x in loss)
                or (n <= WARMUP and any(w[10:]))
                or (n == 0 and any(w))):
            raise ValueError('invalid state')
        a = cls()
        a.n, a.ones, a.pair = n, ones, pair
        a.corr, a.w, a.loss = corr, w, loss
        return a


class AdaptiveContract:
    def __init__(self, public_keys=3):
        if type(public_keys) is not int or not 1 <= public_keys <= 16:
            raise ValueError('public key capacity')
        self.public_keys = public_keys
        self.cursor = 0
        self._rows = [[State() for _ in range(4)] for _ in range(public_keys)]

    def _check(self, key, pattern):
        if (type(key) is not int or not 0 <= key < self.public_keys
                or type(pattern) is not int or not 0 <= pattern < 512):
            raise ValueError('invalid observable key or pattern')

    def predict(self, key, pattern):
        if key is None:
            if type(pattern) is not int or not 0 <= pattern < 512:
                raise ValueError('invalid pattern')
            return None  # abstain; evaluator must charge abstention
        self._check(key, pattern)
        return tuple(a.forecasts(pattern)[a.choice()] for a in self._rows[key])

    def kinds(self, key):
        self._check(key, 0)
        return tuple(KINDS[a.choice()] for a in self._rows[key])

    def observe(self, sequence, key, pattern, outcomes):
        self._check(key, pattern)
        if type(sequence) is not int or sequence != self.cursor or sequence >= 2**64-1:
            raise ValueError('sequence mismatch or exhaustion')
        if (type(outcomes) is not tuple or len(outcomes) != 4 or
                any(type(y) is not int or y not in (0, 1) for y in outcomes)):
            raise ValueError('four jointly observed binary outcomes required')
        # Stage all four updates before committing. No partial event on failure.
        new = [State.unpack(a.pack()) for a in self._rows[key]]
        for a, y in zip(new, outcomes):
            a.update(pattern, y)
        self._rows[key] = new
        self.cursor += 1

    def checkpoint(self):
        payload = HEADER.pack(MAGIC, self.public_keys, self.cursor)
        payload += b''.join(a.pack() for rows in self._rows for a in rows)
        return payload + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not HEADER.size+32 <= len(raw) <= HEADER.size+16*4*ROW.size+32:
            raise ValueError('checkpoint envelope')
        payload, digest = raw[:-32], raw[-32:]
        if hashlib.sha256(payload).digest() != digest:
            raise ValueError('checkpoint digest')
        magic, keys, cursor = HEADER.unpack_from(payload)
        if magic != MAGIC or not 1 <= keys <= 16 or len(payload) != HEADER.size+keys*4*ROW.size:
            raise ValueError('checkpoint schema')
        model = cls(keys)
        for key in range(keys):
            for j in range(4):
                offset = HEADER.size+(key*4+j)*ROW.size
                model._rows[key][j] = State.unpack(payload[offset:offset+ROW.size])
            if len({a.n for a in model._rows[key]}) != 1:
                raise ValueError('joint exposure mismatch')
        if sum(rows[0].n for rows in model._rows) != cursor:
            raise ValueError('cursor/count inconsistency')
        model.cursor = cursor
        return model
