# MR32-M first task-derived utility development result

Date: 2026-10-31

## Disposition

**Frozen development result: NO-GO for MR32-H as currently specified.**

The trial did demonstrate policy-specific post-use task-return feedback, FIT/TRANSFER separation, and exact Windows/Linux event reproducibility. It did not meet the precommitted improvement criteria against the stronger interaction-capable Bayesian control. Preserve this as a negative result. Do not retune MR32-H, the held-out seeds, thresholds, task generator, or Bayesian comparator using these TRANSFER observations.

## Exact evidence identity

- Frozen protocol: 93a63fcdddbfce61eb78848c2665dcd4d14672ce
- Protocol clarification: d7b96160fd5baf2f26650b1ff3be8f42372a0b4a
- Exact executed candidate head: 1ab092e663739603e86f03ad3561f8401ab1e64e
- GitHub Actions run: https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/41228395152
- Windows job: PASS
- Ubuntu job: PASS
- Focused regression suite: 67/67 PASS on each OS
- Source-only contract assertion: PASS on each OS
- FIT events: 768 across 48 frozen episodes
- TRANSFER events: 1,024 across 64 held episodes / 16 seed clusters
- FIT post-use feedback receipts: MR32-H 320; Bayesian 303
- TRANSFER feedback: zero for both learned methods
- TRANSFER event SHA256 on both OS: 5eb3145cffa0f0550768cf4721b03f72b4fa5342d6e2ede25dbc63ddc7191c1b

## Frozen TRANSFER results

Mean task return per task event (higher is better):

| Method | Mean return |
| --- | ---: |
| Random | -0.041015625 |
| Evidence-only | -0.001953125 |
| Fixed recency | 0.005859375 |
| MR32-H learned utility | 0.0751953125 |
| Interaction Bayesian utility | **0.0791015625** |

MR32-H exceeded random, evidence-only and fixed recency. It did not exceed the strongest comparator, the interaction Bayesian control:

- Difference versus strongest comparator: **-0.00390625** (required >= +0.02).
- Paired seed-cluster wins versus Bayesian: **8/16** (required >= 12/16).
- 2.5th percentile paired cluster-bootstrap bound versus Bayesian: **-0.025390625** (required > 0).
- Per-regime win threshold: **FAIL** (required >= 6/8 in each regime).
- FIT/TRANSFER seed disjointness: PASS.
- Zero TRANSFER feedback: PASS.
- Cross-OS event and result reproducibility: PASS.

The frozen development_signal was false on both OSes. This is a substantive negative outcome, not a CI failure.

## Resource evidence and limitations

On the recorded runs:
- Windows process CPU: 1,343,750,000 ns; process peak working set: 25,980,928 bytes.
- Ubuntu process CPU: 1,079,093,133 ns; process peak RSS: 25,059,328 bytes.

These are whole-process measurements on different GitHub-hosted workers, not isolated model costs or matched CPU/RSS comparisons. This run predates the later diagnostic selector-state byte breakdown and the Bayesian control's additional integrity-checked snapshot/restore gate; those additions do not change this result's model-selection logic, but they still require exact-head qualification.

The task generator is a controlled, deterministic task fixture. The outcome-derived utility signal is no longer an externally supplied usefulness label, and is tied to the action stored in each memory; nevertheless this is **not** an independently admitted source-family task, original-world reward, or protected first-use trial. It cannot establish source-neutral transfer or native cognition.

## Next action

Retain MR32-H and its Bayesian comparator as a negative benchmark. Any new utility mechanism must have a new preregistration and disjoint TRANSFER cohort before execution. The existing held-out cohort is consumed and cannot be reused for tuning. An authentic original-source task-reward experiment remains blocked by the independent FSA-04 authority and first-use boundary in FORGE issue #83.

No integration, merge, promotion, accepted-ref mutation, native runner/controller/queue change, paid API or protected scientific first-use was performed.
