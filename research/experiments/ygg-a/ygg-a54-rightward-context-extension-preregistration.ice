YGG-A54 PREREGISTRATION — RIGHTWARD STREAM-CONTEXT EXTENSION
Parent A53 run 36310331783 valid RIGHT_NEIGHBOR_REQUIRED.
Question: once the required 118=C,119=S,120=C triplet is preserved, does collapse depend on the next-right request121, or is the triplet sufficient against one more step of local context?
Freeze exact A53 substrate: replicate6 runtime/programs, donor3 corruption [16,38,146,118], native bits/program identities, no phase3 corruptions105/113, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Native labels116..121 are C,S,C,S,C,S.
Preserve 118=C,119=S,120=C in every arm.
Construct:
1 NATIVE.
2 FLIP_116_ONLY: 116 C->S.
3 FLIP_121_ONLY: 121 S->C.
4 FLIP_116_121: both flips.
Only stream labels116 and/or121 may change. rid/t/bits/programs fixed. All other arrivals exact. Corruption fixed at118.
Anchor: NATIVE must collapse.
Classification:
TRIPLET_LOCALLY_SUFFICIENT if all four arms collapse in both modes.
NEXT_RIGHT_LABEL_REQUIRED if both arms with flipped121 abolish collapse while both native121 arms collapse.
FAR_LEFT_LABEL_REQUIRED if both arms with flipped116 abolish collapse while both native116 arms collapse.
BOTH_OUTER_LABELS_INDEPENDENTLY_REQUIRED if either single outer flip abolishes collapse.
OUTER_CONTEXT_INTERACTION if both single flips retain collapse but double flip abolishes it.
MIXED_OUTER_CONTEXT for any other stable same-mode pattern.
CROSS_MODE_OUTER_DIFFERENCE if patterns differ by mode.
ANCHOR_NOT_REPRODUCED if NATIVE fails.
Validity: exact four arms; 118..120 fixed C/S/C; only116/121 stream labels may vary; rid/t/bits/programs fixed; all other arrivals exact; corruption fixed; []/[2] exact; runtime constants fixed; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
