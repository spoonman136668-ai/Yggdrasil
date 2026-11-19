# YGG-RET05 — learn from the two issued observation-clock forecasts

**Research status:** opt-in source-only engineering candidate. **Scientific
efficacy UNVERIFIED**; no novel source-world training, unknown-family
transfer, valid conventional superiority, promotion or deployment.

Base: [RET04 PR #1300](https://github.com/spoonman136668-ai/Yggdrasil/pull/1300)
at `6b684b7bd3c228333d4efdfd66614124917f0c86`, which passed the
complete exact-source Linux/Windows native+G29 regression.
Source-only engineering hypothesis frozen **before implementation** in
`4c4c685b2272404d8a51930ece29267a45d6ba7f`.

## The actual learning mismatch

RET03/RET04 correctly issue probabilities at the two observation clocks:

1. before the first transition is witnessed, issue `P(s2|public views,x1)`;
2. after publicly witnessing s2 and choosing x2, issue `P(y|views,x1,s2,x2)`.

But RET02's original 17-float readout learns by recomputing a
**full-row forecast after both choices and s2 exist**. Thus its
post-reveal gradient is not necessarily the gradient of the actual
prediction errors RET04 now records. Measuring the correct score
does not automatically train on that score.

## Implemented alternative (opt-in, no new cognitive architecture)

`yggdrasil/native_staged_credit.py` defines `StagedCreditReadout`.
It wraps the **same previously trained Yggdrasil cumulative native
source model and six specialists** through RET04, not a restarted
model or a second controller. The optional new readout captures the
existing 17-number public-only feature **at each issued forecast**
and separately records the two issued archive/live mixture weights.
At final witnessed reward (NEVER before), it computes the exact
derivative of *averaged two-clock Brier* with respect to each of the
**same 17 learned readout weights**:

```
L = ((P_issued(s2)-s2)^2 + (P_issued(y)-y)^2)/2
g_i = sum over j=1,2 [
  (P_issued,j - actual_j)
  * (P_archive,j - P_live,j)
  * w_archive,j * (1 - w_archive,j)
  * feature_at_issue,j,i
]
weight_next_i = clip(weight_old_i -
  LR * (g_i + (DECAY * weight_old_i if i>0 else 0)),
  -MAX_WEIGHT, MAX_WEIGHT)
```

LR, DECAY, numeric width and bounds are **unchanged RET02 values**.
There is NO optimizer search, no original development seed tuning
and no private source phase/evaluator/terminal label in an earlier feature.

The underlying original RET03 `complete` still admits **one genuine
public-shaped source witness exactly once** and continues original
native causal basis and all retained JEPA specialists. The temporary
RET02 post-row 17-weight update is replaced **only in the optional
RET05 readout** by the pre-issued two-stage gradient; no other native
weights, prior ledger, source identities or historical trained
checkpoint are changed. RET01-RET04 remain executable exactly as
before. RET05 has its **own checkpoint schema** because the original
RET02 replay contract assumes the older gradient update; do **not**
incorrectly restore this alternative with RET02/03/04 deserializers.

The new outer checkpoint embeds the original RET03 state, original
RET04 issued-probability receipts, and a separate staged gradient
record with before/after readout weights, intermediate original-update
SHA and final staged-update SHA. Exact cold restoration independently
replays every completed source witness and any partially pending
stage through RET05 itself and verifies complete checkpoint bytes,
gradient, source identities and receipts. Source hashes detect
inconsistent stored state, but they **do not independently authenticate
an external source owner or prevent a fully reconstructed alternative
source history**, so every record marks `source_owner_authenticated=false`.

## Mechanical tests vs genuine science

Seven regression tests with **constructed public-shaped fixtures**
verify the exact gradient calculated from probabilities returned before
their outcomes, comparison against **unchanged original native causal
reader state** with the RET04 control, full last-two-event history,
strict out-of-order/duplicate failure, cold restoration at each stage,
rehashed altered weight/gradient/receipt failure and bounding.
Original old trained source prefixes and six specialists must survive.

This is NOT a positive scientific comparison. An actual gain over
a fully fitted same-information conventional model, unknown causal
action identity transfer, cold usable prior-context memory, or
efficiency remains wholly unmeasured. In particular the original
native 1024 episode capacity still limits how many new RET05 events
can be admitted; [CAP01 #1303](https://github.com/spoonman136668-ai/Yggdrasil/pull/1303)
is a separate bounded extension with scientific uncertainty, **not**
silently integrated here.

A true prequential learned-credit experiment requires a **new
independently source-owner-permitted original unfamiliar causal
family**, signed disjoint TRAIN/VALID/HELD/TRANSFER cohorts,
actual actor/action-consequence journal and preregistered strongest
fully trained Beta/Bayesian/recurrent/symbolic controls with matched
actions, evidence, compute; stage chronology, old-context cold
retention/interference, negative history pairings and whole-process
cost before any first use. The original owner still blocks new
protected actions in [issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426).

**ENGINEERING only / DRAFT / NO MERGE / NO ACCEPTED MAIN / NO FORGE
CONTROLLER / NO SCHEDULE / NO DEPLOYMENT / SCIENTIFIC_PASS=false.**
