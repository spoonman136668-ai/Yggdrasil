YGG-A40 PREREGISTRATION — CELL2 SINGLETON PORTABILITY ACROSS PRIMARY REPLICATES
Parent A39 run 36275113326 valid CELL2_SINGLETON_SUFFICIENT in replicate6.
Question: is singleton cell2 sensitivity intrinsic across the frozen primary replicate population, or specific to replicate6 identity?
Freeze exact A39 substrate: A1 primary manifests, target cell2, alpha=.25, U_A0/U_A25, task, learned weights, scheduler, horizon, service capacity, maturity, matching, terminal-integrity rules; repair off; deterministic; no retraining/adaptation/threshold/topology/baseline changes.
Population: every manifest returned by the exact frozen primary-manifest set. Do not apply A27's L11 eligibility filter. Report and verify actual replicate IDs before classification.
Design per mode and replicate:
1. score exact zero-lesion reference [] while preserving all non-lesion manifest fields;
2. score exact singleton lesion [2];
3. apply the inherited A28 collapse predicate using that replicate's zero-lesion score as anchor and [2] as current.
No other lesions are permitted.
Classify GLOBAL_SINGLETON_SENSITIVITY if every primary replicate collapses in both modes; REPLICATE6_SPECIFIC if the only collapsing replicate is6 in both modes; MULTIREPLICATE_SINGLETON_SENSITIVITY if the same subset of two or more but not all replicates collapses in both modes; CROSS_MODE_SINGLETON_DIFFERENCE if collapsing sets differ; NO_SINGLETON_EFFECT if no replicate collapses; OTHER_VALID_PATTERN otherwise.
Validity: duplicate byte-identical; exact alpha/modes/target; full frozen primary replicate population verified consistently across modes; exact [] and [2] lesions; non-lesion bytes frozen; maturity/matching/terminal integrity/zero branch damage every arm; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
