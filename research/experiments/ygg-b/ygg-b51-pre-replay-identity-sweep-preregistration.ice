YGG-B51 PREREGISTRATION — PRE-REPLAY IDENTITY SWEEP BEFORE TARGET REFRESH
Parent B50 run 36307035998 valid NO_RESTORATIVE_SECOND_IDENTITY; B48 target refresh is uniquely rescuing.
Question: can one bounded preparatory replay reduce collateral if the target refresh is performed last rather than first?
Freeze exact B50/B48 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, seeds [111,222,333,444,555], old-query strata q=[0..4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row use one shared baseline.
Anchor TARGET_ONLY: one exact write of q.
For each pre-replay r in [0..6]\{q}:
- write exact binding r first;
- then exact binding q last;
- score all seven original bindings.
Within each q/r compare TARGET_ONLY and PRE_R_PLUS_TARGET on the same common collateral panel excluding q and r.
Report target accuracy, NEW_ERROR, REPAIR, baseline-correct opportunities for all150 arms.
Classification:
STRICT_PRE_REPLAY_RESTORATIVE_IDENTITY_EXISTS if at least one fixed r preserves universal target rescue, lowers aggregate common-panel NEW_ERROR, and no eligible stratum worsens.
AGGREGATE_PRE_REPLAY_RESTORATIVE_IDENTITY_EXISTS if at least one fixed r preserves universal target rescue and lowers aggregate NEW_ERROR but some stratum worsens.
NO_RESTORATIVE_PRE_REPLAY_IDENTITY if no fixed r lowers aggregate NEW_ERROR while preserving universal target rescue.
TARGET_RESCUE_LOST_FOR_ALL_PRE_REPLAY_IDENTITIES if every fixed r loses target rescue somewhere.
ANCHOR_NOT_REPRODUCED if TARGET_ONLY anchor fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact seed/q/r enumeration; pre-replay first and target last; exactly two added writes; identities exact; same baseline/common panels; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
