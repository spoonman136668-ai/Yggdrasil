YGG-B61 PREREGISTRATION — HELD-OUT VALIDATION OF FROZEN PRE-FAILURE MARGIN GATE
Parent B60 valid MARGIN_OVERLAP with survival rank AUROC0.9737395099.
Frozen calibration threshold from B60 only:
T=2.6009554862976074, predicting NEXT_FAILURE iff PRE_MARGIN <= T.
No threshold or model refitting is permitted in B61.
Held-out seeds are exactly [666,777,888,999,1111], disjoint from B60 [111,222,333,444,555].
Freeze exact B60 model/training/evaluation construction, q=[0..4], deterministic Torch, same12 cyclic forward/reverse competitor orders and one target refresh at depth0.
For every held-out seed/q/order, include only pre-first-loss transitions. PRE_MARGIN remains mean native top1-top2 target-logit margin and uses no correct-label identity.
Report:
- failure/survival counts;
- AUROC for higher margin predicting survival;
- frozen-threshold TP/TN/FP/FN, sensitivity, specificity, balanced accuracy;
- margin ranges.
Classification:
HELDOUT_MARGIN_GATE_REPLICATES if AUROC>=0.90, balanced accuracy>=0.85, sensitivity>=0.85, specificity>=0.80.
HELDOUT_RANK_SIGNAL_ONLY if AUROC>=0.90 but frozen gate misses any gate criterion.
HELDOUT_MARGIN_SIGNAL_WEAK if AUROC<0.90.
NO_FAILURE_TRANSITIONS if no held-out failure examples occur.
ANCHOR_NOT_REPRODUCED if depth0 target anchor fails or order construction is invalid.
OTHER_VALID_PATTERN otherwise.
Validity: exact held-out seeds only; no B60 seeds; exact12 orders; only pre-first-loss transitions; fixed threshold bit-identical; no correct-label use in PRE_MARGIN; fixed state/params; deterministic duplicate.
Scientific negatives are valid. No post-result tuning.
