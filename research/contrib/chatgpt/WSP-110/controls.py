"""WSP110 independent exact symbolic and fully fitted conventional controls.

All three arms access the same million observed raw facts, 3000 training X/Y
feedback pairs, and unknown conditional compositional mechanism. These
controls never import hidden_x, hidden_y or the direct numeric learner.
"""
from __future__ import annotations

from collections import defaultdict
import numpy as np

N_GROUPS = 25000
L2 = 0.01
TOL = 1e-8
MAX_STEPS = 100


class SymbolicAssociationControl:
    """Independent fact-set and learned operator-count association engine."""

    def __init__(self):
        self.facts=set()
        self.pos1=defaultdict(int)
        self.n1=defaultdict(int)
        self.pos2=defaultdict(int)
        self.n2=defaultdict(int)
        self.derived_x=set()
        self.derived_y=set()

    def load_facts(self, sources, relations, targets):
        if self.facts:
            raise ValueError("cannot reload symbolic control facts")
        self.facts={(int(s),int(r),int(t)) for s,r,t in zip(
            sources,relations,targets)}
        if len(self.facts)!=1_000_000:
            raise ValueError("symbolic exact baseline requires identical million facts")

    def get_chain(self,group):
        s=4*group
        left=[i for i in range(4) if (s,i,s+1) in self.facts]
        middle=[i for i in range(4,8) if (s+1,i,s+2) in self.facts]
        right=[i for i in range(10,14) if (s+2,i,s+3) in self.facts]
        if len(left)!=1 or len(middle)!=1 or len(right)!=1:
            raise ValueError("symbolic chain not grounded in source observations")
        return left[0],middle[0],right[0]

    def observe(self, training):
        seen=set()
        for g,x,y in training:
            if g in seen or not 0<=g<3000 or y and not x:
                raise ValueError("invalid supervised symbolic evidence")
            seen.add(g)
            a,b,c=self.get_chain(g)
            k=a*4+b-4
            self.n1[k]+=1
            self.pos1[k]+=int(x)
            if x:
                self.n2[c-10]+=1
                self.pos2[c-10]+=int(y)
        if seen!=set(range(3000)) or set(self.n1)!=set(range(16)) or set(self.n2)!=set(range(4)):
            raise ValueError("symbolic support incomplete")

    def infer_first(self):
        if self.derived_x:
            raise ValueError("symbolic first round repeated")
        for g in range(N_GROUPS):
            a,b,_=self.get_chain(g)
            k=a*4+b-4
            if 2*(self.pos1[k]+1)>self.n1[k]+2:
                self.derived_x.add((4*g,4*g+2))

    def infer_second(self):
        if not self.derived_x:
            raise ValueError("second symbolic round without learned first operator")
        if self.derived_y:
            raise ValueError("symbolic second round repeated")
        for g in range(N_GROUPS):
            s=4*g
            if (s,s+2) not in self.derived_x:
                continue
            _,_,c=self.get_chain(g)
            k=c-10
            if 2*(self.pos2[k]+1)>self.n2[k]+2:
                self.derived_y.add((s,s+3))

    def predictions(self,g):
        s=4*g
        return ((s,s+2) in self.derived_x,(s,s+3) in self.derived_y)


class RegularizedLogistic:
    """Exact Newton-fit convex logistic, not tuned on heldout observations."""

    def __init__(self,n_features):
        self.n_features=n_features
        self.theta=None
        self.steps=None
        self.gradient_inf=None
        self.train_accuracy=None

    @staticmethod
    def _objective(t,X,y):
        z=X@t
        return float(np.mean(np.logaddexp(0,z))-y@z/len(y)
                     +.5*L2*(t@t))

    def fit(self,indices,outcomes):
        n=len(indices)
        if n<100:
            raise ValueError("conventional baseline requires full support cohort")
        if not all(type(i) is int and 0<=i<self.n_features for i in indices):
            raise ValueError("unknown conventional feature")
        if not all(type(y) is bool for y in outcomes):
            raise ValueError("labels must come from observed binary support")
        x=np.zeros((n,self.n_features+1),dtype=np.float64)
        x[np.arange(n),indices]=1.
        x[:,-1]=1.
        y=np.asarray(outcomes,dtype=np.float64)
        theta=np.zeros(self.n_features+1,dtype=np.float64)
        step=0
        for step in range(1,MAX_STEPS+1):
            z=x@theta
            p=1/(1+np.exp(-np.clip(z,-40,40)))
            grad=x.T@(p-y)/n + L2*theta
            resid=float(np.max(np.abs(grad)))
            if resid<=TOL:
                break
            curvature=p*(1-p)
            H=(x.T*curvature)@x/n + L2*np.eye(self.n_features+1)
            delta=np.linalg.solve(H,grad)
            slope=float(grad@delta)
            before=self._objective(theta,x,y)
            alpha=1.
            for attempt in range(40):
                proposed=theta-alpha*delta
                if self._objective(proposed,x,y)<=before-1e-4*alpha*slope:
                    theta=proposed
                    break
                alpha*=.5
            else:
                raise FloatingPointError("conventional full-data Newton Armijo failed")
        if resid>TOL:
            raise FloatingPointError("full conventional baseline not stationary")
        self.theta=theta
        self.steps=step
        self.gradient_inf=resid
        self.train_accuracy=float(np.mean((x@theta>0)==(y>0)))

    def predict(self,index):
        if self.theta is None:
            raise ValueError("untrained conventional control")
        return bool(self.theta[index]+self.theta[-1]>0)


class ConventionalOperatorControl:
    """Two fully optimized learned relation heads, same observed labels."""

    def __init__(self,symbolic_memory):
        self.facts=symbolic_memory
        self.first=RegularizedLogistic(16)
        self.second=RegularizedLogistic(4)
        self.derived_x=set()
        self.derived_y=set()

    def learn(self,feedback):
        features1,labels1=[],[]
        features2,labels2=[],[]
        for g,x,y in feedback:
            a,b,c=self.facts.get_chain(g)
            features1.append(a*4+b-4)
            labels1.append(x)
            if x:
                features2.append(c-10)
                labels2.append(y)
        self.first.fit(features1,labels1)
        self.second.fit(features2,labels2)

    def infer_first(self):
        for g in range(N_GROUPS):
            a,b,_=self.facts.get_chain(g)
            if self.first.predict(a*4+b-4):
                self.derived_x.add((4*g,4*g+2))

    def infer_second(self):
        if not self.derived_x:
            raise ValueError("conventional second round before first")
        for g in range(N_GROUPS):
            s=4*g
            if (s,s+2) not in self.derived_x:
                continue
            _,_,c=self.facts.get_chain(g)
            if self.second.predict(c-10):
                self.derived_y.add((s,s+3))

    def predictions(self,g):
        s=4*g
        return ((s,s+2) in self.derived_x,(s,s+3) in self.derived_y)
