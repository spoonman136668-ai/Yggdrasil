# DG1-HC09 — bounded context memory plus nonlinear executable causality

**Preregistered before code/outcome:** `74e8e317c851f0004809dc77e5ea5921225c3474`.
**Source parent:** Yggdrasil external draft HC08 at
`aa8927d462cab69ba6b4a7fd704ec66d2a62af34`.

## Purpose

HC08 demonstrated that **physically charged state perturbations** allow
a simple non-token causal learner to identify rules unreachable through
ordinary actions. It did NOT retain reliably after physical laws changed
and made 76 confidently wrong nonlinear predictions.

HC09 tests two independent and potentially separable hypotheses:
(1) Does retaining two sets of causal hypotheses permit recovery when a
previously experienced environment returns?
(2) Can a bounded executable-library expansion learn nonlinear majority
interactions while preserving the previous charged-intervention capability?

The proposed model is still a **source-only conventional binary rule
system** rather than an accepted Yggdrasil neural substrate or proof of
novel intelligence.

## Architecture and limits

Each physical mechanism action begins with 40 alternative Boolean
programs: 32 affine parity-over-any-subset-plus-sign rules and eight
majority-of-any-three-visible-bits-plus-sign rules. Two version-space
banks provide a fixed maximum of **320 logical rule mask bits** for
four public actions, plus bounded routing/counters. Programs are
eliminated only by actual public before/selected-action/after physical
observations. Contradiction can reselect a compatible older bank;
when both banks fail, the model **abstains rather than overwriting memory**.

A real exogenous bit flip costs one action and changes the public state
but never provides a causal-model training label. The actor chooses an
informative causal action first, else a permitted charged bit flip.
There is no free physics oracle, no hidden regime indicator, no arbitrary
state reset and no gradient training.

## Frozen developer challenges

Four cohorts over distinct synthetic worlds and source seeds:

- **Eight affine worlds 71001–71008**, 48 charged steps each:
  ≥384/512 correct and zero wrong-confident total.
- **Eight nonlinear majority worlds 71009–71016**, 48 charged steps:
  ≥256/512 correct, zero wrong, and ≥+64/512 over smaller-capacity HC08
  affine baseline. This diagnoses a feature-library effect, not
  equal-capacity scientific superiority.
- **Eight A→B→A worlds 71017–71024**, 16 A + 12 B + 4 return-A =
  32 **charged physical steps**, max six forced flips, without
  environment-change labels. For a narrow developer retention signal:
  ≥128/512 correct, zero confidently wrong, and ≥+64/512 correct over
  the **equal-capacity two-bank no-reactivation** ablation.
- **Four out-of-grammar nonlinear cubic worlds 71025–71028**:
  count every confident error. Even zero on this small cohort would not
  prove safety.

Each stationary world allows exactly 48 steps and max eight physical
flips, across each controller's own uninterrupted physical trajectory,
from the same initial state. The true physics changes with the clock
step, not with model-selected probes. No learner sees any phase label.

After the final action, the **evaluator alone** audits all 16 public
states × four mechanism actions, counting exact correct, confidently
wrong and abstained predictions and unseen contexts. Those audit
answers do not change any model.

Six fixed comparisons: two-bank candidate, **separately implemented**
conventional two-context symbolic rule learner with identical 320-bit
prior/action rights, equal-capacity no-reactivation, 160-bit single-bank
ablation, 128-bit historical HC08 affine control, and 320-bit
round-robin perturb policy. Only like-capacity controls can support
comparable mechanism claims. Record all world-action ledgers and actual
CPU/heap; equal action counts do **not** prove equal compute.

## Falsification interpretation

A passing developer criterion is **not SCIENTIFIC_PASS**. All worlds
remain human-specified four-bit synthetic systems with preselected rule
families. It cannot prove discovering new nonlinear grammar, real-world
transfer, AGI, or mathematical novelty against conventional context
models. The matched conventional model may tie the candidate.

Existing HC03–HC08 evidence, Yggdrasil native runtime, the independently
maintained weight-programming program, and FORGE owner loops remain
untouched. No accepted-ref mutation, merge, scientific first-use, paid
model API, new controller or scheduled task.

To reproduce on the checked-out source:

```sh
python -m unittest discover -s research/contrib/chatgpt/dg1-hc09-20261113 -p "test_*.py" -v
python research/contrib/chatgpt/dg1-hc09-20261113/eval_dev.py
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build_code_atlas.py --check-if-present
```

Qualify final exact SHA on Ubuntu and Windows, with regenerated G29
source atlas and frozen negative/dev artifacts before any independent
acceptance discussion.
