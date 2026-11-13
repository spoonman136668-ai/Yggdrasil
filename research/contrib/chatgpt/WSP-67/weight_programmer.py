"""WSP67 zero-gradient source-blind learning -> executable neural weight matrices.

LEARNING: infer candidate causal conjunctions from charged physical experiences
and construct numeric dense W1/b1, W2/b2, W3/b3 ReLU neural parameters.
INFERENCE: run *only* the dense neural forward pass. Never call a symbolic
candidate model, evidence lookup, hidden simulator or compiler to predict.
Confidence is a separate learned neural output head; it stores no outcome
labels. This is an engineered hypothesis-to-weights compiler, not independent
neural feature discovery or replacement of general neural training.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import combinations,product
from math import isfinite
import json

ACTIONS=tuple(range(4))
STATES=tuple(product((0,1),repeat=4))
INPUTS=8
MAX_CHARGES=96
MAX_WEIGHTS=50000
MAX_SNAPSHOT_CHARS=1500000


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def statecheck(s):
    if type(s) is not tuple or s not in STATES:
        raise ValueError("invalid sensor state")
    return s


def patterns():
    """Predeclared candidate causal flip hypothesis class: constants+<=2 AND."""
    out=[None,()]
    for k in (1,2):
        for dims in combinations(range(4),k):
            for vals in product((0,1),repeat=k):
                out.append(tuple(zip(dims,vals)))
    return tuple(out)


PREDICATES=patterns()


def activates(predicate,state):
    return False if predicate is None else all(state[dim]==val
                                                for dim,val in predicate)


def _detector(conditions,action):
    """A ReLU neuron of exactly 1 iff action and all state literals match."""
    row=[0.0]*INPUTS
    row[4+action]=1.0
    bias=0.0
    for dim,val in conditions:
        row[dim]=1.0 if val==1 else -1.0
        if val==1:
            bias-=1.0
    return row,bias


def _affine_relu(matrix,bias,x):
    return [max(0.0,sum(w*v for w,v in zip(row,x))+b)
            for row,b in zip(matrix,bias)]


class NeuralWeights:
    """An executable 8->H1->13->5 ReLU network, not a symbolic rule table."""
    def __init__(self,w1,b1,w2,b2,w3,b3):
        self.w1,self.b1=w1,b1
        self.w2,self.b2=w2,b2
        self.w3,self.b3=w3,b3
        self._validate()

    def _validate(self):
        n=len(self.w1)
        if n==0 or n>MAX_WEIGHTS:
            raise ValueError("invalid first hidden width")
        shapes=((self.w1,self.b1,n,INPUTS),
                (self.w2,self.b2,13,n),
                (self.w3,self.b3,5,13))
        for matrix,bias,height,width in shapes:
            if (type(matrix) is not list or type(bias) is not list or
                    len(matrix)!=height or len(bias)!=height):
                raise ValueError("bad neural matrix dimensions")
            for row in matrix:
                if type(row) is not list or len(row)!=width:
                    raise ValueError("ragged or invalid neural weight matrix")
                if any(type(x) not in (float,int) or not isfinite(x) for x in row):
                    raise ValueError("nonfinite or invalid neural weight")
            if any(type(x) not in (float,int) or not isfinite(x) for x in bias):
                raise ValueError("nonfinite neural bias")
        if self.parameter_count()>MAX_WEIGHTS:
            raise ValueError("neural parameter budget exceeded")

    def parameter_count(self):
        return sum(len(r) for matrix in (self.w1,self.w2,self.w3)
                   for r in matrix)+len(self.b1)+len(self.b2)+len(self.b3)

    def nonzero_parameters(self):
        return sum(x!=0 for matrix in (self.w1,self.w2,self.w3)
                   for row in matrix for x in row)+sum(x!=0 for bias in
                   (self.b1,self.b2,self.b3) for x in bias)

    def _raw(self,before,action):
        statecheck(before)
        if type(action) is not int or action not in ACTIONS:
            raise ValueError("invalid action channel")
        x=list(map(float,before)) + [float(a==action) for a in ACTIONS]
        h1=_affine_relu(self.w1,self.b1,x)
        h2=_affine_relu(self.w2,self.b2,h1)
        return [sum(w*z for w,z in zip(row,h2))+b
                for row,b in zip(self.w3,self.b3)]

    def predict(self,before,action):
        y=self._raw(before,action)
        confidence=y[4]
        if not (abs(confidence)<1e-8 or abs(confidence-1)<1e-8):
            raise ArithmeticError("nonbinary neural confidence head")
        if confidence<0.5:
            return None
        for z in y[:4]:
            if min(abs(z),abs(z-1))>1e-8:
                raise ArithmeticError("nonbinary neural physical outcome")
        return tuple(int(round(z)) for z in y[:4])

    def snapshot(self):
        payload={
            "schema":"wsp67.executable-neural-weights.v1",
            "W1":self.w1,"b1":self.b1,
            "W2":self.w2,"b2":self.b2,
            "W3":self.w3,"b3":self.b3
        }
        raw=canonical(payload)
        digest=sha256(raw.encode("ascii")).hexdigest()
        result=canonical({"payload":payload,"sha256":digest})
        if len(result)>MAX_SNAPSHOT_CHARS:
            raise OverflowError("neural snapshot size cap")
        return result

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>MAX_SNAPSHOT_CHARS:
            raise ValueError("invalid neural weight bytes")
        try:
            obj=json.loads(raw)
            if type(obj) is not dict or set(obj)!={"payload","sha256"}:
                raise ValueError("invalid weight envelope")
            p=obj["payload"]
            if (type(p) is not dict or set(p)!={"schema","W1","b1","W2","b2","W3","b3"} or
                    p["schema"]!="wsp67.executable-neural-weights.v1" or
                    sha256(canonical(p).encode("ascii")).hexdigest()!=obj["sha256"]):
                raise ValueError("neural weight checksum/schema invalid")
            net=cls(p["W1"],p["b1"],p["W2"],p["b2"],p["W3"],p["b3"])
            if net.snapshot()!=raw:
                raise ValueError("neural weight snapshot noncanonical")
            return net
        except (KeyError,TypeError,ValueError,OverflowError,
                UnicodeError,json.JSONDecodeError) as e:
            raise ValueError("invalid/tampered neural weights") from e

    def zeros_ablation(self):
        return NeuralWeights(
            [[0.0]*len(row) for row in self.w1],
            [0.0]*len(self.b1),
            [[0.0]*len(row) for row in self.w2],
            [0.0]*len(self.b2),
            [[0.0]*len(row) for row in self.w3],
            [0.0]*len(self.b3)
        )

    def confidence_erase_ablation(self):
        other=NeuralWeights.restore(self.snapshot())
        other.w3[4]=[0.0]*len(other.w3[4])
        other.b3[4]=0.0
        return other


class DirectNeuralProgrammer:
    gradient_steps=0
    def __init__(self):
        self.ledger=[]
        self.current=(0,0,0,0)
        self.edits=0

    def observe(self,row):
        statecheck(row.before)
        statecheck(row.after)
        if (row.before!=self.current or
                type(row.action) is not int or row.action not in ACTIONS or
                type(row.action_cost) is not int or row.action_cost!=1 or
                len(self.ledger)>=MAX_CHARGES):
            raise ValueError("invalid charged chronological source observation")
        self.ledger.append((row.before,row.action,row.after))
        self.current=row.after

    def _candidate_functions(self,action,output_bit):
        evidence=[(before,after[output_bit]^before[output_bit])
                  for before,a,after in self.ledger if a==action]
        return tuple(predicate for predicate in PREDICATES
                     if all(int(activates(predicate,before))==flip
                            for before,flip in evidence))

    def compile(self):
        """The *only* path that uses candidate tables. Test never calls it.

        The representative rule computes outputs. A separate encoded
        confidence detector approves a state/action ONLY when every
        consistent causal candidate predicts the same output.
        """
        if not self.ledger:
            raise ValueError("no physical evidence to program")
        candidates={(a,j):self._candidate_functions(a,j)
                    for a in ACTIONS for j in range(4)}
        chosen={}
        for key,models in candidates.items():
            if not models:
                raise ValueError("observed physical effects outside structural prior")
            chosen[key]=min(models,key=lambda pred:(
                9 if pred is None else len(pred), () if pred is None else pred
            ))
        w1=[];b1=[]
        def add(row,b):
            i=len(w1)
            w1.append(row)
            b1.append(b)
            return i
        copied=[add([float(k==i) for k in range(INPUTS)],0.0)
                for i in range(4)]
        effects={j:[] for j in range(4)}
        for a in ACTIONS:
            for j in range(4):
                predicate=chosen[a,j]
                if predicate is not None:
                    row,b=_detector(predicate,a)
                    effects[j].append(add(row,b))
        confident=[]
        for a in ACTIONS:
            for s in STATES:
                if all(len({int(activates(p,s)) for p in candidates[a,j]})==1
                       for j in range(4)):
                    row,b=_detector(tuple(enumerate(s)),a)
                    confident.append(add(row,b))
        w2=[[0.0]*len(w1) for _ in range(13)]
        b2=[0.0]*13
        for j in range(4):
            w2[j][copied[j]]=1.0
            w2[8+j][copied[j]]=1.0
            b2[8+j]=-1.0
            for idx in effects[j]:
                w2[4+j][idx]+=1.0
                w2[8+j][idx]+=1.0
        for idx in confident:
            w2[12][idx]=1.0
        w3=[[0.0]*13 for _ in range(5)]
        b3=[0.0]*5
        for j in range(4):
            w3[j][j]=1.0
            w3[j][4+j]=1.0
            w3[j][8+j]=-2.0
        w3[4][12]=1.0
        self.edits+=1
        return NeuralWeights(w1,b1,w2,b2,w3,b3)
