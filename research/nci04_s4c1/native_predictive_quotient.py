"""NCI-04 S4C1: opt-in native 45-coefficient predictive-state quotient.

Each of the eight Yggdrasil cells retains ONE bounded latent scalar.
Rather than a fixed temporal blend or an imposed topology, each local
state is formed from the cell's own CURRENT PREDICTED outcome and
public source features. Full source-training-episode derivatives learn
whether a projected prediction is useful for later native predictions.

No true current/future native outcome feeds the model's inference state.
The true original next-public outcome is solely the training loss target,
AFTER the source has executed its real action. This is a local-cell
architectural DEVELOPMENT hypothesis, not independent cognitive transfer.

Exactly 3x7 native genome plus 8x3 native cell roles = 45 trained
coefficients, eight source-episode inference states, no ring messages.
Offline full BPTT caches are ADDITIONAL training-only resource memory.
"""
from hashlib import sha256
import json
import math

import numpy as np

from yggdrasil.task_runtime import LocalTaskRuntime

N=8
D=7
PARAMETERS=45
SCHEMA="yggdrasil.nci04.s4c1.native-predicted-outcome-state.v1"


def cell_public_features(x):
    """Seven frozen PUBLIC features for each of eight receiving cells.

    All are projections of the original conventional 23 PUBLIC features,
    with LESS available information than conventional full-23 controls.
    They do not use original source object types, private identities or
    native game state. Action is read from its same 7-way public onehot.
    """
    if type(x) is not np.ndarray or x.shape!=(23,) or (
        not np.all(np.isfinite(x)) or not np.all(x[:16]>=0) or
        not np.all(x[:16]<=1) or
        not np.all((x[16:]==0)|(x[16:]==1)) or
        np.sum(x[16:])!=1.):
        raise ValueError("NCI04_S4C1_INVALID_ORIGINAL_COMMON_PUBLIC_FEATURES")
    a=int(np.argmax(x[16:]))
    angles=2.*math.pi*a/7.
    own=x[:16].reshape(8,2)
    f=np.empty((N,D),dtype=np.float64)
    f[:,0]=1.
    f[:,1:3]=own
    f[:,3]=float(np.mean(own[:,0]))
    f[:,4]=float(np.mean(own[:,1]))
    f[:,5]=math.cos(angles)
    f[:,6]=math.sin(angles)
    return f


class NativePredictiveQuotient45:
    def __init__(self):
        self.native=LocalTaskRuntime()
        if self.native.damaged or len(self.native.core.roles)!=N:
            raise ValueError("NCI04_S4C1_NATIVE_SOURCE_DAMAGED")
        self.g=np.array(self.native.core.genome,dtype=np.float64)
        self.roles=np.array(self.native.core.roles,dtype=np.float64)
        if self.g.shape!=(3,D) or self.roles.shape!=(N,3):
            raise ValueError("NCI04_S4C1_45_SLOT_IDENTITY_DRIFT")
        self.train_updates=0

    def params(self):
        return (self.g,self.roles)

    def _validate_params(self):
        if (self.g.shape!=(3,D) or self.roles.shape!=(N,3) or
            self.g.size+self.roles.size!=PARAMETERS or
            not np.all(np.isfinite(self.g)) or
            not np.all(np.isfinite(self.roles)) or
            np.max(np.abs(self.g))>15 or
            np.max(np.abs(self.roles))>20):
            raise ValueError("NCI04_S4C1_EXCESS_OR_INVALID_NATIVE_PARAMETER")

    def forward(self,episode,zero_state=False,permuted_roles=False,cache=False):
        """Preaction p_t, then local state inferred from p_t, NEVER y_t."""
        self._validate_params()
        if not episode or type(zero_state) is not bool or (
            type(permuted_roles) is not bool):
            raise ValueError("NCI04_S4C1_INVALID_NATIVE_EPISODE")
        roles=(self.roles[[0,2,4,6,1,3,5,7]].copy()
               if permuted_roles else self.roles)
        s=np.zeros(N,dtype=np.float64)
        forecasts=[]
        details=[]
        for row in episode:
            x=row[0]
            f=cell_public_features(x)
            used_s=np.zeros(N) if zero_state else s
            read=f@self.g[1]+roles[:,1]
            u=f@self.g[0]+roles[:,0]+used_s*read
            p=1./(1.+np.exp(-np.clip(u,-35.,35.)))
            next_s=np.tanh(f@self.g[2]+roles[:,2]*(2.*p-1.))
            if not np.all(np.isfinite(next_s)) or np.max(np.abs(next_s))>1.:
                raise ValueError("NCI04_S4C1_NATIVE_INFERENCE_STATE_INVALID")
            forecasts.append(p)
            if cache:
                details.append((f,used_s.copy(),read,p,next_s.copy()))
            s=next_s
        ps=np.array(forecasts,dtype=np.float64)
        return (ps,details) if cache else ps

    def bernoulli_ce(self,episode):
        pp=self.forward(episode)
        y=np.array([r[2] for r in episode],dtype=np.float64)
        p=np.clip(pp,1e-12,1.-1e-12)
        return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))

    def analytic_bptt(self,episode):
        pp,details=self.forward(episode,cache=True)
        length=len(episode)
        if pp.shape!=(length,N):
            raise ValueError("NCI04_S4C1_PREDICTION_SHAPE_DRIFT")
        dg=np.zeros_like(self.g)
        dr=np.zeros_like(self.roles)
        future=np.zeros(N,dtype=np.float64)
        for t in range(length-1,-1,-1):
            f,s,read,p,ns=details[t]
            y=np.asarray(episode[t][2],dtype=np.float64)
            # True targets only enter the retrospective TRAINING gradient.
            dz=future*(1.-ns*ns)
            du=(p-y)/(length*N)+dz*self.roles[:,2]*2.*p*(1.-p)
            dg[0]+=np.sum(du[:,None]*f,axis=0)
            dg[1]+=np.sum((du*s)[:,None]*f,axis=0)
            dg[2]+=np.sum(dz[:,None]*f,axis=0)
            dr[:,0]+=du
            dr[:,1]+=du*s
            dr[:,2]+=dz*(2.*p-1.)
            future=du*read
        if not np.all(np.isfinite(dg)) or not np.all(np.isfinite(dr)):
            raise ValueError("NCI04_S4C1_BPTT_NONFINITE")
        return dg,dr

    def source_gradient_finite_difference(self,episode,epsilon=1e-5):
        grad=self.analytic_bptt(episode)
        coordinates=((0,(0,0)),(0,(1,1)),(0,(2,3)),
                     (1,(0,0)),(1,(1,1)),(1,(2,2)))
        records=[]
        for group,index in coordinates:
            parameter=self.params()[group]
            original=float(parameter[index])
            parameter[index]=original+epsilon
            positive=self.bernoulli_ce(episode)
            parameter[index]=original-epsilon
            negative=self.bernoulli_ce(episode)
            parameter[index]=original
            numerical=(positive-negative)/(2.*epsilon)
            analytical=float(grad[group][index])
            records.append({"group":group,"at":list(index),
                            "analytic":analytical,"numeric":numerical,
                            "absolute_error":abs(analytical-numerical)})
        error=max(z["absolute_error"] for z in records)
        if not math.isfinite(error) or error>1e-5:
            raise ValueError("NCI04_S4C1_NATIVE_REAL_SOURCE_GRADIENT_INVALID")
        return {"maximum_absolute_gradient_error":error,
                "source_checked_coordinates":records,"passed":True}

    def snapshot(self):
        self._validate_params()
        # Serialize via ORIGINAL native LocalGenome receipt.
        self.native.core.genome=self.g.tolist()
        self.native.core.roles=self.roles.tolist()
        self.native.core.events=self.train_updates
        return json.dumps({
            "schema":SCHEMA,
            "original_native_runtime":json.loads(self.native.snapshot()),
            "actual_inference_scalar_state_count":8,
        },sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls,serialized):
        if type(serialized) is not str or len(serialized)>65536:
            raise ValueError("NCI04_S4C1_MODEL_SNAPSHOT_SIZE")
        o=json.loads(serialized)
        if set(o)!={"schema","original_native_runtime",
                    "actual_inference_scalar_state_count"} or (
            o["schema"]!=SCHEMA or
            o["actual_inference_scalar_state_count"]!=8):
            raise ValueError("NCI04_S4C1_MODEL_SNAPSHOT_IDENTITY")
        z=cls()
        z.native=LocalTaskRuntime.restore(json.dumps(
            o["original_native_runtime"]))
        z.g=np.array(z.native.core.genome,dtype=np.float64)
        z.roles=np.array(z.native.core.roles,dtype=np.float64)
        z.train_updates=z.native.core.events
        if z.snapshot()!=serialized:
            raise ValueError("NCI04_S4C1_NATIVE_MODEL_ROUNDTRIP_DRIFT")
        return z
