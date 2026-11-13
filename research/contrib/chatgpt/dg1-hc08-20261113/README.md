# DG1-HC08 — Charged controllability for native causal-program learning

**Exact parent:** HC07 experimental head `d9873d19717d17e12683e81c9c4016a7c8438b61`.
**Preregistered before implementation and first result:** `63f5d0feb44ddb95a268c13a856167a578011282`.

## Question

HC07 exposed an observability dead end: in the known physical states of
seeds 51001, 51002 and 51007, **none** of the available mechanism actions
changes the public world. A learner cannot identify other state-dependent
laws from indefinitely repeating those same action consequences.

Can a non-token causal learner resolve that bottleneck by actually
intervening on the world, rather than by increasing training epochs,
sampling synthetic observations, or arbitrarily resetting to states it
never physically visited?

## The physically charged new interface

The only new primitive is an exogenous bit flip:
`do(flip public bit j)`. It is a real source-world physical operation,
charges **one action**, and changes the observed state deterministically
to `state ^ (1<<j)`. It does **not** evaluate the hidden causal mechanism
and yields **no causal training update**. A sham actuator costs one action
but changes nothing. Causal actions (0..3) also cost one real action, and
*only* these feed public `before, action, after` labels into the learner.

Stationary worlds allow exactly 48 total actions and at most 8 flips per
arm; A→B→A worlds allow 25 total actions and at most 4 flips. There are
**no free resets, no hidden-world queries, no uncharged probes, no access
to graph labels or environment-change labels**, and no paid model APIs.

## Candidate and conventional controls

The HC07 source-aligned native research cell is **not rewritten**: an
immutable 32-affine-program version space per action, four actions,
**128 logical learned mask bits**. Its source-blind steering policy
selects the causal action of maximum current Gini disagreement; only
if none can yield information does it spend one permitted charged bit
flip toward a next state with maximal aggregate causal-rule disagreement.

An independently written HC07 conventional `BayesianGraphController`
retains exactly the same hypothesis capacity and receives the same
physical actuator/budget; its separately implemented selector uses
Shannon entropy. Both need equal real action cost. **Equal physical
actions is not equal CPU cost**, so execution time and Python allocations
are measured separately.

Additional negative controls use the same HC07 learned masks with:
causal actions only (no actuator), the same steering policy with a
**physically ineffective sham** actuator, and an explicit fixed
round-robin perturb schedule. Any failure to learn or discover the
physical graph is preserved.

## Frozen source-only challenge

- 3 **already-known absorbing worlds**: 51001, 51002, 51007. These are
  **post-hoc mechanistic replays**, not independent confirmatory science.
  The frozen replay signal requires >=16/64 accurate for the intervention
  learner and >1 visited state, with zero confident errors, versus
  <=4/64 and one state for the no-actuator control.
- 8 previously unused **rewired** 61001–61008: zero confident errors,
  >=16 correct/64 **for each seed**, and total gain >=64/512 beyond
  128-bit no-actuator equal-capacity model. Otherwise primary negative.
- 4 fresh **old-ring** 61009–61012: report all outcomes, no threshold
  rescue.
- 4 deliberately **non-affine majority** 61013–61016: count every
  confidently wrong prediction, never rename it safe on abstention.
- 4 new **A→B→A** 61017–61020: phase changes at physical steps 16 and
  24 regardless of whether a causal or forced action occurs, with no
  phase labels to learner. Frozen limited retention signal: >=64/256
  correct on final A, zero confident errors.

After the last actual action, the evaluator *only* audits 16 public
states x4 actions; these answers are never returned to model fitting.
Report per-seed correct/wrong-confident/abstain, unseen contexts,
distinct visited states, charged causal/forced/sham steps, retained
hypothesis support, checkpoint bytes, exact-action ledger SHA256,
wall-clock and process memory.

Reproduce from repository root:

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-hc08-20261113 -p 'test_*.py' -v
python research/contrib/chatgpt/dg1-hc08-20261113/eval_dev.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

Passing source-aligned DEV is **not SCIENTIFIC_PASS**, an AGI claim or a
new mathematically superior method. Novelty here is a physically grounded
capability test of the native substrate, not a claim that Shannon entropy
or version-space causal identification is unconventional in isolation.
No main merge, native/runtime integration, autonomous research owner
modification, scheduled task, protected first-use, or WSP direct
weight-programming changes are authorized by this experiment.
