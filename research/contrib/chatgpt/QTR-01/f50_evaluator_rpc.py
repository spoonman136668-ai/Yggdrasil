#!/usr/bin/env python3
"""QTR-01 F50 isolated evaluator JSON-lines transport, strictly FIXTURE ONLY.

The client side never imports the private evaluator. The child interpreter
imports it only in --fixture-worker mode and constructs an independently
generated synthetic-law fixture (NOT F50 target-development seeds or laws).
This is engineering process isolation, not an OS privilege/security sandbox;
real DEV first-use has no route in this module.
"""
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
import json
import os
from pathlib import Path
import subprocess
import sys

SCHEMA = "yggdrasil.qtr01.f50.fixture-process-transport.v1"
ALLOWED = frozenset((
    "hello", "public_candidates", "heldout_inputs_for_prediction",
    "public_event", "score_once", "public_receipt", "shutdown",
))
MAX_FRAME = 1024 * 1024
RESPONSE_TIMEOUT_SECONDS = 120


class TransportRejected(RuntimeError):
    pass


def _fixture_law(world):
    # Synthetic mathematical fixture: NOT a development-target derivation.
    a, b, c = (world.leaf(i) for i in (0, 1, 2))
    context, lag1, lag2 = world.leaf(30), world.leaf(10), world.leaf(22)
    core = ("and", context, ("and", ("and", a, b), lag2))
    return ("xor", core, ("and", ("not", context), ("xor", c, lag1)))


def _fixture_inputs(world):
    used, groups = set(), []
    for lane in ("public", "heldout"):
        group = []
        for index in range(512):
            for nonce in range(1024):
                episode = world._trajectory(
                    "F50/isolated-synthetic-fixture/v1", 1024, 9949,
                    lane, index, nonce)
                if episode is not None and episode not in used:
                    used.add(episode)
                    group.append(episode)
                    break
            else:
                raise TransportRejected("F50_FIXTURE_INPUT_EXHAUSTION")
        groups.append(tuple(group))
    if len(used) != 1024:
        raise TransportRejected("F50_FIXTURE_INPUT_OVERLAP")
    return tuple(groups)


def _work():
    # Import of evaluator and causal rule stays EXCLUSIVELY in child process.
    import f50_worlds as world
    from f50_target_evaluator import PrivateTargetEvaluator

    world.freeze()
    public, heldout = _fixture_inputs(world)
    evaluator = PrivateTargetEvaluator.synthetic_fixture(
        1024, _fixture_law(world), public, heldout)
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
                raise TransportRejected("F50_RPC_REQUEST_INVALID")
            method, args = request["method"], request["args"]
            if method == "hello":
                if args:
                    raise TransportRejected("F50_RPC_INVALID_ARGS")
                value = {"worker_pid": os.getpid(), "fixture_only": True,
                         "development_first_use": "BLOCKED",
                         "target_law_disclosed": False,
                         "frozen_prereg_blob": world.PREREG_BLOB}
            elif method == "public_candidates":
                if args:
                    raise TransportRejected("F50_RPC_INVALID_ARGS")
                value = evaluator.public_candidates()
            elif method == "public_event":
                if set(args) != {"index", "trajectory"}:
                    raise TransportRejected("F50_RPC_INVALID_ARGS")
                value = evaluator.public_event(
                    args["index"], args["trajectory"])
            elif method == "heldout_inputs_for_prediction":
                if args:
                    raise TransportRejected("F50_RPC_INVALID_ARGS")
                r = evaluator.public_receipt()
                if (r["public_events_used"] not in (16, 32, 64)
                    or r["public_events_used"] in r["scored_checkpoints"]):
                    raise TransportRejected("F50_RPC_HELDOUT_CHECKPOINT_FENCE")
                value = evaluator.heldout_inputs_for_prediction()
            elif method == "score_once":
                if set(args) != {"probabilities"}:
                    raise TransportRejected("F50_RPC_INVALID_ARGS")
                value = evaluator.score_once(args["probabilities"])
            elif method == "public_receipt":
                if args:
                    raise TransportRejected("F50_RPC_INVALID_ARGS")
                value = evaluator.public_receipt()
            else:
                if args:
                    raise TransportRejected("F50_RPC_INVALID_ARGS")
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


class FixtureEvaluatorClient:
    """Whitelisted JSON-lines client. Hidden rule lives in child process only."""

    __slots__ = ("_proc", "_reader", "_next_seq", "_closed", "_hello")

    def __init__(self, *, mode="fixture"):
        if mode != "fixture":
            raise TransportRejected("F50_DEV_FIRST_USE_NOT_AUTHORIZED")
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONHASHSEED"] = "0"
        self._proc = subprocess.Popen(
            [sys.executable, "-u", str(Path(__file__).resolve()), "--fixture-worker"],
            cwd=str(Path(__file__).resolve().parent),
            env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, encoding="utf-8", bufsize=1)
        self._reader = ThreadPoolExecutor(max_workers=1)
        self._next_seq, self._closed, self._hello = 1, False, None
        try:
            value = self._rpc("hello")
            if (type(value) is not dict or value.get("fixture_only") is not True
                or value.get("target_law_disclosed") is not False
                or value.get("development_first_use") != "BLOCKED"
                or value.get("worker_pid") == os.getpid()):
                raise TransportRejected("F50_RPC_UNSAFE_WORKER")
            self._hello = value
        except Exception:
            self.close()
            raise

    @property
    def worker_pid(self):
        return self._hello["worker_pid"]

    def _rpc(self, method, args=None):
        if self._closed or method not in ALLOWED or type(method) is not str:
            raise TransportRejected("F50_RPC_METHOD_BLOCKED")
        request = {"schema": SCHEMA, "seq": self._next_seq,
                   "method": method, "args": {} if args is None else args}
        try:
            payload = json.dumps(request, sort_keys=True, separators=(",", ":"),
                                 allow_nan=False)
            if len(payload) > MAX_FRAME:
                raise TransportRejected("F50_RPC_TOO_LARGE")
            self._proc.stdin.write(payload + "\n")
            self._proc.stdin.flush()
            frame = self._reader.submit(self._proc.stdout.readline).result(
                timeout=RESPONSE_TIMEOUT_SECONDS)
            if not frame:
                raise TransportRejected("F50_RPC_WORKER_STOPPED")
            response = json.loads(frame)
            if (type(response) is not dict
                or response.get("schema") != SCHEMA
                or response.get("seq") != self._next_seq
                or type(response.get("ok")) is not bool):
                raise TransportRejected("F50_RPC_RESPONSE_INVALID")
            self._next_seq += 1
            if not response["ok"]:
                raise TransportRejected("F50_RPC_DENIED")
            if set(response) != {"schema", "seq", "ok", "value"}:
                raise TransportRejected("F50_RPC_RESPONSE_EXTRA_FIELDS")
            return response["value"]
        except FutureTimeout as exc:
            self._proc.kill()
            raise TransportRejected("F50_RPC_WORKER_TIMEOUT") from exc
        except (OSError, BrokenPipeError, ValueError, TypeError) as exc:
            raise TransportRejected("F50_RPC_IO_OR_FRAME_INVALID") from exc

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
    if sys.argv[1:] != ["--fixture-worker"]:
        raise SystemExit("F50_FIXTURE_WORKER_ONLY_NO_DEV_FIRST_USE")
    raise SystemExit(_work())
