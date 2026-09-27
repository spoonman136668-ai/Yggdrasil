YGG-A52 PREREGISTRATION — SINGLE-SLOT STREAM LABEL CAUSALITY
Parent A51 run 36309192379 valid STREAM_LABEL_REQUIRED.
Question: does collapse depend specifically on the stream label of the corrupted request118, on neighboring request119, or on their paired label context?
Freeze exact A51 substrate: replicate6 runtime/programs, donor3 corruption [16,38,146,118], native request bits/program identities, no phase3 corruptions105/113, alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Native phase3 labels are request118=C and request119=S.
Construct four arms with rid/t/bits/program_a..d fixed:
1 NATIVE: 118=C,119=S.
2 FLIP_118_ONLY: 118=S,119=S.
3 FLIP_119_ONLY: 118=C,119=C.
4 FLIP_BOTH: 118=S,119=C, reproducing A51 STREAM_SWAP_ONLY.
All other 158 arrivals remain exact. Corruption remains fixed at request118.
Anchors:
- NATIVE must collapse.
- FLIP_BOTH must not collapse.
Classification:
CORRUPTED_SLOT_LABEL_REQUIRED if FLIP_118_ONLY abolishes collapse while FLIP_119_ONLY retains it.
NEIGHBOR_LABEL_REQUIRED if FLIP_119_ONLY abolishes collapse while FLIP_118_ONLY retains it.
BOTH_LABELS_INDEPENDENTLY_REQUIRED if both single flips abolish collapse.
PAIRED_LABEL_CONTEXT_INTERACTION if both single flips retain collapse but FLIP_BOTH abolishes it.
CROSS_MODE_SINGLE_SLOT_LABEL_DIFFERENCE if arm patterns differ across modes.
ANCHOR_NOT_REPRODUCED if NATIVE/FLIP_BOTH anchors fail.
OTHER_VALID_PATTERN otherwise.
Validity: exact four arms; only preregistered stream labels at118/119 may change; rid/t/bits/programs fixed; other158 arrivals exact; corruption set fixed; []/[2] exact; runtime constants fixed; scientific integrity; duplicate byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
