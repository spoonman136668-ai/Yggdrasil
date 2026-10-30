"""MG43: source-context-local selected reward guard over frozen MG28."""
from research.native.itd02.mg28.selected_change_cells import SelectedChangeCells
from research.native.itd02.mg23.selected_target_cells import observed_key
from research.native.itd02.mg37.progress_cells import LocalProgressCells

MAX_REWARD_CONTEXTS=4096

from research.native.itd02.r10.public_adapter import canonical
import hashlib
import json
import math

MG49_SCHEMA="yggdrasil.itd02.mg49.context-reward-checkpoint.v1"
MAX_CHECKPOINT=9000000


class SelectedProgressCells:
    def __init__(self, parent=None, progress=None):
        self.parent=SelectedChangeCells() if parent is None else parent
        if type(self.parent) is not SelectedChangeCells:
            raise ValueError("MG43_WRONG_NATIVE_PARENT")
        if progress is not None and type(progress) is not LocalProgressCells:
            raise ValueError("MG43_WRONG_PROGRESS")
        self.cells={}
        # An optional prior learner is not inherited across unknown contexts.
        if progress is not None and any(progress.count):
            raise ValueError("MG43_UNSCOPED_LEGACY_REWARD")
    @property
    def progress(self):
        # Compatibility alias for source-only callers before any context is learned.
        if len(self.cells)==1:
            return next(iter(self.cells.values()))
        return LocalProgressCells()

    def start_session(self, adapter, name, live=False):
        self.parent.start_session(adapter,name,live=live)

    def choose(self, before):
        key=observed_key(before)
        base=self.parent.choose(before)
        cell=self.cells.get(key)
        if cell is None:
            return base
        selected,override=cell.choose(base["action"])
        if not override:
            return base
        return {"schema":"yggdrasil.itd02.mg43.context-reward-progress.v1",
                "action":selected,"status":"MG43_CONTEXT_REWARD_PROGRESS_OVERRIDE",
                "external_fallback":False}

    def learn_selected(self, adapter, before, after):
        key=observed_key(before)
        if key not in self.cells and len(self.cells)>=MAX_REWARD_CONTEXTS:
            raise ValueError("MG43_REWARD_CONTEXT_CAP")
        # No reward admitted before the original selected ledger validates.
        receipt=self.parent.learn_selected(adapter,before,after)
        latest=adapter.ledger[-1]
        cell=self.cells.setdefault(key,LocalProgressCells())
        cell.observe_selected(latest["action"],latest["reward"])
        return receipt

    def checkpoint(self):
        if len(self.cells)>MAX_REWARD_CONTEXTS:
            raise ValueError("MG49_CONTEXT_CAP")
        rewards={}
        for key,cell in self.cells.items():
            if (type(key) is not str or len(key)!=64 or
                any(c not in "0123456789abcdef" for c in key) or
                type(cell) is not LocalProgressCells):
                raise ValueError("MG49_CONTEXT_INVALID")
            if any(type(n) is not int or n<0 or n>4096 for n in cell.count):
                raise ValueError("MG49_COUNT_INVALID")
            if any(not math.isfinite(s) or abs(s)>n
                   for n,s in zip(cell.count,cell.reward_sum)):
                raise ValueError("MG49_REWARD_INVALID")
            rewards[key]={"count":cell.count,"reward_sum":cell.reward_sum}
        state={"schema":MG49_SCHEMA,
               "parent":self.parent.checkpoint().decode("utf-8"),
               "rewards":rewards}
        raw=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(raw)>MAX_CHECKPOINT:
            raise ValueError("MG49_CHECKPOINT_CAP")
        return raw

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_CHECKPOINT:
                raise ValueError("MG49_BAD_SIZE")
            wire=json.loads(raw)
            if type(wire) is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("MG49_BAD_ENVELOPE")
            state=wire["state"]
            if (type(state) is not dict or
                set(state)!={"schema","parent","rewards"} or
                state["schema"]!=MG49_SCHEMA or
                type(state["parent"]) is not str or
                type(state["rewards"]) is not dict or
                hashlib.sha256(canonical(state)).hexdigest()!=wire["sha256"]):
                raise ValueError("MG49_BAD_DIGEST")
            parent=SelectedChangeCells.restore(state["parent"].encode("utf-8"))
            obj=cls(parent=parent)
            if len(state["rewards"])>MAX_REWARD_CONTEXTS:
                raise ValueError("MG49_BAD_CONTEXT_CAP")
            for key,row in state["rewards"].items():
                if (type(key) is not str or len(key)!=64 or
                    any(c not in "0123456789abcdef" for c in key) or
                    type(row) is not dict or set(row)!={"count","reward_sum"} or
                    type(row["count"]) is not list or
                    type(row["reward_sum"]) is not list or
                    len(row["count"])!=7 or len(row["reward_sum"])!=7):
                    raise ValueError("MG49_BAD_REWARD_ROW")
                cell=LocalProgressCells()
                if any(type(n) is not int or not 0<=n<=4096 for n in row["count"]):
                    raise ValueError("MG49_BAD_COUNT")
                if any(type(s) not in (int,float) or not math.isfinite(s) or abs(s)>n
                       for n,s in zip(row["count"],row["reward_sum"])):
                    raise ValueError("MG49_BAD_REWARD")
                cell.count=list(row["count"])
                cell.reward_sum=list(row["reward_sum"])
                obj.cells[key]=cell
            if obj.checkpoint()!=raw:
                raise ValueError("MG49_NONCANONICAL")
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as exc:
            raise ValueError("MG49_UNTRUSTED_CHECKPOINT") from exc
