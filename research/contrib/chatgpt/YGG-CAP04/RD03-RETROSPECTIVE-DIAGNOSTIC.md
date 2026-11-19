# CAP04-RD03 — frozen read-only mechanism diagnosis of RD02 NO_GO

**Scope:** independent research contributor on existing CAP04 draft PR #1324.
**Parent exact SHA:** `5cf78c6181bdde6870885d41825a42f270c38611`.
**Chronology:** publish this analysis contract before adding RD03 instrumentation.
**Classification:** retrospective engineering diagnosis of *already scored* RD02
synthetic A→B→A sources; **NOT** a new experiment, re-scoring as fresh evidence,
new source first-use or a new scientific result. The two 256-row RD02 sources
and all prior failures remain frozen and unchanged.

## Question and competing explanations

The opt-in direct reward readout passed a simple structural construction
(RD01) but failed frozen A→B→A RD02 vs fitted ridge and a misaligned-history
sham. Distinguish with read-only instrumentation:

- **Gating:** `selected_feature("residual")` stays `None` in the B scoring
  interval even though prior actions are available; `LOG_PENALTY=5` and
  `MIN_EVIDENCE=16` are fixed and unmodified.
- **Feature capacity/history:** reward-feature selections occur, but
  `previous_pair` historical readout fails to predict the observed B
  reward independently of pooled current state/action/sensor.
- **Interference/context re-entry:** cumulative counts are retained, but
  the selected feature changes after B and earlier familiar-A query
  probabilities drift, without evidence of lost ledger bytes.
- **Information or strong-control effect:** a fitted conventional predictor
  already captures correlations/history better than the finite selector.

These are **hypotheses to localize failure**, not pre-declared tests for
mechanistic causality. Do not infer proof of any explanation from a single
feature frequency or post-hoc loss comparison.

## Source and diagnostic protocol

Operate on **only** the already frozen `rd02_engineering.source()` identities
`cap04-rd02-source-a` and `cap04-rd02-source-b`, which have known source
SHA256 hashes `1b859f00f466d9d20b20f078cc47a4ddb0baaa91ea54895df9b22017be06ed77`
and `780e046fbcbec0f22dc9201eabbafafbe8777305a8bd8a135a0122c1e39c8ec0`
respectively. No other world or seed accepted.

At each t=0..255, **before observing the terminal reward** and after reading
the actual current public s2, for exactly the existing RD01
`PredictiveStateSplit(reward_mode="direct")` and its existing
`sham=True` negative control:

1. Record each model's actual terminal `selected_feature`, the four
   `_evidence["residual"]` cumulative log-likelihood increments, selected
   feature eligibility, and number of prior qualified observations. The
   diagnostics must not modify the learner. `None` counts as no routing.
2. Record **read-only**, source-only Brier of the chosen feature forecast,
   its existing pooled forecast (no history), and a *counterfactual
   readout* forcing existing `previous_pair` on the same pre-observation
   checkpoint, never treating that forced readout as a preregistered
   candidate or science.
3. Ingest the single actually witnessed public consequence identically
   into direct and sham after all readouts; no hidden phase/source flag,
   private source law, future reward or counterfactual new action.
4. Summarize selection counts and prequential terminal Brier over fixed
   **A-acquisition [0,64)**, **B-adaptation [64,96)**,
   **B-scored [96,192)**, **A-return [192,256)**. Report observed differences
   to no-history and forced-history comparisons, and cumulative evidence at
   t=64/96/192/256. **No tuning, new feature, threshold change, or accepted
   model write** is allowed.

## Source integrity, negative controls, and stopping rule

An auditor reruns the same fixed source and recomputes the diagnostic; changes
to source identity, selected-feature counts, cumulative-evidence values,
terminal Brier, or input provenance must be rejected. Check that the chosen
forecast reproduces the already-published RD02 direct terminal Brier
**0.1464878998506287** for source A and **0.19896147453966154**
for source B over B-scored [96,192) to tolerance <=1e-12, with
the originally named source SHA and no changes to the original RD02
`status=RD02_ENGINEERING_NO_GO` or its stored failed clauses.

Compare against already-published matched-control results only as historical
context; do not re-label retrospective gating as fresh DEV gain.
Pin exactly the present source and both old protocol blobs:
original CAP04 scientific protocol
`1d79e222685ea1a6889bfc49e5bf405a9aed9580`,
RD02 engineering protocol
`aac12e09ff4ea6729693c1fac41d8aa0dfb82a4f`.

**Engineering success:** source/score replay, mutation-free instrumentation,
negative/tamper tests, cross-platform numerical parity and complete
Linux+Windows source-exact regression. **Scientific success is not assessed.**
If an invariant fails, report DIAGNOSTIC_INVALID instead of repairing it
using consumed examples. Preserve independent source/no-history and
forced-feature metrics regardless of whether they appear useful.

## Native seam and owner boundary

The method to inspect is the existing
`yggdrasil.native_predictive_state_split.PredictiveStateSplit.selected_feature()`
with `_evidence`, `_qualified` and read-only `_estimate` on its existing
`_conditioned_state()`. No new learner, controller, router, training owner,
scheduler or accepted checkpoint. Full original Amalgam trained state and
the canonical model remain under the sole Unified Causal Intelligence
Amalgam Work coordinator. No original-source first-use under issue #426;
no protected CAP04 registered DEV/pilot/primary and no PR merge.

The output is a scoped contributor diagnosis in **PR #1324**, with
explicit limits and subsequent prospective experimental recommendations
only. Avoid another model-owner claim.
