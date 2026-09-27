YGG-A62 PREREGISTRATION — SUPPRESSOR PORTABILITY ACROSS DISTINCT CAUSAL PAIRS
Parent A61 run 36331200003 valid DISTRIBUTED_PAIR_SUPPRESSION.
Question: is the distributed suppressor field found around causal pair(106,117) portable to a distinct known causal pair, or pair-specific?
Freeze exact A61/A60 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Test pair P2=(105,111), established by A57 as causal while each singleton is A56-insensitive.
Anchors per mode:
- NATIVE collapses.
- FLIP105_ONLY collapses.
- FLIP111_ONLY collapses.
- PAIR_105_111 abolishes collapse.
For every k in phase3 requests96..127 excluding105 and111, evaluate TRIPLE_105_111_k.
There are exactly30 context arms.
Frozen A61 suppressor field S1={96,97,99,103,111,112,113,116,121}.
For comparison over positions available in both sweeps, use S1_COMMON=S1 minus {111}={96,97,99,103,112,113,116,121}.
Report S2 and:
- shared_common = S2 intersect S1_COMMON
- lost_common = S1_COMMON minus S2
- new_suppressors = S2 minus S1_COMMON
Classification:
PORTABLE_SUPPRESSOR_FIELD if S2 contains all S1_COMMON and has no new suppressors.
PARTIAL_SUPPRESSOR_PORTABILITY if shared_common is nonempty but the portable-field condition fails.
PAIR_SPECIFIC_SUPPRESSION if shared_common is empty and S2 is nonempty.
NO_SUPPRESSION_FOR_SECOND_PAIR if S2 is empty.
CROSS_MODE_PORTABILITY_DIFFERENCE if S2 differs across modes.
ANCHOR_NOT_REPRODUCED if native/single/pair anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact30 context arms; exact anchors; frozen S1/S1_COMMON exact; only registered stream labels vary; rid/t/bits/programs fixed; all other arrivals exact; corruption fixed; []/[2] exact; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
