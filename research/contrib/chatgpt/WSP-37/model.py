"""WSP37: general-arity numerical weight memory and matched controls."""
import hashlib, json, math
VERSION=b"WSP37V1|"
GATES=8
def checked_bit(v):
    if type(v) is not int or v not in (0,1): raise ValueError("WSP37_BAD_BIT")
    return v
def spec_ok(arity,topology,n_inputs=None):
    if type(arity) is not int or arity not in (2,3,4): raise ValueError("WSP37_BAD_ARITY")
    n_inputs=arity+1 if n_inputs is None else n_inputs
    if type(topology) is not tuple or len(topology)!=GATES: raise ValueError("WSP37_BAD_TOPOLOGY")
    for i,route in enumerate(topology):
        if type(route) is not tuple or len(route)!=arity: raise ValueError("WSP37_BAD_ROUTE")
        if any(type(p) is not int or p<0 or p>=n_inputs+i for p in route): raise ValueError("WSP37_FORWARD_ROUTE")
    return True
def independent_eval(topology,truths,x):
    """Evaluator only, never called by acquisition."""
    vals=list(x)
    for route,truth in zip(topology,truths):
        k=sum(vals[p]<<j for j,p in enumerate(route))
        vals.append(truth[k])
    return vals[-1]
class NumericProgram:
    def __init__(self,arity,topology,tables):
        spec_ok(arity,topology)
        if type(tables) is not tuple or len(tables)!=GATES: raise ValueError("WSP37_BAD_TABLES")
        if any(type(t) is not tuple or len(t)!=1<<arity for t in tables): raise ValueError("WSP37_BAD_WIDTH")
        for t in tables:
            for y in t: checked_bit(y)
        self.arity,self.topology,self.tables=arity,topology,tables
        self.n_inputs=arity+1
        self.slots=self.n_inputs+GATES
        self.bits=GATES*(arity*self.slots+(1<<arity)+1)
        rows=[]
        for route,truth in zip(topology,tables):
            links=[0]*(arity*self.slots)
            for j,p in enumerate(route): links[j*self.slots+p]=1
            rows.append(tuple(links+list(truth)+[1]))
        self.rows=tuple(rows)
    def predict(self,x):
        if type(x) is not tuple or len(x)!=self.n_inputs: raise ValueError("WSP37_BAD_INPUT")
        vals=[checked_bit(b) for b in x]+[0]*GATES
        width=1<<self.arity
        for i,row in enumerate(self.rows):
            operands=[sum(row[j*self.slots+p]*vals[p] for p in range(self.slots)) for j in range(self.arity)]
            basis=[math.prod(v if (k>>j)&1 else 1-v for j,v in enumerate(operands)) for k in range(width)]
            vals[self.n_inputs+i]=sum(v*w for v,w in zip(basis,row[-width-1:-1]))*row[-1]
        return vals[-1]
    def patch(self,gate,k,newbit):
        checked_bit(newbit)
        if type(gate) is not int or not 0<=gate<GATES or type(k) is not int or not 0<=k<(1<<self.arity): raise ValueError("WSP37_BAD_PATCH")
        t=list(self.tables); new=list(t[gate]); new[k]=newbit; t[gate]=tuple(new)
        return NumericProgram(self.arity,self.topology,tuple(t))
    def snapshot(self):
        body=json.dumps({"arity":self.arity,"topology":self.topology,"tables":self.tables},sort_keys=True,separators=(",",":")).encode("ascii")
        return VERSION+len(body).to_bytes(4,"big")+body+hashlib.sha256(body).digest()
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not raw.startswith(VERSION) or len(raw)<len(VERSION)+36: raise ValueError("WSP37_BAD_CHECKPOINT")
        size=int.from_bytes(raw[len(VERSION):len(VERSION)+4],"big"); body=raw[len(VERSION)+4:-32]
        if size!=len(body) or hashlib.sha256(body).digest()!=raw[-32:]: raise ValueError("WSP37_BAD_CHECKPOINT")
        try:
            d=json.loads(body.decode("ascii"))
            if type(d) is not dict or set(d)!={"arity","topology","tables"}: raise ValueError("bad fields")
            obj=cls(d["arity"],tuple(tuple(r) for r in d["topology"]),tuple(tuple(r) for r in d["tables"]))
            if obj.snapshot()!=raw: raise ValueError("noncanonical")
            return obj
        except (ValueError,TypeError,OverflowError,UnicodeError,KeyError,RecursionError):
            raise ValueError("WSP37_BAD_CHECKPOINT") from None
def acquire(arity,topology,rows_by_gate,probe):
    """Learner only sees topology, permitted probe schedule and returned bits."""
    spec_ok(arity,topology); width=1<<arity
    if type(rows_by_gate) is not tuple or len(rows_by_gate)!=GATES: raise ValueError("WSP37_BAD_SCHEDULE")
    tables,transcript=[],[]
    for g,rows in enumerate(rows_by_gate):
        if type(rows) is not tuple or len(set(rows))!=len(rows) or any(type(r) is not int or not 0<=r<width for r in rows): raise ValueError("WSP37_BAD_SCHEDULE")
        truth=[0]*width
        for k in rows:
            truth[k]=checked_bit(probe(g,k)); transcript.append((g,k,truth[k]))
        tables.append(tuple(truth))
    return NumericProgram(arity,topology,tuple(tables)),tuple(transcript)
def gradient_fit(tables,rows_by_gate):
    """Converged sigmoid/BCE on observed entries, unseen default zero."""
    learned=[]; updates=0; worst_bce=0.0
    for truth,seen in zip(tables,rows_by_gate):
        result=[0]*len(truth)
        for k in seen:
            y=checked_bit(truth[k]); w=0.0
            for step in range(2048):
                p=1/(1+math.exp(-w)); bce=-math.log(max(p if y else 1-p,1e-15))
                if bce<=.01: break
                w+=y-p; updates+=1
            else: raise AssertionError("WSP37_TRAIN_NOT_CONVERGED")
            worst_bce=max(worst_bce,bce); result[k]=int(w>0)
            if result[k]!=y: raise AssertionError("WSP37_TRAIN_WRONG_OBSERVED")
        learned.append(tuple(result))
    return tuple(learned),updates,worst_bce
