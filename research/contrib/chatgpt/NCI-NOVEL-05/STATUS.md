# NCI-NOVEL-05 execution status — incomplete primary (2026-11-20)

**ENGINEERING: focused PASS, primary runtime FAIL. SCIENCE: UNVERIFIED (not a GO or a scored NO-GO). DEPLOYMENT: NONE.**

## Immutable source custody
- Accepted Yggdrasil main at research start: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; unchanged at source-frozen readback.
- Prereg committed BEFORE executable/primary: `1ea882ae8188e8ba6a7e91fa4e008785c62f9423`.
- Executable source archive committed BEFORE primary: `5890b1556825ad77edf281d9356794a2f688590f`, tree `987d5e87eda7452f75fabfc048d9988b0faa5c84`.
- Exact source archive `source_preprimary.tar.gz`: 6,029 bytes, SHA-256 `532fc6a824f1b50fe4cfaf7880619407a2a25a73f888db045e145d2782568e40`. Git object SHA `6f3d810788f1055267a9794cfa2a2739ec367919` matched repository blob creation; content REST readback failed because the binary endpoint requires UTF-8; do not claim a separate binary download verified.
- Bundle contains source `experiment.py` (10,793 bytes; SHA-256 `ce72306fa92c5b474e779427933e819bc59f262f491b849d6081bf4b24708e56`), `test_experiment.py` (2,001 bytes; SHA-256 `6184cc14dede3e972ba21b2480013df22a2fd4c6f2a25d163e9397a752bb9005`), and `pilot.json` (8,942 bytes; SHA-256 `2c067d43cf8ed50616259aa9c02e962e1dc20786d9e8c5352f717010eca2da6c`). Extract locally with `tar -xzf source_preprimary.tar.gz`, then run focused tests; no primary replay.
- Local environment: Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0. Source-free 11/11 focused tests PASS before primary. No GitHub CI/full native regression completed.

## Pilot only — not scientific evidence
Engineering pilot `809001` across seven synthetic families: 7 worlds, 15.11 s local wall. No novel family cleared the preregistered strong-control reward+Brier gate (0/4). Negative family false-identification condition PASS; research old-readout preservation PASS. Before pilot, an unpicklable local defaultdict factory caused a failure; source was corrected before pilot success, source freeze and primary. No threshold or source changes after the frozen archive commit. Pilot scores are engineering-only and may not be promoted.

## Primary execution incident
The ONE frozen primary invocation started on seeds `809011,809033,809057,809089` and requested `--primary --output primary_result.json`. The containing execution hit its 180-second timeout and was terminated without producing `primary_result.json`. No primary aggregate, complete per-world scores, scientific PASS, native training, or full regression receipt exists. A post-timeout process check found no remaining `experiment.py` process. At least some source-free synthetic execution may have occurred; **treat all four primary seeds as potentially exposed and never replay them**. This is a runtime resource/receipt-custody failure, *not* evidence that the candidate passed or failed its scientific gates.

## Reproducibility / next scientific boundary
Preserve exact prereg, source and engineering pilot. Do not rerun the original primary or retune from partial evidence. Future work requires a NEW independently preregistered cohort and NEW untouched seeds, a bounded per-world incremental receipt/checkpoint producer, a measured per-world wall/CPU preflight, and controls that still include fully fitted exact BMA and trained conventional baselines. Run a small falsifiable source-free test before seeking native owner admission; NCI-NOVEL-04's previously verified full-control tie and one out-of-grammar false identification remain open negatives.

No merge, source first-use, model checkpoint, canonical Amalgam lineage, research loop, runner/scheduler or deployment was modified. Sole canonical integration owner: Unified Causal Intelligence Amalgam Work chat / PR #1278. The retired NCI-SOURCE guard engineering investigation is not reopened by this experiment.
