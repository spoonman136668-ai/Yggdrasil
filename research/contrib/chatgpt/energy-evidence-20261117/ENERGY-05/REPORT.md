# ENERGY-05 — incomplete-evidence intervention reasoning (source-free exploratory development)

Date: 2026-11-17 (UTC). Affinity: Yggdrasil, without modifying its native architecture, main branch, or accepted research assets.

## Objective and frozen source

Determine whether learned higher-order discrete energies infer missing causal states under incomplete noisy evidence better or faster than equally informed fitted exact symbolic inference and a trained four-step recurrent network. ENERGY-04 had succeeded in learning structures but had a direct-forward shortcut because all exogenous inputs were known; this study hides exogenous x2 at each test query and interventions sometimes disrupt forward propagation. The comparison is on synthetic binary/XOR structures, not original Yggdrasil world data or CRAM/HRM/TRM replication.

`prereg.json` SHA-256 `4ec55791a7aa6ec5328f298ac25606698ec48462d1e3037350adad618fa7ba16` and `experiment.py` SHA-256 `fc4961fd6c7343dac04b24ac96da6249588284da02b143026f17111c3c8c9a3f` were frozen in `freeze.json` before the first scored run. The sole smoke seed was 999 and is excluded from scoring. Scored seeds: 17, 29, 43. Six worlds (two/seed), each with 512 training, 128 validation, and 96 unseen test events. Training and evaluation events use disjoint seeded streams.

Each world has 3 exogenous inputs, 4 unknown causal XOR equations with up to 3 parents, and randomized interventions on endogenous y0, y1, y2. Test queries hide x2, show x0/x1 and a randomized subset of noisy y sensors plus the intervention. Per-world sensor corruption is randomized in 4%–16% and unknown to fitted methods. Every trained arm receives the same available event observations and intervention labels; the RNN has known training x2 values, and its target y is noisy measurement rather than latent truth. Ground truth is used only for evaluation and the nontrained Bayes ceiling.

## Frozen scored outcome: DEVELOPMENT NO-GO

| Solver | Correct complete 5-bit latent states | Fit + test inference, local CPU |
|---|---:|---:|
| Learned factor energy, four deterministic starts and twelve sweeps | 441/576 = 76.56% | 0.9237 s |
| Independently fitted exact symbolic posterior over x2=0/1 | 482/576 = 83.68% | 0.8276 s |
| Trainable four-step 48-hidden tanh recurrent network, two random starts, validation selection | 291/576 = 50.52% | 6.7057 s |
| Corrupted-outcome negative control (energy) | 188/576 = 32.64% | 0.9185 s |
| Ground-truth conditional Bayes MAP **diagnostic ceiling only** | 483/576 = 83.85% | noncomparative (no fit) |
| Exhaustive optimum of **fitted energy objective** | 418/576 = 72.57% | 0.8584 s |

The trained energy scheme recovered all 24/24 true synthetic XOR structural equations. It nevertheless recovered 41 fewer five-bit latent states than exact Bayesian inference using the same learned structures, and its measured whole-process cost was 1.116× symbolic (i.e. *slower*). It was ~7.3× faster than the particular Python recurrent implementation but **not at matched accuracy**; the recurrent baseline did undergo 2 Adam restarts and validation early stopping, but its strongest-model convergence/capacity adequacy is not proved. None of these CPU measurements supports an intrinsic energy-versus-HRM/TRM claim.

Energy coordinate descent found a global minimum of its *learned soft objective* on 566/576 = 98.26% queries, below the frozen 99% bar. Counterintuitively, exact minimization of that soft objective scored **worse** against world truth (418/576) than bounded descent (441/576). This means the soft learned objective sometimes rewards violating actual causal equations when sensors conflict; errors are not explained just by local minima or insufficient search. The exact symbolic control models deterministic structure and calibrated measurement noise rather than allowing violations of learned causal equations.

**Information limit:** 469/576 queries have at least one observed output which depends on x2 under the actual intervention; the other 107 are structurally unidentifiable from the available measurements. This does not imply the 469 are always statistically decidable under noisy sensors. On the 469 structurally identifiable queries: energy recovered 370, symbolic 434, and the diagnostic Bayes ceiling 435. The resulting best fitted symbolic accuracy closely tracks the Bayes limit.

## Independent post-result audit

`audit.py` was written only *after* frozen scoring. It does not import `experiment.py`. Its reconstructed training/validation/test events independently re-fit all 24 equations and sensor noise weights, recomputed exact symbolic and Bayes MAP outputs, brute-forced the learned energy objective, checked hard intervention clamps and non-identifiability, compared 576 outcomes and per-seed aggregates, and validated frozen source SHA-256 hashes. `audit_result.json`: PASS, 7,488 recorded audit assertions/checks, six worlds, 576 heldout query reproductions, six frozen-protocol checks plus 6 cold-restore checks in the scored study. Synthetic local audit, not independent native Yggdrasil scientific qualification.

## Qualification / authority

- **ENGINEERING:** local source freeze PASS; smoke PASS; 7,488 post-result independent checks PASS; `python -m py_compile` PASS. Full platform regression, native Yggdrasil build, CI, source atlas qualification: **UNVERIFIED**.
- **SCIENCE:** **DEVELOPMENT_NO_GO**. Exact symbolic beats energy on accuracy and time, energy misses the 99% objective-optimum gate, the recurrent comparison is not converged proof, and no real action–consequence learning or unfamiliar operator discovery is demonstrated.
- **DEPLOYMENT:** **NONE**. No project repository/PR changes, scientific first-use, original external heldout consumption, controller, runner, scheduled job, paid API, model acceptance, merge, or FORGE integration.

## Research decision

Freeze ENERGY-05 as another negative; do **not** rescue it by tuning restarts/weights/thresholds on the consumed cohort. The technically meaningful next test, if pursued independently and prospectively, must move to *non-deterministic or cyclic causal constraints* with genuine global uncertainty where direct forward symbolic inference is no longer an inexpensive near-Bayes-optimal ceiling. Frozen size/cost scaling, fully converged conventional comparators, intervention contrast validity, cold retention, novel factor-family transfer and strong exact controls must be kept. Until then there is no credible faster-reasoning promotion candidate.

## Reproduction

```sh
python experiment.py --smoke --out smoke-new.json
python experiment.py --out scored-new.json
python audit.py
```

Timing bytes depend on environment, and the independent auditor reads the committed `scored.json` instead of rerun outputs. The frozen model does not use the original research environment.