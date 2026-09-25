TITLE: YGG-C4 Fixed-Cardinality Lesion Topology Sensitivity Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: 8fb0d5fcb5aeaf3379f02ea680fd4728984f80e4
FROZEN_SCIENTIFIC_PARENT: LU-2V / YGG-C3

QUESTION
At a fixed temporary lesion cardinality of 16 of 64 cells, is capability retention controlled materially by the spatial topology of the lesion rather than cell count alone?

RATIONALE
C3 retained the full frozen capability envelope at L16 while L12, L24, and L32 failed stream non-collapse. The non-monotonic cardinality result motivates a fixed-cardinality topology test.

FROZEN
- exact LU-2V source, weights, alpha, ten primary manifests, task, arrivals, programs, corruption, anchors, horizon, recovery semantics, and A0/A25 arms;
- lesion_cells=16 exactly;
- exact C3 aggregate retention criteria;
- no horizon, load, service-capacity, model, or learned-authority change;
- duplicate complete execution.

TOPOLOGIES
For every seed generate exactly 16 unique lesion cells:

HASH16
Exact C3 deterministic nested-hash L16 set.

CONTIGUOUS16
start = h64("YGG-C4-CONTIGUOUS",seed) mod 64.
Lesion the 16 consecutive ring cells start..start+15 modulo 64.

EVEN16
offset = h64("YGG-C4-EVEN",seed) mod 4.
Lesion offset + 4*i for i=0..15.

TWO_ARC16
start = h64("YGG-C4-TWO-ARC",seed) mod 32.
Lesion 8 consecutive cells from start and 8 consecutive cells from start+32.

FOUR_ARC16
start = h64("YGG-C4-FOUR-ARC",seed) mod 16.
Lesion four consecutive cells beginning at start, start+16, start+32, and start+48.

PRIMARY HYPOTHESIS
Topology sensitivity is supported iff, under the exact C3 retention criteria, at least one preregistered topology is retained and at least one preregistered topology is not retained.

C3 RETENTION CRITERIA
Relative to the exact inherited L8 parent:
- A25 aggregate correct-completion area >= 90% of L8;
- incorrect_done total == 0;
- matching duplicate cell/request violations == 0;
- maturity/repair integrity passes;
- stream non-collapse: for every matched replicate/phase/stream with L8 A25 >=4 completions, topology A25 >=75% of matched L8.

REPORT
For each topology:
- aggregate A0/A25 completion area;
- A25 retention ratio;
- total correct, incorrect, expired, backlog;
- maturity and matching integrity;
- stream non-collapse;
- retained yes/no;
- per-world lesion set and stream-phase counts.

VALIDITY
- all lesion sets exactly 16 unique cells;
- each topology exactly follows its preregistered deterministic construction;
- all non-lesion manifest fields frozen;
- current parent L8 execution remains byte-identical to the C3 parent reference under the same run;
- duplicate complete C4 executions byte-identical.

FAILURE
If all topologies share the same retained/not-retained classification, C4 is a scientific negative for the preregistered topology-sensitivity hypothesis.
Do not alter topology families or thresholds after observing results.

BOUNDARY
No accepted LU-2V mutation.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
