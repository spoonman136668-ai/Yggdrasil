YGG-A42 PREREGISTRATION — RUNTIME SEED IDENTITY VS REQUEST REALIZATION
Parent A41 run 36278456398 valid SEED_CONTEXT_DOMINANT.
Question: does replicate6-specific singleton-cell2 sensitivity follow replicate6's runtime/spatial seed identity, its realized request/corruption stream, or their interaction?
Freeze exact A41/A40 substrate: alpha=.25; U_A0/U_A25; target cell2; primary IDs1..10; exact task, learned weights, scheduler, horizon, service capacity, maturity, matching and terminal-integrity rules; repair off; deterministic; no retraining/adaptation/threshold/topology/baseline changes.
Programs: use exact replicate6 program composition in every A42 arm, eliminating program identity as a variable after A41.
For each non6 partner r, construct:
A. R6_RUNTIME_PARTNER_REQUEST: runtime context/seed/namespace/replicate metadata and seed-derived anchors from replicate6; arrivals and corrupt_ids generated from partner-r seed using the fixed replicate6 programs.
B. PARTNER_RUNTIME_R6_REQUEST: runtime context/seed/namespace/replicate metadata and seed-derived anchors from partner r; arrivals and corrupt_ids generated from replicate6 seed using the fixed replicate6 programs.
The runtime seed therefore controls all runtime seed-hash behavior and anchors; the request donor controls the exact request bits/program bindings in arrivals and scheduled corruption IDs. Constant substrate/lineage fields remain those of the runtime context.
Also reproduce native fixed-program anchors: replicate6 runtime+request collapses; every non6 runtime+own-request does not.
Evaluate exact [] versus [2] per arm with inherited A28 collapse predicate.
Classification:
RUNTIME_SEED_DOMINANT if every A-family hybrid collapses and no B-family hybrid collapses in both modes.
REQUEST_REALIZATION_DOMINANT if every B-family hybrid collapses and no A-family hybrid collapses in both modes.
BOTH_COMPONENTS_INDEPENDENTLY_SUFFICIENT if both families universally collapse.
RUNTIME_REQUEST_INTERACTION_REQUIRED if neither family collapses while native replicate6 does.
MIXED_RUNTIME_REQUEST_INTERACTION for any other stable valid pattern.
CROSS_MODE_CONTEXT_DIFFERENCE if family collapsing sets differ by mode.
ANCHOR_NOT_REPRODUCED if native fixed-program anchors fail.
Validity: primary/partner IDs exact; donor/runtime seeds dynamically attested; replicate6 programs exact; request arrivals and corrupt_ids exactly regenerated from the designated donor seed; anchors exactly match runtime seed; []/[2] exact; constants frozen; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
