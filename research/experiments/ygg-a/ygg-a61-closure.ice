YGG-A61 CLOSURE
Run 36331200003 SHA dd5c53b145e6cb01d29474bc145d5c0bb4f4b75d
Classification: DISTRIBUTED_PAIR_SUPPRESSION
Valid: true. Duplicate SHA256 b7ac92e65ce461f60bc164da6a3943ee9873b957754ef497e21dc5918b9f6738.
Anchors reproduced in both U_A0/U_A25:
NATIVE collapses; FLIP106 alone collapses; FLIP117 alone collapses; pair(106,117) abolishes collapse.
Adding one additional phase3 stream flip to the causal pair restored collapse at exactly nine positions in both modes:
96,97,99,103,111,112,113,116,121.
Interpretation: suppression of a known causal pair is distributed across phase3 and not localized near the pair itself. The same suppressor set appears in both tested modes.
Plain speak: the pair106/117 can stop failure, but nine different third changes spread across the phase can switch failure back on.
Next: repeat the same full context sweep around a distinct known causal pair, (105,111), and compare the common-context suppressor field to A61. This tests whether suppressor positions are globally portable or pair-specific.
