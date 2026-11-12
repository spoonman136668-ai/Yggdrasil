"""Grow conjunction features from real counterexamples; no degree enumeration."""
import hashlib
import itertools
import json
import math
import random


def rotate(width, action, state):
    n = action + 1
    return ((state << n) | (state >> (width - n))) & ((1 << width) - 1)


class NumericModel:
    def __init__(self, width, terms):
        if type(width) is not int or width not in (8, 12, 16):
            raise ValueError("width")
        if type(terms) is not tuple or len(terms) != 2:
            raise ValueError("terms")
        for group in terms:
            if type(group) is not tuple or len(group) > 32 or tuple(sorted(set(group))) != group:
                raise ValueError("canonical terms")
            if any(type(m) is not int or m < 0 or m >= 1 << width for m in group):
                raise ValueError("term")
        self.width, self.terms = width, terms

    def residual(self, action, state):
        out = 0
        for mask in self.terms[action]:
            # Homogeneous binary weighted threshold neuron, including constant.
            out ^= int((state & mask).bit_count() >= mask.bit_count())
        return out

    def apply(self, action, state):
        if type(action) is not int or action not in (0, 1) or type(state) is not int or not 0 <= state < 1 << self.width:
            raise ValueError("action/state")
        return rotate(self.width, action, state) ^ self.residual(action, state)

    def rollout(self, state, actions):
        for action in actions: state = self.apply(action, state)
        return state

    def plan(self, start, goal):
        for actions in itertools.product(range(2), repeat=3):
            if self.rollout(start, actions) == goal: return actions
        return None

    def snapshot(self):
        body = json.dumps(["wsp41.grown.v1", self.width, self.terms], separators=(",", ":")).encode()
        return body + b"|" + hashlib.sha256(body).hexdigest().encode()

    @classmethod
    def restore(cls, data):
        try:
            body, digest = data.rsplit(b"|", 1)
            if hashlib.sha256(body).hexdigest().encode() != digest: raise ValueError("digest")
            schema, width, groups = json.loads(body)
            if schema != "wsp41.grown.v1": raise ValueError("schema")
            model = cls(width, tuple(tuple(g) for g in groups))
            if model.snapshot() != data: raise ValueError("canonical")
            return model
        except (ValueError, TypeError, AttributeError):
            raise ValueError("checkpoint") from None


def acquire(width, probe, budget):
    if budget not in (64, 128): raise ValueError("budget")
    groups, transcripts, stats = [], [], []
    rng = random.Random(977 + width)
    for action in range(2):
        cache, terms = {}, set()
        updates, reads, draws = 0, 0, 0
        reason = "query_budget"
        def query(state):
            nonlocal reads
            reads += 1
            if state not in cache:
                if len(cache) >= budget: raise StopIteration
                answer = probe(action, state)
                if type(answer) is not int or not 0 <= answer < 1 << width: raise ValueError("oracle")
                residual = answer ^ rotate(width, action, state)
                if residual not in (0, 1): raise ValueError("non-scalar")
                cache[state] = residual
            return cache[state]
        def prediction(state):
            out = 0
            for mask in terms: out ^= int((state & mask) == mask)
            return out
        while len(cache) < budget and updates < 512:
            witness = next((x for x, y in cache.items() if y != prediction(x)), None)
            if witness is None:
                if not cache:
                    witness = (1 << width) - 1
                else:
                    while True:
                        density = (0.5, 0.75, 0.875)[draws % 3]
                        draws += 1
                        witness = sum((rng.random() < density) << i for i in range(width))
                        if witness not in cache: break
                if query(witness) == prediction(witness): continue
            try:
                for bit in range(width):
                    if witness & (1 << bit):
                        smaller = witness ^ (1 << bit)
                        if query(smaller) != prediction(smaller): witness = smaller
            except StopIteration:
                reason = "budget_during_minimization"
                break
            if witness in terms:
                terms.remove(witness)
            elif len(terms) == 32:
                reason = "capacity"
                break
            else:
                terms.add(witness)
            updates += 1
        if updates == 512: reason = "update_budget"
        groups.append(tuple(sorted(terms)))
        transcripts.extend((action, x, y) for x, y in cache.items())
        stats.append({"queries": len(cache), "cache_reads": reads, "updates": updates,
                      "terms": len(terms), "degrees": sorted(m.bit_count() for m in terms),
                      "cached_errors": sum(y != prediction(x) for x, y in cache.items()), "stop": reason})
    return NumericModel(width, tuple(groups)), tuple(transcripts), stats


def random_transcript(width, probe, budgets):
    rng = random.Random(1777 + width)
    rows = []
    for action, budget in enumerate(budgets):
        for state in rng.sample(range(1 << width), budget):
            rows.append((action, state, probe(action, state) ^ rotate(width, action, state)))
    return tuple(rows)


class SymbolicExecution:
    """Independent execution parity only; supplied learned supports, no new fit."""
    def __init__(self, model):
        self.width = model.width
        self.groups = tuple(tuple(tuple(i for i in range(model.width) if m >> i & 1) for m in g) for g in model.terms)

    def apply(self, action, state):
        return rotate(self.width, action, state) ^ (sum(all(state >> i & 1 for i in indices) for indices in self.groups[action]) % 2)

    rollout = NumericModel.rollout
    plan = NumericModel.plan


class KernelRegression:
    """Closed-form conventional RBF interpolation, every actual observation used."""
    def __init__(self, width, transcript):
        self.width, self.centers, self.alphas, self.max_errors = width, [], [], []
        for action in range(2):
            rows = [(x, float(y)) for a, x, y in transcript if a == action]
            xs, ys = zip(*rows)
            n = len(xs)
            matrix = [[2.0 ** (-(x ^ z).bit_count()) for z in xs] for x in xs]
            lower = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1):
                    value = matrix[i][j] - sum(lower[i][k] * lower[j][k] for k in range(j))
                    if i == j:
                        if value <= 1e-12: raise ValueError("kernel not positive definite")
                        lower[i][j] = math.sqrt(value)
                    else:
                        lower[i][j] = value / lower[j][j]
            forward = []
            for i in range(n):
                forward.append((ys[i] - sum(lower[i][k] * forward[k] for k in range(i))) / lower[i][i])
            alpha = [0.0] * n
            for i in range(n - 1, -1, -1):
                alpha[i] = (forward[i] - sum(lower[k][i] * alpha[k] for k in range(i+1, n))) / lower[i][i]
            self.centers.append(xs)
            self.alphas.append(alpha)
            self.max_errors.append(max(abs(sum(v * a for v, a in zip(row, alpha)) - y) for row, y in zip(matrix, ys)))

    def apply(self, action, state):
        score = sum(a * 2.0 ** (-(state ^ x).bit_count()) for x, a in zip(self.centers[action], self.alphas[action]))
        return rotate(self.width, action, state) ^ int(round(score, 12) >= 0.5)

    rollout = NumericModel.rollout
    plan = NumericModel.plan
