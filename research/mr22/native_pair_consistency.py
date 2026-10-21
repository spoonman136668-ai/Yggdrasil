"""MR22: self-supervised causal-frame consistency on original 45 native slots.

The *only* pair correspondence given to the learner is equality of currently
PUBLIC observed image pixels under two earlier, real native action histories.
Native world grid, pose, object/role identity and rewards are evaluator-only
and never enter this algorithm. A consistency gradient acts on existing
genome feature slot 4 (the previous-view delta), with NO new coefficients.

Conventional same-model/full-input and engineered delta-agnostic 45-weight
controls are trained from exactly the same original native action outcomes.
This is a DEV mechanism, not scientific transfer or world-frame recovery.
"""
import math
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.developmental import N,K, sig, softmax
from research.mr18.native_public_learning import Native45, public_features, validate


class DeltaAgnostic45(Native45):
    """Conventional 45-slot same-input nonlearned reference-frame control."""
    def features(self,raw,bits,action,i):
        f=list(public_features(raw,bits,action,i))
        f[4]=0.0
        return tuple(f)


def one_pair_divergence(model, raw, bits_a, bits_b, action):
    validate(raw,bits_a,action);validate(raw,bits_b,action)
    a=model.predict(raw,bits_a,action)
    b=model.predict(raw,bits_b,action)
    return sum(abs(x-y) for x,y in zip(a,b))/N


class PublicConsistency45(Native45):
    def learn_matched_public_pair(self,raw,bits_a,bits_b,action,rate=0.1):
        validate(raw,bits_a,action); validate(raw,bits_b,action)
        if (type(rate) not in (int,float) or not math.isfinite(rate) or
            not 0<rate<=0.1):
            raise ValueError("MR22_INVALID_FROZEN_PAIR_RATE")
        # PUBLIC-image equality is attested by caller prior to native step.
        # This routine cannot accept privileged original world truth or any
        # future native target/y. Pair image bytes are SAME for both arms.
        frozen=self.snapshot()
        if tuple(bits_a)==tuple(bits_b):
            return {"changed":False,"pair_abs_pre":0.,"pair_abs_post":0.}
        features_a=[self.features(raw,bits_a,action,i) for i in range(N)]
        features_b=[self.features(raw,bits_b,action,i) for i in range(N)]
        if any(any(
            fa[j]!=fb[j] for j in range(7) if j!=4
        ) for fa,fb in zip(features_a,features_b)):
            raise ValueError("MR22_NONDELTA_INPUT_DIFFERENCE")
        proposal=LocalTaskRuntime.restore(frozen)
        gradient=[0.]*K
        pre=one_pair_divergence(self,raw,bits_a,bits_b,action)
        # d/dw_k4 [(pA-pB)^2]/8 uses ORIGINAL expert mixture sigmoid.
        # Identical source-public images/actions mean differences can arise
        # only from prior path-dependent MR15 delta values at feature 4.
        for i in range(N):
            g=softmax(proposal.core.roles[i])
            pa,pb=0.,0.
            dha,dhb=[0.]*K,[0.]*K
            for k,row in enumerate(proposal.core.genome):
                za=sum(w*f for w,f in zip(row,features_a[i]))
                zb=sum(w*f for w,f in zip(row,features_b[i]))
                sa,sb=sig(za),sig(zb)
                pa+=g[k]*sa
                pb+=g[k]*sb
                dha[k]=g[k]*sa*(1.-sa)*features_a[i][4]
                dhb[k]=g[k]*sb*(1.-sb)*features_b[i][4]
            for k in range(K):
                gradient[k]+=2*(pa-pb)*(dha[k]-dhb[k])/N
        for k in range(K):
            value=proposal.core.genome[k][4]-rate*gradient[k]
            if not math.isfinite(value):
                raise ValueError("MR22_NONFINITE_PAIR_CREDIT")
            proposal.core.genome[k][4]=max(-15.,min(15.,value))
        if sum(map(len,proposal.core.genome))+sum(map(len,proposal.core.roles))!=45:
            raise ValueError("MR22_FIXED_BUDGET_DRIFT")
        packed=proposal.snapshot()
        if LocalTaskRuntime.restore(packed).snapshot()!=packed or self.snapshot()!=frozen:
            raise ValueError("MR22_NONATOMIC_MODEL_STATE")
        self.rt=proposal
        post=one_pair_divergence(self,raw,bits_a,bits_b,action)
        return {"changed":post!=pre,"pair_abs_pre":pre,
                "pair_abs_post":post,
                "gradient_abs":sum(map(abs,gradient))}

    @classmethod
    def restore(cls,payload):
        value=cls("public",LocalTaskRuntime.restore(payload))
        if value.snapshot()!=payload:
            raise ValueError("MR22_NONCANONICAL_NATIVE_SNAPSHOT")
        return value
