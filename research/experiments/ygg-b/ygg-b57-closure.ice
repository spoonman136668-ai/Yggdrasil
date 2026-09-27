YGG-B57 CLOSURE
Run 36329853182 SHA 38db023aeb48705c06a1c83b741f5b783bf598c2
Classification: BOUNDED_INTERFERENCE_HORIZON_WITH_RECOVERY
Valid: true. Duplicate SHA256 1c6f23d893fb204a8c7a1e824fd33af42b3480bb2a75ea0375f61a7a8c86cdf6.
After one exact target refresh, six distinct competing writes accumulated with no repair between them.
Loss counts by depth:
1:0
2:0
3:1
4:15
5:25
6:25
All25 strata had lost target capability by depth5, and all remained lost at depth6.
A single final exact target refresh restored every lost stratum to >=.90 capability; observed post-repair target accuracy was1.0 for every reported lost stratum.
Interpretation: this substrate has a real bounded interference horizon, typically depth4-5, and the same one-write target refresh is sufficient to recover from the full six-write interference sequence.
Plain speak: now we finally broke the memory for real, and one precise rewrite repaired it every time.
Next: repeat the same six distinct competitor identities in the reverse frozen order. This tests whether first-loss depth is mainly cumulative load or depends strongly on which competing identities arrive when.
