TITLE: YGG-C10 Learned-Blend Onset Bisection Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: 193f06d96b9807e43071a228dcc93a4de706da4c
PARENT_EXPERIMENT: YGG-C9

QUESTION
Does the learned developmental A/C interaction begin by alpha=0.15625, or only above it?

NORTH-STAR TARGET
Refine the learned-control boundary without changing mechanism, task, lesions, weights, or retention semantics.

FROZEN FROM YGG-C9
- exact accepted learned weights;
- exact C6 manifests and factorial lesion conditions;
- exact task, programs, arrivals, corruptions, anchors, horizon, recovery, matching, service capacity, seeds, and retention definition;
- exact interaction classifier;
- harness-only temporary dose allowlist extension with exact restoration;
- duplicate deterministic execution.

TEST EXACTLY
alpha=0.125
alpha=0.15625
alpha=0.1875

ANCHORS
alpha=0.125 must reproduce C9:
interaction_driven=false
duplicate_sha256=9f6a7bf9f64ee726a1f705a17cce22c99a9996d2dfa883c0740c3d2fc8bbfc26

alpha=0.1875 must reproduce C9:
interaction_driven=true
context slots=A,C
duplicate_sha256=75e0993a93235bb08e00461c855f42a5ca220abe778a803492283282469ad7b4

PRIMARY CLASSIFICATION
If alpha=0.15625 is interaction-driven:
ONSET_BETWEEN_0125_AND_015625

If alpha=0.15625 is not interaction-driven:
ONSET_BETWEEN_015625_AND_01875

Any failure of the two endpoint anchors is invalidity, not a scientific negative.

VALIDITY
- alpha levels exact and ordered;
- endpoint duplicate hashes exact;
- endpoint interaction states exact;
- alpha=.1875 context slots exactly A,C;
- exact factorial lesions and non-lesion lineage at every alpha;
- learned weight identity exact;
- matching integrity exact;
- duplicate execution byte-identical;
- runtime alpha and dose allowlist restored exactly.

SUCCESS
YGG_C10_LEARNED_BLEND_ONSET_BISECTION=true iff all validity gates pass and one preregistered half-interval is selected.

FAILURE
Do not alter alphas, weights, lesions, thresholds, manifests, seeds, task semantics, or classification after observing results.

BOUNDARY
No accepted source mutation.
No learned-weight update.
No online adaptation.
No shared-baseline promotion.
No recursive self-modification.
