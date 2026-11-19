"""ST10 opt-in, public-evidence-conditioned intervention proposal for ST9.

Source-only interface; no source-world imports, private law, evaluator labels,
new scientific first-use or changes to the frozen ST9 model/evaluation.
This is contradiction-conditioned *experimental design*, not trained action
values or proven novel-world transfer. The action basis remains disclosed.
"""
from research.nci04_st9.native_repair import NativeRepair8, features

MAX_PROBES = 8


def _rank(vectors, width):
    basis = [0] * width
    rank = 0
    for raw in vectors:
        if type(raw) is not int or raw < 0 or raw >= (1 << width):
            raise ValueError("ST10_PUBLIC_BASIS_INVALID")
        value = raw
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def choose_intervention(native):
    """Return next intervention *action code* 1..16, or None to abstain.

    Must be called AFTER an independently observed neutral calibration
    and BEFORE the intervention is executed. Uses only the exact native
    cold state updated from earlier observed public consequences.
    No probabilities or effects for unexecuted actions are manufactured.
    """
    if type(native) is not NativeRepair8 or native.variant != "repair":
        raise ValueError("ST10_EXACT_REPAIR_MODEL_REQUIRED")
    snapshot = native.snapshot()
    if NativeRepair8.restore(snapshot).snapshot() != snapshot:
        raise ValueError("ST10_COLD_CUSTODY_INVALID")
    if native.phase != 1 or native.rotation not in (1, 2, 3):
        raise ValueError("ST10_NO_PUBLIC_NEUTRAL_CALIBRATION")
    used = [pair[0] for pair in native.experiences]
    if (native.updates != len(used) or len(used) != len(set(used))
            or len(used) > MAX_PROBES):
        raise ValueError("ST10_UNRECONCILED_PUBLIC_EVENT_LEDGER")
    if native.post_growth_conflicts:
        return None  # A changed, unidentifiable law needs new source custody.
    if len(used) == MAX_PROBES:
        return None
    degree = native.degree
    if _rank([features(b, degree) for b in used], 4 if degree == 1 else 8) != native.rank:
        raise ValueError("ST10_NATIVE_RANK_NOT_SUPPORTED_BY_PUBLIC_HISTORY")

    candidates = [b for b in range(1, 16) if b not in used]
    if degree == 1:
        # Acquire actual linear evidence first, without presuming all eight
        # quadratic coefficients are causally active.
        base = _rank([features(b, 1) for b in used], 4)
        advancing = [
            b for b in candidates
            if _rank([features(x, 1) for x in used] + [features(b, 1)], 4) > base
        ]
        if advancing:
            result = min(advancing) + 1
        else:
            # Once linear learning is saturated, deliberately probe a
            # *falsifiable* adjacent-action interaction. If its observed
            # consequence contradicts the model, NativeRepair8 itself
            # performs structural growth and replay; this selector cannot.
            base2 = _rank([features(b, 2) for b in used], 8)
            challengers = [
                b for b in candidates
                if _rank([features(x, 2) for x in used] + [features(b, 2)], 8) > base2
                and features(b, 2) >> 4
            ]
            result = min(challengers) + 1 if challengers else None
    else:
        # A witnessed contradiction already caused native structural
        # growth. Now prioritize independent probes rich in interactions
        # rather than the pre-growth linear curriculum. This is a fixed
        # transparent design heuristic, NOT learned action-value optimality.
        base = _rank([features(b, 2) for b in used], 8)
        advancing = [
            b for b in candidates
            if _rank([features(x, 2) for x in used] + [features(b, 2)], 8) > base
        ]
        result = (
            max(advancing, key=lambda b: ((features(b, 2) >> 4).bit_count(), -b)) + 1
            if advancing else None
        )
    if native.snapshot() != snapshot:
        raise ValueError("ST10_SELECTOR_MUTATED_NATIVE_MODEL")
    return result
