YGG-B59 PREREGISTRATION — CYCLIC FORWARD/REVERSE ORDER FAMILY
Parents: B57 BOUNDED_INTERFERENCE_HORIZON_WITH_RECOVERY and B58 ORDER_SHIFTS_HORIZON_WITH_RECOVERY.
Question: over a bounded family of orders using exactly the same six competing identities, what range of first-loss depths is induced by ordering, and does one final target refresh recover every induced loss?
Freeze exact B58/B57 substrate: same model,120 parameters,32 persistent-state scalars, seven original bindings, seeds[111,222,333,444,555], q=[0..4], deterministic Torch, shared baseline and one target refresh at depth0.
For each seed/q construct:
F = [(q+d) mod7 for d=1..6].
R = reverse(F).
Evaluate exactly the six cyclic rotations of F and six cyclic rotations of R, deduplicated; for six distinct identities this yields12 orders.
For each order:
- no target writes between depths1..6;
- score all seven decisions and q capability after every depth;
- after depth6 apply one exact q refresh and score again.
Inherited anchors:
- rotation F0 must reproduce B57 first-loss depth.
- rotation R0 must reproduce B58 first-loss depth.
Primary per seed/q:
- minimum and maximum first-loss depth across12 orders;
- whether any order remains capable through depth6;
- whether final one-refresh recovery is universal for all orders that lose capability.
Classification:
ORDER_FAMILY_BOUNDED_WITH_UNIVERSAL_RECOVERY if every order loses by depth6, at least one seed/q has varying first-loss depth across orders, and every lost sequence recovers after final refresh.
ORDER_FAMILY_HORIZON_INVARIANT if every order loses by depth6, first-loss depth is identical across all12 orders within every seed/q, and final recovery is universal.
SOME_ORDERS_RESIST_SIX_WRITES if at least one order remains target-capable through depth6.
RECOVERY_ORDER_DEPENDENT if any lost sequence fails final recovery.
ANCHOR_NOT_REPRODUCED if B57/B58 order anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact12 unique orders per seed/q; exact forward/reverse rotations only; inherited F0/R0 tables exact; no q writes between depths; all-seven scoring every depth; final repair exact; fixed state/params; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
