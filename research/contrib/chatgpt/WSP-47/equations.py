"""Fixed gated numeric equation memory, bit-parallel Boolean implementation."""
import hashlib
import itertools
import json


def step(value):return int(value>=0)


class EquationBank:
    def __init__(self,width,degree):
        if type(width) is not int or width not in (4,6,8) or degree not in (1,2,3,'full'):raise ValueError('architecture')
        self.width,self.degree,self.size=width,degree,1<<width
        limit=width if degree=='full' else degree
        self.masks=tuple(m for m in range(self.size) if m.bit_count()<=limit);self.M=len(self.masks)
        self.rows=[0]*self.M;self.rhs=[0]*self.M;self.occupied=[0]*self.M
        self.seen=0;self.planes=[0]*width;self.fault=0;self.analytical_scalar_ops=0

    def features(self,state):
        if type(state) is not int or not 0<=state<self.size:raise ValueError('state')
        return sum(step((state&m).bit_count()-m.bit_count())<<j for j,m in enumerate(self.masks))

    def observe(self,state,answer):
        if type(answer) is not int or not 0<=answer<self.size:raise ValueError('answer')
        row=self.features(state);rhs=answer
        # Fixed-size column circuit; every host iteration is architecture-defined.
        for j in range(self.M):
            bit=row>>j&1;old=self.occupied[j]
            eliminate=bit*old;write=bit*(1-old)
            row^=self.rows[j]*eliminate;rhs^=self.rhs[j]*eliminate
            self.rows[j]+=write*(row-self.rows[j]);self.rhs[j]+=write*(rhs-self.rhs[j])
            self.occupied[j]=old+write*(1-old)
            row*=1-write;rhs*=1-write
        self.fault=step(self.fault+step(rhs-1)-1)
        address=1<<state
        self.planes=[plane^(((plane>>state&1)^(answer>>j&1))*address) for j,plane in enumerate(self.planes)]
        self.seen|=address
        self.analytical_scalar_ops+=self.M*(3*self.M+3*self.width+8)+5*self.width

    def fact(self,state):
        return sum((plane>>state&1)<<j for j,plane in enumerate(self.planes)),self.seen>>state&1

    def span(self,state):
        row=self.features(state);value=0
        for j in range(self.M):
            eliminate=(row>>j&1)*self.occupied[j]
            row^=self.rows[j]*eliminate;value^=self.rhs[j]*eliminate
        known=(1-step(row-1))*(1-self.fault)
        return value,known

    def prediction(self,state):
        value,known=self.span(state);fact,observed=self.fact(state)
        return observed*fact+(1-observed)*value,step(observed+known-1)

    def predict(self,state):
        value,known=self.prediction(state)
        return value if known else None  # Generic valid-bit output decoder.

    def canonical(self):
        if any(type(v) is not int or v not in (0,1) for v in self.occupied) or type(self.fault) is not int or self.fault not in (0,1):return False
        if len(self.rows)!=self.M or len(self.rhs)!=self.M or len(self.occupied)!=self.M or len(self.planes)!=self.width:return False
        if type(self.seen) is not int or self.seen<0 or self.seen.bit_length()>self.size:return False
        for j,(row,rhs,present) in enumerate(zip(self.rows,self.rhs,self.occupied)):
            if type(row) is not int or type(rhs) is not int or row<0 or row.bit_length()>self.M or not 0<=rhs<self.size:return False
            if present and (not row>>j&1 or row&((1<<j)-1)):return False
            if not present and (row or rhs):return False
        if any(type(p) is not int or p<0 or p.bit_length()>self.size or p&~self.seen for p in self.planes):return False
        return True

    def snapshot(self):
        if not self.canonical():raise ValueError('numeric state')
        body=json.dumps(dict(schema='wsp47.equations.v1',width=self.width,degree=self.degree,rows=self.rows,rhs=self.rhs,occupied=self.occupied,seen=self.seen,planes=self.planes,fault=self.fault),sort_keys=True,separators=(',',':')).encode()
        return body+b'|'+hashlib.sha256(body).hexdigest().encode()

    @classmethod
    def restore(cls,raw):
        try:
            body,digest=raw.rsplit(b'|',1)
            if hashlib.sha256(body).hexdigest().encode()!=digest:raise ValueError('digest')
            d=json.loads(body)
            if set(d)!={'schema','width','degree','rows','rhs','occupied','seen','planes','fault'} or d['schema']!='wsp47.equations.v1':raise ValueError('schema')
            obj=cls(d['width'],d['degree'])
            for k in ('rows','rhs','occupied','seen','planes','fault'):setattr(obj,k,d[k])
            if obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,TypeError,KeyError,AttributeError):raise ValueError('checkpoint') from None


class BankModel:
    def __init__(self,banks):self.banks=banks
    def apply(self,action,state):return self.banks[action].predict(state)
    def rollout(self,state,actions):
        for a in actions:
            if state is None:return None
            state=self.apply(a,state)
        return state
    def plan(self,start,goal):
        for actions in itertools.product(range(2),repeat=3):
            if self.rollout(start,actions)==goal:return actions
        return None


class AdaptiveModel(BankModel):
    def __init__(self,models):self.models=models
    def selected(self,action):
        prefix=0;wins=[]
        for model in self.models:
            viable=1-model.banks[action].fault;wins.append(viable*(1-step(prefix-1)));prefix+=viable
        return wins
    def apply(self,action,state):
        wins=self.selected(action);pairs=[model.banks[action].prediction(state) for model in self.models]
        missing=1-step(sum(wins)-1);fact,observed=self.models[-1].banks[action].fact(state)
        value=sum(w*p[0] for w,p in zip(wins,pairs))+missing*fact
        known=sum(w*p[1] for w,p in zip(wins,pairs))+missing*observed
        return value if known else None
