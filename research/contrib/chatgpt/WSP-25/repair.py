"""Numeric local correction instance allocation; no world/evaluator access."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent/'WSP-24'))
from knowledge import NumericKnowledge, bit, step, xor, event_checked

MAGIC=b'WSP25'
ARCH='wsp25.local-repair.53bits.v1'
PAIRS=((0,0),(0,1),(1,0),(1,1))

def match(weights,x,y):
    return step(sum(a*b for a,b in zip(weights,(1-x,x,1-y,y)))-2)

class LocalRepair:
    def __init__(self,growth_enabled=1):
        bit(growth_enabled)
        self.base=NumericKnowledge();self.seen=[0]*4;self.labels=[0]*4
        self.weights=[0]*4;self.occupied=0;self.residual=0
        self.fault_z=0;self.probe_used=0;self.growth_enabled=growth_enabled

    def raw(self,x,y,weights=None,occupied=None,residual=None):
        p=self.base.joint(0,x,y)
        if p is None:return None
        w=self.weights if weights is None else weights
        a=self.occupied if occupied is None else occupied
        r=self.residual if residual is None else residual
        return xor(p,a*r*match(w,x,y))

    def canonical(self):
        if not self.base.canonical():return False
        for row,n in ((self.seen,4),(self.labels,4),(self.weights,4)):
            if type(row) is not list or len(row)!=n or any(type(v) is not int or v not in (0,1) for v in row):return False
        if any(type(v) is not int or v not in (0,1) for v in (self.occupied,self.residual,self.fault_z,self.probe_used,self.growth_enabled)):return False
        if self.occupied:
            if self.residual!=1 or sum(self.weights[:2])!=1 or sum(self.weights[2:])!=1 or not self.base.complete():return False
            if not self.seen[2*self.weights[1]+self.weights[3]]:return False
        elif self.weights!=[0]*4 or self.residual:return False
        if any(v and not s for s,v in zip(self.seen,self.labels)):return False
        if not self.base.fault:
            for i,(x,y) in enumerate(PAIRS):
                p=self.raw(x,y)
                if self.seen[i] and p is not None and p!=self.labels[i]:return False
        return True

    def observe(self,event):
        u,x,y,z,mask=event_checked(event)
        if not self.canonical():raise ValueError('WSP25_BAD_STATE')
        if self.fault_z or self.base.fault:return
        address=2*x+y
        if not self.base.complete():
            self.base.observe(event)
            if not self.base.fault:
                self.seen[address]=1;self.labels[address]=z
            return
        # Once complete, keep the affine substrate immutable. An unclamped
        # contradictory Y observation faults the wrapper's Z use, never rewrites Y.
        y_bad=(1-int(bool(mask&2)))*xor(self.predict_y(u,x),y)
        prediction=self.raw(x,y);error=xor(prediction,z)
        proposal=[1-x,x,1-y,y]
        protected_error=sum(s*xor(self.raw(a,b,proposal,1,error),label)
                            for s,label,(a,b) in zip(self.seen,self.labels,PAIRS))
        gate=error*(1-self.seen[address])*(1-self.occupied)*self.growth_enabled*(1-step(protected_error-1))*(1-y_bad)
        self.weights=[old*(1-gate)+new*gate for old,new in zip(self.weights,proposal)]
        self.occupied=self.occupied*(1-gate)+gate
        self.residual=self.residual*(1-gate)+error*gate
        self.fault_z=step(error*(1-gate)+y_bad-1)
        if not self.fault_z:
            self.seen[address]=1;self.labels[address]=z
        self.probe_used=step(self.probe_used+int(mask==3)-1)

    def choose(self):return self.base.choose()

    def validation_query(self):
        if not self.canonical():raise ValueError('WSP25_BAD_STATE')
        if not self.base.complete() or self.fault_z or self.probe_used:return None
        previous=1;claims=[]
        for s in self.seen:
            claims.append(previous*(1-s));previous*=s
        if sum(claims)==0:return None
        address=sum(i*c for i,c in enumerate(claims))
        return (0,3,address//2,address%2)

    def joint(self,u,x,y):
        for v in (u,x,y):bit(v)
        if not self.canonical():raise ValueError('WSP25_BAD_STATE')
        return None if self.fault_z else self.raw(x,y)

    def predict_y(self,u,x):
        for v in (u,x):bit(v)
        return self.base.mechanism(0,(1,u,x))

    def snapshot(self):
        if not self.canonical():raise ValueError('WSP25_BAD_STATE')
        d={k:getattr(self,k) for k in ('seen','labels','weights','occupied','residual','fault_z','probe_used','growth_enabled')}
        d.update(schema=ARCH,base=self.base.snapshot().hex())
        body=json.dumps(d,sort_keys=True,separators=(',',':')).encode('ascii')
        raw=MAGIC+len(body).to_bytes(4,'big')+body
        return raw+hashlib.sha256(raw).digest()

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 41<=len(raw)<=10000 or raw[:5]!=MAGIC or int.from_bytes(raw[5:9],'big')!=len(raw)-41 or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]:raise ValueError('WSP25_CHECKPOINT_REJECTED')
        try:
            d=json.loads(raw[9:-32].decode('ascii'))
            fields={'seen','labels','weights','occupied','residual','fault_z','probe_used','growth_enabled'}
            if type(d) is not dict or set(d)!=fields|{'schema','base'} or d['schema']!=ARCH:raise ValueError('schema')
            obj=cls(d['growth_enabled']);obj.base=NumericKnowledge.restore(bytes.fromhex(d['base']))
            for key in fields:setattr(obj,key,d[key])
            if not obj.canonical() or obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,OverflowError):raise ValueError('WSP25_CHECKPOINT_REJECTED') from None
