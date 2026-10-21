"""MR28: bounded learned-surprise predictive-state bottleneck, DEV ONLY.

Unlike unconditional MR19 state updates, encode the current native PUBLIC
transition as the SURPRISE under a jointly trained source-public expected
transition. Eight scalars retain compressed exponentially discounted
surprises. Existing 3x7 Yggdrasil genome and 8x3 local roles = EXACTLY 45
trainable coefficients. The code adds no learner buffer, source-object
registry, eligibility arrays, or hidden semantic labels.

Honest limit: the event compressor learns immediate transition expectation
through direct source-public predictive error; the subsequent state reading
is optimized with a one-step local loss surrogate, not exact BPTT or proof
of stable world identities/causal sufficiency. Eight indexed slots remain
CAMERA RELATIVE, not physical cellular specialization.
"""
import json
import math

from research.mr18.native_public_learning import public_features,validate
from yggdrasil.developmental import sig,valid
from yggdrasil.task_runtime import LocalTaskRuntime

N=8;D=7;LEARN=.035;STATE_DECAY=.72;SURPRISE_GAIN=.50


def clip(v,limit=15.):
    if not math.isfinite(v):
        raise ValueError("MR28_NONFINITE_ORIGINAL_NATIVE_LEARNING")
    return min(limit,max(-limit,v))


class PredictiveSurprise45:
    def __init__(self,runtime=None,state=None,learn_encoder=True):
        if type(learn_encoder) is not bool:
            raise ValueError("MR28_INVALID_ENCODING_ABLATION_FLAG")
        self.runtime=LocalTaskRuntime() if runtime is None else runtime
        self.state=[0.]*8 if state is None else list(state)
        self.learn_encoder=learn_encoder
        if (type(self.runtime) is not LocalTaskRuntime or
            self.runtime.damaged or
            self.runtime.neighbors!=LocalTaskRuntime().neighbors or
            len(self.state)!=8 or
            any(type(x) not in (int,float) or not math.isfinite(x)
                or abs(x)>1.0000001 for x in self.state) or
            sum(map(len,self.runtime.core.genome))+
            sum(map(len,self.runtime.core.roles))!=45):
            raise ValueError("MR28_ORIGINAL_FIXED_BUDGET_NATIVE_STATE_DRIFT")

    def reset_episode(self):
        self.state=[0.]*8

    def predict(self,raw,bits,action,drop_history=False):
        validate(raw,bits,action)
        if type(drop_history) is not bool:
            raise ValueError("MR28_INVALID_MEMORY_ABLATION")
        p=[]
        for i in range(N):
            f=public_features(raw,bits,action,i)
            g=self.runtime.core.genome
            role=self.runtime.core.roles[i]
            base=sum(g[0][j]*f[j] for j in range(D))+role[0]
            read=math.tanh(sum(g[1][j]*f[j] for j in range(D)))+role[1]
            h=0. if drop_history else self.state[i]
            p.append(sig(base+h*read))
        return p

    def observe(self,raw,bits,action,target,train=True):
        validate(raw,bits,action);valid(target)
        if type(train) is not bool:
            raise ValueError("MR28_INVALID_NATIVE_TRAINING_FLAG")
        pre=self.predict(raw,bits,action)
        before=self.snapshot()
        proposal=self.restore(before)
        for i,y in enumerate(target):
            f=public_features(raw,bits,action,i)
            g=proposal.runtime.core.genome
            role=proposal.runtime.core.roles[i]
            h=proposal.state[i]
            # Both the output and the source-public compressor are
            # PREDICTED PRE-ACTION, before authentic source native step.
            internal_expected=sig(
                sum(g[2][j]*f[j] for j in range(D))+role[2])
            output_error=y-pre[i]
            surprise=y-internal_expected
            if train:
                tr=math.tanh(sum(g[1][j]*f[j] for j in range(D)))
                for j,x in enumerate(f):
                    g[0][j]=clip(g[0][j]+LEARN*output_error*x)
                    g[1][j]=clip(g[1][j]+LEARN*output_error*h*
                                  (1-tr*tr)*x)
                    if self.learn_encoder:
                        g[2][j]=clip(g[2][j]+LEARN*surprise*x)
                role[0]=clip(role[0]+LEARN*output_error,20.)
                role[1]=clip(role[1]+LEARN*output_error*h,20.)
                if self.learn_encoder:
                    role[2]=clip(role[2]+LEARN*surprise,20.)
            # Crucially the compressed state consumes only the public
            # source error *after* the authentic step. No future source
            # outcome, unbounded history, or privileged label.
            proposal.state[i]=math.tanh(
                STATE_DECAY*h+SURPRISE_GAIN*2.*surprise)
        if train:
            proposal.runtime.core.events+=1
        candidate=proposal.snapshot()
        if (self.snapshot()!=before or
            self.restore(candidate).snapshot()!=candidate or
            sum(map(len,proposal.runtime.core.genome))+
            sum(map(len,proposal.runtime.core.roles))!=45):
            raise ValueError("MR28_NATIVE_MODEL_MUTATION_OR_CUSTODY_DRIFT")
        self.runtime=proposal.runtime
        self.state=proposal.state
        return pre

    def snapshot(self):
        return json.dumps({
            "schema":"yggdrasil.mr28.learned-surprise-bottleneck.v1",
            "original_native_runtime":json.loads(self.runtime.snapshot()),
            "camera_relative_surprise_states":self.state,
            "learn_encoder":self.learn_encoder},
            sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,snapshot):
        if type(snapshot) is not str or len(snapshot)>65536:
            raise ValueError("MR28_INVALID_NATIVE_STATE_SIZE")
        data=json.loads(snapshot)
        if (type(data) is not dict or
            set(data)!={"schema","original_native_runtime",
                        "camera_relative_surprise_states","learn_encoder"} or
            data["schema"]!="yggdrasil.mr28.learned-surprise-bottleneck.v1" or
            type(data["learn_encoder"]) is not bool or
            type(data["camera_relative_surprise_states"]) is not list or
            len(data["camera_relative_surprise_states"])!=8):
            raise ValueError("MR28_INVALID_NATIVE_STATE_SCHEMA")
        rt=LocalTaskRuntime.restore(json.dumps(
            data["original_native_runtime"]))
        m=cls(rt,data["camera_relative_surprise_states"],
              data["learn_encoder"])
        if m.snapshot()!=snapshot:
            raise ValueError("MR28_NONCANONICAL_ORIGINAL_STATE")
        return m
