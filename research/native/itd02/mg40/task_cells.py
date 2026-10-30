"""NR-M1Q: independently implemented local-cell native public task-effect memory.

A source-free, opt-in wrapper over Yggdrasil's unchanged MG37 selected learner.
Only original selected ledger feedback may update task cells; no world stepping.
"""
import hashlib
import json
import re
from research.native.itd02.mg23.selected_target_cells import observed_key
from research.native.itd02.mg37.source_bridge import SelectedProgressCells
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter, original_public
from research.native.itd02.r10.public_adapter import canonical

SCHEMA="yggdrasil.itd02.nr-m1q.local-task-effect.v1"
MAX_CONTEXTS=4096
MAX_COUNT=4096
MAX_CHECKPOINT=12500000
COLORS={"red":0,"green":1,"blue":2,"purple":3,"yellow":4,"grey":5}
OBJECTS={"key":5,"ball":6,"box":7}
PICKUP=re.compile(r"pick up the (red|green|blue|purple|yellow|grey) (key|ball|box)\Z")

def selected_task_effect(before,selected,after):
    original_public(before)
    original_public(after)
    if type(selected) is not int or selected not in range(7):
        raise ValueError("NRM1Q_INVALID_SELECTED_ACTION")
    if before["mission"]!=after["mission"]:
        raise ValueError("NRM1Q_MISSION_CHANGED")
    if before["direction"]!=after["direction"]:
        return False
    b=before["image"][3][5]
    a=after["image"][3][5]
    if selected==5:
        return b[0]==a[0]==4 and b[1]==a[1] and b[2] in (1,2) and a[2]==0
    if selected==3:
        match=PICKUP.fullmatch(before["mission"])
        if not match:
            return False
        col,obj=match.groups()
        return b[0]==OBJECTS[obj] and b[1]==COLORS[col] and a[0]==1
    return False

class TaskCell:
    def __init__(self):
        self.count=[0]*7
        self.effect=[0]*7
    def record(self,selected,effect):
        if type(selected) is not int or selected not in range(7):
            raise ValueError("NRM1Q_INVALID_SOURCE_ACTION")
        if self.count[selected]>=MAX_COUNT:
            raise ValueError("NRM1Q_COUNT_CAP")
        self.count[selected]+=1
        if effect:
            self.effect[selected]+=1
    def propose(self,parent):
        if type(parent) is not int or parent not in range(7):
            raise ValueError("NRM1Q_BAD_NATIVE_PARENT")
        if self.count[parent]<2:
            return parent,False
        base=10000*(self.effect[parent]+1)//(self.count[parent]+2)
        best=parent
        best_score=0
        # Only observed source-selected pickup and door-toggle evidence matters.
        for action in (3,5):
            if action==parent or self.count[action]<2 or self.effect[action]==0:
                continue
            score=10000*(self.effect[action]+1)//(self.count[action]+2)
            if score>=5000 and score>=base+1000 and score>best_score:
                best=action
                best_score=score
        return best,best!=parent

class SelectedTaskCells:
    def __init__(self,parent=None,enabled=False):
        if parent is None:
            parent=SelectedProgressCells()
        if type(parent) is not SelectedProgressCells or type(enabled) is not bool:
            raise ValueError("NRM1Q_WRONG_NATIVE_PARENT")
        self.parent=parent
        self.enabled=enabled
        self.cells={}

    def start_session(self,adapter,name,live=False):
        self.parent.start_session(adapter,name,live=live)

    def choose(self,before):
        key=observed_key(before)
        base=self.parent.choose(before)
        if not self.enabled:
            return base
        cell=self.cells.get(key)
        if cell is None:
            return base
        chosen,override=cell.propose(base["action"])
        if not override:
            return base
        return {"schema":SCHEMA,"action":chosen,
                "status":"NRM1Q_LOCAL_REAL_PUBLIC_TASK_EFFECT",
                "external_fallback":False}

    def learn_selected(self,adapter,before,after):
        if type(adapter) is not OriginalMissionAdapter:
            raise ValueError("NRM1Q_WRONG_SOURCE_ADAPTER")
        key=observed_key(before)
        original_public(after)
        if key not in self.cells and len(self.cells)>=MAX_CONTEXTS:
            raise ValueError("NRM1Q_CONTEXT_CAP")
        if (not adapter.ledger or adapter.pending is not None or
            adapter.current!=after or before["mission"]!=after["mission"]):
            raise ValueError("NRM1Q_NOT_COMPLETED_SELECTED_SOURCE")
        latest=adapter.ledger[-1]
        action=latest["action"]
        effect=selected_task_effect(before,action,after)
        cell=self.cells.get(key)
        if cell is not None and cell.count[action]>=MAX_COUNT:
            raise ValueError("NRM1Q_SAMPLE_CAP")
        # The original parent validates the one genuine selected public event.
        receipt=self.parent.learn_selected(adapter,before,after)
        if cell is None:
            cell=TaskCell()
            self.cells[key]=cell
        cell.record(action,effect)
        return receipt

    def _valid(self):
        if len(self.cells)>MAX_CONTEXTS or set(self.cells)!=set(self.parent.cells):
            raise ValueError("NRM1Q_TASK_PARENT_CONTEXT_DRIFT")
        for key,cell in self.cells.items():
            if (type(key) is not str or len(key)!=64 or
                any(c not in "0123456789abcdef" for c in key) or
                type(cell) is not TaskCell or
                len(cell.count)!=7 or len(cell.effect)!=7):
                raise ValueError("NRM1Q_CONTEXT_SHAPE")
            parent=self.parent.cells[key]
            for a in range(7):
                n=cell.count[a];effect=cell.effect[a]
                if (type(n) is not int or type(effect) is not int or
                    not 0<=effect<=n<=MAX_COUNT or
                    n!=parent.count[a]):
                    raise ValueError("NRM1Q_SOURCE_COUNT_INVARIANT")

    def checkpoint(self):
        self._valid()
        task={key:{"count":cell.count,"effect":cell.effect}
              for key,cell in self.cells.items()}
        state={"schema":SCHEMA,"parent":self.parent.checkpoint().decode("utf8"),
               "task":task,"enabled":self.enabled}
        raw=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(raw)>MAX_CHECKPOINT:
            raise ValueError("NRM1Q_CHECKPOINT_CAP")
        return raw

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_CHECKPOINT:
                raise ValueError("NRM1Q_CHECKPOINT_SIZE")
            wire=json.loads(raw)
            if type(wire) is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("NRM1Q_CHECKPOINT_SHAPE")
            state=wire["state"]
            if (type(state) is not dict or
                set(state)!={"schema","parent","task","enabled"} or
                state["schema"]!=SCHEMA or type(state["parent"]) is not str or
                type(state["task"]) is not dict or type(state["enabled"]) is not bool or
                hashlib.sha256(canonical(state)).hexdigest()!=wire["sha256"]):
                raise ValueError("NRM1Q_CHECKPOINT_DIGEST")
            parent=SelectedProgressCells.restore(state["parent"].encode("utf8"))
            result=cls(parent,enabled=state["enabled"])
            if len(state["task"])>MAX_CONTEXTS:
                raise ValueError("NRM1Q_CONTEXT_CAP")
            for key,item in state["task"].items():
                if (type(item) is not dict or set(item)!={"count","effect"} or
                    type(item["count"]) is not list or type(item["effect"]) is not list or
                    len(item["count"])!=7 or len(item["effect"])!=7):
                    raise ValueError("NRM1Q_BAD_TASK_CELLS")
                cell=TaskCell()
                cell.count=item["count"]
                cell.effect=item["effect"]
                result.cells[key]=cell
            result._valid()
            if result.checkpoint()!=raw:
                raise ValueError("NRM1Q_NONCANONICAL")
            return result
        except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as error:
            raise ValueError("NRM1Q_UNTRUSTED_TASK_MEMORY") from error
