"""WSP-10: directly programmed sparse threshold circuit, public synthetic DEV.

All TASK-SPECIFIC synaptic weights start zero. A deterministic compiler receives
an ENTIRE Boolean truth-table specification and writes connection weights.
The runtime is a homogeneous weighted-threshold circuit, NOT a learner;
no new primitive types or labels are inferred from unseen evidence.
"""
from __future__ import annotations

import hashlib
import json

SCHEMA = "wsp10.direct-crossbar-state.v1"
MAGIC = b"WSPX"
GRADIENT_STEPS = 0


def checked_bits(bits: tuple[int, ...], n: int) -> tuple[int, ...]:
    if (type(bits) is not tuple or len(bits) != n or
            any(type(b) is not int or b not in (0, 1) for b in bits)):
        raise ValueError("WSP10_INVALID_INPUT_BITS")
    return bits


def checked_mask(n: int, mask: int) -> None:
    if type(n) is not int or n not in (2, 3):
        raise ValueError("WSP10_UNSUPPORTED_INPUT_DIMENSION")
    if type(mask) is not int or not 0 <= mask < (1 << (1 << n)):
        raise ValueError("WSP10_INVALID_TRUTH_TABLE")


class DirectCrossbar:
    """A fixed universal AND/OR layout; task-specific active EDGES are weights.

    Sites are not associative state/label slots: each n-input threshold site
    becomes an executable minterm gate only after the compiler turns on its
    n polarity input edges; the output link is a separately programmed edge.
    A complete truth table is the compiler input; this is not online learning.
    """

    def __init__(self, n: int):
        checked_mask(n, 0)
        self.n = n
        self.sites = 1 << n
        self.stride = 2 * n + 1
        self.weights = [0] * (self.sites * self.stride)

    @property
    def architecture_sha256(self) -> str:
        spec = ("wsp10-crossbar-v1|n=%d|sites=%d|stride=%d|thresholds=n,1"
                % (self.n, self.sites, self.stride))
        return hashlib.sha256(spec.encode("ascii")).hexdigest()

    @classmethod
    def from_spec(cls, n: int, mask: int) -> "DirectCrossbar":
        checked_mask(n, mask)
        c = cls(n)
        for pattern in range(1 << n):
            if not (mask >> pattern) & 1:
                continue
            base = pattern * c.stride
            # One physical/potential synaptic incidence per polarity.
            # Exactly one polarity is connected per bit of each active gate.
            for bit in range(n):
                polarity = (pattern >> bit) & 1
                c.weights[base + 2 * bit + (1 - polarity)] = 1
            c.weights[base + 2 * n] = 1  # gate -> OR output
        return c

    def evaluate(self, bits: tuple[int, ...]) -> int:
        checked_bits(bits, self.n)
        polarity = tuple(v for b in bits for v in (b, 1 - b))
        output_sum = 0
        for site in range(self.sites):
            base = site * self.stride
            # Same sum-and-threshold kernel for each gate; ALL new paths are
            # realized by weights, not runtime per-task Python dispatch.
            drive = sum(self.weights[base + j] * polarity[j]
                        for j in range(2 * self.n))
            gate = int(drive >= self.n)
            output_sum += self.weights[base + 2 * self.n] * gate
        return int(output_sum >= 1)

    def active_connections(self) -> int:
        return sum(self.weights)

    def programmed_sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.weights,
                separators=(",", ":")).encode("ascii")).hexdigest()

    def _canonical_weights(self) -> bool:
        if (len(self.weights) != self.sites * self.stride or
                any(type(w) is not int or w not in (0, 1)
                    for w in self.weights)):
            return False
        for pattern in range(self.sites):
            base = pattern * self.stride
            link = self.weights[base + 2 * self.n]
            for bit in range(self.n):
                correct = base + 2 * bit + (1 - ((pattern >> bit) & 1))
                opposite = base + 2 * bit + ((pattern >> bit) & 1)
                if self.weights[correct] != link or self.weights[opposite] != 0:
                    return False
        return True

    def snapshot(self) -> bytes:
        if not self._canonical_weights():
            raise ValueError("WSP10_NONCANONICAL_WEIGHTS")
        body = json.dumps({"schema": SCHEMA, "n": self.n,
                           "architecture_sha256": self.architecture_sha256,
                           "weights": self.weights},
                          sort_keys=True, separators=(",", ":")).encode("ascii")
        prefix = MAGIC + len(body).to_bytes(4, "big") + body
        return prefix + hashlib.sha256(prefix).digest()

    @classmethod
    def restore(cls, raw: bytes) -> "DirectCrossbar":
        if (type(raw) is not bytes or not 42 <= len(raw) <= 4096 or
                raw[:4] != MAGIC or
                len(raw) - 40 != int.from_bytes(raw[4:8], "big") or
                hashlib.sha256(raw[:-32]).digest() != raw[-32:]):
            raise ValueError("WSP10_CHECKPOINT_REJECTED")
        try:
            data = json.loads(raw[8:-32].decode("ascii"))
            if (type(data) is not dict or
                    set(data) != {"schema", "n", "architecture_sha256", "weights"} or
                    data["schema"] != SCHEMA or
                    type(data["n"]) is not int or data["n"] not in (2, 3) or
                    type(data["weights"]) is not list):
                raise ValueError("invalid schema")
            c = cls(data["n"])
            if data["architecture_sha256"] != c.architecture_sha256:
                raise ValueError("wrong architecture")
            c.weights = data["weights"][:]
            if not c._canonical_weights() or c.snapshot() != raw:
                raise ValueError("noncanonical")
            return c
        except (ValueError, TypeError, UnicodeError, OverflowError, KeyError):
            raise ValueError("WSP10_CHECKPOINT_REJECTED") from None
