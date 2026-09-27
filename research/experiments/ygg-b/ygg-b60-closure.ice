YGG-B60 CLOSURE
Run 36333420842 SHA f06b516de6155bdfefaf7d8aabf55641c748c9da
Classification: MARGIN_OVERLAP
Valid: true. Duplicate SHA256 340a040c99c99e08e7f53895fade29928a5f195e46a26f9201fb9a17b9963f69.
Using only native top1-top2 target-logit margin before each next write:
- 300 imminent-failure transitions and 993 next-survival transitions reproduced.
- failure margin range: 1.9863022566 .. 2.8066248894.
- survival margin range: 2.1002981663 .. 3.6464371681.
- ranges overlap, so no strict separator exists.
- survival rank AUROC = 0.9737395099.
A deterministic calibration scan over the B60 observations, predicting NEXT_FAILURE when PRE_MARGIN <= threshold and choosing the lowest threshold maximizing balanced accuracy, yields frozen threshold 2.6009554862976074.
At that threshold on B60: TP287 TN881 FP112 FN13; sensitivity0.9566666667; specificity0.8872104733; balanced accuracy0.92193857.
Interpretation: margin is not a perfect separator, but it is a strong prospective warning coordinate.
Plain speak: the model usually looks less confident right before memory breaks, but there are some overlaps.
Next: freeze the threshold now and validate it prospectively on entirely new seeds without refitting.
