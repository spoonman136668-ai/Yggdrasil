# CAP04-RD08 — provenance-checked historical readout interface

**Prospective engineering contract frozen before implementation**.
Independent CAP04 contributor only, on existing draft PR #1324.
Original RD02/RD04 engineering NO_GO; RD07 retrospective results intact.
Canonical Yggdrasil learner/checkpoint has sole coordinator:
Unified Causal Intelligence Amalgam Work chat. This PR does not merge it.

**Parent:** `b3d384d7fa5bd40702dec65d5618150bb0f772da`
**Scope:** existing *research-only* `PredictiveStateSplit` class
in `yggdrasil/native_predictive_state_split.py`; no accepted main,
no new learner, no scientific first-use, no training-owner or scheduler.

## Need

RD07 proved the historical old-A probe's incomplete conditioning
context can misattribute functional readout drift. Its retrospective
script currently accesses private `_winner`, `_estimate`,
`_conditioned_state` and `_events`. A stable **read-only, public,
source-witness-bound** method will make that diagnostic repeatable
without lending an evaluator-only hidden-world phase input.

## Frozen interface and semantics

Add `PredictiveStateSplit.forecast_witnessed_context(identifier,
views, chosen, stage, witnessed_s2=None, *, predecessor_id=None)`.

1. Explicitly **RETROSPECTIVE ONLY**: the queried witness ID must already
   be ingested in this exact learner's append-only witness ledger;
   this method must not be used as a legal prequential forecast of new
   interventions, fresh source first-use, source-phase inference or a
   success score in prospective science.
2. Reject nonexistent/unseen ID, identifier type/shape violation, forged
   original views/current action, invalid stage, unobserved or
   altered terminal s2, future/predecessor spoofing, wrong predecessor
   identifier, and `sham=True` (misaligned-history readouts do not
   have the actual one-event predecessor semantics).
3. The exact witness ledger at index i supplies the indexed original
   `(views,action,s2)` and provenance. At i=0 the original history
   is unavailable; require `predecessor_id=None`. At i>0,
   require `predecessor_id == _events[i-1][0]` (the genuine prior
   witnessed ID). Historical values are *only* prior witness
   actual `(action, post, reward)`, exactly matching
   `_feature_values` with lag 1 when run prequentially.
4. Use only the already-existing `_winner`, `_conditioned_state`,
   `_estimate` and legacy XOR branch **at the current checkpoint**.
   No target-event reward or source-private phase is used in
   predicting that past query. No weights/routers/counters changed
   or temporary changes to `_events` permitted.
5. Stage 1 `transition` must be called without witnessed_s2;
   stage 2 `residual` must receive exactly the originally witnessed
   public s2. Both predictions must be finite floats [0,1].
   Strict no mutation: checkpoint byte identity before/after,
   even for rejected or malformed queries.
6. XOR legacy, direct cumulative and direct recent32 checkpoint
   schema/bytes **remain identical**. No new optional state, new
   feature, global controller or training policy.

## Engineering qualification

- Add negative/focused regression tests for all three existing
  unshammed readout modes: exact equality with independently computed
  old RD07 private readout on *all 16 original A queries* at native
  research-shadow checkpoint ages 64, 192, 256; source A and B,
  observed-only. Verify exact cold checkpoint restore yields the same.
- Change RD07's `frozen_prediction` to call the public method,
  retaining separate source-ledger provenance verification.
- Demand **the identical RD07 canonical full receipt SHA256** on
  previously consumed synthetic source A
  `7fed6a81dc508ab101e7996c5aea984a7558acef89dc8b487807b65a82b3d361`
  and source B
  `040e34fea391b1980937968151e6e75fa3afccde9ac8ee2b0651a3f35909e23e`.
  This locks every old numeric metric and original RD04 NO_GO.
- Pin exact original source A SHA
  `a3a06178c1bc0955bb7e5258284aaaa90691c556cd832310d146373f703339be`,
  B SHA
  `4ed6c8044fa88c4667c3b6194c93f74480ed18462e9720b0e1dba9a718a7cdf3`.
- Run source-first focused tests; source/atlas seal; MANDATORY full
  final Linux + Windows regression and checked-out source tree on
  sealed candidate SHA. Classify `RD08_INTERFACE_ENGINEERING_PASS`
  only if all pass, else `RD08_INTERFACE_ENGINEERING_FAIL`.
  No rerunning or redefining previous consumed cohorts as fresh
  scientific trials.

**Science:** UNVERIFIED. A trustworthy historic query is a measurement
instrument, not demonstrable genuine causal learning or retention.
For new scientific evaluation, freeze complete public queries and
training data prospectively, matched full-fit conventional controls,
cold retention, action budget and independent source first use.
Do not reuse this retrospective interface for prequential scoring.
No changes to Quine #1329 guarded acceptance, LR-92AR #1330
memory banks, NCI-05 #1333 factor discovery, or original #426.
