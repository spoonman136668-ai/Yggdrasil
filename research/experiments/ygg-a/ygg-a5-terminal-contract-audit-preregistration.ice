TITLE: YGG-A5 Terminal Integrity Contract Consistency Audit Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-A
PARENT_A3_CLOSURE: 3f3fe316558e2ec804af45b0bd5aeeb56ee3de84
SOURCE_A4_CLOSURE: c493896e4552f2bc9c9b0190bf105212a66ec572
SOURCE_EXPERIMENT: YGG-A4

QUESTION
Does the inherited compact repair_integrity summary conflict with the already-frozen terminal maturity contract by rejecting a valid epoch-159 detected REPAIR_PENDING state?

SCOPE
Read-only measurement-contract audit.
No scientific mechanism change.
No new scheduler.
No route change.
No atomic-handoff change.
No horizon change.
No capacity change.
No threshold tuning.

FROZEN EVIDENCE
Re-execute the exact frozen YGG-A4 primary mechanism and manifests.
Use the existing A4 result fields, maturity rows, and target-141 diagnostics unchanged.

AUDIT RULE
For every world where:
- maturity.pass == true; and
- result.repair.repair_integrity == false;

determine whether the entire mismatch is exactly explained by one or more passing TERMINAL_159 rows.

A mismatch is TERMINAL_159-explained iff all are true:
- every maturity row passes;
- every unrepaired detected corruption corresponds to a maturity row with kind=TERMINAL_159;
- every TERMINAL_159 row has detection_epoch=159, repaired=false, repair_epoch=null, verified_epoch=null, done_epoch=null, terminal_state=REPAIR_PENDING;
- verification_detected == repaired + count(TERMINAL_159);
- incorrect_done == 0;
- matching duplicate cell/request integrity remains exact.

PRIMARY CLASSIFICATION
YGG_A5_TERMINAL_CONTRACT_DIVERGENCE=true iff:
- at least one maturity-pass / repair_integrity-false mismatch exists; and
- every such mismatch is TERMINAL_159-explained; and
- there are no repair_integrity failures in maturity-failing worlds used to support the classification; and
- duplicate audit execution is byte-identical.

INTERPRETATION
Positive:
The compact repair_integrity summary is horizon-insensitive and inconsistent with the frozen maturity contract at epoch 159. This does not retroactively change A4's formal verdict. It authorizes a future separately preregistered experiment to use a horizon-aware integrity metric aligned with the frozen maturity rules.

Negative:
The A4 repair_integrity failure has additional causes beyond valid TERMINAL_159 state and must not be treated as a measurement-contract issue.

FAILURE DISCIPLINE
Do not modify A4, its output, or its preregistered verdict.
Do not redefine TERMINAL_159 after observing the audit.
Do not remove any failed legacy field from historical evidence.

BOUNDARY
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
No modification of other lanes or external runtimes.
