YGG-B47 PREREGISTRATION — TARGET VS CONTROL REFRESH COLLATERAL
Parent B46 run 36283971330 valid TARGET_RESCUE_WITH_COLLATERAL and parent B45-B valid TARGET_SPECIFIC_UNIVERSAL_REFRESH.
Question: is collateral redistribution specific to rewriting the requested binding, or is it a generic consequence of performing any one extra write under fixed memory capacity?
Freeze exact B46/B45-B/B27 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, seeds [111,222,333,444,555], old-query strata q=[0,1,2,3,4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row:
1. process the exact original seven writes;
2. score all seven original bindings at baseline;
3. TARGET_REFRESH arm: one extra write of binding q, then score all seven bindings;
4. CONTROL_REFRESH arm: one extra write of binding (q+1) mod7, then score all seven bindings.
Inherited anchors:
- TARGET_REFRESH target-q accuracy >=.90 for every stratum.
- CONTROL_REFRESH target-q accuracy remains <.90 for every stratum, as B45-B.
For each arm and every non-refreshed binding, report NEW_ERROR and REPAIR counts relative to the same baseline.
Classification:
NO_EXTRA_WRITE_COLLATERAL if both arms have zero collateral NEW_ERROR.
TARGET_ONLY_COLLATERAL if target arm has NEW_ERROR>0 and control arm has zero.
CONTROL_ONLY_COLLATERAL if control arm has NEW_ERROR>0 and target arm has zero.
GENERAL_EXTRA_WRITE_COLLATERAL if both arms have NEW_ERROR>0.
ANCHOR_NOT_REPRODUCED if target/control target-q anchors fail.
OTHER_VALID_PATTERN otherwise.
No threshold is applied to collateral magnitude; exact counts are reported.
Validity: exact seeds/q strata; refresh identities exact; one added write per transformed arm; same baseline used for both comparisons; all six non-refreshed bindings scored per arm; target/control anchors exact; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
