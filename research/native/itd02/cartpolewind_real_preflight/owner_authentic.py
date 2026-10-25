"""Source-owner *synthetic-only* transport fixture.

The original upstream CartPoleWind and core modules ARE imported here solely
inside the isolated source-owner container. No environment construction,
reset, step, episode or model training is authorized.
"""
import json
import os
import pathlib
import socket
import sys

import importlib
import hashlib
import types
import gymnasium as gym

ORIGINAL_DIR = pathlib.Path("/sealed/upstream/causal_gym")
ORIGINAL_CARTPOLE_BLOB = "d65a6a31941709dc9201259d80dd4ebbcf48b4fa"


def git_blob(path):
    blob = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(blob)).encode("ascii") + b"\0" + blob).hexdigest()


def load_authenticated_original_classes():
    source = ORIGINAL_DIR / "envs" / "cartpole_wind.py"
    require(source.is_file(), "UPSTREAM_CARTPOLE_SOURCE_NOT_PRESENT")
    require(git_blob(source) == ORIGINAL_CARTPOLE_BLOB, "UPSTREAM_CARTPOLE_GIT_BLOB_DRIFT")
    # Force the import-only boundary: even accidental env construction through
    # module-level code must abort before any original Gym environment exists.
    def deny_gym_make(*args, **kwargs):
        raise RuntimeError("ORIGINAL_GYM_ENV_CONSTRUCTION_DENIED_BY_FROZEN_GATE")
    gym.make = deny_gym_make
    # Original root/envs __init__.py eagerly imports many unrelated external
    # domains; do NOT execute those. This only supplies package namespaces;
    # both core and cartpole_wind.py below are UNCHANGED original source.
    for name, path in (("causal_gym", ORIGINAL_DIR),
                       ("causal_gym.envs", ORIGINAL_DIR / "envs")):
        p = types.ModuleType(name)
        p.__path__ = [str(path)]
        p.__package__ = name
        sys.modules[name] = p
    from causal_gym.core import SCM, PCH, Task, Graph
    orig = importlib.import_module("causal_gym.envs.cartpole_wind")
    require(orig.CartPoleWindSCM.__module__ == "causal_gym.envs.cartpole_wind",
            "AUTHENTIC_SCM_CLASS_NOT_IMPORTED")
    require(orig.CartPoleWindPCH.__module__ == "causal_gym.envs.cartpole_wind",
            "AUTHENTIC_PCH_CLASS_NOT_IMPORTED")
    require(issubclass(orig.CartPoleWindSCM, SCM),
            "AUTHENTIC_CORE_SCM_INHERITANCE_FAILED")
    require(issubclass(orig.CartPoleWindPCH, PCH),
            "AUTHENTIC_CORE_PCH_INHERITANCE_FAILED")
    require(orig.Task is Task and orig.Graph is Graph,
            "AUTHENTIC_ORIGINAL_CORE_IDENTITY_DRIFT")
    require("causal_gym.envs.cartpole_wind" in sys.modules,
            "UPSTREAM_MODULE_NOT_REGISTERED")
    print("CARTPOLEWIND_AUTHENTIC_ORIGINAL_MODULE_IMPORTED=PASS", flush=True)
    print("CARTPOLEWIND_ORIGINAL_GYM_ENV_CONSTRUCTION_GUARDED=PASS",flush=True)


SOURCE = pathlib.Path("/sealed/source_original.py")
PRIVATE = pathlib.Path("/sealed/private_canary.txt")
MAX_LINES = 24
MAX_BYTES = 2048
PUBLIC_FIELDS = frozenset(("observation", "reward", "terminated", "truncated"))


def require(cond, reason):
    if not cond:
        raise RuntimeError("SOURCE_OWNER_DENIED:" + reason)


def initialize():
    require(os.geteuid() != 0, "ROOT_FORBIDDEN")
    require(SOURCE.is_file() and PRIVATE.is_file(), "ORIGINAL_SOURCE_OR_CANARY_MISSING")
    require(b"class CartPoleWindSCM" in SOURCE.read_bytes(), "ORIGINAL_PINNED_SOURCE_IDENTITY")
    require(PRIVATE.read_text(encoding="ascii").strip() ==
            "PRIVATE_CARTPOLEWIND_CANARY_DO_NOT_EXPOSE", "PRIVATE_CANARY_DRIFT")
    load_authenticated_original_classes()
    require("causal_gym.envs.cartpole_wind" in sys.modules,
            "UPSTREAM_AUTHENTIC_IMPORT_NOT_AVAILABLE")


def response(message):
    # Any malformed, introspective, extra-key or privileged method is denied.
    if not isinstance(message, dict):
        return {"error": "DENIED"}
    if message == {"op": "health"}:
        return {"protocol": "synthetic-owner-wire-v1", "status": "ready",
                "original_imports": 1, "original_episodes": 0, "protected_first_use": False}
    if (set(message) == {"op", "action"} and message["op"] == "probe" and
            type(message["action"]) is int and message["action"] in (0, 1)):
        # Demonstrate protocol only; these are NOT real CartPole transitions.
        return {"observation": [0.1, -0.2, 0.0, 0.05],
                "reward": 0.0, "terminated": False, "truncated": False}
    if message == {"op": "quit"}:
        return {"status": "bye", "original_episodes": 0}
    return {"error": "DENIED"}


def main():
    initialize()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 8765))
        sock.listen(1)
        sock.settimeout(20)
        conn, addr = sock.accept()
        with conn:
            conn.settimeout(10)
            inp, out = conn.makefile("rb"), conn.makefile("wb")
            for _ in range(MAX_LINES):
                line = inp.readline(MAX_BYTES + 1)
                if not line:
                    break
                if len(line) > MAX_BYTES:
                    break
                try:
                    message = json.loads(line.decode("utf-8"))
                except (ValueError, UnicodeError):
                    message = None
                result = response(message)
                require(result.keys() == PUBLIC_FIELDS or
                        result.keys() <= {"error", "status", "protocol", "original_imports",
                                           "original_episodes", "protected_first_use"},
                        "UNEXPECTED_WIRE_OUTPUT")
                out.write((json.dumps(result, sort_keys=True, allow_nan=False) + "\n").encode("ascii"))
                out.flush()
                if message == {"op": "quit"}:
                    break
    require("causal_gym.envs.cartpole_wind" in sys.modules,
            "ORIGINAL_SOURCE_IMPORT_WAS_LOST")
    print("CARTPOLEWIND_OWNER_SEPARATE_PROCESS=PASS", flush=True)
    print("CARTPOLEWIND_ORIGINAL_MODULE_IMPORTS=1", flush=True)
    print("CARTPOLEWIND_ORIGINAL_ENV_EPISODES=0", flush=True)
    print("CARTPOLEWIND_SCIENTIFIC_GO=FALSE", flush=True)


if __name__ == "__main__":
    main()
