"""CAP04 source-shortcut control audit, ENGINEERING ONLY, not a research result.

Each arm independently fits online Beta counts to the same two public witnessed
engineering tapes, with score-before-observe and correct reward-stage timing.
Source identity is available ONLY to explicitly labeled invalid oracle arms.
No registered research seed, private source law, hidden phase, or future outcome.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
from collections import defaultdict

from yggdrasil.native_context_basis import canonical, digest

SCHEMA = "yggdrasil.cap04.shortcut-control-audit.v1"
FIXTURES = ("cap04-source-structure-fixture-a", "cap04-source-structure-fixture-b")
ARMS = (
    "action_only_beta", "clock_only_beta", "clock_action_beta",
    "public_state_action_beta", "prior_action_beta",
    "two_back_history_sham_beta", "source_identity_only_oracle_beta",
    "source_identity_action_oracle_beta",
)
DIAGNOSTIC_ORACLES = ("source_identity_only_oracle_beta",
                      "source_identity_action_oracle_beta")
PHASE_WINDOWS = {"novel": (48, 72), "cold_return": (72, 96), "pooled": (48, 96)}
SOURCE_PATH = Path(__file__).resolve().parent / "prospective_source.py"


def require(ok, reason):
    if not ok:
        raise ValueError("CAP04_SHORTCUT_AUDIT_" + reason)


def source_module():
    spec = importlib.util.spec_from_file_location("cap04_shortcut_fixture", SOURCE_PATH)
    require(spec is not None and spec.loader is not None, "SOURCE_IMPORT")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    require(tuple(mod.ENGINEERING_FIXTURES) == FIXTURES, "FIXTURE_IDS")
    require(mod.EPISODES == 96 and mod.BOUNDARIES == (0, 32, 72, 96),
            "BOUNDARIES")
    return mod


def valid_bits(seq, length):
    return (type(seq) in (tuple, list) and len(seq) == length and
            all(type(z) is int and z in (0, 1) for z in seq))


def public_event(row):
    require(type(row) is dict and
            set(row) == {"id", "views", "action", "s2", "y", "post"},
            "PUBLIC_FIELDS")
    views, action, post = row["views"], row["action"], row["post"]
    require(type(views) in (tuple, list) and len(views) == 2 and
            valid_bits(views[0], 2) and valid_bits(views[1], 2) and
            views[0][1] == views[1][0], "PUBLIC_VIEWS")
    require(valid_bits(action, 2) and valid_bits(post, 3) and
            type(row["s2"]) is int and row["s2"] in (0, 1) and
            type(row["y"]) is int and row["y"] in (0, 1) and
            post[1] == row["s2"], "PUBLIC_OUTCOME")
    require(type(row["id"]) is str and
            re.fullmatch(r"[0-9a-f]{64}", row["id"]) is not None,
            "PUBLIC_ID")


class ShortcutControls:
    """Explicitly scoped predictive controls; source-ID arms are oracles."""
    def __init__(self):
        self._events = {f: [] for f in FIXTURES}
        self._seen = set()
        self._counts = {stage: {name: {} for name in ARMS}
                        for stage in ("transition", "reward")}

    def _keys(self, fixture, t, views, action, stage, sensor):
        require(type(fixture) is str and fixture in FIXTURES, "FIXTURE")
        require(type(t) is int and t == len(self._events[fixture])
                and 0 <= t < 96, "CLOCK")
        require(type(views) in (tuple, list) and len(views) == 2 and
                valid_bits(views[0], 2) and valid_bits(views[1], 2) and
                views[0][1] == views[1][0] and valid_bits(action, 2),
                "PUBLIC_INPUT")
        require(stage in ("transition", "reward"), "STAGE")
        if stage == "transition":
            require(sensor is None, "FUTURE_SENSOR")
        else:
            require(type(sensor) is int and sensor in (0, 1),
                    "WITNESSED_SENSOR")
        a = tuple(action)
        state = (views[0][0], views[0][1], views[1][1])
        past = self._events[fixture]
        prior = tuple(past[-1]["action"]) if past else None
        sham = tuple(past[-2]["action"]) if len(past) > 1 else None
        keys = {
            "action_only_beta": (a,),
            "clock_only_beta": (t % 16,),
            "clock_action_beta": (t % 16, a),
            "public_state_action_beta": (state, a),
            "prior_action_beta": (state, a, prior),
            "two_back_history_sham_beta": (state, a, sham),
            "source_identity_only_oracle_beta": (fixture,),
            "source_identity_action_oracle_beta": (fixture, a),
        }
        require(set(keys) == set(ARMS), "COMPLETE_ARMS")
        # The actual measured current s2 may enter every arm's stage-2
        # forecast; stage 1 cannot access it.
        extra = (sensor,) if stage == "reward" else ()
        return {name: repr(key + extra) for name, key in keys.items()}

    def forecast(self, fixture, t, views, action, stage, witnessed_s2=None):
        keys = self._keys(fixture, t, views, action, stage, witnessed_s2)
        out = {}
        for name, key in keys.items():
            positive, total = self._counts[stage][name].get(key, (0, 0))
            out[name] = (positive + 1.0) / (total + 2.0)
        return out

    def observe(self, fixture, t, row):
        public_event(row)
        require((fixture, row["id"]) not in self._seen, "DUPLICATE")
        transition = self._keys(fixture, t, row["views"], row["action"],
                                "transition", None)
        reward = self._keys(fixture, t, row["views"], row["action"],
                            "reward", row["s2"])
        for stage, keys, value in (("transition", transition, row["s2"]),
                                   ("reward", reward, row["y"])):
            for name, key in keys.items():
                yes, n = self._counts[stage][name].get(key, (0, 0))
                self._counts[stage][name][key] = (yes + value, n + 1)
        self._events[fixture].append(row)
        self._seen.add((fixture, row["id"]))
        return self

    def checkpoint(self):
        return canonical({"schema": SCHEMA, "tapes":
                          {f: self._events[f] for f in FIXTURES}})

    @classmethod
    def restore(cls, raw, expected_sha):
        require(type(raw) is bytes and digest(raw) == expected_sha,
                "COLD_HASH")
        try:
            doc = json.loads(raw.decode("ascii"))
            require(type(doc) is dict and
                    set(doc) == {"schema", "tapes"} and
                    doc["schema"] == SCHEMA and
                    set(doc["tapes"]) == set(FIXTURES) and
                    canonical(doc) == raw, "COLD_SCHEMA")
            result = cls()
            # The same sequential public history is reconstructed without
            # learning from any future labels during readout.
            for t in range(max(map(len, doc["tapes"].values()))):
                for fixture in FIXTURES:
                    if t < len(doc["tapes"][fixture]):
                        result.observe(fixture, t, doc["tapes"][fixture][t])
            require(result.checkpoint() == raw, "COLD_REPLAY")
            return result
        except (ValueError, TypeError, KeyError, IndexError,
                UnicodeError, ArithmeticError, OverflowError) as exc:
            raise ValueError("CAP04_SHORTCUT_AUDIT_COLD_REJECTED") from exc


def audit_engineering_fixtures():
    """No scientific GO/NO-GO classification; purely structural diagnostics."""
    source = source_module()
    tapes = {f: source.engineering_fixture(f) for f in FIXTURES}
    require(all(len(x) == 96 for x in tapes.values()), "TAPE_LENGTH")
    model = ShortcutControls()
    scored = {f: [] for f in FIXTURES}
    for t in range(96):
        for fixture in FIXTURES:
            row = tapes[fixture][t]
            before = model.checkpoint()
            s1 = model.forecast(fixture, t, row["views"], row["action"],
                                "transition")
            s2 = model.forecast(fixture, t, row["views"], row["action"],
                                "reward", row["s2"])
            require(before == model.checkpoint(), "FORECAST_MUTATED")
            brier = {arm: ((s1[arm] - row["s2"]) ** 2 +
                           (s2[arm] - row["y"]) ** 2) / 2.0 for arm in ARMS}
            scored[fixture].append(brier)
            model.observe(fixture, t, row)
    receipt = {"schema": SCHEMA,
               "evidence_class": "ENGINEERING_FIXTURE_DIAGNOSTIC_ONLY",
               "fixture_ids": list(FIXTURES), "arms": list(ARMS),
               "invalid_oracle_arms": list(DIAGNOSTIC_ORACLES),
               "source_hashes": {f: digest(canonical(tapes[f])) for f in FIXTURES},
               "fitted_events": {f: len(tapes[f]) for f in FIXTURES},
               "phase_mean_brier": {}, "final_cold_sha256": digest(model.checkpoint())}
    for phase, (start, end) in PHASE_WINDOWS.items():
        receipt["phase_mean_brier"][phase] = {}
        for arm in ARMS:
            receipt["phase_mean_brier"][phase][arm] = (
                sum(scored[f][t][arm] for f in FIXTURES
                    for t in range(start, end)) /
                (len(FIXTURES) * (end - start)))
    cold = ShortcutControls.restore(model.checkpoint(), digest(model.checkpoint()))
    require(cold.checkpoint() == model.checkpoint(), "COLD_DIFF")
    return receipt
