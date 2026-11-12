"""Fixed threshold/synaptic acquisition; no world or external compiler calls."""
import hashlib
import itertools
import json


def step(value):return int(value>=0)
def xor(a,b):return step(a+b-1)-step(a+b-2)


class NumericLearner:
    def __init__(self,width):
        if type(width) is not int or width not in (4,6,8):raise ValueError('width')
        self.width,self.size=width,1<<width
        self.addresses=tuple(tuple(i>>j&1 for j in range(width)) for i in range(self.size))
        self.order=tuple(sorted(range(self.size),key=lambda i:(i.bit_count(),i)))
        self.truth=[[0]*width for _ in range(self.size)]
        self.partial=[[0]*width for _ in range(self.size)]
        self.seen=[0]*self.size;self.counts=[0]*self.size;self.fault=0
        self.threshold_evaluations=0

    def choose(self):
        # All addresses compete in a fixed first-missing threshold/winner array.
        prefix=0;wins=[]
        for address in self.order:
            available=1-self.seen[address]
            wins.append(available*(1-step(prefix-1)))
            prefix+=available
        self.threshold_evaluations+=self.size
        count=sum(wins)
        if count==0:return None  # Decode numeric done signal; not a host selector.
        if count!=1:raise ValueError('winner invariant')
        return sum(win*address for win,address in zip(wins,self.order))

    def observe(self,state,answer):
        if type(state) is not int or type(answer) is not int or not 0<=state<self.size or not 0<=answer<self.size:raise ValueError('event')
        x=tuple(state>>j&1 for j in range(self.width))
        y=tuple(answer>>j&1 for j in range(self.width))
        select=[step(sum((2*b-1)*v for b,v in zip(address,x))-sum(address)) for address in self.addresses]
        old=[sum(s*row[j] for s,row in zip(select,self.truth)) for j in range(self.width)]
        already=sum(s*seen for s,seen in zip(select,self.seen));new=1-already
        delta=[xor(a,b) for a,b in zip(y,old)]
        changed=step(sum(delta)-1)*already
        self.fault=step(self.fault+changed-1)
        subset=[step(-sum((1*b)*v for b,v in zip((1-z for z in mask),x))) for mask in self.addresses]
        # Uniform local gated synaptic writes, including replacement observations.
        self.truth=[[v+s*(out-v) for v,out in zip(row,y)] for row,s in zip(self.truth,select)]
        self.seen=[step(old+s-1) for old,s in zip(self.seen,select)]
        self.partial=[[xor(v,g*d) for v,d in zip(row,delta)] for row,g in zip(self.partial,subset)]
        self.counts=[old+g*new for old,g in zip(self.counts,subset)]
        self.threshold_evaluations+=3*self.size+2*self.width+2+2*self.size*self.width

    def coefficients(self):
        return [[step(count-(1<<sum(mask)))*v for v in row] for row,count,mask in zip(self.partial,self.counts,self.addresses)]

    def predict(self,state):
        if type(state) is not int or not 0<=state<self.size:raise ValueError('state')
        x=tuple(state>>j&1 for j in range(self.width))
        features=[step(sum(b*v for b,v in zip(mask,x))-sum(mask)) for mask in self.addresses]
        coeff=self.coefficients();out=[]
        for bit in range(self.width):
            activity=sum(f*row[bit] for f,row in zip(features,coeff))
            out.append(sum((1 if t%2 else -1)*step(activity-t) for t in range(1,self.size+1)))
        self.threshold_evaluations+=self.size*(self.width+2)
        return sum(v<<j for j,v in enumerate(out))

    def canonical(self):
        if any(type(rows) is not list or len(rows)!=self.size or any(type(row) is not list or len(row)!=self.width or any(type(v) is not int or v not in (0,1) for v in row) for row in rows) for rows in (self.truth,self.partial)):return False
        if len(self.seen)!=self.size or any(type(v) is not int or v not in (0,1) for v in self.seen) or len(self.counts)!=self.size or type(self.fault) is not int or self.fault not in (0,1):return False
        if any(any(row) and not flag for row,flag in zip(self.truth,self.seen)):return False
        # Independent integrity checks only, never used to perform learning.
        values=[sum(v<<j for j,v in enumerate(row)) for row in self.truth]
        for bit in range(self.width):
            for state in range(self.size):
                if state>>bit&1:values[state]^=values[state^(1<<bit)]
        if values!=[sum(v<<j for j,v in enumerate(row)) for row in self.partial]:return False
        for mask,count in enumerate(self.counts):
            if type(count) is not int or count!=sum(flag for state,flag in enumerate(self.seen) if state&mask==state):return False
        return True

    def snapshot(self):
        if not self.canonical():raise ValueError('numeric state')
        body=json.dumps(dict(schema='wsp45.numeric.v1',width=self.width,truth=self.truth,partial=self.partial,seen=self.seen,counts=self.counts,fault=self.fault),sort_keys=True,separators=(',',':')).encode()
        return body+b'|'+hashlib.sha256(body).hexdigest().encode()

    @classmethod
    def restore(cls,raw):
        try:
            body,digest=raw.rsplit(b'|',1)
            if hashlib.sha256(body).hexdigest().encode()!=digest:raise ValueError('digest')
            d=json.loads(body)
            if set(d)!={'schema','width','truth','partial','seen','counts','fault'} or d['schema']!='wsp45.numeric.v1':raise ValueError('schema')
            obj=cls(d['width'])
            for key in ('truth','partial','seen','counts','fault'):setattr(obj,key,d[key])
            if obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,TypeError,KeyError,AttributeError):raise ValueError('checkpoint') from None


class ActionModel:
    def __init__(self,learners):self.learners=learners
    def apply(self,action,state):return self.learners[action].predict(state)
    def rollout(self,state,actions):
        for action in actions:state=self.apply(action,state)
        return state
    def plan(self,start,goal):
        for actions in itertools.product(range(2),repeat=3):
            if self.rollout(start,actions)==goal:return actions
        return None
