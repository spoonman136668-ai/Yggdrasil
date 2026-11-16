"""Public-row-only learners; cannot access hidden-world generator, group identities or masks."""
from __future__ import annotations
import hashlib
import json

ARMS=('uncertainty_gated','two_slot_bayes','last_slot_reuse','local_only_beta','donor_only_fixed')
FIELDS={'x','y','ports','edge'}

def validate(row):
    if type(row)!=dict or set(row)!=FIELDS:raise ValueError('invalid public row fields')
    x=row['x'];ports=row['ports'];y=row['y'];edge=row['edge']
    if (type(x)!=list or len(x)!=6 or any(type(i)!=int or i not in (0,1) for i in x)
       or type(y)!=int or y not in (0,1) or type(ports)!=list or len(ports)!=4
       or any(type(i)!=int or not 0<=i<6 for i in ports) or len(set(ports))!=4
       or type(edge)!=int or edge not in (0,1)):
        raise ValueError('public data type or port error')
    return tuple(x),tuple(ports)

def code_and_truth(row):
    x,ports=validate(row)
    a,b,c,f=ports
    return 4*x[a]+2*x[b]+x[c],row['y']^x[f]

def slot(rows):
    if len(rows)!=16 or any(row['edge']!=i%2 for i,row in enumerate(rows)):
        raise ValueError('source slots require eight genuine public pairs')
    ports=tuple(rows[0]['ports'])
    counts=[0]*8;ones=[0]*8
    for pre,post in zip(rows[::2],rows[1::2]):
        a,p=validate(pre);b,q=validate(post)
        if p!=q or p!=ports or sum(u!=v for u,v in zip(a,b))!=1 or a[ports[3]]==b[ports[3]]:
            raise ValueError('invalid actual one-bit do pair')
        if pre['y']==post['y']:raise ValueError('source response inconsistent with witnessed bit flip')
        for row in (pre,post):
            i,v=code_and_truth(row);counts[i]+=1;ones[i]+=v
    if counts!=[2]*8:raise ValueError('full source must cover all ternary inputs')
    mask=sum(int(ones[i]*2>counts[i])<<i for i in range(8))
    if any((ones[i] not in (0,2)) for i in range(8)):
        raise ValueError('ambiguous observed primitive')
    return {'mask':mask,'counts':counts}

def receiver_rows(rows):
    if len(rows)!=4 or any(r['edge']!=i%2 for i,r in enumerate(rows)):
        raise ValueError('receiver requires two actual public pairs')
    ports=tuple(rows[0]['ports']);codes=[]
    for a,b in zip(rows[::2],rows[1::2]):
        x,p=validate(a);y,q=validate(b)
        if p!=ports or q!=ports or sum(z!=w for z,w in zip(x,y))!=1 or x[ports[3]]==y[ports[3]]:
            raise ValueError('invalid recipient do')
        ca,va=code_and_truth(a);cb,vb=code_and_truth(b)
        if ca!=cb or va!=vb or a['y']==b['y']:raise ValueError('inconsistent recipient do')
        codes.append(ca)
    if len(set(codes))!=2:raise ValueError('recipient has duplicate ternary code')
    return tuple(rows)

def local_truth(rows,code):
    values=[v for row in rows for i,v in [code_and_truth(row)] if i==code]
    return int(2*sum(values)>len(values)) if values else 0

def mismatch(mask,rows):
    return sum(((mask>>i)&1)!=v for row in rows for i,v in [code_and_truth(row)])

class Memory:
    def __init__(self,arm,donor,interference,local):
        if arm not in ARMS:raise ValueError('unregistered arm')
        self.arm=arm
        self.slots=(slot(donor),slot(interference))
        self.rows=receiver_rows(local)
        self.ports=tuple(self.rows[0]['ports'])
        self.selected=self._choose()

    def _choose(self):
        if self.arm=='uncertainty_gated':
            available=[]
            for j,s in enumerate(self.slots):
                heldout=[i for i in range(8) if i not in {code_and_truth(r)[0] for r in self.rows}]
                confidence=min((c+1)/(c+2) for i,c in enumerate(s['counts']) if i in heldout)
                if mismatch(s['mask'],self.rows)==0 and confidence>=.75:
                    available.append(j)
            return min(available) if available else None
        if self.arm=='donor_only_fixed':return 0
        if self.arm=='last_slot_reuse':return 1
        return None

    def prediction(self,x):
        x=tuple(x)
        if len(x)!=6 or any(v not in (0,1) for v in x):raise ValueError('bad public query')
        a,b,c,f=self.ports;code=4*x[a]+2*x[b]+x[c]
        if self.arm=='two_slot_bayes':
            weights=[]
            for s in self.slots:
                e=mismatch(s['mask'],self.rows)
                weights.append((.75**(len(self.rows)-e))*(.25**e))
            probs=[]
            for s in self.slots:
                bit=(s['mask']>>code)&1
                probs.append(.75 if bit else .25)
            p=sum(w*p for w,p in zip(weights,probs))/sum(weights)
            bit=int(p>.5) if abs(p-.5)>1e-12 else (self.slots[0]['mask']>>code)&1
        elif self.selected is not None:
            bit=(self.slots[self.selected]['mask']>>code)&1
        else:bit=local_truth(self.rows,code)
        return bit^x[f]

    def checkpoint(self):
        payload={'schema':'aai12u.public.v1','arm':self.arm,'slots':list(self.slots),
                 'receiver':list(self.rows),'ports':list(self.ports),'selected':self.selected}
        canonical=json.dumps(payload,sort_keys=True,separators=(',',':'))
        digest=hashlib.sha256(canonical.encode('ascii')).hexdigest()
        return json.dumps({'payload':payload,'sha256':digest},sort_keys=True,separators=(',',':'))

    @classmethod
    def restore(cls,data):
        obj=json.loads(data)
        if type(obj)!=dict or set(obj)!={'payload','sha256'}:raise ValueError('invalid checkpoint')
        p=obj['payload'];canonical=json.dumps(p,sort_keys=True,separators=(',',':'))
        if hashlib.sha256(canonical.encode('ascii')).hexdigest()!=obj['sha256']:
            raise ValueError('tampered public checkpoint')
        if (p['schema']!='aai12u.public.v1' or p['arm'] not in ARMS or len(p['slots'])!=2
            or tuple(p['ports'])!=tuple(p['receiver'][0]['ports'])):raise ValueError('invalid state')
        agent=object.__new__(cls)
        agent.arm=p['arm'];agent.slots=tuple(p['slots'])
        for s in agent.slots:
            if type(s['mask'])!=int or not 0<=s['mask']<256 or s['counts']!=[2]*8:
                raise ValueError('invalid learned primitive')
        agent.rows=receiver_rows(p['receiver']);agent.ports=tuple(p['ports'])
        agent.selected=agent._choose()
        if agent.selected!=p['selected'] or agent.checkpoint()!=data:
            raise ValueError('restored state altered')
        return agent
