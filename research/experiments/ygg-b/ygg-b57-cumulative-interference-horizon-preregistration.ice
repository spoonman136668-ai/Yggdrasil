YGG-B57 PREREGISTRATION — CUMULATIVE DISTINCT-INTERFERENCE HORIZON
Parent B56 run 36327037721 valid NO_INTERFERENCE_TO_REPAIR.
Question: after one exact target refresh, how many distinct competing writes can accumulate before the target loses capability, and can one exact target refresh restore it after the full six-competitor sequence?
Freeze exact B56/B55 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven original bindings, seeds [111,222,333,444,555], q=[0..4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For each seed/q:
1. Build the shared seven-write baseline M0.
2. Apply one exact target-q refresh. This is depth0 and must reproduce the inherited universal target-capable anchor.
3. Define a frozen cyclic competitor order containing each of the six r!=q identities exactly once:
   r_d = (q+d) mod 7 for d=1..6.
4. Without any target repair between competitors, apply one exact competing write at each depth1..6 and score all seven decisions plus q capability after every depth.
5. After depth6 only, apply one exact target-q refresh and score all seven decisions again.
Primary:
- first_loss_depth per seed/q, or NONE if q remains >=.90 through depth6;
- number of strata losing q capability at each depth;
- post-depth6 repair target capability;
- collateral NEW_ERROR/REPAIR vs original M0 at each depth and after repair.
Classification:
BOUNDED_INTERFERENCE_HORIZON_WITH_RECOVERY if at least one stratum loses q capability by depth6 and every lost stratum is restored >=.90 by the final single q refresh.
INTERFERENCE_HORIZON_WITH_PARTIAL_RECOVERY if at least one stratum loses q capability and at least one lost stratum remains <.90 after the final q refresh.
NO_FAILURE_THROUGH_SIX_DISTINCT_WRITES if no stratum loses q capability through depth6.
ANCHOR_NOT_REPRODUCED if depth0 one-refresh anchor fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/q; exact six distinct competitors per stratum; frozen cyclic order exact; no q writes between depths1..6; all-seven scoring at every depth and final repair; fixed state/params; shared baseline; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
