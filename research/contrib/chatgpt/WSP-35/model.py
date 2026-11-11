"""WSP-35 direct-write blank numerical DAG. No task-specific inference branches."""
import hashlib
import json
import math

N_INPUTS=3
GATES=8
SLOTS=N_INPUTS+GATES
ROW=2*SLOTS+4+1
MAGIC=b"WSP35V1|"
MASKS=(8,14,6,9,7,1,11,4)

def bit(v):
    if type(v) is not int or v not in (0,1):
        raise ValueError("WSP35_BAD_BIT")
    return v

def source_spec(spec):
    if type(spec) is not tuple or len(spec)!=GATES:
        raise ValueError("WSP35_BAD_SPEC")
    for i,record in enumerate(spec):
        if type(record) is not tuple or len(record)!=3:
            raise ValueError("WSP35_BAD_GATE")
        a,b,truth=record
        if any(type(p) is not int or not 0<=p<N_INPUTS+i for p in (a,b)):
            raise ValueError("WSP35_FORWARD_REFERENCE")
        if type(truth) is not tuple or len(truth)!=4:
            raise ValueError("WSP35_BAD_TRUTH")
        for v in truth:
            bit(v)
    return spec

def table(mask):
    if type(mask) is not int or not 0<=mask<=15:
        raise ValueError("WSP35_BAD_MASK")
    return tuple((mask>>k)&1 for k in range(4))

class NumericCircuit:
    """216 writable bits: 8 x (2 x 11 route + 4 LUT + enable)."""
    def __init__(self,rows=None):
        self.rows=tuple(tuple(0 for _ in range(ROW)) for _ in range(GATES)) if rows is None else tuple(tuple(r) for r in rows)
        self.validate()
    def validate(self):
        if len(self.rows)!=GATES:
            raise ValueError("WSP35_BAD_ROWS")
        for i,row in enumerate(self.rows):
            if len(row)!=ROW:
                raise ValueError("WSP35_BAD_ROW")
            for v in row:
                bit(v)
            enabled=row[-1]
            if enabled:
                if sum(row[:SLOTS])!=1 or sum(row[SLOTS:2*SLOTS])!=1:
                    raise ValueError("WSP35_BAD_ROUTE")
                if any(row[k] or row[SLOTS+k] for k in range(N_INPUTS+i,SLOTS)):
                    raise ValueError("WSP35_FORWARD_ROUTE")
            elif any(row):
                raise ValueError("WSP35_DISABLED_NONZERO")
        return True
    @classmethod
    def synthesize(cls,spec):
        source_spec(spec)
        rows=[]
        for a,b,truth in spec:
            row=[0]*ROW
            row[a]=1
            row[SLOTS+b]=1
            row[2*SLOTS:2*SLOTS+4]=truth
            row[-1]=1
            rows.append(tuple(row))
        return cls(rows)
    def predict(self,x):
        if type(x) is not tuple or len(x)!=N_INPUTS:
            raise ValueError("WSP35_BAD_INPUT")
        values=[bit(v) for v in x]+[0]*GATES
        # The fixed VM only performs numerical routing and a 4-way one-hot dot.
        for i,row in enumerate(self.rows):
            a=sum(w*v for w,v in zip(row[:SLOTS],values))
            b=sum(w*v for w,v in zip(row[SLOTS:2*SLOTS],values))
            basis=((1-a)*(1-b),(1-a)*b,a*(1-b),a*b)
            y=sum(w*f for w,f in zip(row[2*SLOTS:2*SLOTS+4],basis))
            values[N_INPUTS+i]=row[-1]*y
        return values[-1]
    def snapshot(self):
        self.validate()
        body=json.dumps({"schema":"wsp35.numeric-circuit.v1","rows":self.rows},sort_keys=True,separators=(",",":")).encode("ascii")
        return MAGIC+len(body).to_bytes(4,"big")+body+hashlib.sha256(body).digest()
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not raw.startswith(MAGIC) or len(raw)<len(MAGIC)+36:
            raise ValueError("WSP35_CHECKPOINT_REJECTED")
        n=int.from_bytes(raw[len(MAGIC):len(MAGIC)+4],"big")
        body=raw[len(MAGIC)+4:-32]
        if n!=len(body) or hashlib.sha256(body).digest()!=raw[-32:]:
            raise ValueError("WSP35_CHECKPOINT_REJECTED")
        try:
            d=json.loads(body.decode("ascii"))
            if type(d) is not dict or set(d)!={"schema","rows"} or d["schema"]!="wsp35.numeric-circuit.v1":
                raise ValueError("bad schema")
            restored=cls(d["rows"])
            if restored.snapshot()!=raw:
                raise ValueError("noncanonical")
            return restored
        except (ValueError,TypeError,KeyError,OverflowError,UnicodeError,RecursionError):
            raise ValueError("WSP35_CHECKPOINT_REJECTED") from None

def sigmoid(z):
    return 1.0/(1.0+math.exp(-z))

class GateTrainCache:
    """Converged gate-wise conventional sigmoid/BCE learner, exact-source cached."""
    def __init__(self):
        self.cache={}
        self.updates=0
        self.fresh_fits=0
        self.hits=0
        self.worst_bce=0.0
    def fit(self,truth):
        t=tuple(bit(y) for y in truth)
        if len(t)!=4:
            raise ValueError("WSP35_BAD_TRAINING_TABLE")
        key=("sigmoid-bce-per-gate-v1",1.0,4096,0.01,t)
        if key in self.cache:
            self.hits+=1
            return self.cache[key]
        w=[0.0]*4
        for step in range(4097):
            probabilities=tuple(sigmoid(v) for v in w)
            loss=-sum(y*math.log(max(p,1e-15))+(1-y)*math.log(max(1-p,1e-15)) for p,y in zip(probabilities,t))/4
            if loss<=0.01:
                break
            if step==4096:
                raise AssertionError("WSP35_CONVENTIONAL_NOT_CONVERGED")
            w=[v+(y-p) for v,y,p in zip(w,t,probabilities)]
            self.updates+=1
        self.fresh_fits+=1
        self.worst_bce=max(self.worst_bce,loss)
        output=tuple(int(sigmoid(v)>0.5) for v in w)
        if output!=t:
            raise AssertionError("WSP35_CONVENTIONAL_BAD_TABLE")
        self.cache[key]=output
        return output
    def trained_circuit(self,spec):
        source_spec(spec)
        return NumericCircuit.synthesize(tuple((a,b,self.fit(truth)) for a,b,truth in spec))
