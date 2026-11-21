"""Gate28 compute-matched, *partially enumerated* causal Bayesian comparator.

Every selected finite-grammar hypothesis is fitted on EVERY eligible public
observation with the same rule-evaluation meter as structural arms. Deterministic
uniform coverage of the entire operator dictionary improves on the K96
undersampled diagnostic, but DOES NOT constitute complete-grammar or exact
Bayesian inference, and is not automatically the strongest matched control.
Source-predictive capacity is separately frozen in the same 16 KiB checkpoint.
Only public action/mediator/context/consequence evidence enters the learner.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
import struct

import core
import full_reference

SCHEMA = "yggdrasil.gate28.dense-fitted-causal.v1"
NULL_ARM = "dense_causal_nullmix"
ARMS = ("dense_causal_reward", "dense_causal_eig", NULL_ARM)
NULL_WINDOW = 32
MAX_PER_NODE = 768
BANK_INDICES = tuple(
    tuple(i * len(bank) // min(MAX_PER_NODE, len(bank))
          for i in range(min(MAX_PER_NODE, len(bank))))
    for bank in full_reference.BANKS)
BANKS = tuple(tuple(full_reference.BANKS[node][i] for i in indices)
              for node, indices in enumerate(BANK_INDICES))
SIZES = tuple(map(len, BANKS))
assert sum(SIZES) == 4888
assert all(len(set(indices)) == len(indices) for indices in BANK_INDICES)


def _score_bytes(scores: list[list[int]]) -> list[str]:
    return [base64.b64encode(struct.pack("<" + "h" * len(row), *row)).decode("ascii")
            for row in scores]


def _decode_scores(encoded: object) -> list[list[int]]:
    if not isinstance(encoded, list) or len(encoded) != 7:
        raise ValueError("DENSE_SCORE_SHAPE")
    scores = []
    for i, item in enumerate(encoded):
        if type(item) is not str:
            raise ValueError("DENSE_SCORE_ENCODING")
        try:
            raw = base64.b64decode(item, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ValueError("DENSE_SCORE_BASE64") from exc
        if len(raw) != 2 * SIZES[i]:
            raise ValueError("DENSE_SCORE_LENGTH")
        scores.append(list(struct.unpack("<" + "h" * SIZES[i], raw)))
    return scores


def new(arm: str) -> dict:
    if arm not in ARMS:
        raise ValueError("INVALID_DENSE_ARM")
    state = {"schema": SCHEMA, "arm": arm, "step": 0,
             "scores": [[0] * n for n in SIZES],
             "last_context": None, "source": None, "edits": 0,
             "attempts": 0}
    if arm == NULL_ARM:
        state["null_evidence"] = []
    _validate(state)
    return state


def _prepared(s: dict) -> list[list[tuple[int, float]]]:
    result = []
    for node, scores in enumerate(s["scores"]):
        rank = full_reference._posterior(
            scores, 1 if node < 6 else full_reference.TOP_K)
        result.append([(BANK_INDICES[node][i], weight)
                       for i, weight in rank])
    return result


def _estimate(s: dict, context: tuple[int, ...], action: int,
              prepared: list, work: core.Work) -> tuple[float, float]:
    core.as_mask(context)
    return full_reference._estimate(s, context, action, prepared, work)


def _null_weight(evidence: list[float]) -> float:
    """Bounded rolling public-only prequential likelihood-mixture weight."""
    logit = sum(evidence) - math.log(2.0)
    logit = max(-40.0, min(40.0, logit))
    return 1.0 / (1.0 + math.exp(-logit))


def predict(s: dict, context: tuple[int, ...], action: int,
            work: core.Work) -> float:
    forecast = _estimate(s, context, action, _prepared(s), work)[0]
    if s["arm"] == NULL_ARM:
        return 0.5 + _null_weight(s["null_evidence"]) * (forecast - 0.5)
    return forecast


def choose(s: dict, context: tuple[int, ...], work: core.Work) -> int:
    core.as_mask(context)
    prepared = _prepared(s)
    estimated = [_estimate(s, context, a, prepared, work)[0]
                 for a in range(core.N_ACTIONS)]
    if s["arm"] == "dense_causal_eig":
        h0 = -0.1 * math.log(0.1) - 0.9 * math.log(0.9)
        weights = [-p * math.log(p) - (1 - p) * math.log(1 - p) -
                   h0 + 0.02 * p for p in estimated]
    else:
        weights = estimated
    return max(range(core.N_ACTIONS), key=lambda a: (weights[a], -a))


def observe(s: dict, context: tuple[int, ...],
            intermediates: tuple[int, ...], action: int,
            consequence: int, work: core.Work) -> None:
    core.as_mask(context)
    if (len(intermediates) != 6 or
            any(type(v) is not int or v not in (0, 1) for v in intermediates)):
        raise ValueError("DENSE_PUBLIC_MEDIATOR")
    if type(action) is not int or not 0 <= action < 13:
        raise ValueError("DENSE_ACTION")
    if type(consequence) is not int or consequence not in (0, 1):
        raise ValueError("DENSE_CONSEQUENCE")
    if s["step"] >= 224:
        raise ValueError("DENSE_EXPOSURE_CAP")
    if s["arm"] == NULL_ARM:
        # Prequential forecast is computed before learning THIS consequence,
        # using only past public data. Held queries never enter observe.
        raw = _estimate(s, context, action, _prepared(s), work)[0]
        ratio = math.log(2.0 * (raw if consequence else 1.0 - raw))
        s["null_evidence"].append(round(ratio, 9))
        s["null_evidence"] = s["null_evidence"][-NULL_WINDOW:]
    cells = list(context) + list(intermediates)
    previous = (None if s["last_context"] is None else
                tuple(s["last_context"]))
    for node, bank in enumerate(BANKS):
        if node < 6 and action < 12 and action // 2 == node:
            continue
        expected = intermediates[node] if node < 6 else consequence
        scores = s["scores"][node]
        for i, rule in enumerate(bank):
            predicted = full_reference._rule(rule, cells, previous, work)
            if predicted is not None:
                scores[i] += 1 if predicted == expected else -1
    s["last_context"] = list(context)
    s["step"] += 1
    _validate(s)


def seal_source(s: dict) -> None:
    if s["step"] != 96 or s["source"] is not None:
        raise ValueError("DENSE_SOURCE_REQUIRES_96_ROWS")
    snapshot = {"prepared": _prepared(s),
                "last_context": s["last_context"]}
    if s["arm"] == NULL_ARM:
        snapshot["null_evidence"] = list(s["null_evidence"])
    s["source"] = {"snapshot": snapshot,
                   "digest": hashlib.sha256(core.canonical(snapshot)).hexdigest()}
    _validate(s)


def source_predict(s: dict, context: tuple[int, ...], action: int,
                   work: core.Work) -> float:
    if s["source"] is None:
        raise ValueError("DENSE_SOURCE_UNFROZEN")
    snap = s["source"]["snapshot"]
    raw = _estimate({"last_context": snap["last_context"]},
                    context, action, snap["prepared"], work)[0]
    return (0.5 + _null_weight(snap["null_evidence"]) * (raw - 0.5)
            if s["arm"] == NULL_ARM else raw)


def _validate(s: dict) -> None:
    if s.get("schema") != SCHEMA or s.get("arm") not in ARMS:
        raise ValueError("DENSE_SCHEMA")
    if type(s.get("step")) is not int or not 0 <= s["step"] <= 224:
        raise ValueError("DENSE_STEP")
    scores = s.get("scores")
    if (not isinstance(scores, list) or len(scores) != 7 or
            any(len(x) != SIZES[i] for i, x in enumerate(scores))):
        raise ValueError("DENSE_SHAPE")
    for row in scores:
        if any(type(x) is not int or abs(x) > s["step"]
               for x in row):
            raise ValueError("DENSE_SCORE")
    prev = s.get("last_context")
    if prev is not None:
        core.as_mask(tuple(prev))
    if s.get("edits") != 0 or s.get("attempts") != 0:
        raise ValueError("DENSE_FIXED_STRUCTURE")
    evidence = s.get("null_evidence")
    if s["arm"] == NULL_ARM:
        if (type(evidence) is not list or
                len(evidence) > NULL_WINDOW or len(evidence) > s["step"] or
                any(type(x) not in (float, int) or not math.isfinite(x)
                    or not -1.7 <= x <= 0.7 for x in evidence)):
            raise ValueError("DENSE_NULL_PUBLIC_EVIDENCE")
    elif "null_evidence" in s:
        raise ValueError("DENSE_UNEXPECTED_NULL_EVIDENCE")
    item = s.get("source")
    if item is not None:
        snap = item["snapshot"]
        prep = snap["prepared"]
        if not isinstance(prep, list) or len(prep) != 7:
            raise ValueError("DENSE_SOURCE_SHAPE")
        for node, rows in enumerate(prep):
            if len(rows) != (1 if node < 6 else full_reference.TOP_K):
                raise ValueError("DENSE_SOURCE_POSTERIOR")
            total = 0.0
            seen = set()
            for index, weight in rows:
                if (type(index) is not int or index not in BANK_INDICES[node]
                        or index in seen or type(weight) not in (float, int)
                        or not math.isfinite(weight) or weight < 0.0):
                    raise ValueError("DENSE_SOURCE_PARTICLE")
                seen.add(index)
                total += weight
            if not 0.999999999 <= total <= 1.000000001:
                raise ValueError("DENSE_SOURCE_NORMALIZATION")
        if snap["last_context"] is not None:
            core.as_mask(tuple(snap["last_context"]))
        if s["arm"] == NULL_ARM:
            frozen = snap.get("null_evidence")
            if (type(frozen) is not list or len(frozen) > NULL_WINDOW or
                    any(type(x) not in (int, float) or not math.isfinite(x)
                        or not -1.7 <= x <= 0.7 for x in frozen)):
                raise ValueError("DENSE_FROZEN_NULL_EVIDENCE")
        elif "null_evidence" in snap:
            raise ValueError("DENSE_FROZEN_NULL_UNEXPECTED")
        if hashlib.sha256(core.canonical(snap)).hexdigest() != item["digest"]:
            raise ValueError("DENSE_SOURCE_TAMPER")


def pack(s: dict) -> bytes:
    _validate(s)
    payload = {**s, "scores": _score_bytes(s["scores"])}
    encoded = core.canonical(payload)
    result = core.canonical({"payload": payload,
                             "sha256": hashlib.sha256(encoded).hexdigest()})
    if len(result) > core.MAX_STATE_BYTES:
        raise ValueError("DENSE_CHECKPOINT_CAP")
    return result


def unpack(raw: bytes) -> dict:
    if len(raw) > core.MAX_STATE_BYTES:
        raise ValueError("DENSE_CHECKPOINT_CAP")
    try:
        document = json.loads(raw)
        if type(document) is not dict or set(document) != {"payload", "sha256"}:
            raise ValueError("DENSE_CHECKPOINT_FORMAT")
        payload = document["payload"]
        if (hashlib.sha256(core.canonical(payload)).hexdigest() !=
                document["sha256"] or core.canonical(document) != raw):
            raise ValueError("DENSE_CHECKPOINT_DIGEST")
        state = {**payload, "scores": _decode_scores(payload["scores"])}
        _validate(state)
        return state
    except (TypeError, KeyError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("DENSE_CHECKPOINT_INVALID") from exc


def capacity_receipt(s: dict) -> dict:
    return {"selected_hypotheses": sum(SIZES),
            "grammar_hypotheses": full_reference.TOTAL_HYPOTHESES,
            "fully_fitted_selected_rules": True,
            "complete_grammar_covered": False,
            "exact_bayesian_posterior": False,
            "public_null_mixture_enabled": s["arm"] == NULL_ARM,
            "checkpoint_bytes": len(pack(s)),
            "primary_science": False,
            "scientific_gain": "UNVERIFIED"}
