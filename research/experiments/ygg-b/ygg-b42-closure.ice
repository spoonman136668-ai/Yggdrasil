YGG-B42 CLOSURE
Run 36273730650 SHA 7915f464a6e6c474d54316564c2dfef77713f00d
Classification: TARGET_TO_LATEST_SUFFICIENT
Valid: true. Duplicate SHA256 50b596004675d2317a2c970de452c2996b2a35fba73cdc3b8b4b78a04ed989b6.
Across 30 fixed seed/query strata, RECIPROCAL was capable 30/30 and TARGET_TO_LATEST_ONLY was capable 30/30, each with accuracy 1.0 in every stratum. SOURCE6_TO_QUERY_ONLY was capable only 5/30 and failed universally except query-position4 strata. Exact multiset preservation, parking rule, B41 anchors, state/parameter count, and duplicate execution passed.
Interpretation: rescue is caused by relocating the queried binding to the latest write position, not by importing the original position6 content into the queried slot. The remaining question is whether position6 is uniquely privileged or one end of a recency gradient.
Plain speak: the fix comes from making the thing being asked about the newest write. The content that used to be newest is mostly irrelevant.
Next: controlled target-binding destination sweep across positions0..6 using pure permutation cycles.
