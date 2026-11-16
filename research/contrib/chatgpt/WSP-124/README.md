# WSP-124 — Active causal-structure repair through intervention microfeedback

**Source-safe research. Original science UNVERIFIED, native admission NONE, draft only.**

## Distinct mechanism / why this test

WSP-123 recovered four previously unknown row/column causal-factor tables from
60 charged interventions and transferred to 256 unfamiliar-identity worlds,
but both direct numeric and equally strong symbolic factors made 25%
confident errors on previously unobserved law changes. Its original 15
anchor observations made the separable and changed worlds indistinguishable.
This **new** preregistered experiment tests whether charged interventions can
reveal a contradiction and repair the causal representation *before* transfer.

The entire frozen protocol is in `prereg.json`, committed BEFORE the source,
learner or evaluator. WSP-123, WSP-112, ST7 and WSP-111 outputs are never
replayed as new first-use. Accepted Yggdrasil main is not modified.

## High-first design

- **16 independent causal domains**, each 8 left × 8 right public typed
  relation identities, 64 possible action–consequence combinations.
- Each domain has unknown three-bit left/right factor values and a previously
  unobserved **nonzero three-bit effect correction inside a thresholded
  rectangle**. The source secretly fixes each threshold in [2,7].
  The **XOR, threshold rectangle, effect alphabet and binary-search strategy
  are supplied inductive biases**; true factors, thresholds and correction
  values are not provided to learners.
- **Exactly 23 paid interventions/domain = 368 source calls**. First 15
  anchor probes identify the separable base; an interior (7,7) probe reveals
  a consequential contradiction; six outcome-directed binary searches
  identify two thresholds; a final negative confirms the boundary.
  All queries are chosen from public view plus *previously paid* feedback.
- Fit scoring uses **41 unqueried pairs/domain, 656 total**. There are
  **1,024 new-entity worlds (65,536 held pairs)**, zero transfer calls.
  Separately, **256 off-family worlds (16,384 held pairs)** add an
  unforeseen parity-based interaction (odd left and odd right) that the
  learner grammar cannot represent. This is explicitly a **negative**.
- Candidate direct-programmed state: 16 signed int32 base factors +
  two threshold slots + one correction slot per domain = 19×16 int32 =
  **1,216 bytes of coefficient slots only**. Excludes source, event ledger,
  snapshots, Python model objects, process memory and evaluator costs.

## Strongest controls and credibility

`controls.StrongSymbolic` is independently implemented from the numerical
learner. It enumerates 6×6×7 possible rectangle parameter combinations and
uses a bipartite XOR constraint graph for each, abstaining unless every
consistent candidate predicts the same outcome. It receives identical
active actions, source receipts, outcomes and budgets as the candidate.
`SYMBOLIC_PASSIVE` uses the same full symbolic solver with 23 seeded random
source actions/domain, a defensible comparison for *intervention value*.
`XOR_ONLY` sees the paid active actions but cannot update the factorization;
`NO_UPDATE` abstains. Full conventional training remains outstanding.

Even a perfect candidate result with a strong-symbolic tie would establish
bounded **causal-model identification/repair from feedback**, **not** a
uniquely numerical capability, open-ended invention or general intelligence.
The development source is inspectable in `source.py`; SHA-256 transcript
receipts detect accidental drift but do not independently authenticate
hidden labels or enforce process isolation. No first-use authorization exists.

The numerical cold snapshot contains all 368 paid observation records and
rebuilds its 16 independent factor banks. Both simple and digest-repaired
coefficient forgeries must fail. No held scores may influence the active
sequence. Off-family mistakes are preserved and must never be tuned away.

## Qualification and stop criteria

Before any original-world first-use, require a truly independent source
custodian, full parameter/threshold witnesses, fully trained conventional
model, equal actions/information/compute, predeclared paired-world confidence
intervals, cross-family tests, full-process cost/RSS/energy, no replay, and
separate owner authorization. The final engineering workflow runs all
WSP117–124 focused suites and the mandatory root regression on an identical
Ubuntu/Windows source archive tree with G29 pin check. No accepted weights,
merge, new controller, scheduled task, private runner, or paid API.

## Engineering-only action-plan and JSON custody correction

The initial development CI exposed (a) a duplicate-query edge case when the
hidden threshold was already uniquely inferred before the third reserved
binary-search action, and (b) a JSON digest mismatch caused by serializing
integer-keyed threshold-bounds maps and then restoring them as string keys.
Neither failure consumed original-source data. Both are fixed without
changing cohort membership, hypothesis family, original first-use, or the
frozen per-domain **23 paid actions**.

For (a), the still-paid third diagnostic action becomes a source-blind,
previously unqueried **negative witness** at left=1/right=7 (or left=7/
right=1), which is guaranteed outside every candidate threshold rectangle.
It is a pre-specified implementation fallback for early identification,
not evidence from held labels; the registered three diagnostic *slots* are
still each charged. The initial preregistration's shorthand "three
binary-search interventions" was overly literal for early convergence;
this procedural clarification is preserved rather than rewriting that
frozen record. For (b), the checksum is calculated over stable string-keyed
bounds both before and after JSON cold restoration.

This is a transparent **development repair before any accepted
science**, not an amendment to an already consumed scientific source.
