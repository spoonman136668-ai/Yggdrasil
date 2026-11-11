"""Direct numerical routing between two actually learned generic NAND modules.

The 12-routing language and first-winner rule are supplied; the instance is learned.
No evaluator, task identity, target recipe or hidden outcome table is imported.
"""
import hashlib
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'WSP-15'))
from structural import PlasticNand,forward,checked_context,checked_examples,threshold,context

CONFIGS=tuple((a,b,j) for a in range(2) for b in range(2) for j in range(3))
MAGIC=b'WSP29'

def bit(v):
    if type(v) is not int or v not in (0,1):raise ValueError('WSP29_BAD_BIT')
    return v

def route_bits(cfg):
    a,b,j=cfg
    return [int(a==i) for i in range(2)],[int(b==i) for i in range(2)],[int(j==i) for i in range(3)]

class Composition:
    def __init__(self,payloads,composition_enabled=1):
        bit(composition_enabled)
        if type(payloads) is not tuple or len(payloads)!=2:raise ValueError('WSP29_BAD_BANK')
        self.banks=tuple(tuple(tuple(row) for row in PlasticNand.restore(p).rows) for p in payloads)
        self.first=[0,0];self.outer=[0,0];self.inject=[0,0,0];self.occupied=0;self.composition_enabled=composition_enabled
    def canonical(self):
        if type(self.banks) is not tuple or len(self.banks)!=2:return False
        for bank in self.banks:
            if type(bank) is not tuple or any(type(row) is not tuple for row in bank):return False
            probe=PlasticNand();probe.rows=[list(row) for row in bank]
            if not probe.canonical():return False
        if any(type(v) is not int or v not in (0,1) for v in (self.occupied,self.composition_enabled)):return False
        for row,n in ((self.first,2),(self.outer,2),(self.inject,3)):
            if type(row) is not list or len(row)!=n or any(type(v) is not int or v not in (0,1) for v in row):return False
            if sum(row)!=self.occupied:return False
        return True
    def _output(self,x,first,outer,inject):
        inner=sum(w*forward(bank,x) for w,bank in zip(first,self.banks))
        modified=tuple(v+self.composition_enabled*g*(inner-v) for v,g in zip(x,inject))
        return sum(w*forward(bank,modified) for w,bank in zip(outer,self.banks))
    def learn(self,examples):
        checked_examples(examples)
        if not self.canonical():raise ValueError('WSP29_BAD_STATE')
        scores=[]
        for cfg in CONFIGS:
            f,o,j=route_bits(cfg)
            scores.append(sum(1-abs(self._output(x,f,o,j)-y) for x,y in examples))
        wins=[]
        for i,s in enumerate(scores):
            win=1
            for j,t in enumerate(scores):
                if i!=j:win*=threshold(s-t-int(j<i))
            wins.append(win)
        if sum(wins)!=1:raise AssertionError('WSP29_NUMERIC_WINNER')
        self.first=[sum(w*int(cfg[0]==i) for w,cfg in zip(wins,CONFIGS)) for i in range(2)]
        self.outer=[sum(w*int(cfg[1]==i) for w,cfg in zip(wins,CONFIGS)) for i in range(2)]
        self.inject=[sum(w*int(cfg[2]==i) for w,cfg in zip(wins,CONFIGS)) for i in range(3)]
        self.occupied=1
        return self
    def predict(self,x):
        checked_context(x)
        if not self.canonical():raise ValueError('WSP29_BAD_STATE')
        return self._output(x,self.first,self.outer,self.inject) if self.occupied else None
    def base_outputs(self):
        if not self.canonical():raise ValueError('WSP29_BAD_STATE')
        return tuple(tuple(forward(bank,context(i)) for i in range(8)) for bank in self.banks)
    def payloads(self):
        if not self.canonical():raise ValueError('WSP29_BAD_STATE')
        raw=[]
        for bank in self.banks:
            model=PlasticNand();model.rows=[list(row) for row in bank];raw.append(model.snapshot())
        return tuple(raw)
    def snapshot(self):
        if not self.canonical():raise ValueError('WSP29_BAD_STATE')
        d={'schema':'wsp29.acquired-composition.v1','banks':[p.hex() for p in self.payloads()],'first':self.first,'outer':self.outer,'inject':self.inject,'occupied':self.occupied,'composition_enabled':self.composition_enabled}
        body=json.dumps(d,sort_keys=True,separators=(',',':')).encode('ascii');raw=MAGIC+len(body).to_bytes(4,'big')+body
        return raw+hashlib.sha256(raw).digest()
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 41<=len(raw)<=10000 or raw[:5]!=MAGIC or int.from_bytes(raw[5:9],'big')!=len(raw)-41 or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]:raise ValueError('WSP29_CHECKPOINT_REJECTED')
        try:
            d=json.loads(raw[9:-32].decode('ascii'))
            if type(d) is not dict or set(d)!={'schema','banks','first','outer','inject','occupied','composition_enabled'} or d['schema']!='wsp29.acquired-composition.v1' or type(d['banks']) is not list or len(d['banks'])!=2:raise ValueError('schema')
            obj=cls(tuple(bytes.fromhex(p) for p in d['banks']),d['composition_enabled'])
            for k in ('first','outer','inject','occupied'):setattr(obj,k,d[k])
            if not obj.canonical() or obj.snapshot()!=raw:raise ValueError('canonical')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,OverflowError):raise ValueError('WSP29_CHECKPOINT_REJECTED') from None
