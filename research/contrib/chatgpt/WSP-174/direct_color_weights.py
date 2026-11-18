"""WSP178: directly programmed stochastic descendant-color weights.

This is an explicitly restricted, exact arithmetic experimental candidate.
For the SAME input features a conventional Dirichlet categorical estimator
has EXACTLY EQUIVALENT predictions: weight programming alone proves no gain.
No original simulator invocation, protected data, lease or deployment.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import hmac
import json

from public_boundary import N_COLORS, PublicEvidence
from stochastic_controls import descendants, validate_policy_input

SCHEMA = "yggdrasil.wsp178.direct-color-weights.v1"
MAX_FIT_RECORDS = 100000
MAX_WIRE_BYTES = 16384
MAX_CELLS = 50


def _reject_dupes(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("WSP178_DUPLICATE_KEY")
        result[k] = v
    return result


def _nonfinite(_: str) -> object:
    raise ValueError("WSP178_NONFINITE")


class DirectColorWeights:
    """Closed-form online direct programming of categorical output weights.

    Each key (action, strictly-downstream object) has five output probabilities.
    Starting from one unit pseudocount per class, after observing public
    output y, each weight is directly set to (D*p + onehot(y))/(D+1),
    D=5+n_observed. This is not a gradient, does not model graph structure
    and MUST be compared with an equivalently keyed Dirichlet reference.
    """

    def __init__(self) -> None:
        self._weights: dict[tuple[int, int], tuple[Fraction, ...]] = {}
        self._counts: dict[tuple[int, int], tuple[int, ...]] = {}
        self._frozen = False
        self.fit_records = 0
        self.fit_descendants = 0

    def fit_observed(self, record: PublicEvidence) -> None:
        if self._frozen:
            raise ValueError("WSP178_FIT_FROZEN")
        if type(record) is not PublicEvidence:
            raise ValueError("WSP178_PUBLIC_ONLY")
        if self.fit_records >= MAX_FIT_RECORDS:
            raise ValueError("WSP178_FIT_CAP")
        for target in descendants(record.action):
            key = (record.action, target)
            old_counts = self._counts.get(key, (0,) * N_COLORS)
            n = sum(old_counts)
            old_weights = self._weights.get(key, (Fraction(1, N_COLORS),) * N_COLORS)
            color = record.next[target][2]
            self._weights[key] = tuple(
                (Fraction(N_COLORS + n) * p + int(k == color)) / (N_COLORS + n + 1)
                for k, p in enumerate(old_weights)
            )
            self._counts[key] = tuple(c + int(k == color) for k, c in enumerate(old_counts))
            self.fit_descendants += 1
        self.fit_records += 1

    def freeze(self) -> None:
        self._frozen = True

    def forecast(self, policy_input: dict[str, object],
                 action: int) -> dict[int, tuple[float, ...]]:
        if not self._frozen:
            raise ValueError("WSP178_NOT_FROZEN")
        validate_policy_input(policy_input, action)
        prior = (Fraction(1, N_COLORS),) * N_COLORS
        return {target: tuple(float(x) for x in self._weights.get((action, target), prior))
                for target in descendants(action)}

    def summary(self) -> dict[str, object]:
        return {"schema": SCHEMA, "fit_records": self.fit_records,
                "fit_descendants": self.fit_descendants, "weight_cells": len(self._weights),
                "frozen": self._frozen}

    def canonical(self) -> bytes:
        if not self._frozen:
            raise ValueError("WSP178_NOT_FROZEN")
        cells = [[a, j, *self._counts[(a, j)]]
                 for a, j in sorted(self._weights)]
        return json.dumps(
            {"schema": SCHEMA, "fit_records": self.fit_records, "cells": cells},
            sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("ascii")

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()

    @classmethod
    def restore(cls, raw: bytes, digest: str) -> "DirectColorWeights":
        if type(raw) is not bytes or not (0 < len(raw) <= MAX_WIRE_BYTES):
            raise ValueError("WSP178_WIRE_SIZE")
        if (type(digest) is not str or len(digest) != 64 or
                any(c not in "0123456789abcdef" for c in digest) or
                not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), digest)):
            raise ValueError("WSP178_WIRE_HASH")
        try:
            payload = json.loads(raw.decode("ascii"), object_pairs_hook=_reject_dupes,
                                 parse_constant=_nonfinite)
        except (ValueError, UnicodeError, TypeError) as exc:
            raise ValueError("WSP178_WIRE_PARSE") from exc
        if (type(payload) is not dict or set(payload) != {"schema", "fit_records", "cells"}
                or payload["schema"] != SCHEMA):
            raise ValueError("WSP178_WIRE_SCHEMA")
        n = payload["fit_records"]
        if type(n) is not int or not 0 <= n <= MAX_FIT_RECORDS:
            raise ValueError("WSP178_FIT_COUNT")
        cells = payload["cells"]
        if type(cells) is not list or len(cells) > MAX_CELLS:
            raise ValueError("WSP178_CELL_COUNT")
        obj = cls()
        obj.fit_records = n
        for cell in cells:
            if type(cell) is not list or len(cell) != 2 + N_COLORS:
                raise ValueError("WSP178_CELL_SHAPE")
            action, target, *counts = cell
            if (type(action) is not int or type(target) is not int or
                    target not in descendants(action)):
                raise ValueError("WSP178_CELL_KEY")
            if any(type(c) is not int or c < 0 or c > n for c in counts):
                raise ValueError("WSP178_CELL_COUNTS")
            if not (0 < sum(counts) <= n):
                raise ValueError("WSP178_CELL_COUNTS")
            key = (action, target)
            if key in obj._weights:
                raise ValueError("WSP178_DUPLICATE_CELL")
            obj._counts[key] = tuple(counts)
            denominator = sum(counts) + N_COLORS
            obj._weights[key] = tuple(Fraction(c + 1, denominator) for c in counts)
            obj.fit_descendants += sum(counts)
        obj.freeze()
        if raw != obj.canonical():
            raise ValueError("WSP178_WIRE_NONCANONICAL")
        if obj.fit_descendants > n * 4:
            raise ValueError("WSP178_CELL_TOTAL")
        return obj
