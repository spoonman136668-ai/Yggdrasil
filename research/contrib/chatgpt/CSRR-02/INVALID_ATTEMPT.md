# CSRR-02 first attempt: invalid execution, not a scientific result

2026-11-21. Frozen source/protocol at commit `ac29f850856348eabc27337e1f9af15467d4d36d`; original source blob `5d36f0e4525b30d7dd9eb68d45655b28434f3585`.

The first Linux Node v22 source-only attempt terminated at global step 511 on seed 404 with `TypeError: Assignment to constant variable` in `score()` when restoring the cold clone. It returned nonzero, produced no finalized metrics/result, and did not run remaining seed cohorts. The already generated synthetic observations were consumed for development; do not relabel the attempt as a scientific test or rerun its seeds as fresh confirmatory data. No protected original-world actions, native training, checkpoints, runner or workflow dispatch occurred.

The next preregistration uses new seeds 707/808/909 with only the variable declaration repaired and explicit unchanged hypothesis, thresholds, phase grammar, comparator rules, and scoring. This is a test-harness/infrastructure failure, **not** a negative scientific finding. Full Linux/Windows regression, G29, source-owner acceptance and real causal transfer remain unverified.
