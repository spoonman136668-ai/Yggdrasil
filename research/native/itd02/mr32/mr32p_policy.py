"""Policy-side process boundary for MR32-P.

This module imports no evaluator or task-generator code. Its only inputs are
public memory/query records and public selector state.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys

Q = 65_536
TOTAL = 16
ACTIVE = 7
METHODS = {
    "random", "fixed_recency", "evidence_only",
    "uniform_mc", "leave_one_out", "shapley",
}
LEARNED = {"uniform_mc", "leave_one_out", "shapley"}
INPUT_SCHEMA = "yggdrasil.mr32p.policy-message.v1"
STATE_SCHEMA = "yggdrasil.mr32p.policy-state.v1"


class PolicyInputError(ValueError):
    pass


def _require_keys(value: dict, keys: set[str], code: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise PolicyInputError(code)


def _features(record: dict, uses: list[int], last_used: list[int],
              clock: int) -> tuple[int, ...]:
    item = record["item_id"]
    age = max(0, clock - last_used[item])
    return (
        Q,
        record["evidence_level"] * Q // 7,
        record["error_level"] * Q // 3,
        record["contradiction_level"] * Q // 3,
        Q // (1 + age),
        min(uses[item], 16) * Q // 16,
    )


def _predict(weights: list[int], features: tuple[int, ...]) -> int:
    if len(weights) != 6:
        raise PolicyInputError("POLICY_WEIGHT_DIMENSION")
    return max(-Q, min(Q, sum(w * x for w, x in zip(weights, features)) // Q))


def _validate_records(records: object) -> list[dict]:
    if not isinstance(records, list) or len(records) != TOTAL:
        raise PolicyInputError("PUBLIC_RECORD_COUNT")
    normalized = []
    for row in records:
        _require_keys(row, {
            "item_id", "evidence_level", "error_level",
            "contradiction_level", "proposed_action",
        }, "PUBLIC_RECORD_FIELDS")
        for key in ("item_id", "evidence_level", "error_level",
                    "contradiction_level", "proposed_action"):
            value = row[key]
            if isinstance(value, bool) or not isinstance(value, int):
                raise PolicyInputError("PUBLIC_RECORD_INTEGER")
        if not 0 <= row["item_id"] < TOTAL:
            raise PolicyInputError("PUBLIC_ITEM_RANGE")
        if not 0 <= row["evidence_level"] <= 7:
            raise PolicyInputError("PUBLIC_EVIDENCE_RANGE")
        if not 0 <= row["error_level"] <= 3:
            raise PolicyInputError("PUBLIC_ERROR_RANGE")
        if not 0 <= row["contradiction_level"] <= 3:
            raise PolicyInputError("PUBLIC_CONTRADICTION_RANGE")
        if row["proposed_action"] not in (0, 1):
            raise PolicyInputError("PUBLIC_ACTION_RANGE")
        normalized.append(dict(row))
    if {row["item_id"] for row in normalized} != set(range(TOTAL)):
        raise PolicyInputError("PUBLIC_ITEM_SET")
    return sorted(normalized, key=lambda row: row["item_id"])


def _validate_state(state: object) -> dict:
    _require_keys(state, {
        "schema", "weights", "uses", "last_used", "clock"
    }, "PUBLIC_STATE_FIELDS")
    if state["schema"] != STATE_SCHEMA:
        raise PolicyInputError("PUBLIC_STATE_SCHEMA")
    weights, uses, last_used = state["weights"], state["uses"], state["last_used"]
    if not isinstance(weights, list) or len(weights) != 6:
        raise PolicyInputError("PUBLIC_STATE_WEIGHTS")
    if not isinstance(uses, list) or len(uses) != TOTAL:
        raise PolicyInputError("PUBLIC_STATE_USES")
    if not isinstance(last_used, list) or len(last_used) != TOTAL:
        raise PolicyInputError("PUBLIC_STATE_RECENCY")
    for value in weights:
        if isinstance(value, bool) or not isinstance(value, int) or not -4*Q <= value <= 4*Q:
            raise PolicyInputError("PUBLIC_STATE_WEIGHT_RANGE")
    for value in uses:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise PolicyInputError("PUBLIC_STATE_USE_RANGE")
    clock = state["clock"]
    if isinstance(clock, bool) or not isinstance(clock, int) or clock < 0:
        raise PolicyInputError("PUBLIC_STATE_CLOCK")
    for value in last_used:
        if (isinstance(value, bool) or not isinstance(value, int)
                or value < -1 or (value != -1 and value >= clock)):
            raise PolicyInputError("PUBLIC_STATE_RECENCY_RANGE")
    return {
        "schema": STATE_SCHEMA,
        "weights": list(weights),
        "uses": list(uses),
        "last_used": list(last_used),
        "clock": clock,
    }


def initial_state() -> dict:
    return {
        "schema": STATE_SCHEMA,
        "weights": [0] * 6,
        "uses": [0] * TOTAL,
        "last_used": [-1] * TOTAL,
        "clock": 0,
    }


def select_and_act(message: dict) -> dict:
    _require_keys(message, {
        "schema", "operation", "method", "public_items", "records", "state"
    }, "POLICY_MESSAGE_FIELDS")
    if message["schema"] != INPUT_SCHEMA or message["operation"] != "act":
        raise PolicyInputError("POLICY_MESSAGE_SCHEMA_OR_OPERATION")
    method = message["method"]
    if method not in METHODS:
        raise PolicyInputError("POLICY_METHOD")
    items = message["public_items"]
    if (not isinstance(items, list) or len(items) != TOTAL
            or any(isinstance(x, bool) or not isinstance(x, int) for x in items)
            or set(items) != set(range(TOTAL))):
        raise PolicyInputError("PUBLIC_QUERY_PERMUTATION")
    records = _validate_records(message["records"])
    state = _validate_state(message["state"])
    by_id = {row["item_id"]: row for row in records}

    if method == "random":
        digest = hashlib.sha256(
            json.dumps(items, separators=(",", ":")).encode("ascii")
        ).digest()
        rng = random.Random(int.from_bytes(digest[:8], "big"))
        selected = set(rng.sample(range(TOTAL), ACTIVE))
    elif method == "fixed_recency":
        selected = set(sorted(
            range(TOTAL), key=lambda item: (-state["last_used"][item], item)
        )[:ACTIVE])
    elif method == "evidence_only":
        selected = set(sorted(
            range(TOTAL),
            key=lambda item: (-2 ** by_id[item]["evidence_level"], item)
        )[:ACTIVE])
    else:
        ranked = []
        for item in range(TOTAL):
            features = _features(by_id[item], state["uses"],
                                 state["last_used"], state["clock"])
            ranked.append((_predict(state["weights"], features), item))
        ranked.sort(key=lambda pair: (-pair[0], pair[1]))
        selected = {item for _, item in ranked[:ACTIVE]}

    if len(selected) != ACTIVE:
        raise PolicyInputError("ACTIVE_PARTITION")
    actions = []
    uses = []
    public_trace = []
    for step, item in enumerate(items):
        if item in selected:
            row = by_id[item]
            features = _features(row, state["uses"], state["last_used"],
                                 state["clock"])
            action = row["proposed_action"]
            uses.append({
                "step": step,
                "item_id": item,
                "action": action,
                "features_q16": list(features),
            })
            state["uses"][item] += 1
            state["last_used"][item] = state["clock"]
        else:
            action = 0
        actions.append(action)
        public_trace.append({
            "step": step, "item_id": item,
            "selected": item in selected, "action": action,
        })
        state["clock"] += 1

    return {
        "schema": "yggdrasil.mr32p.policy-output.v1",
        "method": method,
        "selected_items": sorted(selected),
        "actions": actions,
        "public_trace": public_trace,
        "use_receipts": uses,
        "state_after_episode": state,
    }


def apply_post_episode_credits(message: dict) -> dict:
    _require_keys(message, {
        "schema", "operation", "method", "episode_terminal",
        "state", "use_receipts", "credits_q16",
    }, "LEARNER_MESSAGE_FIELDS")
    if message["schema"] != INPUT_SCHEMA or message["operation"] != "update":
        raise PolicyInputError("LEARNER_MESSAGE_SCHEMA_OR_OPERATION")
    method = message["method"]
    if method not in LEARNED:
        raise PolicyInputError("LEARNER_METHOD")
    if message["episode_terminal"] is not True:
        raise PolicyInputError("FEEDBACK_BEFORE_TERMINAL")
    state = _validate_state(message["state"])
    receipts, credits = message["use_receipts"], message["credits_q16"]
    if not isinstance(receipts, list) or len(receipts) != ACTIVE:
        raise PolicyInputError("LEARNER_USE_RECEIPTS")
    if not isinstance(credits, list) or len(credits) != ACTIVE:
        raise PolicyInputError("LEARNER_CREDIT_COUNT")
    seen = set()
    normalized = []
    for use, credit in zip(receipts, credits):
        _require_keys(use, {
            "step", "item_id", "action", "features_q16"
        }, "LEARNER_USE_FIELDS")
        step, item, action = use["step"], use["item_id"], use["action"]
        if (isinstance(step, bool) or not isinstance(step, int)
                or not 0 <= step < TOTAL or step in seen):
            raise PolicyInputError("LEARNER_STEP_RANGE_OR_DUPLICATE")
        seen.add(step)
        if isinstance(item, bool) or not isinstance(item, int) or not 0 <= item < TOTAL:
            raise PolicyInputError("LEARNER_ITEM_RANGE")
        if isinstance(action, bool) or action not in (0, 1):
            raise PolicyInputError("LEARNER_ACTION_RANGE")
        if isinstance(credit, bool) or not isinstance(credit, int):
            raise PolicyInputError("LEARNER_CREDIT_INTEGER")
        if not -Q <= credit <= Q:
            raise PolicyInputError("LEARNER_CREDIT_RANGE")
        features = use["features_q16"]
        if (not isinstance(features, list) or len(features) != 6
                or any(isinstance(x, bool) or not isinstance(x, int)
                       for x in features)):
            raise PolicyInputError("LEARNER_FEATURE_VECTOR")
        normalized.append((step, item, tuple(features), credit))
    normalized.sort(key=lambda row: row[0])

    for step, item, features, credit in normalized:
        prediction = _predict(state["weights"], features)
        error = credit - prediction
        for index, feature in enumerate(features):
            change = (5243 * error * feature) // (Q * Q)
            state["weights"][index] = max(
                -4 * Q, min(4 * Q, state["weights"][index] + change)
            )
    return {
        "schema": "yggdrasil.mr32p.learner-output.v1",
        "method": method,
        "weights": state["weights"],
        "weights_sha256": hashlib.sha256(
            json.dumps(state["weights"], separators=(",", ":")).encode("ascii")
        ).hexdigest(),
    }


def main() -> int:
    try:
        raw = sys.stdin.read()
        message = json.loads(raw)
        if not isinstance(message, dict):
            raise PolicyInputError("POLICY_MESSAGE_NOT_OBJECT")
        if message.get("operation") == "act":
            result = select_and_act(message)
        elif message.get("operation") == "update":
            result = apply_post_episode_credits(message)
        else:
            raise PolicyInputError("POLICY_OPERATION")
        sys.stdout.write(json.dumps(result, sort_keys=True, separators=(",", ":")))
        sys.stdout.write("\n")
        return 0
    except Exception as exc:
        sys.stderr.write(type(exc).__name__ + ":" + str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
