"""Gate28 full-dictionary, *budgeted* sparse causal Bayesian-style control.

This is a candidate matched-budget diagnostic, NOT an exhaustive Bayes
posterior or independently qualified strongest control.  All node-specific
rules remain reachable through deterministic round-robin proposals. Only
public context, observed mediator bits, intervention and outcome are fitted.
Rule evaluations are charged using the same core.Work as structural arms.
No hidden world seed, family label, oracle truth or held feedback is read.
"""
from __future__ import annotations

import hashlib
import json
import math

import core
import full_reference

SCHEMA = "yggdrasil.gate28.sparse-causal-reference.v1"
ARMS = ("sparse_causal_reward", "sparse_causal_eig")
BANKS = full_reference.BANKS
SIZES = full_reference.BANK_SIZES
PROBES_PER_NODE = 64
BEAM_SIZE = 16
MAX_RULE_EVALS = core.MAX_RULE_EVALS
MAX_STATE_BYTES = core.MAX_STATE_BYTES
assert sum(SIZES) == 11424


def new(arm: str) -> dict:
    if arm not in ARMS:
        raise ValueError("INVALID_SPARSE_ARM")
    s = {"schema": SCHEMA, "arm": arm, "step": 0,
         "cursor": [0] * 7, "beam": [[] for _ in range(7)],
         "last_context": None, "source": None, "edits": 0,
         "attempts": 0}
    _validate(s)
    return s


def _score(entry: list[int]) -> float:
    """Smoothed held-evidence accuracy with low-sample penalty.

    The score is a *heuristic approximation*, not a normalized posterior
    across hypotheses evaluated on equal observation sets.
    """
    _, correct, trials = entry
    return ((correct + 1) / (trials + 2)
            - 0.2 / math.sqrt(trials + 1))


def _ordered(beam: list[list[int]]) -> list[list[int]]:
    return sorted(beam, key=lambda r: (-_score(r), -r[2], r[0]))


def _posterior(beam: list[list[int]]) -> list[tuple[int, float]]:
    if not beam:
        return []
    ranked = _ordered(beam)
    best = _score(ranked[0])
    raw = [math.exp(8 * (_score(r) - best)) for r in ranked]
    denominator = sum(raw)
    return [(r[0], p / denominator) for r, p in zip(ranked, raw)]


def _estimate(s: dict, x: tuple[int, ...], action: int,
              work: core.Work) -> tuple[float, float]:
    if type(action) is not int or not 0 <= action < 13:
        raise ValueError("INVALID_ACTION")
    core.as_mask(x)
    cells = list(x)
    previous = (None if s["last_context"] is None else
                tuple(s["last_context"]))
    for node in range(6):
        if action < 12 and action // 2 == node:
            bit = action % 2
        else:
            best = _ordered(s["beam"][node])
            if not best:
                bit = 0
            else:
                bit = full_reference._rule(BANKS[node][best[0][0]], cells,
                                           previous, work)
                if bit is None:
                    bit = 0
        cells.append(bit)
    hypotheses = _posterior(s["beam"][6])
    if not hypotheses:
        return 0.5, 0.0
    p, epistemic = 0.0, 0.0
    for index, weight in hypotheses:
        bit = full_reference._rule(BANKS[6][index], cells, previous, work)
        if bit is None:
            continue
        p += weight * (0.9 if bit else 0.1)
        epistemic += weight * bit
    return min(0.9, max(0.1, p)), epistemic


def predict(s: dict, context: tuple[int, ...], action: int,
            work: core.Work) -> float:
    return _estimate(s, context, action, work)[0]


def choose(s: dict, context: tuple[int, ...], work: core.Work) -> int:
    core.as_mask(context)
    estimates = [_estimate(s, context, a, work) for a in range(13)]
    if s["arm"] == "sparse_causal_eig":
        # EIG conditional on point-estimate mediators and 10% label noise.
        h0 = -0.1 * math.log(0.1) - 0.9 * math.log(0.9)
        scores = [(-p * math.log(p) - (1 - p) * math.log(1 - p)
                   - h0 + 0.02 * p) for p, _ in estimates]
    else:
        scores = [p for p, _ in estimates]
    return max(range(13), key=lambda a: (scores[a], -a))


def observe(s: dict, context: tuple[int, ...],
            intermediates: tuple[int, ...], action: int,
            consequence: int, work: core.Work) -> None:
    core.as_mask(context)
    if (len(intermediates) != 6 or any(type(x) is not int or x not in (0, 1)
                                       for x in intermediates)):
        raise ValueError("INVALID_PUBLIC_MEDIATOR")
    if type(action) is not int or not 0 <= action < 13:
        raise ValueError("INVALID_ACTION")
    if type(consequence) is not int or consequence not in (0, 1):
        raise ValueError("INVALID_CONSEQUENCE")
    cells = list(context) + list(intermediates)
    prev = None if s["last_context"] is None else tuple(s["last_context"])
    # Every evaluated candidate consumes a rule evaluation. We do not fit
    # the targeted mediator, whose generating rule was bypassed by do().
    for node, bank in enumerate(BANKS):
        if node < 6 and action < 12 and action // 2 == node:
            continue
        observed = intermediates[node] if node < 6 else consequence
        candidates = {r[0]: list(r) for r in s["beam"][node]}
        start = s["cursor"][node]
        for j in range(PROBES_PER_NODE):
            index = (start + j) % len(bank)
            if index not in candidates:
                candidates[index] = [index, 0, 0]
        s["cursor"][node] = (start + PROBES_PER_NODE) % len(bank)
        for index in sorted(candidates):
            predicted = full_reference._rule(bank[index], cells, prev, work)
            if predicted is not None:
                row = candidates[index]
                row[1] += int(predicted == observed)
                row[2] += 1
        s["beam"][node] = _ordered(list(candidates.values()))[:BEAM_SIZE]
    s["last_context"] = list(context)
    s["step"] += 1
    _validate(s)


def seal_source(s: dict) -> None:
    if s["source"] is not None or s["step"] != 96:
        raise ValueError("SOURCE_FREEZE_REQUIRES_96_OBSERVATIONS")
    snap = {"beam": [[list(r) for r in node] for node in s["beam"]],
            "last_context": s["last_context"]}
    s["source"] = {"snapshot": snap,
                   "digest": hashlib.sha256(core.canonical(snap)).hexdigest()}
    _validate(s)


def source_predict(s: dict, context: tuple[int, ...], action: int,
                   work: core.Work) -> float:
    if s["source"] is None:
        raise ValueError("SOURCE_UNFROZEN")
    return predict(s["source"]["snapshot"], context, action, work)


def _validate_beam(beam: object) -> None:
    if not isinstance(beam, list) or len(beam) != 7:
        raise ValueError("SPARSE_NODE_COUNT")
    for node, rows in enumerate(beam):
        if not isinstance(rows, list) or len(rows) > BEAM_SIZE:
            raise ValueError("SPARSE_BEAM_CAP")
        seen = set()
        for row in rows:
            if not isinstance(row, list) or len(row) != 3:
                raise ValueError("SPARSE_PARTICLE_SHAPE")
            i, correct, trials = row
            if any(type(v) is not int for v in row) or not (
                    0 <= i < SIZES[node] and 0 <= correct <= trials):
                raise ValueError("SPARSE_PARTICLE_RANGE")
            if i in seen:
                raise ValueError("SPARSE_DUPLICATE_PARTICLE")
            seen.add(i)


def _validate(s: dict) -> None:
    if s.get("schema") != SCHEMA or s.get("arm") not in ARMS:
        raise ValueError("SPARSE_SCHEMA")
    if type(s.get("step")) is not int or not 0 <= s["step"] <= 224:
        raise ValueError("SPARSE_STEP")
    cursors = s.get("cursor")
    if (not isinstance(cursors, list) or len(cursors) != 7 or
            any(type(v) is not int or not 0 <= v < SIZES[i]
                for i, v in enumerate(cursors))):
        raise ValueError("SPARSE_CURSOR")
    _validate_beam(s.get("beam"))
    if s.get("last_context") is not None:
        core.as_mask(tuple(s["last_context"]))
    if s.get("edits") != 0 or s.get("attempts") != 0:
        raise ValueError("SPARSE_FIXED_STRUCTURE_ONLY")
    if s.get("source") is not None:
        item = s["source"]
        snap = item["snapshot"]
        _validate_beam(snap["beam"])
        if snap["last_context"] is not None:
            core.as_mask(tuple(snap["last_context"]))
        if hashlib.sha256(core.canonical(snap)).hexdigest() != item["digest"]:
            raise ValueError("SPARSE_SOURCE_TAMPER")
    if len(core.canonical(s)) > MAX_STATE_BYTES - 110:
        raise ValueError("SPARSE_MEMORY_LIMIT")


def pack(s: dict) -> bytes:
    _validate(s)
    encoded = core.canonical(s)
    wire = core.canonical({"payload": s,
                           "sha256": hashlib.sha256(encoded).hexdigest()})
    if len(wire) > MAX_STATE_BYTES:
        raise ValueError("SPARSE_MEMORY_LIMIT")
    return wire


def unpack(raw: bytes) -> dict:
    if len(raw) > MAX_STATE_BYTES:
        raise ValueError("SPARSE_MEMORY_LIMIT")
    try:
        doc = json.loads(raw)
        if set(doc) != {"payload", "sha256"}:
            raise ValueError("SPARSE_FORMAT")
        s = doc["payload"]
        if doc["sha256"] != hashlib.sha256(core.canonical(s)).hexdigest():
            raise ValueError("SPARSE_CHECKPOINT_DIGEST")
        if raw != core.canonical(doc):
            raise ValueError("SPARSE_CHECKPOINT_NONCANONICAL")
        _validate(s)
        return s
    except (TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("SPARSE_CHECKPOINT_INVALID") from exc


def diagnostic() -> dict:
    """Only synthetic public rows; not a primary result or science gain."""
    s = new(ARMS[0])
    maxwork = 0
    for step in range(96):
        context = core.as_bits((step * 29 + 11) % 256)
        intermediate = tuple(context[i] ^ context[(i + 1) % 8]
                             for i in range(6))
        action = step % 13
        consequence = intermediate[0] ^ intermediate[3]
        work = core.Work()
        observe(s, context, intermediate, action, consequence, work)
        maxwork = max(maxwork, work.count)
    seal_source(s)
    for step in range(128):
        context = core.as_bits((step * 43 + 7) % 256)
        intermediate = tuple(context[i] ^ context[(i + 2) % 8]
                             for i in range(6))
        w = core.Work()
        action = choose(s, context, w)
        observe(s, context, intermediate, action,
                intermediate[0] ^ intermediate[2], w)
        maxwork = max(maxwork, w.count)
    b = pack(s)
    return {"status": "G28_BUDGET_BAYES_DIAGNOSTIC_PASS",
            "maximum_work": maxwork, "checkpoint_bytes": len(b),
            "hypotheses_reachable": sum(SIZES),
            "source_digest": s["source"]["digest"],
            "steps": s["step"], "primary_scored": False,
            "strength_vs_fully_trained_control": "UNVERIFIED"}
