YGG-A60 CLOSURE
Run 36327853734 SHA 4bbeeef756c62647e001ffc65b17117bfd6d9234
Classification: NONMONOTONE_EDGE_FAILURE
Valid: true. Duplicate SHA256 e087abbdf30c6aa724435e22b2c0de8fa13d57f4621ccdea06224c366660cfb1.
The frozen A57-A59 minimal causal hypergraph was tested exhaustively over all256 flip subsets of I={103,105,106,111,117,121,123,125} in both U_A0/U_A25.
Observed:
- 156 noncollapse subsets, 100 collapse subsets.
- zero false positives: every observed noncollapse subset contained at least one frozen minimal causal edge.
- 49 false negatives in each mode: many supersets containing a known causal edge reverted back to collapse.
- mismatch sets were identical across modes.
- all known lower-order anchors reproduced.
Interpretation: the discovered pair/triple/quadruple edges are necessary descriptors of noncollapse but are not monotone sufficient causes. Additional flips can suppress or reverse an otherwise causal configuration.
Plain speak: a combination that stops failure can be cancelled by adding another change. The causal logic is context-sensitive, not a simple “once a bad edge appears, failure is gone” rule.
Next: hold one reproducible causal pair, (106,117), fixed and add each other phase3 stream flip one at a time across requests96..127. This maps suppressor positions across the full phase, not only the eight resistant vertices.
