YGG-A29 PREREGISTRATION — REPLICATE-6 CELL-2 PAIR-REMOVAL NECESSITY
Parent: YGG-A28 run 36233223778, valid DISTRIBUTED_CONTEXT.
Question: after no single L11 removal abolished cell-2-induced collapse, does removal of any pair from the exact frozen replicate-6 L11 abolish collapse, and is that pair effect mode-stable?
Frozen: actual replicate 6; L11=[7,15,23,29,31,32,39,47,52,55,63]; target cell 2; alpha=0.25; U_A0/U_A25; exact A28 task, manifests, learned weights, scheduler, horizon, maturity/integrity rules; repair OFF; deterministic execution. No retraining, online adaptation, threshold change, topology change, or baseline mutation.
Design: reproduce L11 anchor and L11+cell2 positive control in each mode. Exhaustively test all 55 unordered pair removals: (L11-{x,y})+cell2. This set is fixed before outcomes and is not selected from effect sizes.
Classification: PAIR_NECESSITY_FOUND if one or more identical abolishing pairs occur in both modes; MODE_SPECIFIC_PAIR_INTERACTION if abolishing-pair sets differ; NO_PAIR_NECESSITY if all 55 arms still collapse in both modes; OTHER_VALID_PATTERN otherwise.
Validity: duplicate complete execution byte-identical; exact replicate/L11/cell2/alpha; positive control reproduced; exactly 55 unique pair arms per mode; inherited integrity/maturity gates preserved.
Scientific negatives are valid results. No post-result tuning.
