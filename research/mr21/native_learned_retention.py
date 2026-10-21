"""MR21 development-only learned predictive-memory retention.

All features are frozen from MR18 and all 45 original native trainable slots
are reused. The eight MR15 observation slots are CAMERA RELATIVE (MR19B);
they are NOT assumed to represent independently stable world cells.

Unlike MR19's fixed write-all heuristic, an existing shared 7-weight
pathway and eight existing private logits decide how much public event history
to retain. The gate is adapted from previous-history predictive advantage:
pre-action full-state vs state-zero predictions, scored ONLY after authentic
original env.step. That is a retrospective LOCAL SURROGATE credit signal,
not proof of exact one-step delayed write attribution or emergent identity.
No additional learned coefficient, teacher relevance labels, hidden object IDs,
reward, or model-independent evaluator labels.
"""
import json
import math

from research.mr18.native_public_learning import public_features
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.developmental import valid, sig

N,K,D = 8,3,7
LR=.035
GATE_RATE=.20

def clip(x, bound=15.0):
    if not math.isfinite(x):
        raise ValueError("MR21_NONFINITE_LEARNING")
    return max(-bound,min(bound,x))


class LearnedRetention:
    """Original 45 coefficients + eight temporary camera-slot memories."""
    def __init__(self, native=None, states=None, learn_selection=True):
        if type(learn_selection) is not bool:
            raise ValueError("MR21_BAD_SELECTION_MODE")
        self.native=LocalTaskRuntime() if native is None else native
        self.states=[0.]*N if states is None else list(states)
        self.learn_selection=learn_selection
        if (type(self.native) is not LocalTaskRuntime or self.native.damaged or
            self.native.neighbors!=LocalTaskRuntime().neighbors or
            len(self.states)!=N or
            any(type(v) not in (int,float) or
                not math.isfinite(v) or abs(v)>1.000001 for v in self.states)):
            raise ValueError("MR21_ORIGINAL_BUDGET_OR_STATE_DRIFT")

    def reset_episode(self):
        self.states=[0.]*N

    def predictions(self,raw,bits,action):
        valid(bits)
        full,without,write=[],[],[]
        for i in range(N):
            f=public_features(raw,bits,action,i)
            g=self.native.core.genome
            roles=self.native.core.roles[i]
            base=sum(w*x for w,x in zip(g[0],f))+roles[0]
            temporal=math.tanh(sum(w*x for w,x in zip(g[1],f)))
            memory_contribution=self.states[i]*(temporal+roles[1])
            gate=sig(sum(w*x for w,x in zip(g[2],f))+roles[2])
            full.append(sig(base+memory_contribution))
            without.append(sig(base))
            write.append(gate)
        return full,without,write

    def step_after_native(self,raw,bits,action,observed_target,
                          training=True):
        valid(bits);valid(observed_target)
        if type(training) is not bool:
            raise ValueError("MR21_BAD_TRAIN_FLAG")
        full,without,gate=self.predictions(raw,bits,action)
        old=self.snapshot()
        candidate=self.restore(old)
        for i,y in enumerate(observed_target):
            f=public_features(raw,bits,action,i)
            g=candidate.native.core.genome
            role=candidate.native.core.roles[i]
            state=candidate.states[i]
            residual=y-full[i]
            # State utility was predicted BEFORE the original event. It
            # rewards retention if the previously selected state improved
            # this event's prediction versus exact same weights with h=0.
            advantage=(without[i]-y)**2-(full[i]-y)**2
            if training:
                shared_temporal=math.tanh(sum(w*x for w,x in zip(g[1],f)))
                for j,x in enumerate(f):
                    g[0][j]=clip(g[0][j]+LR*residual*x)
                    g[1][j]=clip(g[1][j]+LR*residual*state*
                                  (1-shared_temporal**2)*x)
                role[0]=clip(role[0]+LR*residual,20.)
                role[1]=clip(role[1]+LR*residual*state,20.)
                if self.learn_selection:
                    # This is a one-step surrogate and MAY fail to learn
                    # truly useful delayed memories. It cannot access a
                    # correct-write teacher or latent object identities.
                    signal=clip(advantage,1.)
                    ds=GATE_RATE*signal*gate[i]*(1-gate[i])
                    role[2]=clip(role[2]+ds,20.)
                    for j,x in enumerate(f):
                        g[2][j]=clip(g[2][j]+ds*x/N)
            # The learned/frozen selection gate is always pre-outcome and
            # uses no target to decide whether this CURRENT event is written.
            # The outcome becomes public only AFTER the source action.
            candidate.states[i]=clip(
                (1-gate[i])*state+gate[i]*(2*y-1),1.)
        if training:
            candidate.native.core.events+=1
        if sum(map(len,candidate.native.core.genome))+sum(
            map(len,candidate.native.core.roles))!=45:
            raise ValueError("MR21_TRAINABLE_CAPACITY_DRIFT")
        tested=self.restore(candidate.snapshot())
        if tested.snapshot()!=candidate.snapshot() or self.snapshot()!=old:
            raise ValueError("MR21_ATOMIC_NATIVE_SNAPSHOT_DRIFT")
        self.native=candidate.native
        self.states=candidate.states
        return full,without,gate

    def snapshot(self):
        return json.dumps({
            "schema":"yggdrasil.mr21.learned-retention.v1",
            "native":json.loads(self.native.snapshot()),
            "states":self.states,
            "learn_selection":self.learn_selection},
            sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>65536:
            raise ValueError("MR21_BAD_SNAPSHOT")
        d=json.loads(payload)
        if (type(d) is not dict or set(d)!={"schema","native",
            "states","learn_selection"} or
            d["schema"]!="yggdrasil.mr21.learned-retention.v1" or
            type(d["learn_selection"]) is not bool or
            type(d["states"]) is not list or len(d["states"])!=8):
            raise ValueError("MR21_INVALID_NATIVE_SNAPSHOT")
        native=LocalTaskRuntime.restore(json.dumps(d["native"]))
        r=cls(native,d["states"],d["learn_selection"])
        if r.snapshot()!=payload:
            raise ValueError("MR21_NONCANONICAL_NATIVE_STATE")
        return r
