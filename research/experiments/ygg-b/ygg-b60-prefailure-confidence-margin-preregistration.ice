YGG-B60 PREREGISTRATION — NATIVE PRE-FAILURE CONFIDENCE-MARGIN SIGNAL
Parent B59 valid ORDER_FAMILY_BOUNDED_WITH_UNIVERSAL_RECOVERY.
Question: before observable target capability loss, does a simple native output-confidence signal separate states that will fail on the next competing write from states that will survive it?
Freeze exact B59 substrate: same model,120 parameters,32 persistent-state scalars, seven original bindings, seeds[111,222,333,444,555], q=[0..4], deterministic Torch, same12 cyclic forward/reverse orders, same shared baseline and one target refresh at depth0.
For every seed/q/order trajectory, at each pre-write state while target capability is still >=.90:
- query target position q using the current native memory state;
- for every row compute top1_logit - top2_logit, using no ground-truth value identity;
- define PRE_MARGIN as the arithmetic mean of those per-row top1-top2 margins;
- apply the next preregistered competing write;
- label NEXT_FAILURE=true iff that write causes the first target capability loss (<.90).
Stop contributing transitions after first loss for that order.
No threshold is selected or tuned.
Primary:
- exact PRE_MARGIN values for all eligible transitions;
- min/max PRE_MARGIN for NEXT_FAILURE and NEXT_SURVIVAL groups;
- deterministic rank AUROC of PRE_MARGIN for survival (higher margin predicts survival), reported descriptively;
- exact overlap status.
Classification:
STRICT_MARGIN_SEPARATION if max PRE_MARGIN among NEXT_FAILURE states is strictly less than min PRE_MARGIN among NEXT_SURVIVAL states.
MARGIN_OVERLAP if both groups are nonempty and their PRE_MARGIN ranges overlap.
NO_FAILURE_TRANSITIONS if no NEXT_FAILURE examples reproduce.
ANCHOR_NOT_REPRODUCED if B59 order/first-loss anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact B59 12-order family and first-loss table reproduced; only pre-first-loss transitions included; PRE_MARGIN uses top1-top2 logits only and never the correct label; deterministic mean/rank computation; fixed state/params; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
