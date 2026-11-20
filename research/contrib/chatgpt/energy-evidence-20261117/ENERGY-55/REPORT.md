# ENERGY-55 — Matched-intervention causal representation, exploratory screening

**Classification: UNPREREGISTERED — EXPLORATORY_SCREEN_NO_GO**. Date: 2026-11-19. External synthetic experiment; not native Yggdrasil model training or SCIENTIFIC_PASS.

## Research question

Earlier external ENERGY-49 showed diversity can improve acquisition within a supplied operator dictionary; ENERGY-50/51/52/54 did not establish robust transfer to new mechanism classes, and ENERGY-53 failed per-seed stability. ENERGY-55 probes an upstream representation problem: can controlled one-bit `do` interventions reveal which of twelve observable variables truly affect hidden fourth-order parity, threshold and conditional consequences, despite correlated nuisance cues that shift at cold evaluation?

The new candidate screens inputs by **mean squared paired response difference**. The decisive same-budget conventional counterfactual is **mean absolute paired response difference**: it uses the exact same 72 paired observations and chooses exactly six bits before fitting the identical kernel-ridge model. Other conventional same-label controls include supervised mutual information, ExtraTrees and linear ElasticNet variable ranking; raw 12-bit kernel ridge with and without cross-validated hyperparameters, 12-bit ExtraTrees, random 6-bit selection, and a shuffled-label matched-pair sham. This is classical variable screening, not a claim of newly invented native cognition.

## Source and study design

The **two screens were scored before GitHub source/protocol freeze**, using excluded developmental seeds `99983` and `99989`. Consequently this contribution is **UNPREREGISTERED**, not prospective confirmation, regardless of how well individual metrics look. No source or threshold tuning was applied after either independent cohort's result except updating the initial pre-freeze exploratory scorer to add stronger conventional controls, after which both screens were regenerated unchanged. Final source and original scorer hashes and reproduction requirements are in `provenance.json`.

Twelve worlds per seed: four world IDs across parity4, threshold4, conditional4 synthetic nonlinear factors; six contributor-planted causal variables hidden among twelve observed binary inputs. Two randomly chosen noncausal bits are observationally correlated with causal bits in OLD and NEW and independent at COLD. The initial action-consequence stream includes **72 paired old interventions** (36 one-bit flips, 3 per observed bit), **24 further old-context labels**, and **48 new-context labels**; all learners receive identical 144 labeled examples. OLD, NEW and COLD each have 96 separately generated held-out labels inaccessible to learners. *Causal action assignments may coincide across streams; this evaluates nuisance-distribution shift, not disjoint causal-assignment novelty*. Exact hidden world mechanisms are known to the test generator but not model input; they use author-specified parity, threshold and gated functions. The downstream head is ordinary scikit-learn regression trained separately for old and new; no persistent native Yggdrasil weights are involved.

## Aggregated exploratory results: 24 worlds, 10 arms

| Fixed downstream representation policy | Old MSE ↓ | New MSE ↓ | Cold MSE ↓ |
|---|---:|---:|---:|
| **Conventional paired absolute contrast + RBF KRR** | 1.663797 | 2.163401 | **2.165165** |
| Candidate paired squared contrast + RBF KRR | 1.685727 | 2.192264 | 2.227677 |
| ExtraTrees feature-ranked six-bit + RBF KRR | 2.174201 | 2.449653 | 2.525648 |
| Full 12-bit RBF KRR with TRAIN-only cross-validation | 2.207871 | 2.333163 | 2.549705 |
| Linear ElasticNet-selected six-bit + RBF KRR | 2.640829 | 2.527886 | 2.625045 |
| Fixed full 12-bit RBF KRR | 2.251535 | 2.455175 | 2.656415 |
| Mutual-information-selected six-bit + RBF KRR | 2.537729 | 2.806665 | 2.967429 |
| Full 12-bit ExtraTrees | 3.389838 | 3.358180 | 3.562289 |
| Random six-bit + RBF KRR | 3.132715 | 3.599349 | 3.712446 |
| Shuffled-pair-effect six-bit + RBF KRR | 3.518217 | 3.645646 | 3.836755 |

The candidate cold mean MSE **2.227677** was **2.887% worse** than the strongest matched conventional pair-absolute method (**2.165165**), though better than the less informed passive controls. The squared and absolute paired estimators chose the **same six causal-feature set on 23 of 24 worlds**. The squared method exactly recovered 141/144 planted causal bit memberships (**97.9167% recall**) and conventional absolute recovered 142/144 (**98.6111% recall**). A simpler conventional method did at least as well on both accuracy and correct causal-variable identification. Zero evidence of novel energy-specific representation superiority.

Per excluded seed: `99983` candidate cold **2.069716**, paired-absolute **2.069716**; `99989` candidate **2.385638**, paired-absolute **2.260614**. One tied and one lost; no per-seed superiority. The stage-new prediction MSE was candidate **2.192264** vs paired-absolute **2.163885**, also a loss.

## Verification and limitations

- **PASS:** Independent deterministic pairing audit verified three controlled pairs for each observed input bit; all selected input identities; source-reconstructed train data; all per-arm held predictions and MSE; and aggregate scores. Two excluded screens: 36,284 checks each, **72,568 total PASS**. Source generator and NumPy/sklearn estimator implementations remain shared, not wholly independent science.
- **PASS:** A single unchanged-source replay of seed `99983` matched every non-timing semantic field byte-for-byte; canonical timing-free SHA-256 is recorded in `replay_receipt.json`. Fit/predict timings change on replay and are explicitly excluded; this is not a full end-to-end compute benchmark.
- **PRIMARY NOT RUN:** reserved seed cohort `9811`, `9827`, `9839` untouched. No PR merge, native Yggdrasil acceptance, real-world causal action acquisition, science first-use or deployment.
- **Validity constraint:** The scorer was built and exploratory cohorts observed before archival source commit. The contribution is **UNPREREGISTERED** by the repository's own contribution rules. This result cannot be rebranded as confirmatory by committing retrospective thresholds.

## Decision

**EXPLORATORY NO-GO** for the squared contrast mechanism: no evidence it outperforms the standard matched-intervention absolute-contrast method using the same actions and downstream learner. Retain both exploratory cohorts, source and independent audit as a negative control on future proposals. The useful signal is in **paired intervention evidence itself**, not a proposed new estimator. A future study should test genuinely novel compositional causal operators learned from held-out action consequences, with independent generator and frozen controls before any confirmatory scoring, rather than tuning two nearly identical contrast norms.
