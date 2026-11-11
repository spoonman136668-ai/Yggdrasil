"""Full source fact acquisition with explicit direct-write fact weights.

The memory/address primitive,finite routing language and impact heuristic are
supplied. Derived fallback/plan caches are counted,not hidden truth knowledge.
"""
import hashlib
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'WSP-29'))
from composition import Composition,PlasticNand,CONFIGS,route_bits,context,forward,checked_context,threshold,bit
PUBLIC=(0,1,2,4,7);SOURCE_KNOWN=PUBLIC+(3,);HIDDEN=(3,5,6)
MODES=('source_four','source_two','no_query')
BUDGETS={'source_four':4,'source_two':2,'no_query':0}
QUESTIONS=(('s',0,5),('s',0,6),('s',1,5),('s',1,6))
MAGIC=b'WSP33'

def address(x):checked_context(x);return x[0]+2*x[1]+4*x[2]
def checked_evidence(examples,indices):
    if type(examples) is not tuple or len(examples)!=len(indices):raise ValueError('WSP33_BAD_EVIDENCE')
    for e,i in zip(examples,indices):
        if type(e) is not tuple or len(e)!=2 or e[0]!=context(i):raise ValueError('WSP33_BAD_EVIDENCE')
        checked_context(e[0]);bit(e[1])

def winner(scores):
    wins=[]
    for i,s in enumerate(scores):
        w=1
        for j,t in enumerate(scores):
            if i!=j:w*=threshold(s-t-int(j<i))
        wins.append(w)
    if sum(wins)!=1:raise AssertionError('WSP33_NUMERIC_WINNER')
    return sum(i*w for i,w in enumerate(wins))

class BroadModel(Composition):
    def __init__(self,payloads,source_examples,target_examples,mode='no_query'):
        if mode not in MODES:raise ValueError('WSP33_BAD_MODE')
        if type(source_examples) is not tuple or len(source_examples)!=2:raise ValueError('WSP33_BAD_SOURCE_EVIDENCE')
        for obs in source_examples:checked_evidence(obs,SOURCE_KNOWN)
        checked_evidence(target_examples,PUBLIC);super().__init__(payloads)
        self.source_known=[[0]*8 for _ in range(2)];self.source_labels=[[0]*8 for _ in range(2)]
        self.target_known=[0]*8;self.target_labels=[0]*8;self.query_used=0;self.mode=mode
        self._fallback=tuple(tuple(forward(bank,context(i)) for i in range(8)) for bank in self.banks);self._plan=None;self.plan_evaluations=0
        for b,obs in enumerate(source_examples):
            for x,y in obs:self.source_known[b][address(x)]=1;self.source_labels[b][address(x)]=y
        for x,y in target_examples:self.target_known[address(x)]=1;self.target_labels[address(x)]=y
        self._fit()
    def canonical(self):
        if not Composition.canonical(self) or self.mode not in MODES or type(self.query_used) is not int or not 0<=self.query_used<=BUDGETS[self.mode]:return False
        for rows in (self.source_known,self.source_labels):
            if type(rows) is not list or len(rows)!=2 or any(type(r) is not list or len(r)!=8 or any(type(v) is not int or v not in (0,1) for v in r) for r in rows):return False
        for row in (self.target_known,self.target_labels):
            if type(row) is not list or len(row)!=8 or any(type(v) is not int or v not in (0,1) for v in row):return False
        if any(v and not k for ks,vs in zip(self.source_known,self.source_labels) for k,v in zip(ks,vs)) or any(v and not k for k,v in zip(self.target_known,self.target_labels)):return False
        if any(not self.source_known[b][i] for b in range(2) for i in SOURCE_KNOWN) or any(not self.target_known[i] for i in PUBLIC):return False
        counts=(sum(self.source_known[0]),sum(self.source_known[1]),sum(self.target_known))
        if counts[2]!=5 or counts[0]+counts[1]!=12+self.query_used or not all(6<=v<=8 for v in counts[:2]):return False
        if type(self._fallback) is not tuple or len(self._fallback)!=2 or any(type(r) is not tuple or len(r)!=8 or any(type(v) is not int or v not in (0,1) for v in r) for r in self._fallback):return False
        return self._plan is None or (type(self._plan) is tuple and len(self._plan)==4 and all(type(v) is int and -1<=v<=3 for v in self._plan))
    def effective_tables(self):
        return tuple(tuple(k*y+(1-k)*p for k,y,p in zip(ks,ys,ps)) for ks,ys,ps in zip(self.source_known,self.source_labels,self._fallback))
    def _source(self,b,x):
        i=x[0]+2*x[1]+4*x[2];k=self.source_known[b][i]
        return k*self.source_labels[b][i]+(1-k)*self._fallback[b][i]
    def _output(self,x,first,outer,inject):
        inner=sum(w*self._source(b,x) for b,w in enumerate(first))
        modified=tuple(v+g*(inner-v) for v,g in zip(x,inject))
        return sum(w*self._source(b,modified) for b,w in enumerate(outer))
    def _fit(self):
        scores=[]
        for cfg in CONFIGS:
            f,o,j=route_bits(cfg)
            scores.append(sum(self.target_known[i]*(1-abs(self._output(context(i),f,o,j)-self.target_labels[i])) for i in range(8)))
        self.first,self.outer,self.inject=route_bits(CONFIGS[winner(scores)]);self.occupied=1
    def predict(self,x):
        i=address(x)
        if not self.canonical():raise ValueError('WSP33_BAD_STATE')
        if self.target_known[i]:return self.target_labels[i]
        return self._output(x,self.first,self.outer,self.inject) if self.occupied else None
    def clone(self,mode=None):
        if not self.canonical():raise ValueError('WSP33_BAD_STATE')
        m=object.__new__(BroadModel);m.banks=self.banks;m._fallback=self._fallback;m.composition_enabled=1
        m.first=self.first[:];m.outer=self.outer[:];m.inject=self.inject[:];m.occupied=self.occupied
        m.source_known=[r[:] for r in self.source_known];m.source_labels=[r[:] for r in self.source_labels]
        m.target_known=self.target_known[:];m.target_labels=self.target_labels[:];m.query_used=self.query_used;m.mode=self.mode if mode is None else mode
        if m.mode not in MODES:raise ValueError('WSP33_BAD_MODE')
        m._plan=self._plan;m.plan_evaluations=0
        return m
    def _store(self,q,y):
        kind,b,i=q;bit(y)
        if kind=='s':ks,vs=self.source_known[b],self.source_labels[b]
        else:ks,vs=self.target_known,self.target_labels
        if ks[i] and vs[i]!=y:raise ValueError('WSP33_CONTRADICTORY_KNOWN_FACT')
        ks[i]=1;vs[i]=y;self._plan=None
    def plan(self):
        if not self.canonical():raise ValueError('WSP33_BAD_STATE')
        if self.query_used>=BUDGETS[self.mode]:return None
        if self._plan is None:
            scores=[]
            for q in QUESTIONS:
                if self.source_known[q[1]][q[2]]:
                    scores.append(-1);continue
                predictions=[]
                for y in (0,1):
                    trial=self.clone('source_four')
                    trial._store(q,y);trial.query_used+=1;trial._fit()
                    predictions.append(tuple(trial.predict(context(i)) for i in HIDDEN))
                scores.append(sum(a!=b for a,b in zip(*predictions)))
            self._plan=tuple(scores);self.plan_evaluations+=1
        return self._plan
    def query(self):
        if not self.canonical():raise ValueError('WSP33_BAD_STATE')
        if self.query_used>=BUDGETS[self.mode]:return None
        scores=self.plan()
        return QUESTIONS[winner(scores)]
    def answer(self,q,y):
        bit(y)
        if type(q) is not tuple or len(q)!=3 or type(q[1]) is not int or type(q[2]) is not int or q not in QUESTIONS:raise ValueError('WSP33_BAD_ANSWER_ADDRESS')
        if not self.canonical():raise ValueError('WSP33_BAD_STATE')
        kind,b,i=q;known=self.source_known[b][i] if kind=='s' else self.target_known[i];value=self.source_labels[b][i] if kind=='s' else self.target_labels[i]
        if known:
            if value==y:return
            raise ValueError('WSP33_CONTRADICTORY_KNOWN_FACT')
        if self.query_used>=BUDGETS[self.mode]:raise ValueError('WSP33_QUERY_BUDGET')
        if q!=self.query():raise ValueError('WSP33_UNSOLICITED_ANSWER')
        self._store(q,y);self.query_used+=1;self._fit()
    def snapshot(self):
        if not self.canonical():raise ValueError('WSP33_BAD_STATE')
        if self._fallback!=tuple(tuple(forward(bank,context(i)) for i in range(8)) for bank in self.banks):raise ValueError('WSP33_CORRUPT_DERIVED_FALLBACK')
        fields=('source_known','source_labels','target_known','target_labels','first','outer','inject','occupied','query_used','mode')
        d={k:getattr(self,k) for k in fields};d.update(schema='wsp33.broad-facts.v1',banks=[p.hex() for p in self.payloads()])
        body=json.dumps(d,sort_keys=True,separators=(',',':')).encode('ascii');raw=MAGIC+len(body).to_bytes(4,'big')+body
        return raw+hashlib.sha256(raw).digest()
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 41<=len(raw)<=12000 or raw[:5]!=MAGIC or int.from_bytes(raw[5:9],'big')!=len(raw)-41 or hashlib.sha256(raw[:-32]).digest()!=raw[-32:]:raise ValueError('WSP33_CHECKPOINT_REJECTED')
        try:
            d=json.loads(raw[9:-32].decode('ascii'));fields={'source_known','source_labels','target_known','target_labels','first','outer','inject','occupied','query_used','mode'}
            if type(d) is not dict or set(d)!=fields|{'schema','banks'} or d['schema']!='wsp33.broad-facts.v1' or type(d['banks']) is not list or len(d['banks'])!=2:raise ValueError('schema')
            m=object.__new__(cls);Composition.__init__(m,tuple(bytes.fromhex(p) for p in d['banks']))
            for k in fields:setattr(m,k,d[k])
            m._fallback=tuple(tuple(forward(bank,context(i)) for i in range(8)) for bank in m.banks);m._plan=None;m.plan_evaluations=0
            if not m.canonical() or m.snapshot()!=raw:raise ValueError('canonical')
            return m
        except (ValueError,TypeError,KeyError,IndexError,UnicodeError,RecursionError,OverflowError):raise ValueError('WSP33_CHECKPOINT_REJECTED') from None
