#!/usr/bin/env python3
"""QTR F17: Linux evaluator/learner isolation on PUBLIC development worlds.

Kernel Landlock limits learner filesystem access; seccomp rejects socket creation.
The evaluator alone imports causal_worlds. Strict IPC exposes only F14 public JSON.
Not a general sandbox, model-training run, protected first-use or science claim.
"""
import argparse
import ctypes
import errno
import json
import os
import platform
import resource
import select
import subprocess
import sys
from pathlib import Path

from f14_boundary import reset_frame, step_frame

UPSTREAM_SHA = "51f1431515e310dec72e3f4b6db378df46f832ea"
UPSTREAM_TREE = "c1bf53ecf03ae326b69c0321f4412d81f3122894"

WORKER_SOURCE = r'''
import json
import os
import socket
import sys

def denied(fn):
    try:
        fn()
    except (OSError, ImportError, PermissionError):
        return True
    return False

def process(request):
    if request.get("op") == "probe":
        paths = request["paths"]
        results = {
            "upstream_file_denied": denied(lambda: open(paths["source"], "rb").read(32)),
            "upstream_listing_denied": denied(lambda: os.listdir(paths["source_dir"])),
            "evaluator_source_denied": denied(lambda: open(paths["host"], "rb").read(32)),
            "network_socket_denied": denied(lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM)),
            "package_import_denied": denied(lambda: __import__("causal_worlds")),
        }
        return {"op": "probe", "results": results}
    if request.get("op") == "act":
        payload = json.loads(request["public_wire"])
        if set(payload) - {"observation", "reward", "done"}:
            raise ValueError("PRIVILEGED_KEY")
        values = payload["observation"]
        if not isinstance(values, list) or not values:
            raise ValueError("BAD_OBSERVATION")
        count = request["action_dim"]
        if type(count) is not int or not 1 <= count <= 16:
            raise ValueError("BAD_ACTION_DIMENSION")
        action = max(-1., min(1., .05 * sum(float(v) for v in values)))
        return {"op": "act", "action": [action] * count}
    raise ValueError("BAD_OPERATION")

for line in sys.stdin:
    try:
        response = process(json.loads(line))
    except Exception as exc:
        response = {"op": "error", "error": type(exc).__name__}
    sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n")
    sys.stdout.flush()
'''

# Landlock syscall IDs / seccomp syscall IDs are x86_64-specific.
SYS_LL_CREATE, SYS_LL_ADD, SYS_LL_RESTRICT = 444, 445, 446
PR_NO_NEW_PRIVS, PR_SECCOMP, MODE_FILTER = 38, 22, 2
LL_VERSION, LL_RULE_PATH = 1, 1
FS_RIGHTS_V1 = (1 << 13) - 1
READ_FILE, READ_DIR, EXECUTE = 1 << 2, 1 << 3, 1 << 0


class PathRule(ctypes.Structure):
    _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]


class Filter(ctypes.Structure):
    _fields_ = [("code", ctypes.c_ushort), ("jt", ctypes.c_ubyte),
                ("jf", ctypes.c_ubyte), ("k", ctypes.c_uint32)]


class FilterProgram(ctypes.Structure):
    _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.POINTER(Filter))]


def syscall(libc, num, *args):
    value = libc.syscall(num, *args)
    if value == -1:
        raise OSError(ctypes.get_errno(), os.strerror(ctypes.get_errno()))
    return value


def install_landlock(libc, python_home):
    abi = syscall(libc, SYS_LL_CREATE, ctypes.c_void_p(0), 0, LL_VERSION)
    if abi < 1:
        raise RuntimeError("F17_LANDLOCK_UNSUPPORTED")
    rights = FS_RIGHTS_V1
    if abi >= 2:
        rights |= 1 << 13  # REFER
    if abi >= 3:
        rights |= 1 << 14  # TRUNCATE
    if abi >= 5:
        rights |= 1 << 15  # IOCTL_DEV
    attributes = ctypes.c_uint64(rights)
    ruleset = syscall(libc, SYS_LL_CREATE, ctypes.byref(attributes),
                      ctypes.sizeof(attributes), 0)
    try:
        seen = set()
        # Source and evaluator checkout are NEVER in this read/execute allowlist.
        for candidate in (python_home, "/usr", "/lib", "/lib64", "/bin",
                          "/dev/null", "/dev/urandom"):
            path = os.path.realpath(candidate)
            if not os.path.exists(path) or path in seen:
                continue
            seen.add(path)
            allowed = (READ_FILE | READ_DIR | EXECUTE) if os.path.isdir(path) else READ_FILE
            parent_fd = os.open(path, os.O_PATH | os.O_CLOEXEC)
            try:
                rule = PathRule(allowed, parent_fd)
                syscall(libc, SYS_LL_ADD, ruleset, LL_RULE_PATH, ctypes.byref(rule), 0)
            finally:
                os.close(parent_fd)
        syscall(libc, SYS_LL_RESTRICT, ruleset, 0)
    finally:
        os.close(ruleset)


def install_seccomp(libc):
    # For a fresh process with ONLY stdin/stdout/stderr FDs, deny socket creation.
    # Also deny direct connect, including any unforeseen inherited socket FD.
    instructions = [(0x20, 0, 0, 0)]  # BPF LD syscall number
    for nr in (41, 42, 53):  # socket, connect, socketpair (Linux x86-64)
        instructions.append((0x15, 0, 1, nr))  # BPF JEQ skip denial if unequal
        instructions.append((0x06, 0, 0, 0x00050000 | errno.EPERM))
    instructions.append((0x06, 0, 0, 0x7fff0000))
    array = (Filter * len(instructions))(*[Filter(*x) for x in instructions])
    program = FilterProgram(len(instructions), array)
    if libc.prctl(PR_SECCOMP, MODE_FILTER, ctypes.byref(program), 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "F17_SECCOMP_NOT_INSTALLED")


def restrict_child(python_home):
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise RuntimeError("F17_WRONG_PLATFORM")
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    libc.prctl.restype = ctypes.c_int
    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    if libc.prctl(PR_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "F17_NO_NEW_PRIVS_FAILED")
    install_landlock(libc, python_home)
    install_seccomp(libc)


def verify_source(root):
    commit = subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"],
                                     text=True).strip()
    tree = subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD^{tree}"],
                                   text=True).strip()
    if (commit, tree) != (UPSTREAM_SHA, UPSTREAM_TREE):
        raise ValueError("F17_UPSTREAM_SOURCE_DRIFT")


def exchange(proc, payload):
    proc.stdin.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    proc.stdin.flush()
    ready, _, _ = select.select([proc.stdout], [], [], 8)
    if not ready:
        raise RuntimeError("F17_WORKER_TIMEOUT")
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("F17_WORKER_EXIT")
    answer = json.loads(line)
    if answer.get("op") != payload["op"]:
        raise RuntimeError("F17_BAD_WORKER_RESPONSE")
    return answer


def run(upstream, checkout):
    verify_source(upstream)
    import numpy as np
    from causal_worlds import worlds
    from causal_worlds.gym import ControlEnv

    base_python = os.path.realpath(sys._base_executable)
    python_home = os.path.realpath(sys.base_prefix)
    if not base_python.startswith(python_home + os.sep):
        raise RuntimeError("F17_PYTHON_BASE_MISMATCH")
    environment = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
                   "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1"}
    command = [base_python, "-I", "-S", "-B", "-c", WORKER_SOURCE]
    with subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, bufsize=1,
                          env=environment, cwd="/", close_fds=True,
                          preexec_fn=lambda: restrict_child(python_home)) as learner:
        try:
            probe = exchange(learner, {"op": "probe", "paths": {
                "source": os.path.join(upstream, "src", "causal_worlds", "worlds.py"),
                "source_dir": os.path.join(upstream, "src", "causal_worlds"),
                "host": os.path.join(checkout, "research", "contrib", "chatgpt",
                                     "QTR-01", "f14_boundary.py"),
            }})
            if set(probe["results"]) != {"upstream_file_denied", "upstream_listing_denied",
                                         "evaluator_source_denied", "network_socket_denied",
                                         "package_import_denied"} or not all(probe["results"].values()):
                raise RuntimeError("F17_LEAKAGE_NEGATIVE_CONTROL_FAIL")
            results = {}
            for name in ("coffee", "ecommerce"):
                env = ControlEnv(worlds.get(name), horizon=2)
                try:
                    wire = reset_frame(env.reset(seed=1701))
                    rewards = []
                    for _ in range(2):
                        reply = exchange(learner, {"op": "act", "public_wire": wire,
                                                    "action_dim": env.action_space.shape[0]})
                        action = reply.get("action")
                        if type(action) is not list or len(action) != env.action_space.shape[0]:
                            raise ValueError("F17_MALFORMED_ACTION")
                        if any(type(v) not in (int, float) or not -5 <= v <= 5
                               for v in action):
                            raise ValueError("F17_OUT_OF_RANGE_ACTION")
                        wire = step_frame(env.step(np.asarray(action, dtype=np.float64)))
                        packet = json.loads(wire)
                        if set(packet) != {"observation", "reward", "done"}:
                            raise ValueError("F17_PRIVILEGED_WIRE_FIELD")
                        rewards.append(packet["reward"])
                    if not json.loads(wire)["done"]:
                        raise ValueError("F17_MISSING_TERMINATION")
                    results[name] = {"public_actions": 2, "public_rewards": rewards}
                finally:
                    env.close()
            return {
                "schema": "yggdrasil.qtr.f17.dev.process-isolation.v1",
                "source_commit": UPSTREAM_SHA,
                "source_tree": UPSTREAM_TREE,
                "learner_is_a_separate_process": True,
                "landlock_read_boundary": True,
                "seccomp_network_socket_denied": True,
                "negative_probes": probe["results"],
                "published_dev_worlds_only": True,
                "scientific_first_use": False,
                "native_model_training": False,
                "general_untrusted_code_sandbox": False,
                "worlds": results,
                "classification": "DEV_BOUNDED_PROCESS_ISOLATION_PASS",
            }
        finally:
            learner.stdin.close()
            learner.kill()
            learner.wait(timeout=8)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path, required=True)
    parser.add_argument("--checkout-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(str(args.upstream_root.resolve()),
                         str(args.checkout_root.resolve())), sort_keys=True, indent=2))
