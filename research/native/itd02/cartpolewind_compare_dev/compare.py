"""Source-only, public-wire development comparator. No original-world execution.

Three architecture-distinct learners consume identical CartPoleWind-shaped
PUBLIC transitions. Literal test rows are synthetic protocol fixtures, not a
replacement environment and not scientific fitness evidence.
"""
import hashlib
import json
import math

SCHEMA = "ygg.itd02.cartpolewind.three_arm_dev_model.v1"
ARMS = ("native", "tabular", "recurrent")
FEATURE_CAP = 5.0
MAX_ABS_OBS = 1e6


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _observation(value):
    if type(value) not in (tuple, list) or len(value) != 4:
        raise ValueError("NOT_FOUR_PUBLIC_OBSERVABLES")
    if any(type(x) not in (float, int) or not math.isfinite(x)
           or abs(x) > MAX_ABS_OBS for x in value):
        raise ValueError("INVALID_PUBLIC_OBSERVATION")
    return tuple(float(x) for x in value)


def _event(record):
    if type(record) is not dict or set(record) != {
        "observation", "action", "next_observation",
        "reward", "terminated", "truncated"
    }:
        raise ValueError("PRIVATE_OR_MISSING_WIRE_FIELD")
    before = _observation(record["observation"])
    after = _observation(record["next_observation"])
    action, reward = record["action"], record["reward"]
    if (type(action) is not int or action not in (0, 1)
            or type(reward) not in (float, int)
            or not math.isfinite(reward) or abs(reward) > 10000
            or type(record["terminated"]) is not bool
            or type(record["truncated"]) is not bool):
        raise ValueError("INVALID_PUBLIC_ACTION_REWARD_OR_TERMINAL")
    return before, action, after, float(reward), (
        record["terminated"] or record["truncated"]
    )


def _clip(x, limit=FEATURE_CAP):
    return min(limit, max(-limit, x))


def _features(obs):
    # Fixed public observation normalization. No hidden physics/oracle values.
    x = tuple(_clip(z) for z in _observation(obs))
    return (1.0,) + x + tuple(_clip(z * z, 5) for z in x)


def _dot(w, phi):
    return sum(a * b for a, b in zip(w, phi))


class Model:
    """Generic frozen-schema model; no upstream modules or privileged API."""

    def __init__(self, arm):
        if arm not in ARMS:
            raise ValueError("UNSUPPORTED_ARM")
        self.arm = arm
        self.updates = 0
        self.action_calls = 0
        self.fast = {str(a): [0.0] * 9 for a in (0, 1)}
        self.slow = {str(a): [0.0] * 9 for a in (0, 1)}
        self.table = {}
        self.trace = [0.0] * 4
        self.recurrent = {str(a): [0.0] * 9 for a in (0, 1)}
        self._frozen_fit_sha256 = None  # Local evaluation guard, outside checkpoint schema.

    def _key(self, obs):
        # Tabular control discretizes PUBLIC inputs only, on fixed bins.
        edges = (-2.0, -1.0, -0.2, 0.2, 1.0, 2.0)
        return ",".join(str(sum(z >= edge for edge in edges)) for z in _observation(obs))

    def _q(self, obs, action):
        if self.arm == "native":
            phi = _features(obs)
            return .7 * _dot(self.fast[str(action)], phi) + .3 * _dot(self.slow[str(action)], phi)
        if self.arm == "tabular":
            return self.table.get(self._key(obs), [0.0, 0.0])[action]
        phi = (1.0,) + tuple(_clip(z) for z in _observation(obs)) + tuple(self.trace)
        return _dot(self.recurrent[str(action)], phi)

    def choose(self, observation):
        obs = _observation(observation)
        if (self._frozen_fit_sha256 is not None
                and self.fitted_parameter_sha256() != self._frozen_fit_sha256):
            raise ValueError("FROZEN_FIT_CHANGED")
        self.action_calls += 1
        return 0 if self._q(obs, 0) >= self._q(obs, 1) else 1

    def fitted_parameter_sha256(self):
        """Hash FIT parameters only, excluding live public history and counters."""
        if self.arm == "native":
            learned = {"fast": self.fast, "slow": self.slow}
        elif self.arm == "tabular":
            learned = {"table": self.table}
        else:
            learned = {"recurrent": self.recurrent}
        return hashlib.sha256(_canonical({"schema": SCHEMA,
            "arm": self.arm, "parameters": learned})).hexdigest()

    def start_frozen_evaluation(self, expected_weight_sha256, reset_trace=True):
        """The trusted evaluation owner must supply independently sealed FIT identity."""
        if (type(expected_weight_sha256) is not str
                or len(expected_weight_sha256) != 64
                or self.fitted_parameter_sha256() != expected_weight_sha256):
            raise ValueError("FITTED_WEIGHT_IDENTITY_MISMATCH")
        if type(reset_trace) is not bool:
            raise ValueError("INVALID_EVALUATION_HISTORY_RESET")
        if reset_trace:
            self.episode_boundary()
        self._frozen_fit_sha256 = expected_weight_sha256

    def frozen_public_return(self, next_observation, terminal=False, truncated=False):
        """After selected action, advance allowed recurrent public state without learning."""
        if self._frozen_fit_sha256 is None:
            raise ValueError("NOT_FROZEN_EVALUATION")
        if type(terminal) is not bool or type(truncated) is not bool:
            raise ValueError("INVALID_EVALUATION_TERMINAL")
        after = _observation(next_observation)
        if self.fitted_parameter_sha256() != self._frozen_fit_sha256:
            raise ValueError("FROZEN_FIT_CHANGED")
        if self.arm == "recurrent":
            self.trace = [0.0] * 4 if terminal or truncated else [
                _clip(.8 * prior + .2 * value)
                for prior, value in zip(self.trace, after)
            ]
        if self.fitted_parameter_sha256() != self._frozen_fit_sha256:
            raise ValueError("FROZEN_FIT_CHANGED")


    def observe(self, record):
        if self._frozen_fit_sha256 is not None:
            raise ValueError("FITTING_FORBIDDEN_DURING_EVALUATION")
        before, action, after, reward, terminal = _event(record)
        q_old = self._q(before, action)
        # Source-blind, bounded public one-step TD target; no oracle target.
        target = reward + (0.0 if terminal else .95 * max(
            self._q(after, 0), self._q(after, 1)))
        td = _clip(target - q_old, 1.0)
        key = str(action)
        if self.arm == "native":
            phi = _features(before)
            for j, f in enumerate(phi):
                self.fast[key][j] = _clip(self.fast[key][j] + .015 * td * f, 20.0)
                self.slow[key][j] = _clip(
                    .96 * self.slow[key][j] + .04 * self.fast[key][j], 20.0)
        elif self.arm == "tabular":
            row = self.table.setdefault(self._key(before), [0.0, 0.0])
            row[action] = _clip(row[action] + .12 * td, 20.0)
        else:
            phi = (1.0,) + tuple(_clip(z) for z in before) + tuple(self.trace)
            for j, f in enumerate(phi):
                self.recurrent[key][j] = _clip(
                    self.recurrent[key][j] + .015 * td * f, 20.0)
            self.trace = [0.0] * 4 if terminal else [
                _clip(.8 * prior + .2 * value) for prior, value
                in zip(self.trace, after)
            ]
        self.updates += 1

    def episode_boundary(self):
        self.trace = [0.0] * 4

    def checkpoint(self):
        body = {"schema": SCHEMA, "arm": self.arm,
                "updates": self.updates, "action_calls": self.action_calls,
                "fast": self.fast, "slow": self.slow, "table": self.table,
                "trace": self.trace, "recurrent": self.recurrent}
        raw = _canonical(body)
        if len(raw) > 262144:
            raise ValueError("DEVELOPMENT_CHECKPOINT_OVERSIZE")
        return _canonical({"body": body, "sha256": hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not 0 < len(raw) <= 262144:
            raise ValueError("CHECKPOINT_TYPE_OR_SIZE_INVALID")
        try:
            wire = json.loads(raw)
            if set(wire) != {"body", "sha256"}:
                raise ValueError("CHECKPOINT_ENVELOPE")
            body = wire["body"]
            if hashlib.sha256(_canonical(body)).hexdigest() != wire["sha256"]:
                raise ValueError("CHECKPOINT_HASH")
            if set(body) != {"schema", "arm", "updates", "action_calls",
                              "fast", "slow", "table", "trace", "recurrent"}:
                raise ValueError("CHECKPOINT_FIELDS")
            if body["schema"] != SCHEMA or body["arm"] not in ARMS:
                raise ValueError("CHECKPOINT_SCHEMA")
            if (type(body["updates"]) is not int or body["updates"] < 0
                    or type(body["action_calls"]) is not int
                    or body["action_calls"] < 0):
                raise ValueError("CHECKPOINT_COUNTS")
            obj = cls(body["arm"])
            for name in ("fast", "slow", "recurrent"):
                data = body[name]
                if type(data) is not dict or set(data) != {"0", "1"}:
                    raise ValueError("CHECKPOINT_ACTIONS")
                if any(type(v) is not list or len(v) != 9
                       or any(type(x) not in (int, float) or not math.isfinite(x)
                              or abs(x) > 20 for x in v) for v in data.values()):
                    raise ValueError("CHECKPOINT_WEIGHT_CORRUPTION")
            if (type(body["trace"]) is not list or len(body["trace"]) != 4
                    or any(type(x) not in (int, float) or not math.isfinite(x)
                           or abs(x) > 5 for x in body["trace"])
                    or type(body["table"]) is not dict or len(body["table"]) > 10000):
                raise ValueError("CHECKPOINT_TRACE_OR_TABLE")
            for k, row in body["table"].items():
                if (type(k) is not str or len(k) > 20 or
                        type(row) is not list or len(row) != 2 or
                        any(type(x) not in (int, float) or not math.isfinite(x)
                            or abs(x) > 20 for x in row)):
                    raise ValueError("CHECKPOINT_TABLE_ENTRY")
            for name in ("fast", "slow", "recurrent", "trace", "table",
                         "updates", "action_calls"):
                setattr(obj, name, body[name])
            return obj
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            raise ValueError("UNTRUSTED_CHECKPOINT") from exc


def fit_identical_public_replay(arms, records):
    """Fit exactly three model arms on identical ordered public records.

    Every record is validated in advance; a partially invalid batch never fits.
    Caller must freeze source/budgets separately before ANY real episodes.
    """
    if (type(arms) not in (tuple, list) or len(arms) != 3
            or {getattr(a, "arm", None) for a in arms} != set(ARMS)
            or any(type(a) is not Model or a.updates != 0 for a in arms)):
        raise ValueError("THREE_FRESH_ARMS_REQUIRED")
    if type(records) not in (tuple, list) or not 1 <= len(records) <= 10000:
        raise ValueError("INVALID_REPLAY_BUDGET")
    # Prevalidate exact allowed public field names, values and shape.
    for row in records:
        _event(row)
    for row in records:
        for arm in arms:
            arm.observe(row)
        if row["terminated"] or row["truncated"]:
            for arm in arms:
                arm.episode_boundary()
    if len({a.updates for a in arms}) != 1:
        raise AssertionError("PUBLIC_INTERACTION_PARITY_BROKEN")
    return {"public_updates_per_arm": len(records),
            "checkpoint_bytes": {a.arm: len(a.checkpoint()) for a in arms},
            "original_source_episodes": 0,
            "scientific_go": False,
            "data_label": "SYNTHETIC_PROTOCOL_ONLY_NO_BENCHMARK"}
