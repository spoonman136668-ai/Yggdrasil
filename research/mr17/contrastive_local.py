"""MR17: local predictive-error contrast, not the MR16 softmax role selector.

Eight existing cell roles encode a learned LOCAL response correction; the 3x7
genome encodes common prediction. Only original public 8-bit observations,
actual prior action and authentic next 8 public bits enter updates.

For each cell i, the feedback e_i minus the mean immediate-neighbor feedback
assigns LOCAL, contrastive credit, not a privileged functional-role teacher.
No role-ID lookup, object identity, hidden state, target oracle, extra model
coefficient, protected science, or post-lesion training.
"""
import math
from yggdrasil.developmental import N, K, D, valid, sig
from yggdrasil.task_runtime import LocalTaskRuntime
from research.mr16.native_local_online import native_action_features


def local_basis(prior, action, i):
    valid(prior)
    if type(action) is not int or not 0 <= action <= 6 or type(i) is not int or not 0 <= i < N:
        raise ValueError("MR17_INVALID_ACTION_OR_CELL")
    # Generic same three local residual bases at ALL cells. Nothing encodes
    # an upstream object identity, evaluator role or source-specific answer.
    return (1., float(action/3.0-1.), float(2*prior[i]-1))


class LocalContrastLearner:
    __slots__ = ("rt",)

    def __init__(self, rt=None):
        self.rt = LocalTaskRuntime() if rt is None else rt
        if type(self.rt) is not LocalTaskRuntime or self.rt.damaged:
            raise ValueError("MR17_ORIGINAL_PRELESION_RUNTIME_REQUIRED")

    def predict(self, prior, action):
        valid(prior)
        if type(action) is not int or not 0 <= action <= 6:
            raise ValueError("MR17_INVALID_ACTION")
        out=[]
        for i in range(N):
            f=native_action_features(self.rt,prior,i,action)
            g=local_basis(prior,action,i)
            # Original 21 shared coefficients supply the global predictor.
            # Original 24 roles now supply LOCAL prediction residuals, not
            # mixture-gating logits. Same fixed 45 coefficients overall.
            common=sum(sum(a*b for a,b in zip(row,f)) for row in self.rt.core.genome)/K
            local=sum(a*b for a,b in zip(self.rt.core.roles[i],g))
            out.append(sig(common+local))
        if any(not math.isfinite(p) for p in out):
            raise ValueError("MR17_NONFINITE_PREDICTION")
        return out

    def observe_after_original_step(self,prior,action,observed,rate=.035):
        valid(prior);valid(observed)
        if (type(action) is not int or not 0 <= action <= 6 or
            type(rate) not in (int,float) or not math.isfinite(rate) or
            not 0 < rate <= .1):
            raise ValueError("MR17_INVALID_FEEDBACK_ENVELOPE")
        frozen=self.rt.snapshot()
        proposed=LocalTaskRuntime.restore(frozen)
        if proposed.damaged:
            raise ValueError("MR17_LABELS_AFTER_LESION_FORBIDDEN")
        p=self.predict(prior,action)
        errors=[y-v for y,v in zip(observed,p)]
        features=[native_action_features(proposed,prior,i,action) for i in range(N)]
        # Local-only causal credit: no role identities or non-neighbor
        # outcome is used in computing cell i's private correction.
        credits=[]
        for i in range(N):
            left,right=proposed.neighbors[i]
            credits.append(errors[i]-(errors[left]+errors[right])/2.)
        for i in range(N):
            basis=local_basis(prior,action,i)
            for j in range(K):
                u=proposed.core.roles[i][j]+rate*credits[i]*basis[j]
                if not math.isfinite(u):
                    raise ValueError("MR17_NONFINITE_PRIVATE_CREDIT")
                proposed.core.roles[i][j]=max(-20.,min(20.,u))
        # The common predictor aggregates the same source-observed signals,
        # but only as a shared predictor: it does not overwrite private roles.
        mean_gradient=[sum(errors[i]*features[i][j] for i in range(N))/N
                       for j in range(D)]
        for row in proposed.core.genome:
            for j in range(D):
                u=row[j]+rate*mean_gradient[j]
                if not math.isfinite(u):
                    raise ValueError("MR17_NONFINITE_COMMON_GRADIENT")
                row[j]=max(-15.,min(15.,u))
        proposed.core.events+=1
        if (sum(len(row) for row in proposed.core.genome)+
            sum(len(row) for row in proposed.core.roles)!=45):
            raise ValueError("MR17_MODEL_CAPACITY_DRIFT")
        packed=proposed.snapshot()
        if LocalTaskRuntime.restore(packed).snapshot()!=packed:
            raise ValueError("MR17_UNRESTORABLE_STATE")
        if self.rt.snapshot()!=frozen:
            raise ValueError("MR17_NONATOMIC_NATIVE_OBSERVATION")
        self.rt=proposed

    def snapshot(self):
        return self.rt.snapshot()

    @classmethod
    def restore(cls,payload):
        rt=LocalTaskRuntime.restore(payload)
        if rt.damaged:
            raise ValueError("MR17_POSTLESION_TRAINING_FORBIDDEN")
        return cls(rt)

    def ablate_cell(self,cell):
        if type(cell) is not int or not 0<=cell<N:
            raise ValueError("MR17_ABLATION_CELL_INVALID")
        cloned=self.restore(self.snapshot())
        cloned.rt.core.roles[cell]=[0.]*K
        return cloned
