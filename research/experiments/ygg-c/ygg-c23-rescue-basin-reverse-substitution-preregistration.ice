YGG-C23 PREREGISTRATION — PARTNER6 RESCUE-BASIN REVERSE SINGLE SUBSTITUTION
Parent C22 run 36276037967 valid MIXED_LOCAL_CONTEXT; full replicate6 lesion rescues replicate8 at every level8..16 and forward substitution 38->42 rescues at every level.
Question: once replicate8 is in the fully rescued partner6 lesion context, is that rescue locally robust to one-cell reversions toward its original lesion, or does a narrow set of partner6 cells remain necessary?
Freeze exact corrected C22/C20 substrate: below alpha 0.134765625; levels8..16; replicate8 identity; partner6 lesion donor; exact manifests, learned weights, task/scheduler, retention/maturity predicates; deterministic; no retraining/adaptation/threshold/topology/baseline mutation.
Per level:
- reproduce original replicate8 lesion as failing anchor;
- reproduce full partner6 lesion on replicate8 as rescuing anchor;
- compute replicate8-unique cells and partner6-unique cells exactly as C22;
- starting from the full partner6 lesion, enumerate every distinct one-for-one reverse substitution formed by removing one partner6-unique cell and adding one replicate8-unique cell, preserving lesion cardinality; deduplicate lexicographically.
Explicitly report reverse edge 42->38 at every level; its forward counterpart 38->42 was universally rescuing in C22.
Classification:
RESCUE_BASIN_ROBUST if every valid reverse one-cell substitution remains mature at every level.
SINGLE_REVERSION_FRAGILE if at least one fixed reverse pair abolishes rescue at every level and all anchors reproduce.
MIXED_RESCUE_BASIN if both mature and failing reverse substitutions occur.
NO_REVERSE_DIFFERENCE if no reverse substitution exists.
ANCHOR_NOT_REPRODUCED if original failure or full-partner rescue fails.
OTHER_VALID_PATTERN otherwise.
Validity: exact alpha/levels/replicate8/partner6; cardinality preserved; every unique reverse substitution tested; 42->38 present every level; anchors reproduced; non-lesion fields preserved; duplicate analysis byte-identical; runtime globals restored.
Scientific negatives are valid. No post-result tuning.
