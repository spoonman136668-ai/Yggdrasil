YGG-B37 PREREGISTRATION — DESTINATION-3 SOURCE SPECIFICITY
Parent B36 run 36264388367 valid LOCAL_WINDOW_CONFIRMED.
Question: is the portable reciprocal rescue at destination3 specific to source position5 content, or is destination3 generically improved by reciprocal exchange with other source positions?
Freeze exact B36 model/training/evaluation, threshold .90, 120 params, 32 state scalars, query position4, deterministic Torch, seeds [111,222,333,444,555]. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
Design: for each fixed seed evaluate original plus exactly five reciprocal composition-preserving swaps into destination3 from sources [0,1,2,5,6]. Source4 is excluded because query position4 is the evaluated target context and changing it would alter a distinct factor. The 5<->3 arm is the frozen B36 positive anchor. Preserve the exact seven-binding multiset in every arm. No sources may be added or removed after outcomes.
Classify SOURCE5_SPECIFIC if source5 is portable across all five seeds and no other tested source is portable across all five; MULTISOURCE_DESTINATION3 if source5 and at least one other tested source are portable across all five; SOURCE5_NOT_REPRODUCED if the 5<->3 anchor fails; OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/query/threshold/state/params; exact B36 5<->3 per-seed endpoints reproduced; exact sources [0,1,2,5,6]; exact binding multiset preserved every arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
