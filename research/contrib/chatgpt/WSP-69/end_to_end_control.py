"""Independent fully trainable end-to-end neural MLP baseline for WSP69.

Eight binary inputs -> 32 learned ReLU hidden units -> 4 learned sigmoid
sensor outputs. ALL input-to-hidden and hidden-to-output weights/biases train
through ordinary chain-rule backpropagation with Adam on only the 96 charged
public state/action/consequence examples. Three independent fixed seeds,
up to 6000 updates/restart; training-side >=95% exact accuracy required
to label the neural control CONVERGED, otherwise mark INCOMPLETE.
Never use hidden physics, heldout/source labels or direct-writer code.
"""
from __future__ import annotations
from hashlib import sha256
from math import exp,isfinite
from random import Random

INPUTS=8
HIDDEN=32
OUTPUTS=4
RESTARTS=3
MAX_STEPS=6000
MIN_STEPS=500
BATCH_SIZE=24
LR=0.015


def _sigmoid(z):
    if z>=0:
        return 1.0/(1.0+exp(-z))
    e=exp(z)
    return e/(1.0+e)


def _inputs(s,a):
    if type(s) is not tuple or len(s)!=4 or (
            type(a) is not int or a not in range(4)):
        raise ValueError("invalid public input")
    return tuple(float(v) for v in s)+tuple(
        float(i==a) for i in range(4))


class _MLP:
    def __init__(self,seed):
        rng=Random(seed)
        self.w1=[[rng.uniform(-0.5,0.5) for _ in range(INPUTS)]
                 for _ in range(HIDDEN)]
        self.b1=[0.025]*HIDDEN
        self.w2=[[rng.uniform(-0.25,0.25) for _ in range(HIDDEN)]
                 for _ in range(OUTPUTS)]
        self.b2=[0.0]*OUTPUTS

    def probability(self,s,a):
        x=_inputs(s,a)
        h=[max(0.0,sum(w*z for w,z in zip(row,x))+bias)
           for row,bias in zip(self.w1,self.b1)]
        logits=[sum(w*z for w,z in zip(row,h))+b
                for row,b in zip(self.w2,self.b2)]
        return tuple(_sigmoid(z) for z in logits)

    def predict(self,s,a,confidence=False):
        probs=self.probability(s,a)
        if confidence and any(min(p,1-p)>0.10 for p in probs):
            return None
        return tuple(int(p>=0.5) for p in probs)


class EndToEndAdamControl:
    def __init__(self,seed):
        if type(seed) is not int:
            raise ValueError("invalid baseline seed")
        self.seed=seed
        self.winner=None
        self.training_trials=[]
        self.fully_trained=False

    @staticmethod
    def _adam(vec,grad,m,v,step,lr):
        import math
        b1=0.9
        b2=0.999
        correction1=1-b1**step
        correction2=1-b2**step
        for i in range(len(vec)):
            g=grad[i]
            m[i]=b1*m[i]+(1-b1)*g
            v[i]=b2*v[i]+(1-b2)*g*g
            vec[i]-=lr*(m[i]/correction1)/(
                math.sqrt(v[i]/correction2)+1e-8)

    def _train(self,seed,ledger):
        net=_MLP(seed)
        rng=Random(seed ^ 0xB69E207)
        m1=[[0.0]*INPUTS for _ in range(HIDDEN)]
        v1=[[0.0]*INPUTS for _ in range(HIDDEN)]
        mb1=[0.0]*HIDDEN
        vb1=[0.0]*HIDDEN
        m2=[[0.0]*HIDDEN for _ in range(OUTPUTS)]
        v2=[[0.0]*HIDDEN for _ in range(OUTPUTS)]
        mb2=[0.0]*OUTPUTS
        vb2=[0.0]*OUTPUTS
        charged=[(_inputs(s,a),tuple(float(x) for x in y))
                 for s,a,y in ledger]
        train_exact=0.0
        step=0
        for step in range(1,MAX_STEPS+1):
            gw1=[[0.0]*INPUTS for _ in range(HIDDEN)]
            gb1=[0.0]*HIDDEN
            gw2=[[0.0]*HIDDEN for _ in range(OUTPUTS)]
            gb2=[0.0]*OUTPUTS
            for _ in range(BATCH_SIZE):
                x,y=charged[rng.randrange(len(charged))]
                z1=[sum(w[i]*x[i] for i in range(INPUTS))+b
                    for w,b in zip(net.w1,net.b1)]
                h=[max(0.0,z) for z in z1]
                out=[_sigmoid(sum(w[i]*h[i] for i in range(HIDDEN))+b)
                     for w,b in zip(net.w2,net.b2)]
                d2=[(out[i]-y[i])/(OUTPUTS*BATCH_SIZE)
                    for i in range(OUTPUTS)]
                # Accumulate dE/d(hidden) BEFORE updating output weights.
                for i in range(HIDDEN):
                    if z1[i]<=0:
                        continue
                    d1=sum(d2[j]*net.w2[j][i] for j in range(OUTPUTS))
                    gb1[i]+=d1
                    for k in range(INPUTS):
                        gw1[i][k]+=d1*x[k]
                for j in range(OUTPUTS):
                    gb2[j]+=d2[j]
                    for i in range(HIDDEN):
                        gw2[j][i]+=d2[j]*h[i]
            for i in range(HIDDEN):
                self._adam(net.w1[i],gw1[i],m1[i],v1[i],step,LR)
            self._adam(net.b1,gb1,mb1,vb1,step,LR)
            for j in range(OUTPUTS):
                self._adam(net.w2[j],gw2[j],m2[j],v2[j],step,LR)
            self._adam(net.b2,gb2,mb2,vb2,step,LR)
            if step>=MIN_STEPS and step%200==0:
                train_exact=sum(net.predict(s,a)==y for s,a,y in ledger)/len(ledger)
                if train_exact>=0.95:
                    break
        train_exact=sum(net.predict(s,a)==y for s,a,y in ledger)/len(ledger)
        if not all(isfinite(x) for row in (net.w1+net.w2) for x in row):
            raise ArithmeticError("Adam produced nonfinite weights")
        return net,train_exact,step

    def fit(self,ledger):
        if (not ledger or len(ledger)>96 or any(
                type(b) is not tuple or len(b)!=4 or
                type(y) is not tuple or len(y)!=4
                for b,a,y in ledger)):
            raise ValueError("invalid charged model training rows")
        contenders=[]
        for trial in range(RESTARTS):
            seed=int.from_bytes(sha256(
                f"WSP69|Adam-end-to-end|{self.seed}|{trial}".encode("ascii")
            ).digest(),"big")
            net,train,steps=self._train(seed,ledger)
            self.training_trials.append({
                "restart":trial,"train_exact":train,
                "gradient_updates":steps,"converged":train>=0.95
            })
            contenders.append((train,-steps,-trial,net))
        best=max(contenders,key=lambda x:x[:3])
        self.winner=best[3]
        self.fully_trained=best[0]>=0.95
        return {"fully_trained":self.fully_trained,
                "best_train_exact":best[0],
                "gradient_updates_total":sum(t["gradient_updates"]
                                             for t in self.training_trials),
                "trials":self.training_trials,
                "architecture":"8->32 ReLU->4 sigmoid, trained all weights"}

    def predict(self,s,a,confidence=False):
        if self.winner is None:
            raise ValueError("train neural control first")
        return self.winner.predict(s,a,confidence=confidence)
