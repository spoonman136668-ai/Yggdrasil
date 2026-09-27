YGG-B46 PREREGISTRATION — TARGETED REFRESH COLLATERAL RETRIEVAL
Parent B45-B run 36282455288 valid TARGET_SPECIFIC_UNIVERSAL_REFRESH.
Question: does one targeted rewrite restore the old queried binding without causing collateral retrieval loss in the other six stored bindings under fixed memory capacity?
Freeze exact B45-B/B27 model, training, evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, threshold .90 for the target-rescue anchor, seeds [111,222,333,444,555], original old-query strata q=[0,1,2,3,4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed and every row in each old-query stratum:
1. process the exact original seven writes;
2. baseline-query each of the seven stored bindings using its exact original key/role/slot and score against its exact original value;
3. perform exactly one TARGET_REFRESH using the original queried binding q;
4. query each of the seven stored bindings again.
Primary target anchor: aggregate target-q accuracy after refresh must remain >=.90 for every seed/q stratum exactly as B45-B.
Collateral metric for j!=q:
- NEW_ERROR = baseline prediction correct and post-refresh prediction incorrect;
- REPAIR = baseline prediction incorrect and post-refresh prediction correct.
No arbitrary delta threshold is introduced.
Classification:
CLEAN_LOCAL_CORRECTION if the target anchor is universal and total collateral NEW_ERROR count is zero.
TARGET_RESCUE_WITH_COLLATERAL if the target anchor is universal and at least one collateral NEW_ERROR occurs.
TARGET_RESCUE_NOT_REPRODUCED if any target stratum falls below .90.
OTHER_VALID_PATTERN otherwise.
Report total baseline-correct collateral opportunities, NEW_ERROR count, REPAIR count, and per-seed/q/per-binding counts.
Validity: exact seeds/q strata; seven unique original binding blocks unchanged; target refresh block exactly equals q binding; one added write only; every post-refresh collateral query addresses an original non-q binding; target B45-B anchor exact; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
