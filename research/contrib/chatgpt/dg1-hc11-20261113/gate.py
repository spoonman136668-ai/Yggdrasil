"""HC11: finite physical-witness confidence filter on frozen HC09 causal banks.

The gate never learns from evaluator queries, hidden phases, or forced flips.
Its output is conservative empirical *recall*, not proof of generalization.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HC10 = Path(__file__).resolve().parents[1] / "dg1-hc10-20261113"
if str(HC10) not in sys.path:
    sys.path.append(str(HC10))
from interbank_policy import base, choose as native_choose
from conventional_jsd import control, choose as conventional_choose

SCHEMA = "ygg.dg1-hc11.physical-witness-gate.v1"
LIMIT = 4096


class EvidenceGate:
    """Remember only repeated, physically observed transitions in an epoch."""

    def __init__(self, family="native", minimum=2):
        if family not in ("native", "conventional") or type(minimum) is not int or minimum not in (1, 2):
            raise ValueError("HC11_BAD_FAMILY_OR_THRESHOLD")
        self.family = family
        self.minimum = minimum
        self.model = base.DualRegimeCausalCells() if family == "native" else control.ConventionalContextModel()
        self.witness = {}
        self.epoch = 0
        self.conflicts = 0
        self.context_resets = 0

    def _context(self):
        return self.model.active if self.family == "native" else self.model.selected

    def _unresolved(self):
        return self.model.unresolved if self.family == "native" else self.model.mismatch

    def observe(self, before, action, after):
        base.valid_state(before)
        base.valid_action(action)
        base.valid_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("HC11_NONLOCAL_OBSERVATION")
        key = (before, action)
        old = self.witness.get(key)
        conflict = old is not None and old[0] != after
        if conflict:
            self.witness.clear()
            self.conflicts += 1
            self.epoch += 1
        active = self._context()
        success = self.model.observe(before, action, after)
        if self._context() != active or not success or self._unresolved():
            self.witness.clear()
            self.context_resets += 1
            self.epoch += 1
        old = self.witness.get(key)
        count = min(2, old[1] + 1) if old is not None and old[0] == after else 1
        self.witness[key] = (after, count)
        assert len(self.witness) <= 64
        return success

    def choose(self, state, flips, cap):
        return (native_choose(self.model, state, flips, cap) if self.family == "native"
                else conventional_choose(self.model, state, flips, cap))

    def predict(self, state, action):
        base.valid_state(state)
        base.valid_action(action)
        evidence = self.witness.get((state, action))
        if evidence is None or evidence[1] < self.minimum:
            return None
        predicted = self.model.predict(state, action)
        if predicted != evidence[0]:
            return None
        return predicted

    def snapshot(self):
        entries = [[s, a, nxt, count] for (s, a), (nxt, count) in sorted(self.witness.items())]
        payload = {
            "schema": SCHEMA,
            "family": self.family,
            "minimum": self.minimum,
            "model": self.model.snapshot().decode("ascii"),
            "witness": entries,
            "epoch": self.epoch,
            "conflicts": self.conflicts,
            "context_resets": self.context_resets,
        }
        plain = base.encode(payload)
        packet = base.encode({"payload": payload, "sha256": hashlib.sha256(plain).hexdigest()})
        if len(packet) > LIMIT:
            raise ValueError("HC11_OVERSIZED_CHECKPOINT")
        return packet

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not 0 < len(raw) <= LIMIT:
            raise ValueError("HC11_BAD_CHECKPOINT")
        try:
            packet = json.loads(raw)
            if type(packet) is not dict or set(packet) != {"payload", "sha256"}:
                raise ValueError("HC11_ENVELOPE")
            p = packet["payload"]
            fields = {"schema", "family", "minimum", "model", "witness",
                      "epoch", "conflicts", "context_resets"}
            if type(p) is not dict or set(p) != fields or p["schema"] != SCHEMA:
                raise ValueError("HC11_SCHEMA")
            if hashlib.sha256(base.encode(p)).hexdigest() != packet["sha256"]:
                raise ValueError("HC11_HASH")
            out = cls(p["family"], p["minimum"])
            raw_model = p["model"]
            if type(raw_model) is not str:
                raise ValueError("HC11_MODEL_TYPE")
            model_bytes = raw_model.encode("ascii")
            out.model = (base.DualRegimeCausalCells.restore(model_bytes) if out.family == "native"
                         else control.ConventionalContextModel.restore(model_bytes))
            seen = set()
            if type(p["witness"]) is not list or len(p["witness"]) > 64:
                raise ValueError("HC11_WITNESS_COUNT")
            for v in p["witness"]:
                if type(v) is not list or len(v) != 4:
                    raise ValueError("HC11_WITNESS_SHAPE")
                s, a, nxt, count = v
                base.valid_state(s)
                base.valid_action(a)
                base.valid_state(nxt)
                if nxt not in (s, s ^ (1 << a)) or type(count) is not int or count not in (1, 2):
                    raise ValueError("HC11_WITNESS_VALUE")
                if (s, a) in seen:
                    raise ValueError("HC11_DUPLICATE_WITNESS")
                seen.add((s, a))
                out.witness[(s, a)] = (nxt, count)
            for name in ("epoch", "conflicts", "context_resets"):
                if type(p[name]) is not int or not 0 <= p[name] <= 100000:
                    raise ValueError("HC11_COUNTER")
                setattr(out, name, p[name])
            if out.epoch != out.conflicts + out.context_resets:
                raise ValueError("HC11_COUNTER_RELATION")
            if out.snapshot() != raw:
                raise ValueError("HC11_NONCANONICAL")
            return out
        except (TypeError, ValueError, KeyError, UnicodeError, OverflowError) as exc:
            raise ValueError("HC11_BAD_CHECKPOINT") from exc
