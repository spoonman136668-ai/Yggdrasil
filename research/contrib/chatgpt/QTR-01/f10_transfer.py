"""F10: typed causal relation adapter over existing Yggdrasil native cells."""
import sys
from pathlib import Path
from dataclasses import dataclass
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from yggdrasil.public_causal_cells import PublicCausalCells

@dataclass(frozen=True)
class Link:
    source: int
    flip: int
    def __post_init__(self):
        if type(self.source) is not int or not 0<=self.source<4: raise ValueError("BAD_SOURCE")
        if type(self.flip) is not int or self.flip not in (0,1): raise ValueError("BAD_FLIP")

def checked_map(mapping):
    if type(mapping) is not dict or set(mapping)!=set(range(4)):
        raise ValueError("BAD_RELATION_MAP")
    if any(type(t) is not int or type(v) is not Link for t,v in mapping.items()):
        raise ValueError("BAD_RELATION_MAP")
    return dict(mapping)

class NativeTransfer:
    def __init__(self, cells, mapping):
        if type(cells) is not PublicCausalCells: raise ValueError("BAD_NATIVE_CELLS")
        self.cells=cells
        self.mapping=checked_map(mapping)
    def choose_target(self,target):
        if type(target) is not int or target not in self.mapping: raise ValueError("BAD_TARGET")
        edge=self.mapping[target]
        action=self.cells.choose(edge.source)
        return None if action is None else action^edge.flip

class ExactRetrieval:
    """Independent raw-event control with IDENTICAL observations and relation map."""
    def __init__(self,events,mapping):
        self.mapping=checked_map(mapping)
        if type(events) not in (tuple,list): raise ValueError("BAD_EVENTS")
        self.events=[]
        for row in events:
            if type(row) is not tuple or len(row)!=3: raise ValueError("BAD_EVENT")
            s,a,y=row
            if (type(s) is not int or not 0<=s<4 or type(a) is not int or
                a not in (0,1) or type(y) is not int or y not in (0,1)):
                raise ValueError("BAD_EVENT")
            self.events.append(row)
    def choose_target(self,target):
        if type(target) is not int or target not in self.mapping: raise ValueError("BAD_TARGET")
        edge=self.mapping[target]
        trials=[0,0];wins=[0,0]
        for s,a,y in self.events:
            if s==edge.source:
                trials[a]+=1;wins[a]+=y
        if not trials[0] or not trials[1]: return None
        lhs,rhs=wins[0]*trials[1],wins[1]*trials[0]
        return None if lhs==rhs else (0 if lhs>rhs else 1)^edge.flip
