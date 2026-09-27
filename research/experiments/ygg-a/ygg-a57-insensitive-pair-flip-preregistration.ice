YGG-A57 PREREGISTRATION — PAIRWISE INTERACTIONS AMONG A56 SINGLE-FLIP-INSENSITIVE POSITIONS
Parent A56 run 36316830109 valid DISTRIBUTED_STREAM_SENSITIVITY.
Question: are the eight phase3 positions whose individual stream flips preserve collapse genuinely noncausal, or do they contain redundant/higher-order causal interactions revealed by pair flips?
Freeze exact A56 native substrate: replicate6 runtime/programs/arrival stream, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Frozen A56 insensitive set I={103,105,106,111,117,121,123,125}.
Arms per mode:
- NATIVE anchor.
- Eight SINGLE_k anchors, one for each k in I; every inherited single must retain collapse.
- Every unordered PAIR_i_j for i<j in I: exactly 28 pair arms, flipping only streams at i and j.
rid/t/bits/program_a..d remain native. All other arrivals remain exact. Corruption set fixed.
Report exact sensitive_pairs = pairs that abolish collapse.
Classification:
PAIRWISE_REDUNDANT_CAUSALITY if at least one pair abolishes collapse.
ALL_INSENSITIVE_PAIRS_ROBUST if all28 pair flips retain collapse.
CROSS_MODE_PAIR_DIFFERENCE if sensitive-pair sets differ across U_A0/U_A25.
SINGLE_ANCHOR_NOT_REPRODUCED if any inherited insensitive single abolishes collapse.
NATIVE_ANCHOR_NOT_REPRODUCED if native no longer collapses.
OTHER_VALID_PATTERN otherwise.
Validity: exact native+8 single+28 pair arms per mode; only registered one/two stream labels changed; rid/t/bits/programs fixed; all other arrivals exact; corruption fixed; []/[2] exact; A56 insensitive set exact; runtime constants fixed; scientific integrity; duplicate byte-identical; globals restored.
Scientific negatives are valid. No post-result tuning.
