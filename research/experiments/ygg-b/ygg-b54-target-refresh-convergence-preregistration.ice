YGG-B54 PREREGISTRATION — TARGET-REFRESH NUMERICAL CONVERGENCE THROUGH DOSE16
Parent B53 run 36312694100 valid OUTPUT_CHANGES_WITHOUT_DECISION_CHANGE.
Question: does repeated exact target rehearsal reach an exact numerical fixed point, continue a behaviorally silent contracting tail, or eventually alter retrieval decisions?
Freeze exact B53/B52 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, seeds [111,222,333,444,555], old-query strata q=[0..4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row:
- shared baseline after original seven writes;
- apply the exact target-q write consecutively for doses1..16;
- after every dose record target and all seven retrieval decisions plus collateral NEW_ERROR;
- for every transition d->d+1 record torch.equal state, max absolute state delta, changed state elements, all-seven logit equality and max absolute logit delta.
Inherited anchors through dose3: universal target rescue and collateral NEW_ERROR=3724 at doses1,2,3.
Classification:
EXACT_FIXED_POINT_REACHED if there exists a dose k<=15 such that every stratum has state[d]==state[d+1] for every transition d>=k and all logits remain equal thereafter.
NUMERIC_TAIL_DECISION_INVARIANT if no universal exact fixed point is reached, but target/collateral decisions remain identical to dose1 through dose16.
BEHAVIOR_CHANGES_AT_HIGHER_DOSE if any target capability or collateral decision/count differs from dose1 at dose4..16.
ANCHOR_NOT_REPRODUCED if inherited dose1..3 behavior fails.
OTHER_VALID_PATTERN otherwise.
No epsilon threshold is used for classification; exact equality and exact decisions only. Report the numerical deltas descriptively.
Validity: exact seeds/q/doses1..16; only exact target binding rewritten; state shape exact; all seven logits inspected at every dose; inherited anchors exact; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
