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
    # The owner may construct EXACTLY one real source environment but must
    # fail closed before any reset/step, seed, data or reward can be sampled.
    original_gym_make = gym.make
    from gymnasium.envs.classic_control.cartpole import CartPoleEnv
    def deny_reset(self, *args, **kwargs):
        COUNTS["resets"] += 1
        raise RuntimeError("UNAUTHORIZED_ORIGINAL_RESET")
    def deny_step(self, *args, **kwargs):
        COUNTS["steps"] += 1
        raise RuntimeError("UNAUTHORIZED_ORIGINAL_STEP")
    CartPoleEnv.reset = deny_reset
    CartPoleEnv.step = deny_step
    def constructor_only_make(env_id, *args, **kwargs):
        require(env_id == "CartPole-v1", "FORBIDDEN_ENV_ID")
        require(not args and kwargs == {"render_mode": None},
                "CONSTRUCTOR_KEYWORD_DRIFT")
        require(COUNTS["constructors"] == 0, "SECOND_ENV_CONSTRUCTOR")
        COUNTS["constructors"] += 1
        return original_gym_make(env_id, **kwargs)
    gym.make = constructor_only_make
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
    # Use the unchanged original CartPoleWindSCM.__init__ (not a simulator).
    # Any accidental source reset or step is blocked before dynamics execute.
    original_reset, original_step = orig.CartPoleWindSCM.reset, orig.CartPoleWindSCM.step
    def deny_source_reset(self, *args, **kwargs):
        COUNTS["source_resets"] += 1
        raise RuntimeError("UNAUTHORIZED_ORIGINAL_SCM_RESET")
    def deny_source_step(self, *args, **kwargs):
        COUNTS["source_steps"] += 1
        raise RuntimeError("UNAUTHORIZED_ORIGINAL_SCM_STEP")
    orig.CartPoleWindSCM.reset = deny_source_reset
    orig.CartPoleWindSCM.step = deny_source_step
    original = orig.CartPoleWindSCM(
        max_episode_steps=200, wind_mean=0.0, wind_std=0.01,
        init_theta_mean=0.0, init_theta_std=0.0, render_mode=None)
    require(type(original).__module__ == "causal_gym.envs.cartpole_wind",
            "CONSTRUCTED_OBJECT_WRONG_MODULE")
    require(original.max_episode_steps == 200 and original._elapsed_steps == 0,
            "UNEXPECTED_SOURCE_HORIZON")
    require(original.current_wind is None, "SOURCE_WIND_ALREADY_SAMPLED")
    require(original.action_space.n == 2 and tuple(original.observation_space.shape) == (4,),
            "CARTPOLE_SOURCE_PUBLIC_ACTION_OBS_SHAPE_DRIFT")
    require(original._env.unwrapped.state is None,
            "GYM_STATE_WAS_RESET_OR_SAMPLED")
    require(COUNTS == {"constructors": 1, "resets": 0, "steps": 0,
                       "source_resets": 0, "source_steps": 0},
            "SOURCE_EPISODE_ACTIVITY_DETECTED")
    original.close()
    require(COUNTS["resets"] == 0 and COUNTS["steps"] == 0
            and COUNTS["source_resets"] == 0 and COUNTS["source_steps"] == 0,
            "CONSTRUCTOR_CLOSE_TRIGGERED_EPISODE")
    print("CARTPOLEWIND_AUTHENTIC_ORIGINAL_MODULE_IMPORTED=PASS",flush=True)
    print("CARTPOLEWIND_ORIGINAL_ENV_CONSTRUCTOR_ONLY=PASS",flush=True)
    print("CARTPOLEWIND_ORIGINAL_RESET_STEP_DENIED=PASS",flush=True)
    print("CARTPOLEWIND_ORIGINAL_CONSTRUCTORS=1",flush=True)


COUNTS = {"constructors": 0, "resets": 0, "steps": 0,
          "source_resets": 0, "source_steps": 0}

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
                "original_imports": 1, "original_constructors": COUNTS["constructors"],
                "original_resets": COUNTS["resets"] + COUNTS["source_resets"],
                "original_steps": COUNTS["steps"] + COUNTS["source_steps"],
                "original_episodes": 0, "protected_first_use": False}
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
                                           "original_episodes", "original_constructors",
                                           "original_resets", "original_steps",
                                           "protected_first_use"},
                        "UNEXPECTED_WIRE_OUTPUT")
                out.write((json.dumps(result, sort_keys=True, allow_nan=False) + "\n").encode("ascii"))
                out.flush()
                if message == {"op": "quit"}:
                    break
    require("causal_gym.envs.cartpole_wind" in sys.modules,
            "ORIGINAL_SOURCE_IMPORT_WAS_LOST")
    print("CARTPOLEWIND_OWNER_SEPARATE_PROCESS=PASS", flush=True)
    require(COUNTS == {"constructors": 1, "resets": 0, "steps": 0,
                       "source_resets": 0, "source_steps": 0},
            "ORIGINAL_EPISODE_CONSUMED")
    print("CARTPOLEWIND_ORIGINAL_MODULE_IMPORTS=1", flush=True)
    print("CARTPOLEWIND_ORIGINAL_CONSTRUCTORS=1", flush=True)
    print("CARTPOLEWIND_ORIGINAL_RESET_STEP_CALLS=0", flush=True)
    print("CARTPOLEWIND_ORIGINAL_ENV_EPISODES=0", flush=True)
    print("CARTPOLEWIND_SCIENTIFIC_GO=FALSE", flush=True)


if __name__ == "__main__":
    main()
