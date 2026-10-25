"""Independent empirical public seven-action outcome control; no native R11 import.

R7-C30 comparisons use equal original source selected FIT events and no
hidden MiniGrid state, object or environment access.
"""
import hashlib,json,math
SCHEMA="mass.r7c30.independent-public-categorical-control.v1"

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def cues(raw):
    if type(raw) is not dict or set(raw)!={'image','direction','mission'}:raise ValueError("NONPUBLIC")
    im=raw['image']
    if type(im) is not list or len(im)!=7 or any(type(row)is not list or len(row)!=7 for row in im):
        raise ValueError("INVALID_PUBLIC_VIEW")
    for row in im:
        for px in row:
            if type(px) is not list or len(px)!=3 or any(type(v)is not int for v in px):
                raise ValueError("INVALID_PUBLIC_PIXEL")
    front=im[3][5]
    carried=im[3][6] if im[3][6][0] in (5,6,7) else None
    return front,carried

def context(raw,action):
    front,carry=cues(raw)
    if type(action)is not int or not 0<=action<7:raise ValueError("ACTION")
    held=[0,0] if carry is None else carry[:2]
    return ':'.join(map(str,[*front,*held,action]))

def label(event):
    if type(event)is not dict:raise ValueError("EVENT")
    before=event['front_before'];after=event['front_after']
    channels=[
        before!=after,
        before[0]==4 and after[0]==4 and before[2]!=after[2],
        event['carried_before']!=event['carried_after'],
        event['heading_before']!=event['heading_after'],
        event['reward']>0,
        event['terminated'],
        event['truncated']]
    return sum(int(v)<<i for i,v in enumerate(channels))

class Control:
    def __init__(self):
        self.counts={};self.samples=0

    def learn(self,event):
        f=event['front_before'];c=event['carried_before'];a=event['action']
        held=[0,0] if c is None else c[:2]
        key=':'.join(map(str,[*f,*held,a]))
        v=str(label(event))
        group=self.counts.setdefault(key,{})
        group[v]=group.get(v,0)+1
        self.samples+=1

    def predict(self,frame,action):
        key=context(frame,action)
        group=self.counts.get(key)
        if not group:return {'status':'ABSTAIN_UNOBSERVED','samples':0,'modal':None,'modal_probability':None,'observed_distribution':None}
        n=sum(group.values());code=min(group,key=lambda v:(-group[v],int(v)))
        prob=(group[code]+1)/(n+len(group)) # Laplace smoothing over support
        return {'status':'LEARNED_PUBLIC_CONSEQUENCE','samples':n,'modal':int(code),
                'modal_probability':round(prob,9),'observed_distribution':dict(group)}

    def checkpoint(self):
        state={'schema':SCHEMA,'counts':self.counts,'samples':self.samples}
        return canonical({'state':state,'sha256':hashlib.sha256(canonical(state)).hexdigest()})

    @classmethod
    def restore(cls,blob):
        outer=json.loads(blob)
        if type(outer)is not dict or set(outer)!={'state','sha256'}:raise ValueError("CONTROL_SNAPSHOT")
        d=outer['state']
        if hashlib.sha256(canonical(d)).hexdigest()!=outer['sha256'] or d['schema']!=SCHEMA:
            raise ValueError("CONTROL_INTEGRITY")
        c=cls()
        if type(d['counts'])is not dict or type(d['samples'])is not int or not 0<=d['samples']<=4096:
            raise ValueError("CONTROL_SCHEMA")
        n=0
        for key,g in d['counts'].items():
            assert type(key)is str and len(key.split(':'))==6
            if type(g)is not dict or not g:raise ValueError("CONTROL_OUTCOME")
            for val,count in g.items():
                if not val.isdecimal() or not 0<=int(val)<128 or type(count)is not int or count<1:
                    raise ValueError("CONTROL_OUTCOME")
                n+=count
        if n!=d['samples']:raise ValueError("CONTROL_SAMPLE_DRIFT")
        c.counts=d['counts'];c.samples=d['samples']
        return c
