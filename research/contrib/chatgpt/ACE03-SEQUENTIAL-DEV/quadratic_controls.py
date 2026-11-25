"""Conventional controls for ACE03-XFER01-DEV-A1. No source or evaluator access."""
import hashlib
import math
import struct
from adaptive_contract import PAIRS, sigmoid, fit_step

MODES = ("local", "shared", "replay")
H = struct.Struct("<8sBIHHHQ")
W = struct.Struct("<I184d")
G = struct.Struct("<4d")
EVENT = struct.Struct("<BHB")
CAP = 512
LIMIT = 65535
MAGIC = b"ACE03QC1"


def features(pattern):
    x = tuple(2*((pattern >> i)&1)-1 for i in range(9))
    return (1,*x,*(x[i]*x[j] for i,j in PAIRS))


class Quad:
    def __init__(self):
        self.age = 0
        self.w = [[0.]*46 for _ in range(4)]

    def predict(self, x):
        return tuple(sigmoid(sum(a*b for a,b in zip(row,x))) for row in self.w)

    def update(self, x, y):
        self.w = [fit_step(w,x,v,self.age) for w,v in zip(self.w,y)]
        self.age += 1

    def pack(self):
        return W.pack(self.age,*(v for row in self.w for v in row))

    @classmethod
    def unpack(cls, raw):
        age,*w = W.unpack(raw)
        if age > 2*LIMIT or any(not math.isfinite(v) or abs(v)>32 for v in w):
            raise ValueError("quad state")
        if not age and any(w):
            raise ValueError("untrained weights")
        obj = cls()
        obj.age = age
        obj.w = [w[i:i+46] for i in range(0,184,46)]
        return obj


class QuadraticControl:
    def __init__(self, mode="local", seed=0):
        if mode not in MODES or type(seed) is not int or not 0<=seed<2**32:
            raise ValueError("control identity")
        self.mode,self.seed = mode,seed
        self.cursor = 0
        self.count = [0]*3
        self.local = [Quad() for _ in range(3)]
        self.shared = Quad() if mode=="shared" else None
        self.prior = [None]*3
        self.odds = [(0.,)*4 for _ in range(3)]
        self.reservoir = []

    @staticmethod
    def check(key, pattern):
        if type(key) is not int or not 0<=key<3 or type(pattern) is not int or not 0<=pattern<512:
            raise ValueError("public input")

    def predict(self, key, pattern):
        self.check(key,pattern)
        x = features(pattern)
        p = self.local[key].predict(x)
        if self.mode!="shared":
            return p
        q = (self.prior[key] or self.shared).predict(x)
        return tuple((1-w)*a+w*b for a,b,w in zip(p,q,map(sigmoid,self.odds[key])))

    def draw(self, purpose, n):
        return int.from_bytes(hashlib.sha256(
            f"ACE03-XFER01-DEV-A1:{self.seed}:replay:{purpose}:{self.cursor}".encode("ascii")
        ).digest()[:8],"big")%n

    def observe(self, sequence, key, pattern, outcomes):
        self.check(key,pattern)
        if type(sequence) is not int or sequence!=self.cursor or sequence>=LIMIT:
            raise ValueError("cursor")
        if type(outcomes) is not tuple or len(outcomes)!=4 or any(type(v) is not int or v not in (0,1) for v in outcomes):
            raise ValueError("labels")
        x = features(pattern)
        if self.mode=="shared":
            if self.prior[key] is None:
                self.prior[key] = Quad.unpack(self.shared.pack())
            p,q = self.local[key].predict(x),self.prior[key].predict(x)
            self.odds[key] = tuple(max(-16.,min(16.,z+(a-y)**2-(b-y)**2))
                                    for z,a,b,y in zip(self.odds[key],p,q,outcomes))
            self.shared.update(x,outcomes)
        self.local[key].update(x,outcomes)
        if self.mode=="replay":
            if self.reservoir:
                k,p,y = self.reservoir[self.draw("sample",len(self.reservoir))]
                self.local[k].update(features(p),y)
            event = (key,pattern,outcomes)
            if len(self.reservoir)<CAP:
                self.reservoir.append(event)
            else:
                j = self.draw("replace",self.cursor+1)
                if j<CAP:
                    self.reservoir[j] = event
        self.count[key] += 1
        self.cursor += 1

    def checkpoint(self):
        raw = H.pack(MAGIC,MODES.index(self.mode),self.seed,*self.count,self.cursor)
        raw += b"".join(q.pack() for q in self.local)
        if self.mode=="shared":
            raw += self.shared.pack()
            for p,z in zip(self.prior,self.odds):
                raw += bytes([p is not None])+(p.pack() if p else bytes(W.size))+G.pack(*z)
        if self.mode=="replay":
            raw += b"".join(EVENT.pack(k,p,sum(v<<i for i,v in enumerate(y)))
                            for k,p,y in self.reservoir)
        return raw+hashlib.sha256(raw).digest()

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not H.size+3*W.size+32<=len(raw)<=16384:
            raise ValueError("envelope")
        payload,digest = raw[:-32],raw[-32:]
        if hashlib.sha256(payload).digest()!=digest:
            raise ValueError("digest")
        magic,mode,seed,*tail = H.unpack_from(payload)
        count,cursor = tail[:3],tail[3]
        if magic!=MAGIC or mode>=len(MODES) or cursor!=sum(count) or cursor>LIMIT:
            raise ValueError("header")
        obj = cls(MODES[mode],seed)
        obj.cursor,obj.count = cursor,count
        offset = H.size
        def quad():
            nonlocal offset
            if offset+W.size>len(payload):
                raise ValueError("truncated quad")
            out = Quad.unpack(payload[offset:offset+W.size])
            offset += W.size
            return out
        obj.local = [quad() for _ in range(3)]
        ages = [q.age for q in obj.local]
        if obj.mode=="replay":
            if any(a<c for a,c in zip(ages,count)) or sum(ages)!=cursor+max(0,cursor-1):
                raise ValueError("replay ages")
            if len(payload)-offset!=min(CAP,cursor)*EVENT.size:
                raise ValueError("reservoir size")
            for k,p,bits in EVENT.iter_unpack(payload[offset:]):
                obj.check(k,p)
                if bits>15 or not count[k]:
                    raise ValueError("reservoir event")
                obj.reservoir.append((k,p,tuple((bits>>i)&1 for i in range(4))))
            offset = len(payload)
        elif ages!=count:
            raise ValueError("local exposure")
        if obj.mode=="shared":
            obj.shared = quad()
            if obj.shared.age!=cursor:
                raise ValueError("shared exposure")
            for k,n in enumerate(count):
                if offset+1+W.size+G.size>len(payload):
                    raise ValueError("truncated prior")
                flag = payload[offset]
                offset += 1
                if flag!=int(n>0):
                    raise ValueError("prior flag")
                if flag:
                    obj.prior[k] = quad()
                    if obj.prior[k].age>cursor-n:
                        raise ValueError("prior exposure")
                else:
                    if any(payload[offset:offset+W.size]):
                        raise ValueError("inactive prior")
                    offset += W.size
                z = G.unpack_from(payload,offset)
                offset += G.size
                if any(not math.isfinite(v) or abs(v)>min(n,16) for v in z):
                    raise ValueError("odds")
                obj.odds[k] = z
        if offset!=len(payload):
            raise ValueError("trailing bytes")
        return obj
