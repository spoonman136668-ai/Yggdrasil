YGG-B45 PREREGISTRATION — RECENCY-BAND BACKGROUND-ORDER ROBUSTNESS
Parent B44 run 36277246562 valid ROBUST_TWO_POSITION_RECENCY_BAND.
Question: does recovery at destination5/6 remain robust when the entire nonqueried binding order is changed, or does the confirmed recency band still depend on broader binding identity/order?
Freeze exact B44 model/training/evaluation, threshold .90, 120 parameters, 32 state scalars, deterministic Torch, seeds [111,222,333,444,555], first-read query strata q=[0,1,2,3,4,5], seven active bindings, exact held-out evaluation set. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
Destinations: d in [5,6] when d!=q.
For each seed/query/destination:
- place the queried binding exactly at d;
- fill the six remaining destination slots using twelve preregistered orderings of the six remaining source bindings:
  1 identity source order,
  2-6 cyclic left rotations by 1..5,
  7 reversed source order,
  8-12 cyclic left rotations by 1..5 of the reversed order.
Ordering family is fixed mechanically before outcomes.
Each arm is a pure permutation of the seven original four-token binding blocks; the queried binding stays at d and the full binding multiset is preserved.
Also reproduce the corresponding B44 designated-parking arm for each eligible seed/query/destination as an inherited anchor.
Classification:
FULL_BACKGROUND_ORDER_ROBUST_RECENCY if every d5 and d6 order arm is capable across every eligible seed/query stratum.
LATEST_ONLY_BACKGROUND_ORDER_ROBUST if all d6 order arms are capable but at least one d5 order arm is not.
BACKGROUND_ORDER_SENSITIVE_RECENCY if either destination has both capable and noncapable order arms while inherited anchors reproduce.
ANCHOR_NOT_REPRODUCED if any inherited B44 designated-parking anchor fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/query strata/destination set/order family; every stratum nonempty; threshold/state/params exact; inherited B44 anchors exact; queried binding at destination exact; multiset preserved every arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
