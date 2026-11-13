"""DG1-HC03: contradiction-triggered executable microprogram cells.

Research-only synthetic mechanism. A cell carries four *explicitly biased*
parity-offset causal programs. It does not discover latent state dimensions,
infer general program syntax, or learn source physics beyond this frozen family.
No source/evaluator import and no regime label input.
"""
from __future__ import annotations

import hashlib
import json

SCHEMA = "yggdrasil.dg1-hc03.program-society.dev.v1"
ACTIONS = 4
SITES = 4
MAX_BANKS = 2
MAX_CHECKPOINT_BYTES = 1024


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def check_state(state):
    if type(state) is not int or not 0 <= state < (1 << SITES):
        raise ValueError("HC03_INVALID_PUBLIC_STATE")
    return state


def check_action(action):
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("HC03_INVALID_PUBLIC_ACTION")
    return action


def parity_context(state, action):
    check_state(state)
    check_action(action)
    return ((state >> ((action - 1) % SITES)) & 1) ^ (
        (state >> ((action + 1) % SITES)) & 1)


class CausalProgramSociety:
    """Two bounded causal-program cells, differentiated only by contradictions.

    Each action cell contains a single XOR-offset sign, or 'not yet known'.
    A contradiction can differentiate a blank alternative or reactivate a
    previously retained compatible program society. Never observes regime ID.
    """

    def __init__(self, *, bank_limit=MAX_BANKS, reactivate=True):
        if type(bank_limit) is not int or not 1 <= bank_limit <= MAX_BANKS:
            raise ValueError("HC03_INVALID_BANK_LIMIT")
        if type(reactivate) is not bool:
            raise ValueError("HC03_INVALID_REACTIVATION_FLAG")
        self.bank_limit = bank_limit
        self.reactivate = reactivate
        self.banks = [[None] * ACTIONS]
        self.active = 0
        self.updates = 0
        self.splits = 0
        self.reactivations = 0
        self.unresolved = 0

    def predict(self, before, action):
        check_state(before)
        check_action(action)
        flag = self.banks[self.active][action]
        if flag is None:
            return None
        effect = parity_context(before, action) ^ flag
        return before ^ (effect << action)

    def observe(self, before, action, after):
        """Update only from one genuine public physical before/action/after.

        Reject invalid reports before touching memory. A transition must
        change only the addressed physical bit or leave it unchanged.
        """
        check_state(before)
        check_action(action)
        check_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("HC03_NONLOCAL_PUBLIC_DELTA")
        effect = int(after != before)
        sign = parity_context(before, action) ^ effect
        current = self.banks[self.active]
        if current[action] not in (None, sign):
            alternatives = [i for i, bank in enumerate(self.banks)
                            if i != self.active and bank[action] == sign]
            if self.reactivate and alternatives:
                # Previously acquired evidence is not overwritten.
                self.active = alternatives[0]
                self.reactivations += 1
            elif len(self.banks) < self.bank_limit:
                self.banks.append([None] * ACTIONS)
                self.active = len(self.banks) - 1
                self.splits += 1
            elif not self.reactivate:
                # Source-only destructive control: no archived reactivation.
                self.banks[self.active] = [None] * ACTIONS
            else:
                # No admissible causal explanation within fixed capacity.
                # Preserve old program; do not invent an overwrite.
                self.unresolved += 1
                self.updates += 1
                return False
        self.banks[self.active][action] = sign
        self.updates += 1
        return True

    @property
    def logical_rule_bits(self):
        # Fixed capacity, not Python heap size: 2 bits x 4 actions x 2 cells.
        return 2 * ACTIONS * MAX_BANKS

    def snapshot(self):
        payload = {
            "schema": SCHEMA, "bank_limit": self.bank_limit,
            "reactivate": self.reactivate, "banks": self.banks,
            "active": self.active, "updates": self.updates,
            "splits": self.splits, "reactivations": self.reactivations,
            "unresolved": self.unresolved,
        }
        raw = canonical(payload)
        result = canonical({
            "payload": payload, "sha256": hashlib.sha256(raw).hexdigest()
        })
        if len(result) > MAX_CHECKPOINT_BYTES:
            raise OverflowError("HC03_CHECKPOINT_BUDGET")
        return result

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not 0 < len(raw) <= MAX_CHECKPOINT_BYTES:
            raise ValueError("HC03_UNTRUSTED_CHECKPOINT")
        try:
            env = json.loads(raw)
            if type(env) is not dict or set(env) != {"payload", "sha256"}:
                raise ValueError("HC03_ENVELOPE")
            p = env["payload"]
            required = {"schema", "bank_limit", "reactivate", "banks", "active",
                        "updates", "splits", "reactivations", "unresolved"}
            if type(p) is not dict or set(p) != required or p["schema"] != SCHEMA:
                raise ValueError("HC03_SCHEMA")
            if hashlib.sha256(canonical(p)).hexdigest() != env["sha256"]:
                raise ValueError("HC03_CHECKSUM")
            model = cls(bank_limit=p["bank_limit"], reactivate=p["reactivate"])
            banks = p["banks"]
            if (type(banks) is not list or
                    not 1 <= len(banks) <= model.bank_limit or
                    any(type(row) is not list or len(row) != ACTIONS or
                        any(flag is not None and
                            (type(flag) is not int or flag not in (0, 1))
                            for flag in row) for row in banks)):
                raise ValueError("HC03_BANK_CONTENT")
            active = p["active"]
            if type(active) is not int or not 0 <= active < len(banks):
                raise ValueError("HC03_ACTIVE_INDEX")
            for field in ("updates", "splits", "reactivations", "unresolved"):
                if type(p[field]) is not int or not 0 <= p[field] <= 100000:
                    raise ValueError("HC03_COUNTER_INVALID")
            if p["splits"] > len(banks) - 1 or p["reactivations"] > p["updates"]:
                raise ValueError("HC03_COUNT_DRIFT")
            model.banks = [list(row) for row in banks]
            model.active = active
            for field in ("updates", "splits", "reactivations", "unresolved"):
                setattr(model, field, p[field])
            if model.snapshot() != raw:
                raise ValueError("HC03_NONCANONICAL")
            return model
        except (UnicodeError, TypeError, ValueError, KeyError,
                OverflowError, json.JSONDecodeError) as error:
            raise ValueError("HC03_UNTRUSTED_CHECKPOINT") from error
