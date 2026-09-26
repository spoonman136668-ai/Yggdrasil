YGG-A30 PREREGISTRATION — REPLICATE-6 CELL-2 TRIPLE-REMOVAL NECESSITY
Parent: YGG-A29 run 36251899924, valid NO_PAIR_NECESSITY.
Question: after no single or pair removal from the exact frozen L11 abolished cell-2-induced collapse, does removal of any unordered triple abolish collapse, and is any such effect mode-stable?
Frozen: actual replicate 6; L11=[7,15,23,29,31,32,39,47,52,55,63]; target cell=2; alpha=0.25; U_A0 and U_A25; exact inherited A29/A28 task, manifests, learned weights, scheduler, horizon, maturity and integrity predicates; repair OFF; deterministic. No retraining, online adaptation, threshold/topology/baseline mutation.
Design: reproduce L11 anchor and L11+cell2 positive control in each mode. Exhaustively test all C(11,3)=165 unordered triple-removal arms (L11-{x,y,z})+cell2 in each mode. Triple set is fixed lexicographically before outcomes and is not effect-selected.
Classification:
 TRIPLE_NECESSITY_FOUND if one or more identical abolishing triples occur in both modes;
 MODE_SPECIFIC_TRIPLE_INTERACTION if abolishing sets differ by mode;
 NO_TRIPLE_NECESSITY if all 165 arms still collapse in both modes;
 OTHER_VALID_PATTERN otherwise.
Validity: duplicate complete execution byte-identical; exact replicate/L11/cell2/alpha/modes; positive controls reproduced; exactly 165 unique triple arms per mode; inherited integrity and maturity pass.
Scientific negatives are valid. No post-result tuning.
