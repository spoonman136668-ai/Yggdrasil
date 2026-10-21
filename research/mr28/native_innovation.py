"""MR28 — original native bounded prediction-INNOVATION state; 45 coefficients.

Unlike MR19's direct target-bit recurrent state, this candidate compresses
only the SURPRISE from an actually observed original native consequence.
The existing third seven-coefficient genome row and third per-cell role
coefficient gate innovation salience. Readout comes from the existing second
genome row / role coefficient. Every number comes from the original permitted
public sample, source action, and *post-action* real public result.

This is a small, frozen surrogate online-learning hypothesis, NOT exact
backpropagation through time. Eight persistent activations are accounted.
"""
import json
import math

from research.mr18.native_public_learning import public_features
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.developmental import sig,valid

N,K,D=8,3,7
LR=0.035
DECAY=0.5
INNOVATION=0.5


def bounded(x,limit=15.):
    if not math.isfinite(x):
        raise ValueError("MR28_NONFINITE_NATIVE_WEIGHT")
    return max(-limit,min(limit,x))


class NativeInnovation45:
    __slots__=("runtime","state")

    def __init__(self,runtime=None,state=None):
        self.runtime=LocalTaskRuntime() if runtime is None else runtime
        self.state=[0.]*N if state is None else list(state)
        if (type(self.runtime) is not LocalTaskRuntime or
            self.runtime.damaged or
            self.runtime.neighbors!=LocalTaskRuntime().neighbors or
            type(self.state) is not list or len(self.state)!=N or
            any(type(v) not in (int,float) or not math.isfinite(v)
                or abs(v)>1.00000001 for v in self.state)):
            raise ValueError("MR28_UNQUALIFIED_NATIVE_MODEL_IDENTITY")

    def reset_episode(self):
        self.state=[0.]*N

    def predict(self,raw,bits,action,drop_temporal_state=False):
        valid(bits)
        if type(drop_temporal_state) is not bool:
            raise ValueError("MR28_INVALID_ABLATION_FLAG")
        probabilities=[]
        for i in range(N):
            feature=public_features(raw,bits,action,i)
            genome=self.runtime.core.genome
            role=self.runtime.core.roles[i]
            h=0. if drop_temporal_state else self.state[i]
            current=sum(w*x for w,x in zip(genome[0],feature))
            effect=sum(w*x for w,x in zip(genome[1],feature))
            probabilities.append(sig(current+role[0]+h*(effect+role[1])))
        if any(not math.isfinite(p) or p<0 or p>1 for p in probabilities):
            raise ValueError("MR28_INVALID_NATIVE_PROBABILITY")
        return probabilities

    def observe(self,raw,bits,action,outcomes,train=True):
        valid(bits);valid(outcomes)
        if type(train) is not bool:
            raise ValueError("MR28_TRAIN_FLAG_INVALID")
        forecast=self.predict(raw,bits,action)
        frozen=self.snapshot()
        candidate=self.restore(frozen)
        for i,target in enumerate(outcomes):
            feature=public_features(raw,bits,action,i)
            genome=candidate.runtime.core.genome
            roles=candidate.runtime.core.roles[i]
            old_state=candidate.state[i]
            innovation=target-forecast[i]
            if train:
                # Source-supervised proper pre-outcome prediction gradient.
                for j,f in enumerate(feature):
                    genome[0][j]=bounded(genome[0][j]+LR*innovation*f)
                    genome[1][j]=bounded(
                        genome[1][j]+LR*innovation*old_state*f)
                roles[0]=bounded(roles[0]+LR*innovation,20.)
                roles[1]=bounded(roles[1]+LR*innovation*old_state,20.)
                # Frozen local innovation-salience SURROGATE, not BPTT.
                # It tests whether unpredictable action-conditioned sensory
                # results should be retained, without object/door labels.
                salience=innovation*old_state
                for j,f in enumerate(feature):
                    genome[2][j]=bounded(
                        genome[2][j]+LR*salience*f)
                roles[2]=bounded(roles[2]+LR*salience,20.)
            strength=math.tanh(
                sum(w*f for w,f in zip(genome[2],feature))+roles[2])
            candidate.state[i]=math.tanh(
                DECAY*old_state+INNOVATION*innovation*strength)
            if abs(candidate.state[i])>1.00000001:
                raise ValueError("MR28_BOUNDED_INNOVATION_STATE_DRIFT")
        if train:
            candidate.runtime.core.events+=1
        if (sum(map(len,candidate.runtime.core.genome))+
            sum(map(len,candidate.runtime.core.roles))!=45 or
            len(candidate.state)!=8):
            raise ValueError("MR28_NATIVE_CAPACITY_DRIFT")
        packed=candidate.snapshot()
        if self.snapshot()!=frozen or self.restore(packed).snapshot()!=packed:
            raise ValueError("MR28_NONATOMIC_OR_NONRESTORABLE_STATE")
        self.runtime=candidate.runtime
        self.state=candidate.state

    def snapshot(self):
        return json.dumps({
            "schema":"yggdrasil.mr28.native-innovation45.v1",
            "native_runtime":json.loads(self.runtime.snapshot()),
            "eight_ephemeral_innovations":self.state
        },sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>65536:
            raise ValueError("MR28_UNBOUNDED_SNAPSHOT")
        obj=json.loads(payload)
        if (type(obj) is not dict or
            set(obj)!={"schema","native_runtime",
                       "eight_ephemeral_innovations"} or
            obj["schema"]!="yggdrasil.mr28.native-innovation45.v1"):
            raise ValueError("MR28_SOURCE_MODEL_SCHEMA_CHANGED")
        runtime=LocalTaskRuntime.restore(
            json.dumps(obj["native_runtime"]))
        state=obj["eight_ephemeral_innovations"]
        model=cls(runtime,state)
        if model.snapshot()!=payload:
            raise ValueError("MR28_NONCANONICAL_SOURCE_SNAPSHOT")
        return model
