"""MR16: opt-in pre-outcome learning from MR15 public MiniGrid observations.

Not an original MiniGrid environment, new hidden task family, or source oracle.
The only trainable capacity is the EXISTING 3x7 shared genome + 8x3 roles
(45 coefficients). Original LocalTaskRuntime training remains untouched.

Action enters the existing final feature slot as a signed observed scalar.
This is a designed causal information interface, NOT spontaneous learning of
features or evidence of local specialization. Original public view is fed in
only via MR15's eight bits and pre-execution action; no privileged state.
"""
import math

from yggdrasil.developmental import K, D, N, valid, sig, softmax
from yggdrasil.task_runtime import LocalTaskRuntime


def native_action_features(runtime, prior, i, action):
    valid(prior)
    if (type(i) is not int or not 0<=i<N or
            type(action) is not int or not 0<=action<=6):
        raise ValueError("MR16_INVALID_LOCAL_ACTION")
    left, right = runtime.neighbors[i]
    x = 2*prior[i]-1
    a = 2*prior[left]-1
    b = 2*prior[right]-1
    return (1.,float(x),float(a),float(b),float(a*b),
            float(x*a), float(action/3.0-1.0))


class NativeLocalActionLearner:
    __slots__=("rt",)
    def __init__(self, rt=None):
        self.rt=LocalTaskRuntime() if rt is None else rt
        if type(self.rt) is not LocalTaskRuntime or self.rt.damaged:
            raise ValueError("MR16_PRELESION_ORIGINAL_RUNTIME_REQUIRED")

    def predict(self, prior, action):
        valid(prior)
        if type(action) is not int or not 0<=action<=6:
            raise ValueError("MR16_INVALID_ACTION")
        out=[]
        for i in range(N):
            f=native_action_features(self.rt,prior,i,action)
            experts=[sig(sum(w*x for w,x in zip(row,f)))
                     for row in self.rt.core.genome]
            gate=softmax(self.rt.core.roles[i])
            p=sum(w*v for w,v in zip(gate,experts))
            if not math.isfinite(p) or not 0<=p<=1:
                raise ValueError("MR16_NONFINITE_PREDICTION")
            out.append(p)
        return out

    def observe_after_original_step(self, prior, action, observed, rate=.035):
        valid(prior);valid(observed)
        if (type(action) is not int or not 0<=action<=6 or
            type(rate) not in (int,float) or not math.isfinite(rate)
            or not 0<rate<=.1):
            raise ValueError("MR16_UNQUALIFIED_ACTION_OR_RATE")
        frozen=self.rt.snapshot()
        candidate=LocalTaskRuntime.restore(frozen)
        if candidate.damaged:
            raise ValueError("MR16_POSTLESION_LABELS_FORBIDDEN")
        for i,y in enumerate(observed):
            f=native_action_features(candidate,prior,i,action)
            guesses=[sig(sum(w*x for w,x in zip(row,f)))
                     for row in candidate.core.genome]
            gate=softmax(candidate.core.roles[i])
            losses=[(y-p)**2 for p in guesses]
            avg=sum(w*v for w,v in zip(gate,losses))
            for k in range(K):
                new_role=candidate.core.roles[i][k]+rate*2*(avg-losses[k])
                if not math.isfinite(new_role):
                    raise ValueError("MR16_NONFINITE_ROLE")
                candidate.core.roles[i][k]=max(-20.,min(20.,new_role))
                delta=rate*gate[k]*(y-guesses[k])
                for j in range(D):
                    new_weight=candidate.core.genome[k][j]+delta*f[j]
                    if not math.isfinite(new_weight):
                        raise ValueError("MR16_NONFINITE_GENOME")
                    candidate.core.genome[k][j]=max(-15.,min(15.,new_weight))
        candidate.core.events+=1
        if (sum(len(row) for row in candidate.core.genome)+
            sum(len(row) for row in candidate.core.roles)!=45):
            raise ValueError("MR16_ORIGINAL_45_COEFFICIENT_BUDGET_DRIFT")
        result=candidate.snapshot()
        if LocalTaskRuntime.restore(result).snapshot()!=result:
            raise ValueError("MR16_COLD_SNAPSHOT_INVALID")
        if self.rt.snapshot()!=frozen:
            raise ValueError("MR16_RUNTIME_CHANGED_BEFORE_COMMIT")
        self.rt=candidate

    def snapshot(self):
        return self.rt.snapshot()

    @classmethod
    def restore(cls, payload):
        rt=LocalTaskRuntime.restore(payload)
        if rt.damaged:
            raise ValueError("MR16_RECOVERY_TRAINING_FORBIDDEN")
        return cls(rt)

    def role_ablation_mean_effect(self, events):
        # DEV data replay: only original, previously observed public 8-bit
        # records; never protected future outcomes or model-predicted labels.
        with_roles=NativeLocalActionLearner.restore(self.snapshot())
        no_roles=NativeLocalActionLearner.restore(self.snapshot())
        for i in range(N):
            no_roles.rt.core.roles[i]=[0.]*K
        diffs=[]
        for prior,action,_ in events:
            a=with_roles.predict(prior,action)
            b=no_roles.predict(prior,action)
            diffs.extend(abs(x-y) for x,y in zip(a,b))
        return sum(diffs)/len(diffs) if diffs else 0.


class ConditionalCount:
    """Strong conventional exact-history count; same public action/inputs."""
    __slots__=("neighbors","per_cell","counts")
    def __init__(self, *, per_cell):
        self.neighbors=LocalTaskRuntime().neighbors
        self.per_cell=per_cell
        self.counts={}

    def _key(self,prior,action,i):
        left,right=self.neighbors[i]
        # No environment object IDs, mission or privileged state.
        key=(prior[i],prior[left],prior[right],action)
        return (i,)+key if self.per_cell else key

    def predict(self,prior,action):
        valid(prior)
        if type(action) is not int or not 0<=action<=6:
            raise ValueError("MR16_COUNT_INVALID_ACTION")
        return [(self.counts.get(self._key(prior,action,i),(0,0))[0]+1)/
                (self.counts.get(self._key(prior,action,i),(0,0))[1]+2)
                for i in range(N)]

    def observe(self,prior,action,observed):
        valid(prior);valid(observed)
        for i,y in enumerate(observed):
            key=self._key(prior,action,i)
            yes,total=self.counts.get(key,(0,0))
            self.counts[key]=(yes+y,total+1)


def brier(prediction,outcome):
    if len(prediction)!=N:
        raise ValueError("MR16_PREDICTION_SHAPE")
    valid(outcome)
    return sum((p-y)**2 for p,y in zip(prediction,outcome))/N
