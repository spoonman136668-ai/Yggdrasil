"""Independent symbolic and fully trained neural controls for public WSP-08 DEV.

These controls MAY use Python state dictionaries. The direct weight circuit
never imports them; they exist solely to prevent a strawman comparison.
"""
from __future__ import annotations

import math
import random

from graph import N, validate_state, validate_bit


class SymbolicAdaptive:
    """Exact minimal causal-observation prefix compatible with public labels."""
    def __init__(self, max_depth:int=3):
        if type(max_depth) is not int or max_depth not in (1,2,3):
            raise ValueError("WSP08_SYMBOLIC_DEPTH_INVALID")
        self.max_depth=max_depth
        self.transitions:dict[int,tuple[int,int]]={}
        self.labels:dict[int,int]={}
        self.fault=False

    def observe(self,state:int,action:int,reward:int,successor:int)->None:
        validate_state(state)
        validate_state(successor)
        validate_bit(action,"ACTION")
        validate_bit(reward,"REWARD")
        target=self.transitions if action==0 else self.labels
        if action==0:
            entry=(reward,successor)
            if state in target and target[state]!=entry:
                self.fault=True
            target[state]=entry
        else:
            if state in target and target[state]!=reward:
                self.fault=True
            target[state]=reward

    def signature(self,state:int,depth:int=3)->tuple[int,...]|None:
        validate_state(state)
        if not 1<=depth<=3:
            raise ValueError("WSP08_SIGNATURE_DEPTH_INVALID")
        out=[]
        for _ in range(depth):
            if state not in self.transitions:
                return None
            reward,next_state=self.transitions[state]
            out.append(reward)
            state=next_state
        return tuple(out)

    def active_depth(self)->int|None:
        if self.fault:
            return None
        for depth in range(1,self.max_depth+1):
            groups:dict[tuple[int,...],set[int]]={}
            for s,reward in self.labels.items():
                key=self.signature(s,depth)
                if key is None:
                    return None
                groups.setdefault(key,set()).add(reward)
            if all(len(labels)==1 for labels in groups.values()):
                return depth
        return None

    def predict_a1(self,state:int)->int|None:
        depth=self.active_depth()
        if depth is None:
            return None
        key=self.signature(state,depth)
        if key is None:
            return None
        found={reward for s,reward in self.labels.items()
               if self.signature(s,depth)==key}
        return next(iter(found)) if len(found)==1 else None


class TrainedMLP:
    """3 input, 8 tanh hidden, 1 sigmoid; 41 parameters; full-batch Adam."""
    SEED=17
    HIDDEN=8
    PARAMETERS=41
    LEARNING_RATE=0.03
    MAX_STEPS=2048
    STOP_BCE=0.02

    def __init__(self):
        rng=random.Random(self.SEED)
        self.w=[[rng.uniform(-0.5,0.5) for _ in range(3)]
                for _ in range(self.HIDDEN)]
        self.b=[0.0]*self.HIDDEN
        self.v=[rng.uniform(-0.5,0.5) for _ in range(self.HIDDEN)]
        self.bias=0.0
        self.steps=0
        self.loss:float|None=None
        self.converged=False

    def _flat(self)->list[float]:
        return [v for row in self.w for v in row]+self.b+self.v+[self.bias]

    def _load(self,theta:list[float])->None:
        if len(theta)!=self.PARAMETERS:
            raise ValueError("WSP08_MLP_PARAM_INVALID")
        self.w=[theta[3*i:3*i+3] for i in range(8)]
        self.b=theta[24:32]
        self.v=theta[32:40]
        self.bias=theta[40]

    def _forward(self,x:tuple[int,int,int])->tuple[list[float],float]:
        if type(x) is not tuple or len(x)!=3:
            raise ValueError("WSP08_MLP_INPUT_SHAPE")
        for k in x:
            validate_bit(k,"MLP_INPUT")
        h=[math.tanh(sum(row[i]*x[i] for i in range(3))+bias)
           for row,bias in zip(self.w,self.b)]
        score=max(-40.0,min(40.0,sum(v*z for v,z in zip(self.v,h))+self.bias))
        return h,1/(1+math.exp(-score))

    def fit(self,examples:tuple[tuple[tuple[int,int,int],int],...])->None:
        if type(examples) is not tuple or len(examples)!=16:
            raise ValueError("WSP08_MLP_TRAINING_BUDGET")
        for x,y in examples:
            if type(x) is not tuple or len(x)!=3:
                raise ValueError("WSP08_MLP_TRAINING_FEATURE")
            for v in x:
                validate_bit(v,"FEATURE")
            validate_bit(y,"TRAINING_TARGET")
        theta=self._flat()
        m=[0.0]*len(theta)
        v=[0.0]*len(theta)
        n=len(examples)
        for epoch in range(1,self.MAX_STEPS+1):
            grad=[0.0]*len(theta)
            loss=0.0
            for x,y in examples:
                h,p=self._forward(x)
                p=max(1e-12,min(1-1e-12,p))
                loss+=(-y*math.log(p)-(1-y)*math.log(1-p))/n
                err=(p-y)/n
                grad[40]+=err
                for j in range(8):
                    grad[32+j]+=err*h[j]
                    back=err*self.v[j]*(1-h[j]*h[j])
                    grad[24+j]+=back
                    for k in range(3):
                        grad[3*j+k]+=back*x[k]
            self.loss=loss
            self.steps=epoch-1
            if loss<=self.STOP_BCE:
                self.converged=True
                break
            for i,g in enumerate(grad):
                m[i]=0.9*m[i]+0.1*g
                v[i]=0.999*v[i]+0.001*g*g
                mean=m[i]/(1-0.9**epoch)
                var=v[i]/(1-0.999**epoch)
                theta[i]-=self.LEARNING_RATE*mean/(math.sqrt(var)+1e-8)
            self._load(theta)
            self.steps=epoch
        if not self.converged:
            self.loss=sum(
                -(y*math.log(max(1e-12,self._forward(x)[1]))+
                  (1-y)*math.log(max(1e-12,1-self._forward(x)[1])))/n
                for x,y in examples)
            self.converged=self.loss<=self.STOP_BCE

    def predict(self,x:tuple[int,int,int])->int:
        return int(self._forward(x)[1]>=0.5)
