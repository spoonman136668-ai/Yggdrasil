"""Independent active Bayesian control: same information and action budget, no oracle.

Separate coefficient/hypothesis construction from the numerical direct-writer.
Its fully enumerated 2^16 Boolean polynomial hypotheses are deliberately strong.
"""
from __future__ import annotations
import numpy as np
from core import MONOMIALS,N_QUERY

class ActiveBayes:
    def __init__(self,training_tables):
        a=np.asarray(training_tables,dtype=np.uint8)
        if a.shape!=(512,16,2):raise ValueError("requires all 512 observed training worlds")
        # Independently derive the Boolean expansion coefficients for all training worlds.
        freq=np.ones((16,2),dtype=np.float64)
        for t in a:
            for j,mask in enumerate(MONOMIALS):
                sub=mask
                ans=np.zeros(2,dtype=np.uint8)
                while True:
                    ans^=t[sub]
                    if sub==0:break
                    sub=(sub-1)&mask
                freq[j]+=ans
        p=freq/514.0
        self.coeff=((np.arange(65536,dtype=np.uint16)[:,None]
                     >>np.arange(16,dtype=np.uint16))&1).astype(np.uint8)
        x=np.arange(16,dtype=np.uint16)
        feat=np.array([[int(v&m==m) for m in MONOMIALS] for v in x],dtype=np.uint8)
        self.effects=((self.coeff@feat.T)&1).astype(np.uint8)
        self.mass=[]
        for bit in range(2):
            logp=(self.coeff@np.log(p[:,bit])+(1-self.coeff)@np.log1p(-p[:,bit]))
            self.mass.append(np.exp(logp-logp.max()))
        self.obs=[]
        self.pred=np.zeros((16,2),dtype=np.float64)
        self._refresh()

    def _refresh(self):
        for bit in range(2):
            w=self.mass[bit]
            if w.sum()<=0:raise ValueError("impossible observations")
            self.pred[:,bit]=w@self.effects/w.sum()
        for x,y in self.obs:self.pred[x]=(y&1,(y>>1)&1)

    def choose(self):
        if len(self.obs)>=N_QUERY:raise ValueError("Bayesian budget")
        used={x for x,_ in self.obs}
        p=np.clip(self.pred,1e-9,1-1e-9)
        ent=-(p*np.log2(p)+(1-p)*np.log2(1-p)).sum(axis=1)
        return max((x for x in range(16) if x not in used),
                   key=lambda x:(float(ent[x]),-x))

    def observe(self,x,y):
        if type(x)!=int or type(y)!=int or not 0<=x<16 or not 0<=y<4:
            raise ValueError("bad Bayesian intervention")
        if len(self.obs)>=N_QUERY or x in {a for a,_ in self.obs}:
            raise ValueError("duplicate/over-budget Bayesian intervention")
        for bit in range(2):
            self.mass[bit]*=(self.effects[:,x]==((y>>bit)&1))
        self.obs.append((x,y))
        self._refresh()

    def predict(self,x):
        return int(self.pred[x,0]>=0.5)+2*int(self.pred[x,1]>=0.5)
