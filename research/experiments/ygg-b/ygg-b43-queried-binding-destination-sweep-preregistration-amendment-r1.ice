YGG-B43 PREREGISTRATION AMENDMENT R1 — PRE-IMPLEMENTATION PARKING RULE CORRECTION
Parent preregistration commit: 0caae820b16e7ec3adaa3d304563aa2bc20a62ac
Status at amendment: no YGG-B43 implementation committed; no YGG-B43 workflow registered; no YGG-B43 execution or outcome observed.

Reason:
The parent text specified a generic smallest-distinct parking rule while also requiring d=6 arms to reproduce B42 TARGET_TO_LATEST_ONLY exactly. Those two requirements conflict because B42 used parking p=(q+1) mod 6. The generic rule could also select position6 as parking for d<6, contaminating the intended directional isolation by moving original position6 content into q.

Frozen corrected parking rule:
- if destination d==6: p=(q+1) mod 6, exactly reproducing B42 TARGET_TO_LATEST_ONLY.
- if destination d!=6: p is the smallest position in [0,1,2,3,4,5] distinct from q and d. Position6 is never used as parking in these arms.
- apply the same pure three-cycle q->d, d->p, p->q.
Thus every transformed arm relocates the queried binding to d while preventing original destination content from entering q, and d=6 is an exact inherited B42 anchor.

All seeds, query strata, destinations, threshold, state, parameters, model/training/evaluation, classifications, multiset checks, duplicate criterion, and no-post-result-tuning rule remain unchanged.
