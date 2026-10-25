"""Y095 pre-freeze *mechanism only*: frozen retained-majority decision gate.

The CKB-plane R189 / R180 design authority is unchanged. This module implements
the three deterministic consumer state projections, but deliberately contains
NO experiment runner, source acquisition, cohort builder, approval, or evaluation.
Only a separate CKB-approved, frozen, independently born/disjoint cohort may
be evaluated in a later qualified execution tranche.
"""

from __future__ import annotations

import math

EXPERIMENT = "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-MAJORITY-DECISION-GATE-095"
ARMS = ("A0", "A1", "A2")
CAPACITY = (16, 7, 9)
LEARNED_SCALARS = 0
EXTERNAL_MODEL_CALLS = 0
CONTINUOUS_FIELDS = ("total", "best_count", "consistency", "utility")
DISCRETE_FIELDS = ("best", "map_best")


class InvalidConsumerState(ValueError):
    """Reject malformed or ambiguous source state instead of silently coercing it."""


def _strict_int(value: object, name: str) -> int:
    if type(value) is not int:
        raise InvalidConsumerState("Y095_NOT_EXACT_INTEGER_" + name)
    return value


def _validate(target: dict, retained: dict) -> None:
    if not isinstance(target, dict) or not isinstance(retained, dict):
        raise InvalidConsumerState("Y095_INVALID_STATE_TYPE")
    for label, state in (("target", target), ("retained", retained)):
        if any(field not in state for field in (*CONTINUOUS_FIELDS, *DISCRETE_FIELDS, "key")):
            raise InvalidConsumerState("Y095_MISSING_" + label + "_FIELDS")
        _strict_int(state["best"], label + "_best")
        _strict_int(state["map_best"], label + "_map_best")
        total = _strict_int(state["total"], label + "_total")
        count = _strict_int(state["best_count"], label + "_best_count")
        if total <= 0 or count < 0 or count > total:
            raise InvalidConsumerState("Y095_INVALID_" + label + "_COUNTS")
        for key in ("consistency", "utility"):
            value = state[key]
            if type(value) not in (int, float) or not math.isfinite(value):
                raise InvalidConsumerState("Y095_NONFINITE_" + label + "_" + key)
        if not isinstance(state["key"], (tuple, list)) or not state["key"]:
            raise InvalidConsumerState("Y095_INVALID_" + label + "_KEY")
        if any(type(v) is not int for v in state["key"]):
            raise InvalidConsumerState("Y095_INVALID_" + label + "_KEY_MEMBER")


def project_consumer(target: dict, retained: dict, arm_id: str) -> dict:
    """Return a NEW projected state without changing any source state.

    A0: exact Y094 negative-parent endpoint (retained continuous, target discrete).
    A1: existing Y094 retained endpoint (retained continuous/discrete).
    A2: only source-derived strict-majority AND coherence may choose retained.best;
        otherwise choose target.best. Both projected decision fields equal the choice.

    Retained key, continuous fields and all other retained fields stay unchanged.
    """
    if arm_id not in ARMS:
        raise InvalidConsumerState("Y095_UNDECLARED_ARM")
    _validate(target, retained)
    out = dict(retained)
    if arm_id == "A0":
        out["best"] = target["best"]
        out["map_best"] = target["map_best"]
    elif arm_id == "A1":
        out["best"] = retained["best"]
        out["map_best"] = retained["map_best"]
    else:
        majority = 2 * retained["best_count"] > retained["total"]
        coherent = retained["best"] == retained["map_best"]
        selected = retained["best"] if majority and coherent else target["best"]
        out["best"] = selected
        out["map_best"] = selected
    return out
