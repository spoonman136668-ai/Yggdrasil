"""FKP09: 65 shared numerical causal counts, 32 fixed nine-byte current slots.
Direct GF(2) fitting; conventional exact/optimized incremental controls.
Research-only; never writes Yggdrasil's accepted native model.
"""
from array import array
import hashlib
import struct

N=65
SLOTS=32
RAW_BYTES=65*2+32*9+4
CHECKPOINT_BYTES=4+RAW_BYTES+32
assert RAW_BYTES==422 and CHECKPOINT_BYTES==458

def validate(h):
    if type(h) is not tuple or not 1<=len(h)<=128:
        raise ValueError("FKP09_HISTORY_BUDGET")
    if any(type(x)!=int or not 0<=x<2**64 or type(y)!=int or y not in (0,1) for x,y in h):
        raise ValueError("FKP09_INVALID_OBSERVATION")
    if len(set(x for x,y in h))!=len(h):
        raise ValueError("FKP09_DUPLICATE_OBSERVATION")

def predict_program(p,x):
    if type(p)!=int or not 0<=p<2**N or type(x)!=int or not 0<=x<2**64:
        raise ValueError("FKP09_PREDICTION_INPUT")
    return ((p & (x | (1<<64))).bit_count())&1

def direct_solve(h):
    """Incremental XOR basis; only true paid action/consequence pairs."""
    validate(h); basis={}
    for x,y in h:
        row=x|(1<<64)
        while row:
            pivot=row.bit_length()-1
            if pivot not in basis:
                basis[pivot]=(row,y);break
            old,old_y=basis[pivot];row^=old;y^=old_y
        else:
            if y:return "INCONSISTENT",None,len(basis)
    if len(basis)!=N:return "UNDERDETERMINED",None,len(basis)
    p=0
    for k in sorted(basis):
        row,rhs=basis[k]
        if rhs^((p & (row & ((1<<k)-1))).bit_count()&1):
            p|=1<<k
    if any(predict_program(p,x)!=y for x,y in h):
        raise AssertionError("FKP09_DIRECT_SOLVER_MISMATCH")
    return "EXACT",p,N

def conventional_exact_solve(h):
    """Independent Gauss-Jordan conventional strong predictive control."""
    validate(h); m=[[x|(1<<64),y] for x,y in h]; rank=0
    for col in range(N):
        r=next((i for i in range(rank,len(m)) if (m[i][0]>>col)&1),None)
        if r is None:continue
        m[rank],m[r]=m[r],m[rank]
        mask,rhs=m[rank]
        for i in range(len(m)):
            if i!=rank and (m[i][0]>>col)&1:
                m[i][0]^=mask;m[i][1]^=rhs
        rank+=1
    if any(mask==0 and rhs for mask,rhs in m):
        return "INCONSISTENT",None,rank
    if rank!=N:return "UNDERDETERMINED",None,rank
    p=sum((rhs&1)<<((mask&-mask).bit_length()-1) for mask,rhs in m if mask)
    if any(predict_program(p,x)!=y for x,y in h):
        raise AssertionError("FKP09_CONVENTIONAL_SOLVER_MISMATCH")
    return "EXACT",p,rank

def replay_counts(programs):
    if len(programs)!=SLOTS:raise ValueError("FKP09_CAPACITY")
    counts=[0]*N
    for p in programs:
        if p is None:continue
        if type(p)!=int or not 0<=p<2**N:raise ValueError("FKP09_REPLAY_PROGRAM")
        for i in range(N):
            counts[i]+=((p>>i)&1)
    return tuple(counts)

class SharedWeights:
    __slots__=("counts","slots","occupied")
    def __init__(self):
        self.counts=array("H",[0]*N)
        self.slots=bytearray(SLOTS*9)
        self.occupied=0
    def program(self,i):
        if type(i)!=int or not 0<=i<SLOTS:raise ValueError("FKP09_SLOT")
        if not (self.occupied>>i)&1:return None
        p=int.from_bytes(self.slots[i*9:i*9+9],"little")
        if p>=2**N:raise ValueError("FKP09_HIGH_BITS")
        return p
    def all_programs(self):
        return tuple(self.program(i) for i in range(SLOTS))
    def update(self,i,p):
        if type(i)!=int or not 0<=i<SLOTS or type(p)!=int or not 0<=p<2**N:
            raise ValueError("FKP09_UPDATE_INPUT")
        old=self.program(i)
        if old==p:return
        step=[((p>>k)&1)-(((old or 0)>>k)&1) for k in range(N)]
        if any(not 0<=self.counts[k]+d<=SLOTS for k,d in enumerate(step)):
            raise ValueError("FKP09_ATOMIC_BOUND")
        for k,d in enumerate(step):self.counts[k]+=d
        self.slots[i*9:i*9+9]=p.to_bytes(9,"little")
        self.occupied|=1<<i
    def predict(self,i,x):
        p=self.program(i)
        return None if p is None else predict_program(p,x)
    def raw_weights(self):
        return struct.pack(">"+("H"*N),*self.counts)+bytes(self.slots)+struct.pack(">I",self.occupied)
    def snapshot(self):
        body=b"FKP9"+self.raw_weights()
        return body+hashlib.sha256(body).digest()
    @classmethod
    def restore(cls,blob):
        if type(blob)!=bytes or len(blob)!=CHECKPOINT_BYTES or blob[:4]!=b"FKP9" or hashlib.sha256(blob[:-32]).digest()!=blob[-32:]:
            raise ValueError("FKP09_TAMPER_OR_SCHEMA")
        obj=cls();pos=4
        obj.counts=array("H",struct.unpack(">"+("H"*N),blob[pos:pos+N*2]));pos+=N*2
        obj.slots=bytearray(blob[pos:pos+SLOTS*9]);pos+=SLOTS*9
        obj.occupied,=struct.unpack(">I",blob[pos:pos+4])
        for i in range(SLOTS):
            if obj.program(i) is None and any(obj.slots[i*9:i*9+9]):
                raise ValueError("FKP09_UNOCCUPIED_SLOT")
        if tuple(obj.counts)!=replay_counts(obj.all_programs()):
            raise ValueError("FKP09_COUNTERS_NOT_REPLAYABLE")
        return obj

class ConventionalIncremental:
    """Independent same-data, same-capacity optimized conventional update."""
    def __init__(self):
        self.slots=[None]*SLOTS;self.counts=[0]*N
    def update(self,i,p):
        if type(i)!=int or not 0<=i<SLOTS or type(p)!=int or not 0<=p<2**N:
            raise ValueError("FKP09_CONTROL_INPUT")
        old=self.slots[i]
        if old is not None:
            for k in range(N):self.counts[k]-=(old>>k)&1
        self.slots[i]=p
        for k in range(N):self.counts[k]+=(p>>k)&1
