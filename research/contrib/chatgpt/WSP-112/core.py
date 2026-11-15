"""WSP112 observed causal effects, active interventions and numeric memory.

No model module imports the hidden evaluator. Controlled action input x=(state<<2)|action.
"""
from __future__ import annotations
from hashlib import sha256
import numpy as np

N_QUERY=8
MONOMIALS=tuple(sorted(range(16),key=lambda m:(m.bit_count(),m)))
FEATURES=np.asarray([[int(x&m==m) for m in MONOMIALS] for x in range(16)],dtype=np.uint8)
COEFF=np.asarray([(np.arange(65536,dtype=np.uint16)>>j)&1 for j in range(16)],dtype=np.uint8).T
TRUTH=((COEFF@FEATURES.T)&1).astype(np.uint8)

def invert_truth(table):
    """GF(2) Moebius inversion on the entirely observed public training world."""
    a=np.asarray(table,dtype=np.uint8)
    if a.shape!=(16,2) or np.any(a>1):raise ValueError("expected 16x2 observed bits")
    result=np.zeros((16,2),dtype=np.uint8)
    for j,mask in enumerate(MONOMIALS):
        v=np.zeros(2,dtype=np.uint8)
        sub=mask
        while True:
            v^=a[sub]
            if sub==0:break
            sub=(sub-1)&mask
        result[j]=v
    return result

def prior_from_full_training(tables):
    arr=np.asarray(tables,dtype=np.uint8)
    if arr.ndim!=3 or arr.shape[1:]!=(16,2) or not len(arr) or np.any(arr>1):
        raise ValueError("training requires observed full 16x2 worlds")
    count=np.zeros((16,2),dtype=np.float64)
    for table in arr:count+=invert_truth(table)
    return (count+1)/(len(arr)+2)

class DirectWriter:
    """Adapt by direct-writing numerical operator coefficients and effect weights.

    A generic numerical parity hypothesis filter programs the reusable native
    weights. Prediction reads numeric_effect_weights, never hidden generator code.
    """
    def __init__(self,prior):
        p=np.asarray(prior,dtype=np.float64)
        if p.shape!=(16,2) or np.any(p<=0) or np.any(p>=1):
            raise ValueError("invalid training-derived prior")
        self.prior=p.copy()
        log_p=np.log(p);log_q=np.log1p(-p)
        self.base_log=np.asarray([COEFF@log_p[:,b]+(1-COEFF)@log_q[:,b]
                                  for b in range(2)],dtype=np.float64)
        self.hyp=np.exp(self.base_log-self.base_log.max(axis=1,keepdims=True))
        self.observations=[]
        self.synapses=np.zeros((16,2),dtype=np.float32)
        self.numeric_effect_weights=np.zeros((16,2),dtype=np.float32)
        self._rewrite()

    def _rewrite(self):
        for b in range(2):
            w=self.hyp[b];den=w.sum(dtype=np.float64)
            if den<=0:raise ValueError("inconsistent causal observations")
            self.numeric_effect_weights[:,b]=(w@TRUTH/den).astype(np.float32)
            self.synapses[:,b]=(w@COEFF/den).astype(np.float32)
        for x,y in self.observations:
            self.numeric_effect_weights[x]=(y&1,(y>>1)&1)

    def choose(self):
        used={x for x,_ in self.observations}
        if len(used)>=N_QUERY:raise ValueError("intervention budget exhausted")
        p=np.clip(self.numeric_effect_weights.astype(np.float64),1e-9,1-1e-9)
        h=-(p*np.log2(p)+(1-p)*np.log2(1-p)).sum(axis=1)
        return max((x for x in range(16) if x not in used),
                   key=lambda x:(float(h[x]),-x))

    def observe(self,x,y):
        if type(x)!=int or type(y)!=int or not 0<=x<16 or not 0<=y<4:
            raise ValueError("invalid causal consequence")
        if len(self.observations)>=N_QUERY or x in {i for i,_ in self.observations}:
            raise ValueError("duplicate or over-budget intervention")
        for b in range(2):self.hyp[b]*=(TRUTH[:,x]==((y>>b)&1))
        self.observations.append((x,y))
        self._rewrite()

    def predict(self,x):
        if not 0<=x<16:raise ValueError("input out of range")
        p=self.numeric_effect_weights[x]
        return int(p[0]>=0.5)+2*int(p[1]>=0.5)

    def checkpoint(self):
        import json
        blocks={"prior":self.prior.tobytes().hex(),
                "obs":[list(p) for p in self.observations],
                "effects":self.numeric_effect_weights.tobytes().hex(),
                "synapses":self.synapses.tobytes().hex()}
        seal=sha256(json.dumps(blocks,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        return {"schema":"wsp112.numeric-causal-memory.v1","blocks":blocks,"sha256":seal}

    @classmethod
    def restore(cls,snapshot):
        import json
        if snapshot.get("schema")!="wsp112.numeric-causal-memory.v1":
            raise ValueError("bad memory schema")
        blocks=snapshot["blocks"]
        seal=sha256(json.dumps(blocks,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if snapshot.get("sha256")!=seal:raise ValueError("tampered causal memory")
        obj=cls(np.frombuffer(bytes.fromhex(blocks["prior"]),dtype=np.float64).reshape(16,2))
        for x,y in blocks["obs"]:obj.observe(x,y)
        if (obj.numeric_effect_weights.tobytes().hex()!=blocks["effects"] or
            obj.synapses.tobytes().hex()!=blocks["synapses"]):
            raise ValueError("invalid numeric replay")
        return obj

class SymbolicGF2:
    """Independent exact Boolean elimination; free coefficients are zero."""
    def __init__(self):self.obs=[]

    @staticmethod
    def _solve(observations,bit):
        rows=[]
        for x,y in observations:
            bits=sum(int(x&m==m)<<j for j,m in enumerate(MONOMIALS))
            rows.append([bits,(y>>bit)&1])
        pivots=[];rank=0
        for col in range(16):
            idx=next((i for i in range(rank,len(rows)) if rows[i][0]&(1<<col)),None)
            if idx is None:continue
            rows[rank],rows[idx]=rows[idx],rows[rank]
            for i in range(len(rows)):
                if i!=rank and rows[i][0]&(1<<col):
                    rows[i][0]^=rows[rank][0];rows[i][1]^=rows[rank][1]
            pivots.append(col);rank+=1
        result=0
        for row,col in reversed(list(zip(rows,pivots))):
            val=row[1]^((row[0]&result).bit_count()&1)
            result|=val<<col
        return result,rank

    def choose(self):
        if len(self.obs)>=N_QUERY:raise ValueError("symbolic budget")
        used={x for x,_ in self.obs}
        equations=[sum(int(x&m==m)<<j for j,m in enumerate(MONOMIALS))
                   for x,_ in self.obs]
        def rank(values):
            basis={}
            for v in values:
                while v:
                    j=v.bit_length()-1
                    if j in basis:v^=basis[j]
                    else:basis[j]=v;break
            return len(basis)
        base=rank(equations)
        return max((x for x in range(16) if x not in used),
                   key=lambda x:(rank(equations+
                           [sum(int(x&m==m)<<j for j,m in enumerate(MONOMIALS))])-base,-x))

    def observe(self,x,y):
        if len(self.obs)>=N_QUERY or x in {a for a,_ in self.obs} or not(0<=x<16 and 0<=y<4):
            raise ValueError("invalid symbolic feedback")
        self.obs.append((x,y))

    def predict(self,x):
        values=[]
        for b in range(2):
            coef,_=self._solve(self.obs,b)
            v=0
            for j,m in enumerate(MONOMIALS):
                v^=((coef>>j)&1)*int(x&m==m)
            values.append(v)
        return values[0]+2*values[1]

class ConventionalGP:
    """Fully trained conventional nonlinear GP, exactly conditioned per world.

    All hyperparameters frozen: covariance from public training, ridge 1e-5.
    """
    def __init__(self,full_training_tables):
        data=np.asarray(full_training_tables,dtype=np.float64)
        if data.ndim!=3 or data.shape[1:]!=(16,2):raise ValueError("GP training shape")
        self.mean=data.mean(axis=0)
        self.cov=np.stack([np.cov(data[:,:,b].T)+np.eye(16)*1e-5 for b in range(2)])
        self.obs=[]
        self.predictive=self.mean.copy()
        self.variances=np.stack([np.diag(c).copy() for c in self.cov],axis=1)

    def _condition(self):
        idx=[x for x,_ in self.obs]
        if not idx:return
        labels=np.asarray([[(y>>b)&1 for b in range(2)] for _,y in self.obs],dtype=np.float64)
        for b in range(2):
            c=self.cov[b]
            gram=c[np.ix_(idx,idx)]
            inv=np.linalg.solve(gram,c[idx,:])
            self.predictive[:,b]=self.mean[:,b]+(labels[:,b]-self.mean[idx,b])@inv
            self.variances[:,b]=np.maximum(0,np.diag(c)-(c[:,idx]*inv.T).sum(axis=1))
        for x,y in self.obs:self.predictive[x]=(y&1,(y>>1)&1)

    def choose(self):
        if len(self.obs)>=N_QUERY:raise ValueError("GP budget")
        used={x for x,_ in self.obs}
        return max((x for x in range(16) if x not in used),
                   key=lambda x:(float(self.variances[x].sum()),-x))

    def observe(self,x,y):
        if len(self.obs)>=N_QUERY or x in {a for a,_ in self.obs} or not(0<=x<16 and 0<=y<4):
            raise ValueError("invalid GP feedback")
        self.obs.append((x,y))
        self._condition()

    def predict(self,x):
        return int(self.predictive[x,0]>=0.5)+2*int(self.predictive[x,1]>=0.5)
