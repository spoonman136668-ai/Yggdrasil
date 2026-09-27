YGG-B48 CLOSURE
Run 36286528372 SHA 794dc97077cfb2ae8f6c4d3c5af349ee6674828f
Classification: TARGET_IDENTITY_UNIQUE_RESCUE
Valid: true. Duplicate SHA256 60cb5d393aab6a41e6a33b3af6b7916262dee6e5a87187a606b4369747525d9a.
All 175 seed/query/refresh-identity strata were tested.
For every old-query stratum q in [0..4], exactly refresh identity r=q reached the inherited >=0.90 target capability threshold. No non-target rewrite rescued the old query.
Collateral new-error rate from the target rewrite decreased with original query position:
q0 1050/14190=0.073996
q1 1035/13797=0.075016
q2 650/13604=0.047780
q3 562/13059=0.043035
q4 427/12966=0.032932
Across all refresh identities, later original bindings caused progressively less collateral; rewriting r6 produced zero change because it replays the already-latest binding.
Interpretation: correction is identity-specific, while collateral cost is structured by write history/age.
Plain speak: to fix an old memory you must rewrite that exact memory. Rewriting something else never fixes it, and rewriting older items disturbs the memory state more than replaying recent ones.
Next: after the mandatory target refresh, add one deterministic second write replaying the oldest non-target binding. Because the target then becomes the second-most-recent write, test whether it stays rescued while collateral damage is reduced.
