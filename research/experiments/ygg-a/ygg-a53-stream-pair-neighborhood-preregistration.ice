YGG-A53 PREREGISTRATION — STREAM-PAIR LOCAL NEIGHBORHOOD ROBUSTNESS
Parent A52 run 36309892412 valid BOTH_LABELS_INDEPENDENTLY_REQUIRED.
Question: is the required ordered pair 118=C,119=S locally sufficient against immediate stream-context perturbation, or does collapse depend on the broader 117..120 label history?
Freeze exact A52 substrate: replicate6 runtime/programs, donor3 corruption [16,38,146,118], native bits/program identities, no phase3 corruptions105/113, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Native labels over 117..120 are [S,C,S,C].
Preserve request118=C and119=S in every arm.
Construct:
1 NATIVE: 117=S,118=C,119=S,120=C.
2 FLIP_117_ONLY: 117=C,118=C,119=S,120=C.
3 FLIP_120_ONLY: 117=S,118=C,119=S,120=S.
4 FLIP_117_120: 117=C,118=C,119=S,120=S.
Only stream labels at117 and/or120 may change. rid/t/bits/programs stay fixed. Other158 arrivals excluding117/120 remain exact. Corruption remains fixed at118.
Anchor: NATIVE must collapse.
Classification:
PAIR_LOCALLY_SUFFICIENT if all four arms collapse in both modes.
LEFT_NEIGHBOR_REQUIRED if both arms with flipped117 do not collapse while both arms with native117 collapse.
RIGHT_NEIGHBOR_REQUIRED if both arms with flipped120 do not collapse while both arms with native120 collapse.
BOTH_NEIGHBORS_INDEPENDENTLY_REQUIRED if either single neighbor flip abolishes collapse.
BROADER_NEIGHBOR_INTERACTION if single flips retain collapse but double flip abolishes it.
MIXED_NEIGHBOR_CONTEXT for any other stable same-mode pattern.
CROSS_MODE_NEIGHBOR_DIFFERENCE if arm patterns differ across modes.
ANCHOR_NOT_REPRODUCED if NATIVE does not collapse.
Validity: exact four arms; 118/119 labels fixed C/S; only preregistered117/120 stream labels may change; rid/t/bits/programs fixed; all other arrivals exact; corruption fixed; []/[2] exact; runtime constants fixed; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
