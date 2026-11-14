"""WSP-100 wider source-blind DEV identifiability falsifier.

2048 programs, strictly containing the original 256-program DEV fixture class.
This module never imports fixture.py or its sampled program, hidden state,
transition function, target truth or any original first-use generator.
"""
from __future__ import annotations

import hashlib
import json
from itertools import product

SCHEMA = "wsp100.dev-broad-audit.v1"
ALL_PROGRAMS = tuple(product(range(4), range(4), range(4), range(4), range(4), range(2)))
assert len(ALL_PROGRAMS) == 2048


def _hash(payload):
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _rank(fid, stream, index):
    return int.from_bytes(hashlib.sha256(
        f"WSP100|v1|FIXTURE|{fid}|{stream}|{index}".encode("ascii")
    ).digest(), "big")


def _digits(code):
    return tuple((code >> (2 * k)) & 3 for k in range(6))


def _code(x):
    return sum(value << (2 * i) for i, value in enumerate(x))


def _visible(x):
    if not isinstance(x, (tuple, list)) or len(x) != 6 or any(
        type(v) is not int or not 0 <= v <= 3 for v in x
    ):
        raise ValueError("source must contain six four-valued visible channels")
    return tuple(x)


def _action(a):
    if type(a) is not int or not 0 <= a < 4:
        raise ValueError("invalid action")
    return a


def _primitive(f, a, b):
    if f == 0:
        return (a + b) & 3
    if f == 1:
        return a ^ b
    if f == 2:
        return a if (b & 1) == 0 else 3 - a
    if f == 3:
        return (a * b + b) & 3
    raise ValueError("invalid operator")


def _step(program, x, hidden, action):
    f, w, t, p, shift, combiner = program
    y = []
    for i in range(6):
        a = x[(i + w) % 6]
        b = x[(i + 1 + w) % 6]
        first = _primitive(f, a, b)
        second = _primitive((f + 1 + (i % 3) + shift) % 4,
                            first, x[(i + 3) % 6])
        second = (second + p * (1 + (i % 2))) & 3
        if i < 4:
            if combiner == 0:
                second = (second + hidden[i % 2]) & 3
            else:
                second ^= hidden[i % 2]
        y.append(second)
    nxt_h = list(hidden)
    for j in range(2):
        parity = (x[(w + j) % 6] + x[(w + j + 2) % 6] + p + j) & 1
        if action == (t + j) % 4 and parity:
            nxt_h[j] = (hidden[j] + 1 + ((p + j) % 3)) & 3
    return tuple(y), tuple(nxt_h)


def validate_source(bundle):
    if not isinstance(bundle, dict) or set(bundle) != {
        "schema", "fixture_id", "passive", "active", "random", "source_sha256"
    }:
        raise ValueError("bad source fields")
    fid = bundle["fixture_id"]
    if (type(fid) is not int or not 0 <= fid < 8 or
            bundle["schema"] != "wsp100.fixture-source.v1"):
        raise PermissionError("only already published DEV fixture source is admissible")
    for name, required in (("passive", 24), ("active", 8), ("random", 8)):
        episodes = bundle[name]
        if not isinstance(episodes, (tuple, list)) or len(episodes) != required:
            raise ValueError("source episode budget or arm mismatch")
        for index, episode in enumerate(episodes):
            if not isinstance(episode, (tuple, list)) or len(episode) != 4:
                raise ValueError("source episode length mismatch")
            expected_initial = _digits(_rank(
                fid, "PASSIVE-INIT" if name == "passive" else "INVESTIGATE-INIT", index
            ) % 4096)
            if _visible(episode[0][0]) != expected_initial:
                raise ValueError("source initial-state selector drift")
            prior = None
            for step, row in enumerate(episode):
                if not isinstance(row, (tuple, list)) or len(row) != 4:
                    raise ValueError("unregistered source row")
                x, action, y, reward = row
                x, y = _visible(x), _visible(y)
                _action(action)
                if prior is not None and x != prior:
                    raise ValueError("source trajectory discontinuity")
                if type(reward) is not int or reward != int((y[0] + y[1]) % 4 == 3):
                    raise ValueError("inconsistent source visible reward")
                if name in ("passive", "random"):
                    kind = "PASSIVE-ACT" if name == "passive" else "RANDOM-ACT"
                    if action != _rank(fid, kind, 4 * index + step) % 4:
                        raise ValueError("frozen passive/random action selection violated")
                prior = y
    if any(a[0][0] != r[0][0] for a, r in zip(bundle["active"], bundle["random"])):
        raise ValueError("active/random initial worlds not matched")
    payload = {k: bundle[k] for k in ("schema", "fixture_id", "passive", "active", "random")}
    if bundle["source_sha256"] != _hash(payload):
        raise ValueError("source digest mismatch")
    return True


def validate_plan(bundle, plan):
    validate_source(bundle)
    if not isinstance(plan, dict) or set(plan) != {
        "schema", "fixture_id", "source_sha256", "targets", "plan_sha256"
    }:
        raise ValueError("invalid plan fields")
    if (plan["schema"] != "wsp100.fixture-heldout-plan.v1" or
            plan["fixture_id"] != bundle["fixture_id"] or
            plan["source_sha256"] != bundle["source_sha256"]):
        raise ValueError("source/target identity mismatch")
    if len(plan["targets"]) != 12 or plan["plan_sha256"] != _hash(plan["targets"]):
        raise ValueError("plan count or digest mismatch")
    starts = {_visible(ep[0][0]) for arm in ("passive", "active", "random")
              for ep in bundle[arm]}
    fid = bundle["fixture_id"]
    unused = [k for k in range(4096) if _digits(k) not in starts]
    unused.sort(key=lambda code: _rank(fid, "HELDOUT-INIT", code))
    expected = []
    for index, code in enumerate(unused[:12]):
        a = _rank(fid, "HELDOUT-A", index) % 4
        b = (a + 1 + _rank(fid, "HELDOUT-B", index) % 3) % 4
        c = _rank(fid, "HELDOUT-C", 3 * index + 1) % 4
        d = _rank(fid, "HELDOUT-C", 3 * index + 2) % 4
        expected.append((_digits(code), (a, c, d), (b, c, d)))
    if [tuple((_visible(x), tuple(a), tuple(b))) for x, a, b in plan["targets"]] != expected:
        raise ValueError("heldout target selection or counterfactual actions drift")
    return True


def fits(program, episodes):
    """Independent program consistency using ONLY visible observations."""
    for episode in episodes:
        if len(episode) != 4:
            raise ValueError("wrong episode length")
        hidden = (0, 0)
        current = _visible(episode[0][0])
        for row in episode:
            x, action, y, reward = row
            if _visible(x) != current:
                raise ValueError("invalid episode transition")
            _action(action)
            observed = _visible(y)
            predicted, hidden = _step(program, current, hidden, action)
            if predicted != observed or reward != int((predicted[0] + predicted[1]) % 4 == 3):
                return False
            current = predicted
    return True


def version_space(episodes):
    episodes = tuple(episodes)
    return tuple(p for p in ALL_PROGRAMS if fits(p, episodes))


def _rollout(program, initial, actions):
    current, h = _visible(initial), (0, 0)
    prediction = []
    for action in actions:
        _action(action)
        current, h = _step(program, current, h, action)
        prediction.append(current)
    return tuple(prediction)


def identifiability(survivors, targets):
    targets = tuple(targets)
    if not survivors:
        return {"classification": "INVALID_EMPTY_VERSION_SPACE",
                "survivors": 0, "identifiable": 0, "slots": 0, "fraction": None}
    if len(targets) != 12:
        raise ValueError("twelve registered target starts required")
    slots = len(targets) * 2 * 3 * 6
    invariant = [True] * slots
    reference = None
    for program in survivors:
        predicted = []
        for initial, left, right in targets:
            for seq in (left, right):
                for state in _rollout(program, initial, seq):
                    predicted.extend(state)
        if len(predicted) != slots:
            raise ValueError("prediction slot drift")
        if reference is None:
            reference = predicted
        else:
            invariant = [same and a == b
                         for same, a, b in zip(invariant, reference, predicted)]
    n = sum(invariant)
    return {"classification": "DEV_WIDER_CATALOGUE_ONLY",
            "survivors": len(survivors), "identifiable": n,
            "slots": slots, "fraction": n / slots}


def audit(bundle, plan):
    validate_plan(bundle, plan)
    observed = tuple(bundle["passive"]) + tuple(bundle["active"])
    survived = version_space(observed)
    answer = identifiability(survived, plan["targets"])
    return {
        "schema": SCHEMA, "fixture_id": bundle["fixture_id"],
        "source_sha256": bundle["source_sha256"],
        "plan_sha256": plan["plan_sha256"],
        "catalogue": len(ALL_PROGRAMS),
        **answer,
        "scientific_superiority": False,
        "original_worlds_consumed": False,
    }
