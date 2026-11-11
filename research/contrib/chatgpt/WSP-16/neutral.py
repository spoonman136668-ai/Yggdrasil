"""WSP16 numerical neutral exploration after a witnessed contradiction."""
from __future__ import annotations
import hashlib
import json
import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/"WSP-15"))
from structural import (PlasticNand, LENGTHS, GATES, SEEDS, TRIALS, PUBLIC,
                        context, checked_context, mismatch, threshold)

OBSERVED = PUBLIC+(3,)
MAGIC = b"WSP16"
POLICY = "wsp16.neutral-reward.v1"


def checked_six(examples):
    if type(examples) is not tuple or len(examples) != 6:
        raise ValueError("WSP16_BAD_EXAMPLES")
    for pair, i in zip(examples, OBSERVED):
        if type(pair) is not tuple or len(pair) != 2:
            raise ValueError("WSP16_BAD_EXAMPLES")
        x, y = pair
        if checked_context(x) != context(i) or type(y) is not int or y not in (0, 1):
            raise ValueError("WSP16_BAD_EXAMPLES")
    return examples


class NeutralNand(PlasticNand):
    """Same75 synapses; only the numerical reward threshold changes."""
    def __init__(self, initial=None):
        super().__init__()
        self.neutral_accepts = self.improving_accepts = 0
        if initial is not None:
            restored = PlasticNand.restore(initial)
            self.rows = [row[:] for row in restored.rows]

    def adapt(self, examples, seed, mode="neutral"):
        checked_six(examples)
        if not self.canonical() or type(seed) is not int or seed not in SEEDS:
            raise ValueError("WSP16_BAD_STATE_OR_SEED")
        if mode not in ("neutral", "strict", "random", "disabled"):
            raise ValueError("WSP16_BAD_MODE")
        noise = random.Random(seed)
        for _ in range(TRIALS):
            j = noise.randrange(len(LENGTHS))
            k = noise.randrange(LENGTHS[j])
            candidate = [row[:] for row in self.rows]
            candidate[j] = [int(a == k) for a in range(LENGTHS[j])]
            old = mismatch(self.rows, examples)
            new = mismatch(candidate, examples)
            reward = {"neutral": threshold(old-new), "strict": threshold(old-new-1),
                      "random": 1, "disabled": 0}[mode]
            self.rows = [[a+reward*(b-a) for a, b in zip(before, after)]
                         for before, after in zip(self.rows, candidate)]
            self.neutral_accepts += reward*int(old == new)
            self.improving_accepts += reward*threshold(old-new-1)
            self.accepted += reward
            self.proposals += 1
            self.noise_draws += 2
            self.gate_evaluations += 2*len(examples)*GATES
            self.scalar_ops += 2*len(examples)*(2*sum(LENGTHS)+3*GATES+5)+3+3*sum(LENGTHS)
        return self

    def snapshot(self):
        base = super().snapshot().hex()
        body = json.dumps({"schema": POLICY, "synapses": base}, sort_keys=True,
                          separators=(",", ":")).encode("ascii")
        prefix = MAGIC+len(body).to_bytes(4, "big")+body
        return prefix+hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, raw):
        if (type(raw) is not bytes or not 41 <= len(raw) <= 4096 or raw[:5] != MAGIC
                or int.from_bytes(raw[5:9], "big") != len(raw)-41
                or hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP16_CHECKPOINT_REJECTED")
        try:
            d = json.loads(raw[9:-32].decode("ascii"))
            if type(d) is not dict or set(d) != {"schema", "synapses"} or d["schema"] != POLICY:
                raise ValueError("schema")
            obj = cls(bytes.fromhex(d["synapses"]))
            if obj.snapshot() != raw:
                raise ValueError("canonical")
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, OverflowError):
            raise ValueError("WSP16_CHECKPOINT_REJECTED") from None
