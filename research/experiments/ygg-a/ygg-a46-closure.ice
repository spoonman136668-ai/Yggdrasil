YGG-A46 CLOSURE
Run 36284325097 SHA c3d91d7ac33313ca525d0ca6d80bcd8de92a9299
Classification: WITHIN_PHASE_TIMING_SENSITIVE
Valid: true. Duplicate SHA256 ebb1ae4447f61023bff7d033120a90bb1a9401587e15a7c667d2dbd731022b4f.
Donor3 phase3 corruption offsets [9,17,22] were circularly shifted together through all 32 within-phase offsets while preserving total corruption count, phase3 count=3, and the phase3 circular-spacing multiset.
Both U_A0 and U_A25 produced the same collapsing shifts:
[0,2,4,5,7,9,13,15,17]
and noncollapsing shifts:
[1,3,6,8,10,11,12,14,16,18,19,20,21,22,23,24,25,26,27,28,29,30,31].
Interpretation: phase3 membership and internal spacing are not sufficient. Absolute within-phase timing matters.
Plain speak: even inside the critical phase, the exact moments of those three corruption events determine whether cell2 causes failure.
Next: move one of the three phase3 corruption events at a time while holding the other two fixed to identify which individual event timings carry the sensitivity.
