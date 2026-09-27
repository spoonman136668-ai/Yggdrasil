YGG-B58 PREREGISTRATION — REVERSE-ORDER INTERFERENCE HORIZON
Parent B57 valid BOUNDED_INTERFERENCE_HORIZON_WITH_RECOVERY.
Question: is the observed depth3-5 failure horizon primarily cumulative-load driven, or materially dependent on competitor identity/order?
Freeze exact B57 substrate: same model,120 parameters,32 persistent-state scalars, seven original bindings, seeds[111,222,333,444,555], q=[0..4], deterministic Torch, shared baseline and one target refresh at depth0.
For each seed/q, use the exact same six competing identities as B57 but in reverse cyclic order:
r_d = (q-d) mod7 for d=1..6.
No target repair between depths1..6. Score all seven decisions and q capability after every depth, then apply one exact target refresh after depth6 and score again.
Compare first_loss_depth for each seed/q against frozen B57 first_loss_depth.
Classification:
ORDER_INVARIANT_HORIZON if every stratum has the same first_loss_depth as B57 and final recovery remains universal.
ORDER_SHIFTS_HORIZON_WITH_RECOVERY if at least one first_loss_depth changes but all lost strata recover after the final refresh.
ORDER_SHIFTS_AND_RECOVERY_FAILS if first-loss depths change and any lost stratum fails final recovery.
NO_FAILURE_REVERSE_ORDER if no stratum loses capability through depth6.
ANCHOR_NOT_REPRODUCED if depth0 anchor or B57 comparison table fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/q; exact reversed six-identity order; no q writes between depths1..6; all-seven scoring every depth; frozen B57 first-loss table exact; final repair exact; fixed state/params; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
