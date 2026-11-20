"""KNOW30 source-only, phase-blind A/B/A posterior-slot and HMM comparison.

Preregistered before source/held first-use: 13c0f0ad2622acc6ce16605f34ce8a4c59c16985.
Method-concretization commit: c2dbb0e782c4f18f92a01c3acb32b14d819d04eb.
No real-world first use, canonical checkpoint, native code or owner runner.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import time
from pathlib import Path

from unknown_action_affordance_dev import (
    ALL_MAPS, TRUE_MAPS, P_TRUE, P_FALSE, fit_source,
    expected_brier, canonical, digest,
)
from know27_online_action_policy_dev import true_bit

SCHEMA = "yggdrasil.know30.blind-archive-reactivation-result.v1"
PROTO = "yggdrasil.know30.blind-archive-reactivation-prereg.v1"
PROTO_BLOB = "ae7e5987cb4d5910325bb2e2275d5e3e6d26210b"
MODE = "engineering_fixture_only"
SEEDS = (15203, 15217, 15227, 15241, 15259, 15269, 15287, 15307)
FIT_A = (15311, 15313)
FIT_B = (15319, 15329)
HAZARD = 1.0 / 16
WRITE_HI, WRITE_LO = .8, .2
N = 48


def require(ok, message):
    if not ok:
        raise ValueError("YGG_KNOW30_" + message)


def protocol():
    raw = Path(__file__).with_name(
        "know30_blind_archive_reactivation_protocol.json").read_bytes()
    gitblob = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(gitblob == PROTO_BLOB, "PROTOCOL_BLOB")
    p = json.loads(raw)
    require(p["schema"] == PROTO
            and p["frozen_worlds"]["seeds"] == list(SEEDS)
            and p["frozen_worlds"]["phase_lengths"] == [12, 24, 12]
            and p["frozen_worlds"]["observed_actions_per_policy"] == 1152
            and p["methods"]["fit_hazards"] == [HAZARD]
            and p["source"]["source_mode"] == MODE
            and p["authority"]["protected_original_first_use"] is False,
            "PROTOCOL_CONTRACT")
    return p


def private_witness(map_id, seed, t, action, law, *, fit=False, source_mode=MODE):
    """Evaluator only. Never pass map_id, law or private coin to learner APIs."""
    valid = (seed in FIT_A + FIT_B) if fit else (seed in SEEDS)
    require(source_mode == MODE and type(map_id) is int and 0 <= map_id < 3
            and type(seed) is int and valid
            and type(t) is int and 0 <= t < (32 if fit else N)
            and type(action) is int and action in (0, 1, 2, 3)
            and law in ("H0", "H2"), "PRIVATE_SOURCE")
    if fit:
        require((law == "H0" and seed in FIT_A)
                or (law == "H2" and seed in FIT_B), "FIT_SOURCE_LAW")
        domain = "fit"
    else:
        require(law == ("H0" if t < 12 or t >= 36 else "H2"),
                "HELD_SOURCE_LAW")
        domain = "private"
    context = t % 4
    physical = context ^ TRUE_MAPS[map_id][action]
    p = P_TRUE if true_bit(law, physical) else P_FALSE
    raw = hashlib.sha256(
        f"know30:{domain}:coin:v1:{map_id}:{seed}:{t}".encode("ascii")
    ).digest()
    return int(int.from_bytes(raw[:8], "big") / (1 << 64) < p)


class Joint:
    """Six-map x 256 Boolean law, conventional exact conditional posterior.

    Weighted emission updates are explicit mean-field approximations for HMM;
    NOT a full exact 256^2 two-regime HMM. Model never receives private law.
    """
    def __init__(self, prior):
        require(type(prior) is list and len(prior) == 6
                and all(type(x) is float and x > 0 and math.isfinite(x)
                        for x in prior)
                and abs(sum(prior) - 1) < 1e-9, "MAPPING_PRIOR")
        self.prior = list(prior)
        self.logs = [[math.log(x) - math.log(256) for _ in range(256)]
                     for x in prior]
        self.assimilated = 0.0

    def prob(self, c, a):
        require(type(c) is int and 0 <= c < 8
                and type(a) is int and a in (0, 1, 2, 3), "FORECAST")
        top = max(max(row) for row in self.logs)
        z, yes = 0., 0.
        for i, row in enumerate(self.logs):
            pos = c ^ ALL_MAPS[i][a]
            for table, v in enumerate(row):
                w = math.exp(v - top)
                z += w
                if (table >> pos) & 1:
                    yes += w
        return P_FALSE + (P_TRUE - P_FALSE) * yes / z

    def update(self, c, a, y, weight=1.0):
        require(type(c) is int and 0 <= c < 4
                and type(a) is int and a in (0, 1, 2, 3)
                and type(y) is int and y in (0, 1)
                and type(weight) is float and 0 <= weight <= 1
                and math.isfinite(weight), "SINGLE_WITNESS")
        yes = weight * math.log(P_TRUE if y else 1 - P_TRUE)
        no = weight * math.log(P_FALSE if y else 1 - P_FALSE)
        for i, row in enumerate(self.logs):
            pos = c ^ ALL_MAPS[i][a]
            for table in range(256):
                row[table] += yes if (table >> pos) & 1 else no
        self.assimilated += weight


class Pair:
    """Identical FIT prototypes; differing policies only in write admission."""
    def __init__(self, slot_a, slot_b, *, quarantine):
        require(type(quarantine) is bool, "POLICY")
        self.slots = [copy.deepcopy(slot_a), copy.deepcopy(slot_b)]
        self.belief_a = .5
        self.received = 0
        self.quarantined = 0
        self.quarantine = quarantine
        self.false_confidence_switches = 0
        self.last_write = None

    def prior_a(self):
        return self.belief_a * (1 - HAZARD) + (1 - self.belief_a) * HAZARD

    def prob(self, c, a):
        q = self.prior_a()
        return q * self.slots[0].prob(c, a) + (1 - q) * self.slots[1].prob(c, a)

    def observe(self, t, c, a, y, *, source_mode=MODE):
        require(source_mode == MODE and type(t) is int and t == self.received
                and t < N and c == t % 4, "WITNESS_ORDER")
        require(type(y) is int and y in (0, 1), "WITNESSED")
        p_a = self.slots[0].prob(c, a)
        p_b = self.slots[1].prob(c, a)
        prior = self.prior_a()
        like_a = p_a if y else 1 - p_a
        like_b = p_b if y else 1 - p_b
        den = prior * like_a + (1 - prior) * like_b
        require(den > 0, "PHASE_LIKELIHOOD")
        next_b = prior * like_a / den
        if self.quarantine:
            if next_b >= WRITE_HI:
                self.slots[0].update(c, a, y, 1.0)
                self.last_write = 0
            elif next_b <= WRITE_LO:
                self.slots[1].update(c, a, y, 1.0)
                self.last_write = 1
            else:
                self.quarantined += 1
                self.last_write = None
        else:
            self.slots[0].update(c, a, y, float(next_b))
            self.slots[1].update(c, a, y, float(1 - next_b))
            self.last_write = "soft"
        self.belief_a = next_b
        self.received += 1

    def checkpoint(self):
        payload = {
            "schema": "yggdrasil.know30.pair-checkpoint.v1",
            "source_mode": MODE, "accepted_native": False,
            "quarantine": self.quarantine, "belief_a": self.belief_a,
            "received": self.received, "quarantined": self.quarantined,
            "last_write": self.last_write,
            "slots": [{"prior": s.prior, "logs": s.logs,
                       "assimilated": s.assimilated} for s in self.slots],
        }
        raw = canonical(payload)
        require(len(raw) < 300000, "CHECKPOINT_LIMIT")
        return raw

    @classmethod
    def restore(cls, raw, expected_hash):
        require(type(raw) is bytes and digest(raw) == expected_hash
                and 0 < len(raw) < 300000, "COLD_SHA")
        try:
            def unique(pairs):
                out = {}
                for k, v in pairs:
                    require(k not in out, "DUPLICATE_KEY")
                    out[k] = v
                return out
            payload = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            require(set(payload) == {
                "schema", "source_mode", "accepted_native", "quarantine",
                "belief_a", "received", "quarantined", "last_write", "slots"
            } and payload["schema"] == "yggdrasil.know30.pair-checkpoint.v1"
                    and payload["source_mode"] == MODE
                    and payload["accepted_native"] is False
                    and type(payload["quarantine"]) is bool
                    and type(payload["received"]) is int
                    and 0 <= payload["received"] <= N
                    and type(payload["quarantined"]) is int
                    and 0 <= payload["quarantined"] <= payload["received"]
                    and len(payload["slots"]) == 2, "COLD_CONTRACT")
            models = []
            for state in payload["slots"]:
                require(set(state) == {"prior", "logs", "assimilated"}
                        and len(state["logs"]) == 6
                        and all(len(z) == 256 for z in state["logs"])
                        and all(math.isfinite(v) for row in state["logs"]
                                for v in row), "COLD_STATE")
                model = Joint(state["prior"])
                model.logs = state["logs"]
                model.assimilated = state["assimilated"]
                models.append(model)
            restored = cls(*models, quarantine=payload["quarantine"])
            restored.belief_a = payload["belief_a"]
            restored.received = payload["received"]
            restored.quarantined = payload["quarantined"]
            restored.last_write = payload["last_write"]
            require(restored.checkpoint() == raw, "COLD_BYTES")
            return restored
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError) as exc:
            raise ValueError("YGG_KNOW30_COLD_REJECTED") from exc


class Single:
    def __init__(self, model, *, rolling=False):
        self.start = copy.deepcopy(model)
        self.live = copy.deepcopy(model)
        self.rolling = rolling
        self.rows = []
    def prob(self, c, a):
        return self.live.prob(c, a)
    def observe(self, t, c, a, y, *, source_mode=MODE):
        require(source_mode == MODE and t == len(self.rows)
                and t < N and c == t % 4
                and type(y) is int and y in (0, 1), "SINGLE_ORDER")
        self.rows.append((c, a, y))
        if self.rolling:
            self.live = copy.deepcopy(self.start)
            for row in self.rows[-8:]:
                self.live.update(*row)
        else:
            self.live.update(c, a, y)


def trained(map_id):
    """TRAIN uses labelled source laws; HELD input never has those labels."""
    prior, old = fit_source(map_id)  # Already consumed KNOW26 historical FIT.
    a, b = Joint(prior), Joint(prior)
    pooled = Joint(prior)
    for name, seeds, slot in (("H0", FIT_A, a), ("H2", FIT_B, b)):
        for seed in seeds:
            for t in range(32):
                c, action = t % 4, t % 4
                y = private_witness(map_id, seed, t, action, name, fit=True)
                slot.update(c, action, y)
                pooled.update(c, action, y)
    require(a.assimilated == b.assimilated == 64.
            and pooled.assimilated == 128., "FIT_EXPOSURE")
    return prior, a, b, pooled, old


def high_brier(model, law):
    return sum(expected_brier(
        model.prob(c, 0), P_TRUE if true_bit(law, c) else P_FALSE)
        for c in range(4, 8)) / 4


def held_world(map_id, seed, fitted):
    require(type(map_id) is int and map_id in (0, 1, 2)
            and type(seed) is int and seed in SEEDS, "HELD_WORLD")
    prior, a, b, pooled, _ = fitted
    methods = {
        "archive": Pair(a, b, quarantine=True),
        "switching_bayes": Pair(a, b, quarantine=False),
        "single": Single(pooled),
        "rolling8": Single(pooled, rolling=True),
        "no_fit_archive": Pair(Joint([1 / 6.] * 6),
                               Joint([1 / 6.] * 6), quarantine=True),
    }
    scores = {name: {"k": {}, "return": [], "B": []}
              for name in methods}
    fit_a_readout = [a.prob(c, 0) for c in range(4, 8)]
    at_pre_return = None
    archive = methods["archive"]
    phase_moved = False
    b_archive_seen = False
    a_protection_broken = False
    protected_a_snapshot = None
    for t in range(N):
        # Phase is private here ONLY. Models receive c,a,y without phase/seed/map.
        law = "H0" if t < 12 or t >= 36 else "H2"
        c, action = t % 4, t % 4
        for name, model in methods.items():
            z = high_brier(model, law)
            if 12 <= t < 36:
                scores[name]["B"].append(z)
            if t >= 36:
                scores[name]["return"].append(z)
                if t - 36 in (1, 2, 4, 8):
                    scores[name]["k"][str(t - 36)] = z
        if t == 36:
            at_pre_return = [methods["archive"].slots[0].prob(c, 0)
                             for c in range(4, 8)]
        y = private_witness(map_id, seed, t, action, law)
        prior_belief = archive.belief_a
        for model in methods.values():
            model.observe(t, c, action, y)
        phase_moved = phase_moved or (archive.belief_a != prior_belief)
        if archive.belief_a <= WRITE_LO:
            if protected_a_snapshot is None:
                protected_a_snapshot = canonical(archive.slots[0].logs)
                b_archive_seen = True
            elif canonical(archive.slots[0].logs) != protected_a_snapshot:
                a_protection_broken = True
        elif protected_a_snapshot is not None:
            if archive.belief_a < WRITE_HI:
                if canonical(archive.slots[0].logs) != protected_a_snapshot:
                    a_protection_broken = True
            else:
                # Readmission into A ends this nonprivileged B-protection interval.
                protected_a_snapshot = None
    for method in methods.values():
        require(method.received == 48 if isinstance(method, Pair)
                else len(method.rows) == 48, "HELD_BUDGET")
    cold = {}
    for name in ("archive", "switching_bayes", "no_fit_archive"):
        model = methods[name]
        raw = model.checkpoint()
        restored = Pair.restore(raw, digest(raw))
        require(restored.checkpoint() == raw, "COLD_REPLAY")
        require([restored.prob(c, 0) for c in range(8)] ==
                [model.prob(c, 0) for c in range(8)], "COLD_FUNCTIONAL")
        cold[name] = {"checkpoint_bytes": len(raw),
                      "assigned_A": round(model.slots[0].assimilated, 5),
                      "assigned_B": round(model.slots[1].assimilated, 5),
                      "quarantined": model.quarantined}
    return {
        "scores": {name: {
            "k": v["k"],
            "return_brier": sum(v["return"]) / len(v["return"]),
            "B_brier": sum(v["B"]) / len(v["B"])
        } for name, v in scores.items()},
        "A_pre_FIT_high": fit_a_readout,
        "A_before_return_high": at_pre_return,
        "A_high_changed_during_B": sum(
            x != y for x, y in zip(fit_a_readout, at_pre_return)),
        "archive_B_protection": b_archive_seen and not a_protection_broken,
        "B_protection_detected": b_archive_seen,
        "phase_belief_changed": phase_moved,
        "cold": cold,
    }


def study():
    began = time.monotonic()
    protocol()
    fits = {mid: trained(mid) for mid in range(3)}
    rows = [held_world(mid, seed, fits[mid])
            for mid in range(3) for seed in SEEDS]
    require(len(rows) == 24, "WORLD_BUDGET")
    names = tuple(rows[0]["scores"])
    overall = {}
    for name in names:
        overall[name] = {
            "return_brier": round(sum(
                row["scores"][name]["return_brier"] for row in rows) / 24, 8),
            "B_brier": round(sum(
                row["scores"][name]["B_brier"] for row in rows) / 24, 8),
            "after_k": {
                str(k): round(sum(
                    row["scores"][name]["k"][str(k)] for row in rows) / 24, 8)
                for k in (1, 2, 4, 8)
            },
        }
    arc, hmm = overall["archive"], overall["switching_bayes"]
    wins = sum(row["scores"]["archive"]["k"]["8"] <
               row["scores"]["switching_bayes"]["k"]["8"] for row in rows)
    decisions = {
        "H1_no_pre_witness_phase_label": True,
        "H2_return_beats_HMM_k4_k8_and_18of24":
            all(arc["after_k"][str(k)] <= hmm["after_k"][str(k)] - .005
                for k in (4, 8)) and wins >= 18,
        "H3_B_no_more_than_p005_worse":
            arc["B_brier"] <= hmm["B_brier"] + .005,
        "H4_cold_restore_exact_and_A_protected_after_B_detection":
            all(row["archive_B_protection"] for row in rows),
        "H5_witness_affects_phase":
            all(row["phase_belief_changed"] for row in rows),
    }
    supported = all(decisions[z] for z in (
        "H2_return_beats_HMM_k4_k8_and_18of24",
        "H3_B_no_more_than_p005_worse",
        "H4_cold_restore_exact_and_A_protected_after_B_detection",
        "H5_witness_affects_phase"
    ))
    return {
        "schema": SCHEMA, "prereg_first_commit":
            "13c0f0ad2622acc6ce16605f34ce8a4c59c16985",
        "source_mode": MODE, "held_worlds": 24,
        "witnesses_per_policy": 1152, "fit_labeled_A_and_B_per_map": 128,
        "fit_historical_mapping_per_map": 108,
        "results": overall, "worlds": rows, "k8_paired_wins": wins,
        "frozen_decisions": decisions,
        "development_verdict": ("DEVELOPMENT_SUPPORTED_SYNTHETIC"
                                 if supported else "DEVELOPMENT_NO_GO_OR_MIXED"),
        "engineering": "PASS", "scientific": "SCIENCE_NO_GO_NOT_NATIVE",
        "native_model_changed": False, "protected_original_first_use": False,
        "deployment": "NONE", "wall_seconds_script_only":
            round(time.monotonic() - began, 6),
    }


if __name__ == "__main__":
    print(json.dumps(study(), sort_keys=True, indent=2))
