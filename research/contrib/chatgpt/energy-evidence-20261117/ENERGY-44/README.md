# ENERGY-44 — Selective causal weight repair without forgetting

External synthetic falsification only; not native Yggdrasil training or deployment. Reuses immutable ENERGY-43 original source and separate auditor via their SHA-256-pinned original sibling files. Does NOT reuse ENERGY-43 primary seeds or results.

A frozen four-factor old-context model is retained intact. When 96 new-consequence observations contradict that old model, the candidate minimizes regularized squared residual-energy over every pair of a preselected top-16 factor shortlist, adding exactly two context-gated corrective factors. The old model is never overwritten and is used unchanged for old-context predictions.

Full, matched control learners trained with identical 96 old plus 96 new observed interventions include stagewise conventional OMP two-factor corrective repair (especially important), conventional structural-memory OMP7, full OMP7, separate new OMP4, ridge, elastic net, random forest, no repair, and shuffled correction.

The factor grammar is known (364 candidate unary/pair/triple parity and conjunction functions). No learned unrestricted operators, autonomous actions, native tokens, or real-world world-model checkpoint. This is an isolated toy-scale synthetic test with serious fully trained controls.

Frozen local sources: `experiment.py.bz2` and `audit.py.bz2`; parent E43 dependencies at `../ENERGY-43/experiment.py.bz2` and `../ENERGY-43/audit.py.bz2`. Check SHA256 in `prereg.json`. The experiment only has `--smoke` and `--primary` modes. Smoke seed 99829 was independently audited: 11,583 checks PASS; primary seeds 8713,8731,8741 were not touched before preregistration.

Run from the ENERGY-44 directory after unpacking:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --primary --out scored.json
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py scored.json --out audited.json

For independent reproduction from GitHub, decompress E43 and E44 original Python source with bzip2; the E44 loader hashes the exact E43 original source and accepts an `ENERGY-43` sibling folder, not arbitrary imports. No accepted Yggdrasil files or refs are changed.
