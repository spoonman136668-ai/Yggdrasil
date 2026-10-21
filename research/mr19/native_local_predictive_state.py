"""MR19 -- event-conditioned persistent local prediction state, DEV ONLY.

A genuinely stateful alternative to MR18's feed-forward local experts.
The current MR18 PUBLIC feature map is frozen byte-for-byte: no new object
decoder, source-dependent identity, hidden world, reward, or teacher role.
Existing LocalTaskRuntime 3x7 shared and 8x3 cell-private coefficients = 45.
Eight additional ephemeral cell activations and their serialized costs are
explicitly accounted. The source-observed post-action visual delta updates
a local predictive state; no episode completion/goal labels are consumed.

Plasticity is a FROZEN heuristic predictive-error rule (NOT full BPTT).
A state advantage would not establish autonomous cognition by itself.
"""
import json
import math

from research.mr18.native_public_learning import public_features
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.developmental import sig,valid

N=8
K=3
D=7
RATE=.035
STATE_GAIN=.65
OUTCOME_GAIN=.30


def bounded(value, limit=15.):
    if not math.isfinite(value):
        raise ValueError("MR19_NONFINITE_NATIVE_PLASTICITY")
    return max(-limit,min(limit,value))


class NativeLocalPredictiveState:
    def __init__(self, runtime=None, state=None):
        self.runtime=LocalTaskRuntime() if runtime is None else runtime
        self.state=[0.]*N if state is None else list(state)
        if (type(self.runtime) is not LocalTaskRuntime or
            self.runtime.damaged or
            self.runtime.neighbors!=LocalTaskRuntime().neighbors or
            type(self.state) is not list or len(self.state)!=N or
            any(type(v) not in (int,float) or
                not math.isfinite(v) or abs(v)>1.0000001
                for v in self.state)):
            raise ValueError("MR19_INVALID_ORIGINAL_LOCAL_STATE")

    def reset_episode(self):
        self.state=[0.]*N

    def predict(self,raw,bits,action,drop_temporal_state=False):
        valid(bits)
        if type(drop_temporal_state) is not bool:
            raise ValueError("MR19_INVALID_ABLATION")
        out=[]
        for i in range(N):
            f=public_features(raw,bits,action,i)
            g=self.runtime.core.genome
            r=self.runtime.core.roles[i]
            h=0. if drop_temporal_state else self.state[i]
            shared=sum(g[0][j]*f[j] for j in range(D))
            temporal=math.tanh(sum(g[1][j]*f[j] for j in range(D)))
            out.append(sig(shared+r[0]+h*(temporal+r[1])))
        return out

    def observe(self,raw,bits,action,targets,train=True):
        """Post-action real public-image consequences only, transactional."""
        valid(bits);valid(targets)
        if type(train) is not bool:
            raise ValueError("MR19_INVALID_TRAIN_FLAG")
        # Validate all inputs and record predictions BEFORE model mutation.
        predictions=self.predict(raw,bits,action)
        frozen=self.snapshot()
        proposal=self.restore(frozen)
        for i,target in enumerate(targets):
            f=public_features(raw,bits,action,i)
            h=proposal.state[i]
            g=proposal.runtime.core.genome
            r=proposal.runtime.core.roles[i]
            temporal=math.tanh(sum(g[1][j]*f[j] for j in range(D)))
            residual=target-predictions[i]
            if train:
                # Original 45 trainable slots: no additional predictor fields.
                # Local recurrence and common perceptual pathways are updated
                # from independently observed native predictive error.
                for j in range(D):
                    g[0][j]=bounded(g[0][j]+RATE*residual*f[j])
                    g[1][j]=bounded(g[1][j]+RATE*residual*h*
                                    (1.-temporal**2)*f[j])
                    # Frozen local surprise-derived state-formation rule.
                    g[2][j]=bounded(g[2][j]+.01*residual*
                                    (2*target-1)*f[j])
                r[0]=bounded(r[0]+RATE*residual,20.)
                r[1]=bounded(r[1]+RATE*residual*h,20.)
                r[2]=bounded(r[2]+.01*residual*(2*target-1),20.)
            drive=math.tanh(sum(g[2][j]*f[j] for j in range(D)))
            proposal.state[i]=math.tanh(
                STATE_GAIN*h+OUTCOME_GAIN*(2*target-1)+
                .05*drive+.05*r[2]*(2*target-1))
        if train:
            proposal.runtime.core.events += 1
        assert sum(len(row) for row in proposal.runtime.core.genome)+sum(
            len(row) for row in proposal.runtime.core.roles)==45
        if self.snapshot()!=frozen:
            raise ValueError("MR19_NONTRANSACTIONAL_NATIVE_STATE")
        checked=self.restore(proposal.snapshot())
        if checked.snapshot()!=proposal.snapshot():
            raise ValueError("MR19_NATIVE_COLD_STATE_ROUNDTRIP_FAILED")
        self.runtime=proposal.runtime
        self.state=proposal.state
        return predictions

    def snapshot(self):
        return json.dumps({
            "schema":"yggdrasil.mr19.local-predictive-state.v1",
            "native_runtime":json.loads(self.runtime.snapshot()),
            "ephemeral_states":self.state
        },sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>65536:
            raise ValueError("MR19_INVALID_SNAPSHOT")
        obj=json.loads(payload)
        if (type(obj) is not dict or
            set(obj)!={"schema","native_runtime","ephemeral_states"} or
            obj["schema"]!="yggdrasil.mr19.local-predictive-state.v1"):
            raise ValueError("MR19_INVALID_SCHEMA")
        rt=LocalTaskRuntime.restore(json.dumps(obj["native_runtime"]))
        state=obj["ephemeral_states"]
        if (type(state) is not list or len(state)!=N or
            any(type(x) not in (int,float) or
                not math.isfinite(x) or abs(x)>1.0000001 for x in state)):
            raise ValueError("MR19_INVALID_EPISODIC_STATE")
        result=cls(rt,state)
        if result.snapshot()!=payload:
            raise ValueError("MR19_NONCANONICAL_SNAPSHOT")
        return result
