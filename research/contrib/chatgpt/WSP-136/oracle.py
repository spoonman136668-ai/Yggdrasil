"""Complete SOURCE-GRAMMAR-INFORMED Boolean version-space oracle.

This is an IDENTIFIABILITY UPPER-BOUND diagnostic. Source and generator are
never imported. These candidates are deliberately unavailable to native work.
"""
from hashlib import sha256
from itertools import permutations

MASK=(1<<64)-1
OPS=("AND","OR","XOR","XNOR")
BITS=tuple(sum(1<<x for x in range(64) if ((x>>j)&1)) for j in range(6))

def bitgate(op,a,b):
    if op=="AND":return a&b
    if op=="OR":return a|b
    if op=="XOR":return a^b
    if op=="XNOR":return MASK^(a^b)
    raise ValueError("WSP135_BAD_ORACLE_OP")

def candidate_bank():
    possible=set()
    for p in permutations(range(6)):
        xs=[BITS[i] for i in p]
        for aa in OPS:
            a=bitgate(aa,xs[0],xs[1])
            for bb in OPS:
                b=bitgate(bb,xs[2],xs[3])
                for cc in OPS:
                    y=bitgate(cc,a,b)
                    possible.add(y^xs[4])
                    possible.add(y^(xs[4]&xs[5]))
                majority=(a&b)|(a&xs[4])|(b&xs[4])
                possible.add(majority^xs[5])
    return tuple(sorted(possible))

class ExactOracle:
    def __init__(self,bank):
        if not bank or any(type(x) is not int or x<0 or x>MASK for x in bank):
            raise ValueError("WSP135_INVALID_ORACLE_BANK")
        self.bank=bank
        self.all=(1<<len(bank))-1
        self.positive=tuple(sum((1<<i) for i,b in enumerate(bank) if (b>>x)&1)
                            for x in range(64))
        self.bank_hash=sha256(b"".join(t.to_bytes(8,"little") for t in bank)).hexdigest()
    def begin(self):return VersionSpace(self)

class VersionSpace:
    def __init__(self,oracle):
        self.oracle=oracle
        self.alive=oracle.all
        self.seen=set()
        self.events=[]
    def adaptive_action(self):
        if len(self.seen)>=32:return None
        count=self.alive.bit_count()
        candidates=[]
        for x in range(64):
            if x in self.seen:continue
            positive=(self.alive & self.oracle.positive[x]).bit_count()
            candidates.append((min(positive,count-positive),-x,x))
        return max(candidates)[2]
    def observe(self,x,value):
        if (type(x) is not int or not 0<=x<64 or x in self.seen
                or type(value) is not int or value not in (0,1)
                or len(self.events)>=32):
            raise ValueError("WSP135_ORACLE_INVALID_ACTUAL_EFFECT")
        observed=self.oracle.positive[x]
        self.alive&=observed if value else (self.oracle.all^observed)
        self.seen.add(x)
        self.events.append((x,value))
        if self.alive==0:
            raise AssertionError("WSP135_TRUE_LAW_NOT_IN_SOURCE_GRAMMAR")
    def infer(self,x):
        if type(x) is not int or not 0<=x<64:
            raise ValueError("WSP135_BAD_HELD_ACTION")
        pos=self.alive&self.oracle.positive[x]
        if pos==0:return 0
        if pos==self.alive:return 1
        return None
    def snapshot(self):
        body=(str(self.alive),tuple(self.events))
        return sha256(repr(body).encode()).hexdigest()
    def restore(self):
        cold=self.oracle.begin()
        for x,y in self.events:cold.observe(x,y)
        if cold.alive!=self.alive or cold.snapshot()!=self.snapshot():
            raise ValueError("WSP135_ORACLE_COLD_REPLAY_BROKEN")
        return cold
