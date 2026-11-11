"""Local Boolean influence proxy routes directly overwritten synaptic rows.

Reverse OR sensitivities are not exact global influences at reconvergence.
No task identity, evaluator, proof or symbolic program enters this module.
"""
import hashlib
import json
import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'WSP-26'))
from two_row import TwoRow,PlasticNand,checked_six,lanes,forward_lanes,context,SEEDS,PUBLIC,LENGTHS,threshold,TRIALS20

ARMS=('error_routed','correct_routed','uniform_matched','original_single','disabled')
MAGIC=b'WSP27'

def traced_forward(masks,inputs,width=6):
    full=(1<<width)-1;values=list(inputs)
    for g in range(6):
        a,b=masks[2*g:2*g+2]
        av=values[a.bit_length()-1] if a else 0;bv=values[b.bit_length()-1] if b else 0
        values.append(full^(av&bv))
    return values[masks[-1].bit_length()-1],values

def influence_proxy(masks,values,width=6):
    full=(1<<width)-1;node=[0]*9;rows=[0]*12+[full]
    node[masks[-1].bit_length()-1]=full
    for g in range(5,-1,-1):
        a,b=masks[2*g:2*g+2]
        av=values[a.bit_length()-1] if a else 0;bv=values[b.bit_length()-1] if b else 0
        rows[2*g]=node[3+g]&bv;rows[2*g+1]=node[3+g]&av
        if a:node[a.bit_length()-1]|=rows[2*g]
        if b:node[b.bit_length()-1]|=rows[2*g+1]
    return rows

def first_eligible(influences,feedback,start):
    flags=[threshold((v&feedback).bit_count()-1) for v in influences]
    fallback=1-threshold(sum(flags)-1);flags=[v+fallback*(1-v) for v in flags]
    available=1;address=0
    for off in range(13):
        i=(start+off)%13;claim=available*flags[i];address+=i*claim;available*=1-flags[i]
    return address

class Routed(TwoRow):
    def __init__(self,initial=None,arm='error_routed'):
        if arm not in ARMS:raise ValueError('WSP27_BAD_ARM')
        super().__init__(initial,'single_protected');self.arm=arm
        self.reverse_steps=self.eligibility_tests=self.auxiliary_draws=self.routed_row_changes=0
    def canonical(self):
        return (type(self.masks) is list and len(self.masks)==13 and all(type(m) is int and 0<=m<(1<<n) and m.bit_count()<=1 and (i!=12 or m.bit_count()==1) for i,(m,n) in enumerate(zip(self.masks,LENGTHS))) and type(self.protection) is int and 0<=self.protection<32 and self.arm in ARMS)
    def adapt(self,obs,seed,steps=TRIALS20):
        checked_six(obs)
        if not self.canonical() or type(seed) is not int or seed not in SEEDS or type(steps) is not int or not 1<=steps<=TRIALS20:raise ValueError('WSP27_BAD_ADAPTATION')
        inputs=lanes(obs);target=sum(y<<i for i,(x,y) in enumerate(obs));full=63
        self.protection=(~(forward_lanes(self.masks,inputs)^target))&31
        rng=random.Random(seed);aux=random.Random(seed+27000)
        for t in range(steps):
            j=rng.randrange(13);k=rng.randrange(LENGTHS[j]);g=rng.randrange(6);a=rng.randrange(3+g);b=rng.randrange(3+g)
            prediction,values=traced_forward(self.masks,inputs);before=prediction^target
            influences=influence_proxy(self.masks,values)
            feedback=(full^before) if self.arm=='correct_routed' else before
            chosen=first_eligible(influences,feedback,j)
            routed=int(t%2==1 and self.arm in ('error_routed','correct_routed','disabled'))
            row=j+routed*(chosen-j);source=aux.randrange(LENGTHS[row])
            use_aux=int(t%2==1 and self.arm!='original_single');source=k+use_aux*(source-k)
            trial=self.masks[:];trial[row]=1<<source
            after=forward_lanes(trial,inputs)^target
            gate=threshold(before.bit_count()-after.bit_count())*threshold(-(after&self.protection).bit_count())*int(self.arm!='disabled')
            changes=sum((old^new).bit_count() for old,new in zip(self.masks,trial))
            self.masks=[old+gate*(new-old) for old,new in zip(self.masks,trial)]
            self.proposals+=1;self.accepted+=gate;self.proposed_row_writes+=1
            self.changed_coordinates+=changes;self.accepted_coordinates+=gate*changes
            self.noise_draws+=5;self.gate_evaluations+=72
            self.reverse_steps+=6;self.eligibility_tests+=13;self.auxiliary_draws+=1;self.routed_row_changes+=int(row!=j)
        return self
    def snapshot(self):
        if not self.canonical():raise ValueError('WSP27_BAD_STATE')
        base=PlasticNand();base.rows=self.rows
        body=json.dumps({'schema':'wsp27.error-routing.v1','base':base.snapshot().hex(),'protection':self.protection,'arm':self.arm},sort_keys=True,separators=(',',':')).encode('ascii')
        raw=MAGIC+len(body).to_bytes(4,'big')+body
        return raw+hashlib.sha256(raw).digest()
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 41<=len(raw)<=4096 or raw[:5]!=MAGIC or int.from_bytes(raw[5:9],'big')!=len(raw)-41 or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]:raise ValueError('WSP27_CHECKPOINT_REJECTED')
        try:
            d=json.loads(raw[9:-32].decode('ascii'))
            if type(d) is not dict or set(d)!={'schema','base','protection','arm'} or d['schema']!='wsp27.error-routing.v1':raise ValueError('schema')
            obj=cls(bytes.fromhex(d['base']),d['arm']);obj.protection=d['protection']
            if not obj.canonical() or obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,OverflowError):raise ValueError('WSP27_CHECKPOINT_REJECTED') from None
