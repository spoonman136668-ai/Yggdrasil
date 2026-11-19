# Transfer with misspecified transition laws

Frozen executable `234d6a95e5c763df0a666e3a17d937409a4c5497`, tree `bee5dd657fc1b6724ce9cb25cd1eae2f534ee1c0`. Fresh seed namespaces
and two new true margin families, both hidden from the fitted estimator.

**DEV_NO_GO.** Pooled correlated-condition Brier gain was **-0.000170**
versus independent forecasts, below the prespecified 0.005. Worst independent
drift was **0.010303**, above 0.002. Uniformly noisier conditions averaged
0.005929 gain. Asymmetric contrast averaged -0.006269. This falsifies treating
the known original transition margins as portable.

The known-law diagnostic remains intact. This run had 13,248 simulator probes,
0.0148 s timed kernel, and no native witnesses or training. The next comparison
will learn each marginal contrast from public calibration counts on fresh worlds,
with known-law and misspecified counterparts on the same evidence and budget.
