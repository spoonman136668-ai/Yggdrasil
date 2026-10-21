"""NCI-04G7A: model-independent simulated local consequence custody.

Unlike G7 model-emitted pseudo-labels, the next bit is computed in a separate
source-pinned environment process with NO candidate or control weights. It is
still source-free SIMULATION, not a genuinely external physical observation.
The candidate sees the same one-hop sender transition as conventional controls.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from .developmental import N
from .nci04g6_native_credit import NativeSurvivorCredit

ENV_SOURCE="scripts/nci04g7a_environment.py"

class BoundedLocalEnvironment:
    __slots__=("root","credit")
    def __init__(self,root,runtime):
        self.root=pathlib.Path(root).resolve()
        self.credit=NativeSurvivorCredit(runtime)

    def source_receipt(self):
        src=self.root/ENV_SOURCE
        if src.is_symlink() or not src.is_file():
            raise ValueError("environment source unavailable")
        before=src.read_bytes()
        process=subprocess.run(["git","show","HEAD:"+ENV_SOURCE],
            cwd=self.root,capture_output=True,timeout=10,check=True)
        if process.stdout!=before:
            raise ValueError("uncommitted environment source")
        commit=subprocess.run(["git","rev-parse","HEAD"],cwd=self.root,
            capture_output=True,timeout=10,check=True).stdout.decode().strip()
        if len(commit)!=40 or any(c not in "0123456789abcdef" for c in commit):
            raise ValueError("invalid environment commit identity")
        return {"source_commit":commit,
                "environment_sha256":hashlib.sha256(before).hexdigest(),
                "provenance":"EXACT_GIT_NATIVE_SIMULATED_ENVIRONMENT",
                "external_sensor_attestation":False}

    def observe(self,prior,action,recipient,from_cell,sequence):
        rt=self.credit.adapter.runtime
        if (type(prior) not in (list,tuple) or len(prior)!=N or
            any(type(b)!=int or b not in (0,1) for b in prior)):
            raise ValueError("invalid source-free prior")
        if (type(recipient)!=int or type(from_cell)!=int or
            not 0<=recipient<N or not 0<=from_cell<N or
            rt.neighbors!=tuple(((i-1)%N,(i+1)%N) for i in range(N)) or
            from_cell not in rt.neighbors[recipient] or from_cell in rt.damaged or
            recipient not in rt.damaged):
            raise ValueError("unknown topology or nonlocal receipt")
        if type(action)!=int or action not in (0,1):
            raise ValueError("invalid action")
        if type(sequence)!=int or not 0<=sequence<=65535:
            raise ValueError("sequence outside native bounded envelope")
        proof=self.source_receipt()
        request=json.dumps({"prior":list(prior),"action":action,
                            "sender":from_cell,"damaged":recipient},
                           separators=(",",":"))
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",PYTHONNOUSERSITE="1")
        start=time.process_time_ns()
        p=subprocess.run([sys.executable,"-B",ENV_SOURCE],cwd=self.root,
            input=request,encoding="utf-8",capture_output=True,timeout=10,
            check=True,env=env)
        parent_cpu=time.process_time_ns()-start
        records=p.stdout.splitlines()
        if len(records)!=1:
            raise ValueError("unexpected environment output")
        observed=json.loads(records[0])
        if (type(observed)!=dict or
            set(observed)!={"schema","sender","damaged","action",
                            "observed_sender_next_bit","source"} or
            observed["schema"]!="yggdrasil.nci04g7a.native-world.v1" or
            observed["source"]!="SOURCE_PINNED_SIMULATED_ENVIRONMENT_NOT_EXTERNAL_SENSOR" or
            observed["sender"]!=from_cell or observed["damaged"]!=recipient or
            observed["action"]!=action or
            type(observed["observed_sender_next_bit"])!=int or
            observed["observed_sender_next_bit"] not in (0,1)):
            raise ValueError("invalid environment measurement identity")
        measured=observed["observed_sender_next_bit"]
        other=(from_cell-1)%N if (from_cell+1)%N==recipient else (from_cell+1)%N
        if measured!=(prior[from_cell]^prior[other]^action):
            raise ValueError("source-birth rule mismatch or tampered measurement")
        local=(prior[from_cell],prior[(from_cell-1)%N],prior[(from_cell+1)%N])
        before=rt.snapshot()
        wire=self.credit.observe_own_transition(recipient,from_cell,local,measured,sequence)
        receipt=self.credit.adapter.verify(wire,before)
        if receipt["own_next_bit"]!=measured:
            raise ValueError("end-to-end local custody mismatch")
        return wire,{"producer":proof,"measured_sender_next_bit":measured,
                     "action":action,"observed_world":"DETERMINISTIC_SIMULATED_CAUSAL_TRANSITION",
                     "external_sensor":False,"postlesion_damaged_target_labels":0,
                     "wire_bytes":len(wire),"parent_process_cpu_ns":parent_cpu}
