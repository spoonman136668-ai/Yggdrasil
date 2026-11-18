# ENERGY-08 — genuine energy-incumbent warm starts against exact inference

**Date:** 2026-11-17. **Overall decision: DEVELOPMENT NO-GO for faster certified reasoning.** Engineering local benchmark and independent numerical audit PASS. Scientific superiority UNVERIFIED/FAIL; recurrent comparator did not converge. No native Yggdrasil integration or original scientific first-use.

## Exact checkpoint and provenance

Read-only GitHub checkpoint before work: `spoonman136668-ai/Yggdrasil` main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. ENERGY-01 draft PR #1201 remains unmerged at `69123bc92cad8bc14fe6596f42d9b2f4e71a2542`. Existing CKAD PR #1182 was not modified. No ENERGY-08 PR was present in GitHub search. No GitHub writes, runner dispatch, scheduled tasks, accepted-ref edits, owner changes or deployments.

Original ENERGY-07-R1 was a negative, with energy-guided MILP better feasible incumbents in 65/72 instances but fewer optimality certificates and no total speed win. **Its energy cutoff was not a true solver warm start.** ENERGY-08 instead passes a complete feasible bit assignment as the incumbent to a new exact branch-and-bound solver, reducing the upper bound for pruning. A separately stronger, presolved HiGHS MILP is an independent solver control. This is still small-scale synthetic development, not a CRAM/HRM/TRM reproduction.

- Frozen prereg and source hashes: `freeze.json` (created before any scored calls).
- Frozen code SHA-256: `76726fe41b89f9e8407a37c8a49d67ef691c5b86d8f0949f2c79816767c5afa6`.
- Frozen prereg SHA-256: `116c4a2306f3194a39bde540ca759649baf968df000001e8ea710471c0c23b05`.
- Previously qualified reused ENERGY-07-R1 source copy SHA-256: `c67ab62bff3ee640a53140a176c850b681a7081cf2b476f1c6b96e1d3f1b5046`.
- New scored seeds: 881, 1021, 1429. Sizes: 16, 24, 32. Four unseen test instances per seed-size = 36 cases and nine distinct fitted worlds. Smoke seed 9001 was separate.
- Every world has 320 fully labeled training observations, 48 calibration observations and random 3/4-way factors with **known factor scopes**. The model learns noise reliabilities, not the topology, and predicts a hidden state from noisy syndromes, unary observations and a truthful hard clamp.
- Fixed 0.18-second nominal per-case search budgets. Cold and warm BnB use identical branching, lower-bound logic and 8,000-node caps. Energy fitting and feasible-incumbent generation are charged; warm search receives less remaining search time. HiGHS presolve is enabled.

## Frozen results

| Variables | Test instances | Cold BnB optimality certificates | Warm BnB certificates | Presolved HiGHS certificates | Warm strictly better feasible than cold |
|---:|---:|---:|---:|---:|---:|
| 16 | 12 | 12 | 12 | 10 | 0 |
| 24 | 12 | 12 | 12 | 1 | 0 |
| 32 | 12 | 0 | 1 | 0 | 9 |
| **TOTAL** | **36** | **24** | **25** | **11** | **9** |

A branch-and-bound certificate here means the custom exact search exhausted all branches that could beat its incumbent using nonnegative admissible cost bounds before time/node limits. On all 12 sixteen-variable cases, an **independent exhaustive evaluator** checked all 2^15 = 32,768 clamp-feasible assignments (393,216 total) and agreed with the certified minima. On larger cases, the auditor checked feasible objective values and certificate consistency but did not independently exhaust all 24-/32-variable assignments. Thus certified counts remain **custom-solver certificates** on larger graphs, not separately verified by a second unrestricted exact run.

Warm BnB found strictly better feasible objective values on 9/36 cases, worse on 0, tied on 27. All nine improvements occurred at 32 variables. At the largest size, only one warm BnB case had an optimality certificate. A feasible low-energy assignment is **not** proof it is the truth or globally optimal.

Whole-process fit plus inference elapsed on the local CPU, seconds:

| Variables | Energy only | Cold BnB | Warm BnB | Presolved HiGHS | Trained recurrent |
|---:|---:|---:|---:|---:|---:|
| 16 | 0.142 | 0.168 | 0.180 | 1.573 | 3.028 |
| 24 | 0.194 | 0.987 | 0.786 | 2.310 | 3.879 |
| 32 | 0.245 | 2.336 | 2.274 | 2.483 | 5.371 |
| **TOTAL** | **0.581** | **3.491** | **3.240** | **6.366** | **12.278** |

Warm exact search is approximately 1.08× faster than cold exact search in this local implementation, **not the preregistered 2× target**. At 16 variables, warm actually costs more. Different solver implementations (Python custom BnB vs SciPy/HiGHS) have dissimilar performance profiles; these results should not be extrapolated to optimized hardware or general reasoning systems.

Whole-hidden-state truth recovery out of 36: energy-only 9, cold BnB 9, warm BnB 12, presolved HiGHS feasible output 4, recurrent 0. The low rates partly reflect underdetermined, noisy hidden states; a fitted-objective optimum is not necessarily ground truth.

## Recurrent control limitation

The comparator was a fully *executed* supervised trainable 12-step recurrent factor-message network with three learned shared scalar parameters and Adam. It received the same train and calibration observations; nine worlds ran all 25 fixed epochs. All nine **failed to meet the validation early-stopping convergence condition**, with training BCE ~0.75–0.785 and validation BCE ~0.759–0.806. Its 0/36 exact-state recovery cannot justify claiming superiority over trained looped reasoning networks, HRM/TRM, or other capacity-matched controls. This was a weak and not fully converged baseline, despite completion of its fixed training budget.

## Independent audit and control gap

`audit.py` imports neither scoring solver. It verified source hashes, freeze/seed coverage, independent energy reconstruction for every arm, hard-clamp feasibility, aggregate truth/objective/timing/certification counts, and exhaustive enumeration of the 12 size-16 tasks. **4,707 independent checks PASS**, with no missing evaluated cases.

The preregistered wrong-syndrome *negative control* was incorrectly implemented in the primary scored receipt as only a score diagnostic on existing recurrent assignments, rather than as a full rerun. Therefore this negative-control requirement is **NOT SATISFIED by frozen scoring**. A separately labeled post-score exploratory diagnostic (`postscore_diagnostic.py`) reran energy search with flipped syndromes. It changed 36/36 assignments and reduced exact truth recovery from 9/36 to 0/36. This is **not** prospective evidence and does not repair the frozen control gap.

## Scientific decision / next useful experiment

**DEVELOPMENT NO-GO:** The primary frozen 2× total-cost threshold failed; at the largest size, two of three seed-size groups had zero warm-search certificates; the trained recurrent control did not converge; and the preregistered negative control was incomplete. No accepted science or integration.

A meaningful next study would use a capacity-matched, demonstrably converged trained recurrent comparator and a true MIP-start-capable *industrial solver* (or another independently verified exact backend) with explicit incumbent APIs rather than a homegrown Python branch-and-bound. Predefine budgets, accuracy/certificates, real-seed splits and the negative control before scoring. No reason to retune ENERGY-08 post hoc or activate this on Yggdrasil.

**Deployment:** NONE. **User action:** NONE for this completed local development gate.

## Reproduction

From this directory with NumPy, SciPy and PyTorch installed:

```sh
python experiment.py --smoke --output fresh-smoke.json
python experiment.py --output fresh-scored.json
python audit.py
python postscore_diagnostic.py
```

`audit.py` checks the **original scored.json**, not a new file, by design; rerun receipt audits against a copied, separately frozen scoring package if necessary. CPU timings vary by host. Frozen primary result is immutable; do not overwrite `scored.json` to requalify the historical result.