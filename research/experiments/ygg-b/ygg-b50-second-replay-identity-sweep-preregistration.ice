YGG-B50 PREREGISTRATION — SECOND-REPLAY IDENTITY SWEEP AFTER TARGET REFRESH
Parent B49 scientific result valid NO_COLLATERAL_REDUCTION; parent B48 TARGET_IDENTITY_UNIQUE_RESCUE.
Question: after the mandatory target refresh, does any non-target second replay preserve target rescue while reducing collateral relative to TARGET_ONLY?
Freeze exact B49/B48 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, seeds [111,222,333,444,555], old-query strata q=[0,1,2,3,4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row use one shared baseline after the original seven writes.
Anchor TARGET_ONLY: one extra write of exact binding q.
For every second replay r in [0..6]\{q}:
- write exact binding q first;
- then exact binding r;
- score all seven original bindings.
Use the same common collateral panel for comparison within each q/r: exclude q and r from both TARGET_ONLY and TWO_WRITE counts.
Report target-q accuracy, collateral NEW_ERROR, REPAIR, and baseline-correct opportunities for all 150 seed/q/r arms.
Inherited target anchor: TARGET_ONLY target-q >=.90 for every stratum.
Classification:
STRICT_RESTORATIVE_IDENTITY_EXISTS if at least one fixed second-replay identity rule r has universal target rescue, lower total common-panel NEW_ERROR than TARGET_ONLY, and no seed/q arm under that rule is worse than TARGET_ONLY.
AGGREGATE_RESTORATIVE_IDENTITY_EXISTS if at least one fixed r has universal target rescue and lower aggregate NEW_ERROR but some stratum worsens.
NO_RESTORATIVE_SECOND_IDENTITY if no fixed r lowers aggregate common-panel NEW_ERROR while preserving universal target rescue.
TARGET_RESCUE_LOST_FOR_ALL_SECOND_IDENTITIES if every fixed r causes at least one target-q stratum below .90.
ANCHOR_NOT_REPRODUCED if TARGET_ONLY anchor fails.
OTHER_VALID_PATTERN otherwise.
No collateral magnitude threshold is introduced.
Validity: exact seeds/q/r enumeration; target write first; exactly two added writes; refresh identities exact; same baseline; common panels exact; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
