"""Lossless full-grammar score compression; not exact Bayesian mediation.

Every original hypothesis and duplicate prior retains its original index.
Complement/alias rules share one signed sufficient statistic. No private
world labels or held outcomes enter this module. Reconstructing and sorting
scores costs CPU/memory as well as the metered primitive rule evaluations.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
import struct

import core
import full_reference as full

SCHEMA = "yggdrasil.gate28.lossless-grammar-reference.v1"
ARMS = ("quotient_causal_reward", "quotient_causal_eig")


def representative(rule: tuple) -> tuple[tuple, int]:
    kind, parents, invert = rule
    if kind == "nand":
        kind, invert = "and", invert ^ 1
    if kind == "lag_xor":
        parents = (parents[0] % 8, parents[1])
    return (kind, parents, 0), (-1 if invert else 1)


def build_tables() -> tuple:
    bases, mappings = [], []
    for bank in full.BANKS:
        canonical = sorted({representative(rule)[0] for rule in bank})
        indices = {rule: i for i, rule in enumerate(canonical)}
        mappings.append(tuple((indices[rep], sign)
                              for rep, sign in map(representative, bank)))
        bases.append(tuple(canonical))
    return tuple(bases), tuple(mappings)


BASES, MAPS = build_tables()
SIZES = tuple(map(len, BASES))
assert SIZES == (364, 509, 689, 908, 1170, 1479, 125)
assert sum(map(len, MAPS)) == full.TOTAL_HYPOTHESES == 11424
assert sum(SIZES) == 5244


def new(arm: str) -> dict:
    if arm not in ARMS:
        raise ValueError("QUOTIENT_ARM")
    return {"schema": SCHEMA, "arm": arm, "step": 0,
            "scores": [[0] * n for n in SIZES],
            "last_context": None, "source": None, "edits": 0, "attempts": 0}


def expanded_scores(s: dict) -> list[list[int]]:
    return [[sign * row[index] for index, sign in mapping]
            for row, mapping in zip(s["scores"], MAPS)]


def _prepared(s: dict) -> list:
    # Preserve full-reference posterior order, ties and multiplicity.
    return full._prepared({"scores": expanded_scores(s)})


def predict(s: dict, context: tuple[int, ...], action: int,
            work: core.Work) -> float:
    core.as_mask(context)
    return full._estimate(s, context, action, _prepared(s), work)[0]


def choose(s: dict, context: tuple[int, ...], work: core.Work) -> int:
    core.as_mask(context)
    prep = _prepared(s)
    estimates = [full._estimate(s, context, a, prep, work)[0]
                 for a in range(core.N_ACTIONS)]
    if s["arm"] == ARMS[1]:
        noise = full.OUTCOME_FLIP
        h0 = -noise * math.log(noise) - (1 - noise) * math.log(1 - noise)
        estimates = [-p * math.log(p) - (1 - p) * math.log(1 - p)
                     - h0 + 0.02 * p for p in estimates]
    return max(range(core.N_ACTIONS), key=lambda a: (estimates[a], -a))


def observe(s: dict, context: tuple[int, ...], intermediates: tuple[int, ...],
            action: int, consequence: int, work: core.Work) -> None:
    full._validate_bits(context, intermediates)
    if type(action) is not int or not 0 <= action < core.N_ACTIONS:
        raise ValueError("QUOTIENT_ACTION")
    if type(consequence) is not int or consequence not in (0, 1):
        raise ValueError("QUOTIENT_CONSEQUENCE")
    if s["step"] >= 224:
        raise ValueError("QUOTIENT_EXPOSURE_CAP")
    cells = list(context) + list(intermediates)
    prev = None if s["last_context"] is None else tuple(s["last_context"])
    for node, bank in enumerate(BASES):
        if node < 6 and action < 12 and action // 2 == node:
            continue
        observed = intermediates[node] if node < 6 else consequence
        for i, rule in enumerate(bank):
            pred = full._rule(rule, cells, prev, work)
            if pred is not None:
                s["scores"][node][i] += 1 if pred == observed else -1
    s["step"] += 1
    s["last_context"] = list(context)


def seal_source(s: dict) -> None:
    if s["step"] != 96 or s["source"] is not None:
        raise ValueError("QUOTIENT_SOURCE_ORDER")
    snap = {"prepared": _prepared(s), "last_context": s["last_context"]}
    s["source"] = {"snapshot": snap,
                   "digest": hashlib.sha256(core.canonical(snap)).hexdigest()}


def source_predict(s: dict, context: tuple[int, ...], action: int,
                   work: core.Work) -> float:
    core.as_mask(context)
    if s["source"] is None:
        raise ValueError("QUOTIENT_SOURCE_UNFROZEN")
    snap = s["source"]["snapshot"]
    return full._estimate(snap, context, action, snap["prepared"], work)[0]


def _validate(s: dict) -> None:
    step = s.get("step")
    if (s.get("schema") != SCHEMA or s.get("arm") not in ARMS or
            type(step) is not int or not 0 <= step <= 224):
        raise ValueError("QUOTIENT_SCHEMA_STEP")
    scores = s.get("scores")
    if (not isinstance(scores, list) or len(scores) != 7 or
            any(not isinstance(row, list) or len(row) != SIZES[i]
                or any(type(x) is not int or abs(x) > step for x in row)
                for i, row in enumerate(scores))):
        raise ValueError("QUOTIENT_SCORE_RANGE")
    if s.get("edits") != 0 or s.get("attempts") != 0:
        raise ValueError("QUOTIENT_FIXED_STRUCTURE")
    if step:
        core.as_mask(tuple(s["last_context"]))
    elif s.get("last_context") is not None:
        raise ValueError("QUOTIENT_CONTEXT")
    source = s.get("source")
    if source is None:
        if step > 96:
            raise ValueError("QUOTIENT_SOURCE_MISSING")
        return
    if step < 96 or set(source) != {"snapshot", "digest"}:
        raise ValueError("QUOTIENT_SOURCE_FORMAT")
    snap = source["snapshot"]
    if set(snap) != {"prepared", "last_context"}:
        raise ValueError("QUOTIENT_SNAPSHOT_FORMAT")
    core.as_mask(tuple(snap["last_context"]))
    prep = snap["prepared"]
    if len(prep) != 7:
        raise ValueError("QUOTIENT_SOURCE_SHAPE")
    for node, rows in enumerate(prep):
        if len(rows) != (1 if node < 6 else full.TOP_K):
            raise ValueError("QUOTIENT_SOURCE_POSTERIOR")
        seen = set()
        total = 0.0
        for idx, weight in rows:
            if (type(idx) is not int or not 0 <= idx < len(full.BANKS[node])
                    or idx in seen or type(weight) not in (int, float)
                    or not math.isfinite(weight) or not 0 <= weight <= 1):
                raise ValueError("QUOTIENT_SOURCE_PARTICLE")
            seen.add(idx)
            total += weight
        if abs(total - 1.0) > 1e-9:
            raise ValueError("QUOTIENT_SOURCE_NORMALIZATION")
    if hashlib.sha256(core.canonical(snap)).hexdigest() != source["digest"]:
        raise ValueError("QUOTIENT_SOURCE_DIGEST")


def pack(s: dict) -> bytes:
    _validate(s)
    counts = [x for row in s["scores"] for x in row]
    payload = {**s, "scores": base64.b64encode(
        struct.pack("<" + "h" * len(counts), *counts)).decode("ascii")}
    raw = core.canonical({"payload": payload, "sha256": hashlib.sha256(
        core.canonical(payload)).hexdigest()})
    if len(raw) > core.MAX_STATE_BYTES:
        raise ValueError("QUOTIENT_CHECKPOINT_CAP")
    return raw


def unpack(raw: bytes) -> dict:
    if len(raw) > core.MAX_STATE_BYTES:
        raise ValueError("QUOTIENT_CHECKPOINT_CAP")
    try:
        doc = json.loads(raw)
        if (set(doc) != {"payload", "sha256"} or core.canonical(doc) != raw
                or hashlib.sha256(core.canonical(doc["payload"])).hexdigest()
                != doc["sha256"]):
            raise ValueError("QUOTIENT_INTEGRITY")
        p = doc["payload"]
        buf = base64.b64decode(p["scores"], validate=True)
        if len(buf) != 2 * sum(SIZES):
            raise ValueError("QUOTIENT_COUNT_ENCODING")
        vals = struct.unpack("<" + "h" * sum(SIZES), buf)
        rows, offset = [], 0
        for n in SIZES:
            rows.append(list(vals[offset:offset + n]))
            offset += n
        s = {**p, "scores": rows}
        _validate(s)
        if pack(s) != raw:
            raise ValueError("QUOTIENT_NONCANONICAL")
        return s
    except (TypeError, KeyError, AttributeError, ValueError, struct.error) as exc:
        raise ValueError("QUOTIENT_CHECKPOINT_INVALID") from exc
