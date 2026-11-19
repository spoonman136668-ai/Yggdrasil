# P0 — Quine functional-retention guard (research only)

**Disposition:** isolated engineering candidate; scientific result **UNVERIFIED**; no merge, owner training, accepted-state mutation, fresh first-use or deployment.

## Canonical research starting point

| Role | Immutable pin |
| --- | --- |
| Amalgam source for this isolated proposal | 86264b41a08d49f558418c0fba367f3a2636befa (PR #1278, draft) |
| Original joint 1,025-witness checkpoint **content SHA-256** | 576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8 |
| Frozen transfer-curve protocol **content SHA-256** | 22edfde67e981c561ade96b988e4ae9ba1f0d8cf2fb3ae6c9560b6f421b8a60e |
| Accepted main, unchanged | 5e74f8db85b2f5839c42148c0dfba69a88b1a2c9 |
| Original experiment | [transfer-curve-dev-01](transfer-curve-dev-01/README.md); [PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) |
| Owner / checkpoint-lineage audit | [PR #1322](https://github.com/spoonman136668-ai/Yggdrasil/pull/1322) |

The original joint SHA is a **checkpoint content hash**, not a Git commit. Source SHA is a Git commit, not trained weights. This pins the **experimental P0 anchor**, not an authenticated accepted continually trained model. The independent owner audit found no canonical continuously trained accepted model in inspected Git. Host-local checkpoint, ledger, runner and owner custody remain **UNVERIFIED**.

**Cold restore prerequisite:** use the original sealed native/JEPA donor blobs and the existing selection_trial.restore route. Verify the original P0 hash, complete original ledger and all four trained heads before new execution. Never substitute a 1,145-witness descendant for the 1,025-witness parent.

## Baseline failure and freeze

Original transfer-curve-dev-01 is **DEV_NO_GO**. Four replicas each continued from 1,025 to 1,145 witnesses. Final held native Brier **0.210820** failed against the mean best per-seed control **0.195822**. Familiar transition Brier rose from **0.091801 to 0.189425**, a **+0.097624** drift against the frozen maximum **+0.02**. The JEPA heads and selector did not rescue the study.

**Freeze additional JEPA gating heuristics or unconditional blending on this research line.** Do not modify the original frozen experiment or tune on its consumed held outcomes.

## Quine guard: engineering candidate

The additive research-only quine_retention.py:

1. Requires explicit, independently provenance-certified mastered-regime windows in the pinned original witness ledger. Selects 5–10 high *retrospective anchor-transition Brier* witnesses per range (default 8), with deterministic index tie-breaking. These scores are NOT original prequential surprise or independently demonstrated mastery. It uses binary terminal reward as signed ±1 proxy; this is NOT a measured action cost.
2. Pins original checkpoint and witness-ledger content, exact selected witness identities and the Quine manifest's SHA-256. Selection makes forecasts only; it does not replay 1,025 training witnesses, generate interventions or modify the ledger.
3. Checks each proposed single-witness shared-state update **before admission**, validating exact original/current witness prefixes and unchanged input checkpoint bytes.
4. **Vetoes** admission if ANY Quine transition or terminal-reward Brier drifts more than **+0.02** versus P0, or if either complete mastered-regime Brier or complete old-prefix Brier exceeds +0.02. The frozen 1/50 bound cannot be loosened by the caller.
5. On veto returns **the previously admitted current state**, not the original anchor. Reports rejected candidate's checkpoint hash as advisory provenance for a separately qualified context-gated specialist fork. It does not create a rival learner, persist or activate a fork, route policy through it, or assert a null-space projection.
6. Refuses wrong pins, rewrites, overlaps, unsupported/underfilled regimes, replay tampering and multi-witness jumps. Idempotent witness replay is a no-op.

Compact Quines do NOT replace separate held familiar testing; complete old-range checks remain mandatory. The guard alone does NOT prove that any useful new learning can pass it. It leaves accepted main, existing native action selection, the original frozen study and JEPA parameters untouched.

## Next qualifying experiment — NOT RUN

First authenticate the native owner/runner, obtain a P0 cold-restore receipt and certify real mastered-regime windows; then pin the Quine manifest into a **new preregistered** protocol with genuinely fresh development worlds, seeds, splits, charged outcomes, cost/compute caps, negative controls, strict stop criteria and non-overlapping source custody. Do not run protected scientific first-use or disturb another active owner.

Compare unchanged native, unconstrained native continuation, Quine-veto native continuation, separately qualified context specialist where appropriate, and **fully fitted** full-history/trailing/change-point/structural Bayesian/exact symbolic controls under matched public actions, information and budgets. Preserve independent old-regime and unfamiliar held rows. Reconstruct every trial from exact checkpoints and receipts.

**Joint scientific PASS requires ALL**: each Quine and each mastered-regime transition/reward Brier delta <= +0.02; whole old-prefix and separate withheld familiar retention within the bound; genuinely unseen held transition Brier better than the same-cohort strongest control, with the historical **0.195822** reference reported separately; cold restore and receipt replay; cost accounting; no label leakage. Beating 0.195822 on a different cohort alone is not proof. The old frozen 0.01 per-seed advantage may be unidentifiable for some held-label mixes; address this in prospectively designed fresh cohorts, not by changing consumed labels or thresholds.

A successful isolated code test is **engineering only**. Mandatory exact-SHA/tree full regression on Ubuntu/Windows and independently authorized science/acceptance are separate gates. No automatic promotion or merge.

## Work explicitly deferred

- **Causal-role P3:** new action-permutation and charged-probe study only after retention. [PR #1327](https://github.com/spoonman136668-ai/Yggdrasil/pull/1327) is an independent review brief, not a completed P3 implementation.
- **CKAD41–49 SCDR/H1:** read-only loop-obstruction diagnostics first; an H1 cycle alone cannot identify an omitted physical latent state. Require reproducible charged intervention inconsistency and strong controls before any variable minting. [CKAD audit PR #1320](https://github.com/spoonman136668-ai/Yggdrasil/pull/1320) found **0/9 scientific DEV_PASS**.

**Engineering:** guard/tests proposed, exact final CI not yet verified. **Science:** previous transfer FAIL; next fresh study UNVERIFIED. **Deployment:** none. **Owner:** independent custody/first-use qualification remains required.
