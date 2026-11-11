"""Numerically gated counterfactual endpoint rewiring; no evaluator imports.

Packed binary lanes execute the original NAND threshold circuit exactly.
The hand-designed policy is bounded stochastic structural search.
"""
import hashlib
import json
import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'WSP-20'))
from joint_credit import PlasticNand,checked_six,context,SEEDS,PUBLIC,LENGTHS,threshold,TRIALS20

ARMS=('mixed_protected','single_protected','pair_protected','disabled')
MAGIC=b'WSP26'

def pack_rows(rows):return [sum(v<<i for i,v in enumerate(row)) for row in rows]
def unpack_rows(masks):return [[(m>>i)&1 for i in range(n)] for m,n in zip(masks,LENGTHS)]
def lanes(obs):return tuple(sum(x[j]<<i for i,(x,y) in enumerate(obs)) for j in range(3))
def forward_lanes(masks,inputs,width=6):
    full=(1<<width)-1;values=list(inputs)
    for g in range(6):
        a,b=masks[2*g:2*g+2]
        av=values[a.bit_length()-1] if a else 0
        bv=values[b.bit_length()-1] if b else 0
        values.append(full^(av&bv))
    return values[masks[-1].bit_length()-1]
def error_lanes(masks,inputs,target):return forward_lanes(masks,inputs)^target

def changed_proposal(masks,noise,paired):
    j,k,g,a,b=noise;new=masks[:];new[j]=1<<k
    if paired:new[2*g+(b%2)]=1<<a
    return new

class TwoRow:
    def __init__(self,initial=None,arm='mixed_protected'):
        if arm not in ARMS:raise ValueError('WSP26_BAD_ARM')
        base=PlasticNand() if initial is None else PlasticNand.restore(initial)
        self.masks=pack_rows(base.rows);self.protection=0;self.arm=arm
        self.proposals=self.accepted=self.noise_draws=self.gate_evaluations=0
        self.proposed_row_writes=self.changed_coordinates=self.accepted_coordinates=0
    @property
    def rows(self):return unpack_rows(self.masks)
    def canonical(self):
        return (type(self.masks) is list and len(self.masks)==13 and all(type(m) is int and 0<=m<(1<<n) and m.bit_count()<=1 and (i!=12 or m.bit_count()==1) for i,(m,n) in enumerate(zip(self.masks,LENGTHS))) and type(self.protection) is int and 0<=self.protection<32 and self.arm in ARMS)
    def predict(self,x):
        from structural import checked_context
        checked_context(x)
        if not self.canonical():raise ValueError('WSP26_BAD_STATE')
        return forward_lanes(self.masks,x,1)
    def adapt(self,obs,seed,steps=TRIALS20):
        checked_six(obs)
        if not self.canonical() or type(seed) is not int or seed not in SEEDS or type(steps) is not int or not 1<=steps<=TRIALS20:raise ValueError('WSP26_BAD_ADAPTATION')
        inputs=lanes(obs);target=sum(y<<i for i,(x,y) in enumerate(obs))
        self.protection=(~error_lanes(self.masks,inputs,target))&31;rng=random.Random(seed)
        for t in range(steps):
            j=rng.randrange(13);k=rng.randrange(LENGTHS[j]);g=rng.randrange(6);a=rng.randrange(3+g);b=rng.randrange(3+g)
            paired=self.arm=='pair_protected' or (self.arm in ('mixed_protected','disabled') and t%2==0)
            trial=changed_proposal(self.masks,(j,k,g,a,b),paired)
            before=error_lanes(self.masks,inputs,target);after=error_lanes(trial,inputs,target)
            gate=threshold(before.bit_count()-after.bit_count())*threshold(-(after&self.protection).bit_count())*int(self.arm!='disabled')
            changes=sum((old^new).bit_count() for old,new in zip(self.masks,trial))
            self.masks=[old+gate*(new-old) for old,new in zip(self.masks,trial)]
            self.proposals+=1;self.accepted+=gate;self.proposed_row_writes+=1+int(paired)
            self.changed_coordinates+=changes;self.accepted_coordinates+=gate*changes
            self.noise_draws+=5;self.gate_evaluations+=72
        return self
    def snapshot(self):
        if not self.canonical():raise ValueError('WSP26_BAD_STATE')
        base=PlasticNand();base.rows=self.rows
        body=json.dumps({'schema':'wsp26.two-row.v1','base':base.snapshot().hex(),'protection':self.protection,'arm':self.arm},sort_keys=True,separators=(',',':')).encode('ascii')
        raw=MAGIC+len(body).to_bytes(4,'big')+body
        return raw+hashlib.sha256(raw).digest()
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 41<=len(raw)<=4096 or raw[:5]!=MAGIC or int.from_bytes(raw[5:9],'big')!=len(raw)-41 or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]:raise ValueError('WSP26_CHECKPOINT_REJECTED')
        try:
            d=json.loads(raw[9:-32].decode('ascii'))
            if type(d) is not dict or set(d)!={'schema','base','protection','arm'} or d['schema']!='wsp26.two-row.v1':raise ValueError('schema')
            obj=cls(bytes.fromhex(d['base']),d['arm']);obj.protection=d['protection']
            if not obj.canonical() or obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,OverflowError):raise ValueError('WSP26_CHECKPOINT_REJECTED') from None
