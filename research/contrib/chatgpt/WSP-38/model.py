"""WSP-38: training-free numerical relation memory with a fixed compositional interpreter.

The interpreter is supplied software. This is *not* a model trained to invent rules.
"""
import hashlib
import json
from sys import getsizeof

MAGIC=b'WSP38-NUMERIC-V1|'
RELATIONS=8


def check_index(value, limit):
    if type(value) is not int or not 0 <= value < limit:
        raise ValueError('WSP38_BAD_INDEX')
    return value


class NumericalWorld:
    def __init__(self, n, rows):
        if type(n) is not int or not 2 <= n <= 32768:
            raise ValueError('WSP38_BAD_SIZE')
        if type(rows) is not tuple or len(rows) != RELATIONS:
            raise ValueError('WSP38_BAD_RELATIONS')
        canonical=[]
        for group in rows:
            if type(group) is not tuple or len(group) != n:
                raise ValueError('WSP38_BAD_ROWS')
            for row in group:
                if type(row) is not int or row < 0 or row.bit_length() > n:
                    raise ValueError('WSP38_BAD_NUMERICAL_ROW')
            canonical.append(group)
        self.n=n
        self.rows=tuple(canonical)

    @staticmethod
    def from_observations(n, records):
        """Only actually observed source, relation and target triples are received."""
        if type(records) is not tuple:
            raise ValueError('WSP38_BAD_OBSERVATIONS')
        rows=[[0]*n for _ in range(RELATIONS)]
        count=0
        for rec in records:
            if type(rec) is not tuple or len(rec)!=3:
                raise ValueError('WSP38_BAD_OBSERVATION')
            rel,source,target=rec
            check_index(rel,RELATIONS)
            check_index(source,n)
            check_index(target,n)
            old=rows[rel][source]
            new=old | (1<<target)
            if new!=old:
                count+=1
            rows[rel][source]=new
        return NumericalWorld(n,tuple(tuple(g) for g in rows)),count

    def knows(self,rel,src,dst):
        check_index(rel,RELATIONS)
        check_index(src,self.n)
        check_index(dst,self.n)
        return (self.rows[rel][src] >> dst)&1

    def reach(self,source,rel_sequence):
        check_index(source,self.n)
        if type(rel_sequence) is not tuple or not 1<=len(rel_sequence)<=6:
            raise ValueError('WSP38_BAD_PATH')
        cur=1<<source
        for rel in rel_sequence:
            check_index(rel,RELATIONS)
            destinations=0
            frontier=cur
            group=self.rows[rel]
            while frontier:
                low=frontier & -frontier
                src=low.bit_length()-1
                destinations |= group[src]
                frontier ^= low
            cur=destinations
        return cur

    def answer(self,src,rel_sequence,dst):
        check_index(dst,self.n)
        return (self.reach(src,rel_sequence)>>dst)&1

    def patch(self,rel,src,dst,value):
        check_index(rel,RELATIONS)
        check_index(src,self.n)
        check_index(dst,self.n)
        if type(value) is not int or value not in (0,1):
            raise ValueError('WSP38_BAD_PATCH')
        old=self.rows[rel][src]
        new=old | (1<<dst) if value else old & ~(1<<dst)
        groups=list(self.rows)
        group=list(groups[rel])
        group[src]=new
        groups[rel]=tuple(group)
        return NumericalWorld(self.n,tuple(groups))

    @property
    def nominal_bits(self):
        return RELATIONS*self.n*self.n

    @property
    def numerical_heap_bytes(self):
        return sum(getsizeof(v) for group in self.rows for v in group)

    @property
    def active_edges(self):
        return sum(v.bit_count() for group in self.rows for v in group)

    def snapshot(self):
        """Canonical sparse edge list, not zero-padded dense tensor; checksum enforced."""
        groups=[]
        for group in self.rows:
            out=[]
            for mask in group:
                dest=[]
                while mask:
                    low=mask & -mask
                    dest.append(low.bit_length()-1)
                    mask^=low
                out.append(dest)
            groups.append(out)
        raw=json.dumps({'schema':'wsp38.numeric-memory.v1','n':self.n,'groups':groups},sort_keys=True,separators=(',',':')).encode('ascii')
        return MAGIC+len(raw).to_bytes(8,'big')+raw+hashlib.sha256(raw).digest()

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not raw.startswith(MAGIC) or len(raw)<len(MAGIC)+40:
            raise ValueError('WSP38_CHECKPOINT_REJECTED')
        length=int.from_bytes(raw[len(MAGIC):len(MAGIC)+8],'big')
        data=raw[len(MAGIC)+8:-32]
        if length!=len(data) or hashlib.sha256(data).digest()!=raw[-32:]:
            raise ValueError('WSP38_CHECKPOINT_REJECTED')
        try:
            obj=json.loads(data.decode('ascii'))
            if type(obj) is not dict or set(obj)!={'schema','n','groups'} or obj['schema']!='wsp38.numeric-memory.v1':
                raise ValueError('bad schema')
            n=obj['n']
            if type(n) is not int or not 2<=n<=32768 or type(obj['groups']) is not list or len(obj['groups'])!=RELATIONS:
                raise ValueError('bad shape')
            rows=[]
            for group in obj['groups']:
                if type(group) is not list or len(group)!=n:
                    raise ValueError('bad group')
                masks=[]
                for entries in group:
                    if type(entries) is not list or entries!=sorted(set(entries)):
                        raise ValueError('bad entries')
                    mask=0
                    for dst in entries:
                        check_index(dst,n)
                        mask|=1<<dst
                    masks.append(mask)
                rows.append(tuple(masks))
            world=cls(n,tuple(rows))
            if world.snapshot()!=raw:
                raise ValueError('noncanonical')
            return world
        except (ValueError,TypeError,KeyError,OverflowError,UnicodeError,RecursionError):
            raise ValueError('WSP38_CHECKPOINT_REJECTED') from None
