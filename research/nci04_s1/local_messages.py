"""NCI-04 S1: locally learned predictive contribution from neighboring cells.

New architectural hypothesis, NOT a retune of the MR19–MR33 recurrence:
local cells send their learned predictive states to two neighboring cells,
whose message usefulness is itself trainable. Errors on later authentic
native action outcomes give exactly-one-step delayed analytic gradient to
the state encoders that generated those prior neighbor messages.

45 original LocalGenome weights = three shared 7-input rows (21) plus
eight 3-weight local cellular roles (24). Exactly eight episodic native
prediction states are retained during inference. The existing eight-cell
ring is a STRUCTURAL prior, not a discovered world-space neighborhood.
Role learning is observer-relative, not physical object specialization.

IMPORTANT honest training cost: updating the latent encoder using actual
later outcomes requires the prior eight 7-feature vectors and eight prior
binary signs (64 float scalars) as a training-only trace. This is explicitly
serialized, measured, and NOT an equal-total-resource scientific win.
"""
import json
import math

from research.mr18.native_public_learning import public_features,validate
from yggdrasil.developmental import sig,valid
from yggdrasil.task_runtime import LocalTaskRuntime

N=8
D=7
RATE=0.035


def bound(value,limit=15.):
    if not math.isfinite(value):
        raise ValueError("NCI04_S1_NONFINITE_COEFFICIENT")
    return max(-limit,min(limit,value))


class LocalPredictiveMessages45:
    def __init__(self,runtime=None,state=None,trace=None):
        self.runtime=LocalTaskRuntime() if runtime is None else runtime
        self.state=[0.]*N if state is None else list(state)
        self.trace=trace
        if (type(self.runtime) is not LocalTaskRuntime or
            self.runtime.damaged or
            self.runtime.neighbors!=LocalTaskRuntime().neighbors or
            len(self.state)!=N or
            any(type(x) not in (int,float) or not math.isfinite(x) or
                abs(x)>1.000000001 for x in self.state) or
            sum(map(len,self.runtime.core.genome))+
                sum(map(len,self.runtime.core.roles))!=45):
            raise ValueError("NCI04_S1_NATIVE_45_STATE_INVALID")
        if self.trace is not None:
            f,s=self.trace
            if (len(f)!=N or any(len(row)!=D for row in f) or
                len(s)!=N or any(x not in (-1.,1.) for x in s)):
                raise ValueError("NCI04_S1_TRAINING_ONLY_TRACE_INVALID")

    def reset_episode(self):
        self.state=[0.]*N
        self.trace=None

    def features(self,raw,bits,action):
        validate(raw,bits,action)
        return [public_features(raw,bits,action,i) for i in range(N)]

    def _logits(self,features,use_neighbors=True,use_state=True):
        g=self.runtime.core.genome
        roles=self.runtime.core.roles
        outputs=[]
        for i,f in enumerate(features):
            st=self.state[i] if use_state else 0.
            a,b=self.runtime.neighbors[i]
            # Exactly two neighbor state scalars per local cell read.
            incoming=.5*(self.state[a]+self.state[b]) if (
                use_neighbors and use_state) else 0.
            value=(sum(g[0][j]*f[j] for j in range(D))+
                   roles[i][0]+
                   st*sum(g[1][j]*f[j] for j in range(D))+
                   roles[i][1]*incoming)
            outputs.append(value)
        return outputs

    def predict(self,raw,bits,action,drop_neighbors=False,drop_state=False):
        if type(drop_neighbors) is not bool or type(drop_state) is not bool:
            raise ValueError("NCI04_S1_INVALID_INTERVENTION_ABLATION")
        f=self.features(raw,bits,action)
        return [sig(x) for x in self._logits(
            f,not drop_neighbors,not drop_state)]

    def observe(self,raw,bits,action,targets,train=True):
        validate(raw,bits,action)
        valid(targets)
        if type(train) is not bool:
            raise ValueError("NCI04_S1_TRAINING_IDENTITY_INVALID")
        f=self.features(raw,bits,action)
        before=self.snapshot()
        pred=[sig(x) for x in self._logits(f)]
        signed=[float(2*t-1) for t in targets]
        if train:
            # Compute the entire local gradient from BEFORE-step weights.
            # Current source consequence may update weights only AFTER
            # preaction predictions above have been frozen.
            g=self.runtime.core.genome
            role=self.runtime.core.roles
            err=[y-p for y,p in zip(targets,pred)]
            dg=[[0.]*D for _ in range(3)]
            dr=[[0.]*3 for _ in range(N)]
            for i in range(N):
                left,right=self.runtime.neighbors[i]
                incoming=.5*(self.state[left]+self.state[right])
                dr[i][0]=err[i]
                dr[i][1]=err[i]*incoming
                for j in range(D):
                    dg[0][j]+=err[i]*f[i][j]/N
                    dg[1][j]+=err[i]*self.state[i]*f[i][j]/N
            # TRUE delayed predictive credit to encoder parameters,
            # not a same-event reconstruction/novelty objective.
            if self.trace is not None:
                prior_features,prior_signs=self.trace
                for i in range(N):
                    left,right=self.runtime.neighbors[i]
                    own=sum(g[1][j]*f[i][j] for j in range(D))
                    influence=(err[i]*own +
                        .5*err[left]*role[left][1]+
                        .5*err[right]*role[right][1])
                    sens=(1-self.state[i]**2)*influence
                    dr[i][2]+=sens*prior_signs[i]
                    for j in range(D):
                        dg[2][j]+=sens*prior_features[i][j]/N
            for k in range(3):
                for j in range(D):
                    g[k][j]=bound(g[k][j]+RATE*dg[k][j])
            for i in range(N):
                for k in range(3):
                    role[i][k]=bound(role[i][k]+RATE*dr[i][k],20.)
            self.runtime.core.events+=1
        # A new message/state forms locally ONLY from public source
        # history that just occurred. No future, grid or object labels.
        g=self.runtime.core.genome
        role=self.runtime.core.roles
        self.state=[
            math.tanh(sum(g[2][j]*f[i][j] for j in range(D))+
                      role[i][2]*signed[i])
            for i in range(N)]
        self.trace=(f,signed) if train else None
        if (sum(map(len,self.runtime.core.genome))+
            sum(map(len,self.runtime.core.roles))!=45 or
            self.restore(self.snapshot()).snapshot()!=self.snapshot()):
            raise ValueError("NCI04_S1_PARAMETERS_OR_RESTART_DRIFT")
        return pred

    def snapshot(self):
        return json.dumps({
            "schema":"yggdrasil.nci04.s1.local-messaging.v1",
            "native":json.loads(self.runtime.snapshot()),
            "state":self.state,
            "train_trace":self.trace
        },sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>65536:
            raise ValueError("NCI04_S1_SNAPSHOT_SIZE_INVALID")
        obj=json.loads(payload)
        if (type(obj) is not dict or
            set(obj)!={"schema","native","state","train_trace"} or
            obj["schema"]!="yggdrasil.nci04.s1.local-messaging.v1"):
            raise ValueError("NCI04_S1_SNAPSHOT_SCHEMA_INVALID")
        out=cls(LocalTaskRuntime.restore(json.dumps(obj["native"])),
                obj["state"],obj["train_trace"])
        if out.snapshot()!=payload:
            raise ValueError("NCI04_S1_NONCANONICAL_STATE")
        return out

    def local_roles(self):
        return [tuple(v) for v in self.runtime.core.roles]
