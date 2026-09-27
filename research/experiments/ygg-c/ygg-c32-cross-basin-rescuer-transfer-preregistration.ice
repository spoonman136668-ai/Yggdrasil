YGG-C32 PREREGISTRATION — CROSS-BASIN TRANSFER OF PRESSURE-PORTABLE RESCUERS 40/45
Parent C31 valid NOVEL_RESCUERS_PRESSURE_SPECIFIC.
Question: do the two pressure-portable F-state rescuers40 and45 also repair the original replicate8 failure basin?
Freeze exact corrected C31/C25 substrate: replicate8 identity, alpha0.134765625, levels8..16, exact manifests/weights/task/scheduler/retention/maturity, deterministic.
At each level start from ORIGINAL_R8 lesion, which must fail.
Evaluate single additions:
ADD40
ADD45
Context controls:
ADD41
ADD47
Inherited C25 controls:
ADD2 must reproduce rescue only levels14..16.
ADD10 must reproduce no rescue at levels8..16.
No removal or other lesion change.
Classification:
CROSS_BASIN_PORTABLE_40_45 if ADD40 and ADD45 both rescue all levels8..16.
PARTIAL_CROSS_BASIN_PORTABILITY if either40 or45 rescues at least one but not both rescue all levels.
F_STATE_SPECIFIC_40_45 if neither40 nor45 rescues any level.
ANCHOR_NOT_REPRODUCED if ORIGINAL_R8 or C25 ADD2/ADD10 anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact levels8..16; alpha/replicate exact; original lesion exact; exactly six registered single-addition arms; each differs by exactly one cell membership; inherited ADD2/ADD10 outcomes exact; duplicate byte-identical; globals restored.
Scientific negatives are valid. No post-result tuning.
