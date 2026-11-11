"""WSP24 numerical causal knowledge buckets. No evaluator/world import.

The finite affine prior, causal order and experiment-selection algorithm are
preprogrammed. Unknown coefficients are acquired from actual observations.
"""
import hashlib
import json

ACTIONS=tuple((u,mask,value) for mask in (1,2) for u in (0,1) for value in (0,1))
PRIOR=tuple(tuple((h>>j)&1 for j in range(3)) for h in range(8))
ARCH=hashlib.sha256(b'WSP24|two-affine-buckets|37taskbits|known-causal-order|gini-query-v1').hexdigest()
MAGIC=b'WSP24'


def bit(x):
    if type(x) is not int or x not in (0,1):raise ValueError('WSP24_BAD_BIT')
    return x


def step(x):return int(x>=0)


def parity(weights,features):
    s=sum(w*x for w,x in zip(weights,features))
    return step(s-1)-step(s-2)+step(s-3)


def xor(a,b):return step(a+b-1)-step(a+b-2)


def event_checked(event):
    if type(event) is not tuple or len(event)!=5:raise ValueError('WSP24_BAD_EVENT')
    u,x,y,z,mask=event
    for v in (u,x,y,z):bit(v)
    if type(mask) is not int or mask not in range(4) or (not(mask&1) and x!=u):raise ValueError('WSP24_BAD_EVENT')
    return event


def features_for(event):
    u,x,y,z,mask=event_checked(event)
    return ((1,u,x),y,1-int(bool(mask&2))),((1,x,y),z,1)


def derived(viable):
    n=sum(viable);coeff=[];known=[]
    for j in range(3):
        votes=sum(w*h[j] for w,h in zip(viable,PRIOR))
        zero=1-step(votes-1);one=step(votes-n)
        k=step(n-1)*step(zero+one-1)
        known.append(k);coeff.append(k*one)
    return coeff,known


class NumericKnowledge:
    def __init__(self):
        self.viable=[[1]*8 for _ in range(2)]
        self.coeff=[[0]*3 for _ in range(2)];self.known=[[0]*3 for _ in range(2)]
        self.used=[0]*8;self.fault=0;self.selection_evaluations=0

    def canonical(self):
        for value,n,width in ((self.viable,2,8),(self.coeff,2,3),(self.known,2,3)):
            if type(value) is not list or len(value)!=n or any(type(row) is not list or len(row)!=width or any(type(v) is not int or v not in (0,1) for v in row) for row in value):return False
        if type(self.used) is not list or len(self.used)!=8 or any(type(v) is not int or v not in (0,1) for v in self.used) or type(self.fault) is not int or self.fault not in (0,1):return False
        if self.fault!=int(any(sum(row)==0 for row in self.viable)):return False
        return all((self.coeff[j],self.known[j])==derived(self.viable[j]) for j in range(2))

    def observe(self,event):
        event_checked(event)
        if not self.canonical():raise ValueError('WSP24_BAD_KNOWLEDGE')
        if self.fault:return
        for j,(features,outcome,gate) in enumerate(features_for(event)):
            self.viable[j]=[old*(1-gate+gate*(1-xor(parity(h,features),outcome))) for old,h in zip(self.viable[j],PRIOR)]
            self.coeff[j],self.known[j]=derived(self.viable[j])
        self.fault=step(sum(1-step(sum(v)-1) for v in self.viable)-1)
        u,x,y,z,mask=event
        if mask in (1,2):
            value=x if mask==1 else y
            claim=[int((u,mask,value)==a) for a in ACTIONS]
            self.used=[old+c*(1-old) for old,c in zip(self.used,claim)]

    def complete(self):return not self.fault and sum(map(sum,self.known))==6

    def mechanism(self,bucket,features):
        if type(bucket) is not int or bucket not in (0,1) or type(features) is not tuple or len(features)!=3:
            raise ValueError('WSP24_BAD_MECHANISM_INPUT')
        for v in features:bit(v)
        if self.fault:return None
        if all(self.known[bucket]):return parity(self.coeff[bucket],features)
        n=sum(self.viable[bucket]);votes=sum(w*parity(h,features) for w,h in zip(self.viable[bucket],PRIOR))
        if votes==0:return 0
        if votes==n:return 1
        return None

    def joint(self,u,x,y):
        for v in (u,x,y):bit(v)
        if not self.canonical():raise ValueError('WSP24_BAD_KNOWLEDGE')
        return self.mechanism(1,(1,x,y))

    def choose(self):
        if not self.canonical():raise ValueError('WSP24_BAD_KNOWLEDGE')
        if self.fault or self.complete() or sum(self.used)==8:return None
        scores=[];total=sum(self.viable[0])*sum(self.viable[1])
        for u,mask,value in ACTIONS:
            x=value if mask==1 else u;counts=[0]*4
            for iy,hy in enumerate(PRIOR):
                y=value if mask==2 else parity(hy,(1,u,x))
                for iz,hz in enumerate(PRIOR):
                    z=parity(hz,(1,x,y))
                    counts[2*y+z]+=self.viable[0][iy]*self.viable[1][iz]
            scores.append(sum(c*(total-c) for c in counts))
        self.selection_evaluations+=8*64
        wins=[]
        for q,score in enumerate(scores):
            win=1-self.used[q]
            for r,other in enumerate(scores):
                if r==q:continue
                beats=step(score-other-int(r<q))
                win*=self.used[r]+(1-self.used[r])*beats
            wins.append(win)
        if sum(wins)!=1:raise AssertionError('WSP24_NUMERIC_WINNER_FAILURE')
        address=sum(i*v for i,v in enumerate(wins))
        return ACTIONS[address]

    def snapshot(self):
        if not self.canonical():raise ValueError('WSP24_BAD_KNOWLEDGE')
        body=json.dumps({'schema':'wsp24.knowledge.v1','architecture':ARCH,'viable':self.viable,'coeff':self.coeff,'known':self.known,'used':self.used,'fault':self.fault},sort_keys=True,separators=(',',':')).encode('ascii')
        raw=MAGIC+len(body).to_bytes(4,'big')+body
        return raw+hashlib.sha256(raw).digest()

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 41<=len(raw)<=4096 or raw[:5]!=MAGIC or int.from_bytes(raw[5:9],'big')!=len(raw)-41 or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]:raise ValueError('WSP24_CHECKPOINT_REJECTED')
        try:
            d=json.loads(raw[9:-32].decode('ascii'))
            if type(d) is not dict or set(d)!={'schema','architecture','viable','coeff','known','used','fault'} or d['schema']!='wsp24.knowledge.v1' or d['architecture']!=ARCH:raise ValueError('schema')
            obj=cls()
            for k in ('viable','coeff','known','used','fault'):setattr(obj,k,d[k])
            if not obj.canonical() or obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,OverflowError):raise ValueError('WSP24_CHECKPOINT_REJECTED') from None
