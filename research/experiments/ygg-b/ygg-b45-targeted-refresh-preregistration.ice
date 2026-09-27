YGG-B45 PREREGISTRATION — BOUNDED TARGETED MEMORY REFRESH
Parent B44 run 36277246562 valid ROBUST_TWO_POSITION_RECENCY_BAND.
Question: can one bounded rewrite of the queried binding exploit the recency mechanism to restore old READ1 capability, and is the effect specific to refreshing the target rather than merely performing any extra write?
Freeze exact B44/B27 model/training/evaluation, threshold .90, 120 params, 32 persistent-state scalars, seven unique initial bindings, deterministic Torch, seeds [111,222,333,444,555]. No retraining/adaptation/capacity/architecture/threshold change.
Test first-read query strata q=[0,1,2,3,4], the historically old/subthreshold region.
For each seed/q row, first process the exact original seven writes.
Arms:
1. ORIGINAL: immediate READ1 with no added write; must reproduce inherited original accuracy.
2. TARGET_REFRESH: perform exactly one additional write immediately before READ1 using the exact key/role/slot/value block of the queried original binding, then query. This changes temporal history only; it introduces no new binding identity or value.
3. CONTROL_REFRESH: perform exactly one additional write immediately before READ1 using the mechanically fixed nonqueried binding at position (q+1) mod 7, then query.
Classification:
TARGET_SPECIFIC_UNIVERSAL_REFRESH if TARGET_REFRESH is >=.90 for every seed/q stratum and CONTROL_REFRESH is not universal.
GENERAL_EXTRA_WRITE_RESCUE if both refresh arms are universal.
PARTIAL_TARGET_REFRESH if target refresh rescues at least one but not all originally subthreshold strata.
NO_TARGET_REFRESH_RESCUE if target refresh rescues none of the originally subthreshold strata.
OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/q strata; original endpoints reproduce; refresh block identity/value exact; control never equals query binding; one and only one added write per transformed arm; initial seven writes unchanged; threshold/state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
