"""Authenticated R20 source-conditioned credit checkpoint."""
import hashlib
import json
from research.native.itd02.r10.public_adapter import canonical
from research.native.itd02.r18.mission_cells import MissionCells
from research.native.itd02.r20.state_credit_cells import (
    StateCreditCells,SCHEMA,MAX_CHECKPOINT
)

def checkpoint(agent):
    agent._valid()
    state={"schema":SCHEMA,"parent":agent.parent.checkpoint().decode(),
           "states":agent.states}
    raw=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
    if len(raw)>MAX_CHECKPOINT:raise ValueError("R20_SNAPSHOT_BUDGET")
    return raw

def restore(blob):
    try:
        if type(blob)is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
            raise ValueError("R20_RESTORE_SIZE")
        wire=json.loads(blob)
        if type(wire)is not dict or set(wire)!={"state","sha256"}:
            raise ValueError("R20_SOURCE_ENVELOPE")
        state=wire["state"]
        if (type(state)is not dict or set(state)!={"schema","parent","states"}
            or state["schema"]!=SCHEMA
            or hashlib.sha256(canonical(state)).hexdigest()!=wire["sha256"]
            or type(state["states"])is not dict):
            raise ValueError("R20_SOURCE_CHECKSUM")
        parent=MissionCells.restore(state["parent"].encode())
        model=StateCreditCells(parent);model.states=state["states"]
        model._valid()
        if checkpoint(model)!=blob:raise ValueError("R20_SOURCE_NONCANONICAL")
        return model
    except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as e:
        raise ValueError("R20_UNTRUSTED_CHECKPOINT") from e
