# Mirrored-cell transfer

Frozen commit `277c45fe814fa0fcf5a371166a3a67df506e2d18`, tree `7710c0d7d5b668839698248c9ac1f4cf4e1214d8`. Cold restore
from the unchanged 1,025-witness anchor. Only synthetic development.

**DEV_NO_GO.** The hard transfer arm learned complement probabilities
0.574, 0.751 and 0.723. All three were below its preregistered 0.8 threshold,
so it fell back on the old prediction at the withheld cell, as designed.
The mean target Brier deficit versus the best matched control was 0.108114.
Full-history fitted Beta was strongest on the shifted target on all seeds.

Soft Bayesian averaging improved over independent target-only updates by
approximately 0.015093 mean shifted-target Brier across the matched seeds.
It still lost to fitted full-history Beta on every seed. It scores a learned
proposal, not a qualified new relation or policy. Two seeds failed the
hard arm's retention requirement across unchanged/return addresses. Its
target fallback alone does not prevent drift at observed addresses.

There were 2,664 simulator actions, 124 FIT witnesses per disposable
descendant, and 372 new steps in each of the four retained JEPA heads.
The candidate cold-restored before evaluation. No scored outcome was
admitted, and the parent stayed unchanged. Three focused tests passed
on the frozen source. Wall 74.31 s, CPU 74.19 s and peak RSS 64,444 KiB.

## Why the historical relation was insufficient

The separate analytic source-law check distinguishes matching output
relationships from correlated changes. With independent flips, eight
donor-only probes leave the exact target forecast unchanged. Forcing
a coupled prediction raises expected Brier from 0.250000 to 0.326374.
Known 90% agreement or 90% disagreement permits 0.201121 under the
same budget, by correctly using or reversing the evidence. The result
comes from exact probability enumeration with zero new source actions.

The next comparison learns this dependence from observed calibration
receipts, then tests donor-only evidence on disjoint environments.
