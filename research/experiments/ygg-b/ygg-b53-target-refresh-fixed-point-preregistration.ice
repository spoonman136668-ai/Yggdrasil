YGG-B53 PREREGISTRATION — TARGET-REFRESH NATIVE STATE FIXED POINT
Parent B52 run 36310819187 valid DOSE_NONMONOTONIC with exactly equal D1/D2/D3 collateral outcomes.
Question: after one exact target rewrite, is the 32-scalar persistent memory state itself an exact fixed point under additional identical target rewrites, or do later writes change hidden state without changing measured retrieval?
Freeze exact B52/B48 model, training/evaluation rows, 120 parameters, 32 persistent-state scalars, seven initial bindings, seeds [111,222,333,444,555], old-query strata q=[0..4], deterministic Torch. No retraining/adaptation/capacity/architecture/threshold change.
For every seed/q row:
- build shared baseline M0 after seven writes;
- D1 = exact target-q refresh once;
- D2 = refresh exact target q again from D1;
- D3 = refresh exact target q again from D2.
Record for D1->D2 and D2->D3:
- torch.equal state tensor;
- maximum absolute state delta;
- number of changed state scalars/elements;
- for all seven query bindings, torch.equal logits and maximum absolute logit delta.
Inherited behavioral anchor: target rescue universal and collateral NEW_ERROR totals D1=D2=D3=3724.
Classification:
EXACT_STATE_FIXED_POINT_AFTER_ONE if every D1==D2==D3 state tensor exactly and all logits exactly equal.
BEHAVIORAL_FIXED_POINT_ONLY if any state tensor changes but all seven query logits remain exactly equal through D3.
OUTPUT_CHANGES_WITHOUT_DECISION_CHANGE if logits change but inherited behavioral outcomes remain exactly dose-invariant.
BEHAVIORAL_ANCHOR_NOT_REPRODUCED if inherited B52 outcome equality fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/q/doses; exact target identity each refresh; state shape exact; all seven logits inspected; inherited B52 aggregate anchors exact; state/params exact; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
