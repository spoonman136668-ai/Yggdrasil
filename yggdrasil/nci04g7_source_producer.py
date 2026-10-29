"""NCI-04G7 — source-pinned, separate-process *native model* observation.

The sender's postlesion bit is NOT passed to this adapter. It is computed
inside a separate unmodified scripts/native_cells.py process, after bounded
prelesion training, then selected strictly for the intact local sender.

This certifies Git-source/process provenance of a model-emitted bit, not an
independently measured external cell or physical sensor. It is therefore
not an authentic real-world transition or accepted regeneration evidence.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from .cells import CELLS
from .nci04g6_native_credit import NativeSurvivorCredit

PRODUCER=("yggdrasil/cells.py","scripts/native_cells.py")
MAX_SOURCE_EVENTS=64
MAX_INPUT_BYTES=8192

class SourceBoundNativeCellSensor:
    __slots__=("root","credit")
    def __init__(self,root,runtime):
        p=pathlib.Path(root).resolve()
        if not (p/"scripts/native_cells.py").is_file():
            raise ValueError("native producer unavailable")
        self.root=p
        self.credit=NativeSurvivorCredit(runtime)

    def source_receipt(self):
        pinned={}
        for name in PRODUCER:
            path=self.root/name
            if path.is_symlink() or not path.is_file():
                raise ValueError("native source must be regular")
            committed=subprocess.run(["git","show","HEAD:"+name],
                cwd=self.root,capture_output=True,check=True,timeout=10).stdout
            current=path.read_bytes()
            if current.replace(b"\r\n", b"\n") != committed.replace(b"\r\n", b"\n"):
                raise ValueError("native producer source/commit mismatch")
            pinned[name]=hashlib.sha256(committed).hexdigest()
        commit=subprocess.run(["git","rev-parse","HEAD"],cwd=self.root,
            capture_output=True,check=True,timeout=10).stdout.decode().strip()
        if len(commit)!=40 or any(ch not in "0123456789abcdef" for ch in commit):
            raise ValueError("invalid source commit")
        return {"commit":commit,"git_source_sha256":pinned,
                "attestation":"EXACT_LOCAL_GIT_SOURCE_NOT_EXTERNAL_SENSOR"}

    @staticmethod
    def valid_bits(bits):
        if type(bits) not in (list,tuple) or len(bits)!=CELLS or any(type(x)!=int or x not in (0,1) for x in bits):
            raise ValueError("only eight locally bounded binary values")

    def observe_native_source(self,recipient,from_cell,bit_history,current_bits,sequence):
        """Return a SOURCE-produced bounded message, never a passed next bit.

        bit_history contains SOURCE-FREE development observations made before
        lesion only. It must not contain postlesion target labels. There is no
        live external sensor attestation: the bit comes from native prediction.
        """
        self.valid_bits(current_bits)
        if type(bit_history) not in (list,tuple) or not 1<=len(bit_history)<=MAX_SOURCE_EVENTS:
            raise ValueError("prelesion experience budget exceeded")
        native=self.credit.adapter.runtime
        if native.neighbors!=tuple(((i-1)%CELLS,(i+1)%CELLS) for i in range(CELLS)):
            raise ValueError("native ring producer cannot attest custom graph topology")
        if (type(recipient)!=int or type(from_cell)!=int
            or not 0<=recipient<CELLS or not 0<=from_cell<CELLS
            or from_cell not in native.neighbors[recipient]
            or from_cell in native.damaged or recipient not in native.damaged):
            raise ValueError("unqualified one-hop source")
        events=[]
        for pair in bit_history:
            if type(pair) not in (tuple,list) or len(pair)!=2:
                raise ValueError("invalid prelesion source experience")
            bits,outcome=pair
            self.valid_bits(bits);self.valid_bits(outcome)
            events.append({"op":"observe","bits":list(bits),"consequences":list(outcome)})
        events.append({"op":"lesion","cell":recipient})
        events.append({"op":"predict","bits":list(current_bits)})
        payload="\n".join(json.dumps(x,separators=(",",":")) for x in events)+"\n"
        if len(payload.encode())>MAX_INPUT_BYTES:
            raise ValueError("source input budget exceeded")
        receipt=self.source_receipt()
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",PYTHONNOUSERSITE="1")
        start=time.process_time_ns()
        run=subprocess.run([sys.executable,"-B","scripts/native_cells.py"],
            input=payload,encoding="utf-8",capture_output=True,cwd=self.root,
            env=env,timeout=12,check=True)
        elapsed_parent_cpu=time.process_time_ns()-start
        rows=run.stdout.splitlines()
        if len(rows)!=1:
            raise ValueError("unexpected native producer output")
        obj=json.loads(rows[0])
        if type(obj)!=dict or set(obj)!={"probabilities"}:
            raise ValueError("unexpected native prediction")
        probabilities=obj["probabilities"]
        if type(probabilities)!=list or len(probabilities)!=CELLS or any(
            type(p) not in (float,int) or not 0<=p<=1 for p in probabilities
        ):
            raise ValueError("invalid native model probabilities")
        own_model_bit=int(probabilities[from_cell]>=.5)
        prior=(current_bits[from_cell],
               current_bits[(from_cell-1)%CELLS],
               current_bits[(from_cell+1)%CELLS])
        native_before=self.credit.adapter.runtime.snapshot()
        msg=self.credit.observe_own_transition(
            recipient,from_cell,prior,own_model_bit,sequence)
        if self.credit.adapter.verify(msg,native_before)["own_next_bit"]!=own_model_bit:
            raise ValueError("native output/learning custody mismatch")
        return msg,{"producer":receipt,
                    "origin":"INTERNAL_NATIVE_MODEL_EMITTED_PSEUDO_OBSERVATION",
                    "not_externally_observed":True,
                    "own_model_probability":probabilities[from_cell],
                    "own_model_bit":own_model_bit,
                    "parent_cpu_ns_excludes_child":elapsed_parent_cpu,
                    "actual_message_bytes":len(msg),
                    "postlesion_true_target_labels":0}
