"""MR23B fixed-budget action-conditioned camera correspondence.

Only original current PUBLIC image and the 24-byte MR15 sampled-prior
view are used. Three candidate transforms about the observer's image
coordinate frame are engineered alternatives, NOT learned objects or
source world identities. An original LocalTaskRuntime genome uses 21
of its EXISTING 45 coefficient slots to learn an action-conditioned
hypothesis distribution; 24 original local-role slots are untouched.

The model selects a hypothesis BEFORE original source env.step. Training
then uses the genuine observed public image to adjust its source-blind
action policy. The same two source-cache points must be visible for all
hypotheses so missing pixels can never improve a hypothesis's score.
"""
import math

from research.mr15.public_view_delta import POSITIONS, public_raw_view
from yggdrasil.task_runtime import LocalTaskRuntime

ANCHOR=(3,6)
COMMON=((3,3),(3,5))
HYPOTHESES=("identity","left","right")
LR=.35


def projected(point,hypothesis):
    dx,dy=point[0]-ANCHOR[0],point[1]-ANCHOR[1]
    if hypothesis==0:
        return point
    if hypothesis==1:
        return ANCHOR[0]-dy,ANCHOR[1]+dx
    if hypothesis==2:
        return ANCHOR[0]+dy,ANCHOR[1]-dx
    raise ValueError("MR23B_INVALID_TRANSFORM")


# Always require two shared, source-independent, geometric cached points.
assert all(
    0<=k<7
    for point in COMMON
    for h in range(3)
    for k in projected(point,h)
)


def triple_from_cached(raw,point):
    if (type(raw) not in (tuple,list) or len(raw)!=24 or
        any(type(v) is not int or not 0<=v<=255 for v in raw)):
        raise ValueError("MR23B_INVALID_ORIGINAL_24BYTE_PRIOR")
    i=POSITIONS.index(point)
    return tuple(raw[3*i:3*i+3])


def public_source_scores(previous_raw,new_public_image):
    # Validate full 7x7 public source image via the original MR15 contract.
    public_raw_view(new_public_image)
    observed=[]
    for h in range(3):
        agree=0
        for original_point in COMMON:
            x,y=projected(original_point,h)
            old=triple_from_cached(previous_raw,original_point)
            new=tuple(int(new_public_image[x,y,k]) for k in range(3))
            agree+=int(old==new)
        observed.append(agree/len(COMMON))
    return tuple(observed)


def action_features(action):
    if type(action) is not int or not 0<=action<=6:
        raise ValueError("MR23B_INVALID_ORIGINAL_NATIVE_ACTION")
    return tuple(float(i==action) for i in range(7))


class NativeSourceCorrespondence:
    def __init__(self,runtime=None):
        self.runtime=LocalTaskRuntime() if runtime is None else runtime
        if (type(self.runtime) is not LocalTaskRuntime or
            self.runtime.damaged or
            self.runtime.neighbors!=LocalTaskRuntime().neighbors or
            len(self.runtime.core.genome)!=3 or
            any(len(row)!=7 for row in self.runtime.core.genome) or
            sum(len(row) for row in self.runtime.core.roles)!=24):
            raise ValueError("MR23B_NATIVE_45_SLOT_MODEL_INVALID")

    def predict_before_native_step(self,action):
        f=action_features(action)
        logits=[sum(a*x for a,x in zip(row,f))
                for row in self.runtime.core.genome]
        high=max(logits)
        es=[math.exp(x-high) for x in logits]
        denom=sum(es)
        if not math.isfinite(denom) or denom<=0:
            raise ValueError("MR23B_INVALID_CORRESPONDENCE_NORMALIZER")
        return tuple(v/denom for v in es)

    def update_after_original_source(self,action,prior_prob,observed_scores):
        if (type(prior_prob) not in (list,tuple) or len(prior_prob)!=3 or
            type(observed_scores) not in (list,tuple) or
            len(observed_scores)!=3 or
            any(not math.isfinite(x) or not 0<=x<=1
                for x in tuple(prior_prob)+tuple(observed_scores)) or
            tuple(self.predict_before_native_step(action))!=tuple(prior_prob)):
            raise ValueError("MR23B_PREDICTION_OR_SOURCE_SCORE_INVALID")
        frozen=self.runtime.snapshot()
        clone=LocalTaskRuntime.restore(frozen)
        advantage=sum(p*y for p,y in zip(prior_prob,observed_scores))
        # Gradient of expected SOURCE-OBSERVED public visual agreement.
        # No hidden transform label or world identity target enters training.
        for h in range(3):
            delta=LR*prior_prob[h]*(observed_scores[h]-advantage)
            for j,value in enumerate(action_features(action)):
                w=clone.core.genome[h][j]+delta*value
                if not math.isfinite(w):
                    raise ValueError("MR23B_NONFINITE_NATIVE_MODEL")
                clone.core.genome[h][j]=max(-15.,min(15.,w))
        clone.core.events+=1
        if (self.runtime.snapshot()!=frozen or
            len(clone.core.genome)*len(clone.core.genome[0])+
            sum(len(row) for row in clone.core.roles)!=45 or
            LocalTaskRuntime.restore(clone.snapshot()).snapshot()!=
            clone.snapshot()):
            raise ValueError("MR23B_MODEL_CAPACITY_OR_CUSTODY_FAILURE")
        self.runtime=clone

    def snapshot(self):
        return self.runtime.snapshot()

    @classmethod
    def restore(cls,snapshot):
        out=cls(LocalTaskRuntime.restore(snapshot))
        if out.snapshot()!=snapshot:
            raise ValueError("MR23B_SOURCE_NATIVE_MODEL_RESTART_FAILURE")
        return out
