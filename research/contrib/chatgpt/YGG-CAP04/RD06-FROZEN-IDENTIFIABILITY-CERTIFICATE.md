# CAP04-RD06 — retrospective finite-state identifiability certificate

**Status:** preregistered **source-only, read-only mathematical audit** of the
two already consumed synthetic CAP04-RD04 fixtures. Not a fresh scientific
test, a new source, or a mechanism to be integrated.
**Parent SHA pinned before implementation:** `ee6164dc0722b0583c11f227fbd4b19884cb2c59`.
**Owner:** CAP04 independent research contributor on existing draft PR #1324,
not an integration coordinator. The sole central coordinator is the
Unified Causal Intelligence Amalgam Work chat.

## Primary question

Do exactly the bounded public variables that the CAP04 direct terminal
head can condition upon—`(3-bit current public state, current 2-bit
action, currently observed s2, immediately previous witnessed 2-bit action)`—
form a stationary sufficient input for familiar law A and unfamiliar law B?
If the same identical public/history key has both outcome labels in
the *previously witnessed* A and B public records, there is no single
**static deterministic or probabilistic key→reward map** that predicts all
such records perfectly.

This is not a theorem about arbitrary recurrent histories, causal
discovery, online adaptation, or architectures that can infer an
unobserved regime from longer past interactions. It is a
**representational lower bound for the fixed current+one-lag key class**
and a retrospective diagnostic rather than a prospective performance
claim. The stage-two `s2` is public before reward prediction by contract.

## Frozen input, boundaries, calculations

Only original preregistered synthetic RD04 source identities:
`cap04-rd04-source-a` with original `source_sha256=
a3a06178c1bc0955bb7e5258284aaaa90691c556cd832310d146373f703339be`,
and `cap04-rd04-source-b` with `source_sha256=
4ed6c8044fa88c4667c3b6194c93f74480ed18462e9720b0e1dba9a718a7cdf3`.
Regenerate solely from the already frozen
`rd04_engineering.source` equations. Reject any source/hash variation.
No RD04 experiment is rerun as a new scientific cohort.

Analyze the **first 192** actually witnessed episodes, old A [0,64) and
new B [64,192), then separately all **256** episodes including old A
return [192,256). For each set compute exact current+one-lag key counts
`n0(k),n1(k)`, across both laws. Define independently fitted optimal
**static** empirical Bernoulli forecast
`p*(k)=n1(k)/(n0(k)+n1(k))` and prove/check its
sample weighted Brier minimizer
`L_min=sum_k[n0(k)*n1(k)/(n0(k)+n1(k))]/N`.
All probability values and losses derive solely from source-labeled
historical rows, *post hoc*. They may not train any learner or be passed
to a source-facing model.

Also calculate the **static deterministic lookup minimum error count**
`sum_k min(n0(k),n1(k))` (ties are counted as minimum either way);
count conflicting joint keys and number of rows in those keys. Compare to
a separate **oracle phase-tagged static lookup** on A/B (and A-return)
which can achieve zero empirical loss on this deterministic synthetic
source **only if** there are no internal contradictory cells within
each known private phase. If such within-phase contradictions occur,
report the oracle's actual nonzero minimum loss rather than assume zero.
That phase tag is a source-only **unavailable oracle**, not a valid
learner feature or legitimate control in an online science comparison.

For each of the **16 familiar A-prefix probe queries used in RD04**,
evaluate whether identical historical keys occur with opposite reward
labels later in the B segment; count probe keys (and probe rows)
subject to this conflicting-identity challenge. A failure here means
active-old-A and active-B simultaneously on identical public keys cannot
both be perfect under a static one-lag function, NOT that archived
knowledge was destroyed.

**Mandatory controls:** independently recompute all counts from public
observations in tests rather than trusting the audit report; verify that
the phase-blind optimum is exactly achieved by each key's empirical
mean, and that fixed p0=.5 is never better on the full source than
the retrospective optimum. Verify at least one pair of conflicting
public keys directly by two original public witnessed event IDs and
different actual rewards; no fabricated counterfactual. Verify
source order, original immutable SHA, no access to private production
or original pilot/dev source, and tampered receipt rejection.

**No speculation from outcome:** The result can be positive
(`STATIC_KEY_INSUFFICIENT`) or negative
(`NO_STATIC_KEY_CONFLICT_FOUND`) based on actual source counts.
Do not make a threshold or source revision after looking at the
outcome. If source or proofs do not reproduce, output
`RD06_DIAGNOSTIC_INVALID`.

## Research disposition and engineering gate

This is a *necessary-condition test* for static memory of those
particular variables. A nonzero mathematical lower bound does NOT
prove Yggdrasil has no capacity for cumulative reasoning; it says the
chosen fixed feature list cannot represent both temporally distinct
laws as one stationary mapping, even with unlimited samples from the
same keys. Evidence should separate:
- source exposure/sparsity (RD05);
- incompatible labels in identical one-lag public contexts (RD06);
- owner checkpoint/parameters retention (UNVERIFIED);
- active adaptation and return skill after a source switch (RD04 NO_GO).

Implementation only extends CAP04 contributor docs, standalone
source-only auditing/tests and existing scoped CI. Existing
`PredictiveStateSplit`, six matched controls and frozen protocols
remain unchanged. Before claiming full **engineering PASS**, require
exact-source complete Linux+Windows regression, code atlas and numerical
report parity; preserve negative outcomes.
**SCIENTIFIC_PASS stays false, canonical model untouched.**
No merging, another controller/scheduler, protected first-use under
issue #426, new owner, first-use trial, or PR duplication.

Overlap check: LR-92AR PR #1330 already studies phase-blind
archived/recent banks, and NCI-05 PR #1333 studies narrow factor-role
identifiability. RD06 is an analytical certificate of CAP04 exact
public-state sufficiency on already consumed fixtures, not a competing
variant of either research model.
