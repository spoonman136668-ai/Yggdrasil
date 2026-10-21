"""NCI-04G7F: one-bit native functional witness retained across lesion.

An intact target cell produces its own native response to ONE frozen probe.
Two adjacent surviving cells retain a bounded one-bit categorization and
presence marker in the common mode of their EXISTING three role logits.
Uniform shifts leave softmax routing invariant, if all coefficients remain
within the original [-20,20] envelope.

This is a model-output witness, NOT environmental task correctness, a learned
full-function copy, a transferable function, or independently authenticated
science. No more than one static-probe bit is recoverable; all other queries
MUST abstain. The pre-lesion observer must be invoked while the target lives.
"""
from dataclasses import dataclass
import hashlib
import math
import pathlib
import subprocess

from .developmental import K, N, valid, softmax
from .task_runtime import LocalTaskRuntime
from .nci04g7d_native_lesion import NativeNeighborLesionObserver

# Frozen, task-local observation only. No caller-selected probe / task answer.
PROBE = (1, 1, 0, 0, 0, 0, 0, 0)
BIT_ZERO = -0.75
BIT_ONE = 0.75
MARKER = 1.25
TOL = 1e-5
MODULE = "yggdrasil/nci04g7f_retained_witness.py"


@dataclass(frozen=True)
class WitnessReceipt:
    source_commit: str
    target: int
    left: int
    right: int
    retained_bit: int
    kind: str = "NATIVE_MODEL_OUTPUT_NOT_EXTERNAL_TASK_TRUTH"


@dataclass(frozen=True)
class WitnessReadout:
    status: str
    bit: int | None
    evidence_basis: str = "TWO_SURVIVING_NATIVE_ROLE_COMMON_MODES"
    complete_function_recovery: bool = False


def _pin_sources(runtime, root):
    observer = NativeNeighborLesionObserver(runtime, root)
    commit, _ = observer._source_receipt()
    path = pathlib.Path(root).resolve(strict=True)
    current = (path / MODULE).read_bytes()
    immutable = subprocess.run(
        ["git", "show", commit + ":" + MODULE], cwd=path,
        capture_output=True, check=True, timeout=10).stdout
    if current != immutable or not current:
        raise ValueError("native witness implementation source drift")
    return commit


def _mean(values):
    return sum(values) / K


def _encoded_role(values, common):
    mean = _mean(values)
    revised = [v - mean + common for v in values]
    if (any(not math.isfinite(x) or abs(x) > 20 for x in revised) or
            any(abs(p-q) > 1e-12 for p,q in
                zip(softmax(values), softmax(revised)))):
        raise ValueError("fixed native coefficient or invariant exceeded")
    return revised


def retain_native_probe(runtime, root, target):
    """Sample target's OWN native response, place one bit in local survivors.

    No target parameter, label, function ID, or observed bit is supplied by
    caller. Inputs that need extra capacity or ambiguous role framing fail
    before changing native state.
    """
    if type(runtime) is not LocalTaskRuntime:
        raise TypeError("requires original LocalTaskRuntime")
    if type(target) is not int or not 0 <= target < N or runtime.damaged:
        raise ValueError("must witness an intact native target")
    if K != 3 or N != 8:
        raise ValueError("unqualified native role budget")
    valid(PROBE)
    left, right = runtime.neighbors[target]
    if (left == right or target not in runtime.neighbors[left] or
            target not in runtime.neighbors[right]):
        raise ValueError("local bidirectional neighbor ownership missing")
    commit = _pin_sources(runtime, root)
    # Conservative integration boundary: no loss of pre-existing common mode
    # is silently authorized. Valid learned role DIFFERENCES are retained.
    for i in (left, right):
        role = runtime.core.roles[i]
        if (len(role) != K or any(not math.isfinite(v) for v in role) or
                abs(_mean(role)) > 0.25):
            raise ValueError("cannot reuse occupied native common mode")
    observed_response = runtime.component(PROBE, target)
    if not math.isfinite(observed_response):
        raise ValueError("nonfinite target native response")
    bit = int(observed_response >= 0.5)
    first = _encoded_role(runtime.core.roles[left], BIT_ONE if bit else BIT_ZERO)
    second = _encoded_role(runtime.core.roles[right], MARKER)
    # All checks above precede any state mutation. No learned coefficients
    # or additional fields are added to the existing genome / role layout.
    runtime.core.roles[left] = first
    runtime.core.roles[right] = second
    return WitnessReceipt(commit, target, left, right, bit)


def read_retained_probe(runtime, target, probe=PROBE):
    """After damage, read ONLY role common modes; otherwise abstain."""
    if type(runtime) is not LocalTaskRuntime:
        raise TypeError("requires original LocalTaskRuntime")
    if type(target) is not int or not 0 <= target < N:
        raise ValueError("invalid native target")
    valid(probe)
    if tuple(probe) != PROBE:
        return WitnessReadout("ABSTAIN_UNSEEN_PROBE", None)
    if target not in runtime.damaged:
        return WitnessReadout("ABSTAIN_TARGET_NOT_DAMAGED", None)
    left, right = runtime.neighbors[target]
    if (target not in runtime.neighbors[left] or
            target not in runtime.neighbors[right] or
            left in runtime.damaged or right in runtime.damaged):
        return WitnessReadout("ABSTAIN_WITNESS_UNAVAILABLE", None)
    role_l, role_r = runtime.core.roles[left], runtime.core.roles[right]
    if (len(role_l) != K or len(role_r) != K or
            any(not math.isfinite(v) or abs(v) > 20 for v in role_l+role_r)):
        return WitnessReadout("ABSTAIN_INVALID_WITNESS", None)
    if abs(_mean(role_r) - MARKER) > TOL:
        return WitnessReadout("ABSTAIN_MISSING_WITNESS_MARKER", None)
    avg = _mean(role_l)
    if abs(avg - BIT_ZERO) <= TOL:
        return WitnessReadout("RETAINED_NATIVE_PROBE_BIT", 0)
    if abs(avg - BIT_ONE) <= TOL:
        return WitnessReadout("RETAINED_NATIVE_PROBE_BIT", 1)
    return WitnessReadout("ABSTAIN_AMBIGUOUS_LOCAL_BIT", None)
