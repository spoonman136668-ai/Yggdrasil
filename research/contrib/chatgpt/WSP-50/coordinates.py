"""Programmed numerical experience-order coordinates and affine operator prior."""
import hashlib,json,itertools

def step(v):return int(v>=0)

def inverse_numeric(x,n):return sum(r*step(-abs((r*x)%n-1)) for r in range(n))

class CycleModel:
    def __init__(self,width):
        if type(width) is not int or width not in (4,6,8):raise ValueError('width')
        self.width=width;self.size=1<<width;self.coords=[0]*self.size;self.labels=[0]*self.size;self.cycle_seen=0
        self.seen=[0,0];self.planes=[[0]*width for _ in range(2)];self.valid=0;self.fitted=0;self.rejected=0;self.b=0;self.m=0
    def coord(self,x):return sum(v*step(-abs(j-x)) for j,v in enumerate(self.coords))
    def decode(self,c):return sum(v*step(-abs(j-c)) for j,v in enumerate(self.labels))
    def record_cycle(self,x,index):
        self.coords=[v+step(-abs(j-x))*(index-v) for j,v in enumerate(self.coords)]
        self.labels=[v+step(-abs(j-index))*(x-v) for j,v in enumerate(self.labels)]
        self.cycle_seen|=1<<x
    def certify(self,terminal):self.valid=step(self.cycle_seen.bit_count()-self.size)*step(-abs(terminal))
    def fit_first(self,y):self.b=self.coord(y)
    def fit_second(self,x,y):
        c=self.coord(x)
        if not self.valid or not c&1:raise ValueError('fit domain')
        self.m=((self.coord(y)-self.b)*inverse_numeric(c,self.size))%self.size;self.fitted=1
    def fact(self,a,x):return sum((p>>x&1)<<j for j,p in enumerate(self.planes[a])),self.seen[a]>>x&1
    def observe(self,a,x,y):
        if self.valid and self.fitted and a==1:
            predicted=self.decode((self.m*self.coord(x)+self.b)%self.size)
            self.rejected=step(self.rejected+step(abs(predicted-y)-1)-1)
        address=1<<x
        self.planes[a]=[p^(((p>>x&1)^(y>>j&1))*address) for j,p in enumerate(self.planes[a])];self.seen[a]|=address
    def apply(self,a,x):
        fact,observed=self.fact(a,x)
        if observed:return fact
        if not self.valid:return None
        if a==0:return self.decode((self.coord(x)+1)%self.size)
        if self.fitted and not self.rejected:return self.decode((self.m*self.coord(x)+self.b)%self.size)
        return None
    def rollout(self,x,aa):
        for a in aa:
            if x is None:return None
            x=self.apply(a,x)
        return x
    def plan(self,x,g):
        for aa in itertools.product(range(2),repeat=3):
            if self.rollout(x,aa)==g:return aa
        return None
    def snapshot(self):
        d=dict(schema='wsp50.cycle.v1',width=self.width,coords=self.coords,labels=self.labels,cycle_seen=self.cycle_seen,seen=self.seen,planes=self.planes,valid=self.valid,fitted=self.fitted,rejected=self.rejected,b=self.b,m=self.m)
        body=json.dumps(d,sort_keys=True,separators=(',',':')).encode();return body+b'|'+hashlib.sha256(body).hexdigest().encode()
    @classmethod
    def restore(cls,raw):
        try:
            body,digest=raw.rsplit(b'|',1)
            if hashlib.sha256(body).hexdigest().encode()!=digest:raise ValueError('digest')
            d=json.loads(body)
            if set(d)!={'schema','width','coords','labels','cycle_seen','seen','planes','valid','fitted','rejected','b','m'} or d['schema']!='wsp50.cycle.v1':raise ValueError('schema')
            o=cls(d['width'])
            for k in ('coords','labels','cycle_seen','seen','planes','valid','fitted','rejected','b','m'):setattr(o,k,d[k])
            if len(o.coords)!=o.size or len(o.labels)!=o.size or len(o.seen)!=2 or len(o.planes)!=2:raise ValueError('shape')
            if any(type(v) is not int or not 0<=v<o.size for v in o.coords+o.labels+[o.b,o.m]):raise ValueError('range')
            if any(type(v) is not int or v not in (0,1) for v in (o.valid,o.fitted,o.rejected)):raise ValueError('flag')
            if any(type(v) is not int or v<0 or v.bit_length()>o.size for v in o.seen+[o.cycle_seen]):raise ValueError('seen')
            for a in range(2):
                if len(o.planes[a])!=o.width or any(type(p) is not int or p<0 or p.bit_length()>o.size or p&~o.seen[a] for p in o.planes[a]):raise ValueError('planes')
            if o.valid and (sorted(o.coords)!=list(range(o.size)) or any(o.labels[o.coords[x]]!=x for x in range(o.size))):raise ValueError('bijection')
            if o.snapshot()!=raw:raise ValueError('canonical')
            return o
        except (ValueError,TypeError,KeyError,IndexError,AttributeError):raise ValueError('checkpoint') from None
