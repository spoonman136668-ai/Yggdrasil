"""CCE03: bounded, action-conditioned local causal-delta contract composition.

Development-only: six public bits and three public actions. A cell for every
(action, target) retains 16 small hypotheses over zero, one or two *other*
input bits. Selection uses prequential Brier plus a frozen complexity price.
Neither source-world rules nor second-step outcomes enter training.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math

BITS = 6
ACTIONS = 3
TRAIN = 768
SCHEMA = "yggdrasil.y2.cce03.v1"
SUBSETS = tuple(((),) + tuple((i,) for i in range(BITS - 1)) +
                tuple(itertools.combinations(range(BITS - 1), 2)))


def check_event(state: int, action: int, next_state: int | None = None) -> None:
    if (type(state) is not int or not 0 <= state < 64
            or type(action) is not int or not 0 <= action < ACTIONS
            or (next_state is not None and
                (type(next_state) is not int or not 0 <= next_state < 64))):
        raise ValueError("CCE03_PUBLIC_EVENT_INVALID")


def subsets_for(target: int) -> tuple[tuple[int, ...], ...]:
    other = [i for i in range(BITS) if i != target]
    return (((),) + tuple((i,) for i in other) +
            tuple(itertools.combinations(other, 2)))


class Contract:
    def __init__(self, parents: tuple[int, ...]) -> None:
        self.parents = parents
        self.counts: dict[int, list[int]] = {}
        self.prequential_brier = 0.0
        self.n = 0

    def key(self, state: int) -> int:
        return sum(((state >> parent) & 1) << j
                   for j, parent in enumerate(self.parents))

    def predict_flip(self, state: int) -> float:
        failures, successes = self.counts.get(self.key(state), (0, 0))
        return (successes + 1) / (failures + successes + 2)

    def observe(self, state: int, flip: int) -> None:
        if type(flip) is not int or flip not in (0, 1):
            raise ValueError("CCE03_FLIP_INVALID")
        if self.n >= TRAIN:
            raise ValueError("CCE03_OVER_BUDGET")
        p = self.predict_flip(state)
        self.prequential_brier += (p - flip) ** 2
        pair = self.counts.setdefault(self.key(state), [0, 0])
        pair[flip] += 1
        self.n += 1

    def score(self) -> float:
        return self.prequential_brier + 0.5 * (2 ** len(self.parents)) * math.log2(1 + self.n)

    def dump(self) -> dict:
        return {"parents": list(self.parents), "counts": [[k, *self.counts[k]] for k in sorted(self.counts)],
                "n": self.n, "prequential_brier": self.prequential_brier}

    @classmethod
    def load(cls, data: dict, allowed_parents: set[tuple[int, ...]]) -> "Contract":
        if (type(data) is not dict or set(data) != {"parents", "counts", "n", "prequential_brier"}
                or type(data["parents"]) is not list or type(data["counts"]) is not list):
            raise ValueError("CCE03_STATE_INVALID")
        parents = tuple(data["parents"])
        if parents not in allowed_parents:
            raise ValueError("CCE03_PARENTS_INVALID")
        obj = cls(parents)
        if (type(data["n"]) is not int or not 0 <= data["n"] <= TRAIN
                or type(data["prequential_brier"]) not in (float, int)
                or not math.isfinite(data["prequential_brier"])
                or not 0 <= data["prequential_brier"] <= data["n"]):
            raise ValueError("CCE03_LOSS_INVALID")
        for record in data["counts"]:
            if (type(record) is not list or len(record) != 3 or
                    any(type(v) is not int for v in record) or
                    not 0 <= record[0] < 2 ** len(parents) or
                    record[0] in obj.counts or
                    any(not 0 <= n <= TRAIN for n in record[1:])):
                raise ValueError("CCE03_COUNTS_INVALID")
            obj.counts[record[0]] = record[1:]
        if sum(sum(pair) for pair in obj.counts.values()) != data["n"]:
            raise ValueError("CCE03_TOTAL_MISMATCH")
        obj.n = data["n"]
        obj.prequential_brier = float(data["prequential_brier"])
        return obj


class Ecology:
    def __init__(self) -> None:
        self.candidates = {(a, i): [Contract(parents) for parents in subsets_for(i)]
                           for a in range(ACTIONS) for i in range(BITS)}
        self.full = {(a, i): Contract(tuple(range(BITS)))
                     for a in range(ACTIONS) for i in range(BITS)}
        self.action_n = [0] * ACTIONS
        self.n = 0
        self.selected: dict[tuple[int, int], int] = {}
        self.selected_one: dict[tuple[int, int], int] = {}
        self.frozen = False

    def observe(self, state: int, action: int, next_state: int) -> None:
        check_event(state, action, next_state)
        if self.frozen or self.n >= TRAIN:
            raise ValueError("CCE03_FROZEN_OR_OVER_BUDGET")
        for target in range(BITS):
            flip = ((state ^ next_state) >> target) & 1
            for candidate in self.candidates[(action, target)]:
                candidate.observe(state, flip)
            self.full[(action, target)].observe(state, flip)
        self.action_n[action] += 1
        self.n += 1

    def freeze(self) -> None:
        if self.frozen or self.n != TRAIN or not all(self.action_n):
            raise ValueError("CCE03_FREEZE_REQUIRES_FULL_BUDGET")
        for slot, models in self.candidates.items():
            order = sorted(range(len(models)), key=lambda j: (
                models[j].score(), len(models[j].parents), models[j].parents))
            self.selected[slot] = order[0]
            self.selected_one[slot] = next(j for j in order if len(models[j].parents) <= 1)
        self.frozen = True

    def predict_step(self, state: int, action: int, *, mode: str = "cce") -> int:
        check_event(state, action)
        if not self.frozen or mode not in ("cce", "one", "pooled", "full"):
            raise ValueError("CCE03_PREDICTION_INVALID")
        result = state
        for target in range(BITS):
            slot = (action, target)
            models = self.candidates[slot]
            if mode == "full":
                model = self.full[slot]
            elif mode == "pooled":
                model = models[0]
            elif mode == "one":
                model = models[self.selected_one[slot]]
            else:
                model = models[self.selected[slot]]
            if model.predict_flip(state) > 0.5:
                result ^= 1 << target
        return result

    def predict_two(self, state: int, first: int, second: int,
                    *, mode: str = "cce") -> int:
        return self.predict_step(self.predict_step(state, first, mode=mode),
                                 second, mode=mode)

    def chosen_parents(self, mode: str = "cce") -> dict[str, list[int]]:
        if not self.frozen or mode not in ("cce", "one"):
            raise ValueError("CCE03_NOT_FROZEN")
        selection = self.selected if mode == "cce" else self.selected_one
        return {f"{a}:{i}": list(self.candidates[(a, i)][selection[(a, i)]].parents)
                for a in range(ACTIONS) for i in range(BITS)}

    def snapshot(self) -> bytes:
        records = []
        for a in range(ACTIONS):
            for i in range(BITS):
                records.append({"action": a, "target": i,
                                "candidates": [c.dump() for c in self.candidates[a, i]],
                                "full": self.full[a, i].dump(),
                                "selected": self.selected.get((a, i)),
                                "selected_one": self.selected_one.get((a, i))})
        body = json.dumps({"schema": SCHEMA, "n": self.n,
                           "action_n": self.action_n, "frozen": self.frozen,
                           "records": records}, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("ascii")
        return b"CCE03." + hashlib.sha256(body).hexdigest().encode("ascii") + b"." + body

    @classmethod
    def restore(cls, checkpoint: bytes) -> "Ecology":
        if type(checkpoint) is not bytes:
            raise ValueError("CCE03_CHECKPOINT_REJECTED")
        parts = checkpoint.split(b".", 2)
        if (len(parts) != 3 or parts[0] != b"CCE03" or len(parts[1]) != 64 or
                hashlib.sha256(parts[2]).hexdigest().encode("ascii") != parts[1]):
            raise ValueError("CCE03_CHECKPOINT_REJECTED")
        try:
            data = json.loads(parts[2]); obj = cls()
            if (type(data) is not dict or set(data) != {"schema", "n", "action_n", "frozen", "records"}
                    or data["schema"] != SCHEMA or type(data["frozen"]) is not bool
                    or type(data["n"]) is not int or not 0 <= data["n"] <= TRAIN
                    or type(data["action_n"]) is not list or len(data["action_n"]) != ACTIONS
                    or any(type(v) is not int or not 0 <= v <= TRAIN for v in data["action_n"])
                    or sum(data["action_n"]) != data["n"]
                    or type(data["records"]) is not list or len(data["records"]) != ACTIONS * BITS
                    or (data["frozen"] and data["n"] != TRAIN)):
                raise ValueError("CCE03_METADATA_INVALID")
            obj.n = data["n"]; obj.action_n = data["action_n"][:]; obj.frozen = data["frozen"]
            for index, record in enumerate(data["records"]):
                a, i = divmod(index, BITS); slot = (a, i)
                if (type(record) is not dict or set(record) !=
                    {"action", "target", "candidates", "full", "selected", "selected_one"}
                    or type(record["action"]) is not int or record["action"] != a
                    or type(record["target"]) is not int or record["target"] != i
                    or type(record["candidates"]) is not list or len(record["candidates"]) != 16):
                    raise ValueError("CCE03_RECORD_INVALID")
                possible = subsets_for(i)
                models = [Contract.load(v, {possible[j]}) for j, v in enumerate(record["candidates"])]
                full = Contract.load(record["full"], {tuple(range(BITS))})
                if any(v.n != obj.action_n[a] for v in [*models, full]):
                    raise ValueError("CCE03_RECORD_COUNTS_INVALID")
                obj.candidates[slot] = models; obj.full[slot] = full
                if obj.frozen:
                    for field, selection in (("selected", obj.selected),
                                             ("selected_one", obj.selected_one)):
                        value = record[field]
                        if (type(value) is not int or not 0 <= value < len(models)
                                or (field == "selected_one" and len(models[value].parents) > 1)):
                            raise ValueError("CCE03_SELECTION_INVALID")
                        selection[slot] = value
                    order = sorted(range(len(models)), key=lambda j: (
                        models[j].score(), len(models[j].parents), models[j].parents))
                    if (obj.selected[slot] != order[0]
                            or obj.selected_one[slot] != next(j for j in order if len(models[j].parents) <= 1)):
                        raise ValueError("CCE03_SELECTION_RECOMPUTE_MISMATCH")
                elif record["selected"] is not None or record["selected_one"] is not None:
                    raise ValueError("CCE03_SELECTION_PREMATURE")
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError) as exc:
            raise ValueError("CCE03_CHECKPOINT_REJECTED") from exc
