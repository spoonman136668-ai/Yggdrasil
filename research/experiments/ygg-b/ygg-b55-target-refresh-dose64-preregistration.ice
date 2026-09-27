YGG-B55 PREREGISTRATION — TARGET-REFRESH NUMERICAL CONVERGENCE THROUGH DOSE64
Parent B54 run 36316835093 valid NUMERIC_TAIL_DECISION_INVARIANT.
Question: does the behaviorally silent numerical tail reach an exact fixed point by dose64, remain decision-invariant, or eventually alter retrieval?
Freeze exact B54 model, training/evaluation rows,120 parameters,32 persistent-state scalars, seven initial bindings, seeds[111,222,333,444,555], old-query strata q=[0..4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row:
- shared baseline after original seven writes;
- exact target-q write consecutively doses1..64;
- after every dose record target and all-seven retrieval decisions plus collateral NEW_ERROR;
- every transition d->d+1 records exact state equality, maximum absolute state delta, changed state elements, all-seven logit equality and maximum absolute logit delta.
Inherited anchors doses1..16: universal target rescue, aggregate collateral NEW_ERROR=3724, no decision changes.
Classification:
EXACT_FIXED_POINT_REACHED_BY_64 if there exists k<=63 such that every stratum has exact state equality for every transition d>=k.
NUMERIC_TAIL_DECISION_INVARIANT_THROUGH_64 if no universal exact fixed point occurs but all decisions and collateral remain identical to dose1 through64.
BEHAVIOR_CHANGES_BY_64 if any target capability, retrieval decision, or collateral count differs from dose1 at dose17..64.
ANCHOR_NOT_REPRODUCED if inherited doses1..16 behavior fails.
OTHER_VALID_PATTERN otherwise.
No epsilon threshold participates in classification; numerical deltas are descriptive only.
Validity: exact seeds/q/doses1..64; only exact target binding rewritten; state shape exact; all seven logits/decisions inspected each dose; inherited anchors exact; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
