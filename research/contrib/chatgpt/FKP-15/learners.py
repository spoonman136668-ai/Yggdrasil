"""FKP-15 tokenless fixed numeric action-value weights and nonparametric controls.

Actual 16-step SOURCE rewards (nine public macro outcomes/context), never
hidden states. Frozen 4096x9 int32 sum and count, exact non-gradient writes.
"""
from __future__ import annotations
import hashlib
import struct
import numpy as np

SLOTS=4096
ACTIONS=9
DIM=204
RAW_BYTES=SLOTS*ACTIONS*4*2
MAGIC=b"FK15"
SMOOTH=16.

def context_data(rows):
    return [r for r in rows if r["valid"]]


def hash_keys(x,view):
    x=np.asarray(x,dtype=np.float32)
    if x.ndim!=2 or x.shape[1]!=DIM or not np.isfinite(x).all():
        raise ValueError("FKP15_PUBLIC_SUMMARY_SHAPE")
    if view not in (0,1):raise ValueError("FKP15_HASH_VIEW")
    rng=np.random.default_rng(1515 if view==0 else 2626)
    mat=rng.choice((-1.,1.),size=(12,DIM)).astype(np.float32)
    bits=((x-0.5)@mat.T>=0).astype(np.uint16)
    key=np.zeros(len(x),dtype=np.uint16)
    for i in range(12):key|=(bits[:,i]<<i)
    return key.astype(np.int32)


class DirectValues:
    def __init__(self,two_keys=True,shuffled=False):
        self.two_keys=bool(two_keys)
        self.shuffled=bool(shuffled)
        self.count=np.zeros((SLOTS,ACTIONS),dtype=np.int32)
        self.sum_milli=np.zeros((SLOTS,ACTIONS),dtype=np.int32)
        self.global_return=np.zeros(ACTIONS,dtype=np.float64)

    def fit(self,rows):
        rows=context_data(rows)
        if not rows:raise ValueError("FKP15_NO_TRAIN")
        x=np.stack([r["context"] for r in rows])
        y=np.stack([r["returns"] for r in rows])
        if y.shape!=(len(rows),ACTIONS) or not np.isfinite(y).all():
            raise ValueError("FKP15_TRAIN_RETURN_SHAPE")
        self.global_return=y.mean(axis=0)
        if self.shuffled:
            y=y[np.random.default_rng(1515).permutation(len(rows))]
        q=np.rint(y*1000).astype(np.int64)
        if abs(q).max()>20000:raise ValueError("FKP15_REWARD_SCALE")
        for v in ((0,1) if self.two_keys else (0,)):
            key=hash_keys(x,v)
            for i,k in enumerate(key):
                for a in range(ACTIONS):
                    if int(self.count[k,a])>=2**31-1 or abs(int(self.sum_milli[k,a])+int(q[i,a]))>=2**31-1:
                        raise ValueError("FKP15_CAPACITY_EXCEEDED")
                    self.count[k,a]+=1
                    self.sum_milli[k,a]+=int(q[i,a])
        return self

    def predict(self,contexts):
        x=np.asarray(contexts,dtype=np.float32)
        if x.ndim==1:x=x[None,:]
        if self.count.shape!=(SLOTS,ACTIONS):raise ValueError("FKP15_MEMORY_CORRUPT")
        count=self.count[hash_keys(x,0)].astype(np.float64)
        reward=self.sum_milli[hash_keys(x,0)].astype(np.float64)/1000
        if self.two_keys:
            count+=self.count[hash_keys(x,1)]
            reward+=self.sum_milli[hash_keys(x,1)].astype(np.float64)/1000
        return (reward+SMOOTH*self.global_return)/(count+SMOOTH)

    def snapshot(self):
        flags=int(self.two_keys)|(int(self.shuffled)<<1)
        data=MAGIC+struct.pack("<I",flags)
        data+=np.asarray(self.global_return,dtype="<f8").tobytes()
        data+=self.count.astype("<i4",copy=False).tobytes()
        data+=self.sum_milli.astype("<i4",copy=False).tobytes()
        return data+hashlib.sha256(data).digest()

    @classmethod
    def restore(cls,raw):
        want=4+4+9*8+RAW_BYTES+32
        if type(raw) is not bytes or len(raw)!=want or raw[:4]!=MAGIC or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]:
            raise ValueError("FKP15_COLD_TAMPER")
        flags,=struct.unpack("<I",raw[4:8])
        if flags>3:raise ValueError("FKP15_INVALID_FLAGS")
        result=cls(two_keys=bool(flags&1),shuffled=bool(flags&2))
        result.global_return=np.frombuffer(raw[8:80],dtype="<f8").copy()
        p=80
        n=SLOTS*ACTIONS*4
        result.count=np.frombuffer(raw[p:p+n],dtype="<i4").reshape(SLOTS,ACTIONS).copy()
        result.sum_milli=np.frombuffer(raw[p+n:p+2*n],dtype="<i4").reshape(SLOTS,ACTIONS).copy()
        if (result.count<0).any() or int(result.count.max())>100000 or not np.isfinite(result.global_return).all():
            raise ValueError("FKP15_SNAPSHOT_BOUNDS")
        return result


class Retrieval:
    def __init__(self,k):
        if k not in (1,5,15):raise ValueError("FKP15_K")
        self.k=k

    def fit(self,rows):
        data=context_data(rows)
        self.x=np.stack([r["context"] for r in data]).astype(np.float64)
        self.y=np.stack([r["returns"] for r in data]).astype(np.float64)
        self.center=self.x.mean(axis=0)
        self.scale=np.maximum(self.x.std(axis=0),0.05)
        self.normalized=(self.x-self.center)/self.scale
        return self

    def predict(self,x):
        x=np.atleast_2d(np.asarray(x,dtype=np.float64))
        z=(x-self.center)/self.scale
        squared=np.sum((z[:,None,:]-self.normalized[None,:,:])**2,axis=2)
        idx=np.argsort(squared,axis=1,kind="stable")[:,:self.k]
        return self.y[idx].mean(axis=1)


class Ridge:
    def __init__(self,lmbda):
        if lmbda not in (0.01,1.,100.):raise ValueError("FKP15_RIDGE_ALPHA")
        self.alpha=lmbda

    def fit(self,rows):
        data=context_data(rows)
        x=np.stack([r["context"] for r in data]).astype(np.float64)
        y=np.stack([r["returns"] for r in data]).astype(np.float64)
        self.center=x.mean(axis=0)
        self.scale=np.maximum(x.std(axis=0),0.05)
        design=np.concatenate([np.ones((len(x),1)),(x-self.center)/self.scale],axis=1)
        mat=design.T@design+self.alpha*np.diag(np.r_[0.,np.ones(DIM)])
        self.coef=np.linalg.solve(mat,design.T@y)
        return self

    def predict(self,x):
        x=np.atleast_2d(np.asarray(x,dtype=np.float64))
        return np.concatenate([np.ones((len(x),1)),(x-self.center)/self.scale],axis=1)@self.coef


def mse(p,y):
    p=np.asarray(p,dtype=np.float64)
    y=np.asarray(y,dtype=np.float64)
    if p.shape!=y.shape or p.ndim!=2 or p.shape[1]!=9:
        raise ValueError("FKP15_ALL_NINE_OUTCOMES_REQUIRED")
    return float(np.mean((p-y)**2))
