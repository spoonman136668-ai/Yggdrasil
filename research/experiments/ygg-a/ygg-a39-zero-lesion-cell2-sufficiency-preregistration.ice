YGG-A39 PREREGISTRATION — TRUE ZERO-LESION REFERENCE / CELL2 SUFFICIENCY
Parent A38 run 36273728981 valid ZERO_SUPPORT_COLLAPSE relative to historical L11 anchor.
Question: does singleton lesion cell2 itself induce the registered stream-collapse phenotype when compared against a true zero-lesion reference, and is the result mode-stable?
Freeze exact A38 substrate: replicate6 manifest identity outside lesion field; target cell2; alpha=.25; U_A0/U_A25; task, learned weights, scheduler, horizon, service capacity, maturity, matching, terminal-integrity rules; repair off; deterministic; no retraining/adaptation/threshold/topology/baseline changes.
Design per mode:
1. score exact zero-lesion reference lesion=[].
2. score exact singleton target lesion=[2].
3. apply the inherited A28 collapse predicate using zero-lesion as anchor and [2] as current.
Also reproduce the historical L11 anchor and L11+cell2 collapse only as provenance anchors; they do not define the A39 scientific comparison.
No other lesions are permitted.
Classify CELL2_SINGLETON_SUFFICIENT if [2] collapses versus [] in both modes; CELL2_SINGLETON_NOT_SUFFICIENT if neither mode collapses; MODE_SPECIFIC_SINGLETON if modes differ; OTHER_VALID_PATTERN otherwise.
Validity: duplicate byte-identical; actual replicate6; exact alpha/modes/target; zero lesion exactly []; singleton exactly [2]; historical positive control reproduced; maturity/matching/terminal integrity/zero branch damage for both scientific arms; non-lesion manifest bytes frozen.
Scientific negatives are valid. No post-result tuning.
