"""Gate28 public-evidence causal Bayesian diagnostic controls.

Finite 96-hypothesis/node *approximation*, not the exhaustive fully trained
Bayesian reference demanded by the frozen scientific protocol. Never use
these results for Gate28 scientific first-use or a superiority claim.
No hidden-world seed, causal graph, cohort label, or oracle outcome enters here.
"""
from __future__ import annotations

import hashlib
import json
import math
from itertools import combinations

import core

SCHEMA = "yggdrasil.gate28.causal-bayes-diagnostic.v1"
ARMS = ("causal_bayes_reward", "causal_bayes_eig")
K = 96
NOISE = 0.1
MAX_STATE_BYTES = core.MAX_STATE_BYTES
MAX_WORK = core.MAX_RULE_EVALS


def canon(x: object) -> bytes:
    return core.canonical(x)


def _bank(node: int) -> tuple[tuple[str, tuple[int, ...], int], ...]:
    if node not in range(7):
        raise ValueError("INVALID_CAUSAL_NODE")
    parents = range(8 + node) if node < 6 else range(8, 14)
    options: list[tuple[str, tuple[int, ...], int]] = []
    for pair in combinations(parents, 2):
        for kind in ("xor", "and", "or", "nand"):
            for flip in (0, 1):
                options.append((kind, pair, flip))
        if pair[0] < 8 and node < 6:
            for flip in (0, 1):
                options.append(("lag_xor", pair, flip))
    for triple in combinations(parents, 3):
        for kind in ("maj3", "compose"):
            for flip in (0, 1):
                options.append((kind, triple, flip))
    # Deterministic stratified subset of the entire frozen operator dictionary.
    # Source world seeds are never used to select the bank.
    options.sort(key=lambda x: (x[0], x[1], x[2]))
    indices = [i * len(options) // K for i in range(K)]
    result = tuple(options[i] for i in indices)
    assert len(result) == K and len(set(result)) == K
    return result


BANKS = tuple(_bank(i) for i in range(7))


def _eval(h: tuple, cells: list[int], previous: tuple[int, ...] | None,
          meter: core.Work) -> int | None:
    meter.charge()
    kind, ps, flip = h
    if kind == "lag_xor" and previous is None:
        return None
    vals = tuple((previous[p] if kind == "lag_xor" and k == 0
                  else cells[p]) for k, p in enumerate(ps))
    if kind == "xor":
        val = vals[0] ^ vals[1]
    elif kind == "and":
        val = vals[0] & vals[1]
    elif kind == "or":
        val = vals[0] | vals[1]
    elif kind == "nand":
        val = 1 ^ (vals[0] & vals[1])
    elif kind == "lag_xor":
        val = vals[0] ^ vals[1]
    elif kind == "maj3":
        val = int(sum(vals) >= 2)
    elif kind == "compose":
        val = (vals[0] ^ vals[1]) & vals[2]
    else:
        raise ValueError("UNKNOWN_OPERATOR")
    return val ^ flip


def new(arm: str) -> dict:
    if arm not in ARMS:
        raise ValueError("INVALID_BAYES_ARM")
    s = {"schema": SCHEMA, "arm": arm, "step": 0,
         "scores": [[0] * K for _ in range(7)], "source": None,
         "last_context": None, "edits": 0, "attempts": 0}
    _validate(s)
    return s


def _top(scores: list[int], n: int, meter: core.Work) -> list[tuple[int, float]]:
    meter.charge(K)
    ids = sorted(range(K), key=lambda i: (-scores[i], i))[:n]
    best = scores[ids[0]]
    raw = [math.exp(0.3 * (scores[i] - best)) for i in ids]
    normal = sum(raw)
    return [(i, weight / normal) for i, weight in zip(ids, raw)]


def _prepared(s: dict, meter: core.Work) -> list[list[tuple[int, float]]]:
    return [_top(scores, 1 if node < 6 else 24, meter)
            for node, scores in enumerate(s["scores"])]


def _predict(s: dict, context: tuple[int, ...], action: int,
             prepared: list, meter: core.Work) -> float:
    if type(action) is not int or not 0 <= action < 13:
        raise ValueError("INVALID_ACTION")
    cells = list(context)
    previous = None if s["last_context"] is None else tuple(s["last_context"])
    for node in range(6):
        if action < 12 and node == action // 2:
            bit = action % 2
        else:
            # MAP mediator hypothesis. This is a deliberately approximate
            # baseline: output uncertainty is integrated; mediator is not.
            index = prepared[node][0][0]
            bit = _eval(BANKS[node][index], cells, previous, meter)
            if bit is None:
                bit = 0
        cells.append(bit)
    probability = 0.0
    for index, posterior in prepared[6]:
        bit = _eval(BANKS[6][index], cells, previous, meter)
        probability += posterior * (0.9 if bit else 0.1)
    return min(0.9, max(0.1, probability))


def predict(s: dict, context: tuple[int, ...], action: int,
            meter: core.Work) -> float:
    core.as_mask(context)
    return _predict(s, context, action, _prepared(s, meter), meter)


def _entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log(p) - (1 - p) * math.log(1 - p)


def choose(s: dict, context: tuple[int, ...], meter: core.Work) -> int:
    core.as_mask(context)
    prepared = _prepared(s, meter)
    probabilities = [_predict(s, context, action, prepared, meter)
                     for action in range(13)]
    if s["arm"] == "causal_bayes_eig":
        # Information gained about outcome-rule identity under the
        # observed-context, mediator-MAP approximation.
        scores = [(_entropy(p) - _entropy(NOISE)) + 0.02 * p
                  for p in probabilities]
    else:
        scores = probabilities
    return max(range(13), key=lambda a: (scores[a], -a))


def observe(s: dict, context: tuple[int, ...], intermediates: tuple[int, ...],
            action: int, consequence: int, meter: core.Work) -> None:
    core.as_mask(context)
    if type(action) is not int or not 0 <= action < 13:
        raise ValueError("INVALID_ACTION")
    if len(intermediates) != 6 or any(type(v) is not int or v not in (0, 1)
                                      for v in intermediates):
        raise ValueError("INVALID_MEDIATOR_OBSERVATION")
    if type(consequence) is not int or consequence not in (0, 1):
        raise ValueError("INVALID_CONSEQUENCE")
    previous = None if s["last_context"] is None else tuple(s["last_context"])
    cells = list(context) + list(intermediates)
    for node in range(7):
        if node < 6 and action < 12 and action // 2 == node:
            # A do-intervention bypasses this node's generating mechanism.
            continue
        outcome = intermediates[node] if node < 6 else consequence
        for idx, rule in enumerate(BANKS[node]):
            value = _eval(rule, cells, previous, meter)
            if value is None:
                continue
            s["scores"][node][idx] = max(-48, min(48,
                s["scores"][node][idx] + (1 if value == outcome else -1)))
    s["step"] += 1
    s["last_context"] = list(context)
    if s["step"] % 8 == 0:
        for scores in s["scores"]:
            for i, score in enumerate(scores):
                meter.charge()
                scores[i] = round(score * 0.94)
    _validate(s)


def seal_source(s: dict) -> None:
    if s["step"] != 96 or s["source"] is not None:
        raise ValueError("SOURCE_FREEZE_REQUIRES_96_OBSERVATIONS")
    snap = {"scores": [list(x) for x in s["scores"]],
            "last_context": s["last_context"]}
    s["source"] = {"snapshot": snap,
                   "digest": hashlib.sha256(canon(snap)).hexdigest()}
    _validate(s)


def source_predict(s: dict, context: tuple[int, ...], action: int,
                   meter: core.Work) -> float:
    if s["source"] is None:
        raise ValueError("SOURCE_UNFROZEN")
    snap = s["source"]["snapshot"]
    frozen = {"scores": snap["scores"], "last_context": snap["last_context"]}
    return predict(frozen, context, action, meter)


def _validate(s: dict) -> None:
    if s.get("schema") != SCHEMA or s.get("arm") not in ARMS:
        raise ValueError("BAYES_SCHEMA")
    if type(s.get("step")) is not int or s["step"] < 0:
        raise ValueError("BAYES_STEP")
    if len(s.get("scores", [])) != 7:
        raise ValueError("BAYES_NODE_COUNT")
    for scores in s["scores"]:
        if len(scores) != K or any(type(n) is not int or not -48 <= n <= 48
                                   for n in scores):
            raise ValueError("BAYES_SCORE")
    prior = s.get("last_context")
    if prior is not None:
        core.as_mask(tuple(prior))
    if s.get("edits") != 0 or s.get("attempts") != 0:
        raise ValueError("BAYES_STRUCTURE_IMMUTABLE")
    source = s.get("source")
    if source is not None:
        snap = source["snapshot"]
        if len(snap["scores"]) != 7 or any(len(x) != K for x in snap["scores"]):
            raise ValueError("BAYES_SOURCE_SHAPE")
        if hashlib.sha256(canon(snap)).hexdigest() != source["digest"]:
            raise ValueError("BAYES_SOURCE_TAMPER")
    if len(canon(s)) > MAX_STATE_BYTES - 100:
        raise ValueError("BAYES_CAPACITY")


def pack(s: dict) -> bytes:
    _validate(s)
    payload = canon(s)
    raw = canon({"payload": s, "sha256": hashlib.sha256(payload).hexdigest()})
    if len(raw) > MAX_STATE_BYTES:
        raise ValueError("BAYES_CAPACITY")
    return raw


def unpack(raw: bytes) -> dict:
    if len(raw) > MAX_STATE_BYTES:
        raise ValueError("BAYES_CAPACITY")
    try:
        doc = json.loads(raw)
        if set(doc) != {"payload", "sha256"}:
            raise ValueError("BAYES_INVALID_CHECKPOINT")
        s = doc["payload"]
        if doc["sha256"] != hashlib.sha256(canon(s)).hexdigest():
            raise ValueError("BAYES_DIGEST")
        if canon(doc) != raw:
            raise ValueError("BAYES_NONCANONICAL")
        _validate(s)
        return s
    except (TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("BAYES_INVALID_CHECKPOINT") from exc
