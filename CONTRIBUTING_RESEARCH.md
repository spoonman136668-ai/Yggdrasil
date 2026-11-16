# External Research Contributions

Yggdrasil accepts independent research contributions that are run outside the official autonomous research loop.

The purpose of this lane is to increase replication, falsification, ablation, robustness, and disjoint-dataset evidence without giving external experiments authority over accepted research state.

## Core rule

A contribution may produce **evidence**. It does not automatically change accepted state, thresholds, datasets, promotion refs, successor selection, execution authority, or research-loop authority.

Official acceptance remains a separate qualification step.

## What contributors can run

Contributors may use their own workstation, GitHub Actions, university/organization compute, cloud compute, or other reproducible environments.

Useful contribution classes:

1. **Replication** — reproduce a frozen experiment independently.
2. **Disjoint replication** — apply a frozen mechanism to a genuinely new dataset/context.
3. **Falsification** — preregister a test intended to break a current hypothesis.
4. **Ablation** — remove one bounded mechanism to test causality.
5. **Control** — random, sham/no-op, equal-budget, fixed-heuristic, or other frozen control.
6. **Robustness** — frozen seed/order/runtime/environment variations.
7. **Successor proposal** — propose a new preregistered experiment without claiming accepted evidence until it is run and reviewed.

## Evidence classes

A submission is reviewed as one of:

- `REPLICATION_SUPPORTED`
- `REPLICATION_NEGATIVE`
- `SCIENTIFIC_SUPPORTED`
- `SCIENTIFIC_NEGATIVE`
- `MIXED`
- `INVALID`
- `UNPREREGISTERED`

Negative results are first-class evidence.

Exploratory work is welcome, but if the primary result was observed before the hypothesis, thresholds, split, budget, and classification rule were frozen, it must be marked `UNPREREGISTERED` and cannot be promoted as confirmatory evidence.

## Required workflow

### 1. Freeze a preregistration before the primary run

Create:

`research/contrib/<contributor>/<experiment-id>/prereg.json`

Use the template in `research/contrib/experiment-template.json`.

Commit this file **before** producing or inspecting the primary outcome.

For confirmatory evidence, the preregistration commit must precede the primary result artifact/logs.

### 2. Pin exact identity

Record:

- project
- exact parent commit SHA
- experiment ID
- dataset/context identities and hashes
- code/config identity
- permitted changed paths
- seeds/splits/order
- data and compute budgets
- capacity
- evaluator/scoring rule
- success/mixed/negative/invalid classification rules
- expected deterministic/stochastic behavior

Do not silently update the parent or inputs after running.

### 3. Run outside the official loop

Use any reproducible environment you control.

Do not use production credentials, production authority, accepted-ref mutation, hidden evaluator labels, or private held-out answers.

Do not increase capacity, data, compute, model calls, tools, or permissions unless that variable was explicitly preregistered.

### 4. Preserve provenance

Add:

- `result.json` — primary metrics and classification
- `provenance.json` — source SHA, tree/config/runtime/dependency identities, hardware/OS where relevant
- `README.md` — plain-language question, method, result, limitations, and exact reproduction command
- optional logs/artifacts needed to reproduce the claim

If the experiment is stochastic, include all preregistered seeds and aggregate statistics.

### 5. Submit a pull request

Use the Research Contribution PR template.

The PR must identify the preregistration commit and the later result commit separately.

Review must be able to establish that the result did not exist before the preregistration boundary.

## Scientific constraints

Unless the preregistration explicitly makes one of these the independent variable:

- no post-result threshold changes
- no post-result split changes
- no hidden capacity growth
- no extra model calls
- no evaluator/held-out leakage
- no post-result policy selection
- no silent compute/data budget increase
- no accepted-ref mutation
- no production authority
- no queue/scheduler authority
- no changing a negative into an infrastructure failure merely because the result was unfavorable

Infrastructure defects and scientific outcomes must be classified separately.

## Bounded post-result repair: preserve the failure, keep improving

A failed frozen primary test is **not a stop-work instruction**. It is an
immutable measurement of that candidate. The research line may continue through
a small, documented, budgeted repair cycle, without converting the original
negative into a retrospective positive.

### Two separate outcomes

- **Original frozen outcome (immutable):** preserve the source SHA, seeds,
  actions, scores, confident errors, matched controls, and preregistered
  PASS/FAIL/INVALID classification. Keep an actual scientific negative even
  when a code edit subsequently improves performance.
- **Repaired candidate (new identity):** give each edit a new commit/SHA, state
  exactly which defect or mechanism it addresses, and remeasure engineering
  regressions and development diagnostics. The prior result is never
  overwritten, silently reclassified, or presented as fresh evidence.
- **Independent confirmation (separate later decision):** evaluate a frozen
  repaired candidate on an untouched, disjoint confirmation cohort selected
  and committed before inspecting that cohort. Only independent owner-approved
  first-use and appropriate strong controls can support scientific acceptance.

### Authorize and bound repairs before use

A preregistration SHOULD contain a `repair_envelope` before the first primary
measurement. If it does not, preserve the original result and preregister a
successor **before** any *new* independent confirmation; subsequent changes
to already exposed development data are exploratory, not confirmatory.

A suggested conservative initial envelope for one candidate family is:

- Up to **3 distinct algorithmic repair commits** after the original
  development result, and up to **3 reruns of the exposed development
  cohort** as diagnostics. Document any deterministic engineering rerun
  required by exact-SHA, CI or platform qualification separately; it must
  not be represented as a fresh scientific sample.
- Target **one identified failure mechanism per patch**. State the before
  and after metrics for both confident-error rate **and** useful correct
  coverage, plus the strongest equal-information control. A repair that
  achieves zero errors only by abstaining on every case is not a performance
  improvement.
- Preserve the frozen source/evaluator, intervention and compute budget,
  protected data and seed split, and original pass thresholds. Source identity,
  seeds, scoring rule or scientific acceptance threshold may NOT be revised
  after viewing outcomes to manufacture a pass.
- Do not add external model calls, paid services, production data, new runner
  privileges, control-plane authority or scientific first-use. If the proposed
  patch needs any new data, tool, budget, architecture family, or evaluator
  capability, preregister an explicitly bounded successor.
- Reserve an untouched **confirmation split** before development tuning and
  never inspect its labels to select, adjust or terminate candidate repairs.
  Each independent confirmation uses its own documented first-use owner
  authorization; a submitted PR or passing CI does not grant that authority.

The numbers above are a **suggested default**, not permission to override a
stricter existing research contract or to consume protected original sources.
A project can freeze a smaller or otherwise explicitly justified envelope.

### Repair ledger and continuous eligible work

For every repaired candidate, maintain a plain-language and machine-readable
ledger within the repository containing:

1. Failed source/run, exact parent and candidate SHA/tree, failing metrics,
   counts of correct/confident wrong/abstain, and why the failure is
   scientifically meaningful or is only an engineering/scorer defect.
2. The minimum causal hypothesis for the proposed correction, scoped code
   paths, prior repair count, resource budget, affected interfaces, and
   strong-control comparison.
3. Source-identical diagnostics (not fresh scientific evidence), negative
   controls, cold retention, unfamiliar transfer and measured whole-process
   time/cost. Record unsuccessful fixes as carefully as successful ones.
4. Full final regression on the repaired exact SHA on all required OS,
   pinned derived artifacts, independent CI/G29 where applicable, and the
   authorized owner of any further scientific first-use or native admission.

Continue independently authorized repair/edit/test/qualification stages
without asking for repeated routine approvals. Stop only when the repair
envelope is exhausted, a safety/authority/source-custody condition fails,
a change requires additional permission, or measured progress no longer
justifies another attempt. Do **not** introduce another controller or
scheduler to automate this process.

### Classifying fixes without falsifying science

- A **proven implementation or scoring defect** may make its affected
  engineering receipt `INVALID`; retain the old faulty output and
  reference the corrected rerun explicitly. Verify that the correction does
  not quietly alter any scientific outcomes, source or thresholds.
- A **genuine model error** remains `SCIENTIFIC_NEGATIVE`/`MIXED` for its
  frozen original cohort, even if an exploratory repair reaches the original
  target. Label that repair `DEVELOPMENT_REPAIR_SUPPORTED` or
  `DEVELOPMENT_REPAIR_NEGATIVE` as appropriate, not `SCIENTIFIC_SUPPORTED`.
- A **new held-out confirmation** can qualify a repaired candidate against
  its own precommitted constraints, strong trained conventional and symbolic
  controls, matched information/actions/resources and independent custody.
  Any resulting admission to an accepted model or research loop remains a
  separately authorized decision.

**Example:** A learner correctly transfers familiar causal relationships
but confidently mispredicts unfamiliar transformations. Keep its original
confident-error count and negative classification. A bounded successor may
test intervention-driven uncertainty gating or evidence-based semantic
repair against its exact symbolic control, measuring both reductions in wrong
confidence and retention of familiar-world correct coverage. The previously
exposed worlds may guide engineering fixes; they cannot be relabeled as
unseen scientific validation.

## Dataset contributions

New datasets/contexts are especially useful.

A dataset contribution must state:

- source/license
- acquisition method
- immutable hash
- size
- preprocessing
- whether the contributor has inspected evaluation labels/outcomes
- contamination risks
- relationship to existing manifests

Do not submit private personal data, credentials, proprietary data without redistribution rights, or data whose provenance cannot be documented.

## Isolation

Contributor results remain external evidence until qualified.

A contributor result must never automatically:

- promote a branch
- mutate accepted state
- change the research North Star
- alter the official evaluator
- authorize more resources
- launch an official successor
- modify the autonomous research controller

## High-value contributions right now

For Yggdrasil, prioritize independent replication, falsification, and genuinely disjoint transfer/generalization tests over small parameter tweaks.

A clean negative on a new context is more valuable than a tuned positive on an already studied one.

## Directory layout

```
research/contrib/
  experiment-template.json
  <contributor>/
    <experiment-id>/
      prereg.json
      README.md
      result.json
      provenance.json
      ...bounded experiment code/artifacts...
```

This lane is designed so outside researchers can contribute meaningful evidence without needing access to the official runners or autonomous loop.
