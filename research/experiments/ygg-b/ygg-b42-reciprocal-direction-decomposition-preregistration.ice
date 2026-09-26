YGG-B42 PREREGISTRATION — QUERY-RELATIVE RECIPROCAL DIRECTION DECOMPOSITION
Parent B41 run 36272095308 valid QUERY_RELATIVE_PORTABLE with 6<->query_position accuracy 1.0 for every seed and query stratum 0..5.
Question: is rescue caused by moving the queried binding to latest position6, by moving original position6 content into the queried slot, or by their joint reciprocal exchange?
Freeze exact B41 model/training/evaluation, threshold .90, 120 params, 32 state scalars, deterministic Torch, seeds [111,222,333,444,555], query strata q=[0,1,2,3,4,5], seven active bindings, exact held-out evaluation set. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
For each query stratum q define parking position p=(q+1) mod 6, fixed before outcomes and always distinct from q and position6.
Evaluate four arms on the same q rows:
1. ORIGINAL.
2. RECIPROCAL: q->6 and 6->q, frozen B41 positive anchor.
3. TARGET_TO_LATEST_ONLY: three-cycle q->6, 6->p, p->q. The queried binding moves to position6 but original position6 content does not move to q.
4. SOURCE6_TO_QUERY_ONLY: three-cycle 6->q, q->p, p->6. Original position6 content moves to q but the queried binding does not move to position6.
All arms are pure permutations preserving the exact seven-binding multiset.
Classify TARGET_TO_LATEST_SUFFICIENT if RECIPROCAL and TARGET_TO_LATEST_ONLY are portable across every seed/q stratum while SOURCE6_TO_QUERY_ONLY is not; SOURCE6_TO_QUERY_SUFFICIENT if RECIPROCAL and SOURCE6_TO_QUERY_ONLY are universally portable while TARGET_TO_LATEST_ONLY is not; BOTH_DIRECTIONS_SUFFICIENT if all three transformed arms are universally portable; JOINT_RECIPROCAL_REQUIRED if only RECIPROCAL is universally portable; PARTIAL_DIRECTIONAL_PATTERN otherwise; ANCHOR_NOT_REPRODUCED if RECIPROCAL fails any inherited B41 endpoint.
Validity: exact seeds/query strata/parking rule/threshold/state/params; every stratum nonempty; exact B41 reciprocal endpoints 1.0; multiset preserved every arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
