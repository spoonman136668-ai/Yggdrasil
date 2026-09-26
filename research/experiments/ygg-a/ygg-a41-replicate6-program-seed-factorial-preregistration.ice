YGG-A41 PREREGISTRATION — REPLICATE6 PROGRAM / SEED-CONTEXT FACTORIAL
Parent A40 run 36276039607 valid REPLICATE6_SPECIFIC for singleton cell2 sensitivity.
Question: does replicate6-specific cell2 sensitivity follow replicate6's program composition, its seed-derived context, or an interaction between them?
Freeze exact A40 substrate: alpha=.25; U_A0/U_A25; target cell2; A1 primary-manifest population; exact task, learned weights, scheduler, horizon, service capacity, maturity, matching, terminal-integrity rules; repair off; deterministic; no retraining/adaptation/threshold/topology/baseline changes.
Definitions:
- PROGRAM composition = exact manifest["programs"] field.
- SEED-CONTEXT = seed plus fields deterministically derived from seed and programs/context: arrivals, corrupt_ids, anchors0, anchors4, seed namespace / replicate metadata as carried by the context donor. Constant substrate/lineage fields remain frozen.
For every non6 partner replicate r in the primary population create two preregistered hybrid families:
A. R6_PROGRAM_IN_R_CONTEXT: copy partner-r primary manifest context, replace programs with exact replicate6 programs, recompute arrivals from partner seed + R6 programs, recompute corrupt_ids from partner seed + recomputed arrivals, retain partner-seed anchors, then evaluate [] and [2].
B. R_PROGRAM_IN_R6_CONTEXT: copy replicate6 primary context, replace programs with exact partner-r programs, recompute arrivals from replicate6 seed + partner programs, recompute corrupt_ids from replicate6 seed + recomputed arrivals, retain replicate6-seed anchors, then evaluate [] and [2].
Hybrid manifests use an explicit preregistered validator that checks all frozen constants and deterministic field relationships but does not require the original primary replicate->program mapping.
Also reproduce native replicate6 []/[2] collapse and every native partner []/[2] noncollapse as anchors.
Classification:
SEED_CONTEXT_DOMINANT if every B-family hybrid collapses and no A-family hybrid collapses in both modes.
PROGRAM_DOMINANT if every A-family hybrid collapses and no B-family hybrid collapses in both modes.
BOTH_COMPONENTS_INDEPENDENTLY_SUFFICIENT if every hybrid in both families collapses in both modes.
INTERACTION_REQUIRED if no hybrid in either family collapses in both modes while native replicate6 does.
MIXED_PROGRAM_SEED_INTERACTION for any other valid stable pattern.
CROSS_MODE_FACTORIAL_DIFFERENCE if hybrid collapsing sets differ between modes.
ANCHOR_NOT_REPRODUCED if native A40 anchors fail.
Validity: actual primary IDs [1..10] verified; exact partner set all non6; native anchors exact; hybrid deterministic relationships exact; []/[2] lesions exact; non-exchanged constant fields frozen; scientific integrity every arm; duplicate byte-identical; runtime validator/lesion/alpha restored.
Scientific negatives are valid. No post-result tuning.
