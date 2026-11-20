# CAP04-RD05 — frozen retrospective exact-context support audit

**Role:** CAP04 independent research contributor on existing PR #1324 only.
**Freeze point:** source/readout audit contract before implementing or computing
this retrospective diagnostic. Prior RD04 research NO_GO and both *already
consumed synthetic engineering sources* remain immutable.
**Parent:** `e6972c8ee237c8098308a23bf640ef4659a854c4`, accepted Yggdrasil main remains separate and untouched.

## Question and falsifiable mechanism explanation

Is CAP04-RD04 failure solely a gate-window selection problem, or does its
unchanged **lifetime, exact-context** Beta estimator lack sufficient support
for the historical cause and mix contradictory A/B environment labels?

Source-level test: in `PredictiveStateSplit.observe`, `_pool` and `_split`
keep all witnessed events; `recent32` affects only `_recent_gains` and
`_winner`, so a routing gate change **cannot by itself age out** old
reward-table counts. Verify that as an implementation invariant from exact
source, and separately quantify overlap/sparsity of the frozen RD04
historical context cells. Do not claim this alone is the cause of every
performance failure or evidence of unobserved hidden-state identity.

## Fixed consumed sources, no further trained model

Operate only on immutable `rd04_engineering.source` identities
`cap04-rd04-source-a` and `cap04-rd04-source-b` (256 public witnessed
episodes each, 512 observations total), the source construction frozen
at `RD04-FROZEN-ROUTER-EXPERIMENT.md`. No new source generation,
intervention, labeling, learner training, original protected first use,
scientific DEV, model-owner invocation or new candidate variant.

Rebuild *only* the publicly witnessed context keys, from public inputs:
`base=(state(views),chosen_action,observed_s2)`, with 8 possible 3-bit
states x 4 actions x 2 sensor values = 64 base contexts; and
`historical=(base,previous_actual_action)`, with 4 previous-action
values, 256 possible historical exact contexts. Previous-action at t=0
is the public initial (0,0), and for t>0 is the actual preceding witness's
chosen intervention. The source's private phase/law is **not a model input**.

Report for each fixed source:
- Exactly 256 rows and source SHA; first 64 familiar A, next 128 unfamiliar
  B, final 64 returned A, with B-scored t96..191.
- Counts of unique base and historical contexts across A [0,64),
  B [64,192), and B-scored [96,192).
- For each B-scored row, exact historical-key support from *preceding*
  all-world witnessed episodes, from preceding B witnessed episodes only,
  and from familiar-A historical witnesses only. Report zero-support
  row counts and the mean supports, without future labels in prequential
  support.
- Independently count exact historical keys witnessed in both familiar A
  and unfamiliar B that have conflicting observed terminal labels; report
  both key count and B-scored rows whose keys conflict across those phases.
  This is a **post-hoc source contrast** and may not be used as a future
  label in any current learner.
- Report number of B-scored cases where correct prior action is not
  identifiable from `base` alone because two preceding actual actions
  occur under the same `base` in the observed B-scored window.
- Report the prior verified RD04 choice `previous_pair=0/96` on each B
  scoring interval *as historical context only*; do not run RD04
  optimization, rescore consumed trial, change threshold or reconstruct
  the private phase inside a learner.
- All counts integer; all means are descriptive fractions, not scientific
  generalization metrics. Auditor must recompute from the original source
  and reject forged source hash, counts and scope flags.

## Engineering checks and stopping rule

A source-only analysis script may import the existing deterministic RD04
source generator. It must not import, create, fit or update
`PredictiveStateSplit`, controls, official native/JEPA checkpoints, or
original source first-use actors. Tests must verify B-scoring windows,
exact original source digests against independent GitHub CI receipts,
prequential prior-only counting, and tampered diagnostic report rejection.
A focused source/test run followed by pinned full Linux/Windows regression
and unchanged G29 atlas provides an engineering receipt. If any source SHA
or chronology differs, classify `RD05_AUDIT_INVALID` rather than silently
fixing the consumed source or rewriting RD04 outcomes.

**Decision:** This gate only localizes mechanism/data limitations in the
already-failed RD04 hypothesis. It is not a new efficacy experiment and
must not add a candidate, promote a checkpoint, or claim scientific PASS.
If source support is sparse or A/B historical contexts conflict, explain
the information/stationarity limitation and suggest *separately frozen*
future structural-factor/latent-state mechanism experiments, coordinated
by the sole Unified Causal Intelligence Amalgam Work chat. If neither
occurs, preserve the null and investigate a different root cause.

**Overlap:** NCI-05 PR #1333 already researches source-blind factor roles
under a supplied XOR grammar. This audit does not rerun its probes, alter
its independent experiments, or establish a rival canonical integration
owner. Original issue #426 first-use remains prohibited.
