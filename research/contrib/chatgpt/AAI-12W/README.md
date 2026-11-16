# AAI-12W — hidden-state delayed causal role discovery

**Final outcome:** `DEV_NO_GO_NO_SCIENCE` on one frozen mechanical development screen. **Six of seven preregistered gates passed, including perfect in-grammar transfer; the whole-model cost gate failed.** No native source, accepted weights, main, scientific first-use cohort, research owner/runner/controller, or deployment was changed.

## Why this differs from AAI-12V

AAI-12V tried to distinguish information-gain exploration from standard predictive-entropy exploration, but its fixed known/unknown observation-noise model makes these objectives algebraically equivalent. For a candidate action `a` and three latent hypotheses `H`, the information gain is

`I(H;Y|a) = H(Y|a) - sum_h P(h) H(Y|h,a)`.

The two known-table hypotheses each have a Bernoulli .05/.95 observation likelihood, so both have constant binary entropy `h(.05)` for **every** action. The unknown-table hypothesis has entropy `1` for **every** action. Therefore the subtracted term `(P(donor)+P(interference))*h(.05)+P(unknown)` is invariant to the action, and maximizing information gain is mathematically identical to maximizing predictive entropy except tie/numerical variation. This analytical diagnosis motivated a genuinely different test rather than retuning AAI-12V.

AAI-12W asks whether a learner can infer an unknown **causal input-role assignment**, hidden one-bit dynamical state and state-update relation from actual action consequences, then forecast three interventions without observing intermediate outcomes.

## Frozen source and exact custody

- Independent source parent: AAI-12P PR #1074, SHA `abd374e7dc433981df991e103d8ebdff0b5eb093` (separate from failed AAI-12Q/R/S/T/U/V).
- **Preregistration committed before code or outcomes:** `5a929c491142d7b06ec4fa68278af0edb217c334`.
- **All implementation and ten tests committed before the first measured source screen:** `eb10398f232591e6c9778f303b3a5974e3a9a53c`.
- Checked exact Git blobs against the local, already tested byte contents:
  - `world.py` — `9c1c6096023255bec1a54a4f70cbdbdb192a61bc`
  - `learner.py` — `e8b0c9c2bb5349377993454179084840222f3e49`
  - `dev.py` — `6a29187b8c46ec43171e9dd2119a9a82319400aa`
  - `test_dev.py` — `c3582526c5bc69132d9dc922ca4f13be34017833`
- No source/model/test edits after measured outcomes. Full SHA256 identities and execution receipts are in `provenance.json`.

## Protocol and baselines

A mechanical environment contains eight binary inputs, a one-bit latent state `z`, and observed output `y`:

`z_(t+1) = z_t XOR f(x_a,t,x_b,t,x_c,t)`

`y_t = z_t XOR x_k,t`.

The source chooses unknown input roles `a,b,c,k` and unknown ternary truth table `f`; **neither roles, latent state nor table is exposed to any learner**. Public training supplies 48 separate genuine one-bit-do transitions, each as `(x_t,y_t,action,x_(t+1),y_(t+1))`. Heldout evaluation provides `(x0,y0,three actions)`, withholds `y1,y2`, and scores the predicted final `y3`. All evaluation predecessor states are disjoint from training predecessors.

The tokenless candidate learns a three-input truth table and four input roles solely from public recurrence residuals. Four fully fitted conventional comparators receive exactly the same 48 real transitions: fully fitted depth-7 ID3, 200-epoch degree-2 logistic regression, kNN-5, and an unknown-role six-operation pair-grammar causal model. A no-memory persistence arm provides a negative control. Each arm is fitted and cold-restored before heldout use.

The frozen design has two mechanical fixtures, 12 novel ternary-function worlds, four familiar binary-function worlds, and four out-of-family four-input-function worlds. **Every arm is tested on 1,536 novel, 512 familiar, and 512 negative three-action forecasts**: 2,560 heldout predictions and 40 worlds/fixtures per arm. First-use scientific cohorts: **zero**.

The candidate grammar **contains the source novel function family by construction**. Therefore even perfect generalization within it is not evidence of primitive invention outside that grammar, naturalistic causal discovery, persistent cross-world learning, or general intelligence.

## Frozen development result

| Learner | Novel 1,536 | Familiar 512 | Out-of-family 512 |
|---|---:|---:|---:|
| **Ternary causal roles** | **1.000000** | **1.000000** | 0.601563 |
| Strongest conventional, fixed pair grammar | 0.691406 | **1.000000** | **0.626953** |
| Fully fitted depth-7 ID3 | 0.527344 | 0.501953 | 0.500000 |
| Degree-2 full-batch logistic (200 epochs) | 0.496094 | 0.509766 | 0.496094 |
| kNN-5 | 0.487630 | 0.484375 | 0.468750 |
| No-memory persistence | 0.505208 | 0.505859 | 0.511719 |

**Novel absolute gain vs strongest fitted comparator:** **+0.308594**. Every one of 12 novel worlds achieved at least 80% across the two fixtures; the candidate reached 100%. Familiar and negative non-regression requirements both passed.

However, the frozen **whole-model fit + cold restore + prediction elapsed-time ratio** permitted at most **12×** the fastest conventional control. The candidate took **0.635093 s** across the source screen versus **0.043400 s** for the fitted ID3 control, a ratio **14.6335× — FAIL**. An independent identical-source repeat gave **15.5634× — FAIL**. These are local Python source-model timings and are **not** native Yggdrasil all-workflow timing or cross-platform qualification.

**Six gates PASS, one FAIL; all seven were mandatory. Classification: `DEV_NO_GO_NO_SCIENCE`.** Do not change this frozen candidate or relax the ratio after the result.

Exact repeated action/forecast trace SHA256: `37c9dddef17d2cefaab79be67af1d4cf0d6491da74e25eef24f4a27b0b875764`. Original public training digest SHA256: `549f63f4e08f499c0be55130df4f31184301eaae7d4e0d895d7011e98ce961ae`. Both source-only runs had identical predictions, metrics, frozen gates, digest and classification. Pre- and post-outcome **10/10 local tests PASS**, with 240 valid cold restorations.

## Reproduce and interpret safely

From `research/contrib/chatgpt/AAI-12W` (stdlib-only Python 3.13):

```sh
python -m unittest -v test_dev.py
python dev.py --source-dev
python dev.py --primary  # MUST fail
```

Exact measured source: local isolated Linux x86_64 / CPython 3.13.5, **not an official project owner/runner**. See `result.json` and `provenance.json` for full metric/qualification distinctions.

**Engineering:** local focused tests PASS, source Git blobs PASS, cold restore PASS; official exact-final Ubuntu and Windows native regression **NOT RUN**, generated G29 code-atlas not updated. Automatically failing repository jobs, if any, are independent engineering evidence, not causal-learning validation.

**Scientific:** unusually strong **source-only development signal within a matching known grammar**; the prespecified efficiency bound failed, and no independent sealed scientific first-use, multi-environment causal transfer or cross-world retention was qualified. Preserve this result and all out-of-family negatives.

**Deployment:** none; do not merge or promote this source candidate.

A prospective **separately preregistered** experiment could test a semantically equivalent, lower-compute structural learner against independent newly born worlds, all matched controls, cold retention, and an exact-source/native qualification. The failed AAI-12W evidence must not be rewritten as a passing result.
