"""NCI-NOVEL-04: isolated, source-only sparse ANF research. No Yggdrasil owner access.

Causal expressions are XORs of 0..2 public monomials (degree <=3), plus
an optional parity constant. The correct expression is never an input.
"""
from __future__ import annotations
from itertools import combinations
from collections import defaultdict
import hashlib
import json
import math
import zlib

NOISE=.06
STAGES=('t','y')

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def bit(x):
    if type(x) is not int or x not in (0,1):
        raise ValueError('REQUIRE_BINARY_PUBLIC_VALUE')
    return x

def grammar(n):
    if n not in (5,6):raise ValueError('UNSUPPORTED_PUBLIC_FEATURE_COUNT')
    size=1<<n
    universe=(1<<size)-1
    monomials=[]
    for degree in (1,2,3):
        for c in combinations(range(n),degree):
            varmask=sum(1<<i for i in c)
            sig=sum(int((x&varmask)==varmask)<<x for x in range(size))
            monomials.append((sig,tuple(c),degree))
    distinct={}
    def add(sig,complexity,terms,flip):
        prev=distinct.get(sig)
        proposal=(complexity,terms,flip)
        if prev is None or proposal<prev:
            distinct[sig]=proposal
    add(0,0,(),0)
    for sig,terms,degree in monomials:
        add(sig,degree, (terms,),0)
    for (sig1,terms1,degree1),(sig2,terms2,degree2) in combinations(monomials,2):
        add(sig1^sig2,degree1+degree2+1,(terms1,terms2),0)
    base=list(distinct.items())
    for sig,(complexity,terms,flip) in base:
        add(sig^universe,complexity+1,terms,1)
    # Original evidence sees *public coordinate 3* but never an evaluator label.
    return tuple((sig,cost,terms,flip,any(3 in term for term in terms))
                 for sig,(cost,terms,flip) in sorted(distinct.items()))

GRAMMAR={5:grammar(5),6:grammar(6)}

class SparseANF:
    """Exact same-grammar Bayesian and MAP arms, fitted only on witnessed outcomes."""
    def __init__(self, stage,kind):
        if stage not in STAGES or kind not in ('MAP','BMA','NOX3'):
            raise ValueError('BAD_ANF_MODEL')
        self.stage,self.kind=stage,kind
        n=5 if stage=='t' else 6
        self.templates=tuple(z for z in GRAMMAR[n] if kind!='NOX3' or not z[4])
        self.scores=[-.6 * z[1] for z in self.templates]
        self.n=0
        self.seen=set()
    def posterior(self):
        m=max(self.scores)
        w=[math.exp(v-m) for v in self.scores]
        total=sum(w)
        return [v/total for v in w]
    def evidence(self):
        p=self.posterior()
        relevant=sum(v for v, z in zip(p,self.templates) if z[4])
        paired=0
        for context in self.seen:
            if context[3]==0:
                flip=context[:3]+(1,)+context[4:]
                if flip in self.seen:paired+=1
        strongest=max(p)
        identified=(self.kind!='NOX3' and self.n>=64 and paired>=2
                    and relevant>=.95 and strongest>=.95)
        return {'relevance_probability':relevant,'max_posterior':strongest,
                'paired_public_contrasts':paired,'identified':identified,'witnesses':self.n}
    def forecast(self,x):
        if len(x)!=(5 if self.stage=='t' else 6):raise ValueError('INPUT_LENGTH')
        ix=sum(bit(v)<<i for i,v in enumerate(x))
        p=self.posterior()
        if self.kind=='MAP' and self.evidence()['identified']:
            k=max(range(len(p)),key=lambda i:(p[i],-self.templates[i][1],-self.templates[i][0]))
            value=(self.templates[k][0]>>ix)&1
            return (1-NOISE) if value else NOISE
        prob=sum(v for v,z in zip(p,self.templates) if (z[0]>>ix)&1)
        return NOISE+(1-2*NOISE)*prob
    def update(self,x,y):
        ix=sum(bit(v)<<i for i,v in enumerate(x))
        bit(y)
        yes=math.log(1-NOISE)
        no=math.log(NOISE)
        for i,z in enumerate(self.templates):
            self.scores[i]+=yes if ((z[0]>>ix)&1)==y else no
        self.n+=1
        self.seen.add(tuple(x))
    def snapshot(self):
        return {'stage':self.stage,'kind':self.kind,'n':self.n,
                'scores':[x.hex() for x in self.scores],
                'seen':[list(z) for z in sorted(self.seen)]}
    @classmethod
    def restore(cls,d):
        m=cls(d['stage'],d['kind'])
        if len(d['scores'])!=len(m.scores):raise ValueError('ANF_TEMPLATE_DRIFT')
        m.n=d['n'];m.scores=[float.fromhex(s) for s in d['scores']]
        m.seen={tuple(z) for z in d['seen']}
        return m

class PublicBeta:
    def __init__(self,stage,kind):
        if stage not in STAGES or kind not in ('FULL','BACKOFF'):
            raise ValueError('BAD_BETA')
        self.stage,self.kind=stage,kind
        self.counts=defaultdict(lambda:[0,0]);self.n=0
    def forecast(self,x):
        x=tuple(bit(v) for v in x)
        if self.kind=='FULL':
            neg,pos=self.counts.get(('full',x),(0,0))
            return (pos+.5)/(neg+pos+1)
        total=0.0;mass=0.0
        for mask in range(1<<len(x)):
            key=(mask,tuple(x[j] for j in range(len(x)) if (mask>>j)&1))
            neg,pos=self.counts.get(key,(0,0))
            count=neg+pos
            weight=((count+1)/(count+4))/(2**mask.bit_count())
            total+=weight*(pos+.5)/(count+1)
            mass+=weight
        return total/mass
    def update(self,x,y):
        x=tuple(bit(v) for v in x);bit(y)
        if self.kind=='FULL':self.counts[('full',x)][y]+=1
        else:
            for mask in range(1<<len(x)):
                self.counts[(mask,tuple(x[j] for j in range(len(x)) if mask>>j&1))][y]+=1
        self.n+=1
    def evidence(self):
        return {'identified':False,'relevance_probability':None,'max_posterior':None,'witnesses':self.n}
    def snapshot(self):
        return {'stage':self.stage,'kind':self.kind,'n':self.n,
                'counts':[(repr(k),list(v)) for k,v in sorted(self.counts.items())]}
    @classmethod
    def restore(cls,d):
        import ast
        m=cls(d['stage'],d['kind']);m.n=d['n']
        for key,value in d['counts']:
            r=ast.literal_eval(key)
            if type(r) is not tuple:raise ValueError('INVALID_PUBLIC_KEY')
            m.counts[r]=list(value)
        return m

class ResearchArm:
    """Research-only additive old/new public-type scopes. Not a canonical model."""
    KINDS=('MAP','BMA','NOX3','FULL','BACKOFF')
    def __init__(self,kind):
        if kind not in self.KINDS:raise ValueError('UNKNOWN_ARM')
        self.kind=kind
        self.models={};self.receipts={};self.root='0'*64
    def _model(self,ids,stage):
        if not(type(ids) is tuple and len(ids)==6 and len(set(ids))==6
               and all(type(s) is str and s for s in ids)):
            raise ValueError('PUBLIC_ROLE_IDENTITY')
        if stage not in STAGES:raise ValueError('STAGE')
        key=(ids,stage)
        if key not in self.models:
            self.models[key]=(SparseANF(stage,self.kind) if self.kind in ('MAP','BMA','NOX3')
                              else PublicBeta(stage,self.kind))
        return self.models[key]
    def forecast(self,ids,stage,x):
        return self._model(ids,stage).forecast(x)
    def evidence(self,ids,stage):
        return self._model(ids,stage).evidence()
    def admit(self,ids,stage,x,y,witness):
        if type(witness) is not str or len(witness)!=64 or any(q not in '0123456789abcdef' for q in witness):
            raise ValueError('WITNESS_ID')
        event=digest(canonical([ids,stage,x,bit(y)]))
        if witness in self.receipts:
            if self.receipts[witness]!=event:raise ValueError('WITNESS_CONFLICT')
            return False
        self._model(ids,stage).update(x,y)
        self.receipts[witness]=event
        self.root=digest((self.root+witness+event).encode('ascii'))
        return True
    def old_digest(self,ids):
        return digest(canonical({s:self._model(ids,s).snapshot() for s in STAGES}))
    def checkpoint(self):
        raw=canonical({'schema':'nci-novel04.synthetic-additive.v1','kind':self.kind,
                'models':[{'ids':list(ids),'stage':s,'snapshot':m.snapshot()}
                          for (ids,s),m in sorted(self.models.items())],
                'receipts':sorted(self.receipts.items()),'root':self.root,
                'native_accepted':False})
        if len(raw)>1000000:raise ValueError('RESEARCH_CHECKPOINT_CAPACITY')
        return b'N4Z1'+zlib.compress(raw,9)
    @classmethod
    def restore(cls,raw,expected):
        if digest(raw)!=expected or not raw.startswith(b'N4Z1') or len(raw)>250000:
            raise ValueError('CHECKPOINT_PIN')
        z=zlib.decompressobj()
        doc=z.decompress(raw[4:],max_length=1000001)
        if not z.eof or z.unused_data or z.unconsumed_tail or len(doc)>1000000:
            raise ValueError('CHECKPOINT_LIMIT')
        d=json.loads(doc)
        if set(d)!={'schema','kind','models','receipts','root','native_accepted'} or d['schema']!='nci-novel04.synthetic-additive.v1' or d['native_accepted'] is not False:
            raise ValueError('CHECKPOINT_SCHEMA')
        m=cls(d['kind'])
        for item in d['models']:
            k=(tuple(item['ids']),item['stage'])
            s=item['snapshot']
            if k[1]!=s['stage'] or k in m.models:raise ValueError('CHECKPOINT_MODELS')
            m.models[k]=SparseANF.restore(s) if s['kind'] in ('MAP','BMA','NOX3') else PublicBeta.restore(s)
        m.receipts=dict(d['receipts']);m.root=d['root']
        if len(m.receipts)!=len(d['receipts']) or m.checkpoint()!=raw:
            raise ValueError('CHECKPOINT_REPLAY_DRIFT')
        return m
