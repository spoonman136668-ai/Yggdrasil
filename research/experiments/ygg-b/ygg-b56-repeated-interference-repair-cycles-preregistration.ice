YGG-B56 PREREGISTRATION — REPEATED INTERFERENCE/REPAIR CYCLES UNDER FIXED CAPACITY
Parent B55 established one target refresh is behaviorally sufficient and repeated identical refresh is redundant through dose64. B50/B51 showed adding a different replay before or after target repair does not reduce collateral.
Question: can the same exact target refresh repeatedly restore a requested old memory after repeated competing writes, and what collateral cost accumulates under fixed capacity?
Freeze exact B55/B48 model, training/evaluation rows,120 parameters,32 persistent-state scalars, seven original bindings, seeds[111,222,333,444,555], q=[0..4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For each seed/q and each competing identity r in [0..6]\{q}:
1. Build shared seven-write baseline M0.
2. Initial repair: exact q refresh; score all seven.
3. For cycles1..4:
   a. write exact competing binding r once; score target q and all-seven decisions (post-interference).
   b. write exact target q once; score again (post-repair).
No other writes occur.
Primary:
- whether q is >=.90 capable after every repair;
- whether any post-interference step loses q capability;
- collateral NEW_ERROR/REPAIR vs original M0 after every repair;
- exact decision differences vs the initial one-refresh repaired state.
Classification:
REPEATABLE_TARGET_REPAIR_STABLE if every post-repair state preserves universal q rescue and all post-repair decisions/collateral equal the initial repair through cycle4.
REPEATABLE_TARGET_REPAIR_WITH_COLLATERAL_DRIFT if q rescue is universal after every repair but collateral/decisions drift across cycles.
REPAIR_EVENTUALLY_FAILS if any post-repair q loses capability.
NO_INTERFERENCE_TO_REPAIR if competing writes never disrupt q capability in any stratum.
ANCHOR_NOT_REPRODUCED if initial one-refresh anchor fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/q/r enumeration; six competitors per q; exact four cycles; exact r then q order per cycle; fixed state/params; same baseline; all-seven scoring at each step; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
