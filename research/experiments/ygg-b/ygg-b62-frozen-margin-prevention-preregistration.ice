YGG-B62 PREREGISTRATION — ONE-SHOT PREVENTIVE REFRESH FROM FROZEN MARGIN WARNING
Parent B61 HELDOUT_MARGIN_GATE_REPLICATES.
Question: can the frozen native warning gate causally prevent an imminent memory failure using one bounded target refresh, more often than it causes unnecessary intervention?
Frozen threshold T=2.6009554862976074 from B60; no refitting.
New seeds exactly [1222,1333,1444,1555,1666], disjoint from B60/B61.
Freeze exact B61/B59 model,120 parameters,32 persistent-state scalars, q=[0..4], deterministic Torch, same12 cyclic forward/reverse six-competitor orders.
For each seed/q/order create matched clones after the depth0 target refresh:
CONTROL: apply the six competing writes with no intervention.
GATED: before each competing write while target remains capable and before any intervention, compute native PRE_MARGIN. At the first PRE_MARGIN<=T, apply exactly one target-q refresh, then apply the scheduled competing write. No further interventions.
At the trigger state also evaluate a non-mutating counterfactual clone that applies the scheduled competitor without refresh, to determine whether that immediate next write would have caused first target loss.
Report:
- triggered trajectories;
- true imminent triggers (counterfactual next write fails);
- false triggers (counterfactual survives);
- immediate prevented failures (counterfactual fails, gated next state survives);
- intervention harms (counterfactual survives, gated next state fails);
- CONTROL vs GATED first-loss depth and failures-by-depth6;
- all-seven collateral NEW_ERROR/REPAIR after depth6.
Classification:
FROZEN_GATE_PREVENTS_FAILURE if at least one true imminent trigger occurs, every true imminent trigger is immediately prevented, intervention harms=0, and GATED failures-by6 < CONTROL failures-by6.
PARTIAL_PREVENTIVE_BENEFIT if at least one true imminent failure is prevented and GATED failures-by6 < CONTROL, but strict criteria above fail.
NO_NET_PREVENTIVE_BENEFIT if GATED failures-by6 >= CONTROL failures-by6.
NO_TRUE_IMMINENT_TRIGGERS if gate triggers but none are true imminent.
NO_TRIGGERS if gate never triggers.
ANCHOR_NOT_REPRODUCED if depth0/order construction fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact new seeds only; exact12 orders; threshold bit-identical; at most one intervention per trajectory; matched state clones; counterfactual never feeds back; PRE_MARGIN ground-truth-free; fixed resources/state/params; deterministic duplicate.
Scientific negatives are valid. No post-result tuning.
