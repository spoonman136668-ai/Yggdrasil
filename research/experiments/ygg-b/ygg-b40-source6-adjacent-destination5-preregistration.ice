YGG-B40 PREREGISTRATION — SOURCE-6 ADJACENT DESTINATION-5
Parent B39 run 36269419517 valid DESTINATION4_SPECIFIC across destinations0..4.
Question: does source6 also produce portable rescue when moved one slot earlier to destination5, or is destination4 the only portable source6 destination?
Freeze exact B39 model/training/evaluation, threshold .90, 120 params, 32 state scalars, query position4, deterministic Torch, seeds [111,222,333,444,555]. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
Design: for each fixed seed evaluate original plus exactly two reciprocal composition-preserving swaps: 6<->4 (frozen positive anchor) and 6<->5 (previously untested across the full five-seed set). Preserve the exact seven-binding multiset in every arm. No other destination may be added after outcomes.
Classify ADJACENT5_PORTABLE if 6<->4 and 6<->5 are both portable across all five seeds; DESTINATION4_ONLY if 6<->4 is portable across all five and 6<->5 is not; ANCHOR_NOT_REPRODUCED if 6<->4 fails its B39 endpoints; OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/query/threshold/state/params; exact B39 6<->4 per-seed endpoints reproduced; exact destinations [4,5]; exact binding multiset preserved every arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
