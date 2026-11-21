"""KNOW35 DEV: two locally gated, persistent causal-regime Beta banks.

This is a deterministic engineering candidate. There is NO preregistered
held experiment or native scientific result here. Do not call KNOW34 proof(),
private_witness(), owner checkpoints or protected original-world sources.
The learner receives only (t, public x, observed binary consequence y).
No phase label, true law, seed or oracle is supplied to observe().
"""
from __future__ import annotations

import json
from know33_local_metaplastic_dev import Beta, canonical, digest

SCHEMA = "yggdrasil.know35.two-bank-cell-state.dev.v1"
EVENT_LIMIT = 256
CELL_COUNT = 8
BANKS = 2
SAMPLES_PER_BANK = 6
SWITCH_RATIO = 2.0
MAX_BYTES = 4096


def require(ok, label):
    if not ok:
        raise ValueError("YGG_KNOW35_" + label)


class TwoBankCells:
    """Four adjacent-cell gates select between two capped, persistent banks.

    A six-witness prior bank is never overwritten. A contradiction can switch
    to a second bank; later contradictory evidence can reselect the first.
    The local gate reads one current cell's two predictive likelihoods, NOT
    hidden phase/source identities. Each bank/cell freezes at six witnesses.
    This is intentionally only a two-regime toy with a known noise weakness.
    """

    def __init__(self):
        self.banks = [[Beta() for _ in range(CELL_COUNT)] for _ in range(BANKS)]
        self.seen = [[0] * CELL_COUNT for _ in range(BANKS)]
        self.active = [0] * (CELL_COUNT // 2)
        self.received = 0
        self.switches = 0

    def bank_prob(self, bank, x):
        require(type(bank) is int and 0 <= bank < BANKS
                and type(x) is int and 0 <= x < CELL_COUNT, "READOUT")
        return self.banks[bank][x].prob()

    def prob(self, x):
        require(type(x) is int and 0 <= x < CELL_COUNT, "READOUT")
        return self.bank_prob(self.active[x // 2], x)

    def observe(self, t, x, y):
        require(type(t) is int and t == self.received and t < EVENT_LIMIT
                and type(x) is int and 0 <= x < CELL_COUNT
                and type(y) is int and y in (0, 1), "EVENT")
        group = x // 2
        current = self.active[group]
        other = 1 - current
        if self.seen[current][x] == SAMPLES_PER_BANK:
            q = self.bank_prob(current, x)
            alt = self.bank_prob(other, x)
            likelihood = q if y else 1.0 - q
            other_likelihood = alt if y else 1.0 - alt
            if other_likelihood > SWITCH_RATIO * likelihood:
                self.active[group] = other
                current = other
                self.switches += 1
        if self.seen[current][x] < SAMPLES_PER_BANK:
            self.banks[current][x].update(y, 1.0)
            self.seen[current][x] += 1
        self.received += 1

    def state(self):
        return {
            "schema": SCHEMA,
            "banks": [[cell.state() for cell in bank] for bank in self.banks],
            "seen": self.seen,
            "active": self.active,
            "received": self.received,
            "switches": self.switches,
            "original_source": False,
        }

    def checkpoint(self):
        raw = canonical(self.state())
        require(len(raw) < MAX_BYTES, "CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha):
        require(type(raw) is bytes and len(raw) < MAX_BYTES
                and digest(raw) == expected_sha, "CHECKSUM")
        try:
            def unique(pairs):
                out = {}
                for key, value in pairs:
                    require(key not in out, "DUPLICATE_KEY")
                    out[key] = value
                return out

            data = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            model = cls()
            require(type(data) is dict and set(data) == set(model.state())
                    and data["schema"] == SCHEMA
                    and data["original_source"] is False
                    and type(data["received"]) is int
                    and 0 <= data["received"] <= EVENT_LIMIT
                    and type(data["switches"]) is int
                    and 0 <= data["switches"] <= data["received"]
                    and type(data["active"]) is list
                    and len(data["active"]) == CELL_COUNT // 2
                    and all(type(v) is int and v in (0, 1)
                            for v in data["active"])
                    and type(data["seen"]) is list
                    and len(data["seen"]) == BANKS
                    and type(data["banks"]) is list
                    and len(data["banks"]) == BANKS,
                    "STATE_SHAPE")
            for bank in range(BANKS):
                n = data["seen"][bank]
                states = data["banks"][bank]
                require(type(n) is list and len(n) == CELL_COUNT
                        and type(states) is list and len(states) == CELL_COUNT,
                        "BANK_SHAPE")
                for x in range(CELL_COUNT):
                    require(type(n[x]) is int
                            and 0 <= n[x] <= SAMPLES_PER_BANK
                            and type(states[x]) is list and len(states[x]) == 2
                            and all(type(v) in (int, float) for v in states[x]),
                            "BANK_CELL")
                    beta = Beta(*states[x])
                    # Every update contributes exactly one unit of evidence.
                    require(beta.a + beta.b == 2 + n[x],
                            "BANK_WITNESS_COUNT")
                    model.banks[bank][x] = beta
            require(sum(map(sum, data["seen"])) <= data["received"],
                    "WITNESS_BUDGET")
            model.seen = data["seen"]
            model.active = data["active"]
            model.received = data["received"]
            model.switches = data["switches"]
            require(model.checkpoint() == raw, "NONCANONICAL")
            return model
        except (KeyError, ValueError, TypeError, UnicodeError,
                OverflowError) as exc:
            raise ValueError("YGG_KNOW35_COLD_REJECT") from exc
