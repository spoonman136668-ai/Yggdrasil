YGG-C22 PREREGISTRATION — REPLICATE8 / PARTNER6 SINGLE LESION-CELL SUBSTITUTION
Parent C20 R3 run 36272096271 valid corrected MIXED_IDENTITY_CONTEXT at exact below-onset alpha 0.134765625.
Outcome-driven successor selection rule: choose the lowest non8 partner whose full lesion rescues replicate8 at every level8..16. Corrected C20 R3 identifies replicate6 (replicate10 also qualifies); therefore fixed partner for C22 is replicate6.
Question: is replicate8 rescue under the full replicate6 lesion locally reachable by a single lesion-cell substitution, or does failure remain robust until higher-order context changes accumulate?
Freeze exact corrected C20/C19 substrate: below alpha 0.134765625; levels8..16; exact manifests, learned weights, task/scheduler, retention/maturity predicates; replicate8 identity; partner6 identity; deterministic execution; no retraining, online adaptation, threshold redefinition, topology change, or baseline mutation.
Design per level:
- reproduce original replicate8 lesion as failing anchor;
- reproduce full replicate6 lesion on replicate8 as rescuing anchor;
- compute cells unique to replicate8 lesion and unique to replicate6 lesion;
- enumerate every distinct one-for-one substitution: remove one replicate8-unique lesion cell and add one replicate6-unique lesion cell, preserving lesion cardinality;
- evaluate replicate8 only; deduplicate lesion sets lexicographically.
Classify EXACT_PAIRING_FRAGILE if every valid one-cell substitution rescues maturity at every level; LOCAL_CONTEXT_ROBUST if every valid one-cell substitution retains failure at every level; MIXED_LOCAL_CONTEXT if both rescue and failure occur; NO_LOCAL_DIFFERENCE if no one-cell substitution exists; ANCHOR_NOT_REPRODUCED if original failure or full-partner rescue fails; OTHER_VALID_PATTERN otherwise.
Validity: actual replicate8 and partner6 IDs dynamically verified; exact runtime alpha 0.134765625 during every arm and restored afterward; exact levels; lesion cardinality preserved; all unique one-cell substitutions tested; anchors reproduced; non-lesion fields preserved; duplicate analysis byte-identical.
Scientific negatives are valid. No post-result tuning.
