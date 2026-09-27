YGG-A59 PREREGISTRATION — GENUINE FOURTH-ORDER STREAM-HISTORY INTERACTIONS
Parent A58 run 36322926253 valid GENUINE_THIRD_ORDER_CAUSALITY.
Question: do genuine fourth-order interactions exist among A56-insensitive positions after excluding every quadruple containing any known sensitive pair or sensitive triple?
Freeze exact A58 native substrate: replicate6 runtime/programs/arrival stream, donor3 corruption [16,38,146,118], alpha=.25, U_A0/U_A25, target cell2, exact task/weights/scheduler/horizon/service/maturity/matching/terminal rules, repair off, deterministic.
Frozen I={103,105,106,111,117,121,123,125}.
Frozen sensitive pairs E={(103,111),(105,111),(105,117),(106,111),(106,117),(117,123),(121,123)}.
Frozen genuine sensitive triples T={(105,106,121),(105,121,125),(106,123,125),(111,117,121),(111,117,125),(111,121,125)}.
Candidate quadruples are exactly those containing no pair in E and no triple in T:
(103,105,106,123)
(103,105,106,125)
(103,105,123,125)
(103,106,121,125)
(103,117,121,125)
Arms per mode: NATIVE, inherited A57/A58 anchors sufficient to re-establish the frozen lower-order map, and exactly these five quadruple flips.
Classification:
GENUINE_FOURTH_ORDER_CAUSALITY if at least one candidate quadruple abolishes collapse.
LOWER_ORDER_MODEL_SUFFICIENT_THROUGH_FOUR if all five retain collapse.
CROSS_MODE_QUADRUPLE_DIFFERENCE if sensitive sets differ.
LOWER_ORDER_ANCHOR_NOT_REPRODUCED if frozen pair/triple map differs.
NATIVE_ANCHOR_NOT_REPRODUCED if native fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact five candidates derived solely from frozen I/E/T; only registered stream labels vary; rid/t/bits/programs fixed; other arrivals exact; corruption fixed; []/[2] exact; lower-order anchors reproduced; deterministic duplicate; globals restored.
Scientific negatives are valid. No post-result tuning.
