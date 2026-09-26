YGG-B35 PREREGISTRATION — POSITION-5 DESTINATION SPECIFICITY
Parent B34 run 36255030345 valid PORTABLE_ORDER_EFFECT.
Question: is the portable composition-preserving 5<->3 rescue specific to destination position 3, or does reciprocal relocation of position-5 content to nearby earlier positions provide the same cross-seed rescue?
Freeze exact B34 model/training/evaluation, threshold .90, 120 params, 32 state scalars, query position4, deterministic Torch, seeds [111,222,333,444,555]. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
Design: for each fixed seed evaluate original plus exactly three reciprocal composition-preserving swaps: 5<->2, 5<->3, 5<->4. The 5<->3 arm is the preregistered B34 positive anchor. Preserve the exact seven-binding multiset in every arm. No additional destinations may be added after outcomes.
Classify POSITION3_ONLY_PORTABLE if 5<->3 yields capability in all five seeds and neither flank does; ALTERNATE_DESTINATION_PORTABLE if 5<->3 and at least one flank each yield capability in all five seeds; BROAD_LOCAL_PORTABILITY if all three yield capability in all five seeds; ANCHOR_NOT_REPRODUCED if 5<->3 fails to reproduce all five B34 endpoints/capability; OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/query/threshold/state/params; exact B34 5<->3 per-seed endpoints reproduced; exact binding multiset preserved every arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
