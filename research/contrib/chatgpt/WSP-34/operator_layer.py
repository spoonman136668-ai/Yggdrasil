"""WSP-34 generic numerical Boolean operator synapses. No named task operator exists here.

This is a preauthored universal polynomial basis plus local candidate elimination,
NOT discovery of a new primitive or a whole model built without observations.
"""
import hashlib
import json

MAGIC = b"WSP34-OP\\0"
COEFFICIENTS = tuple(tuple((m >> k) & 1 for k in range(8)) for m in range(256))

def _bit(v):
    if type(v) is not int or v not in (0, 1):
        raise ValueError("WSP34_NON_BINARY")
    return v

def basis(signal):
    if len(signal) != 3:
        raise ValueError("WSP34_BAD_SIGNAL")
    a, b, c = tuple(_bit(v) for v in signal)
    return (1, a, b, c, a*b, a*c, b*c, a*b*c)

def _eval(coeff, features):
    # GF(2) dot product, a generic numerical polynomial circuit.
    return sum(x*y for x, y in zip(coeff, features)) & 1

def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")

class OperatorLayer:
    def __init__(self, observations=(), linear_only=False):
        if type(linear_only) is not bool:
            raise ValueError("WSP34_BAD_ABLATION")
        self.linear_only = linear_only
        self.observations = ()
        self.eligible = [int(not linear_only or m < 16) for m in range(256)]
        # Each observation only touches generic eligibility synapses.
        for signal, value in observations:
            self.observe(signal, value)

    def observe(self, signal, value):
        signal = tuple(_bit(v) for v in signal)
        if len(signal) != 3:
            raise ValueError("WSP34_BAD_SIGNAL")
        value = _bit(value)
        row = (signal, value)
        if row in self.observations:
            return
        if any(old_signal == signal and old_value != value
               for old_signal, old_value in self.observations):
            raise ValueError("WSP34_CONTRADICTORY_OBSERVATION")
        features = basis(signal)
        self.eligible = [alive * int(_eval(coeff, features) == value)
                         for alive, coeff in zip(self.eligible, COEFFICIENTS)]
        self.observations = (*self.observations, row)

    def predict(self, signal):
        features = basis(signal)
        voting = [0, 0]
        for alive, coeff, mask in zip(self.eligible, COEFFICIENTS, range(256)):
            if alive:
                voting[_eval(coeff, features)] += (1 << (8 - mask.bit_count()))
        return int(voting[1] > voting[0])  # tie, including no candidates, -> zero

    def snapshot(self):
        payload = _canon({"schema":"wsp34.operator.v1",
                          "linear_only":self.linear_only,
                          "observations":self.observations,
                          "eligible":"".join(str(x) for x in self.eligible)})
        return MAGIC + len(payload).to_bytes(4, "big") + payload + hashlib.sha256(payload).digest()

    @classmethod
    def restore(cls, raw):
        if not isinstance(raw, bytes) or not raw.startswith(MAGIC) or len(raw) < len(MAGIC)+36:
            raise ValueError("WSP34_BAD_CHECKPOINT")
        n = int.from_bytes(raw[len(MAGIC):len(MAGIC)+4], "big")
        payload = raw[len(MAGIC)+4:len(MAGIC)+4+n]
        if len(raw) != len(MAGIC)+4+n+32 or hashlib.sha256(payload).digest() != raw[-32:]:
            raise ValueError("WSP34_CHECKPOINT_DIGEST")
        d = json.loads(payload)
        if d.get("schema") != "wsp34.operator.v1":
            raise ValueError("WSP34_CHECKPOINT_SCHEMA")
        restored = cls(((tuple(s), v) for s, v in d["observations"]), d["linear_only"])
        if "".join(str(x) for x in restored.eligible) != d["eligible"] or restored.snapshot() != raw:
            raise ValueError("WSP34_CHECKPOINT_STATE")
        return restored
