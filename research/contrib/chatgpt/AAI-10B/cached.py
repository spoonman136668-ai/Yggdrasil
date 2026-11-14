"""AAI-10B: semantics-preserving ephemeral prediction caches.

Source-locked AAI-10A ProtectedOperatorBank remains completely unchanged.
This is *only* an implementation speed experiment; no first-use SCIENCE.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "AAI-10A"))
import models as frozen


class CachedOperatorBank(frozen.ProtectedOperatorBank):
    """Same state, update/decision logic and scratch; no cached data serialized."""

    def __init__(self):
        super().__init__(3, True)
        self._reset_ephemeral()

    def _reset_ephemeral(self):
        self._priors = {}
        self._predictions = {}
        self._plans = {}

    def _prior(self, slot):
        slot_id = slot["id"]
        if slot_id not in self._priors:
            self._priors[slot_id] = super()._prior(slot)
        return self._priors[slot_id]

    def _slot_prediction(self, slot, x):
        """Frozen function exactly once per (stable slot ID, public 3-bit input)."""
        key = (slot["id"], frozen.require_bits(x, 3))
        if key not in self._predictions:
            self._predictions[key] = frozen.grammar_predict(
                slot["samples"], key[1], self._prior(slot))
        return self._predictions[key]

    def _likelihood(self, slot, batch):
        """Exactly same rounded probabilities, clamp and log summation order."""
        total = 0.0
        for x, m in batch:
            pred = self._slot_prediction(slot, x)
            for output in range(2):
                p = min(1 - 1e-6, max(1e-6, pred[output]))
                total += math.log(p if m[output] else 1.0 - p)
        return total

    def learn(self, row):
        # Original frozen code does not mutate learned slots on first scratch row.
        # This call validates row through the original method.
        result = super().learn(row)
        if not self.scratch:
            # Exactly two observations were consumed; any slot or archived-prior
            # dependency could have changed. Never preserve a stale prediction.
            self._reset_ephemeral()
        return result

    def predict(self, x):
        return self._slot_prediction(self.active(), x)

    def choose(self, row):
        # Call the original shared planner on first query; decisions of equal
        # public state and equal model memory are otherwise purely deterministic.
        frozen.visible(row)
        key = (tuple(row["x"]), tuple(row["goal"]), row["actions_taken"])
        if key not in self._plans:
            self._plans[key] = super().choose(row)
        return self._plans[key]


def cold_clone(saved):
    """Restore by the original exact-byte state validator, then add no-serialization cache."""
    base = frozen.cold_restore({"candidate": saved})["candidate"]
    clone = CachedOperatorBank()
    for name in ("slots", "active_id", "next_id", "scratch", "retrievals",
                 "max_slots", "reuse"):
        setattr(clone, name, getattr(base, name))
    clone._reset_ephemeral()
    if frozen.canonical(clone.state()) != saved:
        raise ValueError("cached clone violated frozen checkpoint bytes")
    return clone
