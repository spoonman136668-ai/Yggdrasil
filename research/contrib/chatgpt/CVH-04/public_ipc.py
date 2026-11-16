"""CVH-04 isolated public-action wire for source-free one-shot tests.

The existing CVH02 policy runs in this parent. A *separate OS process* owns
the toy source and any private mock state. Only six public outcome fields
cross back into the policy; no source module, object, world ID or hidden
label is provided to the policy. The child is intentionally a MOCK and
cannot start the true external CausalGym original environment.

This process separation is an engineering prototype, NOT an OS sandbox or
independently authorized first-use mechanism. Never use as a source owner,
persistent service, new controller or a real-world environment driver.
"""
from __future__ import annotations

from collections import namedtuple
from hashlib import sha256
import json
from pathlib import Path
from queue import Queue,Empty
import subprocess
import sys
from threading import Thread

HERE=Path(__file__).resolve().parent
SCHEMA="cvh04.public-event-wire.v1"
CHILD=HERE/"toy_source_child.py"
SEEDS=tuple(range(1,7))
MAX_ACTIONS=6
MAX_BYTES=4096
PUBLIC_FIELDS=("before","action","reward","after","terminated","truncated")
PublicConsequence=namedtuple("PublicConsequence",PUBLIC_FIELDS)
READY_KEYS={"schema","kind","before","mock_seed"}
EVENT_KEYS={"schema","kind","seq",*PUBLIC_FIELDS}


class SourceWireError(RuntimeError):
    pass


def _strict_binary(value):
    if type(value) is not int or value not in (0,1):
        raise SourceWireError("CVH04_NONPUBLIC_BINARY_FIELD")
    return value


def _strict_bool(value):
    if type(value) is not bool:
        raise SourceWireError("CVH04_NONPUBLIC_TERMINAL_FIELD")
    return value


def _parse_line(raw):
    if (type(raw) is not str or not raw.endswith("\n")
            or not 0<len(raw.encode("utf-8"))<=MAX_BYTES):
        raise SourceWireError("CVH04_INVALID_OR_OVERSIZE_PUBLIC_RECORD")
    try:
        obj=json.loads(raw)
    except (ValueError,TypeError) as e:
        raise SourceWireError("CVH04_PUBLIC_JSON_INVALID") from e
    if type(obj) is not dict:
        raise SourceWireError("CVH04_NONOBJECT_PUBLIC_MESSAGE")
    return obj


def _receipt_digest(rows):
    data=[r._asdict() for r in rows]
    raw=json.dumps(data,sort_keys=True,separators=(",",":"),
                   allow_nan=False,ensure_ascii=True).encode("ascii")
    return sha256(raw).hexdigest()


class ToySourceSession:
    """One toy episode, one private OS process, no original world actions."""

    def __init__(self,seed,*,fault="none",timeout_seconds=3.0):
        if type(seed) is not int or seed not in SEEDS:
            raise PermissionError("CVH04_ONLY_TOY_SEEDS_1_TO_6")
        if fault not in ("none","private","wrong_action","wrong_seq","stall"):
            raise ValueError("CVH04_UNKNOWN_TEST_FAULT")
        if type(timeout_seconds) not in (int,float) or not 0<timeout_seconds<=10:
            raise ValueError("CVH04_BAD_RECEIVE_TIMEOUT")
        self.seed=seed
        self.fault=fault
        self.timeout_seconds=float(timeout_seconds)
        self.proc=None
        self.state=None
        self.events=[]
        self.inflight=False
        self.closed=False
        self.worker_pid=None

    def __enter__(self):
        if self.closed or self.proc is not None:
            raise SourceWireError("CVH04_SOURCE_SESSION_ALREADY_USED")
        try:
            self.proc=subprocess.Popen(
                [sys.executable,"-I","-B","-u",str(CHILD),
                 "--mock-only","--toy-seed",str(self.seed),"--fault",self.fault],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                encoding="utf-8",text=True,
                bufsize=1,close_fds=True,
            )
            self.worker_pid=self.proc.pid
            msg=self._read()
            if (set(msg)!=READY_KEYS or msg["schema"]!=SCHEMA
                    or msg["kind"]!="ready" or type(msg["mock_seed"]) is not int
                    or msg["mock_seed"]!=self.seed):
                raise SourceWireError("CVH04_BAD_MOCK_READY")
            self.state=_strict_binary(msg["before"])
            return self
        except BaseException:
            self.close()
            raise

    def _read(self):
        if self.proc is None or self.proc.stdout is None:
            raise SourceWireError("CVH04_SOURCE_NOT_STARTED")
        q=Queue(maxsize=1)
        def receive():
            try:
                q.put((self.proc.stdout.readline(),None))
            except BaseException as e:
                q.put(("",e))
        worker=Thread(target=receive,daemon=True)
        worker.start()
        try:
            raw,error=q.get(timeout=self.timeout_seconds)
        except Empty as e:
            self.close()
            raise SourceWireError("CVH04_SOURCE_RESPONSE_TIMEOUT_NO_REPLAY") from e
        if error is not None:
            self.close()
            raise SourceWireError("CVH04_SOURCE_READ_FAILED_NO_REPLAY") from error
        return _parse_line(raw)

    def step(self,action):
        if self.closed or self.proc is None:
            raise SourceWireError("CVH04_SOURCE_ALREADY_CLOSED")
        if self.inflight:
            raise SourceWireError("CVH04_UNCERTAIN_EFFECT_IN_FLIGHT")
        if len(self.events)>=MAX_ACTIONS or (
                self.events and (self.events[-1].terminated
                                 or self.events[-1].truncated)):
            raise SourceWireError("CVH04_SOURCE_EPISODE_CLOSED")
        action=_strict_binary(action)
        seq=len(self.events)+1
        self.inflight=True
        try:
            request={"schema":SCHEMA,"kind":"act","seq":seq,"action":action}
            if self.proc.stdin is None:
                raise SourceWireError("CVH04_SOURCE_PIPE_UNAVAILABLE")
            self.proc.stdin.write(json.dumps(request,sort_keys=True,
                                             separators=(",",":"))+"\n")
            self.proc.stdin.flush()
            result=self._read()
            if set(result)!=EVENT_KEYS or result["schema"]!=SCHEMA or result["kind"]!="event":
                raise SourceWireError("CVH04_PRIVATE_OR_EXTRA_SOURCE_RECORD")
            if type(result["seq"]) is not int or result["seq"]!=seq:
                raise SourceWireError("CVH04_NONMONOTONIC_SOURCE_RECEIPT")
            for key in ("before","action","reward","after"):
                _strict_binary(result[key])
            for key in ("terminated","truncated"):
                _strict_bool(result[key])
            if (result["before"]!=self.state or result["action"]!=action
                    or (result["terminated"] and result["truncated"])):
                raise SourceWireError("CVH04_SOURCE_ACTION_OR_STATE_MISMATCH")
            if (seq==MAX_ACTIONS and not (result["terminated"] or result["truncated"])):
                raise SourceWireError("CVH04_MOCK_UNCLOSED_ACTION_BUDGET")
            row=PublicConsequence(*(result[k] for k in PUBLIC_FIELDS))
            self.events.append(row)
            self.state=row.after
            self.inflight=False
            return row
        except BaseException:
            # A selected action might already have occurred inside the child.
            # Close and never retry, reissue or infer an outcome from a timeout.
            self.close()
            raise

    def drive(self,policy):
        if not callable(getattr(policy,"choose",None)) or (
                not callable(getattr(policy,"observe",None))):
            raise ValueError("CVH04_ONLY_PUBLIC_CHOOSE_OBSERVE_POLICY")
        if self.closed or self.proc is None or self.events:
            raise SourceWireError("CVH04_DRIVE_REQUIRES_FRESH_SESSION")
        try:
            for _ in range(MAX_ACTIONS):
                action=policy.choose(self.state,tuple(self.events))
                row=self.step(action)
                policy.observe(row)
                if row.terminated or row.truncated:
                    break
            if not self.events or not self.events[-1].truncated:
                raise SourceWireError("CVH04_TOY_COMPLETION_NOT_OBSERVED")
            return {"schema":"cvh04.source-free-public-receipt.v1",
                    "mock_only":True,
                    "source_actions":0,
                    "mock_actions":len(self.events),
                    "toy_seed":self.seed,
                    "worker_pid":self.worker_pid,
                    "public_trace_sha256":_receipt_digest(self.events),
                    "public_events":[r._asdict() for r in self.events],
                    "forbidden_info_passed_to_policy":False,
                    "source_original_first_use":False}
        except BaseException:
            self.close()
            raise

    def close(self):
        self.closed=True
        if self.proc is not None:
            p=self.proc
            if p.poll() is None:
                try:p.terminate()
                except OSError:pass
            try:p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(timeout=2)
            for stream in (p.stdin,p.stdout):
                if stream is not None:
                    try:stream.close()
                    except OSError:pass

    def __exit__(self,exc_type,exc,traceback):
        self.close()
        return False
