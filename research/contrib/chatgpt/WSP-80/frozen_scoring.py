"""WSP80 source-blind freeze first, private scoring only after prediction freeze.

This module never imports physics. A private evaluator may supply truth labels
ONLY after the complete public prediction bundle has been materialized and
SHA256-bound. No model can be called by score_frozen().
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
import math

from controls import paid_rows

PUBLIC = tuple((s, a) for s in product((0, 1), repeat=6) for a in range(6))
PUBLIC_SET = frozenset(PUBLIC)
REQUIRED = frozenset((
    "candidate", "stage_a", "fixed_degree3", "always_degree4",
    "symbolic", "paid_memory", "sham_novelty", "frozen_readout",
    "random_candidate", "mlp_forced", "mlp_native",
))


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _valid_prediction(value):
    return value is None or (
        type(value) is tuple and len(value) == 6
        and all(type(bit) is int and bit in (0, 1) for bit in value))


def freeze_public_outputs(ledger, predictors, mlp_probabilities, cost_receipts):
    """Source-blind pre-label receipt, with unlabeled equal-coverage MLP ranking.

    predictors are callable(s,a) functions. The random_candidate predictor
    must be trained on its independently paid random-policy ledger.
    """
    rows = paid_rows(ledger)
    if set(predictors) != REQUIRED:
        raise ValueError("missing required frozen controls")
    if not callable(mlp_probabilities) or type(cost_receipts) is not dict:
        raise ValueError("missing neural margin/cost receipts")
    outputs = {}
    for name in sorted(REQUIRED):
        query_predictions = []
        for state, action in PUBLIC:
            result = predictors[name](state, action)
            if not _valid_prediction(result):
                raise ValueError("invalid frozen public model prediction: " + name)
            query_predictions.append(list(result) if result is not None else None)
        outputs[name] = query_predictions
    confidence_count = sum(x is not None for x in outputs["candidate"])
    margins = []
    for i, (state, action) in enumerate(PUBLIC):
        probabilities = mlp_probabilities(state, action)
        if (type(probabilities) not in (list, tuple) or len(probabilities) != 6
                or any(type(x) not in (float, int) or not math.isfinite(x)
                       or not 0 <= x <= 1 for x in probabilities)):
            raise ValueError("invalid neural unlabeled margin")
        margin = min(abs(x - 0.5) for x in probabilities)
        margins.append((-margin, i))
    equal_coverage = frozenset(i for _, i in sorted(margins)[:confidence_count])
    outputs["mlp_matched"] = [
        outputs["mlp_forced"][i] if i in equal_coverage else None
        for i in range(len(PUBLIC))
    ]
    unique_paid = frozenset(PUBLIC.index((s, a)) for s, a, _ in rows)
    if any(x < 0 for x in unique_paid):
        raise ValueError("invalid paid query index")
    payload = {
        "schema": "wsp80.prelabel-predictions.v1",
        "public_query_count": len(PUBLIC),
        "paid_action_count": len(rows),
        "unique_paid_indices": sorted(unique_paid),
        "outputs": outputs,
        "cost_receipts": cost_receipts,
        "equal_coverage_count": confidence_count,
    }
    raw = _canonical(payload)
    return _canonical({"payload": payload, "sha256": sha256(raw.encode("ascii")).hexdigest()})


def score_frozen(frozen_receipt, truth, compositions):
    """Evaluator-only scoring: never calls a model or accesses source objects.

    truth: complete private mapping (public_state,public_action)->after.
    compositions: 32 private (initial_state,action1,action2,final_state)
    tuples. Both are withheld until freeze_public_outputs() has returned.
    """
    obj = json.loads(frozen_receipt)
    if type(obj) is not dict or set(obj) != {"payload", "sha256"}:
        raise ValueError("invalid frozen envelope")
    payload = obj["payload"]
    if (payload.get("schema") != "wsp80.prelabel-predictions.v1"
            or sha256(_canonical(payload).encode("ascii")).hexdigest() != obj["sha256"]
            or _canonical(obj) != frozen_receipt):
        raise ValueError("tampered or noncanonical frozen receipt")
    if (type(truth) is not dict or set(truth) != PUBLIC_SET
            or any(not _valid_prediction(x) or x is None for x in truth.values())):
        raise ValueError("missing complete evaluator-only truth")
    if type(compositions) not in (tuple, list) or len(compositions) != 32:
        raise ValueError("missing 32 fixed evaluator-only two-action compositions")
    for state, first, second, finish in compositions:
        if ((state, first) not in PUBLIC_SET or (state, second) not in PUBLIC_SET
                or not _valid_prediction(finish) or finish is None):
            raise ValueError("invalid private composition test")
    paid = set(payload["unique_paid_indices"])
    if (payload["public_query_count"] != len(PUBLIC)
            or payload["paid_action_count"] != 384 or len(paid) != len(payload["unique_paid_indices"])
            or any(type(i) is not int or i < 0 or i >= len(PUBLIC) for i in paid)
            or set(payload["outputs"]) != REQUIRED | {"mlp_matched"}):
        raise ValueError("incompatible prelabel bundle")
    answers = [truth[key] for key in PUBLIC]
    metrics = {}
    for name, predictions in payload["outputs"].items():
        if len(predictions) != len(PUBLIC) or any(
                x is not None and (type(x) is not list or not _valid_prediction(tuple(x)))
                for x in predictions):
            raise ValueError("invalid stored prediction shape")
        overall = {"correct": 0, "wrong_confident": 0, "abstain": 0}
        unpaid = {"correct": 0, "wrong_confident": 0, "abstain": 0, "total": len(PUBLIC) - len(paid)}
        for i, observed in enumerate(predictions):
            category = ("abstain" if observed is None else
                        "correct" if tuple(observed) == answers[i] else
                        "wrong_confident")
            overall[category] += 1
            if i not in paid:
                unpaid[category] += 1
        two_action = {"correct": 0, "wrong_confident": 0, "abstain": 0}
        for start, first, second, actual in compositions:
            intermediate = predictions[PUBLIC.index((start, first))]
            finish = (predictions[PUBLIC.index((tuple(intermediate), second))]
                      if intermediate is not None else None)
            category = ("abstain" if finish is None else
                        "correct" if tuple(finish) == actual else "wrong_confident")
            two_action[category] += 1
        metrics[name] = {"physical": overall, "genuinely_unpaid": unpaid,
                         "two_action": two_action}
    stage_a = payload["outputs"]["stage_a"]
    candidate = payload["outputs"]["candidate"]
    initially_correct = [i for i, x in enumerate(stage_a)
                         if x is not None and tuple(x) == answers[i]]
    retained = sum(candidate[i] is not None and tuple(candidate[i]) == answers[i]
                   for i in initially_correct)
    return {
        "schema": "wsp80.evaluator-score.v1",
        "prelabel_sha256": obj["sha256"],
        "paid_action_count": payload["paid_action_count"],
        "unique_paid_count": len(paid),
        "equal_coverage_count": payload["equal_coverage_count"],
        "stageA_true_correct_confident": len(initially_correct),
        "stageA_retained_true_correct_confident": retained,
        "stageA_retention_fraction": (retained / len(initially_correct)
                                      if initially_correct else None),
        "scores": metrics,
        "cost_receipts": payload["cost_receipts"],
    }
