# ENERGY-12 — Adaptive classical energies for unfamiliar causal interactions

**Classification: LOCAL ENGINEERING PASS; SCIENTIFIC DEVELOPMENT NO-GO; NATIVE QUALIFICATION UNVERIFIED; DEPLOYMENT NONE.**

Completed 2026-11-17 in an isolated Linux CPU sandbox. This is a prospective **source-free synthetic development benchmark**, not native Yggdrasil training, not a CRAM reproduction, not scientific first-use of any protected environment, and not evidence of general intelligence. All frozen outcomes are retained, including negatives.

## 1. Verified context and custody

- Repository: `spoonman136668-ai/Yggdrasil`; `main` SHA `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` at latest current-turn GitHub check.
- ENERGY-01 draft PR #1201 unchanged at `69123bc92cad8bc14fe6596f42d9b2f4e71a2542`; CKAD PR #1182 separately at `5df8dbf506027b914f66e19441376d1347a3e09d` at latest check. No ENERGY-12 PR created.
- Read-only Mind-Palace v2 reference was pinned to `4f0ef7cda0441116b253fc53ac11cedd47ce24dc` in the previous continuation checkpoint. Historical project/governance context is advisory, not source execution authority.
- New source and preregistration were smoke-tested **before** source freeze; the smoke's first mechanical problems (missing smoke checkpoint directory, timing-key mismatch) were corrected before freeze and scoring. The original error attempts remain evident in conversation history; scored source was not changed afterward.
- Frozen `experiment.py` SHA-256 `e07962e2e6a2986950d67ec613e8510d2ac4ff0f06b21c8fc4ff2ce0555e32c6` and prereg SHA-256 `b1a3dcbcb365cc38220e2bf8558e959e179499de5b95a9122bd4570d224b0d5c`, committed to local `freeze.json` before scored outcomes. Independent auditor SHA-256 `48eeceea70f90af35d047ea41ac286e2ca227687d684458f4483a0fc933ab819`.
- No modifications to GitHub branches, runners, controllers, accepted checkpoints or research schedules. The repository's mandatory final regression, G29 code atlas and owner-controlled native scientific acceptance were **not** executed.

## 2. Research question and experimental design

**Hypothesis:** A compact, sparse learned energy that **activates three-way monomial features only when lower-order evidence is insufficient** can discover previously unseen higher-order causal laws and transfer to unobserved interventions more efficiently than exact sparse-algebra inference and trained recurrent inference.

Every world has five independently intervenable binary parent variables and a binary consequent. The consequent is the XOR of three unknown conjunction monomials, each involving up to three parents. The formula is unknown to all inference arms. There are 32 possible intervention settings. Each arm observes the exact same 20 distinct intervention outcomes and must predict the remaining 12. No heldout outcomes, chosen true monomial indices or heldout labels are passed to any fit function.

- **In-distribution:** 48 new worlds, all three monomials degree 0–2, 576 unseen queries.
- **Higher-order heldout worlds:** 48 new worlds, exactly one three-input conjunction among three monomials, 576 unseen queries. These 48 worlds are generated under distinct seed streams.
- **Adaptive energy:** minimize `E = 4 × training-errors + number-of-active-monomials`, restricting to at most three active terms. Begin with 16 degree-≤2 basis terms. If the best local solution still contradicts seen evidence, activate 10 degree-3 candidate features. Eight seeded bounded restarts, up to 32 single-bit/swap sweeps. The same energy objective is used for the exact reference.
- **Exact reference:** exhaustive enumeration of all degree-≤3 coefficient vectors containing at most three active terms (1 + 26 + 325 + 2,600 = **2,952** hypotheses); lexicographic tie-breaks. This is the strongest same-objective control.
- **Restricted reference:** exactly the same exhaustive method but with no three-way features (1 + 16 + 120 + 560 = **697** hypotheses). It isolates the representational benefit.
- **Incorrect evidence:** learn from the complemented 20 observed labels while scoring against the unchanged world. This measures evidence dependence, not validity under real interventions.
- **Recurrent comparator:** a 48-hidden-unit GRU, 20 steps of six numerical features (five parent intervention bits plus observed consequence), 32-output supervised truth-table readout. Trained on 1,000 independently generated prior synthetic worlds and validated on another 256, with both lower-order and higher-order families in meta-training; evaluated on the same 20 observed interventions. Frozen Adam learning rate, capacity, max 80 epochs, and patience 10. Its meta-world supervision and parameter budget differ from the per-world energy/exact learners; **do not infer matched-information or compute-parity architectural superiority.**

**Crucial limitation:** the operator vocabulary, XOR composition and possible degree-3 monomial forms are part of the declared algorithm. The energy learner discovers which supplied features are relevant; it does **not** invent a new causal primitive outside its permitted algebra.

**Prospective pass threshold:** ≥95% high-order heldout accuracy, no worse accuracy than exact on either family, energy ≤50% of exact and recurrent inference cost (with recurrent training tracked), negative high-order evidence control at least 15 percentage points worse, and independent audit PASS. No post-result tuning; no integration regardless of outcome.

## 3. Frozen scored results

| Method | Degree ≤2 familiar | New degree-3 interactions | Combined |
|---|---:|---:|---:|
| Adaptive energy | 551/576 (95.66%) | 530/576 (92.01%) | **1,081/1,152 (93.84%)** |
| Exact ≤3 symbolic | 576/576 (100%) | 554/576 (96.18%) | **1,130/1,152 (98.09%)** |
| Exact restricted ≤2 | 576/576 (100%) | 441/576 (76.56%) | 1,017/1,152 (88.28%) |
| Trained GRU | 386/576 (67.01%) | 389/576 (67.53%) | 775/1,152 (67.27%) |
| Complemented evidence | 199/576 (34.55%) | 149/576 (25.87%) | 348/1,152 (30.21%) |

**Mechanism identification:** Exact identified all 48 true familiar coefficient vectors and 43/48 heldout degree-3 vectors (91/96 total). Energy identified 40/48 familiar and 37/48 higher-order true vectors (77/96 total). Energy expanded its allowed feature basis on 12/48 familiar and 46/48 higher-order worlds. The unexpected expansions in familiar worlds reveal a local-optimization weakness: the initial lower-degree solution can remain inconsistent even when the true lower-degree model exists.

**Optimality diagnosis:** Energy cost exceeded the exhaustive global minimum on eight familiar and six higher-order worlds. Across the 48 higher-order worlds, energy equaled exact coefficients in 42. The 24 additional higher-order query errors relative to exact are concentrated in the six worlds where the local objective minimum was missed. Exact itself made 22 heldout errors because some sparse functions are observationally indistinguishable from only 20 of 32 intervention outcomes.

**GRU training limitation:** The GRU ran all 80 frozen epochs; best validation BCE 0.478545 at epoch 76. The frozen patience stop was *not reached*. It is a trained comparator, but not a verified fully converged comparator. No results justify claiming energy is inherently superior to a properly fitted recurrent architecture.

## 4. Cost and audit

Measured in this local Python 3.13 / NumPy / PyTorch CPU sandbox (summed per-world fit and inference; includes interpreter/implementation overhead and is not FLOP-normalized):

| Method | Measured wall time |
|---|---:|
| Adaptive energy | **0.2411 s** |
| Exact enumeration | **0.0703 s** |
| Restricted exact | 0.0218 s |
| Incorrect-evidence energy | 0.1178 s |
| GRU inference | 0.0547 s |
| GRU separate meta-training | **5.0745 s** |
| All-method scored process, including GRU fit and I/O | **6.5521 s** |

Adaptive energy is **3.43× slower than exact enumeration**, while also producing fewer correct predictions. The negative evidence control drops from 92.0% to 25.9% on the high-order cohort, supporting dependence on observed intervention consequences. Whole-process costs cannot be compared fairly to the GRU without an amortization schedule and matched meta-learning budget.

**Independent audit PASS:** `audit.py` reimplements generation, hidden truth construction, exact enumeration and all scoring *without importing the experiment program*. It verified all 96 cases, disjoint observation/query partitions, same-information prediction reconstructions, costs, coefficient bounds, conditional growth behavior, exact global minima, and independent GRU checkpoint inference. **3,515 individual assertions** and **350,304 exact candidate evaluations** completed. Scored JSON SHA-256 `4d85648c778b3f346ffa2cf8b9187a8236f43ba0b56be6050923bd8ba1f95bb3`.

## 5. Classification and research decision

- **ENGINEERING — LOCAL PASS:** frozen synthetic evaluation, pre-scored independent smoke, numerical/custody audit and reproducible source files.
- **SCIENCE — NO-GO:** energy accuracy 92.0% OOD fails ≥95%; exact is more accurate on both cohorts and 3.43× faster; recurrent full convergence unverified.
- **DEPLOYMENT — NONE:** no Yggdrasil native tests, scientifically sealed qualification, model changes, runner, loop, PR, merge, or accepted-state mutation.

**Plain English:** Letting an energy learner construct a richer relationship representation helps it reason about new intervention combinations, but on this task a simple exact symbolic learner both learns better and runs faster. The local optimizer sometimes cannot find an existing correct representation; this is an optimization shortfall, not proof that the causal primitives cannot represent the data. We should stop relying on repetitive toy search improvements and next test genuinely non-polynomial, stateful causal mechanisms with cold retention and information-matched trained comparators. Do **not** claim success over trained looped models from the underfitted GRU.

## Reproduce

Run only from a fresh scratch copy of this evidence package to avoid overwriting immutable receipts:

```bash
python experiment.py --smoke
python audit.py --file smoke/smoke.json
python experiment.py
python audit.py --file scored.json
```

`freeze.json` binds the exact source and preregistration; `MANIFEST.json` binds the completed artifacts. Regenerated count-based outcomes should match; CPU timing and PyTorch training weights may vary across hardware and environment versions.