"""WSP51: bounded generic instruction-chain synthesis from experience.

No source family, latent encoder or action1 rule reaches the learner. The
primitive grammar is nevertheless programmed; this is not arbitrary AI.
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "WSP-50"))
from coordinates import CycleModel


def gate(v, k, width):
    n = 1 << width
    if k == 0:
        return (v + 1) % n
    if k == 1:
        return (v - 1) % n
    if k == 2:
        return ((v << 1) | (v >> (width - 1))) & (n - 1)
    if k == 3:
        return (v >> 1) | ((v & 1) << (width - 1))
    return v ^ (1 << (k - 4))


class ProgramCatalog:
    def __init__(self, width):
        if width not in (4, 6, 8):
            raise ValueError("width")
        self.width = width
        self.n = 1 << width
        initial = tuple(range(self.n))
        self.tapes = [()]
        self.maps = [initial]
        signatures = {initial}
        wave = [(initial, ())]
        for _ in range(3):
            next_wave = []
            for values, tape in wave:
                for k in range(width + 4):
                    new = tuple(gate(v, k, width) for v in values)
                    if new not in signatures:
                        signatures.add(new)
                        grown = tape + (k,)
                        next_wave.append((new, grown))
                        self.maps.append(new)
                        self.tapes.append(grown)
            wave = next_wave
        assert len(self.maps) == len(self.tapes)
        self.full_mask = (1 << len(self.maps)) - 1

    def matching(self, observations):
        mask = self.full_mask
        for x, y in observations:
            mask &= sum((1 << i) for i, values in enumerate(self.maps) if values[x] == y)
        return mask

    def unanimous(self, mask, x):
        if not mask:
            return None
        predictions = {values[x] for i, values in enumerate(self.maps) if mask >> i & 1}
        return next(iter(predictions)) if len(predictions) == 1 else None

    def choose(self, mask, unavailable):
        choices = [x for x in range(self.n) if x not in unavailable]
        if not choices:
            return None
        indices = [i for i in range(len(self.maps)) if mask >> i & 1]
        if not indices:
            return choices[0]
        best = None
        best_score = -1
        for x in choices:
            counts = {}
            for i in indices:
                y = self.maps[i][x]
                counts[y] = counts.get(y, 0) + 1
            score = len(indices) ** 2 - sum(v * v for v in counts.values())
            if score > best_score:
                best, best_score = x, score
        return best


CATALOGS = {}


def catalog(width):
    if width not in CATALOGS:
        CATALOGS[width] = ProgramCatalog(width)
    return CATALOGS[width]


class LearnedProgram:
    """Numeric version-space register, learned coordinate/factual registers."""

    def __init__(self, width):
        self.width = width
        self.cycle = CycleModel(width)
        self.bank = catalog(width)
        self.live = self.bank.full_mask
        self.observation_count = 0

    def record_cycle(self, label, index):
        self.cycle.record_cycle(label, index)

    def certify(self, terminal):
        self.cycle.certify(terminal)

    def observe(self, action, x, y):
        if action not in (0, 1) or not 0 <= x < (1 << self.width) or not 0 <= y < (1 << self.width):
            raise ValueError("source values")
        old, observed = self.cycle.fact(action, x)
        if observed and old != y:
            raise ValueError("contradictory deterministic source")
        self.cycle.observe(action, x, y)
        if self.cycle.valid and action == 1 and not observed:
            cx = self.cycle.coord(x)
            cy = self.cycle.coord(y)
            self.live &= sum(1 << i for i, values in enumerate(self.bank.maps) if values[cx] == cy)
        self.observation_count += 1

    def fact(self, action, x):
        return self.cycle.fact(action, x)

    def suggest_probe(self):
        if not self.cycle.valid:
            return None
        used = {self.cycle.coord(x) for x in range(self.cycle.size) if self.cycle.seen[1] >> x & 1}
        return self.bank.choose(self.live, used)

    def apply(self, action, x):
        y, known = self.cycle.fact(action, x)
        if known:
            return y
        if not self.cycle.valid:
            return None
        index = self.cycle.coord(x)
        if action == 0:
            return self.cycle.decode((index + 1) % self.cycle.size)
        predicted = self.bank.unanimous(self.live, index)
        return None if predicted is None else self.cycle.decode(predicted)

    def rollout(self, x, actions):
        for action in actions:
            if x is None:
                return None
            x = self.apply(action, x)
        return x

    def plan(self, start, goal):
        for actions in itertools.product((0, 1), repeat=3):
            if self.rollout(start, actions) == goal:
                return actions
        return None

    def snapshot(self):
        body = json.dumps(dict(schema="wsp51.program.v1", width=self.width,
                               cycle=self.cycle.snapshot().decode("ascii"), live=self.live,
                               observation_count=self.observation_count),
                          sort_keys=True, separators=(",", ":")).encode()
        return body + b"|" + hashlib.sha256(body).hexdigest().encode()

    @classmethod
    def restore(cls, checkpoint):
        try:
            body, checksum = checkpoint.rsplit(b"|", 1)
            if hashlib.sha256(body).hexdigest().encode() != checksum:
                raise ValueError("checksum")
            d = json.loads(body)
            if set(d) != {"schema", "width", "cycle", "live", "observation_count"} or d["schema"] != "wsp51.program.v1":
                raise ValueError("schema")
            m = cls(d["width"])
            m.cycle = CycleModel.restore(d["cycle"].encode("ascii"))
            m.live = d["live"]
            m.observation_count = d["observation_count"]
            if type(m.live) is not int or m.live < 0 or m.live > m.bank.full_mask:
                raise ValueError("mask")
            if type(m.observation_count) is not int or m.observation_count < 0:
                raise ValueError("count")
            if m.cycle.valid:
                rows = [(m.cycle.coord(x), m.cycle.coord(m.cycle.fact(1, x)[0]))
                        for x in range(m.cycle.size) if m.cycle.fact(1, x)[1]]
                if m.live != m.bank.matching(rows):
                    raise ValueError("version-space")
            elif m.live != m.bank.full_mask:
                raise ValueError("uncertified")
            if m.snapshot() != checkpoint:
                raise ValueError("canonical")
            return m
        except (ValueError, TypeError, KeyError, IndexError, AttributeError, UnicodeError):
            raise ValueError("checkpoint") from None
