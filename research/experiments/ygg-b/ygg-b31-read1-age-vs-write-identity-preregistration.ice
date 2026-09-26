TITLE: YGG-B31 READ1 Age-vs-Write-Identity Preregistration
DATE: 2026-09-26
STATUS: PREREGISTERED
LANE: YGG-B
PARENT_RESULT: YGG-B30 AGE_THRESHOLD_PATTERN
PARENT_RUN: 36229736902

QUESTION
Is the YGG-B30 READ1 degradation determined primarily by the number of subsequent writes (age), or by the identities/order of the intervening bindings?

FROZEN
- exact YGG-B30 model, 120 parameters, 32 persistent-state scalars, seven active bindings, held-out READ2 targets, seeds 111/222/333/444/555;
- inherited accuracy threshold 0.90;
- deterministic execution; no retraining, online adaptation, capacity increase, threshold change, or architecture change.

DESIGN
For each frozen seed and each write position 0..6, evaluate the original sequence and one preregistered deterministic permutation family that changes intervening binding identity/order while preserving: queried binding, number of subsequent writes, total writes, entity-position coverage, sequence length, model state size and parameters. Permutation is derived only from frozen seed and position, never from outcomes.

REPORT
Per seed and position report original and permuted READ1 accuracy, counts, absolute delta, and threshold capability.

CLASSIFICATION
AGE_DOMINANT: threshold-capable position set is identical for original and permuted arms for all seeds and no position changes capability.
IDENTITY_SENSITIVE: at least one position changes threshold capability under permutation.
SUBTHRESHOLD_IDENTITY_EFFECT: capability sets are unchanged but at least one position changes accuracy by >=0.10.
OTHER_VALID_PATTERN: valid evidence matches none above.

SUCCESS
YGG_B31_READ1_AGE_VS_WRITE_IDENTITY=true iff mechanical invariants pass, evidence is valid, duplicate execution is byte-identical, inherited threshold is unchanged, and exactly one classification is emitted.

FAILURE
Do not tune threshold, sequence length, state size, parameter count, number of bindings, seeds, or permutation after results.

BOUNDARY
Diagnostic only. No accepted baseline mutation. No online adaptation. No recursive self-modification.
END
