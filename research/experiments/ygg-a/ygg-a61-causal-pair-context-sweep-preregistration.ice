YGG-A61 PREREGISTRATION — FULL PHASE3 CONTEXT SWEEP AROUND CAUSAL PAIR (106,117)
Parent A60 valid NONMONOTONE_EDGE_FAILURE.
Question: which individual phase3 context flips suppress the known causal pair (106,117), and is suppression localized or distributed?
Freeze exact A60 substrate: replicate6 runtime/programs/native arrivals, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Anchors per mode:
- NATIVE must collapse.
- FLIP_106_ONLY must collapse.
- FLIP_117_ONLY must collapse.
- PAIR_106_117 must abolish collapse.
For every k in phase3 requests96..127 excluding106 and117, evaluate TRIPLE_106_117_k: flip exactly streams106,117,k and nothing else.
There are exactly30 context arms.
Report suppressor_rids = k for which adding k restores collapse to the otherwise noncollapsing pair.
Classification:
DISTRIBUTED_PAIR_SUPPRESSION if >=2 context positions restore collapse.
SINGLE_CONTEXT_SUPPRESSOR if exactly1 restores collapse.
NO_SINGLE_CONTEXT_SUPPRESSION if none restores collapse.
CROSS_MODE_CONTEXT_DIFFERENCE if suppressor sets differ.
ANCHOR_NOT_REPRODUCED if native/single/pair anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact30 context arms; exact anchor behaviors; only registered stream labels vary; rid/t/bits/programs fixed; other arrivals exact; corruption fixed; []/[2] exact; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
