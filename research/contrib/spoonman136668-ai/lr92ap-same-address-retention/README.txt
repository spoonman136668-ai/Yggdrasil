LR-92AP — PREPRIMARY ENGINEERING / NEGATIVE DEVELOPMENT FIXTURE
===========================================================
2026-11-19. EXTERNAL ISOLATED RESEARCH ONLY; NOT NATIVE YGGDRASIL TRAINING.
SCIENTIFIC_PRIMARY: NOT RUN. MERGE/PROMOTION/DEPLOYMENT: HOLD.

CONTEXT
-------
LR-92AO PR #1317 qualified fixed 14-bin temporal causal memory as 6/6
development PASS, but its prediction tied the conventional equal-information
14-bin table exactly. Its reported retention isolated different addresses;
it did not show active recovery after conflicting experience at ONE address.

LR-92AP preregistration FIRST on commit
62d466c924bb0173385d94f83b7fb7f8c26d0f89.
Base main 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9.
Source candidate published next at
89a7e38fb8425abd7b70d44f21e3a761745e5c30.
Eight fixture unit tests published at
57ec8968d3a4ddaaaa1d8fbf03fca5a0161688f2.
Source/dev data committed BEFORE any protected primary evaluation.

SOURCE/TEST EXACT CUSTODY
-------------------------
GitHub source blob e2fca6e277efbf0bd3b77ba7e472e4b5432d205f
SHA256 817e1baa6612b7906a926ad5497c383c6fd4455078b2052d0d3c2241ae1488e2
(5,076 UTF8 bytes; file public_dual_timescale_cells.py.txt)
GitHub fixture-test blob 0bb787292213ab16992e70233fed956046bb458b
SHA256 f691aa8f0cd9cedd183bf59740a669820322cc0434211cc30e9247434eeea66c
(2,514 UTF8 bytes; file test_dual_temporal.py.txt)
Fixture probe blob d08e0363b6744f0deb02c14d2a2edaa0379fa797
SHA256 236fd7355d3bfd6ce166a6bed2d740359ce96faea53bdfcb398df1d9e28592cc
(983 UTF8 bytes; file fixture_probe.py.txt)
GitHub file SHA1 blobs were read back independently and match local
git hash-object bytes. No branch source/atlas/native files modified.

Reproduce from these files (Python 3.13.5 local fixture environment):
  cp public_dual_timescale_cells.py.txt lr92ap_dual_temporal.py
  cp test_dual_temporal.py.txt test_lr92ap_dual_temporal.py
  cp fixture_probe.py.txt fixture_probe.py
  PYTHONPATH=. python -m unittest -v test_lr92ap_dual_temporal.py
  PYTHONPATH=. python fixture_probe.py
Expected focused tests: 8/8 PASS (local run).
First negative fixture test erroneously asserted that ending an episode
should ERASE a learned bin. This *test expectation*, not the learner,
was corrected before GitHub test publication; final tests PASS.

FIXTURE-ONLY FALSIFICATION (not the primary)
-------------------------------------------
Two unconsumed fixture seeds 73004303 and 73004304. 64 A then 64
contradictory B then 64 return-A public observations at the SAME active
address. Binary action random, 15% noise, prequential Brier (lower is
better). The generator knows phase; neither candidate nor control sees
phase labels. History resets each step, so this checks one-address
interference rather than the full 14 two-step-history patterns.
Candidate = published dual-timescale cell; single = full-history
Laplace-count; window = most-recent-32 count, all see exact same data.

seed           phase       candidate    single      window
73004303       B           0.3301       0.3996      0.2206
73004303       A return*   0.3105       0.2085      0.4094
73004304       B           0.3172       0.3702      0.1855
73004304       A return*   0.3187       0.2693      0.4255
*First sixteen A-return predictions before their respective updates.

VERDICT: DEVELOPMENT WARNING; NO EVIDENCE OF SUPERIORITY ON THIS
TWO-SEED FIXTURE. The 32-window control beats candidate during B; the
full-history control beats it during early A restoration. These are
DIFFERENT controls per phase, not an implementable phase-aware oracle
predictor, and not a frozen composite significance test. The candidate
does preserve the archived pre-B protected readout; that narrow cold
retention fixture is PASS, not autonomous prediction repair. An
exploratory protected/recent fixed-mixture diagnostic did not solve
both phase objectives. These fixtures license neither a scientific
positive nor a formal primary scientific negative.

NEXT AUTHORIZED BOUNDARY
------------------------
No primary worlds or protected first-use consumed; 288-world prospective
cohort specified in prereg remains untouched. Do NOT run it with this
unqualified candidate or retune on it. A later candidate must implement
evidence-based online regime selection and have every strong frozen
conventional control implemented/tested BEFORE source-lock and one
prospective primary. Do not recycle fixture results as confirmatory
evidence. No accepted Yggdrasil first-use, no native integration,
no general intelligence or scientific gain claim.

G29 (if green) only qualifies unchanged original source-index custody,
not this .txt Python candidate, full regression or scientific outcome.
