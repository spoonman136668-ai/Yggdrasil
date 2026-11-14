"""DG1-MD30 bounded persistent *non-token* causal-hypothesis tournament.

Synthetic development only: hypotheses are compact physical response
signatures, not tokens, gradients, graph IDs or transferred model weights.
Training reads only precharged public action receipts. Interventions at
evaluation time always require actual World.step calls. Frozen controls
and official MD30 cohorts remain entirely separate.
"""
import json
import math
from pathlib import Path

from bayesian_control import ALL_ACTIONS, COUNT, build_hypotheses
from structural_rewire import canonical, digest

ROOT = Path(__file__).resolve().parent
LOCK = json.loads((ROOT / "native_tournament_lock.json").read_text("utf-8"))
assert LOCK["schema"] == "yggdrasil.dg1-md30-native-causal-tournament-lock.v1"
assert LOCK["status"] == "FROZEN_BEFORE_CANDIDATE_SOURCE__SYNTHETIC_DEVELOPMENT_ONLY"
TRAIN = LOCK["train"]
ONLINE = LOCK["online"]
assert COUNT == 768 and ONLINE["winner_pool"] == 32
ACTION_INDEX = {pair: i for i, pair in enumerate(ALL_ACTIONS)}
MODES = ("persistent", "stateless", "change_agnostic")


def evidence_score(expected, actual):
    if len(expected) != 6 or len(actual) != 6:
        raise AssertionError("MD30_TOURNAMENT_BAD_PUBLIC_SENSOR")
    return sum(1 if p == q else -2 for p, q in zip(expected, actual))


def rank_by_credit(values):
    if len(values) != COUNT:
        raise AssertionError("MD30_TOURNAMENT_CREDIT_WIDTH")
    return tuple(sorted(range(COUNT), key=lambda i: (-values[i], i)))


def _unique(*groups):
    seen = set()
    result = []
    for group in groups:
        for item in group:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return tuple(result)


class PersistentCausalMemory:
    """Training-time persistent hypothesis banks; no graph-object access."""

    def __init__(self, hypotheses, credits, custody):
        if len(hypotheses) != COUNT or len(credits) != 2 or any(
                len(bank) != COUNT for bank in credits):
            raise AssertionError("MD30_TOURNAMENT_MEMORY_SHAPE")
        if any(type(v) is not int for bank in credits for v in bank):
            raise AssertionError("MD30_TOURNAMENT_NONINTEGER_CREDIT")
        self.credits = tuple(tuple(bank) for bank in credits)
        self.hypothesis_sha256 = digest(hypotheses)
        self.physical_training = custody
        self.phase_rank = tuple(rank_by_credit(c) for c in self.credits)
        summed = [a + b for a, b in zip(*self.credits)]
        self.global_rank = rank_by_credit(summed)
        self.phase_banks = tuple(
            v[:TRAIN["phase_bank_keep"]] for v in self.phase_rank)
        self.global_recovery = self.global_rank[:TRAIN["global_recovery_keep"]]

    @classmethod
    def fit(cls, hypotheses, sessions, custody):
        if len(sessions) != 240 or custody["charged_steps"] != 1920:
            raise AssertionError("MD30_TOURNAMENT_NOT_SHARED_PAID_TRAINING")
        credits = [[0] * COUNT for _ in range(2)]
        action_ix = ACTION_INDEX
        count = 0
        for episode in sessions:
            if len(episode) != 2:
                raise AssertionError("MD30_TOURNAMENT_STAGE_CUSTODY")
            for phase, rows in enumerate(episode):
                if len(rows) != 4:
                    raise AssertionError("MD30_TOURNAMENT_UNPAID_STAGE")
                for row in rows:
                    a = row["action"]
                    if (set(row) != {"phase", "action", "sensor_vector", "reward"}
                            or row["phase"] != phase
                            or set(a) != {"kind", "node", "value"}
                            or a["kind"] not in ("diagnostic", "actuator")):
                        raise AssertionError("MD30_TOURNAMENT_PUBLIC_RECEIPT_ONLY")
                    j = action_ix[(a["node"], a["value"])]
                    observed = row["sensor_vector"]
                    bank = credits[phase]
                    for i, signature in enumerate(hypotheses):
                        bank[i] += evidence_score(signature[j], observed)
                    count += 1
        if count != 1920:
            raise AssertionError("MD30_TOURNAMENT_ACTION_CUSTODY_DRIFT")
        return cls(hypotheses, credits, custody)

    def checkpoint(self):
        return {
            "schema": "md30.native-causal-memory.v1",
            "hypotheses_sha256": self.hypothesis_sha256,
            "credited_physical_actions": self.physical_training["charged_steps"],
            "physical_training_sha256": self.physical_training["physical_sha256"],
            "banks": [list(x) for x in self.credits],
            "phase_banks": [list(x) for x in self.phase_banks],
            "global_recovery": list(self.global_recovery),
            "method": "credit+1/-2;two-protected-banks;no-gradient",
        }

    @classmethod
    def from_checkpoint(cls, hypotheses, checkpoint):
        if (checkpoint.get("schema") != "md30.native-causal-memory.v1"
                or checkpoint.get("hypotheses_sha256") != digest(hypotheses)
                or checkpoint.get("credited_physical_actions") != 1920):
            raise AssertionError("MD30_TOURNAMENT_COLD_CUSTODY_DRIFT")
        custody = {
            "charged_steps": checkpoint["credited_physical_actions"],
            "physical_sha256": checkpoint["physical_training_sha256"],
        }
        restored = cls(hypotheses, checkpoint["banks"], custody)
        if (checkpoint["phase_banks"] != [list(x) for x in restored.phase_banks]
                or checkpoint["global_recovery"] != list(restored.global_recovery)
                or checkpoint != restored.checkpoint()):
            raise AssertionError("MD30_TOURNAMENT_COLD_BYTES_DIFFER")
        return restored


class CausalTournament:
    """Bounded credit tournament, not a probabilistic Bayesian filter."""

    def __init__(self, hypotheses, memory, mode="persistent"):
        if mode not in MODES or len(hypotheses) != COUNT:
            raise AssertionError("MD30_TOURNAMENT_INVALID_MODE_OR_CAPACITY")
        if memory.hypothesis_sha256 != digest(hypotheses):
            raise AssertionError("MD30_TOURNAMENT_WRONG_SOURCE_HYPOTHESES")
        self.hypotheses = hypotheses
        self.memory = memory
        self.mode = mode
        self.phase = 0
        self.paid_actions = 0
        self.probed = set()
        self.carried = ()
        self.online_credit = [0] * COUNT
        self.active = self._build_active(0)
        self.model_calls = 0

    def _build_active(self, phase):
        if self.mode == "stateless":
            return tuple(range(COUNT))
        if self.mode == "change_agnostic":
            bank = self.memory.phase_banks[0]
        else:
            bank = self.memory.phase_banks[phase]
        return _unique(
            bank, self.carried[:TRAIN["carried_previous_phase_keep"]],
            self.memory.global_recovery)

    def _score(self, index):
        if self.mode == "stateless":
            base = 0
        elif self.mode == "change_agnostic":
            base = self.memory.credits[0][index]
        else:
            base = self.memory.credits[self.phase][index]
        # Fixed-ratio integer arithmetic avoids OS floating-point rank drift.
        return 16 * base + 1920 * self.online_credit[index]

    def winners(self):
        return tuple(sorted(self.active, key=lambda i: (-self._score(i), i))
                     [:ONLINE["winner_pool"]])

    def choose(self, obs):
        if obs["phase"] not in (0, 1) or obs["phase"] != self.phase:
            raise AssertionError("MD30_TOURNAMENT_PHASE_DRIFT")
        if len(obs["charged_history"]) != self.paid_actions:
            raise AssertionError("MD30_TOURNAMENT_UNCHARGED_HISTORY_DRIFT")
        good = tuple(i for i in (0, 1) if obs["actuator_availability"][i])
        if not good:
            raise AssertionError("MD30_TOURNAMENT_NO_ACTUATOR")
        selected = self.winners()
        if not selected:
            raise AssertionError("MD30_TOURNAMENT_NO_WINNERS")
        ballots = {node: sum(self.hypotheses[idx][node][obs["target_sensor"]]
                             == obs["desired_value"] for idx in selected)
                   for node in good}
        best_actuator = min(good, key=lambda i: (-ballots[i], i))
        baseline = ballots[best_actuator] / len(selected)
        best_probe = None
        best_gain = 1e-9
        self.model_calls += 1
        probes_in_stage = sum(
            row["phase"] == self.phase and
            row["action"]["kind"] == "diagnostic"
            for row in obs["charged_history"])
        if (probes_in_stage < ONLINE["diagnostic_cap_per_stage"] and
                obs["remaining_diagnostics"] > 0):
            for node in obs["diagnostic_nodes"]:
                for value in (0, 1):
                    if (node, value) in self.probed:
                        continue
                    signature_ix = ACTION_INDEX[(node, value)]
                    cases = {}
                    for i in selected:
                        prediction = tuple(self.hypotheses[i][signature_ix])
                        voters = cases.setdefault(prediction, {a: 0 for a in good})
                        for a in good:
                            voters[a] += int(
                                self.hypotheses[i][a][obs["target_sensor"]]
                                == obs["desired_value"])
                    gain = 1.5 * (
                        sum(max(v.values()) for v in cases.values())
                        / len(selected) - baseline) - 0.05
                    if gain > best_gain + 1e-12:
                        best_gain = gain
                        best_probe = (node, value)
        if best_probe is None:
            return {"kind": "actuator", "node": best_actuator, "value": 1}
        return {"kind": "diagnostic", "node": best_probe[0],
                "value": best_probe[1]}

    def consume(self, before, action, after):
        if (not isinstance(before, dict) or not isinstance(after, dict)
                or before.get("phase") != self.phase or
                "charged_history" not in after
                or len(after["charged_history"]) != self.paid_actions + 1):
            raise AssertionError("MD30_TOURNAMENT_REQUIRES_NEW_PAID_RECEIPT")
        row = after["charged_history"][-1]
        if (set(row) != {"phase", "action", "sensor_vector", "reward"}
                or row["phase"] != self.phase or row["action"] != action
                or set(action) != {"kind", "node", "value"}
                or action["kind"] not in ("diagnostic", "actuator")):
            raise AssertionError("MD30_TOURNAMENT_PUBLIC_ACTION_MISMATCH")
        j = ACTION_INDEX[(action["node"], action["value"])]
        for i in self.active:
            self.online_credit[i] += evidence_score(
                self.hypotheses[i][j], row["sensor_vector"])
        self.paid_actions += 1
        if action["kind"] == "diagnostic":
            self.probed.add((action["node"], action["value"]))
        else:
            if self.phase == 0:
                self.carried = self.winners()[:TRAIN["carried_previous_phase_keep"]]
                self.phase = 1
                self.online_credit = [0] * COUNT
                self.probed.clear()
                self.active = self._build_active(1)
            else:
                self.phase = 2
        if after["phase"] != ("done" if self.phase == 2 else self.phase):
            raise AssertionError("MD30_TOURNAMENT_INVALID_STAGE_TRANSITION")


def trained_memory(sessions, custody):
    hypotheses = build_hypotheses()
    return hypotheses, PersistentCausalMemory.fit(hypotheses, sessions, custody)
