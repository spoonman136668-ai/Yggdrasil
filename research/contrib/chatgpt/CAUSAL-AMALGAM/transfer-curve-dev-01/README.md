# Held-cell transfer learning curve

The frozen development protocol and evaluator are in
`5921018140dc5368632f3303a757c31f0d3e8b43`. Four copies continued from the same
qualified 1,025-witness joint checkpoint. Each saw three public context and
action combinations from the new synthetic world. Its omitted fourth
combination was scored on 64 fresh held episodes at every snapshot. The held
rows never entered the witness ledger, specialist gate or conventional fits.
The old checkpoint may contain evidence about that public cell from earlier
worlds. The three new cells alone cannot uniquely determine the fourth.

**DEV_NO_GO.** Native held-cell Brier improved by 0.119644 from the anchor.
Most of the change occurred within 24 witnesses. It did not reach the preset
advantage at either late milestone and only one of four seeds reached the
required final per-seed margin. Familiar transition Brier deteriorated by
0.097624 to 0.189425 across the four copies, exceeding the 0.02 limit in each.

| New witnesses per copy | Native held Brier | Best control per seed, averaged |
| ---: | ---: | ---: |
| 0 | 0.330464 | 0.195782 |
| 8 | 0.277934 | 0.196682 |
| 24 | 0.218976 | 0.191233 |
| 64 | 0.212984 | 0.193970 |
| 120 | 0.210820 | 0.195822 |

The control comparison takes the lowest Brier on each seed among the fixed
anchor, full-history Beta, trailing Beta, change-point and fitted Bayesian
structural controls. At 120 witnesses, the individual structural control's
mean Brier was 0.208725. The direct and temporal transition heads scored
0.760108 and 0.636366. The uniform blend scored 0.458534. The evidence gate
used the native readout for all 256 held decisions at that milestone.
The gate measures evidence for the public cell being scored, and the omitted
cell supplied none during continuation. This is a limitation of that gate's
transfer coverage.

Each trial copy reached 1,145 witnesses and preserved the original ledger.
Each of its four trained heads took 360 additional gradient steps. The
1,984 synthetic actions comprise 960 shared acquisition actions and
1,024 distinct held actions. Every prediction arm used the same witnessed
outcome rows. The producer used 134.70 seconds wall, 134.66 CPU seconds
and 57,648 KiB peak RSS for the whole experiment. Timings are aggregate
experiment costs. The design does not measure independent policy choice
or budget parity by arm.

The result and four traces record exact Brier numerators, prequential losses,
witness counts, source pins and checkpoint hashes. The read-only verifier
reconstructs the result from these traces without generating new outcomes.
The result authorizes no deployment, protected first-use, or tuning on the
held cohorts.
