"""Gate 28 deterministic bounded local topology learners (development only).

No primary seeds, private causal labels or held consequences enter this module.
These learners are *candidate research arms*, NOT a causal Bayesian benchmark,
validated adaptive gain, native Yggdrasil training, or deployment mechanism.
"""
from __future__ import annotations

import hashlib
import json
import math
from itertools import combinations

SCHEMA = "yggdrasil.gate28.local-structure.v1"
ARMS = ("adaptive", "fixed", "random_rewire", "surprise_rewire", "no_memory")
N_ACTIONS = 13
MAX_CELLS = 16
MAX_EDGES = 64
MAX_STATE_BYTES = 16384
MAX_RULE_EVALS = 8192
RECENT_LIMIT = 48
EDGE_LOG_LIMIT = 24
FEATURES = (("bit", (i,)) for i in range(8))
FEATURES = tuple(FEATURES) + tuple(
    (kind, pair) for kind in ("xor", "and", "or") for pair in combinations(range(8), 2)
) + tuple(("majority", triple) for triple in combinations(range(8), 3))
assert len(FEATURES) == 8 + 3 * 28 + 56 == 148


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False).encode("ascii"))


def _pick(seed: int, domain: str, *parts: object) -> int:
    data = ("g28-local-v1|" + str(seed) + "|" + domain + "|" +
            "|".join(str(x) for x in parts)).encode("ascii")
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


class Work:
    """Evaluator passes one meter across prediction, action and one observation."""

    def __init__(self) -> None:
        self.count = 0

    def charge(self, n: int = 1) -> None:
        if n < 0:
            raise ValueError("NEGATIVE_WORK")
        self.count += n
        if self.count > MAX_RULE_EVALS:
            raise ValueError("RULE_BUDGET_EXCEEDED")


def feature(index: int, context: tuple[int, ...], work: Work) -> int:
    if not 0 <= index < len(FEATURES) or len(context) != 8 or any(
            bit not in (0, 1) for bit in context):
        raise ValueError("INVALID_FEATURE_INPUT")
    work.charge()
    kind, parents = FEATURES[index]
    bits = [context[i] for i in parents]
    if kind == "bit":
        return bits[0]
    if kind == "xor":
        return bits[0] ^ bits[1]
    if kind == "and":
        return bits[0] & bits[1]
    if kind == "or":
        return bits[0] | bits[1]
    return int(sum(bits) >= 2)


def as_bits(mask: int) -> tuple[int, ...]:
    if type(mask) is not int or not 0 <= mask <= 255:
        raise ValueError("INVALID_CONTEXT_MASK")
    return tuple((mask >> i) & 1 for i in range(8))


def as_mask(context: tuple[int, ...]) -> int:
    if len(context) != 8 or any(type(bit) is not int or bit not in (0, 1)
                                for bit in context):
        raise ValueError("INVALID_CONTEXT")
    return sum(bit << i for i, bit in enumerate(context))


def new(seed: int, arm: str) -> dict:
    if arm not in ARMS or type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("INVALID_ARM_OR_SEED")
    s = {"schema": SCHEMA, "seed": seed, "arm": arm, "counts": [0] * N_ACTIONS,
         "bias": [0.0] * N_ACTIONS, "edges": [], "recent": [], "step": 0,
         "source": None, "attempts": 0, "edits": 0, "edit_log": []}
    if arm == "fixed":
        # Fixed, *fully trained* topology: 64 deterministic slots, equal ceiling
        # to the mutable arm. Selection is independent of all observations.
        for k in range(MAX_EDGES):
            action = k % N_ACTIONS
            f = _pick(seed, "fixed-slot", action, k // N_ACTIONS) % len(FEATURES)
            while any(e[0] == action and e[1] == f for e in s["edges"]):
                f = (f + 1) % len(FEATURES)
            s["edges"].append([action, f, 0.0])
    _validate(s)
    return s


def _sigmoid(logit: float) -> float:
    z = max(-8.0, min(8.0, logit))
    return 1.0 / (1.0 + math.exp(-z))


def predict(s: dict, context: tuple[int, ...], action: int,
            work: Work) -> float:
    if type(action) is not int or not 0 <= action < N_ACTIONS:
        raise ValueError("INVALID_ACTION")
    as_mask(context)
    work.charge()
    z = s["bias"][action]
    for a, f, weight in s["edges"]:
        if a == action:
            z += weight * (2 * feature(f, context, work) - 1)
    return _sigmoid(z)


def choose(s: dict, context: tuple[int, ...], work: Work) -> int:
    """Deterministic optimistic policy using learned outcome probabilities.

    No hidden family/phase labels or oracle rewards are permitted here.
    """
    estimates = [predict(s, context, a, work) for a in range(N_ACTIONS)]
    # Predeclared exploration term; adds no interventions to the budget.
    scores = [p + 0.12 / math.sqrt(1 + s["counts"][a])
              for a, p in enumerate(estimates)]
    return max(range(N_ACTIONS), key=lambda a: (scores[a], -a))


def _candidate_score(candidate: int, rows: list, work: Work) -> float:
    # Centered residual-feature correlation; computed ONLY on public action
    # consequences already seen by this arm, not hidden counterfactuals.
    pairs = []
    for mask, residual in rows:
        x = as_bits(mask)
        f = feature(candidate, x, work)
        pairs.append((f, residual))
    if len(pairs) < 5:
        return 0.0
    mean_f = sum(x for x, _ in pairs) / len(pairs)
    mean_r = sum(r for _, r in pairs) / len(pairs)
    if mean_f in (0.0, 1.0):
        return 0.0
    return abs(sum((x - mean_f) * (r - mean_r) for x, r in pairs) / len(pairs))


def _edit(s: dict, action: int, feature_id: int, reason: str,
          score: float) -> None:
    edges = s["edges"]
    if any(a == action and f == feature_id for a, f, _ in edges):
        return
    if len(edges) < MAX_EDGES:
        operation = "spawn"
        edges.append([action, feature_id, 0.0])
    else:
        # A change to an existing edge only; never expand allocation.
        candidate = min(range(len(edges)),
                        key=lambda i: (abs(edges[i][2]), i))
        operation = "rewire"
        edges[candidate] = [action, feature_id, 0.0]
    s["edits"] += 1
    s["edit_log"].append([s["step"], operation, action, feature_id,
                          reason, round(score, 6)])
    s["edit_log"] = s["edit_log"][-EDGE_LOG_LIMIT:]


def _maybe_rewire(s: dict, action: int, surprise: float,
                  work: Work) -> None:
    arm = s["arm"]
    if arm in ("fixed", "no_memory") or s["counts"][action] < 8 or (
            s["counts"][action] % 4):
        return
    s["attempts"] += 1
    active = {f for a, f, _ in s["edges"] if a == action}
    if arm == "random_rewire":
        candidate = _pick(s["seed"], "random", s["step"], action) % len(FEATURES)
        if candidate not in active:
            _edit(s, action, candidate, "random_control", 0.0)
        return
    if arm == "surprise_rewire":
        if surprise < 0.45:
            return
        candidate = _pick(s["seed"], "surprise", s["step"], action) % len(FEATURES)
        if candidate not in active:
            _edit(s, action, candidate, "surprise_only", round(surprise, 6))
        return
    # Adaptive: proposals are discriminated by residual explanatory value.
    # Evaluate a bounded *fixed* candidate dictionary; only recent public
    # observations are in scope. No true-parent information is used.
    rows = [(mask, y - predict(s, as_bits(mask), action, work))
            for mask, a, y in s["recent"] if a == action]
    best = (-1.0, -1)
    for i in range(len(FEATURES)):
        if i in active:
            continue
        score = _candidate_score(i, rows, work)
        if score > best[0]:
            best = (score, i)
    if best[0] >= 0.11:
        _edit(s, action, best[1], "public_residual_value", best[0])


def observe(s: dict, context: tuple[int, ...], action: int,
            consequence: int, work: Work) -> None:
    if consequence not in (0, 1) or type(consequence) is not int:
        raise ValueError("INVALID_CONSEQUENCE")
    mask = as_mask(context)
    if s["arm"] == "no_memory":
        s["step"] += 1
        return
    p = predict(s, context, action, work)
    n = s["counts"][action]
    eta = 0.4 / math.sqrt(1 + n / 8)
    residual = consequence - p
    s["bias"][action] = round(max(-6.0, min(6.0,
                                   s["bias"][action] + eta * residual)), 9)
    for e in s["edges"]:
        if e[0] == action:
            sign = 2 * feature(e[1], context, work) - 1
            e[2] = round(max(-6.0, min(6.0, e[2] + eta * sign * residual)), 9)
    s["counts"][action] += 1
    s["step"] += 1
    s["recent"].append([mask, action, consequence])
    s["recent"] = s["recent"][-RECENT_LIMIT:]
    _maybe_rewire(s, action, abs(residual), work)
    _validate(s)


def seal_source(s: dict) -> None:
    if s["source"] is not None or s["step"] != 96:
        raise ValueError("SOURCE_FREEZE_REQUIRES_96_OBSERVATIONS")
    copy = {"counts": list(s["counts"]), "bias": list(s["bias"]),
            "edges": [list(e) for e in s["edges"]]}
    s["source"] = {"snapshot": copy,
                   "digest": hashlib.sha256(canonical(copy)).hexdigest()}
    _validate(s)


def source_predict(s: dict, context: tuple[int, ...], action: int,
                   work: Work) -> float:
    if s["source"] is None:
        raise ValueError("SOURCE_UNFROZEN")
    source = s["source"]["snapshot"]
    return predict(source, context, action, work)


def _validate(s: dict) -> None:
    if s.get("schema") != SCHEMA or s.get("arm") not in ARMS:
        raise ValueError("INVALID_MODEL_SCHEMA")
    if type(s.get("seed")) is not int or not 0 <= s["seed"] < 2**32:
        raise ValueError("INVALID_SEED")
    if type(s.get("step")) is not int or s["step"] < 0:
        raise ValueError("INVALID_STEP")
    if len(s["counts"]) != N_ACTIONS or any(type(n) is not int or n < 0
                                             for n in s["counts"]):
        raise ValueError("INVALID_COUNTS")
    if len(s["bias"]) != N_ACTIONS or any(type(n) not in (float, int) or
                                           not math.isfinite(n) or abs(n) > 6
                                           for n in s["bias"]):
        raise ValueError("INVALID_BIAS")
    if len(s["edges"]) > MAX_EDGES or len(s["recent"]) > RECENT_LIMIT or len(
            s["edit_log"]) > EDGE_LOG_LIMIT:
        raise ValueError("STRUCTURE_CAP_EXCEEDED")
    if len({(a, f) for a, f, _ in s["edges"]}) != len(s["edges"]):
        raise ValueError("DUPLICATE_EDGE")
    for a, f, weight in s["edges"]:
        if type(a) is not int or not 0 <= a < N_ACTIONS or type(f) is not int or not 0 <= f < len(FEATURES) or (
                type(weight) not in (float, int) or not math.isfinite(weight) or abs(weight) > 6):
            raise ValueError("INVALID_EDGE")
    for x, a, y in s["recent"]:
        if type(x) is not int or not 0 <= x <= 255 or type(a) is not int or not 0 <= a < N_ACTIONS or type(y) is not int or y not in (0, 1):
            raise ValueError("INVALID_RECENT_EXPOSURE")
    if s["source"] is not None:
        source = s["source"]
        if hashlib.sha256(canonical(source["snapshot"])).hexdigest() != source["digest"]:
            raise ValueError("SOURCE_ARCHIVE_MODIFIED")
        if len(source["snapshot"]["edges"]) > MAX_EDGES:
            raise ValueError("INVALID_SOURCE_SIZE")
    if len(canonical(s)) > MAX_STATE_BYTES - 110:
        raise ValueError("CHECKPOINT_MEMORY_BUDGET_EXCEEDED")


def pack(s: dict) -> bytes:
    _validate(s)
    payload = canonical(s)
    result = canonical({"payload": s, "sha256": hashlib.sha256(payload).hexdigest()})
    if len(result) > MAX_STATE_BYTES:
        raise ValueError("CHECKPOINT_MEMORY_BUDGET_EXCEEDED")
    return result


def unpack(raw: bytes) -> dict:
    if len(raw) > MAX_STATE_BYTES:
        raise ValueError("CHECKPOINT_TOO_LARGE")
    try:
        doc = json.loads(raw)
        s = doc["payload"]
        if set(doc) != {"payload", "sha256"} or not isinstance(s, dict):
            raise ValueError("CHECKPOINT_FORMAT")
        if doc["sha256"] != hashlib.sha256(canonical(s)).hexdigest():
            raise ValueError("CHECKPOINT_DIGEST_MISMATCH")
        if canonical(doc) != raw:
            raise ValueError("CHECKPOINT_NONCANONICAL")
        _validate(s)
    except (KeyError, TypeError, UnicodeError, json.JSONDecodeError) as err:
        raise ValueError("INVALID_CHECKPOINT") from err
    return s


def diagnostic() -> dict:
    # No reserved Gate28 scientific seeds consumed.
    for arm in ARMS:
        s = new(900012, arm)
        for t in range(96):
            x = as_bits((t * 37) % 256)
            observe(s, x, t % N_ACTIONS, ((t // 7) ^ x[0]) & 1, Work())
        seal_source(s)
        src = s["source"]["digest"]
        cold = unpack(pack(s))
        assert cold["source"]["digest"] == src
        for t in range(24):
            x = as_bits((t * 11) % 256)
            a = choose(cold, x, Work())
            observe(cold, x, a, x[0] ^ x[1], Work())
        assert cold["source"]["digest"] == src
        assert len(cold["edges"]) <= 64
        assert len(pack(cold)) <= 16384
    return {"status": "G28_CORE_DIAGNOSTIC_PASS", "arms": len(ARMS),
            "reserved_primary_used": False, "model_scientific_gain": "UNVERIFIED"}


if __name__ == "__main__":
    print(json.dumps(diagnostic(), sort_keys=True))
