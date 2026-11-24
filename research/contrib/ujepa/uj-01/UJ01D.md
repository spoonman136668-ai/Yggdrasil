# UJ-01D DEV training harness

The bounded optimizer runs explicitly supplied training pairs only; rejects
oversize, uneven and invalid budgets before any optimizer mutation; applies EMA
once per successful update; fails on missing/nonfinite gradients and parameters.
Caller must discard failed models; no automatic restart. Actual UJ-01B modes
completed four optimizer steps each on fabricated data. No real data consumed.

Candidate sources (metadata only; not frozen, acquired, licensed for this use,
or used in training):
- Language continuation: HellaSwag, https://rowanzellers.com/hellaswag/
- Algebra multiple choice: AQuA-RAT, https://github.com/google-deepmind/AQuA

Prior to first-use, owner must establish source/license and revisions, hashes,
length eligibility (no silent truncation), group and near-duplicate disjointness,
label availability, answer-position balance, exact source-family split, per-domain
data budgets and exposure accounting. HellaSwag public test labels may be unavailable;
use a frozen untouched labeled partition instead, not the same validation used
for tuning. Do not read protected labels during preprocessing development.
No corpus files, trained recurrent/transformer/symbolic controls, checkpoint
format, or cold retention implementation are provided in this change. Fixed
steps and bytes do not demonstrate matched FLOPs or wall time. The current
prototype handles byte strings of at most 256 bytes; coverage must be reported.
No scientific preregistration is claimed before the unresolved fields are frozen.

Fixture command from repository root:
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m unittest discover -s research/contrib/ujepa/uj-01 -p test_bounded_train.py -v
