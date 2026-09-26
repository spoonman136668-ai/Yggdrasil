YGG-B39 PREREGISTRATION — SOURCE-6 DESTINATION SPECIFICITY
Parent B38 run 36268329756 valid MULTISOURCE_DESTINATION4. B37 showed source6->destination3 capability only 2/5, while B38 showed source6->destination4 capability 5/5.
Question: is source6 intrinsically a broadly rescuing source, or is its portable effect specific to destination4?
Freeze exact B38/B37 model/training/evaluation, threshold .90, 120 params, 32 state scalars, query position4, deterministic Torch, seeds [111,222,333,444,555]. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
Design: for each fixed seed evaluate original plus exactly five reciprocal composition-preserving swaps from source6 to destinations [0,1,2,3,4]. Destination3 is the frozen B37 partial anchor; destination4 is the frozen B38 portable positive anchor. Preserve the exact seven-binding multiset in every arm. No destinations may be added or removed after outcomes.
Classify DESTINATION4_SPECIFIC if destination4 is portable across all five seeds and no other tested destination is portable across all five; MULTIDESTINATION_SOURCE6 if destination4 and at least one other tested destination are portable across all five; ANCHOR_NOT_REPRODUCED if destination3 or4 fails its inherited behavior; OTHER_VALID_PATTERN otherwise.
Validity: exact seeds/query/threshold/state/params; exact inherited source6->destination3 and source6->destination4 per-seed endpoints reproduced; exact destinations [0,1,2,3,4]; exact binding multiset preserved every arm; duplicate byte-identical.
Scientific negatives are valid. No post-result tuning.
