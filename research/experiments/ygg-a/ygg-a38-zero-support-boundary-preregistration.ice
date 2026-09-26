YGG-A38 PREREGISTRATION — REPLICATE-6 CELL-2 ZERO-L11-SUPPORT BOUNDARY
Parent A37 run 36272092354 valid NO_TEN_NECESSITY.
Question: does cell2-associated collapse persist after removing all eleven members of exact L11, leaving cell2 as the only lesion member, and is that result mode-stable?
Freeze exact A37 substrate: replicate6; L11=[7,15,23,29,31,32,39,47,52,55,63]; target cell2; alpha=.25; U_A0/U_A25; task/manifests/weights/scheduler/horizon/maturity/integrity; repair off; deterministic; no retraining/adaptation/threshold/topology/baseline changes.
Design: per mode reproduce the frozen L11 anchor and L11+cell2 positive-control collapse, then evaluate exactly one zero-support arm with lesion=[2], equivalent to removal of all 11 L11 members. No other lesion composition is permitted.
Classify ZERO_SUPPORT_COLLAPSE if lesion=[2] retains collapse in both modes; L11_SUPPORT_REQUIRED if lesion=[2] abolishes collapse in both modes; MODE_SPECIFIC_ZERO_SUPPORT if modes differ; OTHER_VALID_PATTERN otherwise.
Validity: duplicate byte-identical; exact replicate/L11/cell2/alpha/modes; positive controls; lesion exactly [2]; maturity/integrity preserved.
Scientific negatives are valid. No post-result tuning.
