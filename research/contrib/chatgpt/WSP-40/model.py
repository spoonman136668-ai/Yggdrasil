"""Finite-prior active causal discovery; generic numeric conjunction runtime."""
import hashlib
import itertools
import json
import math
import random


def masks(width):
    return tuple(sorted(sum(1 << i for i in c) for k in (1, 2, 3)
                        for c in itertools.combinations(range(width), k)))


def rotate(width, action, state):
    n = action + 1
    return ((state << n) | (state >> (width - n))) & ((1 << width) - 1)


class NumericModel:
    def __init__(self, width, supports):
        if type(width) is not int or width not in (4, 8, 16):
            raise ValueError("width")
        if type(supports) is not tuple or len(supports) != 2:
            raise ValueError("supports")
        if any(type(m) is not int or m < 0 or m >= 1 << width or m.bit_count() > 3 for m in supports):
            raise ValueError("support")
        self.width, self.supports = width, supports

    def apply(self, action, state):
        if type(action) is not int or action not in (0, 1) or type(state) is not int or not 0 <= state < 1 << self.width:
            raise ValueError("state/action")
        mask = self.supports[action]
        # A zero mask denotes no constructed residual, not constant one.
        residual = int(bool(mask) and (state & mask).bit_count() >= mask.bit_count())
        return rotate(self.width, action, state) ^ residual

    def rollout(self, state, actions):
        for a in actions:
            state = self.apply(a, state)
        return state

    def plan(self, start, goal):
        for actions in itertools.product(range(2), repeat=3):
            if self.rollout(start, actions) == goal:
                return actions
        return None

    def snapshot(self):
        body = json.dumps(["wsp40.numeric.v1", self.width, self.supports], separators=(",", ":")).encode()
        return body + b"|" + hashlib.sha256(body).hexdigest().encode()

    @classmethod
    def restore(cls, data):
        try:
            body, digest = data.rsplit(b"|", 1)
            if hashlib.sha256(body).hexdigest().encode() != digest:
                raise ValueError("digest")
            schema, width, supports = json.loads(body)
            if schema != "wsp40.numeric.v1":
                raise ValueError("schema")
            model = cls(width, tuple(supports))
            if model.snapshot() != data:
                raise ValueError("canonical")
            return model
        except (ValueError, TypeError, AttributeError):
            raise ValueError("checkpoint") from None


def acquire(width, probe, budget, policy, seed):
    """Only probe replies enter discovery; no hidden source/family argument."""
    if budget not in (4, 12) or policy not in ("active", "random", "singleton"):
        raise ValueError("policy/budget")
    rng = random.Random(seed)
    candidates0 = masks(width)
    transcript, supports, remaining = [], [], []
    full = (1 << width) - 1
    for action in range(2):
        candidates, seen = list(candidates0), set()
        for t in range(budget):
            available = [x for x in range(1 << width) if x not in seen] if width == 4 else None
            if policy == "singleton":
                pool = [1 << i for i in range(width)] + [0]
                query = next((x for x in pool if x not in seen), None)
                if query is None:
                    query = next(x for x in range(1 << width) if x not in seen)
            elif policy == "random":
                query = rng.randrange(1 << width)
                while query in seen:
                    query = rng.randrange(1 << width)
            else:
                pool = {full} | {full ^ (1 << i) for i in range(width)}
                for j in range(24):
                    density = (0.5, 0.75, 0.875)[j % 3]
                    pool.add(sum((rng.random() < density) << i for i in range(width)))
                pool -= seen
                if not pool:
                    pool = {next(x for x in (available or range(1 << width)) if x not in seen)}
                def balance(x):
                    count = sum((x & m) == m for m in candidates)
                    return abs(len(candidates) - 2 * count), x
                query = min(pool, key=balance)
            answer = probe(action, query)
            if type(answer) is not int or not 0 <= answer < 1 << width:
                raise ValueError("oracle")
            residual = answer ^ rotate(width, action, query)
            if residual not in (0, 1):
                raise ValueError("non-scalar residual")
            transcript.append((action, query, residual))
            seen.add(query)
            candidates = [m for m in candidates if int((query & m) == m) == residual]
        supports.append(min(candidates) if candidates else 0)
        remaining.append(len(candidates))
    return NumericModel(width, tuple(supports)), tuple(transcript), tuple(remaining)


class IndependentIdentifier(NumericModel):
    """Set-based independent reconstruction from the exact captured transcript."""
    def __init__(self, width, transcript):
        selected = []
        for action in range(2):
            hypotheses = []
            for k in (1, 2, 3):
                for indices in itertools.combinations(range(width), k):
                    if all(int(all((x >> i) & 1 for i in indices)) == y
                           for a, x, y in transcript if a == action):
                        hypotheses.append(sum(1 << i for i in indices))
            selected.append(min(hypotheses) if hypotheses else 0)
        super().__init__(width, tuple(selected))


class FittedRegression:
    """Fully fitted minimum-norm linear monomial head, no early stopping."""
    def __init__(self, width, transcript):
        self.width = width
        self.features = (0,) + masks(width)
        self.weights = []
        self.train_errors = []
        self.train_max_residual = []
        for action in range(2):
            # Orthogonalize constraints, accumulating minimum-norm exact fit.
            basis, targets = [], []
            for a, x, y in transcript:
                if a != action:
                    continue
                row = [float((x & m) == m) for m in self.features]
                target = float(y)
                for _ in range(2):
                    for q, z in zip(basis, targets):
                        dot = sum(u * v for u, v in zip(row, q))
                        row = [u - dot * v for u, v in zip(row, q)]
                        target -= dot * z
                norm = math.sqrt(sum(v * v for v in row))
                if norm > 1e-10:
                    basis.append([v / norm for v in row])
                    targets.append(target / norm)
                elif abs(target) > 1e-8:
                    # Misspecified feature dictionary; retain and report failure.
                    pass
            weights = [sum(q[i] * z for q, z in zip(basis, targets)) for i in range(len(self.features))]
            self.weights.append(weights)
            errors = [abs(sum(w for m, w in zip(self.features, weights) if (x & m) == m) - y)
                      for a, x, y in transcript if a == action]
            self.train_errors.append(sum(e > 1e-8 for e in errors))
            self.train_max_residual.append(max(errors, default=0))

    def apply(self, action, state):
        score = sum(w for m, w in zip(self.features, self.weights[action]) if (state & m) == m)
        return rotate(self.width, action, state) ^ int(score >= 0.5)

    rollout = NumericModel.rollout
    plan = NumericModel.plan
