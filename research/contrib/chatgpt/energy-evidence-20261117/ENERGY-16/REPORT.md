# ENERGY-16 — Original CRAM published-record comparison (read-only)

**Date:** 2026-11-17 (US Eastern). **Classification:** `PUBLISHED_RECORD_ARITHMETIC_PASS_REPRODUCTION_UNVERIFIED`.

## Bottom line

The original CRAM authors' public records show extremely fast learning on Maze-Unique, but this remains an audit of **published measurements**, **not a new run** of the original code or an independent scientific reproduction. The baseline comparison has serious reproducibility/qualification limitations: the upstream `baselines/README.md` discloses that its moved baseline wrappers were syntax checked but **not rerun from the published layout**, and `results/baseline-fit-times.json` explicitly identifies a `code_dirty: true` run-source snapshot. These facts do **not** prove the reported timings false; they mean we cannot treat them as independently qualified present-day baselines without running them.

## Source custody

- Pinned source: `Prefrontal-AI/CRAM`, commit `62bbe830c7d6f87f2ba18f30a28039258b986454`.
- `results/baseline-fit-times.json` blob SHA-1 `59ceee4fa7d9f5cb3064df723c2d34250a9b0a20`.
- `results/op-counts.json` blob SHA-1 `5db3c4e3b0c33a1e9636379820e319cc0cb6591f`.
- `experiments/runs/table/maze-unique__cram-sgd-fg.json` blob SHA-1 `b0108bcc2c451dc506d57962403d46e588b26ec1`.
- `experiments/runs/table/sudoku-extreme__cram-0-fit.json` blob SHA-1 `8970adaed07cbd74b2132dbcdf45ca6bd1967c6d`.
- `baselines/README.md` blob SHA-1 `6c0c47b7ae7ac9f33723c9d4dafd6b3bea82f954`.
- All five were inspected via the linked GitHub account during this gate. `records_snapshot.json` is a selected **transcription**, not a complete copy of upstream source files. `audit.py --verify-upstream` optionally downloads the pinned exact files and validates their Git blob SHA-1, when the user has network access. Network verification was not run in this isolated container.

## Maze-Unique reported measurements

The cold complete-fit timer includes end-to-end fitting (starting with training data already in host memory) on one H200. Each source baseline has three reported seed fits. Accuracy column is the recorded number of exactly correct complete mazes among three batches of 1,000.

| Method | Reported average cold fit | Ratio versus CRAM cold fit | Exact mazes / 3000 |
|:--|--:|--:|--:|
| CRAM | 0.723 s | 1.0× | 3,000 |
| EBR | 7,276.7 s | 10,069× | 2,694 |
| EqR (D64-B128) | 11,045.2 s | 15,284× | 1,996 |
| HRM | 25,577.0 s | 35,391× | 1,199 |
| TRMP | 27,557.6 s | 38,132× | 2,977 |
| FRM | 34,875.6 s | 48,258× | 2,918 |
| TRM | 55,592.8 s | 76,925× | 2,767 |

The same upstream file records HRM seed 2 = 10/1,000 and EqR seed 2 = 0/1,000, with TRM 768/1,000, 1,000/1,000 and 999/1,000 over the three seeds. These records establish substantial variation in **reported** accuracy. They do not establish why the seeds underperformed; do not diagnose convergence or corruption without corresponding training artifacts.

The source distinguishes CRAM **complete cold 0.723 s**, **complete warm 0.132 s**, and **update loop 0.119 s**. The main paper's 132 ms figure is consistent with the warm complete-fit measurement, not its cold one. Compare **cold to cold** only when computing the above ratios.

## Arithmetic check: operation-count convention changes

The revised complete arithmetic exporter `results/op-counts.json` includes operations excluded from older table fields. A mixed old/new denominator misstates relative costs.

| Task | CRAM older table FLOPs | CRAM complete-export FLOPs | Increase |
|:--|--:|--:|--:|
| Maze-Unique | 560,511.72 | 836,870.85 | **49.3%** |
| Sudoku-Extreme | 1,274,597,884.33 | 2,015,770,227.88 | **58.1%** |

Under **the same new convention**:

- Maze-Unique: HRM 3.0113e12 / CRAM 836,870.85 = **3.598 million×**; TRM 3.8406e12 / CRAM = **4.589 million×**.
- Sudoku-Extreme: HRM 2.2043e11 / CRAM 2.0158e9 = **109.4×**; TRM 4.1125e11 / CRAM = **204.0×**.

These counts are **arithmetic operation estimates**, not elapsed inference-time benchmarks; comparisons also need to match model correctness before a scientific speed claim. The paper's qualified matched-accuracy subgroup is different from these unfiltered method pairs. This audit makes no contradiction claim about the paper's separate matched-accuracy figure.

## Engineering, science, deployment

**Engineering — PASS (bounded read-only record analysis):** 27 local fixture/ratio checks passing. The first local run had a report-printing key typo after writing a correct JSON result; corrected `audit.py` and reran. The source records and counted values were unchanged. Python compilation and ZIP integrity checked. No official dataset, scientific first-use, model fitting, or model inference was performed.

**Scientific — UNVERIFIED:** Published-record arithmetic and provenance checks do not reproduce the H200 results or fully qualify comparable looped models. No independent train/infer FLOP count was executed. No causal discovery, cold retention, novel-world transfer or Yggdrasil intelligence advantage is demonstrated in this gate.

**Deployment — NONE:** No changes to `spoonman136668-ai/Yggdrasil`, its branches/PRs, Mind-Palace, runners, autonomous controller or CKAD research. At the verified gate checkpoint, Yggdrasil `main` remained `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; ENERGY-01 PR #1201 is draft/unmerged at `69123bc92cad8bc14fe6596f42d9b2f4e71a2542`; CKAD PR #1182 is draft/unmerged at `5df8dbf506027b914f66e19441376d1347a3e09d`. The latest workflow list includes unrelated G29 and fanout CI failures; these do not turn this source audit into native acceptance.

## Decision

**Do not spend another gate tuning parity/maze synthetic proxies**. The substantive remaining engineering task is independent **original-source GPU qualification** with the exact checkpoint evaluator, seeded benchmark custody, baseline cold-fit runs and source receipts, on an **authorized project-scoped runner**. A prior preflight found no authorized GPU execution route available in these tools; that block remains. Until it clears, energy research can inform hypotheses but cannot be promoted as a native Yggdrasil learning mechanism on this evidence.

## Reproduce this record audit

Run `python audit.py` from this folder to recompute ratios and checks using the selected transcript of source records. On a network-connected host, `python audit.py --verify-upstream` additionally downloads all five original GitHub files pinned to the commit, Git-blob-hash verifies them and compares selected numbers with the source records. It does not consume original test examples.