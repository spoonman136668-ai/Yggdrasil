# ENERGY-14 first scored cohort — INVALID, preserved

The original frozen-source cohort at seeds 17/31/53 produced 192/192 exact synthetic maze-path predictions. Independent audit V1 subsequently FAILED because one test maze appeared twice across scored seeds. Investigation found cross-split repeated maze instances:

- seed 17 train/test overlap: 1; validation/test overlap: 1; train/validation overlap: 1
- seed 31 train/test overlap: 1
- seed 53 train/validation overlap: 2
- cross-seed scored test repetition: 1 (seed 17 case 23 = seed 31 case 0)

Therefore 192/192 is invalid as a disjoint unseen test result. The frozen original source, preregistration, hash receipt and output are preserved without post-score edits. A separate independently seeded, collision-rejecting experiment was created as ENERGY-14B, with unchanged model/training/search hyperparameters. Do not combine the two as replication or average their metrics.