"""WSP67 independent fully trainable conventional neural baseline, CPU-only.

An actual 8->24 ReLU->4 sigmoid MLP with ordinary SGD/backpropagation.
Same 96 charged public transitions as the direct writer, independent seeded
random initialization and 8k capped updates with training-side stop after
2k if >=98% full exact observed transition accuracy. No source data access.
This baseline is declared INCOMPLETE if it does not converge; underfitting
is never evidence that direct programming beats conventional training.
"""
from __future__ import annotations
from hashlib import sha256
from math import exp,isfinite,log
from random import Random

INPUTS=8
HIDDEN=24
OUTPUTS=4
MIN_STEPS=2000
MAX_STEPS=8000
RATE=0.045


def _seed_bytes(seed,kind):
    return sha256(f"WSP67|conventional-SGD|{seed}|{kind}".encode("ascii")).digest()


def _sigmoid(x):
    return (1.0/(1.0+exp(-x))) if x>=0 else (exp(x)/(1.0+exp(x)))


def _input(state,action):
    if type(state) is not tuple or len(state)!=4 or (
            type(action) is not int or action not in range(4)):
        raise ValueError("invalid public state/action")
    return list(map(float,state))+[float(action==i) for i in range(4)]


class ConventionalMLP:
    def __init__(self,seed):
        if type(seed) is not int:
            raise ValueError("invalid train seed")
        self.seed=seed
        r=Random(int.from_bytes(_seed_bytes(seed,"weights"),"big"))
        self.w1=[[r.uniform(-0.22,0.22) for _ in range(INPUTS)]
                 for _ in range(HIDDEN)]
        self.b1=[0.03]*HIDDEN
        self.w2=[[r.uniform(-0.22,0.22) for _ in range(HIDDEN)]
                 for _ in range(OUTPUTS)]
        self.b2=[0.0]*OUTPUTS
        self.updates=0
        self.train_exact=0.0

    def _forward(self,state,action):
        x=_input(state,action)
        z1=[sum(w*v for w,v in zip(row,x))+bias
            for row,bias in zip(self.w1,self.b1)]
        h=[max(0.0,z) for z in z1]
        logits=[sum(w*v for w,v in zip(row,h))+bias
                for row,bias in zip(self.w2,self.b2)]
        return x,z1,h,tuple(_sigmoid(z) for z in logits)

    def predict(self,state,action,confidence=False):
        p=self._forward(state,action)[-1]
        if confidence and any(min(x,1-x)>0.1 for x in p):
            return None
        return tuple(int(x>=0.5) for x in p)

    def parameter_count(self):
        return HIDDEN*(INPUTS+1)+OUTPUTS*(HIDDEN+1)

    def _update(self,before,action,after):
        x,z,h,p=self._forward(before,action)
        dz=[(p[j]-after[j])/OUTPUTS for j in range(OUTPUTS)]
        dh=[sum(dz[j]*self.w2[j][i] for j in range(OUTPUTS))
            if z[i]>0 else 0.0 for i in range(HIDDEN)]
        for j in range(OUTPUTS):
            d=dz[j]
            for i in range(HIDDEN):
                self.w2[j][i]-=RATE*d*h[i]
            self.b2[j]-=RATE*d
        for i in range(HIDDEN):
            d=dh[i]
            if d==0.0:
                continue
            for k in range(INPUTS):
                self.w1[i][k]-=RATE*d*x[k]
            self.b1[i]-=RATE*d
        self.updates+=1

    def _train_accuracy(self,rows):
        correct=sum(self.predict(b,a)==y for b,a,y in rows)
        return correct/len(rows)

    def fit(self,rows):
        if not rows or any(len(b)!=4 or len(y)!=4
                           for b,a,y in rows):
            raise ValueError("bad public charged evidence")
        r=Random(int.from_bytes(_seed_bytes(self.seed,"shuffle"),"big"))
        for _ in range(MAX_STEPS):
            b,a,y=rows[r.randrange(len(rows))]
            self._update(b,a,y)
            if self.updates>=MIN_STEPS and self.updates%400==0:
                self.train_exact=self._train_accuracy(rows)
                if self.train_exact>=0.98:
                    break
        self.train_exact=self._train_accuracy(rows)
        if any(not isfinite(v) for arr in (self.b1,self.b2)
               for v in arr):
            raise ArithmeticError("SGD nonfinite bias")
        return {"gradient_updates":self.updates,
                "train_exact_accuracy":round(self.train_exact,8),
                "fully_trained":self.train_exact>=0.98,
                "parameters":self.parameter_count()}
