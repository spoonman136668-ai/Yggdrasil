YGG-B49 PREREGISTRATION — TWO-WRITE TARGET REFRESH + OLDEST-NONTARGET REPLAY
Parent B48 run 36286528372 valid TARGET_IDENTITY_UNIQUE_RESCUE; B44 established a robust two-position recency band.
Question: can one bounded second replay reduce collateral from the mandatory target refresh while keeping the repaired target in the two-most-recent write band?
Freeze exact B48/B47/B46/B27 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, seeds [111,222,333,444,555], old-query strata q=[0,1,2,3,4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row, use one shared baseline after the original seven writes.
Arms:
1. TARGET_ONLY: one extra write of exact binding q.
2. TARGET_PLUS_OLDEST_OTHER: first write exact binding q, then write exact binding r=min({0..6}\{q}).
The second-write choice is fixed from write age only and never from outcome data.
After each arm score all seven original bindings.
Inherited anchor: TARGET_ONLY target-q accuracy must be >=.90 for every stratum.
Primary checks for TARGET_PLUS_OLDEST_OTHER:
- target-q remains >=.90 for every stratum;
- exact collateral NEW_ERROR and REPAIR counts relative to the same baseline, excluding currently replayed binding from collateral accounting.
Classification:
STRICT_COLLATERAL_REDUCTION if two-write target rescue is universal, total collateral NEW_ERROR is lower than TARGET_ONLY, and no seed/q stratum has more collateral NEW_ERROR than TARGET_ONLY.
AGGREGATE_COLLATERAL_REDUCTION if target rescue is universal and total NEW_ERROR is lower but at least one stratum worsens.
NO_COLLATERAL_REDUCTION if target rescue is universal and total NEW_ERROR is not lower.
TARGET_RESCUE_LOST if any two-write target stratum falls below .90.
ANCHOR_NOT_REPRODUCED if TARGET_ONLY target anchor fails.
OTHER_VALID_PATTERN otherwise.
No arbitrary collateral threshold is introduced; exact counts are reported.
Validity: exact seeds/q strata; oldest-nontarget selection exact; target write first and oldest-other second; exactly two added writes in transformed arm; same baseline; all seven bindings scored; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
