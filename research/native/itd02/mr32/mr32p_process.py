"""Sanitized subprocess launcher for the MR32-P policy-only process."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


class PolicyProcessError(RuntimeError):
    pass


def _policy_environment() -> dict[str, str]:
    # Do not inherit evaluator state, CI secrets, task targets, PYTHONPATH,
    # home-directory config, or arbitrary variables into the policy process.
    allowed = (
        "PATH", "SYSTEMROOT", "WINDIR", "SYSTEMDRIVE",
        "TEMP", "TMP", "PATHEXT", "COMSPEC",
    )
    return {key: os.environ[key] for key in allowed if key in os.environ}


def invoke_policy(message: dict, timeout_seconds: int = 10) -> dict:
    if not isinstance(message, dict):
        raise PolicyProcessError("PUBLIC_MESSAGE_MUST_BE_OBJECT")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int):
        raise PolicyProcessError("TIMEOUT_MUST_BE_INTEGER")
    if not 1 <= timeout_seconds <= 30:
        raise PolicyProcessError("TIMEOUT_RANGE")
    script = Path(__file__).with_name("mr32p_policy.py")
    raw = json.dumps(
        message, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    )
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            input=raw,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            env=_policy_environment(),
        )
    except subprocess.TimeoutExpired as exc:
        raise PolicyProcessError("POLICY_PROCESS_TIMEOUT") from exc
    if result.returncode != 0:
        raise PolicyProcessError(
            f"POLICY_PROCESS_REJECTED:{result.stderr.strip()}"
        )
    try:
        output = json.loads(result.stdout)
    except Exception as exc:
        raise PolicyProcessError("POLICY_PROCESS_INVALID_JSON") from exc
    if not isinstance(output, dict):
        raise PolicyProcessError("POLICY_PROCESS_OUTPUT_NOT_OBJECT")
    return output
