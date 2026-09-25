TITLE: YGG-C5 Fine Nested Resource-Pressure Transition Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: ef52ad725460b9ba6f9f77b84910bbe7068ad7a1
PARENT_EXPERIMENT: YGG-C4
SCIENTIFIC_PARENT: YGG-C3 / LU-2V
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Along the exact deterministic nested C3 lesion construction, does capability recovery between the known L12 failure and L16 retention form a threshold-like retained plateau, or an irregular alternating transition?

RATIONALE
C3 established a non-monotonic nested result: L8 retained, L12 not retained, L16 retained.
C4 showed that five coarse L16 geometries all retain, arguing against L16 retention being a fragile coarse-topology accident.
C5 resolves the transition at single-cell cardinality increments without changing lesion ranking or any scientific parent mechanism.

FROZEN
- exact accepted LU-2V source, weights, alpha, ten primary manifests, task, arrivals, programs, corruption, anchors, horizon, recovery semantics, and A0/A25 arms;
- exact C3 deterministic nested hash ranking for additional lesion cells;
- exact C3 L8 parent set;
- exact C3 retention criteria;
- no model, scheduler, load, service-capacity, horizon, seed, or learned-authority change;
- duplicate complete execution.

PRESSURE LEVELS
Evaluate exactly:
8,9,10,11,12,13,14,15,16 lesion cells out of 64.

NESTED CONSTRUCTION
For every seed:
- L8 is the exact inherited LU-2V lesion set;
- rank every remaining cell by:
  h64("YGG-C3-RESOURCE-PRESSURE", seed, cell), then cell index;
- Lk = L8 plus the first k-8 ranked remaining cells.

Thus L8 subset L9 subset ... subset L16 exactly.

RETENTION CRITERIA
For each level relative to exact L8 A25:
- aggregate correct-completion area >= 90% of L8;
- incorrect_done total == 0;
- matching duplicate cell/request violations == 0;
- maturity/repair integrity passes;
- stream non-collapse: for every matched replicate/phase/stream with L8 A25 >=4 completions, Lk A25 >=75% of matched L8.

PRIMARY CLASSIFICATION
A threshold-like recovery is supported iff there exists a threshold k in {13,14,15,16} such that:
- at least one level in 9..12 is not retained;
- every tested level from k through 16 is retained; and
- every tested level from 12 through k-1 is not retained.

If no such k exists, classify the transition as irregular/non-threshold under this preregistered definition.

REPORT
- retained/not-retained for every cardinality 8..16;
- exact threshold k if supported;
- aggregate A0/A25 completion area;
- A25 retention ratio vs L8;
- total correct, incorrect, expired, backlog;
- maturity and matching integrity;
- stream non-collapse;
- per-world stream-phase counts and lesion sets.

VALIDITY
- every level has exact cardinality;
- lesion sets are strictly nested by one cell at each increment;
- L8 exactly equals inherited LU-2V lesion set;
- non-lesion manifest fields remain frozen;
- L8 parent evidence SHA256 equals 7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1;
- duplicate complete C5 executions byte-identical.

FAILURE
Failure of threshold-like recovery is a valid scientific result.
Do not change the level set, ranking, thresholds, seeds, task, or retention definition after observing results.

BOUNDARY
No accepted LU-2V mutation.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
No external runtime modification.
