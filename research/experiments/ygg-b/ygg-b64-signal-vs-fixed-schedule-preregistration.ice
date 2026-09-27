YGG-B64 PREREGISTRATION — SIGNAL-TIMED ONE-SHOT REFRESH VS FIXED-DEPTH SCHEDULES
Parent B63 valid PREVENTIVE_GATE_REPLICATES.
Question: does the frozen internal margin signal provide useful intervention timing beyond the benefit of a blind one-shot target refresh?
Frozen gate T=2.6009554862976074. No refitting.
New seeds exactly [2333,2444,2555,2666,2777], disjoint from B60-B63.
Freeze exact B63 substrate:120 parameters,32 persistent-state scalars,q=[0..4],deterministic Torch,same12 cyclic forward/reverse six-competitor orders.
Matched branches after depth0 target refresh:
CONTROL: no intervention.
GATED: exact B62/B63 policy, at most one target refresh at first capable pre-write state with margin<=T.
FIXED_D1..FIXED_D5: at most one target refresh immediately before the scheduled competing write at the named depth, but only if target is still capable at that pre-write state. No signal is consulted.
No branch receives more than one intervention.
Report per branch:
- interventions;
- first-loss depths;
- failures-by-depth6;
- final target capability;
- all-seven collateral NEW_ERROR/REPAIR after depth6.
Primary comparison:
- GATED failures-by6 vs each fixed schedule;
- intervention count vs each fixed schedule.
Classification:
SIGNAL_TIMING_STRICTLY_BETTER if GATED failures-by6 is lower than every FIXED_D1..D5 arm.
SIGNAL_TIMING_TIED_BEST if GATED equals the minimum fixed failures-by6 and is not worse than any fixed schedule.
FIXED_SCHEDULE_BETTER if any fixed schedule has fewer failures-by6 than GATED.
NO_INTERVENTION_BENEFIT if GATED failures-by6 >= CONTROL failures-by6 and every fixed schedule also >=CONTROL.
ANCHOR_NOT_REPRODUCED if depth0/order construction fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact fresh seeds and disjointness; exact12 orders; threshold bit-exact; one intervention max/branch; fixed schedules do not read margin; matched starting states; fixed parameters/capacity; deterministic duplicate.
Scientific negatives are valid. No post-result tuning.
