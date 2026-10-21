"""MR18: learned local public-byte distinctions, fixed native 45 coefficients.

Original MiniGrid public 7x7x3 image ONLY; exact MR15 eight fixed tile
locations, raw UINT8 bytes normalized uniformly without decoding object IDs.
Common native 21 coefficients predict public action/context; private 8x3
coefficients learn each cell's visible three-channel causal distinctions.

Two modes use EXACTLY the same model/input/budget: contrastive neighborhood
credit (candidate) versus direct-local error (trained conventional control).
No extra learned storage, hidden map, reward, role labels or first-use.
"""
import math

from yggdrasil.developmental import N, K, D, valid, sig
from yggdrasil.task_runtime import LocalTaskRuntime
from research.mr16.native_local_online import native_action_features
from research.mr15.public_view_delta import public_raw_view


def raw_cell_features(public_image):
    # Derive raw bytes ONLY from original public image before native step.
    raw=public_raw_view(public_image)
    return tuple(tuple(2.0*(raw[i*3+j]/255.0)-1.0
                       for j in range(3)) for i in range(N))


class PublicByteLocalLearner:
    __slots__=("rt","contrast")
    def __init__(self,rt=None,*,contrast):
        self.rt=LocalTaskRuntime() if rt is None else rt
        if type(contrast) is not bool or type(self.rt) is not LocalTaskRuntime or self.rt.damaged:
            raise ValueError("MR18_INVALID_NATIVE_LEARNER_IDENTITY")
        self.contrast=contrast

    def predict(self,prior,action,public_image):
        valid(prior)
        if type(action) is not int or not 0<=action<=6:
            raise ValueError("MR18_INVALID_NATIVE_ACTION")
        local=raw_cell_features(public_image)
        out=[]
        for i in range(N):
            f=native_action_features(self.rt,prior,i,action)
            common=sum(sum(a*b for a,b in zip(row,f))
                       for row in self.rt.core.genome)/K
            local_effect=sum(w*v for w,v in zip(self.rt.core.roles[i],local[i]))
            out.append(sig(common+local_effect))
        return out

    def observe(self,prior,action,public_image,next_bits,rate=.035):
        # Unlike a generic source-independent fixture, this call is made
        # ONLY by MR18's original env.step recorder AFTER the original
        # MiniGrid next public observation has been obtained.
        valid(prior);valid(next_bits)
        if (type(action) is not int or not 0<=action<=6 or
            type(rate) not in (float,int) or not math.isfinite(rate) or
            not 0<rate<=.1):
            raise ValueError("MR18_INVALID_LEARNING_ENVELOPE")
        original=self.snapshot()
        proposal=LocalTaskRuntime.restore(original)
        old_predictions=self.predict(prior,action,public_image)
        errors=[y-p for y,p in zip(next_bits,old_predictions)]
        local=raw_cell_features(public_image)
        features=[native_action_features(proposal,prior,i,action)
                  for i in range(N)]
        for i in range(N):
            left,right=proposal.neighbors[i]
            own=errors[i]
            local_credit=(own-(errors[left]+errors[right])/2.) if self.contrast else own
            for j in range(K):
                candidate=proposal.core.roles[i][j]+rate*local_credit*local[i][j]
                if not math.isfinite(candidate):
                    raise ValueError("MR18_NONFINITE_LOCAL_CREDIT")
                proposal.core.roles[i][j]=max(-20.,min(20.,candidate))
        mean_gradient=[sum(errors[i]*features[i][j] for i in range(N))/N
                       for j in range(D)]
        # No new shared latent state: update same original 3x7 genome rows.
        for row in proposal.core.genome:
            for j in range(D):
                candidate=row[j]+rate*mean_gradient[j]
                if not math.isfinite(candidate):
                    raise ValueError("MR18_NONFINITE_SHARED_CREDIT")
                row[j]=max(-15.,min(15.,candidate))
        proposal.core.events+=1
        if sum(len(r) for r in proposal.core.roles)+sum(
            len(r) for r in proposal.core.genome)!=45:
            raise ValueError("MR18_45_COEFFICIENT_BUDGET_DRIFT")
        packed=proposal.snapshot()
        if LocalTaskRuntime.restore(packed).snapshot()!=packed:
            raise ValueError("MR18_MODEL_SNAPSHOT_RESTART_DRIFT")
        if self.snapshot()!=original:
            raise ValueError("MR18_CONCURRENT_STATE_DRIFT")
        self.rt=proposal

    def snapshot(self):
        return self.rt.snapshot()

    @classmethod
    def restore(cls,payload,*,contrast):
        rt=LocalTaskRuntime.restore(payload)
        if rt.damaged:
            raise ValueError("MR18_POSTLESION_ORACLE_TRAINING_FORBIDDEN")
        return cls(rt,contrast=contrast)

    def ablate_cell(self,i):
        if type(i) is not int or not 0<=i<N:
            raise ValueError("MR18_BAD_CELL")
        clone=self.restore(self.snapshot(),contrast=self.contrast)
        clone.rt.core.roles[i]=[0.]*K
        return clone


class RawPublicConditionalCount:
    """Fully informed nonbudget-matched native conditional count control."""
    __slots__=("neighbors","counts")
    def __init__(self):
        self.neighbors=LocalTaskRuntime().neighbors
        self.counts={}
    def key(self,prior,action,public_image,i):
        valid(prior)
        if type(action) is not int or not 0<=action<=6:
            raise ValueError("MR18_COUNT_BAD_ACTION")
        # Same LOCAL public raw inputs as both 45-coefficient models.
        # Conventional control is given NO hidden object, map or role label.
        from research.mr15.public_view_delta import public_raw_view
        raw=public_raw_view(public_image)
        a,b=self.neighbors[i]
        return (i,prior[i],prior[a],prior[b],action,
                raw[3*i],raw[3*i+1],raw[3*i+2])
    def predict(self,prior,action,image):
        return [(self.counts.get(self.key(prior,action,image,i),(0,0))[0]+1)/
                (self.counts.get(self.key(prior,action,image,i),(0,0))[1]+2)
                for i in range(N)]
    def observe(self,prior,action,image,outcome):
        valid(outcome)
        for i,y in enumerate(outcome):
            k=self.key(prior,action,image,i)
            yes,total=self.counts.get(k,(0,0))
            self.counts[k]=(yes+y,total+1)
