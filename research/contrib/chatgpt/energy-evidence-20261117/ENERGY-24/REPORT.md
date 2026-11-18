# ENERGY-24 — observed action-consequence evaluation of information-gain probing

**Date:** 2026-11-18. **Classification:** isolated synthetic development **NO-GO**; no native Yggdrasil checkpoint replay, source actor, protected scientific first-use, model mutation, merge, schedule, or deployment.

## Question

Does changing the acquisition policy from CKAD22's two-stage weighted forecast-disagreement/variance heuristic to expected information gain improve actual future policy reward and latent-context inference, with equally many witnessed interventions and the same correctly marginalized expected-reward planner?

## Frozen design

Original `prereg.json` SHA256 `7cc41274cd94786ed7040de7c507eb2da6a0439254b2004c10ece8e04003fdb5`; original executable `experiment.py` SHA256 `eaf999e65c2091b6753ece24933c492f337b9cc52747c009bff14b49af6f2d4b`. Both frozen **before primary scoring**, and remain unchanged. Source inspiration CKAD22 at native PR #1207 commit `5da91380fdbb7aeb955735ad39225ce8ac5e89c2`; native episode file Git blob `5c428b88bb46e251f6ced5b1aa6887b18d4c3faa`.

Three independent deterministic seeds 501,607,809, each with 128 distinct source-generated world parameter sets in each of two cohorts (latent old=7/8 from prior, or forced novel=1). Total **768 worlds**. Two conditional candidate tables were provided to each learner, not learned. Hidden ground-truth hypothesis stayed on source side. Each probe chose stage-one action, observed actual sampled next state, chose stage-two action, observed actual sampled reward, and updated the hypothesis posterior from that revealed pair only. No counterfactual observations or family labels supplied. The five cumulative budgets were 1,2,4,8,16 observed episodes, followed by 64 actual held policy outcomes per world/arm/budget. Main arms: variance/disagreement, information gain, seeded random. Additional descriptive controls: frozen untrained prior, hidden-context oracle. All arms had the same initial candidate information and intervention budget. Held evaluations did not update models.

### Primary 16-probe results (24,576 independently executed held decisions per cohort per arm)

| Cohort | Variance policy | Information-gain policy | Random | Frozen prior | Truth-informed oracle | IG minus variance |
|---|---:|---:|---:|---:|---:|---:|
| 7/8 old, 1/8 novel population | 18510 | 18510 | 18489 | 17704 | 18519 | 0/24576 = 0 pp |
| Forced novel shift | 18529 | 18520 | 18477 | 13374 | 18565 | -9/24576 = -0.03662 pp |

Frozen improvement gate required >=**2 percentage points** additional observed held reward in BOTH cohorts, hidden-context posterior-Brier no worse in BOTH, positive gain in at least two of three seeds for both, greater reward than random, and <=2x CPU. The reward/seed gates **FAIL**. Hidden Brier in the 7/8 cohort improved slightly (information gain 0.00109413 vs variance 0.00120283); in forced novel it worsened (0.01962223 vs 0.01932519). Seed-level 16-probe observed reward differences: prior [0,0,0], novel [0,0,-9].

Earlier probe budgets did not rescue the final claim: with 1 probe, IG fell behind variance by 56/24576 prior and 157/24576 forced novel. With 8 probes IG improved by 17/24576 and 36/24576 respectively, well below the frozen 2-pp gate. This is a low-complexity setting with known conditional tables, not proof about larger causal models.

### Computation, numerical caveat and negative evidence

Local Python full process used ~31.69 CPU seconds, ~32.78 wall seconds; peak reported RSS ~114 MB. Within this implementation, IG vs variance score-stage instrumented CPU ratios at 16 probes were 0.872 and 0.888, respectively; these **do not** establish neural/native speedup. No hardware-matched recurrent baseline or actual native Yggdrasil checkpoint was executed.

The independently written auditor initially used the mathematically equivalent KL information formula, which disagreed with the frozen scorer's subtraction-of-entropies expression at an extremely tiny posterior (about 7.38e-15). The two floating-point expressions crossed the arbitrary 1e-14 action tie threshold at one probe, causing a different trajectory. The initial failure is preserved as `independent_audit_first_failure.py`. The final auditor reproduces the **original unchanged scorer** formula for correct frozen byte-level trajectory reaggregation, checks original source hashes, independently reconstructs worlds/probes/held actual outcomes/posteriors, and reports **62,263 assertions PASS**. This is a numerical-stability limitation, not an excuse to retune after scoring.

### Engineering / science / deployment

- **ENGINEERING:** source/protocol frozen; local score and independent full 768-world trajectory audit PASS; source and all results have exact SHA-256 fingerprints in `custody.json`. Original uncompressed `per_world.json` is 3,031,524 bytes, SHA256 `74ce4b36e2fd25bd03825352d8cf0fc52bf4d5a99f7bfe57820f3cdd620a9a73`. The complete archive and replay-core archive are also hashed there. Cross-platform native G29 regression is **not a pass** from this study.
- **SCIENCE:** **DEVELOPMENT NO-GO**, no original scientific acceptance, no claim of trained energy model transfer, latent causal structure discovery, or full CKAD retention.
- **DEPLOYMENT:** NONE. No interference with CKAD23 or accepted main; do not promote information-gain replacement based on this null.

**Recommendation:** Close the information-gain-as-drop-in acquisition policy hypothesis for now. Revisit only when it adds genuinely new learnable structural information or a task-specific objective and beats native retained CKAD and strongest trained controls under new, frozen, externally qualified outcomes.