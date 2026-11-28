"""Experimental retained local truth-slot transfer, not production R7.

Prior world is learned from completed public outcomes. A cold authenticated
snapshot restores the four separate local cells. The new world is assumed
EITHER to preserve each slot or invert all of them uniformly; the hypothesis
is a testable prior, never supplied as a target regime identity.
"""
import hashlib
import json
from unrestricted_operation_cells import INPUTS, UnrestrictedMessageCells

class RetainedCellTransfer:
    def __init__(self, source=None):
        self.source=source if source is not None else UnrestrictedMessageCells()
        self.modes={False,True}
        self.new_observations=0
        self.contradiction=False

    def train_source(self,inputs,outcome):
        if self.new_observations:
            raise ValueError("SOURCE_FROZEN")
        self.source.observe(inputs,outcome)

    def observe_new(self,inputs,outcome):
        self.source.check(inputs)
        if type(outcome) is not bool:
            raise ValueError("PUBLIC_OUTCOME_REQUIRED")
        before=self.source.predict(inputs)
        if before is None:
            raise ValueError("SOURCE_EVIDENCE_INSUFFICIENT")
        self.modes={flip for flip in self.modes if (before ^ flip)==outcome}
        self.new_observations+=1
        if not self.modes:self.contradiction=True

    def predict(self,inputs):
        self.source.check(inputs)
        prior=self.source.predict(inputs)
        if prior is None or not self.modes or self.new_observations==0:
            return None
        votes={prior ^ flip for flip in self.modes}
        return next(iter(votes)) if len(votes)==1 else None

    def checkpoint(self):
        body={"schema":"retained-local-transfer.v1",
              "source":[list(self.source.cells[x].counts) for x in INPUTS],
              "source_observations":self.source.observations,
              "modes":sorted(self.modes),
              "new_observations":self.new_observations,
              "contradiction":self.contradiction}
        raw=json.dumps(body,sort_keys=True,separators=(",",":")).encode()
        signed=json.dumps({"payload":body,"sha256":hashlib.sha256(raw).hexdigest()},
                          sort_keys=True,separators=(",",":")).encode()
        if len(signed)>4096:raise ValueError("SNAPSHOT_CAP")
        return signed

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or not 0<len(blob)<=4096:
            raise ValueError("INVALID_CHECKPOINT")
        data=json.loads(blob)
        if type(data) is not dict or set(data)!={"payload","sha256"}:
            raise ValueError("INVALID_FIELDS")
        body=data["payload"]
        raw=json.dumps(body,sort_keys=True,separators=(",",":")).encode()
        if hashlib.sha256(raw).hexdigest()!=data["sha256"]:
            raise ValueError("INVALID_CHECKSUM")
        if body.get("schema")!="retained-local-transfer.v1":
            raise ValueError("INVALID_SCHEMA")
        if (type(body.get("source")) is not list or len(body["source"])!=4
            or any(type(p) is not list or len(p)!=2
                   or any(type(n) is not int or n<0 or n>100000 for n in p)
                   for p in body["source"])):
            raise ValueError("INVALID_LOCAL_STATE")
        if (type(body.get("modes")) is not list or
            any(type(x) is not bool for x in body["modes"]) or
            len(set(body["modes"]))!=len(body["modes"]) or
            type(body.get("new_observations")) is not int or
            body["new_observations"]<0 or
            type(body.get("source_observations")) is not int or
            body["source_observations"]!=sum(sum(p) for p in body["source"]) or
            type(body.get("contradiction")) is not bool):
            raise ValueError("INVALID_COUNTS")
        result=cls()
        for key,counts in zip(INPUTS,body["source"]):
            result.source.cells[key].counts=counts
            result.source.cells[key].observations=sum(counts)
        result.source.observations=body["source_observations"]
        result.modes=set(body["modes"])
        result.new_observations=body["new_observations"]
        result.contradiction=body["contradiction"]
        return result
