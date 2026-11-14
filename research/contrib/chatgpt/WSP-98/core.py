"""WSP-98 frozen six-node source and no-gradient numeric writer.

No official Yggdrasil model/runtime integration. This module does not execute
public/reserved cohorts and exposes no per-world program to the learner.
"""
from __future__ import annotations

import hashlib
import json
import math
from itertools import combinations

N = 6
D = 22
RIDGE = 0.125
PASSIVE_ROWS = 24
ACTIONS = 8
GATES = ("AND", "OR", "XOR", "XNOR", "NAND", "NOR")
SCHEMA = "wsp98.numeric-direct-rls.v1"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def rank(world_id, purpose, index):
    data = f"WSP98|v1|{world_id}|{purpose}|{index}".encode("ascii")
    return int.from_bytes(hashlib.sha256(data).digest(), "big")


def state(bits):
    if not isinstance(bits, (tuple, list)) or len(bits) != N or any(type(b) is not int or b not in (0, 1) for b in bits):
        raise ValueError("six binary state values required")
    return tuple(bits)


def bits_of(value):
    return tuple((value >> i) & 1 for i in range(N))


def phi(bits):
    z = tuple(2 * b - 1 for b in state(bits))
    return (1.0,) + tuple(float(v) for v in z) + tuple(float(z[i] * z[j]) for i, j in combinations(range(N), 2))


def result_of(bits, program):
    x = state(bits)
    if not isinstance(program, tuple) or len(program) != N:
        raise ValueError("invalid evaluator-only causal program")
    output = []
    for p, q, inv_p, inv_q, gate in program:
        a, b = x[p] ^ inv_p, x[q] ^ inv_q
        if gate == "AND": y = a & b
        elif gate == "OR": y = a | b
        elif gate == "XOR": y = a ^ b
        elif gate == "XNOR": y = 1 ^ a ^ b
        elif gate == "NAND": y = 1 ^ (a & b)
        elif gate == "NOR": y = 1 ^ (a | b)
        else: raise ValueError("unknown gate")
        output.append(y)
    return tuple(output)


class World:
    """Evaluator oracle. Learners receive only observe()/do() results."""
    def __init__(self, world_id):
        if type(world_id) is not int or world_id < 0:
            raise ValueError("invalid world id")
        self.world_id = world_id
        clauses = []
        for i in range(N):
            # Independent, SHA-separated per-node program, no world-constant gate.
            r = rank(world_id, "PROGRAM", i)
            a = r % N
            b = (a + 1 + (r // N) % (N - 1)) % N
            flags = (r // (N * (N - 1))) % 4
            gate = GATES[(r // (N * (N - 1) * 4)) % len(GATES)]
            clauses.append((a, b, flags & 1, (flags >> 1) & 1, gate))
        self.__program = tuple(clauses)
        eligible = [bits_of(k) for k in range(64) if bits_of(k)[0] == bits_of(k)[1]]
        self._passive_x = tuple(sorted(eligible, key=lambda x: rank(world_id, "OBS", sum(b << j for j, b in enumerate(x))))[:PASSIVE_ROWS])
        self._action_receipts = {"active": [], "random": []}

    def passive(self):
        return tuple({"x": x, "y": result_of(x, self.__program)} for x in self._passive_x)

    def intervene(self, arm, trial, original_index, bit, forced):
        if arm not in self._action_receipts or type(trial) is not int or trial != len(self._action_receipts[arm]) or trial >= ACTIONS:
            raise ValueError("intervention replay or arm budget violation")
        if type(original_index) is not int or not 0 <= original_index < PASSIVE_ROWS or type(bit) is not int or not 0 <= bit < N or type(forced) is not int or forced not in (0, 1):
            raise ValueError("unregistered do query")
        original = self._passive_x[original_index]
        after = list(original)
        after[bit] = forced
        row = {"arm": arm, "trial": trial, "original_index": original_index, "bit": bit, "forced": forced,
               "x": tuple(after), "y": result_of(after, self.__program)}
        self._action_receipts[arm].append((original_index, bit, forced))
        return row

    def heldout(self):
        if any(len(v) != ACTIONS for v in self._action_receipts.values()):
            raise ValueError("heldout source cannot be selected until both arms complete")
        excluded = set(self._passive_x)
        for arm, trials in self._action_receipts.items():
            for orig, bit, forced in trials:
                x = list(self._passive_x[orig]); x[bit] = forced
                excluded.add(tuple(x))
        available = [bits_of(k) for k in range(64) if bits_of(k) not in excluded]
        targets = tuple(sorted(available, key=lambda x: rank(self.world_id, "EVAL", sum(b << j for j, b in enumerate(x))))[:20])
        if len(targets) != 20 or sum(x[0] != x[1] for x in targets) < 10:
            raise ValueError("INVALID original heldout cohort / causal-role target count")
        return targets

    def score_after_prediction_freeze(self, targets):
        return tuple(result_of(state(x), self.__program) for x in targets)


class DirectWeights:
    """616 numerical slots (132 coefficients + 484 shared inverse covariance)."""
    def __init__(self):
        self.w = [[0.0] * D for _ in range(N)]
        self.p = [[(1.0 / RIDGE if i == j else 0.0) for j in range(D)] for i in range(D)]
        self.count = 0
        self.source_digest = "0" * 64  # rolling SHA custody, no source replay buffer

    def observe(self, x, y, *, expected_index):
        if type(expected_index) is not int or expected_index != self.count or self.count >= PASSIVE_ROWS + ACTIONS:
            raise ValueError("missing, repeated or excessive source update")
        x, y = state(x), state(y)
        f = phi(x)
        pf = [sum(self.p[i][j] * f[j] for j in range(D)) for i in range(D)]
        denom = 1.0 + sum(f[i] * pf[i] for i in range(D))
        if not math.isfinite(denom) or denom <= 0:
            raise ValueError("invalid covariance")
        gain = [v / denom for v in pf]
        for k in range(N):
            error = (2 * y[k] - 1) - sum(self.w[k][j] * f[j] for j in range(D))
            for j in range(D):
                self.w[k][j] += gain[j] * error
        # The covariance update uses the OLD P for every row and column.
        fp = [sum(f[j] * self.p[j][i] for j in range(D)) for i in range(D)]
        for i in range(D):
            for j in range(D):
                self.p[i][j] -= gain[i] * fp[j]
        self.count += 1
        self.source_digest = digest({"prev": self.source_digest, "index": expected_index, "row": digest({"x": x, "y": y})})

    def leverage(self, x):
        f = phi(x)
        return sum(f[i] * self.p[i][j] * f[j] for i in range(D) for j in range(D))

    def choose(self, original_x, world_id, trial):
        if self.count != PASSIVE_ROWS + trial or type(trial) is not int or not 0 <= trial < ACTIONS:
            raise ValueError("action policy source/trial mismatch")
        ranked = []
        for original_index, base in enumerate(original_x):
            base = state(base)
            for bit in range(N):
                forced = 1 - base[bit]  # actual single-bit do; not a no-op
                query = list(base); query[bit] = forced
                leverage = self.leverage(query)
                tie = rank(world_id, "TIE", trial * (PASSIVE_ROWS * N) + original_index * N + bit)
                ranked.append((-leverage, tie, original_index, bit, forced))
        _, _, idx, bit, forced = min(ranked)
        return (idx, bit, forced)

    def predict(self, x):
        try:
            f = phi(x)
        except ValueError:
            return None
        if self.count != PASSIVE_ROWS + ACTIONS:
            return None
        return tuple(int(sum(w[j] * f[j] for j in range(D)) > 0) for w in self.w)

    def snapshot(self):
        data = {"w": self.w, "p": self.p, "count": self.count, "source_sha256": self.source_digest}
        return canonical({"schema": SCHEMA, "data": data, "checksum": digest(data)})

    @classmethod
    def restore(cls, text):
        doc = json.loads(text)
        data = doc.get("data")
        if doc.get("schema") != SCHEMA or not isinstance(data, dict) or set(data) != {"w", "p", "count", "source_sha256"} or doc.get("checksum") != digest(data):
            raise ValueError("invalid memory checksum")
        if type(data["count"]) is not int or not 0 <= data["count"] <= PASSIVE_ROWS + ACTIONS or not isinstance(data["source_sha256"], str) or len(data["source_sha256"]) != 64:
            raise ValueError("invalid memory provenance")
        if len(data["w"]) != N or any(len(r) != D for r in data["w"]) or len(data["p"]) != D or any(len(r) != D for r in data["p"]):
            raise ValueError("numeric capacity exceeded")
        if any(type(v) not in (float, int) or not math.isfinite(v) for rows in (data["w"], data["p"]) for r in rows for v in r):
            raise ValueError("nonfinite or nonnumeric memory")
        model = cls()
        model.w = data["w"]
        model.p = data["p"]
        model.count = data["count"]
        model.source_digest = data["source_sha256"]
        return model


def random_query(world_id, trial, passive_x):
    if type(trial) is not int or not 0 <= trial < ACTIONS or len(passive_x) != PASSIVE_ROWS:
        raise ValueError("invalid random do trial")
    # Frozen independent arm; no rejection even if the forced value is unchanged.
    return (rank(world_id, "RAND", trial * 3) % PASSIVE_ROWS,
            rank(world_id, "RAND", trial * 3 + 1) % N,
            rank(world_id, "RAND", trial * 3 + 2) % 2)
