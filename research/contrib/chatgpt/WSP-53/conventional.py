"""WSP53 independent raw-bit recurrent conventional comparator, SELFTEST engineering.

No oracle lexicon, semantic triples, token IDs, grammar, or source-world import.
This deterministic baseline is not scientifically qualified until the frozen
fully-trained, train-side stopping, resource and cold-restore gates are met.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from controls import MAX_ACTIONS, bits, canonical, observation, state

HIDDEN = 16
FEATURES = 56
MAX_PARAMETERS = 65536
MAX_UPDATES = 20000
RATE = 0.035
CONTINUITY = 1.5

@dataclass(frozen=True)
class Row:
    before: tuple
    acoustic_bits: str
    after: tuple
    action_cost: int = 1
    reset_cost: int = 0

def segments(family):
    if family == "anchored_effect":
        return tuple((i*4, 4) for i in range(8)) + tuple((32+i*3, 3) for i in range(8))
    if family == "noncommuting_order":
        return tuple((i*7, 7) for i in range(8))
    raise ValueError("invalid physics family")

def _random(seed, family, group, index):
    h = sha256(f"WSP53|raw-recurrent|{seed}|{family}|{group}|{index}".encode("ascii")).digest()
    return (int.from_bytes(h[:8], "big") / 2**64-0.5)*0.12

class RawBitRNN:
    """Fully trainable raw-bit BPTT control with physical-state input/output.

    No prewired meanings. Only the shared observation space, per-register
    categorical cardinalities and continuity prior are hardcoded.
    """
    def __init__(self, *, family, seed="independent-conventional"):
        state((0,)*(16 if family=="anchored_effect" else 8),family)
        if type(seed) is not str or not seed or len(seed)>100:
            raise ValueError("invalid seed")
        self.family,self.seed=family,seed
        self.slices=segments(family)
        self.shapes={"init":HIDDEN*FEATURES,"init_bias":HIDDEN,
                     "recur":HIDDEN*HIDDEN,"bit":HIDDEN,"recur_bias":HIDDEN,
                     "out":FEATURES*HIDDEN,"out_bias":FEATURES}
        self.w={k:[_random(seed,family,k,i) for i in range(n)] for k,n in self.shapes.items()}
        self.rows=[]
        self.updates=0
        self.phase_b=False
        assert self.parameter_count()<=MAX_PARAMETERS

    def parameter_count(self):
        return sum(map(len,self.w.values()))

    def observe(self,row):
        b,s,a=observation(row,self.family)
        if len(self.rows)>=MAX_ACTIONS:
            raise ValueError("action budget exceeded")
        if self.phase_b is False and len(self.rows)>=48:
            raise ValueError("must seal Phase A before Phase B")
        self.rows.append(Row(b,s,a))

    def seal_a(self):
        if self.phase_b or len(self.rows)!=48:
            raise ValueError("expected exactly 48 Phase A actions")
        self.phase_b=True

    def _onehot(self,before):
        x=[0.0]*FEATURES
        for i,(offset,width) in enumerate(self.slices):
            x[offset+before[i]]=1.0
        return x

    def _forward(self,before,raw):
        state(before,self.family);bits(raw)
        w=self.w
        x=self._onehot(before)
        hidden=[math.tanh(w["init_bias"][j]+sum(w["init"][j*FEATURES+k]*x[k]
                      for k in range(FEATURES))) for j in range(HIDDEN)]
        traces=[hidden]
        for bit in raw:
            v=1.0 if bit=="1" else -1.0
            hidden=[math.tanh(w["recur_bias"][j]+w["bit"][j]*v+
                      sum(w["recur"][j*HIDDEN+k]*hidden[k] for k in range(HIDDEN)))
                      for j in range(HIDDEN)]
            traces.append(hidden)
        probs=[]
        for i,(offset,width) in enumerate(self.slices):
            logits=[w["out_bias"][offset+c]+
                    sum(w["out"][(offset+c)*HIDDEN+h]*hidden[h] for h in range(HIDDEN))+
                    (CONTINUITY if before[i]==c else 0.0) for c in range(width)]
            highest=max(logits)
            exps=[math.exp(v-highest) for v in logits]
            total=sum(exps)
            probs.append([v/total for v in exps])
        return x,traces,probs

    def loss_gradient(self,row):
        before,raw,after=observation(row,self.family)
        x,traces,probs=self._forward(before,raw)
        g={k:[0.0]*len(v) for k,v in self.w.items()}
        dh=[0.0]*HIDDEN
        loss=0.0
        denom=len(self.slices)
        for i,(offset,width) in enumerate(self.slices):
            loss-=math.log(max(probs[i][after[i]],1e-300))/denom
            for c in range(width):
                index=offset+c
                delta=(probs[i][c]-(1.0 if c==after[i] else 0.0))/denom
                g["out_bias"][index]+=delta
                for h in range(HIDDEN):
                    g["out"][index*HIDDEN+h]+=delta*traces[-1][h]
                    dh[h]+=self.w["out"][index*HIDDEN+h]*delta
        for t in range(len(raw),0,-1):
            current,previous=traces[t],traces[t-1]
            v=1.0 if raw[t-1]=="1" else -1.0
            d=[dh[j]*(1-current[j]*current[j]) for j in range(HIDDEN)]
            back=[0.0]*HIDDEN
            for j in range(HIDDEN):
                g["bit"][j]+=d[j]*v
                g["recur_bias"][j]+=d[j]
                for k in range(HIDDEN):
                    g["recur"][j*HIDDEN+k]+=d[j]*previous[k]
                    back[k]+=self.w["recur"][j*HIDDEN+k]*d[j]
            dh=back
        for j in range(HIDDEN):
            delta=dh[j]*(1-traces[0][j]**2)
            g["init_bias"][j]+=delta
            for k in range(FEATURES):
                g["init"][j*FEATURES+k]+=delta*x[k]
        return loss,g

    def train(self,steps):
        if type(steps) is not int or not 0<=steps<=MAX_UPDATES-self.updates:
            raise ValueError("gradient-step limit exceeded")
        if not self.rows:
            raise ValueError("no charged observations")
        for iteration in range(steps):
            row=self.rows[self.updates%len(self.rows)]
            _,gradient=self.loss_gradient(row)
            for k,values in self.w.items():
                for j,d in enumerate(gradient[k]):
                    values[j]-=RATE*max(-1.0,min(1.0,d))
                    if not math.isfinite(values[j]):
                        raise ArithmeticError("nonfinite neural weight")
            self.updates+=1
        return self.train_diagnostic()

    def train_diagnostic(self):
        if not self.rows:
            return {"accuracy":0.0,"loss":None,"updates":self.updates,
                    "converged":False}
        losses=[]
        correct=0
        for r in self.rows:
            _,_,p=self._forward(r.before,r.acoustic_bits)
            losses.append(-sum(math.log(max(p[i][r.after[i]],1e-300))
                               for i in range(len(self.slices)))/len(self.slices))
            if self.predict(r.before,r.acoustic_bits)==r.after:
                correct+=1
        return {"accuracy":correct/len(self.rows),"loss":sum(losses)/len(losses),
                "updates":self.updates,
                "converged":(correct/len(self.rows)>=0.95 and
                             sum(losses)/len(losses)<=0.08)}

    def predict(self,before,raw):
        _,_,p=self._forward(before,raw)
        return tuple(max(range(len(item)),key=lambda j:item[j]) for item in p)

    def snapshot(self):
        payload={"schema":"wsp53.raw-bit-rnn.v1","family":self.family,"seed":self.seed,
                 "updates":self.updates,"phase_b":self.phase_b,
                 "rows":[[list(r.before),r.acoustic_bits,list(r.after)] for r in self.rows],
                 "weights":self.w}
        raw=canonical(payload)
        if len(raw)>4000000:
            raise OverflowError("neural snapshot cap")
        return canonical({"payload":payload,"sha256":sha256(raw.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls,data):
        if type(data) is not str or len(data)>4500000:
            raise ValueError("bad snapshot size")
        try:
            box=json.loads(data)
            if type(box) is not dict or set(box)!={"payload","sha256"}:
                raise ValueError("invalid envelope")
            p=box["payload"]
            if (type(p) is not dict or set(p)!={"schema","family","seed","updates",
                    "phase_b","rows","weights"} or
                p["schema"]!="wsp53.raw-bit-rnn.v1" or
                sha256(canonical(p).encode("ascii")).hexdigest()!=box["sha256"]):
                raise ValueError("snapshot integrity failure")
            obj=cls(family=p["family"],seed=p["seed"])
            if (type(p["updates"]) is not int or not 0<=p["updates"]<=MAX_UPDATES
                or type(p["phase_b"]) is not bool or type(p["rows"]) is not list
                or len(p["rows"])>MAX_ACTIONS or
                p["phase_b"]!=(len(p["rows"])>=48)):
                raise ValueError("invalid training metadata")
            for item in p["rows"]:
                if type(item) is not list or len(item)!=3:
                    raise ValueError("invalid evidence row")
                b,s,a=item
                if type(b) is not list or type(a) is not list:
                    raise ValueError("invalid state record")
                obj.rows.append(Row(state(tuple(b),obj.family),bits(s),state(tuple(a),obj.family)))
            if (type(p["weights"]) is not dict or set(p["weights"])!=set(obj.w)):
                raise ValueError("invalid weight tensor map")
            for key,values in p["weights"].items():
                if (type(values) is not list or len(values)!=obj.shapes[key]
                    or any(type(v) is not float or not math.isfinite(v) for v in values)):
                    raise ValueError("invalid neural weights")
            obj.w={k:list(p["weights"][k]) for k in obj.w}
            obj.updates=p["updates"]
            obj.phase_b=p["phase_b"]
            if obj.snapshot()!=data:
                raise ValueError("noncanonical neural snapshot")
            return obj
        except (KeyError,IndexError,TypeError,UnicodeError,json.JSONDecodeError) as exc:
            raise ValueError("malformed neural snapshot") from exc

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii"))*8
