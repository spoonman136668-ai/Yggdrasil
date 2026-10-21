"""NCI-04G5: a *stateless* cell-local sensory-residual observation seam.

No after-lesion target output, global post-lesion state or oracle function ID
is accepted. The *surviving cell's own* observed next bit may be supplied by
a local sensor stream; its authenticity beyond this native process remains a
separate integration obligation. No new routing weights or learned registry.

The fixed 38-byte wire record is observational evidence, NOT a diagnosis or
qualified functional-reconstruction message.
"""
import hashlib
import math
import struct
from .developmental import N, K, D, sig, softmax
from .task_runtime import LocalTaskRuntime

WIRE_FORMAT="!BBHbB32s"
WIRE_BYTES=struct.calcsize(WIRE_FORMAT)
assert WIRE_BYTES==38
MAX_SEQUENCE=65535

def valid_local(values):
    if type(values) not in (list,tuple) or len(values)!=3 or any(type(v)!=int or v not in (0,1) for v in values):
        raise ValueError("only three local, binary pre-transition sensors permitted")

def local_features(values):
    valid_local(values)
    center,left,right=(2*v-1 for v in values)
    return (1.,float(center),float(left),float(right),
            float(left*right),float(center*left),float(center*right))

class LocalResidualAdapter:
    """One-hop ephemeral adapter wrapping the existing native LocalTaskRuntime.

    No retained local credit or learned routing parameters: full persistent
    state and parameter budgets are unchanged. Delivery sequence/replay custody
    remains the responsibility of the native transport, not a hidden table.
    """
    __slots__=("runtime",)
    def __init__(self,runtime):
        if type(runtime) is not LocalTaskRuntime:
            raise TypeError("only original native task runtime accepted")
        self.runtime=runtime

    def emit(self, recipient, from_cell, local_prior, own_next_bit, sequence):
        valid_local(local_prior)
        if (type(recipient)!=int or type(from_cell)!=int or
            not 0<=recipient<N or not 0<=from_cell<N or
            from_cell not in self.runtime.neighbors[recipient]):
            raise ValueError("non-neighbor message rejected")
        if (recipient not in self.runtime.damaged or
            from_cell in self.runtime.damaged):
            raise ValueError("messages require damaged receiver and intact source")
        if type(own_next_bit)!=int or own_next_bit not in (0,1):
            raise ValueError("only local sensory transition admitted")
        if type(sequence)!=int or not 0<=sequence<=MAX_SEQUENCE:
            raise ValueError("invalid bounded sequence number")
        # Derive a prediction only from the source cell's own native learned
        # state and three local pre-transition bits, NEVER the damaged target.
        feat=local_features(local_prior)
        guesses=[sig(sum(w*v for w,v in zip(row,feat))) for row in self.runtime.core.genome]
        gate=softmax(self.runtime.core.roles[from_cell])
        prediction=sum(w*p for w,p in zip(gate,guesses))
        if not math.isfinite(prediction) or not 0<=prediction<=1:
            raise ValueError("invalid native local prediction")
        # Locally observed residual quantized in [-127,+127].
        residual=round(127*(own_next_bit-prediction))
        residual=max(-127,min(127,residual))
        source_digest=hashlib.sha256(self.runtime.snapshot().encode("utf-8")).digest()
        # 38 byte bounded wire: sender, recipient, sequence, signed residual,
        # OWN measured bit, full snapshot digest. No target labels or weights.
        return struct.pack(WIRE_FORMAT,from_cell,recipient,sequence,
                           residual,own_next_bit,source_digest)

    def verify(self,message,local_source_snapshot):
        if type(message)!=bytes or len(message)!=WIRE_BYTES:
            raise ValueError("invalid fixed-width message")
        if type(local_source_snapshot)!=str or len(local_source_snapshot)>65536:
            raise ValueError("invalid source snapshot")
        sender,recipient,sequence,residual,observed,digest=struct.unpack(WIRE_FORMAT,message)
        if (sender not in self.runtime.neighbors[recipient] or
            sender in self.runtime.damaged or recipient not in self.runtime.damaged or
            observed not in (0,1) or not -127<=residual<=127):
            raise ValueError("invalid local-message provenance")
        if hashlib.sha256(local_source_snapshot.encode("utf-8")).digest()!=digest:
            raise ValueError("source snapshot digest mismatch")
        # This validates source identity, not an externally attested sensor.
        return {"sender":sender,"recipient":recipient,"sequence":sequence,
                "signed_residual_i8":residual,"own_next_bit":observed,
                "evidence_basis":"native-neighbor-own-transition; stream-attestation-unproven"}
