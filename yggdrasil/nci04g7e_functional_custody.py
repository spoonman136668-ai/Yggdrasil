"""NCI-04G7E: evaluator-only native functional identifiability falsifier.

Native functional *responses* are measured before/after an actual cell lesion.
The verifier never supplies the pre-lesion responses to repair_unlabeled.
These are responses of the existing model, NOT externally checked task
correctness, novel-source transfer, or scientific recovery evidence.
"""
from dataclasses import dataclass
import hashlib
from .developmental import valid
from .task_runtime import LocalTaskRuntime
from .nci04g7d_native_lesion import NativeNeighborLesionObserver


@dataclass(frozen=True)
class FunctionalNoGo:
    classification: str
    source_commit: str
    sender: int
    damaged: int
    prelesion_response_a: float
    prelesion_response_b: float
    damaged_response_a: float
    damaged_response_b: float
    repaired_response_a: float
    repaired_response_b: float
    surviving_state_identical: bool
    after_repair_state_identical: bool
    abstain: bool
    evaluator_only: bool = True
    information_source: str = "NATIVE_MODEL_FUNCTIONAL_RESPONSE_NOT_INDEPENDENT_TASK_TRUTH"


def evaluate_indistinguishable_functional_loss(world_a, world_b, bits, damaged, sender, root):
    """Distinguishing pre-lesion phenotypes with indistinguishable survivors.

    Two known counterfactual native states are provided only to this evaluator.
    The native learner receives no original response, target label, task-world
    ID or global function copy. The function DOES NOT train or alter the input
    runtimes: it performs the intervention on isolated restored copies.

    It returns an explicit no-go certificate, never a recovered task function.
    """
    if type(world_a) is not LocalTaskRuntime or type(world_b) is not LocalTaskRuntime:
        raise TypeError("requires two existing native task runtimes")
    valid(bits)
    if (type(damaged) is not int or type(sender) is not int or
        not 0 <= damaged < 8 or not 0 <= sender < 8):
        raise ValueError("invalid native cells")
    a = LocalTaskRuntime.restore(world_a.snapshot())
    b = LocalTaskRuntime.restore(world_b.snapshot())
    if (a.damaged or b.damaged or a.neighbors != b.neighbors or
        damaged not in a.neighbors[sender]):
        raise ValueError("requires pristine neighboring native worlds")
    if a.core.genome != b.core.genome:
        raise ValueError("genome drift prevents an identifiability comparison")
    if any(a.core.roles[i] != b.core.roles[i] for i in range(8) if i != damaged):
        raise ValueError("survivor prelesion information differs")
    if a.core.events != b.core.events or a.steps != b.steps:
        raise ValueError("different history counters violate matched evidence")
    before_a = a.component(bits, damaged)
    before_b = b.component(bits, damaged)
    if abs(before_a - before_b) <= 0.01:
        raise ValueError("no distinguishable prelesion functions in counterexample")
    event_a = NativeNeighborLesionObserver(a, root).intervene_and_measure(sender, damaged)
    event_b = NativeNeighborLesionObserver(b, root).intervene_and_measure(sender, damaged)
    if (event_a.source_commit != event_b.source_commit or
        event_a.source_sha256 != event_b.source_sha256):
        raise ValueError("unmatched native source provenance")
    # Only the sender's own learned role, adjacency and observed damage
    # status may reach local recovery. No global PRE-lesion identity digest.
    if (event_a.before_local_sha256 != event_b.before_local_sha256 or
        event_a.after_local_sha256 != event_b.after_local_sha256):
        raise ValueError("local survivor evidence identity drift")
    # The intervention must destroy only local target-role information.
    same_damaged_state = a.snapshot() == b.snapshot()
    if not same_damaged_state:
        raise ValueError("surviving native observations remain distinguishable")
    damaged_a = a.component(bits, damaged)
    damaged_b = b.component(bits, damaged)
    # The evaluation reference outputs never enter this native repair path.
    a.repair_unlabeled(bits, steps=3)
    b.repair_unlabeled(bits, steps=3)
    same_repaired = a.snapshot() == b.snapshot()
    if not same_repaired:
        raise ValueError("identical surviving information yielded different repairs")
    repaired_a = a.component(bits, damaged)
    repaired_b = b.component(bits, damaged)
    if repaired_a != repaired_b:
        raise ValueError("unidentifiable function was claimed distinguishable")
    # No unique recovery is possible: a single response cannot equal both
    # distinct prelesion responses. Abstention is required by information.
    return FunctionalNoGo(
        classification="ABSTAIN_INFORMATION_THEORETICALLY_UNIDENTIFIABLE",
        source_commit=event_a.source_commit,
        sender=sender, damaged=damaged,
        prelesion_response_a=before_a, prelesion_response_b=before_b,
        damaged_response_a=damaged_a, damaged_response_b=damaged_b,
        repaired_response_a=repaired_a, repaired_response_b=repaired_b,
        surviving_state_identical=same_damaged_state,
        after_repair_state_identical=same_repaired,
        abstain=True)
