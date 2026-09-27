YGG-B48 PREREGISTRATION — EXHAUSTIVE REFRESH-IDENTITY SWEEP
Parent B47 run 36285541091 valid GENERAL_EXTRA_WRITE_COLLATERAL; parent B45-B valid TARGET_SPECIFIC_UNIVERSAL_REFRESH.
Question: for an old queried binding, how does the identity of the one rewritten existing binding determine target rescue and collateral redistribution under fixed capacity?
Freeze exact B47/B46/B45-B/B27 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, seeds [111,222,333,444,555], old-query strata q=[0,1,2,3,4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row:
- process exact original seven writes and score baseline;
- for refresh identity r in [0,1,2,3,4,5,6], perform exactly one extra write of the exact original binding r;
- score target binding q and all seven original bindings.
Report per seed/q/r:
- target-q accuracy and >=.90 capability;
- collateral baseline-correct opportunities excluding refreshed binding r;
- collateral NEW_ERROR and REPAIR counts.
Inherited anchors:
- r=q target accuracy must be >=.90 for every seed/q stratum;
- r=(q+1) mod7 target accuracy must be <.90 for every seed/q stratum.
Classification:
TARGET_IDENTITY_UNIQUE_RESCUE if for every seed/q exactly r=q is target-capable.
MULTIPLE_REFRESH_IDENTITIES_RESCUE if at least one seed/q has a non-q target-capable r while all target anchors reproduce.
TARGET_RESCUE_NOT_REPRODUCED if any r=q anchor fails.
CONTROL_ANCHOR_NOT_REPRODUCED if any r=(q+1) mod7 control anchor fails.
OTHER_VALID_PATTERN otherwise.
No collateral threshold is introduced; exact counts are reported for all 175 seed/q/r strata.
Validity: exact seeds/q/r enumeration; exactly one added write; refresh block identity exact; same baseline for all seven r arms; all original bindings scored; target/control anchors exact; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
