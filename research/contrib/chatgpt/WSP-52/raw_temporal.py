"""WSP52 experimental raw-stream gradient controls; fixture-only, no hidden syntax.

No token IDs, delimiters, lexical hints or oracle latent labels. Gradients are
computed from observed before -> after physical states and undelimited bits.
This is *not* a scientific result or a security boundary.
"""
from __future__ import annotations
import hashlib
import json
import math
from dataclasses import dataclass

HIDDEN = 8
STATE_WIDTH = 32
PARAMETER_LIMIT = 65536
MAX_UPDATES = 20000


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _validate(row):
    before, after, bits = row.before, row.after, row.acoustic_bits
    for state in (before, after):
        if type(state) is not tuple or len(state) != 8 or any(type(v) is not int or v not in range(4) for v in state):
            raise ValueError("invalid physical state")
    if type(bits) is not str or not 12 <= len(bits) <= 18 or set(bits)-{"0", "1"}:
        raise ValueError("invalid raw bit stream")
    if type(row.action_cost) is not int or row.action_cost != 1 or type(row.reset_cost) is not int or row.reset_cost != 0:
        raise ValueError("unaccounted environment action")
    return before, after, bits


def _initial_value(key, index):
    data = hashlib.sha256(f"WSP52|raw-rnn|{key}|{index}".encode("ascii")).digest()
    return (int.from_bytes(data[:4], "big") / (2**32) - 0.5) * 0.12


class RawPhysicalRNN:
    """Eight-hidden-state recurrent raw-bit learner with manual full BPTT.

    Trainable: physical state initializer, binary-time recurrence and 32-output
    physical-state classifier. The fixed continuity bias is shared simulator
    knowledge, not a target label. No packages or accelerators required.
    """
    def __init__(self, *, seed="independent-conventional"):
        self.seed = seed
        shapes = {"init": (HIDDEN, STATE_WIDTH), "init_bias": (HIDDEN,),
                  "recur": (HIDDEN, HIDDEN), "bit": (HIDDEN,),
                  "recur_bias": (HIDDEN,), "out": (STATE_WIDTH, HIDDEN),
                  "out_bias": (STATE_WIDTH,)}
        self.shapes = shapes
        self.weights = {}
        for name, shape in shapes.items():
            n = math.prod(shape)
            self.weights[name] = [_initial_value(seed + name, i) for i in range(n)]
        self.updates = 0
        self.learning_rate = 0.035
        assert self.parameter_count() <= PARAMETER_LIMIT

    def parameter_count(self):
        return sum(len(w) for w in self.weights.values())

    def _forward(self, before, bits):
        w = self.weights
        x = [0.0] * STATE_WIDTH
        for i, value in enumerate(before):
            x[4*i+value] = 1.0
        hidden = [math.tanh(w["init_bias"][j] + sum(w["init"][j*32+k] * x[k] for k in range(32))) for j in range(HIDDEN)]
        states = [hidden]
        for bit in bits:
            v = 1.0 if bit == "1" else -1.0
            hidden = [math.tanh(w["recur_bias"][j] + w["bit"][j]*v +
                     sum(w["recur"][j*HIDDEN+k]*hidden[k] for k in range(HIDDEN)))
                     for j in range(HIDDEN)]
            states.append(hidden)
        logits = [w["out_bias"][j] + sum(w["out"][j*HIDDEN+k]*hidden[k] for k in range(HIDDEN)) +
                  (1.5 if before[j//4] == j % 4 else 0.0)
                  for j in range(32)]
        probs = []
        for i in range(8):
            four = logits[4*i:4*i+4]
            maximum = max(four)
            exp = [math.exp(z-maximum) for z in four]
            total = sum(exp)
            probs.append([v/total for v in exp])
        return x, states, probs

    def loss_and_gradient(self, row):
        before, after, bits = _validate(row)
        x, states, probs = self._forward(before, bits)
        w = self.weights
        grad = {name:[0.0]*len(array) for name,array in w.items()}
        dh = [0.0] * HIDDEN
        loss = 0.0
        for i in range(8):
            loss -= math.log(max(probs[i][after[i]], 1e-300)) / 8
            for loc in range(4):
                j = 4*i + loc
                dz = (probs[i][loc] - (1.0 if loc == after[i] else 0.0))/8
                grad["out_bias"][j] += dz
                for h in range(HIDDEN):
                    grad["out"][j*HIDDEN+h] += dz * states[-1][h]
                    dh[h] += w["out"][j*HIDDEN+h] * dz
        for t in range(len(bits), 0, -1):
            now, prev = states[t], states[t-1]
            bit = 1.0 if bits[t-1] == "1" else -1.0
            deriv = [dh[j] * (1-now[j]**2) for j in range(HIDDEN)]
            old_dh = [0.0]*HIDDEN
            for j in range(HIDDEN):
                grad["bit"][j] += deriv[j]*bit
                grad["recur_bias"][j] += deriv[j]
                for k in range(HIDDEN):
                    grad["recur"][j*HIDDEN+k] += deriv[j]*prev[k]
                    old_dh[k] += w["recur"][j*HIDDEN+k] * deriv[j]
            dh = old_dh
        for j in range(HIDDEN):
            dz = dh[j] * (1-states[0][j]**2)
            grad["init_bias"][j] += dz
            for k in range(32):
                grad["init"][j*32+k] += dz*x[k]
        return loss, grad

    def train(self, rows, steps):
        if type(steps) is not int or not 0 <= steps <= MAX_UPDATES - self.updates:
            raise ValueError("gradient budget exceeded")
        if not rows:
            raise ValueError("empty training source")
        for row in rows:
            _validate(row)
        for index in range(steps):
            # Deterministic rotating examples; no additional environment actions.
            row = rows[(self.updates * (len(rows)-1)) % len(rows)]
            _, grad = self.loss_and_gradient(row)
            for name, weights in self.weights.items():
                for k, delta in enumerate(grad[name]):
                    weights[k] -= self.learning_rate * max(-1.0, min(1.0, delta))
                    if not math.isfinite(weights[k]):
                        raise ArithmeticError("nonfinite trained weight")
            self.updates += 1

    def predict(self, before, acoustic_bits):
        # No oracle labels required or accepted. Validate through a synthetic
        # placeholder to share the strict input contract.
        class Visible:
            pass
        v = Visible()
        v.before = before
        v.after = before
        v.acoustic_bits = acoustic_bits
        v.action_cost, v.reset_cost = 1, 0
        _validate(v)
        _, _, p = self._forward(before, acoustic_bits)
        return tuple(max(range(4), key=lambda j:p[i][j]) for i in range(8))

    def probability(self, before, bits, after):
        if type(after) is not tuple or len(after) != 8 or any(type(v) is not int or v not in range(4) for v in after):
            raise ValueError("invalid candidate state")
        self.predict(before, bits)
        _, _, probs = self._forward(before, bits)
        return sum(math.log(max(probs[i][after[i]], 1e-300)) for i in range(8))

    def state(self):
        return {"seed":self.seed,"updates":self.updates,"weights":self.weights}

    @classmethod
    def from_state(cls, state):
        if type(state) is not dict or set(state) != {"seed","updates","weights"}:
            raise ValueError("invalid neural model state")
        if type(state["seed"]) is not str or type(state["updates"]) is not int or not 0 <= state["updates"] <= MAX_UPDATES:
            raise ValueError("invalid neural metadata")
        obj = cls(seed=state["seed"])
        if set(state["weights"]) != set(obj.weights):
            raise ValueError("invalid neural parameter set")
        for name, values in state["weights"].items():
            if type(values) is not list or len(values) != len(obj.weights[name]) or any(type(v) is not float or not math.isfinite(v) for v in values):
                raise ValueError("invalid neural parameter")
        obj.weights = {name:list(state["weights"][name]) for name in obj.weights}
        obj.updates = state["updates"]
        return obj


def _pack(row):
    _validate(row)
    return [list(row.before),row.acoustic_bits,list(row.after),row.action_cost,row.reset_cost]


def _unpack(data):
    from source import Observation
    if type(data) is not list or len(data) != 5:
        raise ValueError("invalid row")
    row = Observation(tuple(data[0]),data[1],tuple(data[2]),data[3],data[4])
    _validate(row)
    return row


def _encode(payload):
    return _canonical({"payload":payload,"sha256":hashlib.sha256(_canonical(payload).encode("ascii")).hexdigest()})


def _decode(data, schema):
    try:
        envelope = json.loads(data)
        if type(envelope) is not dict or set(envelope) != {"payload","sha256"} or _canonical(envelope) != data:
            raise ValueError("noncanonical envelope")
        payload = envelope["payload"]
        if payload["schema"] != schema or hashlib.sha256(_canonical(payload).encode("ascii")).hexdigest() != envelope["sha256"]:
            raise ValueError("invalid envelope digest")
        return payload
    except (TypeError, KeyError, json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("invalid model snapshot") from exc


class WarmupThenDirect:
    """Exactly 64 gradient updates, then unchanged grounded numeric writes.

    The learned raw-stream representation provides a veto (never a new outcome)
    against unsupported confident writer decisions. This is a conservative
    exploratory arm; no claim of an accuracy improvement is baked into it.
    """
    def __init__(self):
        from direct_writer import DirectWeightWriter
        self.writer = DirectWeightWriter()
        self.encoder = RawPhysicalRNN(seed="warmup-64")
        self.a, self.b = [], []
        self.sealed = self.finalized = False
        self.phase = "A"

    def observe(self, row):
        _validate(row)
        if self.finalized:
            raise ValueError("frozen learner")
        rows = self.b if self.sealed else self.a
        if len(rows) >= (6 if self.sealed else 36):
            raise ValueError("environment action budget exceeded")
        rows.append(row)
        if self.sealed:
            self.writer.observe(row)

    def seal_a(self):
        if self.sealed or len(self.a) != 36:
            raise ValueError("requires exactly 36 initial observations")
        self.encoder.train(self.a, 64)
        if self.encoder.updates != 64:
            raise AssertionError("gradient count differs from preregistered warmup")
        for row in self.a:
            self.writer.observe(row)
        self.sealed = True

    def finalize_b(self):
        if not self.sealed or self.finalized or len(self.b) != 6 or self.encoder.updates != 64:
            raise ValueError("requires six final observations and frozen encoder")
        self.phase = "B"
        self.finalized = True

    def use_phase(self, phase):
        if phase not in ("A","B") or (phase=="B" and not self.finalized):
            raise ValueError("phase unavailable")
        self.phase = phase

    def predict(self, before, acoustic_bits):
        if not self.sealed:
            return None
        candidate = self.writer.predict(before, acoustic_bits)
        if candidate is None:
            return None
        unchanged = before
        # A warmup representation cannot invent facts; use only a fixed
        # predeclared agreement veto relative to the original state.
        return candidate if self.encoder.probability(before, acoustic_bits, candidate) >= self.encoder.probability(before, acoustic_bits, unchanged) else None

    @property
    def actions(self):
        return len(self.a)+len(self.b)

    @property
    def gradient_steps(self):
        return self.encoder.updates

    def snapshot(self):
        return _encode({"schema":"wsp52.warmup-direct.v1","a":list(map(_pack,self.a)),
                        "b":list(map(_pack,self.b)),"sealed":self.sealed,
                        "finalized":self.finalized,"phase":self.phase,
                        "encoder":self.encoder.state(),"writer":self.writer.snapshot()})

    @classmethod
    def restore(cls,data):
        from direct_writer import DirectWeightWriter
        payload = _decode(data,"wsp52.warmup-direct.v1")
        if set(payload) != {"schema","a","b","sealed","finalized","phase","encoder","writer"}:
            raise ValueError("invalid warmup keys")
        obj = cls()
        obj.a = [_unpack(x) for x in payload["a"]]
        obj.b = [_unpack(x) for x in payload["b"]]
        obj.sealed, obj.finalized, obj.phase = payload["sealed"],payload["finalized"],payload["phase"]
        if (type(obj.sealed) is not bool or type(obj.finalized) is not bool or
            obj.finalized and not obj.sealed or len(obj.a) > 36 or len(obj.b) > 6 or
            len(obj.b) and not obj.sealed or obj.phase not in ("A","B") or
            obj.phase=="B" and not obj.finalized or obj.sealed and len(obj.a)!=36 or
            obj.finalized and len(obj.b)!=6):
            raise ValueError("invalid warmup progression")
        obj.encoder = RawPhysicalRNN.from_state(payload["encoder"])
        obj.writer = DirectWeightWriter.restore(payload["writer"])
        if obj.encoder.seed != "warmup-64" or obj.encoder.updates != (64 if obj.sealed else 0) or obj.writer.actions != (len(obj.a)+len(obj.b) if obj.sealed else 0):
            raise ValueError("invalid warmup budget")
        if obj.snapshot() != data:
            raise ValueError("noncanonical warmup reconstruction")
        return obj

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii"))*8


class TrainedTemporalComparator:
    """Independent genuinely gradient-trained raw-stream recurrent comparator.

    Each phase uses fixed scheduled training-only early stop; a truncated
    update budget must be reported as such rather than called fully trained.
    Learner never sees heldout targets or hidden codewords.
    """
    def __init__(self, *, a_budget=4096,b_budget=2048):
        if (a_budget,b_budget) != (4096,2048):
            raise ValueError("conventional budget frozen at 4096+2048")
        self.model = RawPhysicalRNN(seed="independent-conventional")
        self.a,self.b = [],[]
        self.sealed=self.finalized=False
        self.phase="A"
        self.loss_a=self.loss_b=None
        self.steps_a=self.steps_b=0
        self.stop_a=self.stop_b=None

    def observe(self,row):
        _validate(row)
        if self.finalized: raise ValueError("frozen comparator")
        rows = self.b if self.sealed else self.a
        if len(rows) >= (6 if self.sealed else 36):
            raise ValueError("environment action budget exceeded")
        rows.append(row)

    def _fit(self,rows,max_steps):
        # Frozen train-only criterion. A small training-loss improvement is
        # required at each 128-update checkpoint; never inspect heldout data.
        best=float("inf")
        stale=0
        total=0
        while total<max_steps:
            chunk=min(128,max_steps-total)
            self.model.train(rows,chunk)
            total+=chunk
            loss=sum(self.model.loss_and_gradient(row)[0] for row in rows)/len(rows)
            if loss<best-1e-4:
                best,stale=loss,0
            else:
                stale+=1
            if stale>=5: break
        return total,best,("TRAIN_LOSS_PLATEAU" if stale>=5 else "BUDGET_LIMIT")

    def seal_a(self):
        if self.sealed or len(self.a)!=36: raise ValueError("requires 36 A rows")
        self.steps_a,self.loss_a,self.stop_a=self._fit(self.a,4096)
        self.sealed=True

    def finalize_b(self):
        if not self.sealed or self.finalized or len(self.b)!=6: raise ValueError("requires 6 B rows")
        # Replay only recorded physical evidence; no new environment actions.
        self.steps_b,self.loss_b,self.stop_b=self._fit(self.a+self.b,2048)
        self.finalized=True
        self.phase="B"

    def use_phase(self,phase):
        if phase not in ("A","B") or phase=="B" and not self.finalized:
            raise ValueError("invalid phase")
        self.phase=phase

    def predict(self,before,acoustic_bits):
        return self.model.predict(before,acoustic_bits) if self.sealed else None

    @property
    def actions(self): return len(self.a)+len(self.b)

    @property
    def gradient_steps(self): return self.model.updates

    def snapshot(self):
        return _encode({"schema":"wsp52.temporal-baseline.v1",
            "a":list(map(_pack,self.a)),"b":list(map(_pack,self.b)),
            "sealed":self.sealed,"finalized":self.finalized,"phase":self.phase,
            "loss_a":self.loss_a,"loss_b":self.loss_b,"steps_a":self.steps_a,
            "steps_b":self.steps_b,"stop_a":self.stop_a,"stop_b":self.stop_b,"model":self.model.state()})

    @classmethod
    def restore(cls,data):
        payload=_decode(data,"wsp52.temporal-baseline.v1")
        if set(payload)!={"schema","a","b","sealed","finalized","phase","loss_a","loss_b","steps_a","steps_b","stop_a","stop_b","model"}:
            raise ValueError("invalid temporal comparator keys")
        obj=cls()
        obj.a=[_unpack(x) for x in payload["a"]]
        obj.b=[_unpack(x) for x in payload["b"]]
        for k in ("sealed","finalized","phase","loss_a","loss_b","steps_a","steps_b","stop_a","stop_b"):
            setattr(obj,k,payload[k])
        if (type(obj.sealed) is not bool or type(obj.finalized) is not bool or
            obj.finalized and not obj.sealed or len(obj.a)>(36) or len(obj.b)>6 or
            obj.sealed and len(obj.a)!=36 or obj.finalized and len(obj.b)!=6 or
            obj.b and not obj.sealed or obj.phase not in ("A","B") or
            obj.phase=="B" and not obj.finalized or
            type(obj.steps_a) is not int or type(obj.steps_b) is not int or
            not 0<=obj.steps_a<=4096 or not 0<=obj.steps_b<=2048):
            raise ValueError("invalid comparator progression")
        if (obj.sealed != (obj.steps_a > 0) or obj.finalized != (obj.steps_b > 0) or
            obj.steps_a % 128 != 0 or obj.steps_b % 128 != 0 or
            (obj.loss_a is None) != (not obj.sealed) or
            (obj.loss_b is None) != (not obj.finalized) or
            (obj.stop_a is None) != (not obj.sealed) or
            (obj.stop_b is None) != (not obj.finalized) or
            any(x is not None and (type(x) is not float or not math.isfinite(x)) for x in (obj.loss_a,obj.loss_b)) or
            any(x is not None and x not in ("TRAIN_LOSS_PLATEAU","BUDGET_LIMIT") for x in (obj.stop_a,obj.stop_b))):
            raise ValueError("invalid training status")
        obj.model=RawPhysicalRNN.from_state(payload["model"])
        if obj.model.seed != "independent-conventional":
            raise ValueError("incorrect baseline initialization")
        if obj.model.updates!=obj.steps_a+obj.steps_b:
            raise ValueError("unaccounted gradient updates")
        if obj.snapshot()!=data: raise ValueError("noncanonical comparator reconstruction")
        return obj

    def capacity_bits(self): return len(self.snapshot().encode("ascii"))*8
