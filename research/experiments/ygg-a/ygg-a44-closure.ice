YGG-A44 CLOSURE
Run 36283331102 SHA 7467625ba9fb0efca3504f9e21af2a04e74989e9
Classification: PHASE_SENSITIVE
Valid: true. Duplicate SHA256 94a64da1e9c563d29e6509a27d9cb803dcbf4d23bfd09535f6a1355cd7f1dd57.
Exact k0 anchor donors [3,6,8,10] reproduced in both U_A0 and U_A25.
Each donor corruption schedule was cyclically rotated by 32-request phases while preserving exact corruption count and the full circular-spacing multiset.
Both modes produced the same donor/rotation collapse matrix:
1:[F,F,F,F,F]
2:[F,F,F,F,F]
3:[T,F,F,F,F]
4:[F,F,F,F,T]
5:[F,F,T,F,F]
6:[T,T,F,F,F]
7:[F,F,F,F,F]
8:[T,F,F,T,F]
9:[F,F,F,F,T]
10:[T,F,F,F,T]
Interpretation: corruption-event count and relative circular spacing are insufficient to determine failure. Developmental phase placement changes the outcome.
Plain speak: moving the exact same corruption pattern to a different developmental phase can turn failure on or off. Timing itself is causal.
Next: choose the lowest donor whose outcome changes under rotation (donor3) and swap one pair of 32-request phase blocks at a time to identify whether a single local phase exchange can abolish collapse.
