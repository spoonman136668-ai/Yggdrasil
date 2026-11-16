#!/usr/bin/env python3
"""QTR-01 F50 independently admitted development evaluator transport.

The client side never imports the target law. First use is only possible after
an external owner verifier explicitly releases a world, prior to worker spawn.
CI MUST NOT supply approval. Owner verification must include exact-source CI,
real source checkpoint custody, once-only use, and authority. The ticket is
an interlock, NOT cryptographic proof or an OS security boundary.
"""
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import json
import os
from pathlib import Path
import subprocess
import sys

import f50_worlds as world

SCHEMA = "yggdrasil.qtr01.f50.development-process-transport.v1"
ALLOWED = frozenset((
    "hello", "public_candidates", "heldout_inputs_for_prediction",
    "public_event", "score_once", "public_receipt", "shutdown",
))
MAX_FRAME = 1024 * 1024
RESPONSE_TIMEOUT_SECONDS = 120


class DevelopmentTransportRejected(RuntimeError):
    pass


def _validated_release(size, seed, ticket):
    if (type(size) is not int or size not in (4096, 2048, 1024)
        or type(seed) is not int or seed not in (4013, 4057, 4099)
        or type(ticket) is not dict
        or set(ticket) != {"candidate_sha", "ubuntu_pass", "windows_pass",
                           "protocol_blob", "operator_first_use"}
        or type(ticket["candidate_sha"]) is not str
        or len(ticket["candidate_sha"]) != 40
        or any(c not in "0123456789abcdef" for c in ticket["candidate_sha"])
        or ticket["protocol_blob"] != "4bd3c4e0d3de0e3910094e38c14a0141c97ad380"
        or ticket["ubuntu_pass"] is not True
        or ticket["windows_pass"] is not True
        or ticket["operator_first_use"] is not True):
        raise DevelopmentTransportRejected("F50_DEV_FIRST_USE_BLOCKED")
    return ticket["candidate_sha"]


def _work():
    # Import of evaluator and causal rule stays EXCLUSIVELY in child process.
    import f50_worlds as world
    from f50_target_evaluator import PrivateTargetEvaluator

    world.freeze()
    evaluator = None
    next_seq = 1
    for line in sys.stdin:
        if len(line) > MAX_FRAME:
            return 2
        try:
            request = json.loads(line)
            if (type(request) is not dict
                or set(request) != {"schema", "seq", "method", "args"}
                or request["schema"] != SCHEMA
                or type(request["seq"]) is not int
                or request["seq"] != next_seq
                or type(request["method"]) is not str
                or request["method"] not in ALLOWED
                or type(request["args"]) is not dict):
                raise DevelopmentTransportRejected("F50_RPC_REQUEST_INVALID")
            method, args = request["method"], request["args"]
            if method == "hello":
                if evaluator is not None or set(args) != {"size", "seed", "ticket"}:
                    raise DevelopmentTransportRejected("F50_RPC_INVALID_ADMISSION")
                admitted_sha = _validated_release(
                    args["size"], args["seed"], args["ticket"])
                evaluator = PrivateTargetEvaluator.open_development(
                    args["size"], args["seed"],
                    externally_verified_release=args["ticket"])
                value = {"worker_pid": os.getpid(), "fixture_only": False,
                         "development_first_use": "EXTERNALLY_ADMITTED",
                         "source_candidate_sha": admitted_sha,
                         "target_law_disclosed": False,
                         "frozen_prereg_blob": world.PREREG_BLOB}
            elif evaluator is None:
                raise DevelopmentTransportRejected("F50_DEV_RPC_UNADMITTED")
            elif method == "public_candidates":
                if args:
                    raise DevelopmentTransportRejected("F50_RPC_INVALID_ARGS")
                value = evaluator.public_candidates()
            elif method == "public_event":
                if set(args) != {"index", "trajectory"}:
                    raise DevelopmentTransportRejected("F50_RPC_INVALID_ARGS")
                value = evaluator.public_event(
                    args["index"], args["trajectory"])
            elif method == "heldout_inputs_for_prediction":
                if args:
                    raise DevelopmentTransportRejected("F50_RPC_INVALID_ARGS")
                r = evaluator.public_receipt()
                if (r["public_events_used"] not in (16, 32, 64)
                    or r["public_events_used"] in r["scored_checkpoints"]):
                    raise DevelopmentTransportRejected("F50_RPC_HELDOUT_CHECKPOINT_FENCE")
                value = evaluator.heldout_inputs_for_prediction()
            elif method == "score_once":
                if set(args) != {"probabilities"}:
                    raise DevelopmentTransportRejected("F50_RPC_INVALID_ARGS")
                value = evaluator.score_once(args["probabilities"])
            elif method == "public_receipt":
                if args:
                    raise DevelopmentTransportRejected("F50_RPC_INVALID_ARGS")
                value = evaluator.public_receipt()
            else:
                if args:
                    raise DevelopmentTransportRejected("F50_RPC_INVALID_ARGS")
                value = {"closed": True}
            frame = {"schema": SCHEMA, "seq": next_seq, "ok": True,
                     "value": value}
        except (Exception,) as exc:
            # No error details or target law, signature, or truth leave worker.
            frame = {"schema": SCHEMA, "seq": next_seq,
                     "ok": False, "error": "F50_RPC_DENIED"}
            # No exception detail logged on the child's public stdout/stderr.
        print(json.dumps(frame, sort_keys=True, separators=(",", ":"),
                         allow_nan=False), flush=True)
        next_seq += 1
        if frame["ok"] and method == "shutdown":
            return 0
    return 0


class DevelopmentEvaluatorClient:
    """Whitelisted client. Owner verifier must approve before construction."""

    __slots__ = ("_proc", "_reader", "_next_seq", "_closed", "_hello")

    def __init__(self, size, seed, ticket=None, *, verified_by_owner=None):
        source_sha = _validated_release(size, seed, ticket)
        if (not callable(verified_by_owner)
            or verified_by_owner(size, seed, ticket) is not True):
            raise DevelopmentTransportRejected("F50_DEV_OWNER_ADMISSION_REQUIRED")
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONHASHSEED"] = "0"
        self._proc = subprocess.Popen(
            [sys.executable, "-u", str(Path(__file__).resolve()), "--admitted-worker"],
            cwd=str(Path(__file__).resolve().parent),
            env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, encoding="utf-8", bufsize=1)
        self._reader = ThreadPoolExecutor(max_workers=1)
        self._next_seq, self._closed, self._hello = 1, False, None
        try:
            value = self._rpc("hello", {"size": size, "seed": seed, "ticket": ticket})
            if (type(value) is not dict or value.get("fixture_only") is not False
                or value.get("target_law_disclosed") is not False
                or value.get("development_first_use") != "EXTERNALLY_ADMITTED"
                or value.get("source_candidate_sha") != source_sha
                or value.get("frozen_prereg_blob") != world.PREREG_BLOB
                or value.get("worker_pid") == os.getpid()):
                raise DevelopmentTransportRejected("F50_RPC_UNSAFE_WORKER")
            self._hello = value
        except Exception:
            self.close()
            raise

    @property
    def candidate_sha(self):
        return self._hello["source_candidate_sha"]

    @property
    def worker_pid(self):
        return self._hello["worker_pid"]

    def _rpc(self, method, args=None):
        if (self._closed or method not in ALLOWED or type(method) is not str
            or (method == "hello" and self._next_seq != 1)):
            raise DevelopmentTransportRejected("F50_RPC_METHOD_BLOCKED")
        request = {"schema": SCHEMA, "seq": self._next_seq,
                   "method": method, "args": {} if args is None else args}
        try:
            payload = json.dumps(request, sort_keys=True, separators=(",", ":"),
                                 allow_nan=False)
            if len(payload) > MAX_FRAME:
                raise DevelopmentTransportRejected("F50_RPC_TOO_LARGE")
            self._proc.stdin.write(payload + "\n")
            self._proc.stdin.flush()
            frame = self._reader.submit(self._proc.stdout.readline).result(
                timeout=RESPONSE_TIMEOUT_SECONDS)
            if not frame:
                raise DevelopmentTransportRejected("F50_RPC_WORKER_STOPPED")
            response = json.loads(frame)
            if (type(response) is not dict
                or response.get("schema") != SCHEMA
                or response.get("seq") != self._next_seq
                or type(response.get("ok")) is not bool):
                raise DevelopmentTransportRejected("F50_RPC_RESPONSE_INVALID")
            self._next_seq += 1
            if not response["ok"]:
                raise DevelopmentTransportRejected("F50_RPC_DENIED")
            if set(response) != {"schema", "seq", "ok", "value"}:
                raise DevelopmentTransportRejected("F50_RPC_RESPONSE_EXTRA_FIELDS")
            return response["value"]
        except FutureTimeout as exc:
            self._proc.kill()
            raise DevelopmentTransportRejected("F50_RPC_WORKER_TIMEOUT") from exc
        except (OSError, BrokenPipeError, ValueError, TypeError) as exc:
            raise DevelopmentTransportRejected("F50_RPC_IO_OR_FRAME_INVALID") from exc

    def public_candidates(self):
        return tuple(tuple(row) for row in self._rpc("public_candidates"))

    def heldout_inputs_for_prediction(self):
        return tuple(tuple(row) for row in self._rpc(
            "heldout_inputs_for_prediction"))

    def public_event(self, index, trajectory):
        return tuple(self._rpc("public_event",
                               {"index": index, "trajectory": list(trajectory)}))

    def score_once(self, predictions):
        return self._rpc("score_once", {"probabilities": predictions})

    def public_receipt(self):
        return self._rpc("public_receipt")

    def close(self):
        if self._closed:
            return
        try:
            if self._proc.poll() is None:
                try:
                    self._rpc("shutdown")
                except Exception:
                    self._proc.kill()
                try:
                    self._proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._proc.kill()
                    self._proc.wait(timeout=5)
        finally:
            self._closed = True
            for stream in (self._proc.stdin, self._proc.stdout):
                if stream is not None:
                    stream.close()
            self._reader.shutdown(wait=False, cancel_futures=True)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, traceback):
        self.close()


if __name__ == "__main__":
    if sys.argv[1:] != ["--admitted-worker"]:
        raise SystemExit("F50_DEVELOPMENT_FIRST_USE_BLOCKED")
    raise SystemExit(_work())
