"""WSP20 preprogrammed numerical protection and coherent structural proposals."""
import hashlib
import json
import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'WSP-16'))
from neutral import (PlasticNand,checked_six,context,SEEDS,PUBLIC,LENGTHS,
                     threshold)
from structural import forward

TRIALS20=8192
ARMS=('joint_protected','single_protected','single_neutral','disabled')
MAGIC=b'WSP20'


def errors(rows,obs):
    return [threshold((p:=forward(rows,x))+y-1)-threshold(p+y-2) for x,y in obs]


def proposal(rows,noise,coherent):
    j,k,g,a,b=noise
    new=[r[:] for r in rows]
    if coherent:  # fixed schedule/noise only, never evidence-dependent
        new[2*g]=[int(i==a) for i in range(3+g)]
        new[2*g+1]=[int(i==b) for i in range(3+g)]
        new[-1]=[int(i==3+g) for i in range(9)]
    else:
        new[j]=[int(i==k) for i in range(LENGTHS[j])]
    return new


class JointNand(PlasticNand):
    def __init__(self,initial=None):
        super().__init__()
        if initial is not None:self.rows=PlasticNand.restore(initial).rows
        self.protection=[0]*5
        self.proposed_row_writes=self.changed_coordinates=self.accepted_coordinates=0

    def adapt(self,obs,seed,arm):
        checked_six(obs)
        if type(seed) is not int or seed not in SEEDS or arm not in ARMS or not self.canonical():
            raise ValueError('WSP20_INVALID_ADAPTATION')
        self.protection=[1-e for e in errors(self.rows,obs)[:5]]
        rng=random.Random(seed)
        for step in range(TRIALS20):
            j=rng.randrange(13);k=rng.randrange(LENGTHS[j]);g=rng.randrange(6)
            a=rng.randrange(3+g);b=rng.randrange(3+g)
            coherent=arm=='joint_protected' and step%2==0
            trial=proposal(self.rows,(j,k,g,a,b),coherent)
            before=errors(self.rows,obs);after=errors(trial,obs)
            reward=threshold(sum(before)-sum(after))
            protected_gate=threshold(-sum(p*e for p,e in zip(self.protection,after[:5])))
            gate={'joint_protected':protected_gate,'single_protected':protected_gate,'single_neutral':1,'disabled':0}[arm]
            reward*=gate
            changed=sum(int(a!=b) for old,new in zip(self.rows,trial) for a,b in zip(old,new))
            self.rows=[[a+reward*(b-a) for a,b in zip(old,new)] for old,new in zip(self.rows,trial)]
            self.accepted+=reward;self.proposals+=1
            self.proposed_row_writes+=3 if coherent else 1
            self.changed_coordinates+=changed;self.accepted_coordinates+=reward*changed
            self.noise_draws+=5;self.gate_evaluations+=72
        return self

    def snapshot(self):
        if type(self.protection) is not list or len(self.protection)!=5 or any(type(v) is not int or v not in (0,1) for v in self.protection):
            raise ValueError('WSP20_BAD_PROTECTION')
        body=json.dumps({'schema':'wsp20.protected-joint.v1','base':PlasticNand.snapshot(self).hex(),'protection':self.protection},sort_keys=True,separators=(',',':')).encode()
        p=MAGIC+len(body).to_bytes(4,'big')+body
        return p+hashlib.sha256(p).digest()

    @classmethod
    def restore(cls,raw):
        if (type(raw) is not bytes or not 41<=len(raw)<=4096 or raw[:5]!=MAGIC
            or int.from_bytes(raw[5:9],'big')!=len(raw)-41 or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]):
            raise ValueError('WSP20_CHECKPOINT_REJECTED')
        try:
            d=json.loads(raw[9:-32])
            if set(d)!={'schema','base','protection'} or d['schema']!='wsp20.protected-joint.v1':raise ValueError('schema')
            obj=cls(bytes.fromhex(d['base']));obj.protection=d['protection']
            if obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,OverflowError):
            raise ValueError('WSP20_CHECKPOINT_REJECTED') from None
