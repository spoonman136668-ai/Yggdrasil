YGG-B36 PREREGISTRATION — POSITION-5 EARLY-DESTINATION PORTABILITY
Parent B35 run 36257434829 valid ALTERNATE_DESTINATION_PORTABLE.
Question: does the composition-preserving position-5 rescue reappear at earlier destinations 0 or 1, or is portable rescue localized to the later positional window already bounded by destination2 failure and destination3 success?
Freeze exact B35 model/training/evaluation, threshold .90, 120 params, 32 state scalars, query position4, deterministic Torch, seeds [111,222,333,444,555]. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
Design: for each fixed seed evaluate original plus exactly four reciprocal composition-preserving swaps: 5<->0, 5<->1, 5<->2, 5<->3. Destination2 is the frozen B35 negative anchor; destination3 is the frozen B35 positive anchor. Preserve the exact seven-binding multiset in every arm. No additional destinations may be added after outcomes.
Classify LOCAL_WINDOW_CONFIRMED if neither destination0 nor1 is portable across all five seeds while destination2 remains nonportable and destination3 remains portable; EARLY_REENTRY if destination0 or1 is portable across all five seeds while anchors reproduce; ANCHOR_NOT_REPRODUCED if destination2 or3 fails its B35 anchor behavior; OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/query/threshold/state/params; exact B35 destination2 and destination3 per-seed endpoints reproduced; exact binding multiset preserved every arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
