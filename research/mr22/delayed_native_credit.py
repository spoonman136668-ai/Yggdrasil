"""MR22: bounded *delayed* prediction-credit memory write gate.

The native 45-coefficient Yggdrasil runtime remains the entire trainable
parameter store. Eight ephemeral camera-relative retained values and eight
additional scalar gate eligibility traces count toward total memory.
An event written at time t can influence the memory-gate coefficient only
through later original native prediction errors (at t+1 or beyond). No
immediate gate reward, target relevance label, privileged grid or teacher.

The 7 original genome[2] coefficients remain reserved/unchanged in this
opt-in mechanism: learning their exact through-time gradient would require
per-cell 7-dimensional eligibility beyond the declared transient budget.
Gate's public feature dependence is fixed and nonsemantic. A trained bias
per camera-relative slot is NOT evidence of physical cell specialization.
"""
import json
import math

from research.mr18.native_public_learning import public_features
from yggdrasil.developmental import sig, valid
from yggdrasil.task_runtime import LocalTaskRuntime

N=8
RATE=.035
DELAYED_RATE=.15


def bound(x,limit):
    if not math.isfinite(x):
        raise ValueError("MR22_NONFINITE_NATIVE_UPDATE")
    return max(-limit,min(limit,x))


class DelayedLocalEligibility:
    def __init__(self,native=None,states=None,eligibilities=None,learn_delayed=True):
        if type(learn_delayed) is not bool:
            raise ValueError("MR22_BAD_GATE_MODE")
        self.native=LocalTaskRuntime() if native is None else native
        self.states=[0.]*8 if states is None else list(states)
        self.eligibilities=[0.]*8 if eligibilities is None else list(eligibilities)
        self.learn_delayed=learn_delayed
        if (type(self.native) is not LocalTaskRuntime or
            self.native.damaged or
            self.native.neighbors!=LocalTaskRuntime().neighbors or
            len(self.states)!=8 or len(self.eligibilities)!=8 or
            any(type(x) not in (int,float) or not math.isfinite(x) or
                abs(x)>1.000001 for x in self.states+self.eligibilities)):
            raise ValueError("MR22_ORIGINAL_NATIVE_STATE_DRIFT")

    def reset_episode(self):
        self.states=[0.]*8
        self.eligibilities=[0.]*8

    def predict(self,raw,bits,action):
        valid(bits)
        full,zero,gates=[],[],[]
        for i in range(N):
            f=public_features(raw,bits,action,i)
            genome=self.native.core.genome
            role=self.native.core.roles[i]
            shared=sum(w*x for w,x in zip(genome[0],f))+role[0]
            transition=math.tanh(sum(w*x for w,x in zip(genome[1],f)))
            # All input dependence is frozen before this study, not
            # optimized on any MR22 environments.
            gate=sig(role[2]+.25*f[1]+.20*f[6])
            full.append(sig(shared+self.states[i]*(transition+role[1])))
            zero.append(sig(shared))
            gates.append(gate)
        return full,zero,gates

    def observe_real_native_consequence(self,raw,bits,action,target,training):
        valid(bits);valid(target)
        if type(training) is not bool:
            raise ValueError("MR22_BAD_TRAIN_FLAG")
        prior=self.snapshot()
        probabilities,zero,gates=self.predict(raw,bits,action)
        clone=self.restore(prior)
        for i,y in enumerate(target):
            f=public_features(raw,bits,action,i)
            genome=clone.native.core.genome
            role=clone.native.core.roles[i]
            h=clone.states[i]
            eligible=clone.eligibilities[i]
            error=y-probabilities[i]
            temporal=math.tanh(sum(w*x for w,x in zip(genome[1],f)))
            # CRITICAL: This trace was computed using outcomes from earlier
            # native steps only; the current y is not a teacher for the
            # current event's write decision. The gate update is *before*
            # recalculating eligibility for the newly revealed target.
            delayed_gradient=error*(temporal+role[1])*eligible
            if training:
                if clone.learn_delayed:
                    role[2]=bound(role[2]+DELAYED_RATE*delayed_gradient,20.)
                for j,x in enumerate(f):
                    genome[0][j]=bound(genome[0][j]+RATE*error*x,15.)
                    genome[1][j]=bound(genome[1][j]+RATE*error*h*
                                       (1.-temporal*temporal)*x,15.)
                role[0]=bound(role[0]+RATE*error,20.)
                role[1]=bound(role[1]+RATE*error*h,20.)
                clone.native.core.events+=0  # count one native source event below
            # Source result y is now authentic, and only now a new eligible
            # retained event can be written. The gate was frozen pre-action.
            z=2*y-1
            g=gates[i]
            clone.eligibilities[i]=bound(
                (1.-g)*eligible+g*(1.-g)*(z-h),1.)
            clone.states[i]=bound((1.-g)*h+g*z,1.)
        if training:
            clone.native.core.events+=1
        if (sum(len(row) for row in clone.native.core.genome)+
            sum(len(row) for row in clone.native.core.roles)!=45):
            raise ValueError("MR22_MODEL_CAPACITY_DRIFT")
        if clone.snapshot()!=self.restore(clone.snapshot()).snapshot() or self.snapshot()!=prior:
            raise ValueError("MR22_ATOMIC_STATE_CUSTODY_DRIFT")
        self.native=clone.native
        self.states=clone.states
        self.eligibilities=clone.eligibilities
        return probabilities,zero,gates

    def snapshot(self):
        return json.dumps({
            "schema":"yggdrasil.mr22.delayed-eligibility.v1",
            "native":json.loads(self.native.snapshot()),
            "states":self.states,
            "eligibilities":self.eligibilities,
            "learn_delayed":self.learn_delayed
        },sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>65536:
            raise ValueError("MR22_INVALID_SNAPSHOT_SIZE")
        d=json.loads(payload)
        if (type(d) is not dict or
            set(d)!={"schema","native","states","eligibilities",
                     "learn_delayed"} or
            d["schema"]!="yggdrasil.mr22.delayed-eligibility.v1" or
            type(d["learn_delayed"]) is not bool or
            type(d["states"]) is not list or
            type(d["eligibilities"]) is not list or
            len(d["states"])!=8 or len(d["eligibilities"])!=8):
            raise ValueError("MR22_INVALID_SNAPSHOT_SCHEMA")
        native=LocalTaskRuntime.restore(json.dumps(d["native"]))
        a=cls(native,d["states"],d["eligibilities"],d["learn_delayed"])
        if a.snapshot()!=payload:
            raise ValueError("MR22_NONCANONICAL_SNAPSHOT")
        return a
