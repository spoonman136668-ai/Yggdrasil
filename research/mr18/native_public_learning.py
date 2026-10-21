"""MR18: prospective native public-information learning, fixed original 45 coefficients.

Opt-in development-only models. Public MiniGrid image is only accessed through
MR15's 24 raw sampled observation bytes; no native environment object, reward,
object/role decoder, mission, hidden grid, or future outcomes enter models.
Feature basis is frozen before any MR18 source runs. This is an engineered
representation experiment, not learned feature formation or scientific first use.
"""
import json
import math
from research.mr16.native_prequential import action_features
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.developmental import N, K, D, valid, sig, softmax

RATE = .035
REPRESENTATION = "mr18-public-low-nibble-v1"
assert (N,K,D) == (8,3,7)


def validate(raw, bits, action):
    valid(bits)
    if (type(raw) not in (tuple,list) or len(raw)!=24 or
        any(type(x) is not int or not 0<=x<=255 for x in raw)):
        raise ValueError("MR18_INVALID_PUBLIC_RAW")
    if type(action) is not int or not 0<=action<=6:
        raise ValueError("MR18_INVALID_ORIGINAL_ACTION")


def scale(x):
    # Nonsemantic, source-independent, fixed low-nibble normalization.
    # Losing high-nibble information is a deliberate bounded limitation.
    return (x & 15)/7.5 - 1.


def public_features(raw, bits, action, i):
    validate(raw,bits,action)
    if type(i) is not int or not 0<=i<N:
        raise ValueError("MR18_INVALID_CELL")
    base = 3*i
    left = 3*((i-1)%N)
    right = 3*((i+1)%N)
    return (1.,scale(raw[base]),scale(raw[base+1]),scale(raw[base+2]),
            float(2*bits[i]-1),.5*(scale(raw[left])+scale(raw[right])),
            (action-3.)/3.)


class Native45:
    """Original LocalTaskRuntime, same 3x7 genome and 8x3 local logits."""
    def __init__(self, mode="public", runtime=None):
        if mode not in ("public","coarse"):
            raise ValueError("MR18_INVALID_FEATURE_MODE")
        self.mode = mode
        self.rt = LocalTaskRuntime() if runtime is None else runtime
        if (type(self.rt) is not LocalTaskRuntime or self.rt.damaged or
            self.rt.neighbors != LocalTaskRuntime().neighbors):
            raise ValueError("MR18_ORIGINAL_MODEL_IDENTITY_DRIFT")

    def features(self, raw,bits,action,i):
        validate(raw,bits,action)
        return (public_features(raw,bits,action,i) if self.mode=="public"
                else action_features(bits,i,action))

    def predict(self,raw,bits,action):
        validate(raw,bits,action)
        out=[]
        for i in range(N):
            f=self.features(raw,bits,action,i)
            experts=[sig(sum(w*x for w,x in zip(row,f)))
                     for row in self.rt.core.genome]
            gate=softmax(self.rt.core.roles[i])
            out.append(sum(g*p for g,p in zip(gate,experts)))
        return out

    def observe(self,raw,bits,action,targets):
        validate(raw,bits,action);valid(targets)
        before=self.rt.snapshot()
        proposal=LocalTaskRuntime.restore(before)
        for i,target in enumerate(targets):
            f=self.features(raw,bits,action,i)
            experts=[sig(sum(w*x for w,x in zip(row,f)))
                     for row in proposal.core.genome]
            gate=softmax(proposal.core.roles[i])
            losses=[(target-p)**2 for p in experts]
            avg=sum(g*l for g,l in zip(gate,losses))
            for k in range(K):
                proposal.core.roles[i][k]=max(-20.,min(20.,
                    proposal.core.roles[i][k]+RATE*2*(avg-losses[k])))
                delta=RATE*gate[k]*(target-experts[k])
                for j in range(D):
                    v=proposal.core.genome[k][j]+delta*f[j]
                    if not math.isfinite(v):
                        raise ValueError("MR18_NONFINITE_MODEL_UPDATE")
                    proposal.core.genome[k][j]=max(-15.,min(15.,v))
        proposal.core.events += 1
        if (sum(map(len,proposal.core.genome))+
            sum(map(len,proposal.core.roles))!=45):
            raise ValueError("MR18_CAPACITY_DRIFT")
        checked=LocalTaskRuntime.restore(proposal.snapshot())
        if checked.snapshot()!=proposal.snapshot() or before!=self.rt.snapshot():
            raise ValueError("MR18_MODEL_SNAPSHOT_DRIFT")
        self.rt=proposal

    def snapshot(self):
        return self.rt.snapshot()

    @classmethod
    def restore(cls, mode, snapshot):
        obj=cls(mode,LocalTaskRuntime.restore(snapshot))
        if obj.snapshot()!=snapshot:
            raise ValueError("MR18_NONCANONICAL_NATIVE_SNAPSHOT")
        return obj


class Recurrent45:
    """Conventional learned logistic recurrent control, exactly 45 weights.

    40 per-cell weights + five shared weights and eight episodic activations.
    The last feature is a recurrent activation formed ONLY from earlier public
    observations. The recurrent state is reset on each real env.reset().
    """
    def __init__(self):
        self.local=[[0.]*5 for _ in range(8)]
        self.shared=[0.]*5
        self.state=[0.]*8

    def features(self,raw,action,i):
        base=3*i
        return (1.,scale(raw[base]),
                .5*(scale(raw[base+1])+scale(raw[base+2])),
                (action-3.)/3., self.state[i])

    def predict(self,raw,bits,action):
        validate(raw,bits,action)
        return [sig(sum((self.local[i][j]+self.shared[j])*v
                    for j,v in enumerate(self.features(raw,action,i))))
                for i in range(8)]

    def advance_public_history(self,raw):
        for i in range(8):
            base=3*i
            content=(scale(raw[base])+scale(raw[base+1])+
                     scale(raw[base+2]))/3.
            self.state[i]=.7*self.state[i]+.3*content

    def observe(self,raw,bits,action,targets):
        validate(raw,bits,action);valid(targets)
        predictions=self.predict(raw,bits,action)
        for i,target in enumerate(targets):
            f=self.features(raw,action,i)
            error=target-predictions[i]
            for j,x in enumerate(f):
                self.local[i][j]=max(-15.,min(15.,
                    self.local[i][j]+RATE*error*x))
                self.shared[j]=max(-15.,min(15.,
                    self.shared[j]+RATE*error*x/8.))
        self.advance_public_history(raw)

    def reset_episode(self):
        self.state=[0.]*8

    def snapshot(self):
        return json.dumps({"schema":"mr18.recurrent45.v1",
            "local":self.local,"shared":self.shared,"state":self.state},
            sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>8192:
            raise ValueError("MR18_BAD_RECURRENT_SNAPSHOT")
        o=json.loads(payload)
        if (type(o) is not dict or set(o)!={"schema","local","shared","state"} or
            o["schema"]!="mr18.recurrent45.v1" or
            type(o["local"]) is not list or len(o["local"])!=8 or
            any(type(row) is not list or len(row)!=5 for row in o["local"]) or
            type(o["shared"]) is not list or len(o["shared"])!=5 or
            type(o["state"]) is not list or len(o["state"])!=8):
            raise ValueError("MR18_BAD_RECURRENT_SHAPE")
        for x in [v for row in o["local"] for v in row]+o["shared"]+o["state"]:
            if type(x) not in (int,float) or not math.isfinite(x) or abs(x)>20:
                raise ValueError("MR18_BAD_RECURRENT_WEIGHT")
        m=cls()
        m.local=[[float(x) for x in row] for row in o["local"]]
        m.shared=[float(x) for x in o["shared"]]
        m.state=[float(x) for x in o["state"]]
        if m.snapshot()!=payload:
            raise ValueError("MR18_NONCANONICAL_RECURRENT_SNAPSHOT")
        return m


class PublicCount:
    """Conventional smoothed count, same public inputs, memory is NOT matched."""
    def __init__(self):
        self.table={}
    def key(self,raw,bits,action,i):
        validate(raw,bits,action)
        return (i,action,tuple(raw[3*i:3*i+3]),bits[i],
                bits[(i-1)%8])
    def predict(self,raw,bits,action):
        out=[]
        for i in range(8):
            yes,total=self.table.get(self.key(raw,bits,action,i),(0,0))
            out.append((yes+1)/(total+2))
        return out
    def observe(self,raw,bits,action,targets):
        validate(raw,bits,action);valid(targets)
        for i,v in enumerate(targets):
            k=self.key(raw,bits,action,i)
            yes,total=self.table.get(k,(0,0))
            self.table[k]=(yes+v,total+1)
    def snapshot(self):
        return json.dumps(sorted(
            [list(k[:2])+[list(k[2])]+list(k[3:])+[yes,total]
             for k,(yes,total) in self.table.items()]),
            separators=(",",":"))
