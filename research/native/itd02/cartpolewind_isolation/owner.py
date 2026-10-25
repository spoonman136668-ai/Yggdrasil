"""Source-owner *synthetic-only* transport fixture.

Original upstream CartPoleWind source exists in this image ONLY as inert data.
No import of its code; no environment construction; reset/step forbidden.
"""
import json
import os
import pathlib
import socket
import sys

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
    require("causal_gym" not in sys.modules, "UPSTREAM_IMPORT_FORBIDDEN")


def response(message):
    # Any malformed, introspective, extra-key or privileged method is denied.
    if not isinstance(message, dict):
        return {"error": "DENIED"}
    if message == {"op": "health"}:
        return {"protocol": "synthetic-owner-wire-v1", "status": "ready",
                "original_imports": 0, "original_episodes": 0, "protected_first_use": False}
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
    require("causal_gym" not in sys.modules, "ORIGINAL_SOURCE_IMPORTED")
    print("CARTPOLEWIND_OWNER_SEPARATE_PROCESS=PASS", flush=True)
    print("CARTPOLEWIND_ORIGINAL_MODULE_IMPORTS=0", flush=True)
    print("CARTPOLEWIND_ORIGINAL_ENV_EPISODES=0", flush=True)
    print("CARTPOLEWIND_SCIENTIFIC_GO=FALSE", flush=True)


if __name__ == "__main__":
    main()
