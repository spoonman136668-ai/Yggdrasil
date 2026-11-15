"""Independent controls for WSP113. No import of numerical native solver or oracle."""
from __future__ import annotations
from collections import Counter
from math import exp,log2
EDGES=((0,1),(0,2),(1,2),(0,3),(1,3),(2,3))
SUPPORT=tuple((s,a) for s in range(8) for a in range(8))
BUDGET=8

def independent_effect(state,action,mask):
    values=[(state>>j)&1 for j in range(4)]
    target=action//2
    for j in range(4):
        if j==target:values[j]=action&1
        else:
            acc=values[j]
            for k,(i,t) in enumerate(EDGES):
                if t==j and (mask>>k)&1:acc ^= values[i]
            values[j]=acc
    return sum(v<<j for j,v in enumerate(values))

class ExactBayesianGraph:
    """Exact strong causal control over all 64 graph structures."""
    def __init__(self):
        self.hypotheses=list(range(64))
        self.obs=[]
    def choose(self):
        if len(self.obs)>=BUDGET:raise ValueError("Bayes intervention budget")
        used={(s,a) for s,a,_ in self.obs}
        def entropy(candidate):
            count=Counter(independent_effect(*candidate,m) for m in self.hypotheses)
            n=len(self.hypotheses)
            return -sum((v/n)*log2(v/n) for v in count.values())
        return max((q for q in SUPPORT if q not in used),
                   key=lambda q:(entropy(q),-q[0],-q[1]))
    def observe(self,s,a,y):
        if len(self.obs)>=BUDGET or (s,a) in {(x,z) for x,z,_ in self.obs}:
            raise ValueError("Bayes duplicate/budget")
        if (s,a) not in SUPPORT or type(y)!=int or not 0<=y<16:
            raise ValueError("Bayes bad feedback")
        self.hypotheses=[m for m in self.hypotheses if independent_effect(s,a,m)==y]
        if not self.hypotheses:raise ValueError("inconsistent causal hypothesis")
        self.obs.append((s,a,y))
    def predict(self,s,a):
        count=Counter(independent_effect(s,a,m) for m in self.hypotheses)
        return min(count,key=lambda y:(-count[y],y))
    def triple(self,state,actions):
        states=[]
        for action in actions:
            state=self.predict(state,action)
            states.append(state)
        return tuple(states)

class IndependentSymbolicGraph:
    """Separate incremental GF(2) causal constraint learner."""
    def __init__(self):self.observations=[]
    @staticmethod
    def _reduce(rows,variables):
        pivots={}
        for row,b in rows:
            a=row
            while a:
                key=a.bit_length()-1
                if key not in pivots:
                    pivots[key]=(a,b)
                    break
                x,y=pivots[key]
                a^=x;b^=y
            if not a and b:raise ValueError("symbolic contradiction")
        answer=0
        for pivot in sorted(pivots):
            bits,y=pivots[pivot]
            value=y^((bits&answer).bit_count()%2)
            answer|=value<<pivot
        return answer,len(pivots)
    def _rows(self):
        rows=[[] for _ in range(4)]
        for s,a,y in self.observations:
            for j in range(1,4):
                if j==a//2:continue
                x=sum(((y>>i)&1)<<i for i in range(j))
                value=((s>>j)&1)^((y>>j)&1)
                rows[j].append((x,value))
        return rows
    def graph_mask(self):
        rows=self._rows()
        result=0
        for j in range(1,4):
            value,_=self._reduce(rows[j],j)
            for i in range(j):
                if (value>>i)&1:result|=1<<EDGES.index((i,j))
        return result
    def choose(self):
        if len(self.observations)>=BUDGET:raise ValueError("symbolic budget")
        rows=self._rows()
        seen={(s,a) for s,a,_ in self.observations}
        def new_information(pair):
            s,a=pair
            y=independent_effect(s,a,self.graph_mask())
            gain=0
            for j in range(1,4):
                if j==a//2:continue
                row=sum(((y>>i)&1)<<i for i in range(j))
                rhs=((y>>j)&1)^((s>>j)&1)
                old=self._reduce(rows[j],j)[1]
                new=self._reduce(rows[j]+[(row,rhs)],j)[1]
                gain+=new-old
            return gain
        return max((p for p in SUPPORT if p not in seen),
                   key=lambda p:(new_information(p),-p[0],-p[1]))
    def observe(self,s,a,y):
        if len(self.observations)>=BUDGET or (s,a) in {(x,z) for x,z,_ in self.observations}:
            raise ValueError("symbolic duplicate/budget")
        if (s,a) not in SUPPORT or type(y)!=int or not 0<=y<16 or ((y>>(a//2))&1)!=(a&1):
            raise ValueError("symbolic invalid intervention")
        self.observations.append((s,a,y))
        try:self.graph_mask()
        except BaseException:
            self.observations.pop()
            raise
    def predict(self,s,a):
        return independent_effect(s,a,self.graph_mask())
    def triple(self,state,actions):
        out=[]
        for a in actions:
            state=self.predict(state,a)
            out.append(state)
        return tuple(out)

class FittedKernelGraph:
    """Fully fitted nonlinear RBF kernel ridge on 128 public graph-world tables.

    Frozen choice: Hamming RBF gamma=0.7, ridge=0.001; exact 8x8 solve.
    """
    GAMMA=0.7
    RIDGE=0.001
    def __init__(self,training_observations):
        n=len(training_observations)
        if n!=128 or any(len(row)!=128 for row in training_observations):
            raise ValueError("conventional prior requires all 128 full public worlds")
        means={}
        for s in range(16):
            for a in range(8):
                values=[row[s*8+a][2] for row in training_observations]
                means[(s,a)]=tuple(sum((y>>b)&1 for y in values)/n for b in range(4))
        self.prior=means
        self.obs=[]
        self.coef=[[0.0]*0 for _ in range(4)]
    @classmethod
    def _kernel(cls,x,z):
        state,action=x
        ss,aa=z
        return exp(-cls.GAMMA*((state^ss).bit_count()+(action^aa).bit_count()))
    @staticmethod
    def _solve(matrix,values):
        n=len(values)
        a=[list(matrix[i])+[float(values[i])] for i in range(n)]
        for col in range(n):
            pivot=max(range(col,n),key=lambda r:abs(a[r][col]))
            if abs(a[pivot][col])<1e-10:raise ValueError("unfitted kernel")
            a[col],a[pivot]=a[pivot],a[col]
            v=a[col][col]
            for j in range(col,n+1):a[col][j]/=v
            for i in range(n):
                if i==col:continue
                f=a[i][col]
                for j in range(col,n+1):a[i][j]-=f*a[col][j]
        result=[a[i][n] for i in range(n)]
        if max((abs(sum(matrix[i][j]*result[j] for j in range(n))-values[i])
                for i in range(n)),default=0)>1e-8:
            raise ValueError("kernel fit nonconverged")
        return result
    def observe(self,s,a,y):
        if len(self.obs)>=BUDGET or (s,a) in {(x,z) for x,z,_ in self.obs} or (s,a) not in SUPPORT:
            raise ValueError("conventional duplicate/budget")
        if type(y)!=int or not 0<=y<16:raise ValueError("invalid effect")
        self.obs.append((s,a,y))
        points=[(x,z) for x,z,_ in self.obs]
        k=[[self._kernel(x,z)+(self.RIDGE if i==j else 0.0)
            for j,z in enumerate(points)] for i,x in enumerate(points)]
        self.coef=[]
        for b in range(4):
            residual=[((out>>b)&1)-self.prior[(x,z)][b] for x,z,out in self.obs]
            self.coef.append(self._solve(k,residual))
    def predict(self,s,a):
        if (s,a) in ((x,z) for x,z,_ in self.obs):
            return next(y for x,z,y in self.obs if x==s and z==a)
        probs=[]
        for b in range(4):
            y=self.prior[(s,a)][b]+sum(weight*self._kernel((s,a),(x,z))
                                         for weight,(x,z,_) in zip(self.coef[b],self.obs))
            probs.append(y)
        return sum(int(v>=0.5)<<b for b,v in enumerate(probs))
    def choose(self):
        if len(self.obs)>=BUDGET:raise ValueError("conventional budget")
        seen={(s,a) for s,a,_ in self.obs}
        def variance(q):
            p=self.prior[q]
            return sum(v*(1-v) for v in p)+(1.0-max(self._kernel(q,z) for z in seen) if seen else 1.0)
        return max((q for q in SUPPORT if q not in seen),
                   key=lambda q:(variance(q),-q[0],-q[1]))
    def triple(self,state,actions):
        out=[]
        for a in actions:
            state=self.predict(state,a)
            out.append(state)
        return tuple(out)
