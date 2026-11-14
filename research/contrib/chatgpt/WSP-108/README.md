# WSP-108 — prospectively frozen causal-action rule programming (synthetic DEV)

**Purpose:** Test actual **direct numerical weight programming** for unseen synthetic causal mechanisms, and whether learned associations survive distinct-world interference and predict the consequences of unobserved interventions. This track stays independent of the tokenless/native Yggdrasil substrate; it is not an architecture replacement or a model promotion.

## Provenance, authority, and scope

- **Parent:** qualified WSP-107 draft [PR #1060](https://github.com/spoonman136668-ai/Yggdrasil/pull/1060), exact SHA `f06b9e87417deb69a8f6e3995e27cc08909b934d`, tree `33156ebfe16b576af8d6ce917c7ebba5d1c199c3`. The prior historical real-TRAIN-only WSP107 TransE run completed four fixed epochs but underperformed WSP105, and WSP106's separate frozen DistMult run failed numerically. Both negative results are **preserved** without post-result edits.
- **Preimplementation prereg:** `prereg.json` committed at `8a82e952d7a4d00398fba9fee2f19c0806bef04d` **before all WSP108 code**. Strongest conventional structural max-pooling arm separately added in `prereg_addendum.json` committed at `97aa4c1f85e65554d4829709d7db1bb06f8344dc`, **also before all world or model code and before reading any fit/transfer oracle labels**. No post-result parameter changes permitted.
- **No original historical data:** no Wikidata source, its valid/test files, any WSP101 protected original cohort or independent scientific first-use. All observations and labels arise from new, precommitted deterministic **synthetic** worlds. These synthetic worlds do not prove general intelligence or real-world causality.
- **Strict authority:** isolated stacked draft PR; no accepted model/refs, merge, private runner, paid APIs, scheduled tasks, controller actions, cross-project integration, deployment or live functionality.

## Identifiable causal-rule experiment

Each world has a hidden, SHA-derived **3 × 3 ordered relation-pair causal law**, with exactly four active rule pairs. The models never see that law. They receive the **same ten physical action/outcome observations**: each of the nine singleton two-hop path types is introduced with an edge-add intervention and its consequence is observed, plus one no-path negative observation.

The three classes of models must then predict **64 independent counterfactual edge-add/removal interventions per world**, each with two to five potential typed paths between novel opaque entities. For every query they predict the **before** state, **after** state and whether the intervention changed the outcome. The withheld oracle consequence is consulted **only after all models' predictions are frozen and SHA256 sealed**, never for learning, hyperparameter selection or feature engineering.

The FIT cohort has **12 worlds (11001–11012)**; the unfamiliar TRANSFER cohort has **12 separately seeded worlds (21001–21012)**. Mechanism-law patterns and entity identity overlap are reported honestly, not presumed disjoint. The task tests **few-shot rule adaptation to unseen entities and law settings with 10 allowed interventions per world**, *not* zero-shot transfer to an arbitrary causal world.

## Independently implemented controls, equal information and action budgets

- **Direct numeric programmer:** stores observed singleton consequence by writing each of nine `float32` causal rule weights **directly** in an individually keyed world-specific `3x3` matrix. No gradient. Predicts by the numeric dot product of directly written weights and observed two-hop path indicators. Keeps tamper-checked, cold-restorable snapshots across subsequent world-law changes.
- **Independent symbolic control:** writes the same nine observations into a relation-pair dictionary and uses an independently coded graph-path evaluator. It is capable of saturating this identifiable task, a crucial strongest baseline.
- **Conventional logistic:** fit an L2-regularized logistic model to *exactly the same ten observations per world*, with a deterministic full Newton solver, fixed regularization **0.03**, stationary gradient infinity norm **<=1e-9**, at most **100** updates, and **100% support-set classification** required. Two precommitted heads use those same learned weights: additive logistic and stronger **per-kind max-pooled logistic** (OR inductive bias) designed not to be a strawman.
- **Negative controls:** no-feedback all-zero predictor and rotated (incorrectly mapped) causal-feedback programmer, on the same test data.

Primary outputs: FIT/TRANSFER post-intervention accuracy, **actual action-causes-change** accuracy (including cases where the answer does or does not change), conditional changed/unchanged accuracy, model prediction SHA256 frozen before evaluator labels, world-law novelty count, exact cold-restoration after all 24 world updates, training convergence, CPU/wall and parameter costs. False positives, nulls, baseline parity, saturation and negative outcomes must be retained.

**Interpretation:** Even 100% DEV prediction would establish only a small **synthetic identifiable law-composition capability**. The independent symbolic and conventional max-pool arms can match the numeric programmer. An exact match is a valuable **null result for superiority**, not scientific proof of an unconventional intelligence advantage. Bigger independently frozen tasks require partial observability, intervention budgets that make mechanisms nontrivial, cold multi-task retention and stringent externally qualified controls.

## Qualification and first use

Fixture tests run **only seeds 51001/51002**, separate from both planned science-DEV cohorts, with positive/negative, tampering, action consistency, deterministic cold copy and convergence checks. Before the one-shot FIT/TRANSFER evaluation, mandate complete inherited WSP80–WSP108 and Yggdrasil root regression **on Linux and Windows**, generated G29 exact-source atlas and independent G29 acceptance, pinned Python 3.12 / NumPy 2.2.6 and complete source cleanliness.

Use no PR uploads/artifact files for model outputs: aggregate JSON in the read-only ephemeral public GitHub workflow log only. No automatic acceptance or deployment; record results and stop if prereg criteria fail.
