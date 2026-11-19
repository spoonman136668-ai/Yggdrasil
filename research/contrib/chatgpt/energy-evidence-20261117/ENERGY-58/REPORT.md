# ENERGY-58 — Three-episode cumulative causal readout retention

**Date:** 2026-11-19. **Classification: DEVELOPMENT_NO_GO (9 of 11 frozen gates PASS).** This is independently auditable **external synthetic research** in the existing draft PR #1210; not native Yggdrasil model training, scientific acceptance, deployment or an autonomous research-loop change.

## Custody and protocol boundaries

- Prior evidence archive HEAD: `1e5cf4e89f4155b78c82d1310a7a93a77bea925c`.
- Frozen scorer, independent auditor, isolated fresh-process checkpoint restore source: **`9e57af260fd10951cefee775e397edadac16331d`**.
- Separate preregistration, including frozen 11 gates and untouched primary seeds: **`a1db091f219b7f12e4cf95e37f1d6d8961a438a5`**. An arithmetic correction to the number of distinct interventions (from 448 to **508 = 3×84 + 4×64**) was committed **before primary scoring** at **`3fc81ffe4c910ce6a487fe68e9b3d8dc0ae744a9`**. No thresholds, seeds, models, or scoring code were changed after scoring.
- Excluded source-development pilots: `999211`, `999227`, world ID 0 across three mechanism families each. Both passed 7,888 independent audit checks and are **not** part of the confirmatory score.
- Actual primary, previously unused: **seeds `100181`, `100193`, `100207` × four world IDs × three families = 36 worlds**.
- Frozen source bundle SHA256 `59ced6691c87e2f9df39bd32c6044e6d9a32d7f6894078c75a1576cd97ad3a20`; Git blob `ea6a0073e9c9cb2361a7b058d9f4f9144d236d8b`. Individual source file SHA256 in `source_manifest.json`. No native code was touched.

## Hypothesis: protect old function while sharing learned relations

Can a learner carry causal relations learned from *three ordered experiences* into a new situation with less error than a strong directly matched conventional learner, while preserving real historical readout functionality after serialize/restart?

Each contributor-generated world provides 10 causal binary `do` variables and 2 correlated nuisance bits. It contains four planted signed pair-parity primitives and relations between them. World families: **`persistent`**, **`edge_reversal`**, **`novel_triple`** (the last includes a relation outside the candidate's pairwise relation basis). The simulator has fresh independently permuted causal action IDs, so exactly **508 underlying 10-bit assignments are disjoint** within a world: 84 witnessed OLD, 84 MIDDLE, 84 NEW, and 64 held outcomes in each OLD/MIDDLE/NEW/COLD context. Nuisance correlations change by episode; COLD nuisance cues are randomized. Observation noise is Gaussian σ=0.20. Learners never receive planted structure, withheld consequence labels, or evaluation outcomes.

The candidate selects four old-stage pair-parity supports using an ordinary OMP fit on **OLD training data only**. It fits three stage-specific graph Ridge models and marks edges as invariant when all three observed train-stage coefficient estimates have compatible magnitude, sign and range. It then jointly fits the selected invariant relation coefficients across all three sets of training observations, allowing other weights and biases to remain stage-specific. Original OLD and MIDDLE prediction heads remain frozen in the checkpoint; NEW and COLD use the final cumulative head. **The operator grammar (all pair parity primitives plus six pair products of four recovered primitives) is supplied**; this is neither unrestricted new operator invention nor a single mutable model that must infer episode identity.

Eight arms see identical **252 witnessed labels** per world: candidate; **matched separate-relations Ridge**; **standard stage-specific rehearsal Ridge** with all episode data but without invariant coefficient ties; unconditional-sharing ablation; full higher-order-feature ElasticNet; RBF kernel ridge; no-update; and shuffled new labels. The directly matched conventional controls have the same old-selected primitives and relational features. All arms are fully fitted; this is not a comparison against zero-trained baselines.

## 36-world primary held errors

MSE is lower-is-better; each entry is the unweighted mean of 36 world-held MSE values.

| Method | OLD held | MIDDLE held | NEW held | COLD held |
|---|---:|---:|---:|---:|
| **Cumulative invariants (candidate)** | **0.081079** | **0.078463** | **0.258021** | **0.403972** |
| **Matched separate relations** | **0.081079** | **0.078463** | 0.263906 | **0.411366** |
| Conventional stage-specific rehearsal | 0.081079 | 0.078463 | 0.263882 | **0.411346** |
| Unconditionally shared relations | 0.081079 | 0.078463 | 0.747025 | 0.854835 |
| Full-feature ElasticNet | 0.229066 | 0.191031 | 0.707507 | 1.585362 |
| RBF Kernel Ridge | 4.347870 | 4.307858 | 4.829513 | 5.324081 |
| No new correction | 0.081079 | 0.078463 | 1.264876 | 1.133947 |
| Shuffled new labels | 0.081079 | 0.078463 | 8.472165 | 8.554081 |

**Candidate improves cold transfer just 1.7973% over matched separate relations and 1.7924% over conventional rehearsal.** Both are smaller than the **preregistered 5.00%** improvement floor. Those are the two decisive scientific FAILs. Improvements against very weak full-input or sham controls cannot override them. Candidate cold error is also ~56.6% higher than its own NEW held error (0.403972 vs 0.258021), showing that nuisance-shift generalization remains imperfect.

### Independent cohort and family stability

| Seed | Candidate cold | Matched separate cold | Direction |
|---|---:|---:|---|
| 100181 | 0.475203 | 0.484748 | Candidate wins |
| 100193 | 0.507040 | 0.510321 | Candidate wins |
| 100207 | 0.229674 | 0.239029 | Candidate wins |

| Family | Candidate cold | Matched separate cold |
|---|---:|---:|
| persistent | 0.285726 | 0.287211 |
| edge_reversal | 0.043094 | 0.043143 |
| novel_triple | 0.883098 | 0.903744 |

The novelty-family error remains substantially above persistent or edge-reversal scenarios, even with original-relations retention.

## All eleven frozen gates

| Gate | Result |
|---|---|
| Cold ≥5% better than matched separate-relations | **FAIL** (1.80%) |
| Cold ≥5% better than conventional stage-specific rehearsal | **FAIL** (~1.79%) |
| Cold ≥10% better than best full-feature conventional nonlinear baseline | PASS |
| Wins versus matched baseline in at least 2/3 independent seeds | PASS (3/3) |
| No family >10% worse than matched baseline | PASS |
| OLD and MIDDLE prediction readouts unchanged within 1e-11 | PASS (exactly) |
| Cold ≥20% better than no-update | PASS |
| Cold ≥20% better than shuffled new-label negative | PASS |
| NEW held error ≤10% above matched separate | PASS |
| Every fresh-process cold-restart readout within 1e-11 | PASS |
| Serialized checkpoint ≤4096 bytes | PASS (maximum **1,101 bytes**) |

**9 PASS + 2 FAIL ⇒ `DEVELOPMENT_NO_GO`.** The reserved primary seeds were consumed exactly once. The identical-source replay is a deterministic duplicate, not a new scientific sample. The outcome must not be tuned against those seeds.

## Evidence, independent audit and true process restart

- **Independent generator + model refit audit PASS: 93,968 checks**, 36 worlds × eight fully trained methods × 4 held contexts, plus generator identities, disjoint interventions, checkpoint source decisions and all aggregate/seed/family metrics. The auditor does **not import** the scorer but uses matching NumPy/scikit-learn backends and an independently written rendition of the self-authored generator (not wholly independent science).
- **Fresh-process restoration PASS:** **36 new isolated Python processes**, each reading a serialized model checkpoint and *only unlabeled held input actions*, outputting **9,216 historical/new/cold readout predictions**. Largest numerical difference vs pre-serialization is **1.78e-15**. This is genuine cross-process JSON checkpoint readout reproducibility, rather than mere file-byte existence.
- **Unchanged-source replay PASS:** 2,427,842 canonical nontiming JSON bytes have identical SHA256 `9a8578c1350e1424df5853be26732ef618c9b0508eac9bf8c738645b02b130e4`. Independent replay auditor repeated **93,968 PASS checks**, and replay fresh-process readouts repeated **36 PASS processes**. Elapsed CPU seconds and per-arm time fields are deliberately excluded from semantic identity.
- **Archive:** `EVIDENCE.tar.bz2.part00...` reassemble to original `.tar.bz2` via concatenation. This retains original `primary.json`, its unchanged-source `replay.json`, both independent audits, separate-process receipts for original/replay, both excluded pilots and their independent audit receipts. See `archive_manifest.json` for byte hashes, and `verify_archive.py` to verify parts, complete original input provenance, checks, source hashes, case receipts and frozen classification. There is no need to store artifacts in the ChatGPT Library.
- Environment: Linux single-thread CPU, Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0; no GPU, paid API or physical Joule measurement. Full hosted CI and actual native Yggdrasil regression are **separate engineering gates**, not synonyms for the local source audit.

## Interpretation and next falsification

The important **positive** result is *functionally reproducible old and intermediate causal readouts after a genuine cold process restart*, not just surviving checkpoint bytes. The important **negative** result is that tying inferred invariant relation weights across episodes contributes **less than the frozen meaningful gain** relative to an exact-feature rehearsal/separate-context conventional control. Retention through explicit episode-tagged heads is not open-ended memory or general causal transfer.

No promotion to accepted native science, merges, controller changes, official science first-use or deployment. A successor should test whether a single adaptive causal readout without supplied context identity can retain and reuse earlier causal functions under interference and novel environments, against fully trained strong recurrence/rehearsal controls, with a new frozen independent generator. Avoid re-testing consumed ENERGY-58 primary seeds.
