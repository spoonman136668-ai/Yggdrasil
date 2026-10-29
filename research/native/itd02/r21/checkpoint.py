"""R21 bounded SHA-authenticated nested local original selected-source custody."""
import hashlib,json
from research.native.itd02.r10.public_adapter import canonical
from research.native.itd02.r20.state_credit_cells import StateCreditCells
from research.native.itd02.r21.local_consequence_cells import (
    LocalConsequenceCells,SCHEMA,MAX_CHECKPOINT
)
def checkpoint(agent):
    agent._valid()
    state={"schema":SCHEMA,"parent":agent.parent.checkpoint().decode(),
           "local":agent.local}
    wire=canonical({"state":state,"sha256":hashlib.sha256(canonical(state)).hexdigest()})
    if len(wire)>MAX_CHECKPOINT:raise ValueError("R21_CHECKPOINT_LIMIT")
    return wire
def restore(blob):
    try:
        if type(blob)is not bytes or not 0<len(blob)<=MAX_CHECKPOINT:
            raise ValueError("R21_UNTRUSTED_CHECKPOINT_SIZE")
        wire=json.loads(blob)
        if type(wire)is not dict or set(wire)!={"state","sha256"}:
            raise ValueError("R21_UNTRUSTED_ENVELOPE")
        state=wire["state"]
        if (type(state)is not dict or set(state)!={"schema","parent","local"}
            or state["schema"]!=SCHEMA or type(state["local"])is not dict
            or hashlib.sha256(canonical(state)).hexdigest()!=wire["sha256"]):
            raise ValueError("R21_UNTRUSTED_SOURCE_HASH")
        parent=StateCreditCells.restore(state["parent"].encode())
        result=LocalConsequenceCells(parent)
        result.local=state["local"];result._valid()
        if checkpoint(result)!=blob:
            raise ValueError("R21_NONCANONICAL_SOURCE")
        return result
    except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as e:
        raise ValueError("R21_UNTRUSTED_CHECKPOINT") from e
