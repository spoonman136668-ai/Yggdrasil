YGG-B44 PREREGISTRATION — RECENCY-BAND PARKING ROBUSTNESS
Parent B43 run 36275111281 valid RECENCY_BAND with destinations5 and6 universally capable under one deterministic parking choice.
Question: are destination5 and destination6 sufficient independent of where displaced content is parked, and is destination4 genuinely outside that band?
Freeze exact B43 model/training/evaluation, threshold .90, 120 params, 32 state scalars, deterministic Torch, seeds [111,222,333,444,555], query strata q=[0,1,2,3,4,5], seven active bindings, exact held-out evaluation set. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
Destinations tested: d in [4,5,6] whenever d!=q.
For each seed/query/destination, enumerate every valid parking position p such that p!=q, p!=d, and:
- if d==6: p is any position in [0..5] except q;
- if d in [4,5]: p is any position in [0..5] except q and d; position6 is never parking, so original latest-write content is not moved into q.
Apply the same pure three-cycle q->d, d->p, p->q. Evaluate on the same query stratum. Preserve the exact seven-binding multiset.
B43's preregistered parking arm for each eligible d=4,5,6 must reproduce exactly as an inherited anchor.
Classification:
ROBUST_TWO_POSITION_RECENCY_BAND if every d5 and d6 arm is capable across every valid parking position and d4 is not universally capable.
ROBUST_THREE_POSITION_BAND if d4,d5,d6 are all universally capable across parking.
LATEST_ONLY_AFTER_PARKING if d6 is universally capable but d5 is not.
PARKING_SENSITIVE_RECENCY if d5 or d6 has mixed capable/noncapable outcomes across parking while inherited B43 anchors reproduce.
ANCHOR_NOT_REPRODUCED if inherited B43 designated-parking endpoints fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/query/destination/parking enumeration; every query stratum nonempty; threshold/state/params exact; inherited B43 arms exact; multiset preserved every arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
