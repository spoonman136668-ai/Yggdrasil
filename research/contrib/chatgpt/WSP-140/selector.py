"""WSP140 exact source-blind bit-parallel version-space selector.

No source import, oracle or received truth beyond actual public action/effect.
Supplied generic structural hypothesis bank is unchanged from WSP137.
"""
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

PATH=Path(__file__).resolve().parents[1]/'WSP-137'/'policy.py'
SPEC=spec_from_file_location('_wsp140_pinned_wsp137_policy',PATH)
BASE=module_from_spec(SPEC)
sys.modules[SPEC.name]=BASE
SPEC.loader.exec_module(BASE)
N=BASE.N
common_held=BASE.common_held
available_pool=BASE.available_pool
fixed_schedule=BASE.fixed_schedule

# No source or truth data are needed to prepare these masks. Rank positions
# match the exact WSP137 candidate_preference SHA256 ordering.
_PAIR_MASKS={}

@lru_cache(maxsize=1)
def _table():
    templates=N.templates()
    ranked=tuple(BASE.candidate_preference())
    size=len(ranked)
    if size!=17640 or len(set(ranked))!=size:
        raise AssertionError('WSP140_PINNED_RANK_OR_GRAMMAR_DRIFT')
    width=(size+7)//8
    buffers=[bytearray(width) for _ in range(64*16)]
    for rank_position,template_index in enumerate(ranked):
        byte=rank_position>>3
        one=1<<(rank_position&7)
        codes=templates[template_index]
        for x,code in enumerate(codes):
            buffers[(x<<4)+code][byte]|=one
    bitsets=tuple(int.from_bytes(b,'little') for b in buffers)
    return ranked,templates,bitsets,(1<<size)-1

def _equal_code_mask(a,b):
    if a>b:a,b=b,a
    if a==b:raise ValueError('PAIR_CANNOT_SAME_QUERY')
    key=(a,b)
    value=_PAIR_MASKS.get(key)
    if value is None:
        table=_table()[2]
        v=0
        pa=a<<4
        pb=b<<4
        for code in range(16):
            v|=table[pa+code]&table[pb+code]
        _PAIR_MASKS[key]=v
        return v
    return value

def global_cache_bytes():
    if not _table.cache_info().currsize:return 0
    rank,bank,masks,full=_table()
    # Bank is common, immutable and already held by original numeric model,
    # so only additional cached ranked tuple, masks and cached pair masks
    # are charged to the candidate.
    return (sys.getsizeof(rank)+sum(sys.getsizeof(x) for x in rank)
      +sys.getsizeof(masks)+sum(sys.getsizeof(m) for m in masks)
      +sys.getsizeof(full)+sys.getsizeof(_PAIR_MASKS)
      +sum(sys.getsizeof(k)+sum(sys.getsizeof(j) for j in k)+sys.getsizeof(v)
            for k,v in _PAIR_MASKS.items()))

class BitParallelPolicy:
    def __init__(self):
        self.events=[]
        self.pending=None
        self.positive=[]
        self.negative=[]
        # Construct initial bitset from grammar cardinality (no WSP140 source).
        self.alive=(1<<len(N.templates()))-1
    def choose(self,legal):
        if len(self.events)>=32:return None
        used={x for x,y in self.events}
        pool=[x for x in legal if x not in used]
        if not pool:raise ValueError('WSP140_NO_PUBLIC_ACTIONS')
        if len(self.events)<4:
            pick=fixed_schedule()[len(self.events)]
            if pick not in pool:raise ValueError('WSP140_MISSING_FIRST4')
        else:
            ranked,templates,masks,all_alive=_table()
            select=[]
            bits=self.alive
            while bits and len(select)<256:
                low=bits&-bits
                rank_pos=low.bit_length()-1
                bits^=low
                idx=ranked[rank_pos]
                codes=templates[idx]
                lut=[-1]*16
                for x,y in self.events:
                    c=codes[x]
                    existing=lut[c]
                    if existing!=-1 and existing!=y:
                        raise AssertionError('WSP140_SURVIVOR_VERSIONSPACE_INCONSISTENT')
                    lut[c]=y
                select.append((codes,lut))
            if not select:
                available=[x for x in fixed_schedule() if x in pool]
                pick=available[0] if available else min(pool)
            else:
                options=[]
                for x in pool:
                    zero=one=unseen=0
                    for codes,lut in select:
                        val=lut[codes[x]]
                        if val==0:zero+=1
                        elif val==1:one+=1
                        else:unseen+=1
                    options.append((min(zero,one),unseen,-x,x))
                pick=max(options)[-1]
        self.pending=pick
        return pick
    def observe(self,x,y):
        if (x!=self.pending or x in {a for a,b in self.events}
                or len(self.events)>=32 or type(y) is not int or y not in (0,1)):
            raise ValueError('WSP140_UNEXPECTED_PUBLIC_EFFECT_OR_REPLAY')
        opposite=self.negative if y else self.positive
        for old_x in opposite:
            self.alive &= ~_equal_code_mask(x,old_x)
        (self.positive if y else self.negative).append(x)
        self.events.append((x,y))
        self.pending=None

class FastArm(BASE.DirectArm):
    """Change only chooser; reuse exact original public receipt, final fit,
    inference, learning-state serialization and verification replay methods.
    """
    def _state(self,view,create=False):
        st=self.states.get(view.law_id)
        if st is None and create:
            if view.cohort!='probe':
                raise PermissionError('WSP140_CANNOT_TRAIN_RELABEL_TRANSFER')
            st={'fingerprint':view.fingerprint(),
                'receipt':BASE.digest([view.fingerprint(),'begin']),
                'events':[],'chosen':[]}
            if self.policy=='active':st['chooser']=BitParallelPolicy()
            self.states[view.law_id]=st
        if st is not None and view.cohort=='probe' and st['fingerprint']!=view.fingerprint():
            raise ValueError('WSP140_PUBLIC_VIEW_DRIFT')
        return st
