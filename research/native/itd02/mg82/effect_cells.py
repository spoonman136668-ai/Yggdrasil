"""MG82: native pre-reward, source-selected public action/effect local cells.

This is an action-conditioned observable-effect learner, not proven causality.
No model-generated privileged state, reward credit, environment stepping, map,
scripted route, or language/token network. The inherited MG28 parent is frozen.
"""
from __future__ import annotations
import hashlib
import json
from research.native.itd02.mg28.selected_change_cells import SelectedChangeCells
from research.native.itd02.mg23.selected_target_cells import observed_key
from research.native.itd02.mg19.original_mission_cells import (
    OriginalMissionAdapter, original_public)
from research.native.itd02.r10.public_adapter import canonical, digest

SCHEMA = "yggdrasil.itd02.mg82.selected-public-action-effect.v1"
MAX_CONTEXTS = 4096
MAX_SAMPLES = 4096
MAX_CHECKPOINT = 9000000
MIN_NO_EFFECT = 2
MODES = ("effect", "count")

def empty():
    return [{"count": 0, "changed": 0} for _ in range(7)]

class PublicEffectCells:
    def __init__(self, parent=None, mode="effect"):
        if mode not in MODES or type(mode) is not str:
            raise ValueError("MG82_MODE_INVALID")
        self.parent = SelectedChangeCells() if parent is None else parent
        if type(self.parent) is not SelectedChangeCells:
            raise ValueError("MG82_PARENT_INVALID")
        self.mode = mode
        self.cells = {}

    @property
    def samples(self):
        return self.parent.samples

    def _valid(self):
        if (type(self.cells) is not dict or len(self.cells)>MAX_CONTEXTS
            or not 0<=self.samples<=MAX_SAMPLES or self.mode not in MODES):
            raise ValueError("MG82_CONTEXT_OR_SAMPLE_CAP")
        count=0
        for key,row in self.cells.items():
            if (type(key) is not str or len(key)!=64
                or any(ch not in "0123456789abcdef" for ch in key)
                or type(row) is not list or len(row)!=7):
                raise ValueError("MG82_CONTEXT_INVALID")
            for item in row:
                if (type(item) is not dict or set(item)!={"count","changed"}
                    or type(item["count"]) is not int
                    or type(item["changed"]) is not int
                    or not 0<=item["changed"]<=item["count"]<=MAX_SAMPLES):
                    raise ValueError("MG82_EFFECT_ROW_INVALID")
                count+=item["count"]
        if count!=self.samples:
            raise ValueError("MG82_SELECTED_SOURCE_COUNT_MISMATCH")
        self.parent._valid()

    def start_session(self, adapter, name, live=False):
        self._valid()
        if type(adapter) is not OriginalMissionAdapter:
            raise ValueError("MG82_SOURCE_ADAPTER_REQUIRED")
        return self.parent.start_session(adapter,name,live=live)

    def choose(self, before):
        self._valid()
        original_public(before)
        base=self.parent.choose(before)
        if (type(base) is not dict or type(base.get("action")) is not int
            or base["action"] not in range(7)
            or base.get("external_fallback") is not False):
            raise ValueError("MG82_NATIVE_PARENT_PROPOSAL_INVALID")
        key=observed_key(before)
        row=self.cells.get(key)
        if row is None:
            return base
        proposed=base["action"]
        stat=row[proposed]
        if stat["count"]<MIN_NO_EFFECT:
            return base
        # Effect learner holds a source-supported action while it has caused
        # ANY actual public change; it explores only after learned stalling.
        if self.mode=="effect" and stat["changed"]>0:
            return base
        if self.mode=="effect":
            # Optimistic action-conditioned public effect from own selected
            # outcomes. No lookahead, reward, scripted action or stage oracle.
            score=lambda a: ((row[a]["changed"]+1)*4096//(row[a]["count"]+2)
                             +4096//(row[a]["count"]+1))
        else:
            # Active ablation sees the same selected source action counts,
            # but cannot inspect next-public changed/not-changed evidence.
            score=lambda a: -row[a]["count"]
        best=max((a for a in range(7) if a!=proposed),
                 key=lambda a: (score(a),-a))
        if score(best)<=score(proposed):
            return base
        return {"schema": SCHEMA, "action": best,
                "status": ("MG82_SELECTED_PUBLIC_EFFECT_EXPLORE" if self.mode=="effect"
                           else "MG82_COUNT_ONLY_EXPLORE"),
                "external_fallback": False}

    def learn_selected(self, adapter, before, after):
        self._valid()
        original_public(before)
        original_public(after)
        if (type(adapter) is not OriginalMissionAdapter
            or adapter.pending is not None or adapter.current!=after
            or not adapter.ledger or before["mission"]!=after["mission"]):
            raise ValueError("MG82_NOT_COMPLETED_ORIGINAL_SELECTION")
        event=adapter.ledger[-1]
        if (event["before_sha"]!=digest(before)
            or event["after_sha"]!=digest(after)
            or type(event["action"]) is not int
            or event["action"] not in range(7)):
            raise ValueError("MG82_SELECTED_SOURCE_DIGEST_MISMATCH")
        key=observed_key(before)
        if (self.samples>=MAX_SAMPLES or
            key not in self.cells and len(self.cells)>=MAX_CONTEXTS):
            raise ValueError("MG82_SELECTED_CAP")
        prior=self.samples
        receipt=self.parent.learn_selected(adapter,before,after)
        if self.samples!=prior+1:
            raise ValueError("MG82_PARENT_SAMPLE_CONSERVATION")
        row=self.cells.setdefault(key,empty())[event["action"]]
        row["count"]+=1
        if event["before_sha"]!=event["after_sha"]:
            row["changed"]+=1
        self._valid()
        return receipt

    def checkpoint(self):
        self._valid()
        state={"schema":SCHEMA,"mode":self.mode,"cells":self.cells,
               "parent":self.parent.checkpoint().decode("utf-8")}
        blob=canonical({"state":state,
                        "sha256":hashlib.sha256(canonical(state)).hexdigest()})
        if len(blob)>MAX_CHECKPOINT:
            raise ValueError("MG82_CHECKPOINT_CAP")
        return blob

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_CHECKPOINT:
                raise ValueError("MG82_CHECKPOINT_BYTES")
            wire=json.loads(raw)
            if type(wire) is not dict or set(wire)!={"state","sha256"}:
                raise ValueError("MG82_CHECKPOINT_FIELDS")
            state=wire["state"]
            if (type(state) is not dict
                or set(state)!={"schema","mode","cells","parent"}
                or state["schema"]!=SCHEMA
                or type(state["mode"]) is not str or state["mode"] not in MODES
                or type(state["parent"]) is not str
                or hashlib.sha256(canonical(state)).hexdigest()!=wire["sha256"]):
                raise ValueError("MG82_CHECKPOINT_DIGEST")
            obj=cls(SelectedChangeCells.restore(state["parent"].encode("utf-8")),
                    mode=state["mode"])
            obj.cells=state["cells"]
            obj._valid()
            if obj.checkpoint()!=raw:
                raise ValueError("MG82_NONCANONICAL_CHECKPOINT")
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as e:
            raise ValueError("MG82_UNTRUSTED_NATIVE_CHECKPOINT") from e
