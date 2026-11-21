"""TGAP23: non-privileged write protection crossed with posterior readout.

Independent, tokenless, source-free synthetic research only. Frozen BEFORE
implementation at 77140819dc564a7ce56095621db4e7861a7294b5.
Never mutates original Yggdrasil native model, canonical checkpoint, or owner.
"""
from __future__ import annotations

import copy
import json
import math
import time
from pathlib import Path

from tgap21_same_address_dev import (
    TwoSlotMemory, Uninformed, canonical, digest, witness, beta
)
from noisy_regime_memory_dev import (
    StationaryBeta, RollingBeta, ResetBeta, BayesianHMM
)

SCHEMA = "yggdrasil.tgap23.protected-write-factorial.dev.v1"
PROTOCOL = "yggdrasil.tgap23.nonprivileged-write-protection-factorial-frozen-dev.v1"
PREREG = "77140819dc564a7ce56095621db4e7861a7294b5"
SOURCE = "engineering_fixture_only"
FIT = (9501, 0, 24, 48, 72)
HELD = ((9601, 0, 12, 36), (9607, 1, 12, 36),
        (9613, 0, 17, 41), (9623, 1, 17, 41),
        (9631, 0, 21, 45), (9643, 1, 21, 45),
        (9653, 0, 9, 33),  (9661, 1, 9, 33),
        (9677, 0, 24, 48), (9689, 1, 24, 48))
ARMS = ("original_gate_fit", "original_soft_fit",
        "guarded_gate_fit", "guarded_soft_fit",
        "original_soft_no_fit", "guarded_soft_no_fit",
        "stationary_fit", "rolling_8_fit", "reset_fit",
        "bayes_hmm_fit", "source_only")
SOFT = frozenset(("original_soft_fit", "guarded_soft_fit",
                  "original_soft_no_fit", "guarded_soft_no_fit"))
WRITERS = frozenset(("original_gate_fit", "original_soft_fit",
                     "guarded_gate_fit", "guarded_soft_fit",
                     "original_soft_no_fit", "guarded_soft_no_fit"))
HAZARD = 1 / 16
SEAL_MIN = 8
SEAL_MARGIN = .2


def require(ok, code):
    if not ok:
        raise ValueError("YGG_TGAP23_" + code)


class GuardedTwoSlot:
    """Bounded archive of first confident A slot; admission only from outcomes.

    The old TGAP21 algorithm is run exactly once on each real witnessed event.
    When original old-slot storage has matured, later attempted writes into
    that slot are rolled back, preserving its first learned consequence counts.
    Other slots, public evidence order, and anomaly transitions are unchanged.
    No hidden regime label, switch time, or role enters this class.
    """
    def __init__(self):
        self.base = TwoSlotMemory()
        self.sealed = False
        self.snapshot = None
        self.suppressed = 0
        self.sealed_at = -1

    @property
    def slots(self):
        return self.base.slots

    @property
    def active(self):
        return self.base.active

    def slot_prediction(self, slot, action):
        return self.base.slot_prediction(slot, action)

    def predict(self, action):
        return self.base.predict(action)

    def observe(self, step, action, outcome, *, source_mode=SOURCE):
        require(source_mode == SOURCE, "SOURCE_MODE")
        pre_active = self.base.active
        self.base.observe(step, action, outcome, source_mode=source_mode)
        if self.sealed and pre_active == 0:
            self.base.slots[0] = copy.deepcopy(self.snapshot)
            self.suppressed += 1
        if not self.sealed:
            trials = sum(p[1] for p in self.base.slots[0])
            gap = abs(self.base.slot_prediction(0, 0) -
                      self.base.slot_prediction(0, 1))
            if trials >= SEAL_MIN and gap >= SEAL_MARGIN:
                self.sealed = True
                self.snapshot = copy.deepcopy(self.base.slots[0])
                self.sealed_at = step
        require(sum(p[1] for slot in self.base.slots for p in slot) +
                self.suppressed == self.base.total_witnesses, "CUSTODY")

    def new_public_world(self):
        other = copy.deepcopy(self)
        other.base = self.base.new_public_world()
        return other

    def checkpoint(self):
        raw = canonical({
            "schema": SCHEMA, "mode": SOURCE, "accepted_native": False,
            "science_pass": False, "base": json.loads(self.base.checkpoint()),
            "sealed": self.sealed, "snapshot": self.snapshot,
            "suppressed": self.suppressed, "sealed_at": self.sealed_at,
        })
        require(len(raw) <= 16384, "MEMORY_BUDGET")
        return raw

    @classmethod
    def restore(cls, raw, sha):
        require(type(raw) is bytes and 0 < len(raw) <= 16384 and
                type(sha) is str and digest(raw) == sha, "COLD_DIGEST")

        def no_duplicates(pairs):
            d = {}
            for k, v in pairs:
                require(k not in d, "DUPLICATE_JSON_KEY")
                d[k] = v
            return d

        try:
            d = json.loads(raw.decode("ascii"), object_pairs_hook=no_duplicates)
            require(type(d) is dict and set(d) == {
                "schema", "mode", "accepted_native", "science_pass", "base",
                "sealed", "snapshot", "suppressed", "sealed_at"
            } and d["schema"] == SCHEMA and d["mode"] == SOURCE
                    and d["accepted_native"] is False
                    and d["science_pass"] is False
                    and canonical(d) == raw, "COLD_SCHEMA")
            base = d["base"]
            require(type(base) is dict and set(base) == {
                "schema", "mode", "accepted_native", "scientific_gain_verified",
                "slots", "active", "recent", "since_switch", "next_step",
                "total_witnesses", "switches"
            } and base["schema"] ==
                    "yggdrasil.tgap21.numeric-two-slot-recurrence.dev.v1"
                    and base["mode"] == SOURCE
                    and base["accepted_native"] is False
                    and base["scientific_gain_verified"] is False,
                    "NESTED_SCHEMA")
            m = cls()
            for name in ("slots", "active", "recent", "since_switch",
                         "next_step", "total_witnesses", "switches"):
                setattr(m.base, name, base[name])
            require(type(m.slots) is list and len(m.slots) == 2
                    and all(type(slot) is list and len(slot) == 2
                            and all(type(pair) is list and len(pair) == 2
                                    and all(type(n) is int and 0 <= n <= 1024
                                            for n in pair)
                                    and pair[0] <= pair[1] for pair in slot)
                            for slot in m.slots), "NESTED_COUNTS")
            require(type(m.active) is int and m.active in (0, 1)
                    and type(m.base.next_step) is int
                    and 0 <= m.base.next_step <= 72
                    and type(m.base.total_witnesses) is int
                    and 0 <= m.base.total_witnesses <= 1024
                    and m.base.total_witnesses >= m.base.next_step
                    and type(m.base.switches) is int
                    and 0 <= m.base.switches <= 256
                    and type(m.base.since_switch) is int
                    and 0 <= m.base.since_switch <= m.base.next_step
                    and type(m.base.recent) is list
                    and len(m.base.recent) <= min(6, m.base.since_switch)
                    and all(type(z) is int and z in (0, 1)
                            for z in m.base.recent), "NESTED_CURSORS")
            require(type(d["sealed"]) is bool
                    and type(d["suppressed"]) is int
                    and 0 <= d["suppressed"] <= 1024
                    and type(d["sealed_at"]) is int,
                    "SEAL_TYPES")
            m.sealed = d["sealed"]
            m.suppressed = d["suppressed"]
            m.sealed_at = d["sealed_at"]
            m.snapshot = d["snapshot"]
            require((m.sealed and type(m.snapshot) is list
                     and m.snapshot == m.slots[0]
                     and 0 <= m.sealed_at < 72)
                    or (not m.sealed and m.snapshot is None
                        and m.sealed_at == -1 and m.suppressed == 0),
                    "SEALED_SNAPSHOT")
            require(sum(p[1] for slot in m.slots for p in slot) +
                    m.suppressed == m.base.total_witnesses and
                    m.checkpoint() == raw, "COLD_COUNTS")
            return m
        except (ValueError, TypeError, KeyError, UnicodeError,
                OverflowError) as exc:
            raise ValueError("YGG_TGAP23_COLD_REJECT") from exc


class PosteriorMix:
    """Read-only selector; never changes memory writer policy."""
    def __init__(self, memory):
        self.memory = memory
        self.p1 = 0.5

    def forecast(self, action):
        q0 = self.memory.slot_prediction(0, action)
        q1 = self.memory.slot_prediction(1, action)
        return (1 - self.p1) * q0 + self.p1 * q1

    def observe(self, step, action, witnessed):
        q0 = self.memory.slot_prediction(0, action)
        q1 = self.memory.slot_prediction(1, action)
        l0 = q0 if witnessed else 1 - q0
        l1 = q1 if witnessed else 1 - q1
        denom = (1 - self.p1) * l0 + self.p1 * l1
        require(denom > 0 and math.isfinite(denom), "SOFT_LIKELIHOOD")
        posterior = self.p1 * l1 / denom
        self.memory.observe(step, action, witnessed)
        self.p1 = HAZARD + (1 - 2 * HAZARD) * posterior


def fit():
    original = TwoSlotMemory()
    guard = GuardedTwoSlot()
    ctrls = {
        "stationary_fit": StationaryBeta(),
        "rolling_8_fit": RollingBeta(),
        "reset_fit": ResetBeta(),
        "bayes_hmm_fit": BayesianHMM(),
    }
    before = {}
    after_B = {}
    for step in range(FIT[4]):
        action = step % 2
        observed = witness(FIT[0], FIT[1], step, action, FIT[2], FIT[3])
        original.observe(step, action, observed)
        guard.observe(step, action, observed)
        for m in ctrls.values():
            m.observe(action, observed)
        if step == 23:
            before = {
                "original": tuple(original.slot_prediction(0, a)
                                  for a in (0, 1)),
                "guarded": tuple(guard.slot_prediction(0, a)
                                 for a in (0, 1)),
            }
        if step == 47:
            after_B = {
                "original": tuple(original.slot_prediction(0, a)
                                  for a in (0, 1)),
                "guarded": tuple(guard.slot_prediction(0, a)
                                 for a in (0, 1)),
            }
    raw_o, raw_g = original.checkpoint(), guard.checkpoint()
    require(TwoSlotMemory.restore(raw_o, digest(raw_o)).checkpoint() == raw_o
            and GuardedTwoSlot.restore(raw_g, digest(raw_g)).checkpoint() == raw_g,
            "FIT_COLD")
    return {
        "original": original, "guard": guard, "controls": ctrls,
        "before": before, "after_B": after_B,
        "checkpoint_bytes": {"original": len(raw_o), "guarded": len(raw_g)},
        "guard_sealed_at": guard.sealed_at,
        "guard_suppressed_fit": guard.suppressed,
    }


def evaluate_world(fit_bundle, world):
    require(type(world) is tuple and world in HELD, "FROZEN_WORLD")
    seed, role, first, second = world
    original = fit_bundle["original"]
    guarded = fit_bundle["guard"]
    writers = {
        "original_gate_fit": original.new_public_world(),
        "original_soft_fit": original.new_public_world(),
        "guarded_gate_fit": guarded.new_public_world(),
        "guarded_soft_fit": guarded.new_public_world(),
        "original_soft_no_fit": TwoSlotMemory(),
        "guarded_soft_no_fit": GuardedTwoSlot(),
    }
    reads = {name: PosteriorMix(writers[name]) for name in SOFT}
    extras = {
        k: copy.deepcopy(v) for k, v in fit_bundle["controls"].items()
    }
    extras["source_only"] = Uninformed()
    losses = {name: {"all": [], "return": []} for name in ARMS}
    equal = 0
    for step in range(64):
        action = step % 2
        outcome = witness(seed, role, step, action, first, second)
        for name in ARMS:
            if name in WRITERS:
                forecast = reads[name].forecast(action) if name in SOFT else (
                    writers[name].predict(action))
            else:
                forecast = extras[name].predict(action)
            require(type(forecast) is float and
                    math.isfinite(forecast) and 0 <= forecast <= 1,
                    "PREDICTION")
            loss = (forecast - outcome) ** 2
            losses[name]["all"].append(loss)
            if step >= second:
                losses[name]["return"].append(loss)
            if name in SOFT:
                reads[name].observe(step, action, outcome)
            elif name in WRITERS:
                writers[name].observe(step, action, outcome)
            else:
                extras[name].observe(action, outcome)
        require(
            writers["original_gate_fit"].checkpoint() ==
            writers["original_soft_fit"].checkpoint(), "ORIGINAL_WRITE_PARITY")
        require(
            writers["guarded_gate_fit"].checkpoint() ==
            writers["guarded_soft_fit"].checkpoint(), "GUARDED_WRITE_PARITY")
        equal += 1
    for name, mem in writers.items():
        raw = mem.checkpoint()
        cls = GuardedTwoSlot if name.startswith("guarded") else TwoSlotMemory
        require(cls.restore(raw, digest(raw)).checkpoint() == raw,
                "HELD_COLD_RESTORE")
    return {
        "sum_losses": {k: {phase: sum(rows) for phase, rows in vals.items()}
                       for k, vals in losses.items()},
        "budget": equal, "return_budget": 64 - second,
        "last_guard_suppressed": writers["guarded_gate_fit"].suppressed,
        "guards_equal": equal
    }


def proof():
    t0 = time.monotonic()
    protocol = json.loads(Path(__file__).with_name(
        "tgap23_protocol.json").read_text(encoding="utf-8"))
    require(protocol["schema"] == PROTOCOL
            and tuple(protocol["world"]["fit"].get(x)
                      for x in ("seed", "role", "first", "second", "steps")) == FIT
            and tuple(tuple(w[x] for x in
                            ("seed", "role", "first", "second"))
                      for w in protocol["world"]["held"]) == HELD
            and protocol["world"]["held_actions_per_policy"] == 640
            and protocol["world"]["held_return_actions_per_policy"] == 234
            and protocol["protected_writer"]["write_rule"].startswith(
                "For subsequent witnessed actions"),
            "FROZEN_PROTOCOL")
    bundle = fit()
    data = [evaluate_world(bundle, w) for w in HELD]
    total = sum(d["budget"] for d in data)
    ret_count = sum(d["return_budget"] for d in data)
    require(total == 640 and ret_count == 234
            and sum(d["guards_equal"] for d in data) == 640,
            "HELD_BUDGET")
    scores = {
        arm: {
            phase: round(sum(d["sum_losses"][arm][phase] for d in data) /
                         (total if phase == "all" else ret_count), 8)
            for phase in ("all", "return")
        } for arm in ARMS
    }
    drift = {name: sum(a != b for a, b in
                       zip(bundle["before"][name], bundle["after_B"][name]))
             for name in ("original", "guarded")}
    margins = {
        "H2_guard_gate_return": round(
            scores["original_gate_fit"]["return"] -
            scores["guarded_gate_fit"]["return"], 8),
        "H3_guard_soft_return": round(
            scores["original_soft_fit"]["return"] -
            scores["guarded_soft_fit"]["return"], 8),
        "H4_guard_soft_vs_rolling_all": round(
            scores["rolling_8_fit"]["all"] -
            scores["guarded_soft_fit"]["all"], 8),
        "readout_orig_all": round(
            scores["original_gate_fit"]["all"] -
            scores["original_soft_fit"]["all"], 8),
        "readout_guard_all": round(
            scores["guarded_gate_fit"]["all"] -
            scores["guarded_soft_fit"]["all"], 8),
        "fit_transfer_guard_soft": round(
            scores["guarded_soft_no_fit"]["all"] -
            scores["guarded_soft_fit"]["all"], 8),
    }
    hypotheses = {
        "H1_guarded_zero_old_A_readout_drift": drift["guarded"] == 0,
        "H2_guard_gate_return_gain_at_least_point01":
            margins["H2_guard_gate_return"] >= .01,
        "H3_guard_soft_return_gain_at_least_point01":
            margins["H3_guard_soft_return"] >= .01,
        "H4_guard_soft_overall_at_least_rolling":
            margins["H4_guard_soft_vs_rolling_all"] >= 0,
    }
    passes = sum(hypotheses.values())
    return {
        "schema": SCHEMA, "prereg_commit": PREREG,
        "source_mode": SOURCE, "fit_witnesses": 72,
        "held_worlds": len(HELD), "held_actions_per_policy": total,
        "return_actions_per_policy": ret_count, "held_brier": scores,
        "A_readout_drift_after_B": drift,
        "guard_sealed_at_fit_step": bundle["guard_sealed_at"],
        "guard_suppressed_fit_writes": bundle["guard_suppressed_fit"],
        "frozen_margins": margins, "frozen_hypotheses": hypotheses,
        "development_verdict": (
            "WRITE_RECOVERY_SUPPORTED_DEV" if passes == 4 else
            "MIXED_WRITE_PROTECTION_DEV" if passes else
            "WRITE_PROTECTION_NO_GO"),
        "write_ledger_equal_over_readout_arms": True,
        "write_ledger_parity_steps": total,
        "checkpoint_bytes_fit": bundle["checkpoint_bytes"],
        "engineering_gate": "PASS",
        "science_gate": "DEV_NO_GO_SYNTHETIC_NOT_NATIVE",
        "canonical_native_modified": False, "first_use_426": False,
        "deployment": "NONE",
        "wall_seconds_no_checkout": round(time.monotonic() - t0, 6)
    }


if __name__ == "__main__":
    print("YGG_TGAP23_RESULT=" + json.dumps(proof(), sort_keys=True))
