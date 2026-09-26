YGG-B34 PREREGISTRATION — 5<->3 ORDER-EFFECT PORTABILITY
Parent B33 run 36253384940 valid ORDER_SUFFICIENT_PARTIAL.
Question: does the exact composition-preserving reciprocal swap positions 5<->3 that restored seed222/query4 capability generalize across the other frozen B31 seeds, or is it seed-specific?
Freeze exact B31/B33 model/training/evaluation, threshold .90, 120 params, 32 state scalars, query position4, deterministic Torch, seeds [111,222,333,444,555]. No retraining/adaptation/capacity/architecture/threshold/baseline changes.
Design: for each fixed seed evaluate original and exactly one reciprocal 5<->3 swap; preserve exact seven-binding multiset; seed222 must reproduce B33 original and swap endpoints. No seed selection after outcomes.
Classify PORTABLE_ORDER_EFFECT if swap improves accuracy in all five seeds and does not reduce number capable; PARTIAL_PORTABILITY if improves >1 but <5 seeds; SEED222_SPECIFIC if only seed222 improves; MIXED_ORDER_EFFECT otherwise.
Validity: exact seeds/query/threshold/state/params; seed222 endpoints reproduced; multiset preserved every row; duplicate byte-identical.
