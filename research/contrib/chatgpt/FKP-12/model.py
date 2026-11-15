"""FKP-12 native-style direct numeric causal association weights.

Bounded integer 4096×3 learned weights, two frozen public visual/action hashes.
Learning is direct numerical association writes, without gradient descent.
This is independent contributor evidence, not the accepted Yggdrasil model.
"""
from __future__ import annotations

import hashlib
import struct

import numpy as np

FEATURES=204
BUCKETS=4096
CLASSES=3
RAW_BYTES=BUCKETS*CLASSES*4
MAGIC=b"FK12"
SNAPSHOT_BYTES=len(MAGIC)+RAW_BYTES+32

def validate(x):
    z=np.asarray(x)
    if z.ndim!=2 or z.shape[1]!=FEATURES or not np.issubdtype(z.dtype,np.floating):
        raise ValueError("FKP12_PUBLIC_FEATURE_SHAPE")
    if not np.isfinite(z).all() or np.any(z[:,:192]<0) or np.any(z[:,:192]>1):
        raise ValueError("FKP12_UNSAFE_FEATURE")
    return z.astype(np.float32,copy=False)

def indices(x,view:int=0,ignore_action:bool=False):
    """Stable, label-free, source-blind random 12-bit visual projections."""
    x=validate(x)
    if view not in (0,1):raise ValueError("FKP12_HASH_VIEW")
    rng=np.random.default_rng(1212+view)
    # 12 projections, 192 visible RGB features. Center before projection.
    p=rng.choice((-1.,1.),size=(12,192)).astype(np.float32)
    z=(x[:,:192]-0.5)@p.T
    bits=(z>=0).astype(np.uint16)
    code=np.zeros(len(x),dtype=np.uint16)
    for b in range(12):code|=(bits[:,b]<<b)
    action=(np.argmax(x[:,192:201],axis=1)).astype(np.uint32)
    previous=(np.argmax(x[:,201:204],axis=1)).astype(np.uint32)
    if ignore_action:action[:]=0
    # Reversible splitmix-like label-free bucket mixing; each learned
    # coefficient remains in the same bounded matrix across world histories.
    k=(code.astype(np.uint32)*np.uint32(2246822519)
       +action*np.uint32(3266489917)
       +previous*np.uint32(668265263)
       +np.uint32((view+1)*374761393))
    k^=(k>>16)
    return (k%np.uint32(BUCKETS)).astype(np.int32)


class DirectMemory:
    def __init__(self,*,two_hash:bool=True,ignore_action:bool=False):
        self.weights=np.zeros((BUCKETS,CLASSES),dtype=np.int32)
        self.two_hash=two_hash
        self.ignore_action=ignore_action

    def fit(self,episodes,*,shuffle_labels:bool=False):
        samples=[(validate(e["x"]),np.asarray(e["y"])) for e in episodes]
        if not samples:raise ValueError("FKP12_NO_REAL_SOURCE_HISTORY")
        y=np.concatenate([labels for _,labels in samples])
        if y.dtype.kind not in ("i","u") or np.any(y<0) or np.any(y>=CLASSES):
            raise ValueError("FKP12_INVALID_SOURCE_CONSEQUENCE")
        if shuffle_labels:y=np.random.default_rng(1212).permutation(y)
        off=0
        for x,labels in samples:
            yi=y[off:off+len(labels)]
            if len(x)!=len(yi):raise ValueError("FKP12_MISMATCHED_OBSERVATION_ACTIONS")
            keys0=indices(x,0,self.ignore_action)
            np.add.at(self.weights,(keys0,yi),1)
            if self.two_hash:
                keys1=indices(x,1,self.ignore_action)
                np.add.at(self.weights,(keys1,yi),1)
            off+=len(yi)
        if (self.weights<0).any() or int(self.weights.max())>=2**31-1:
            raise ValueError("FKP12_NUMERIC_CAPACITY_OVERFLOW")
        return self

    def predict(self,x):
        x=validate(x)
        k0=indices(x,0,self.ignore_action)
        evidence=self.weights[k0].astype(np.float64)
        if self.two_hash:
            evidence+=self.weights[indices(x,1,self.ignore_action)]
        # Equal-data global prior and prespecified Dirichlet smoothing.
        tally=self.weights.sum(axis=0,dtype=np.int64).astype(np.float64)
        prior=(tally+1)/(tally.sum()+3)
        scores=evidence+12.*prior
        return (scores/scores.sum(axis=1,keepdims=True)).astype(np.float64)

    def snapshot(self):
        if self.weights.dtype!=np.int32 or self.weights.shape!=(BUCKETS,CLASSES):
            raise ValueError("FKP12_SCHEMA")
        if (self.weights<0).any():
            raise ValueError("FKP12_WEIGHTS_NEGATIVE")
        # 4-byte mode bitfield stored separately so integrity binds policy.
        flags=int(self.two_hash)|(int(self.ignore_action)<<1)
        data=MAGIC+struct.pack(">I",flags)+self.weights.astype("<i4",copy=False).tobytes()
        return data+hashlib.sha256(data).digest()

    @classmethod
    def restore(cls,snapshot:bytes):
        if type(snapshot)!=bytes or len(snapshot)!=len(MAGIC)+4+RAW_BYTES+32 or snapshot[:4]!=MAGIC or hashlib.sha256(snapshot[:-32]).digest()!=snapshot[-32:]:
            raise ValueError("FKP12_COLD_TAMPER")
        flags,=struct.unpack(">I",snapshot[4:8])
        if flags>3:raise ValueError("FKP12_BAD_FLAGS")
        m=cls(two_hash=bool(flags&1),ignore_action=bool(flags&2))
        m.weights=np.frombuffer(snapshot[8:-32],dtype="<i4").astype(np.int32,copy=True).reshape(BUCKETS,CLASSES)
        if (m.weights<0).any() or int(m.weights.max())>16384:
            raise ValueError("FKP12_UNTRUSTED_COUNTERS")
        return m


def prior_probs(episodes):
    y=np.concatenate([np.asarray(e["y"],dtype=np.int64) for e in episodes])
    if not len(y):raise ValueError("FKP12_NO_PRIOR_SOURCE")
    counts=np.bincount(y,minlength=CLASSES).astype(np.float64)
    return (counts+1)/(len(y)+CLASSES)


def brier(prob,y):
    y=np.asarray(y,dtype=np.int64)
    p=np.asarray(prob,dtype=np.float64)
    if p.shape!=(len(y),CLASSES) or not np.isfinite(p).all() or not np.allclose(p.sum(axis=1),1,atol=1e-5):
        raise ValueError("FKP12_PROBABILITY_INVALID")
    target=np.eye(CLASSES,dtype=np.float64)[y]
    return float(np.mean(np.sum((p-target)**2,axis=1)))


def logloss(prob,y):
    p=np.asarray(prob,dtype=np.float64)
    y=np.asarray(y,dtype=np.int64)
    return float(np.mean(-np.log(np.clip(p[np.arange(len(y)),y],1e-12,1.))))
