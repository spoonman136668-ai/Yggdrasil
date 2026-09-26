TITLE: YGG-A26 A24/A25 Equivalence Reconciliation Closure
DATE: 2026-09-26
STATUS: CLOSED / VALID RECONCILIATION
LANE: YGG-A
PREREGISTRATION: e24e04bf26dca2b0a7e849ac0b34a691b712699c
PARENT_A24_CLOSURE: 64d1aed4e8a4a8aea41324ae3a6625c4beb4e6ee
PARENT_A25_RUN: 33a0c812893f652e8b7c1bce9c0080dce6743536
EXECUTION_HEAD: 2f593907922625d9fabdbc0e993a7449d3511229
WORKFLOW_RUN_ID: 36229298163
DUPLICATE_SHA256: a318c0c19d28bf2f0f812f9c57a0e1e28e0d0efcefb3262f52e6f4cfba22c082

RESULT
YGG_A26_A24_A25_EQUIVALENCE_RECONCILIATION=true
classification=INPUT_DIVERGENCE

For actual manifest replicate 6, seed 583e5e7ad32363990eba4b26f3d128c3:
A24 rank-12 lesion:
[2,7,15,23,29,31,32,39,47,52,55,63]

A25 target-cell-59 lesion:
[7,15,23,29,31,32,39,47,52,55,59,63]

The first differing manifest field is lesion and the runtime bindings differ identically.
Both U_A0 and U_A25 reproduce deterministic but different outputs under those different lesion inputs.

ROOT CAUSE
A24's closure interpretation associated cell 59 with the failing replicate because its marginal-cell report used the zero-based enumeration position as the displayed replicate value. The stream-failure record used the actual manifest replicate ID. The actual failing manifest replicate 6 is the sixth row, seed 583e5e7ad32363990eba4b26f3d128c3, whose rank-12 marginal cell is cell 2.

A25 remains valid as a cell-59 portability test, but it did not reproduce the A24 failing lesion and therefore cannot resolve portability of the actual failing marginal cell.

INTERPRETATION
The apparent A24/A25 contradiction is resolved as an input-attribution error, not nondeterminism and not a controller-family discrepancy.

NEXT QUESTION
Test the true A24 failing marginal cell, cell 2, as the twelfth lesion across every eligible frozen L11 seed context. Determine whether cell 2 is globally sensitive or whether the A24 collapse is specific to actual manifest replicate 6.

BOUNDARY
Diagnostic continuation only.
Repair remains OFF.
No threshold, baseline, controller, or learned-weight mutation.
No online adaptation.
No recursive self-modification.
