"""C26: source-only frozen-FIT action identifiability and strict public-event gate.

No MiniGrid/gym import, environment constructor, reset, step, or episode.
Checking a synthetically authored envelope never constitutes source testimony.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P = json.loads((HERE / "PREREG.json").read_text(encoding="utf-8"))


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\\0" + raw).hexdigest()


def checked_original(path: str, expected: str) -> bytes:
    data = (ROOT / path).read_bytes()
    if git_blob_sha(data) != expected:
        raise ValueError("SOURCE_IDENTITY_DRIFT:" + path)
    return data


def certify_frozen_selected_fit() -> dict:
    """Prove the locked selector admits no turn outcomes to shared 12-row FIT."""
    original = checked_original(P["selected_fit_program"], P["selected_fit_program_blob"]).decode("utf-8")
    old = json.loads(checked_original(P["selected_fit_protocol"], P["selected_fit_protocol_blob"]))
    c25 = json.loads(checked_original(P["r7c25_protocol"], P["r7c25_protocol_blob"]))
    if old["roles"]["fit_steps_per_family"] != 2400:
        raise ValueError("FIT_OBSERVATION_ROLE_DRIFT")
    if "earliest four actually successful legal forward" not in old["roles"]["fit_select"]:
        raise ValueError("FIT_POSITIVE_ROLE_DRIFT")
    if "first eight physically blocked public forward" not in old["roles"]["fit_select"]:
        raise ValueError("FIT_NEGATIVE_ROLE_DRIFT")
    if c25["fit"]["same_12_original_actions"] is not True:
        raise ValueError("C25_FIT_ROLE_DRIFT")
    if c25["fit"]["expected_fit_sha256"] != "4e4e9446169f61a7d1a0398b4fff2d0e31510356111c2cc59fdbeca899f6ce60":
        raise ValueError("C25_FIT_IDENTITY_DRIFT")
    tree = ast.parse(original)
    fit = next((x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "fit_data"), None)
    if fit is None:
        raise ValueError("FIT_SELECTOR_ABSENT")
    # Audited under source blob identity, these exact AST locations describe
    # a single common a!=2/continue gate before BOTH returned categories.
    gates = [n for n in ast.walk(fit) if isinstance(n, ast.If)
             and isinstance(n.test, ast.Compare)
             and isinstance(n.test.left, ast.Name) and n.test.left.id == "a"
             and len(n.test.ops) == 1 and isinstance(n.test.ops[0], ast.NotEq)
             and len(n.test.comparators) == 1
             and isinstance(n.test.comparators[0], ast.Constant)
             and type(n.test.comparators[0].value) is int and n.test.comparators[0].value == 2
             and len(n.body) == 1 and isinstance(n.body[0], ast.Continue)]
    selectors = [n for n in ast.walk(fit)
                 if isinstance(n, ast.Assign) and len(n.targets) == 1
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "selected"
                 and isinstance(n.value, ast.BinOp) and isinstance(n.value.op, ast.Add)
                 and isinstance(n.value.right, ast.Name) and n.value.right.id == "blocked"
                 and isinstance(n.value.left, ast.ListComp)]
    if len(gates) != 1 or len(selectors) != 1:
        raise ValueError("UNRECOGNIZED_FIT_SELECTOR")
    if ast.unparse(selectors[0].value.left) != "[movements[d] for d in range(4)]":
        raise ValueError("FIT_MOVEMENT_SELECTOR_CHANGED")
    frozen = {"0": 0, "1": 0, "2": 12}
    if frozen != P["selected_fit_action_counts"] or P["selected_fit_count"] != 12:
        raise ValueError("FIT_DECLARED_ACTION_COVERAGE_DRIFT")
    return {
        "schema": "itd02.c26.frozen-selected-fit-certificate.v1",
        "source_selector_blob": P["selected_fit_program_blob"],
        "source_upstream": P["source_original"],
        "selected_actions": frozen,
        "observed_legal_turn_effects_in_selected_fit": 0,
        "learnt_turn_value_identifiable_from_selected_fit_alone": False,
        "verdict": "NO_GO_SELECTED_FIT_LACKS_TURN_OUTCOMES",
        "original_source_episodes_executed_by_this_certificate": 0,
    }


PUBLIC_FIELDS = frozenset(("x", "y", "goal_x", "goal_y", "direction", "front_blocked"))
EVENT_FIELDS = frozenset(("episode", "seq", "before", "action", "after", "reward", "terminal"))


def _public(raw: object) -> dict:
    if type(raw) is not dict or set(raw) != PUBLIC_FIELDS:
        raise ValueError("NONPUBLIC_STATE_OR_METADATA")
    for name in ("x", "y", "goal_x", "goal_y", "direction"):
        if type(raw[name]) is not int:
            raise ValueError("NONINTEGER_PUBLIC_COMPONENT")
    if not all(0 <= raw[k] <= 31 for k in ("x", "y", "goal_x", "goal_y")):
        raise ValueError("PUBLIC_COORDINATE_OUT_OF_BOUNDS")
    if raw["direction"] not in range(4) or type(raw["front_blocked"]) is not bool:
        raise ValueError("INVALID_PUBLIC_DIRECTION_OR_FRONT")
    return raw


def certify_candidate_event_coverage(events: list[dict]) -> dict:
    """Structural source-shaped unit gate; input is NOT authenticated original source.

    Actual source evidence additionally requires original-owner signed FIT roles,
    frozen episode IDs, an unbroken action/after-event channel and full budget.
    """
    if type(events) is not list or not 0 < len(events) <= 4096:
        raise ValueError("FIT_EVENT_BUDGET_OR_TYPE")
    counts = Counter()
    last_seq: dict[str, int] = {}
    for ev in events:
        if type(ev) is not dict or set(ev) != EVENT_FIELDS:
            raise ValueError("NONPUBLIC_EVENT_OR_METADATA")
        if type(ev["episode"]) is not str or not ev["episode"] or len(ev["episode"]) > 128:
            raise ValueError("INVALID_EPISODE_ID")
        if type(ev["seq"]) is not int or ev["seq"] != last_seq.get(ev["episode"], -1) + 1:
            raise ValueError("DUPLICATE_OUT_OF_ORDER_OR_MISSING_ACTION_RETURN")
        if type(ev["action"]) is not int or ev["action"] not in (0, 1, 2):
            raise ValueError("ILLEGAL_SELECTED_ACTION")
        if type(ev["reward"]) not in (float, int) or not math.isfinite(ev["reward"]):
            raise ValueError("NONFINITE_OR_MALFORMED_REWARD")
        if type(ev["terminal"]) is not bool:
            raise ValueError("MALFORMED_TERMINATION")
        before = _public(ev["before"])
        after = _public(ev["after"])
        if (before["goal_x"], before["goal_y"]) != (after["goal_x"], after["goal_y"]):
            raise ValueError("PRIVILEGED_OR_CHANGED_GOAL")
        action = ev["action"]
        if action in (0, 1):
            expected = (before["direction"] + (-1 if action == 0 else 1)) % 4
            if (before["x"], before["y"]) != (after["x"], after["y"]) or after["direction"] != expected:
                raise ValueError("TURN_RETURN_NOT_SOURCE_LEGAL")
        elif after["direction"] != before["direction"] or (
            abs(after["x"] - before["x"]) + abs(after["y"] - before["y"]) > 1
        ):
            raise ValueError("FORWARD_RETURN_NOT_SOURCE_LEGAL")
        counts[action] += 1
        last_seq[ev["episode"]] = ev["seq"]
    return {
        "schema": "itd02.c26.action-family-coverage-only.v1",
        "selected_legal_action_counts": {str(a): counts[a] for a in (0, 1, 2)},
        "source_event_authenticity": "UNVERIFIED_SOURCE_FREE_INPUT",
        "action_family_coverage": all(counts[a] > 0 for a in (0, 1, 2)),
        "learned_value_of_information": "NOT_TESTED",
        "science_admission": "DENIED",
    }


if __name__ == "__main__":
    print(json.dumps(certify_frozen_selected_fit(), sort_keys=True))
