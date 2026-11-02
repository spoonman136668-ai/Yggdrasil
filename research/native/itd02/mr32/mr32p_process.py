"""Sanitized JSON-lines launcher for the MR32-P policy-only subprocess."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


class PolicyProcessError(RuntimeError):
    pass


def _policy_script() -> Path:
    return Path(__file__).with_name("mr32p_policy.py")


def _policy_environment() -> dict[str, str]:
    # No evaluator state, credentials, PYTHONPATH, home config or task secrets.
    allowed = (
        "PATH", "SYSTEMROOT", "WINDIR", "SYSTEMDRIVE",
        "TEMP", "TMP", "PATHEXT", "COMSPEC",
    )
    return {key: os.environ[key] for key in allowed if key in os.environ}


def _encode(message: dict) -> str:
    if not isinstance(message, dict):
        raise PolicyProcessError("PUBLIC_MESSAGE_MUST_BE_OBJECT")
    try:
        return json.dumps(
            message, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        )
    except Exception as exc:
        raise PolicyProcessError("PUBLIC_MESSAGE_SERIALIZATION") from exc


def _decode(line: str) -> dict:
    try:
        output = json.loads(line)
    except Exception as exc:
        raise PolicyProcessError("POLICY_PROCESS_INVALID_JSON") from exc
    if not isinstance(output, dict):
        raise PolicyProcessError("POLICY_PROCESS_OUTPUT_NOT_OBJECT")
    if "error" in output:
        raise PolicyProcessError("POLICY_PROCESS_REJECTED:" + str(output["error"]))
    return output


class PolicySession:
    """One persistent child; caller supplies exactly one public message per step."""
    def __init__(self, timeout_seconds: int = 30):
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int):
            raise PolicyProcessError("TIMEOUT_MUST_BE_INTEGER")
        if not 1 <= timeout_seconds <= 120:
            raise PolicyProcessError("TIMEOUT_RANGE")
        self.timeout_seconds = timeout_seconds
        self.process = subprocess.Popen(
            [sys.executable, str(_policy_script())],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=_policy_environment(),
        )
        self.closed = False

    def request(self, message: dict) -> dict:
        if self.closed or self.process.poll() is not None:
            raise PolicyProcessError("POLICY_SESSION_NOT_RUNNING")
        if self.process.stdin is None or self.process.stdout is None:
            raise PolicyProcessError("POLICY_SESSION_PIPES_UNAVAILABLE")
        payload = _encode(message)
        try:
            self.process.stdin.write(payload + "\n")
            self.process.stdin.flush()
            line = self.process.stdout.readline()
        except Exception as exc:
            raise PolicyProcessError("POLICY_SESSION_IO") from exc
        if not line:
            stderr = ""
            if self.process.stderr is not None:
                try:
                    stderr = self.process.stderr.read()
                except Exception:
                    pass
            raise PolicyProcessError(
                "POLICY_SESSION_EOF:" + stderr.strip()
            )
        return _decode(line)

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        if self.process.stdin is not None:
            try:
                self.process.stdin.close()
            except Exception:
                pass
        timed_out = False
        try:
            self.process.wait(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            self.process.kill()
            self.process.wait()
        stderr = ""
        returncode = self.process.returncode
        if returncode != 0 and self.process.stderr is not None:
            try:
                stderr = self.process.stderr.read()
            except Exception:
                pass
        for stream in (self.process.stdout, self.process.stderr):
            if stream is not None:
                try:
                    stream.close()
                except Exception:
                    pass
        if timed_out:
            raise PolicyProcessError("POLICY_SESSION_CLOSE_TIMEOUT")
        if returncode != 0:
            raise PolicyProcessError(
                "POLICY_SESSION_EXIT:" + str(returncode) + ":" + stderr.strip()
            )

    def __enter__(self) -> "PolicySession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def invoke_policy(message: dict, timeout_seconds: int = 10) -> dict:
    """One-message convenience path used by isolated boundary tests."""
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int):
        raise PolicyProcessError("TIMEOUT_MUST_BE_INTEGER")
    if not 1 <= timeout_seconds <= 30:
        raise PolicyProcessError("TIMEOUT_RANGE")
    try:
        result = subprocess.run(
            [sys.executable, str(_policy_script())],
            input=_encode(message),
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
    lines = result.stdout.splitlines()
    if len(lines) != 1:
        raise PolicyProcessError("POLICY_PROCESS_RESPONSE_COUNT")
    return _decode(lines[0])
