"""WSP-162: certificate of contradictory public action consequences.

SOURCE-FREE. This is an evaluator-only mathematical impossibility witness:
if two regimes give different future states for the identical observable
(state, action), no single-valued prediction function of only (state, action)
can have zero error on both. Neither regime labels nor oracle midpoints are
ever supplied to the candidate learner.
"""
from __future__ import annotations

import hashlib
import json
import math

from public_boundary import PublicTransition

SCHEMA = "yggdrasil.wsp162.public-overlap-certificate.v1"
OUTPUTS = 4
MAX_CONTEXTS = 64


def _key(record):
    if type(record) is not PublicTransition:
        raise ValueError("WSP162_PUBLIC_RECORD_REQUIRED")
    # Exact typed public state/action, no invented source identity or timestamp.
    return (record.observation, record.action)


def _collection(rows, side):
    if type(rows) not in (tuple, list) or not 1 <= len(rows) <= MAX_CONTEXTS:
        raise ValueError("WSP162_" + side + "_COUNT")
    indexed = {}
    for row in rows:
        key = _key(row)
        if key in indexed:
            raise ValueError("WSP162_" + side + "_DUPLICATE")
        indexed[key] = row
    return indexed


def certificate(old_rows, new_rows):
    old = _collection(old_rows, "OLD")
    new = _collection(new_rows, "NEW")
    if old.keys() != new.keys():
        raise ValueError("WSP162_NOT_IDENTICAL_PUBLIC_INPUTS")
    entries = []
    sq = []
    for key in sorted(old):
        a, b = old[key], new[key]
        if (a.reward, a.terminated, a.truncated) != (
                b.reward, b.terminated, b.truncated):
            raise ValueError("WSP162_ONLY_NEXT_STATE_DIFF_ALLOWED")
        delta = tuple(b.next_observation[k]-a.next_observation[k]
                      for k in range(OUTPUTS))
        if not all(map(math.isfinite, delta)):
            raise ValueError("WSP162_NONFINITE_DELTA")
        sq.extend(d*d for d in delta)
        entries.append([
            list(a.observation), a.action, list(a.next_observation),
            list(b.next_observation)
        ])
    # Each of old/new labels receives equal weight, four output values
    # each. For every y1,y2 and any p:
    # ((p-y1)^2 + (p-y2)^2)/2 =
    # (p-(y1+y2)/2)^2 + (y1-y2)^2/4.
    floor_mse = math.fsum(sq)/(4.0*len(old)*OUTPUTS)
    payload = json.dumps(
        {"schema": SCHEMA, "paired": entries}, sort_keys=True,
        separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")
    return {
        "schema": SCHEMA,
        "paired_contexts": len(old),
        "conflicting_contexts": sum(
            any(old[key].next_observation[k] != new[key].next_observation[k]
                for k in range(OUTPUTS)) for key in old),
        "irreducible_joint_mse": floor_mse,
        "irreducible_joint_rmse": math.sqrt(floor_mse),
        "public_pair_sha256": hashlib.sha256(payload).hexdigest(),
    }


def paired_rmse(old_rows, new_rows, predictor):
    """Independent held-row scorer, NEVER a training/selection interface."""
    old = _collection(old_rows, "OLD")
    new = _collection(new_rows, "NEW")
    if old.keys() != new.keys():
        raise ValueError("WSP162_NOT_IDENTICAL_PUBLIC_INPUTS")
    errors = []
    for key in sorted(old):
        # Obtain one prediction for this public input; cannot condition on
        # which of its incompatible labels the evaluator subsequently scores.
        pred = predictor(key[0], key[1])
        if type(pred) not in (tuple, list) or len(pred) != OUTPUTS:
            raise ValueError("WSP162_PREDICTION_SHAPE")
        if any(type(x) not in (int, float) or not math.isfinite(x) for x in pred):
            raise ValueError("WSP162_PREDICTION_INVALID")
        for target in (old[key].next_observation, new[key].next_observation):
            errors.extend((pred[k]-target[k])**2 for k in range(OUTPUTS))
    return math.sqrt(math.fsum(errors)/(2.0*len(old)*OUTPUTS))


def ex_post_midpoint_score(old_rows, new_rows):
    """Evaluator-only oracle bound witness; not a deployable control."""
    old = _collection(old_rows, "OLD")
    new = _collection(new_rows, "NEW")
    if old.keys() != new.keys():
        raise ValueError("WSP162_NOT_IDENTICAL_PUBLIC_INPUTS")
    lookup = {
        key: tuple((old[key].next_observation[k]+new[key].next_observation[k])/2.
                   for k in range(OUTPUTS)) for key in old
    }
    return paired_rmse(old_rows, new_rows,
                       lambda obs, act: lookup[(tuple(obs), act)])
