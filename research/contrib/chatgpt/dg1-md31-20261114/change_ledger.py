"""DG1-MD31: non-token, paid-evidence structural-change ledger.

Separate successor mechanism to frozen DG1-MD30; the parent policy source and
previous outcomes are immutable. The change decision never sees the hidden
graph, hidden rewire status, seed, motif, future, or a free World simulation.
A charged internal-node probe is mandatory for all three matched gate arms.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dg1-md30-20261114"))
from native_tournament import (
    ACTION_INDEX, CausalTournament, evidence_score, _unique,
)
from structural_rewire import digest

ROOT = Path(__file__).resolve().parent
PREREG = json.loads((ROOT / "prereg.json").read_text("utf-8"))
assert PREREG["schema"] == "yggdrasil.dg1-md31-prereg.v1"
assert PREREG["status"] == "FROZEN_PREREG_ONLY_NO_NEW_SOURCE_NO_OUTCOME"
ARM_MODES = ("evidence", "sham_stage1", "always_carry")
POOL = 32
EVIDENCE_MARGIN_TIMES_POOL = 24  # mean stage1-stage0 >= 0.75


def six_bit_score(expected, seen):
    return evidence_score(expected, seen)


class PaidChangeLedger:
    """Wraps the unchanged MD30 policy, gates its stage-one memory read."""

    def __init__(self, hypotheses, memory, mode="evidence"):
        if mode not in ARM_MODES:
            raise AssertionError("MD31_UNKNOWN_GATE_MODE")
        self.parent = CausalTournament(hypotheses, memory, "persistent")
        self.hypotheses = hypotheses
        self.mode = mode
        self.phase_one_probe = None
        self.phase_one_banks = None
        self.gate_done = False
        self.selected_bank = None
        self.evidence_delta_times_pool = None
        self.paid_gate_count = 0

    def _banks(self):
        if self.parent.phase != 1:
            raise AssertionError("MD31_NOT_AT_CHANGE_BOUNDARY")
        before = tuple(self.parent.carried[:POOL])
        after = tuple(self.parent.winners()[:POOL])
        if len(before) != POOL or len(after) != POOL:
            raise AssertionError("MD31_INSUFFICIENT_HYPOTHESES")
        return before, after

    def _most_discriminating_probe(self, menu):
        before, after = self._banks()
        best = None
        best_score = -1
        # Count binary sensor predictions per bank. Equal 32-member pools,
        # so total L1 disagreement is exactly an integer and ties are stable.
        for node in sorted(menu):
            for value in (0, 1):
                index = ACTION_INDEX[(node, value)]
                old_counts = [sum(self.hypotheses[h][index][bit]
                                  for h in before) for bit in range(6)]
                new_counts = [sum(self.hypotheses[h][index][bit]
                                  for h in after) for bit in range(6)]
                score = sum(abs(x - y) for x, y in zip(old_counts, new_counts))
                if score > best_score:
                    best, best_score = (node, value), score
        if best is None:
            raise AssertionError("MD31_NO_PAID_INTERNAL_PROBE_AVAILABLE")
        return best

    def choose(self, public_observation):
        if (public_observation["phase"] == 1 and not self.gate_done):
            if self.parent.phase != 1:
                raise AssertionError("MD31_PHASE_OR_PUBLIC_HISTORY_DRIFT")
            if self.phase_one_probe is None:
                self.phase_one_banks = self._banks()
                self.phase_one_probe = self._most_discriminating_probe(
                    public_observation["diagnostic_nodes"])
            if public_observation["remaining_diagnostics"] <= 0:
                raise AssertionError("MD31_UNPAID_CHANGE_DETECTION")
            return {"kind": "diagnostic", "node": self.phase_one_probe[0],
                    "value": self.phase_one_probe[1]}
        return self.parent.choose(public_observation)

    def consume(self, before, action, after):
        gate = before["phase"] == 1 and not self.gate_done
        if gate:
            if (self.phase_one_probe is None or self.phase_one_banks is None or
                    action != {"kind": "diagnostic",
                               "node": self.phase_one_probe[0],
                               "value": self.phase_one_probe[1]}):
                raise AssertionError("MD31_GATE_ACTION_MISMATCH")
            if (len(after["charged_history"]) !=
                    len(before["charged_history"]) + 1):
                raise AssertionError("MD31_GATE_REQUIRES_PAID_PUBLIC_RECEIPT")
            row = after["charged_history"][-1]
            if (row["action"] != action or row["phase"] != 1 or
                    row["reward"] != -0.05):
                raise AssertionError("MD31_GATE_RECEIPT_NOT_PHYSICAL")
            old_active = set(self.parent.active)
            self.parent.consume(before, action, after)
            before_bank, after_bank = self.phase_one_banks
            index = ACTION_INDEX[(action["node"], action["value"])]
            observed = row["sensor_vector"]
            score_a = sum(six_bit_score(self.hypotheses[i][index], observed)
                          for i in before_bank)
            score_b = sum(six_bit_score(self.hypotheses[i][index], observed)
                          for i in after_bank)
            self.evidence_delta_times_pool = score_b - score_a
            if self.mode == "evidence":
                use_new = (score_b - score_a >= EVIDENCE_MARGIN_TIMES_POOL)
            else:
                use_new = self.mode == "sham_stage1"
            chosen = after_bank if use_new else before_bank
            for i in chosen:
                # The original MD30 consume already scored signatures
                # present in its active set. Credit newly recalled ones
                # exactly once using this SAME physically paid response.
                if i not in old_active:
                    self.parent.online_credit[i] += six_bit_score(
                        self.hypotheses[i][index], observed)
            self.parent.active = _unique(chosen, self.parent.memory.global_recovery)
            self.selected_bank = "stage1" if use_new else "stage0"
            self.paid_gate_count += 1
            self.gate_done = True
        else:
            self.parent.consume(before, action, after)

    def audit(self):
        if not self.gate_done or self.paid_gate_count != 1:
            raise AssertionError("MD31_GATE_NOT_PHYSICALLY_EXECUTED")
        return {
            "mode": self.mode,
            "phase1_paid_probe": list(self.phase_one_probe),
            "bank_decision": self.selected_bank,
            "evidence_difference_times_32": self.evidence_delta_times_pool,
            "charged_parent_actions": self.parent.paid_actions,
        }
