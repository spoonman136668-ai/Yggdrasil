YGG-B43 PREREGISTRATION — QUERIED-BINDING DESTINATION / RECENCY SWEEP
Parent B42 run 36273730650 valid TARGET_TO_LATEST_SUFFICIENT.
Question: is latest position6 uniquely sufficient for first-read recovery, or does relocating the queried binding to other write positions reveal a broader positional/recency band?
Freeze exact B42 model/training/evaluation, threshold .90, 120 params, 32 state scalars, deterministic Torch, seeds [111,222,333,444,555], first-read query strata q=[0,1,2,3,4,5], seven active bindings, exact held-out evaluation set. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
For each seed, query stratum q, and destination d in [0,1,2,3,4,5,6] with d!=q:
- choose parking p as the smallest position in [0..6] distinct from q and d, fixed mechanically before outcomes;
- apply pure three-cycle q->d, d->p, p->q, so the queried binding moves to d while original d content does not move into q;
- evaluate accuracy on the same q stratum.
Also evaluate ORIGINAL for each q.
The d=6 arms must reproduce B42 TARGET_TO_LATEST_ONLY accuracy 1.0 in every seed/q stratum.
Classify LATEST_ONLY if d=6 is portable in every eligible seed/q stratum and no other destination is universally portable across its eligible strata; RECENCY_BAND if d=6 and at least one other destination are universally portable; POSITION_INVARIANT if every destination is universally portable; PARTIAL_POSITION_PATTERN otherwise; ANCHOR_NOT_REPRODUCED if any d=6 inherited endpoint fails.
Validity: exact seeds/query strata/destination set/parking rule; every evaluated stratum nonempty; exact threshold/state/params; B42 d6 endpoints exact; exact seven-binding multiset preserved in every transformed arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
