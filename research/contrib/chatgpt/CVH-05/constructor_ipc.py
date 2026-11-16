"""CVH-05 parent-only exact original source custody handshake.

Parent process imports NO CausalGym classes, original SCM/PCH, hidden source
metadata, trainer or learner. It receives one exact public constructor-ready
acknowledgment from a distinct short-lived OS source process, then closes.
No public action, reward or world episode can be requested on this wire.

Engineering handshake, not a security sandbox against malicious same-user
processes, not a native controller, owner or first-use authorization.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from queue import Empty,Queue
import subprocess
import sys
from threading import Thread

HERE=Path(__file__).resolve().parent
CHILD=HERE/"source_child.py"
SCHEMA="cvh05.original-source-constructor-only.v1"
PIN="c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
REQUIRED_READY={"schema","kind","source_sha","source_blobs",
                "original_objects","source_actions","source_resets"}
REQUIRED_CLOSED={"schema","kind"}
MAX_BYTES=4096


class SourceCustodyError(RuntimeError):
    pass


def _frame(raw):
    if (type(raw) is not str or not raw.endswith("\n")
            or not 0<len(raw.encode("utf-8"))<=MAX_BYTES):
        raise SourceCustodyError("CVH05_INVALID_OR_OVERSIZED_PUBLIC_FRAME")
    try:
        obj=json.loads(raw)
    except (ValueError,TypeError) as e:
        raise SourceCustodyError("CVH05_PUBLIC_JSON_INVALID") from e
    if type(obj) is not dict:
        raise SourceCustodyError("CVH05_PUBLIC_JSON_NOT_OBJECT")
    return obj


def _validate_ready(message):
    if (type(message) is not dict or set(message)!=REQUIRED_READY
            or message.get("schema")!=SCHEMA or message.get("kind")!="ready"):
        raise SourceCustodyError("CVH05_NONPUBLIC_SOURCE_ACK")
    if (message.get("source_sha")!=PIN
            or type(message.get("source_blobs")) is not int
            or message["source_blobs"]!=16
            or type(message.get("original_objects")) is not int
            or message["original_objects"]!=1
            or type(message.get("source_resets")) is not int
            or message["source_resets"]!=0
            or type(message.get("source_actions")) is not int
            or message["source_actions"]!=0):
        raise SourceCustodyError("CVH05_ORIGINAL_SOURCE_CUSTODY_MISMATCH")
    return dict(message)


def _validate_closed(message):
    if (type(message) is not dict or set(message)!=REQUIRED_CLOSED
            or message.get("schema")!=SCHEMA or message.get("kind")!="closed"):
        raise SourceCustodyError("CVH05_SOURCE_NOT_CLOSED_CLEANLY")
    return True


class OriginalSourceConstructorSession:
    """Strict one-shot constructor-only real child, no original source action."""

    def __init__(self,checkout,*,timeout_seconds=15):
        if type(timeout_seconds) not in (int,float) or not 0<timeout_seconds<=30:
            raise ValueError("CVH05_TIMEOUT_UNSAFE")
        self.checkout=Path(checkout).expanduser()
        self.timeout=float(timeout_seconds)
        self.proc=None
        self.closed=False
        self.public_ready=None
        self.pid=None

    def _read(self):
        if self.proc is None or self.proc.stdout is None:
            raise SourceCustodyError("CVH05_SOURCE_PROCESS_ABSENT")
        q=Queue(maxsize=1)
        def receive():
            try:q.put((self.proc.stdout.readline(),None))
            except BaseException as e:q.put(("",e))
        Thread(target=receive,daemon=True).start()
        try:
            raw,error=q.get(timeout=self.timeout)
        except Empty as e:
            self._terminate()
            raise SourceCustodyError("CVH05_SOURCE_CONSTRUCTOR_TIMEOUT_NO_RETRY") from e
        if error:
            self._terminate()
            raise SourceCustodyError("CVH05_SOURCE_PUBLIC_READ_ERROR") from error
        return _frame(raw)

    def __enter__(self):
        if self.closed or self.proc is not None:
            raise SourceCustodyError("CVH05_ALREADY_CONSUMED_SESSION")
        if any(k=="causal_gym" or k.startswith("causal_gym.") for k in sys.modules):
            raise SourceCustodyError("CVH05_PARENT_ORIGINAL_SOURCE_IMPORT_FORBIDDEN")
        # No import of original source into parent. Child independently
        # verifies exact Git SHA, original 16 blobs and pinned dependency pins.
        checkout=self.checkout.resolve(strict=True)
        if not checkout.is_dir():
            raise SourceCustodyError("CVH05_ORIGINAL_CHECKOUT_NOT_DIRECTORY")
        try:
            self.proc=subprocess.Popen(
                [sys.executable,"-I","-B","-u",str(CHILD),
                 "--constructor-only","--checkout",str(checkout)],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,encoding="utf-8",text=True,
                bufsize=1,close_fds=True,
            )
            self.pid=self.proc.pid
            if self.pid==os.getpid():
                raise SourceCustodyError("CVH05_SOURCE_NOT_SEPARATE_PROCESS")
            self.public_ready=_validate_ready(self._read())
            return self
        except BaseException:
            self._terminate()
            raise

    def _terminate(self):
        self.closed=True
        if self.proc is None:return
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

    def close(self):
        if self.closed:return
        if self.proc is None or self.public_ready is None:
            self._terminate()
            raise SourceCustodyError("CVH05_NO_ORIGINAL_SOURCE_HANDSHAKE")
        try:
            if self.proc.stdin is None:
                raise SourceCustodyError("CVH05_CLOSE_PIPE_UNAVAILABLE")
            self.proc.stdin.write(json.dumps(
                {"schema":SCHEMA,"kind":"close"},
                sort_keys=True,separators=(",",":"))+"\n")
            self.proc.stdin.flush()
            _validate_closed(self._read())
            self.proc.wait(timeout=self.timeout)
            if self.proc.returncode!=0:
                raise SourceCustodyError("CVH05_ORIGINAL_SOURCE_WORKER_EXIT_FAILED")
        except BaseException:
            self._terminate()
            raise
        finally:
            self._terminate()

    def public_receipt(self):
        if self.public_ready is None:
            raise SourceCustodyError("CVH05_NO_CUSTODY_RECEIPT")
        # Child PID is retained only for external engineering custody, and
        # must never be passed to native policy or its observe() input.
        proof=dict(self.public_ready)
        proof["source_process_isolated"]=self.pid!=os.getpid()
        proof["source_seed_first_use"]=False
        proof["original_source_action_executed"]=False
        proof["model_updated"]=False
        return proof

    def __exit__(self,kind,value,traceback):
        if kind is not None:
            self._terminate()
        else:
            self.close()
        return False


def run_checked_constructor(checkout,*,timeout_seconds=15):
    with OriginalSourceConstructorSession(checkout,timeout_seconds=timeout_seconds) as c:
        receipt=c.public_receipt()
    if c.proc is None or c.proc.poll()!=0 or not c.closed:
        raise SourceCustodyError("CVH05_NOT_CLOSED_AND_REAPED")
    return receipt


def identical_public_receipt_sha256(record):
    data=json.dumps(record,sort_keys=True,separators=(",",":"),
                    ensure_ascii=True,allow_nan=False).encode("ascii")
    return sha256(data).hexdigest()
