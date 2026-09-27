YGG-B45 IDENTIFIER COLLISION RECONCILIATION
Run 36282455288 SHA b25cbbbcc890789f864ba084e8ff807b94869626 contained two separately preregistered scientific steps sharing the historical mode/experiment number B45.
Both steps completed successfully and emitted distinct valid deterministic records. Neither result is renamed or rewritten retroactively.
For lineage references only:
B45-A = RECENCY-BAND BACKGROUND-ORDER ROBUSTNESS
- classification FULL_BACKGROUND_ORDER_ROBUST_RECENCY
- valid true
- duplicate SHA256 e1ba52cbae5d816a7e501f86b8d1b0fa5b069ab0f42daf23457087ccafdbdc52
- d5 300/300 capable, minimum accuracy 0.9038142561912537
- d6 360/360 capable, accuracy 1.0 throughout
B45-B = BOUNDED TARGETED MEMORY REFRESH
- classification TARGET_SPECIFIC_UNIVERSAL_REFRESH
- valid true
- duplicate SHA256 661b87241316865e9913b54990e65c047798744086f253349e010f893777519b
- original subthreshold strata 25/25
- target refresh capable 25/25
- unrelated control refresh capable 0/25
Scientific interpretation: the confirmed two-position recency mechanism is robust to broad background order, and a single targeted rewrite can exploit that mechanism to rescue every tested old-query stratum while an unrelated rewrite cannot.
Plain speak: recency is real, and rewriting the memory you actually need fixes all tested old memories; merely doing another write does not.
Governance correction: B45 remains immutable historical evidence. All successor work uses the next unused identifier B46 and a distinct b46_probe mode.
