"""Hidden synthetic worlds for WSP51. Learner receives only action replies."""
import hashlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "WSP-50"))
from frozen_world import rng_for
from synthesis import gate


def bit_for(tag, width):
    return rng_for(tag + "|parameters").randrange(width)


class World:
    def __init__(self, width, family, tag):
        if family not in ("inc_rol_xorbit", "xor_rol_dec", "rol_xorbit_inc",
                          "random_map", "quadratic_second", "broken_spine"):
            raise ValueError("family")
        self.width, self.family, self.tag = width, family, tag
        self.size = 1 << width
        bit = bit_for(tag, width)
        self.bit = bit
        self.tapes = {
            "inc_rol_xorbit": (0, 2, 4 + bit),
            "xor_rol_dec": (4 + bit, 2, 1),
            "rol_xorbit_inc": (2, 4 + bit, 0),
            "broken_spine": (0, 2, 4 + bit),
        }

    def apply(self, action, x):
        if action not in (0, 1) or not 0 <= x < self.size:
            raise ValueError("transition")
        if action == 0:
            if self.family == "broken_spine":
                return hashlib.sha256((self.tag + "|spine|" + str(x)).encode()).digest()[0] & (self.size - 1)
            return (x + 1) % self.size
        if self.family == "random_map":
            return hashlib.sha256((self.tag + "|second|" + str(x)).encode()).digest()[0] & (self.size - 1)
        if self.family == "quadratic_second":
            return (x * x + 3 * x + self.bit) % self.size
        for k in self.tapes[self.family]:
            x = gate(x, k, self.width)
        return x

    def rollout(self, x, actions):
        for action in actions:
            x = self.apply(action, x)
        return x
