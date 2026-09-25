TITLE: YGG-C8 Learned-Blend Interaction Onset Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: c19a8f5bb5f0f446bf6b09dbd711b41b58ecbb4a
PARENT_EXPERIMENT: YGG-C7
SCIENTIFIC_PARENT: YGG-C6 / LU-2V

QUESTION
Does the A25-only A/C resource-pressure interaction emerge at a partial learned-control blend, or only at the accepted full alpha=0.25 blend?

NORTH-STAR TARGET
Isolate the mechanism behind a learned-developmental robustness interaction before broader scaling or integration.

FROZEN
- exact accepted LU-2V weights and learned controller;
- exact ten primary manifests;
- exact C6 L10 base and A/B/C transition cells for every replicate;
- exact eight factorial lesion conditions:
  000,100,010,001,110,101,011,111;
- exact task, arrivals, programs, corruption, anchors, horizon, recovery semantics, matching, service capacity, and retention criteria;
- exact deterministic execution;
- no weight update or online adaptation.

SCIENTIFIC CHANGE
Vary only the runtime U learned-blend coefficient used by the already-frozen U_A25 control path.

Test exactly:
alpha=0.0
alpha=0.125
alpha=0.25

The accepted model weights, observations, logits, teacher distribution, task state, and lesion sets remain unchanged.

ALPHA=0 TEACHER-PARITY GATE
At alpha=0.0, the U_A25 execution path must reproduce U_A0 compact outcomes and maturity evidence on the exact L8 parent worlds.
If this parity fails, C8 is invalid rather than scientifically negative.

ALPHA=0.25 REPRODUCTION GATE
At alpha=0.25, retained_by_condition must exactly reproduce accepted C7:
000=true
100=false
010=true
001=true
110=false
101=true
011=true
111=true

and classification must be INTERACTION_DRIVEN with context-dependent slots A,C.

ARM-SPECIFIC RETENTION
For each alpha and factorial condition, evaluate the U_A25 path relative to that same alpha's exact L8 parent:
- aggregate correct-completion area >=90% of same-alpha L8;
- incorrect_done total ==0;
- matching duplicate cell/request violations ==0;
- maturity passes in every world;
- stream non-collapse relative to same-alpha L8.

INTERACTION CLASSIFICATION
For each alpha:
- compute exact C6 paired Boolean effects for slots A/B/C;
- context-dependent slot definition is unchanged;
- INTERACTION_DRIVEN requires the C6 path
  000=true,100=false,110=false,111=true
  and at least one context-dependent slot.

PRIMARY ONSET CLASSIFICATION
If alpha=0 is not interaction-driven, alpha=0.125 is interaction-driven, and alpha=0.25 is interaction-driven:
  ONSET_BY_0125

If alpha=0 is not interaction-driven, alpha=0.125 is not interaction-driven, and alpha=0.25 is interaction-driven:
  ENDPOINT_ONLY_025

Any other valid pattern:
  OTHER_NONMONOTONIC_PATTERN

The alpha=0 teacher-parity and alpha=0.25 accepted-map gates remain validity requirements regardless of onset category.

REPORT
For each alpha:
- retained map;
- paired Boolean effects;
- context-dependent slots;
- interaction classification;
- L8 parent aggregate;
- completion/stream/maturity/matching summaries for all eight conditions.
Also report:
- first tested alpha with interaction;
- primary onset classification;
- duplicate evidence hash.

VALIDITY
- exact C6 factorial lesion sets at every alpha;
- non-lesion manifest lineage frozen;
- alpha=0 teacher parity exact on L8 parent;
- alpha=0.25 accepted C7 map exact;
- alpha=0.25 context slots exactly A,C;
- all matching integrity exact;
- duplicate complete C8 execution byte-identical.

SUCCESS
YGG_C8_LEARNED_BLEND_INTERACTION_ONSET=true iff all validity gates pass and a primary onset classification is produced.
No particular valid onset category is required.

FAILURE
Do not change alpha levels, lesions, thresholds, seeds, weights, task, or retention criteria after observing results.

BOUNDARY
No accepted LU-2V mutation.
No learned-weight update.
No online adaptation.
No shared-baseline promotion from C8 alone.
No recursive self-modification.
No external runtime modification.
