"""Gate28 fully *fitted* complete-grammar causal reference (secondary upper bound).

This reference evaluates every canonical node-specific hypothesis against each
public observation. It is an intentionally UNCONSTRAINED conventional baseline,
NOT a compute/memory-matched arm. In particular full-grammar fitting generally
exceeds 8192 primitive evaluations per observation and a 16 KiB checkpoint.
Do not use it to qualify Gate28 primary first-use or claim scientific gain.
Private world seeds, hidden families, true graphs, and held outcomes are absent.
"""
from __future__ import annotations

import hashlib
import json
import math

import core
import grammar

SCHEMA = "yggdrasil.gate28.full-grammar-reference.v1"
ARMS = ("full_reference_reward", "full_reference_eig")
BANKS = tuple(tuple(sorted(bank)) for bank in grammar.FULL_BANKS)
BANK_SIZES = tuple(map(len, BANKS))
TOTAL_HYPOTHESES = sum(BANK_SIZES)
assert TOTAL_HYPOTHESES == 11424
LOG_ODDS = math.log(9.0)
OUTCOME_FLIP = 0.1
TOP_K = 24
DIAGNOSTIC_ONLY = True


class Meter:
    """Full primitive evaluation receipt; deliberately no matched work cap."""

    def __init__(self) -> None:
        self.evaluations = 0

    def charge(self, count: int = 1) -> None:
        if count < 0:
            raise ValueError("NEGATIVE_WORK")
        self.evaluations += count


def _validate_bits(context: tuple[int, ...],
                   intermediate: tuple[int, ...] | None = None) -> None:
    core.as_mask(context)
    if intermediate is not None and (len(intermediate) != 6 or
                                     any(type(x) is not int or x not in (0, 1)
                                         for x in intermediate)):
        raise ValueError("INVALID_PUBLIC_MEDIATORS")


def _rule(rule: tuple, cells: list[int],
          previous: tuple[int, ...] | None, work: Meter) -> int | None:
    """Independently implement world operators, including lag's p % 8.

    A lag rule with first parent >=8 still reads the exogenous previous
    context, as the world generator does. No private world code is imported.
    """
    work.charge()
    kind, parents, invert = rule
    if kind == "lag_xor" and previous is None:
        return None
    values = [
        previous[p % 8] if kind == "lag_xor" and i == 0 else cells[p]
        for i, p in enumerate(parents)
    ]
    if kind in ("xor", "lag_xor"):
        val = values[0] ^ values[1]
    elif kind == "and":
        val = values[0] & values[1]
    elif kind == "or":
        val = values[0] | values[1]
    elif kind == "nand":
        val = 1 ^ (values[0] & values[1])
    elif kind == "maj3":
        val = int(sum(values) >= 2)
    elif kind == "compose":
        val = (values[0] ^ values[1]) & values[2]
    else:
        raise ValueError("UNKNOWN_CAUSAL_OPERATOR")
    return val ^ invert


def new(arm: str) -> dict:
    if arm not in ARMS:
        raise ValueError("INVALID_FULL_REFERENCE_ARM")
    state = {"schema": SCHEMA, "arm": arm, "step": 0,
             "scores": [[0] * n for n in BANK_SIZES],
             "last_context": None, "source": None,
             "total_fit_evaluations": 0,
             "peak_fit_evaluations": 0}
    validate(state)
    return state


def _posterior(scores: list[int], count: int) -> list[tuple[int, float]]:
    # Softmax(log likelihood) from symmetric +1/-1 Bernoulli evidence.
    ids = sorted(range(len(scores)), key=lambda i: (-scores[i], i))[:count]
    best = scores[ids[0]]
    weights = [math.exp((score - best) * LOG_ODDS / 2)
               for score in (scores[i] for i in ids)]
    z = sum(weights)
    return [(i, x / z) for i, x in zip(ids, weights)]


def _prepared(s: dict) -> list[list[tuple[int, float]]]:
    return [_posterior(scores, 1 if node < 6 else TOP_K)
            for node, scores in enumerate(s["scores"])]


def _estimate(s: dict, context: tuple[int, ...], action: int,
              prep: list[list[tuple[int, float]]], work: Meter) -> tuple[float, float]:
    if type(action) is not int or not 0 <= action < 13:
        raise ValueError("INVALID_ACTION")
    cells = list(context)
    prev = None if s["last_context"] is None else tuple(s["last_context"])
    for node in range(6):
        if action < 12 and action // 2 == node:
            bit = action % 2
        else:
            bit = _rule(BANKS[node][prep[node][0][0]], cells, prev, work)
            if bit is None:
                bit = 0
        cells.append(bit)
    p = 0.0
    uncertainty = 0.0
    for index, weight in prep[6]:
        out = _rule(BANKS[6][index], cells, prev, work)
        prob = OUTCOME_FLIP if out == 0 else 1 - OUTCOME_FLIP
        p += weight * prob
        uncertainty += weight * (1.0 if out else 0.0)
    return p, uncertainty


def predict(s: dict, context: tuple[int, ...], action: int,
            work: Meter) -> float:
    _validate_bits(context)
    return _estimate(s, context, action, _prepared(s), work)[0]


def choose(s: dict, context: tuple[int, ...], work: Meter) -> int:
    _validate_bits(context)
    prep = _prepared(s)
    vals = [_estimate(s, context, action, prep, work)
            for action in range(13)]
    if s["arm"] == "full_reference_eig":
        # Outcome-rule EIG approximation conditional on MAP mediators.
        # EIG = H(predictive) - E_model[H(known-noise Bernoulli)].
        h0 = -OUTCOME_FLIP * math.log(OUTCOME_FLIP) - (
            1 - OUTCOME_FLIP) * math.log(1 - OUTCOME_FLIP)
        scores = [(-p * math.log(p) - (1 - p) * math.log(1 - p) - h0)
                  + 0.02 * p for p, _ in vals]
    else:
        scores = [p for p, _ in vals]
    return max(range(13), key=lambda i: (scores[i], -i))


def observe(s: dict, context: tuple[int, ...],
            intermediates: tuple[int, ...], action: int,
            consequence: int, work: Meter) -> None:
    _validate_bits(context, intermediates)
    if type(action) is not int or not 0 <= action < 13:
        raise ValueError("INVALID_ACTION")
    if type(consequence) is not int or consequence not in (0, 1):
        raise ValueError("INVALID_CONSEQUENCE")
    previous = (None if s["last_context"] is None else
                tuple(s["last_context"]))
    cells = list(context) + list(intermediates)
    start = work.evaluations
    for node, bank in enumerate(BANKS):
        if node < 6 and action < 12 and action // 2 == node:
            # Intervention sets the mediator directly. Do not fit its rule.
            continue
        observed = intermediates[node] if node < 6 else consequence
        scores = s["scores"][node]
        for index, rule in enumerate(bank):
            pred = _rule(rule, cells, previous, work)
            if pred is not None:
                scores[index] += 1 if pred == observed else -1
    used = work.evaluations - start
    s["peak_fit_evaluations"] = max(s["peak_fit_evaluations"], used)
    s["total_fit_evaluations"] += used
    s["step"] += 1
    s["last_context"] = list(context)
    validate(s)


def seal_source(s: dict) -> None:
    if s["step"] != 96 or s["source"] is not None:
        raise ValueError("SOURCE_FREEZE_REQUIRES_96_OBSERVATIONS")
    frozen = {"scores": [list(x) for x in s["scores"]],
              "last_context": s["last_context"]}
    s["source"] = {"snapshot": frozen,
                   "digest": hashlib.sha256(core.canonical(frozen)).hexdigest()}
    validate(s)


def source_predict(s: dict, context: tuple[int, ...],
                   action: int, work: Meter) -> float:
    if s["source"] is None:
        raise ValueError("SOURCE_UNFROZEN")
    return predict(s["source"]["snapshot"], context, action, work)


def validate(s: dict) -> None:
    if s.get("schema") != SCHEMA or s.get("arm") not in ARMS:
        raise ValueError("FULL_REFERENCE_SCHEMA")
    if type(s.get("step")) is not int or s["step"] < 0:
        raise ValueError("FULL_REFERENCE_STEP")
    if len(s.get("scores", [])) != 7:
        raise ValueError("FULL_REFERENCE_NODE_COUNT")
    for node, scores in enumerate(s["scores"]):
        if len(scores) != BANK_SIZES[node] or any(
                type(n) is not int or abs(n) > s["step"] for n in scores):
            raise ValueError("FULL_REFERENCE_SCORE_RANGE")
    if s.get("last_context") is not None:
        _validate_bits(tuple(s["last_context"]))
    if any(type(s.get(k)) is not int or s[k] < 0
           for k in ("total_fit_evaluations", "peak_fit_evaluations")):
        raise ValueError("FULL_REFERENCE_WORK_RECEIPT")
    frozen = s.get("source")
    if frozen is not None:
        snap = frozen["snapshot"]
        if len(snap["scores"]) != 7 or any(
                len(scores) != BANK_SIZES[i]
                for i, scores in enumerate(snap["scores"])):
            raise ValueError("FULL_REFERENCE_SOURCE_SHAPE")
        if hashlib.sha256(core.canonical(snap)).hexdigest() != frozen["digest"]:
            raise ValueError("FULL_REFERENCE_SOURCE_TAMPER")


def pack(s: dict) -> bytes:
    validate(s)
    raw = core.canonical(s)
    return core.canonical({"payload": s,
                           "sha256": hashlib.sha256(raw).hexdigest()})


def unpack(raw: bytes) -> dict:
    try:
        obj = json.loads(raw)
        if set(obj) != {"payload", "sha256"}:
            raise ValueError("FULL_REFERENCE_FORMAT")
        s = obj["payload"]
        if hashlib.sha256(core.canonical(s)).hexdigest() != obj["sha256"]:
            raise ValueError("FULL_REFERENCE_DIGEST")
        if core.canonical(obj) != raw:
            raise ValueError("FULL_REFERENCE_NONCANONICAL")
        validate(s)
        return s
    except (KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("FULL_REFERENCE_INVALID_CHECKPOINT") from exc


def resource_receipt(s: dict) -> dict:
    validate(s)
    n = len(pack(s))
    return {"status": "SECONDARY_UNCONSTRAINED_REFERENCE_ONLY",
            "full_hypotheses": TOTAL_HYPOTHESES,
            "training_rows": s["step"],
            "peak_fit_evaluations": s["peak_fit_evaluations"],
            "total_fit_evaluations": s["total_fit_evaluations"],
            "checkpoint_bytes": n,
            "matched_rule_budget_ok": s["peak_fit_evaluations"] <= core.MAX_RULE_EVALS,
            "matched_state_budget_ok": n <= core.MAX_STATE_BYTES,
            "first_use_permitted": False,
            "primary_science_run": False}
