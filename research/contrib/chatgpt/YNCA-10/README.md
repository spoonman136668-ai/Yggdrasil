# YNCA-10 — cross-world learning of an unfamiliar causal operator

**Outcome: DEVELOPMENT_SIGNAL, not SCIENTIFIC_SUPERIORITY or accepted native Yggdrasil training.**

## Purpose

YNCA-09 learned which causal edges were present in a world, but it was told in advance that every response obeyed a specific XOR algebra. YNCA-10 instead asks whether a small tokenless learner can **acquire a reusable causal operator from repeated action–consequence experience** when that operator is not in its standard predefined library, then transfer it to unfamiliar input wirings.

## Exact experimental task

An unknown three-input Boolean function is sampled from 210 truth tables **outside** a fixed library of 46 familiar AND/OR/XOR/MAJ/MUX-like tables (including input role permutations and complement variants). There are 256 total possible Boolean truth tables, so the true rule is still **inside a finite exhaustive hypothesis space**.

In each training world the three observed binary input channels are secretly permuted. The learner receives five randomly selected input interventions and their noisy outcome bits (10% flip rate). Across 48 training worlds, it infers a shared unknown operator by marginalizing over hidden permutations.

The **single targeted correction to Pass A** stores the top eight weighted operator tables from the trained posterior in a serialized compact memory. In each new test world it sees only three noisy interventions and must predict the true outcome for all **five unobserved input assignments**. The true operator and input permutation are only used by the evaluator, never supplied to the fitted policies.

## Controls

All test-time approaches receive the same three intervention/outcome pairs. Training-aware controls also receive the exact same 48-world training history.

- No-transfer exact posterior: uniform 256-table prior independently fitted in each test world
- Fully trained per-action frequency memory with Laplace smoothing
- Fixed 46-known-operator Bayesian library (misspecified by construction, negative control)
- **Fully trained exact hierarchical 256-table Bayesian posterior**, marginalizing world permutations
- **Generator-aware exact 210-table Bayesian posterior**, correctly restricting the prior to eligible novel operators
- Privileged true-table oracle diagnostic (not eligible to establish superiority)

## Pass A — exploratory only

64 test worlds; this result was examined **before the GitHub preregistration**, and must not be treated as confirmatory.

| Method | Unobserved-action Brier ↓ |
| --- | ---: |
| Untrained exact per-world Bayesian | 0.25000000 |
| Fully trained frequency | 0.09421627 |
| Learned eight-entry memory | **0.05932920** |
| Exact 256-table and generator Bayes | **0.05932920** |

Nine source-focused tests passed locally. Pass A suggested that cumulative operator memory deserved one frozen disjoint test.

## Pass B — frozen before first evaluation

A new unknown operator (different operator seed), 48 fresh training worlds, 128 new test worlds. Source and all thresholds were Git-committed before any B outcomes were inspected.

| Method | Unobserved-action Brier ↓ | Correct held-out outputs ↑ |
| --- | ---: | ---: |
| No cross-world training | 0.25000000 | 48.44% |
| Fully trained frequency | 0.09684615 | 87.66% |
| Fixed known-library Bayes | 0.26082357 | 55.00% |
| **Learned eight-entry operator memory** | **0.06821703** | **88.91%** |
| Full exact 256-table Bayes | **0.06821703** | **88.91%** |
| Generator-aware exact 210-table Bayes | **0.06821703** | **88.91%** |
| Privileged true-table oracle | 0.06821703 | 88.91% |

The compact memory reduced prediction Brier **29.56%** versus the fully trained frequency control, and **72.71%** versus no cumulative transfer. Its predictive performance **tied** both exact Bayesian controls and the privileged known-function diagnostic. This confirms finite operator reuse and compression, **not a superior scientific inference principle**.

Eight retained tables replace 256 test-time table hypotheses (**32x fewer**), and a simple modeled likelihood-factor calculation (training included) estimates **2.476x fewer** factors versus full-256 Bayes over these 128 test worlds. These are **analytic operation counts**, not measured whole-process runtime/energy gains.

## Engineering and first-use custody

- Accepted `main` fork: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; original unchanged.
- Initial prereg: `1122e64a7810ccc55d1791a2d0299accb92305b2`.
- Experimental source committed before B at `50642f920d28560971449c76aa9ad6327b10f50d`, SHA256 `6b2f04ebe91ceccd47f675d67a3ade649d5fd030384bcad0aeded0b2180ef305`. Focused tests SHA256 `c11d7e6d202bfac4e41850da67e9608ef0680a9331d419f53e982f44d8344387`.
- Prereg source binding before B at `7031ee2fa4931985d72ba61732895216f7312db3`.
- [Original B dual-platform run #44309458330](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44309458330): nine focused source tests PASS each OS; **original B outputs byte-identical**, SHA256 `5644230ed963b19dfeb7588e67bc234169a6fcce5a0fe6d87da320631ad5ec07`, result committed unchanged at `dbb27cb1bf689876eb1ed5feca8679d8b31a9830`.
- **Why that workflow is marked FAILURE:** its separate cold-restoration step compared floating sums for *exact* equality. JSON sorted key order changed floating addition order by about `3.3e-16`, a harness issue after the scored output, not a change to the scientific model.
- [Independent two-process cold-memory run #44309834560](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44309834560) **PASS Linux and Windows**, using the **same frozen source**, matching eight-entry serialized memory SHA256 `76a02dcc6c4cd6eea486a99e8e0ab416483d83462f71e7278c61ca0a7c34eb63`, maximum absolute prediction difference `3.33e-16` under a frozen `1e-12` numerical tolerance. **No new B-world score** was run.
- The original B result is `result_B.json`; preregistration, A exploratory result, provenance and reproduction commands remain in this directory.

```bash
python -B -m unittest discover -s research/contrib/chatgpt/YNCA-10 -p 'test_*.py' -v
python -B research/contrib/chatgpt/YNCA-10/experiment.py --split A
python -B research/contrib/chatgpt/YNCA-10/experiment.py --split B
```

The B command is only a reproduction of **already-consumed development data**; running it again is not independent scientific evidence.

## Research limits and disposition

**This is finite Boolean operator learning.** The operator is *not* in the familiar 46-function library, but the learner's exhaustive 256-function hypothesis space already contains it. The method trains a Bayesian posterior, compresses the best eight possibilities, and reuses them across new input permutations. It does not invent arbitrary operators outside that hypothesis space, learn latent context routing, demonstrate transfer to unrelated physical systems, or survive long interference sequences.

The learner ties the fully specified strongest control. No native Yggdrasil / CKAD weights, accepted ref, owner, controller, scheduler or deployment changed. The next serious research hypothesis should test **composition, variable-arity extension, independent repeated task-family learning, and cold retention through interfering operators**, with a smaller fully trained baseline and whole-process efficiency measured rather than inferred. Do not tune this consumed B cohort.

Full exact SHA, two-OS inherited/G29 engineering regression must be qualified separately. Preserve this positive development finding without treating it as SCIENTIFIC_PASS.
