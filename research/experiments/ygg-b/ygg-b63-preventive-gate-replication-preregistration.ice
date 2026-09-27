YGG-B63 PREREGISTRATION — INDEPENDENT REPLICATION OF FROZEN ONE-SHOT PREVENTIVE GATE
Parent B62 valid FROZEN_GATE_PREVENTS_FAILURE.
Question: does the exact frozen B62 warning/intervention policy replicate on another disjoint seed block without any refitting?
Threshold remains bit-exact T=2.6009554862976074.
New seeds exactly [1777,1888,1999,2111,2222], disjoint from B60/B61/B62.
Freeze exact B62 model,120 parameters,32 persistent-state scalars, q=[0..4], deterministic Torch, same12 cyclic forward/reverse six-competitor orders.
For every seed/q/order:
CONTROL = no intervention.
GATED = at first capable pre-write state with PRE_MARGIN<=T, apply exactly one target-q refresh before scheduled competitor; no further interventions.
Matched non-mutating counterfactual at trigger determines true imminent vs false trigger; it never feeds back.
Report B62 metrics exactly:
triggered trajectories, true imminent triggers, false triggers, immediate prevented failures, intervention harms, CONTROL failures-by6, GATED failures-by6, collateral after depth6.
Classification:
PREVENTIVE_GATE_REPLICATES if true_imminent>0, every true imminent trigger is immediately prevented, harms=0, and GATED failures-by6 < CONTROL failures-by6.
PARTIAL_REPLICATION if at least one true imminent failure is prevented and GATED failures-by6 < CONTROL but strict replication criteria fail.
NO_NET_PREVENTIVE_BENEFIT if GATED failures-by6 >= CONTROL failures-by6.
NO_TRUE_IMMINENT_TRIGGERS if gate triggers but none are true imminent.
NO_TRIGGERS if gate never triggers.
ANCHOR_NOT_REPRODUCED if depth0/order construction fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact new seeds only and disjoint from prior three blocks; exact12 orders; threshold bit-identical; at most one intervention; matched state clones; counterfactual never feeds back; margin ground-truth-free; no parameter/architecture/capacity change; deterministic duplicate.
Scientific negatives are valid. No post-result tuning.
