"""Raw Unicode signal associations written directly to numeric weights (no tokens)."""
from __future__ import annotations

from functools import lru_cache
from collections import Counter
import hashlib
import json
import math
import unicodedata

WIDTH = 2048
GRAMS = (3, 4, 5)
MARGIN = 0.22
SIGNAL_THRESHOLD = 0.70
MIN_SIGNALS = 3
SGD_EPOCHS = 80
SGD_RATE = 0.75


@lru_cache(maxsize=4096)
def features(raw: str) -> tuple[tuple[int, float], ...]:
    if not isinstance(raw, str) or not raw or len(raw.encode("utf-8")) > 512:
        raise ValueError("raw UTF-8 utterance required")
    # Casefold + Unicode normalization are signal conditioning, not lexical tokens.
    stream = "\u0002" + unicodedata.normalize("NFC", raw).casefold() + "\u0003"
    bins: Counter[int] = Counter()
    for length in GRAMS:
        for i in range(len(stream) - length + 1):
            fragment = stream[i:i + length].encode("utf-8")
            index = int.from_bytes(hashlib.blake2s(fragment, digest_size=4).digest(), "big") % WIDTH
            bins[index] += 1
    scale = math.sqrt(sum(v * v for v in bins.values()))
    return tuple(sorted((i, float(v) / scale) for i, v in bins.items()))


class DirectWeights:
    def __init__(self) -> None:
        self.weights = [[0.0] * WIDTH for _ in range(3)]

    def observe(self, text: str, actuator: int, succeeded: bool) -> None:
        if actuator not in (0, 1, 2) or type(succeeded) is not bool:
            raise ValueError("invalid paid intervention record")
        gain = 2.0 if succeeded else -1.0
        row = self.weights[actuator]
        for index, value in features(text):
            row[index] += gain * value

    def scores(self, text: str) -> tuple[float, float, float]:
        f = features(text)
        return tuple(sum(row[i] * v for i, v in f) for row in self.weights)

    def predict(self, text: str) -> int | None:
        f = features(text)
        scores = self.scores(text)
        order = sorted(range(3), key=lambda i: (-scores[i], i))
        margin = scores[order[0]] - scores[order[1]]
        signals = sum(
            1 for idx, _ in f
            if max(row[idx] for row in self.weights) -
               min(row[idx] for row in self.weights) >= SIGNAL_THRESHOLD
        )
        return order[0] if margin >= MARGIN and signals >= MIN_SIGNALS else None

    def snapshot(self) -> str:
        payload = {"width": WIDTH, "weights": self.weights}
        canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True, allow_nan=False)
        checksum = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return json.dumps({"schema": "wsp88.direct-weights.v1",
                           "sha256": checksum, "payload": payload},
                          sort_keys=True, separators=(",", ":"), allow_nan=False)

    @classmethod
    def restore(cls, snapshot: str) -> "DirectWeights":
        envelope = json.loads(snapshot)
        if envelope.get("schema") != "wsp88.direct-weights.v1":
            raise ValueError("snapshot schema mismatch")
        payload = envelope["payload"]
        canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True, allow_nan=False)
        if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != envelope.get("sha256"):
            raise ValueError("snapshot hash mismatch")
        weights = payload.get("weights")
        if payload.get("width") != WIDTH or not isinstance(weights, list) or len(weights) != 3:
            raise ValueError("wrong matrix shape")
        if any(not isinstance(row, list) or len(row) != WIDTH or
               any(type(x) is not float or not math.isfinite(x) for x in row)
               for row in weights):
            raise ValueError("invalid numerical weights")
        result = cls()
        result.weights = [list(row) for row in weights]
        return result


class GradientSoftmaxControl:
    """Ordinary fully trained comparator; identical observed labels/features."""

    def __init__(self) -> None:
        self.weights = [[0.0] * WIDTH for _ in range(3)]

    def fit(self, labeled: tuple[tuple[str, int], ...]) -> None:
        if not labeled:
            raise ValueError("no paid data")
        self.weights = [[0.0] * WIDTH for _ in range(3)]
        cached = tuple((features(text), action) for text, action in labeled)
        for _ in range(SGD_EPOCHS):
            for f, truth in cached:
                scores = [sum(row[i] * v for i, v in f) for row in self.weights]
                highest = max(scores)
                raw = [math.exp(v - highest) for v in scores]
                probs = [v / sum(raw) for v in raw]
                for actuator in range(3):
                    delta = SGD_RATE * (float(truth == actuator) - probs[actuator])
                    row = self.weights[actuator]
                    for idx, value in f:
                        row[idx] += delta * value

    def predict(self, text: str) -> int:
        f = features(text)
        scores = [sum(row[i] * v for i, v in f) for row in self.weights]
        return max(range(3), key=lambda i: (scores[i], -i))


class LiteralLookup:
    def __init__(self) -> None:
        self.observations: dict[str, list[bool | None]] = {}

    def observe(self, text: str, action: int, succeeded: bool) -> None:
        if action not in (0, 1, 2):
            raise ValueError("bad action")
        self.observations.setdefault(text, [None, None, None])[action] = succeeded

    def predict(self, text: str) -> int | None:
        outcomes = self.observations.get(text)
        if outcomes is None or outcomes.count(True) != 1:
            return None
        return outcomes.index(True)
