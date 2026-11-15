"""WSP110 directly programmed sparse factual and compositional native parameters.

This is a *sparse associative parameter memory*, not an ordinary external
knowledge graph query at inference and not a dense native neural substrate.
One million input relation facts are encoded as uint64 parameter addresses
with float32 1.0 weights. New operators and two generations of inferred
relation-8 / relation-9 facts are held in new numeric parameter arrays.
No import of the hidden world oracle or unobserved labels is permitted.
"""
from __future__ import annotations

from hashlib import sha256
import numpy as np

N_GROUPS = 25_000
N_ORIGINAL = 1_000_000
NODE_BITS = 22
REL_BITS = 5
DEST_MASK = (1 << NODE_BITS) - 1
REL_MASK = (1 << REL_BITS) - 1
SHIFT = NODE_BITS + REL_BITS
X_REL,Y_REL = 8,9


def encode_one(source:int, relation:int, target:int) -> np.uint64:
    if (min(source,relation,target) < 0 or source >= (1<<NODE_BITS)
            or target >= (1<<NODE_BITS) or relation >= (1<<REL_BITS)):
        raise ValueError("native relational weight address out of range")
    return np.uint64((source<<SHIFT)|(relation<<NODE_BITS)|target)


def encode_batch(sources,relations,targets) -> np.ndarray:
    a = np.asarray(sources,dtype=np.uint64)
    r = np.asarray(relations,dtype=np.uint64)
    b = np.asarray(targets,dtype=np.uint64)
    if not (len(a)==len(r)==len(b)):
        raise ValueError("each fact must provide source relation target")
    if (np.any(a >= (1<<NODE_BITS)) or np.any(b >= (1<<NODE_BITS))
            or np.any(r >= (1<<REL_BITS))):
        raise ValueError("native weight address out of range")
    return (a << np.uint64(SHIFT)) | (r << np.uint64(NODE_BITS)) | b


class NativeSparseWeightMemory:
    def __init__(self):
        self.keys = None
        self.fact_weights = None
        self.stage1_operator = None
        self.stage2_operator = None
        self.support_counts_1 = None
        self.support_counts_2 = None
        self.derived_x_keys = np.empty(0,dtype=np.uint64)
        self.derived_y_keys = np.empty(0,dtype=np.uint64)

    def program_million(self,source,relation,target):
        if self.keys is not None:
            raise ValueError("original native facts may be programmed only once")
        codes = encode_batch(source,relation,target)
        if len(codes) != N_ORIGINAL:
            raise ValueError("full exact-million input required")
        keys = np.sort(codes,kind="stable")
        if np.any(keys[1:] == keys[:-1]):
            raise ValueError("duplicate fact addresses")
        self.keys = keys
        self.fact_weights = np.ones(N_ORIGINAL,dtype=np.float32)

    def original_digest(self) -> str:
        if self.keys is None:
            raise ValueError("uninitialized original native parameter memory")
        h=sha256()
        h.update(self.keys.tobytes())
        h.update(self.fact_weights.tobytes())
        return h.hexdigest()

    def original_storage_bytes(self):
        return self.keys.nbytes+self.fact_weights.nbytes

    def _first_outgoing(self,source:int) -> tuple[int,int]:
        if self.keys is None:
            raise ValueError("original facts not programmed")
        index=int(np.searchsorted(self.keys, np.uint64(source)<<np.uint64(SHIFT)))
        if index>=len(self.keys):
            raise ValueError("unknown source entity")
        key=int(self.keys[index])
        if key >> SHIFT != source or self.fact_weights[index] != 1.0:
            raise ValueError("missing or disabled source fact")
        relation = (key >> NODE_BITS) & REL_MASK
        target = key & DEST_MASK
        return relation,target

    def get_chain(self,group:int)->tuple[int,int,int]:
        """Derive source chain solely from programmed factual weights."""
        if type(group) is not int or not 0<=group<N_GROUPS:
            raise ValueError("group outside frozen query range")
        s=4*group
        a,m=self._first_outgoing(s)
        b,n=self._first_outgoing(m)
        c,t=self._first_outgoing(n)
        if not (m==s+1 and n==s+2 and t==s+3
                and 0<=a<=3 and 4<=b<=7 and 10<=c<=13):
            raise ValueError("native weight graph does not witness required chain")
        return a,b,c

    def program_operator_weights(self,feedback):
        """Program weighted rules from observed *TRAIN only* X/Y labels."""
        if self.stage1_operator is not None:
            raise ValueError("operator weights already programmed")
        pos1=np.zeros(16,dtype=np.int32)
        tot1=np.zeros(16,dtype=np.int32)
        pos2=np.zeros(4,dtype=np.int32)
        tot2=np.zeros(4,dtype=np.int32)
        seen=set()
        for group, observed_x, observed_y in feedback:
            if (type(group) is not int or not 0<=group<3000 or
                    group in seen or type(observed_x) is not bool or
                    type(observed_y) is not bool):
                raise ValueError("invalid or replayed support observation")
            if observed_y and not observed_x:
                raise ValueError("Y observation violates X-precondition")
            seen.add(group)
            a,b,c=self.get_chain(group)
            kind=a*4+(b-4)
            tot1[kind]+=1
            pos1[kind]+=int(observed_x)
            if observed_x:
                tot2[c-10]+=1
                pos2[c-10]+=int(observed_y)
        if seen!=set(range(3000)) or np.any(tot1==0) or np.any(tot2==0):
            raise ValueError("incomplete first-use observational coverage")
        self.support_counts_1=(pos1.copy(),tot1.copy())
        self.support_counts_2=(pos2.copy(),tot2.copy())
        self.stage1_operator=((pos1+1)/(tot1+2)).astype(np.float32)
        self.stage2_operator=((pos2+1)/(tot2+2)).astype(np.float32)

    def predict_rule_x(self,group:int)->bool:
        if self.stage1_operator is None:
            raise ValueError("stage1 operator not induced")
        a,b,_=self.get_chain(group)
        return bool(self.stage1_operator[a*4+b-4]>0.5)

    def _has_derived_x(self, group:int) -> bool:
        query=encode_one(4*group,X_REL,4*group+2)
        at=int(np.searchsorted(self.derived_x_keys,query))
        return bool(at<len(self.derived_x_keys) and self.derived_x_keys[at]==query)

    def infer_first_round(self):
        if self.derived_x_keys.size:
            raise ValueError("first discovery round already performed")
        new=[]
        for g in range(N_GROUPS):
            if self.predict_rule_x(g):
                new.append(encode_one(4*g,X_REL,4*g+2))
        self.derived_x_keys=np.array(sorted(new),dtype=np.uint64)

    def infer_second_round(self):
        if self.stage2_operator is None or not self.derived_x_keys.size:
            raise ValueError("second stage requires first learned relation weights")
        if self.derived_y_keys.size:
            raise ValueError("second discovery round already performed")
        new=[]
        for g in range(N_GROUPS):
            # The newly predicted X fact is retrieved from internally written
            # sparse parameters. It is NEVER replaced by the oracle X label.
            if not self._has_derived_x(g):
                continue
            _,_,c=self.get_chain(g)
            if self.stage2_operator[c-10]>0.5:
                new.append(encode_one(4*g,Y_REL,4*g+3))
        self.derived_y_keys=np.array(sorted(new),dtype=np.uint64)

    def predictions(self,group:int)->tuple[bool,bool]:
        x=encode_one(4*group,X_REL,4*group+2)
        y=encode_one(4*group,Y_REL,4*group+3)
        i=int(np.searchsorted(self.derived_x_keys,x))
        j=int(np.searchsorted(self.derived_y_keys,y))
        return (
            bool(i<len(self.derived_x_keys) and self.derived_x_keys[i]==x),
            bool(j<len(self.derived_y_keys) and self.derived_y_keys[j]==y),
        )

    def checkpoint(self):
        if self.derived_x_keys.size == 0:
            raise ValueError("checkpoint before first discovery")
        parts={
            "keys": self.keys.tobytes(),
            "fact_weights":self.fact_weights.tobytes(),
            "operator1":self.stage1_operator.tobytes(),
            "operator2":self.stage2_operator.tobytes(),
            "derived_x":self.derived_x_keys.tobytes(),
            "derived_y":self.derived_y_keys.tobytes(),
        }
        h=sha256()
        for k in sorted(parts):
            h.update(k.encode("ascii"))
            h.update(len(parts[k]).to_bytes(8,"little"))
            h.update(parts[k])
        return {"schema":"wsp110.native-sparse-weights.v1",
                "parts":parts,"sha256":h.hexdigest()}

    @classmethod
    def cold_restore(cls,document):
        if document.get("schema")!="wsp110.native-sparse-weights.v1":
            raise ValueError("invalid sparse weight checkpoint schema")
        parts=document["parts"]
        h=sha256()
        for k in sorted(parts):
            h.update(k.encode("ascii"))
            h.update(len(parts[k]).to_bytes(8,"little"))
            h.update(parts[k])
        if h.hexdigest()!=document.get("sha256"):
            raise ValueError("tampered weights or operator checkpoint")
        result=cls()
        result.keys=np.frombuffer(parts["keys"],dtype=np.uint64).copy()
        result.fact_weights=np.frombuffer(parts["fact_weights"],dtype=np.float32).copy()
        result.stage1_operator=np.frombuffer(parts["operator1"],dtype=np.float32).copy()
        result.stage2_operator=np.frombuffer(parts["operator2"],dtype=np.float32).copy()
        result.derived_x_keys=np.frombuffer(parts["derived_x"],dtype=np.uint64).copy()
        result.derived_y_keys=np.frombuffer(parts["derived_y"],dtype=np.uint64).copy()
        if (len(result.keys)!=N_ORIGINAL or
            len(result.fact_weights)!=N_ORIGINAL or
            len(result.stage1_operator)!=16 or len(result.stage2_operator)!=4 or
            np.any(result.keys[1:]<=result.keys[:-1]) or
            not np.all(result.fact_weights==1.0) or
            np.any((result.stage1_operator<=0)|(result.stage1_operator>=1)) or
            np.any((result.stage2_operator<=0)|(result.stage2_operator>=1)) or
            np.any(result.derived_x_keys[1:]<=result.derived_x_keys[:-1]) or
            np.any(result.derived_y_keys[1:]<=result.derived_y_keys[:-1])):
            raise ValueError("malformed or invalid sparse weight state")
        return result
