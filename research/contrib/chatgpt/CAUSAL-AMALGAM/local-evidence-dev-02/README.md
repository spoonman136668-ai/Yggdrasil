# Crossed-shift local evidence development result

**DEV_NO_GO.** The source and protocol were frozen at
`efcd3a93dd6540515a346add7fcf58677147e23e` (tree
`cb86ee081a207acb1d5d5ab25d3df45d2b6027ac`) before outcome generation.
The first protocol hit its 480-second scoring cap and has a separate failure
receipt. This bounded correction cached immutable forecasts, reused the
historical Brier precision, and used disjoint synthetic seed and ID namespaces.

| Seed | Local changed Brier | Pooled Brier | Strongest assigned control | Control Brier | Maximum unchanged/return drift |
|---|---:|---:|---|---:|---:|
| 993301 | 0.268459 | 0.290619 | Fitted change point | 0.127311 | 0.141183 |
| 993323 | 0.301000 | 0.327380 | Continued native | 0.118729 | 0.470464 |
| 993337 | 0.294863 | 0.319456 | Fitted change point | 0.144961 | 0.096253 |

The local readout reduced mean changed-cell Brier by **0.024391** versus
shared evidence weighting. It still trailed the strongest seeded comparator
by **0.157774** on average. Each seed exceeded the 0.02 preservation bound.
Scores come from the same fixed action schedule. No active policy was tested.

The three sequential disposable replicas used **2,304 simulated actions**:
384 FIT actions, 384 public-prefix actions and 1,536 scored actions. Each
replica retained all 1,025 original witnesses, added 64, advanced each of the
four trained heads by 192 steps and restored its resulting joint checkpoint
before evaluation. The sealed trace and descendant hashes are in the result.
No held witness entered persistent training. This fixture studies shifts in two public cells.
The separately staged sixteen-circuit roster has not been consumed.

## Retrospective diagnosis

Choosing the better original or continued endpoint after viewing held scores
would produce changed-cell Brier **0.237375 / 0.118729 / 0.243457**. That
privileged endpoint choice would still trail the fitted change-point control
by **0.110065** and **0.098496** on seeds 993301 and 993337. It does not bound
every possible forecast mixture. Together with the high all-old and
familiar-return losses, it gives two separable next questions: can a native
cell-local update fit the new effect itself, and can the original forecast
remain available when that local effect is unsupported? The next candidate
should change the learned cell forecast before testing a readout gate again.
Use the existing local witness/counter update path in shadow and compare a
scope-isolated update against exact Beta and fitted change-point controls.
No particular threshold is selected from these held outcomes.

## Reproduction and custody

Local Linux x86_64, Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, scikit-learn
1.8.0, joblib 1.5.3 and threadpoolctl 3.6.0. BLAS and OpenMP were set to one
thread and PYTHONHASHSEED was zero. Wall time was **49.99 s**, CPU time
**49.93 s**, peak RSS **68,644 KiB**. The earlier source-bound receipt
candidate has its separate dual-platform qualification. The trial branch
received only the five focused readout tests, and it is not a selected
engineering or model-promotion candidate.

The Git commit above is the sealed design. Use the pinned donor blobs and
legacy joint parent from the adjacent `EXTERNAL-RECEIPTS.md` instructions.
For authorized readback, use the checked-in result and recorded trace and
checkpoint digests as provenance. This study did not promote a descendant,
change planning authority, deploy, or use protected source data.
