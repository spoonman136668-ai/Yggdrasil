# CAP04-RD04 — prospective finite-window history-routing research falsifier

**PR:** #1324, existing independent contributor research branch only.
**Freeze commit precedes implementation and all RD04 synthetic source creation.**
**Parent pinned:** `148df7272d3e1c4a9ea3a713c7ed15bb0b219f2b`. No accepted native Yggdrasil owner,
model continuation, checkpoint, source first-use, merge or scientific admission.
**Status:** SYNTHETIC_ENGINEERING_ONLY, not a registered CAP04 DEV cohort.
Central cumulative model integration belongs solely to Unified Causal
Intelligence Amalgam Work chat; this contributor cannot promote or deploy.

## Research hypothesis and alternatives (frozen before source outcome scoring)

RD03 retrospectively observed that CAP04's direct-reward cumulative evidence
router never selected `previous_pair` over 96 unfamiliar B-scored events
in either fixed RD02 engineering world. A *prospective* test should determine
whether **bounded recent predictive evidence** rather than cumulative
evidence can route actual previous-action relationships under environmental
change, while retaining an earlier, separately learned A relationship.

**One opt-in router** on the *existing* `PredictiveStateSplit` class:
`routing_mode="recent32"` valid only with `reward_mode="direct"`. In each
stage, keep the 32 most recent **prequential** per-feature log-likelihood
gains over the existing pooled Beta model, recorded only after the actually
witnessed target. Use the same four existing fixed features and shrinkage.
After at least 16 qualified examples, select the single feature maximizing
the sum of its last up-to-32 gains if the maximum is **>= 2.5**. Otherwise
keep pooled forecast. Hardcoded window=32, gate=2.5, no extra tuned
features. *No* private phase/state or source identity is provided to the
router. Existing cumulative/XOR/direct behavior and prior v1/v2 checkpoint
bytes must remain unchanged. Opt-in recent32 receives its own explicitly
tagged checkpoint schema and exact cold replay. No new model training owner,
repository branch, controller, scheduler, or canonical checkpoint is allowed.

Alternative explanations and negatives: the recent-window router may select
spurious history, fail to beat direct cumulative, lose to independently fitted
linear/ridge, appear to improve equally on misaligned-history sham,
or cause old-world readout drift. If it fails any frozen condition, preserve
RD04_ENGINEERING_NO_GO: do not lower gate, change source, or selectively
choose successful worlds.

## Fixed NEW synthetic sources, interventions and chronological budget

Exactly two identities, not previously scored: `cap04-rd04-source-a` and
`cap04-rd04-source-b`; **256 public witnessed episodes each, 512 total**.
These are new *engineering* rows, not protected original-world first-use.
Initial public bits `u,v,w` are SHA256 low bits of
`cap04/rd04/<source>/start/<index>`. At each t, current views
`((u,v),(v,w))`. Chosen action is one of
`ARMS=((0,0),(0,1),(1,0),(1,1))` with index equal to low two
bits of SHA256 first byte of `cap04/rd04/<source>/<t>/action`;
`s2` is first SHA256 byte low bit of
`cap04/rd04/<source>/<t>/intermediate`. These are fixed independent
of learner, previous forecasts and private phase. No off-policy labels.
True terminal reward is `y=s2` on familiar stages t=0..63 and
t=192..255. Novel B stage t=64..191 uses **different hidden**
history dependencies: source-a `y=s2 XOR previous_actual_action[0]`,
source-b `y=s2 XOR previous_actual_action[1]`. The actual previous
action begins at (0,0) and is updated each episode; never supplied as a
label or source identity. Public post=`(v XOR action[0],s2,w XOR action[1])`;
next public state is this actual post. Each witnessed ID is SHA256 of
`cap04/rd04/<source>/witness/<t>`. The experiment source and actor are
fixed by this contract, not by outcomes or selected feature counts.

**Identifiability negative:** reject a generated source as INVALID if its
96 B-score steps [96,192) do not include all 16 ordered previous/current
action pairs, or lack at least four identical (current views/action/s2)
cells with two distinct preceding action values. INVALID is never a PASS
and does not authorize replacing an inconvenient fixed source.

## Same-information candidate, ablation and fitted controls

At each t prior to observing s2, score `P(s2)`; after the *actually
observed public s2*, before revealing reward, score `P(y)`.
All learn from exactly the same witnessed (id,views,chosen,s2,y,post)
and **never** see hidden phase/source identity or unchosen outcomes.

Readouts:
1. candidate `PredictiveStateSplit(reward_mode="direct",routing_mode="recent32")`;
2. same new finite-window mode `sham=True`, with old misaligned history;
3. existing `PredictiveStateSplit(reward_mode="direct")` cumulative router;
4. existing `PredictiveStateSplit()` XOR mode as structural ablation;
5. six independently trained existing `MatchedHistoryControls`, including
   exact full direct Beta, order-1/2 history Beta, Bayesian tree, regularized
   full-history ridge, random-history sham.

**No newer control mechanism or new running model owner**. All readouts
are independent research objects on the same fixed public sequence; the
single accepted Yggdrasil learner and trained JEPA heads remain untouched.
Prequential forecast calls may not mutate checkpoints.

## Predeclared scoring and retention

Fixed scoring intervals per source: novel B [96,192) (96 events; first 32
novel B events [64,96) are adaptation), A-return [192,256) (64 events),
and pooled [96,256) (160 events).
- Equally weighted stage-1 transition and stage-2 terminal-reward Brier,
  and separate terminal Brier, for all 10 readouts. Lower is better.
- The strongest of six conventional controls is selected descriptively
  in each phase after scoring; this is **engineering**, not independent
  held science.
- At t=64 pin the first 16 witnessed familiar A public queries
  (views/action/s2) and read their fixed `y=s2` terminal Brier at the
  A anchor, at t=192 post-B, and t=256 after A return, without training
  those probe labels or using hidden phase signals in readouts.
- Record feature selection counts (none and all four features) for
  recent32 candidate and recent32 sham over the three intervals, source
  digest, candidate checkpoint SHA and exact source-free cold replay.
- Before scoring verify the fixed B phase contains all previous/current
  action pairs and independent identical observed public-cell contrasts.
- Include wall-clock whole-loop and checkpoint byte metrics; do not claim
  compute parity of internal implementations or scientific efficiency.

**RD04_ENGINEERING_FEASIBLE requires BOTH fixed sources simultaneously:**
(a) recent32 candidate pooled 2-stage Brier at least **0.005 lower**
than the best of six fully fitted conventional controls;
(b) candidate novel and familiar-return 2-stage Brier no worse than their
best respective control by **0.010**;
(c) candidate novel B terminal Brier at least **0.005 lower** than its
recent32 misaligned-history sham;
(d) candidate pooled 2-stage Brier at least **0.005 lower** than the old
direct cumulative router;
(e) old-A probe Brier at t=192 and t=256 worsens no more than **0.020**
relative to t=64 anchor;
(f) actual correct prior action feature `previous_pair` must be selected
on >= **16/96** B-scored episodes;
(g) both source identity, identifiability, pinned protocol, no label
leakage, immutable forecasts, cold replay, audit and exact Linux/Windows
full regression PASS.

If (a)–(g) do not all hold, result is RD04_ENGINEERING_NO_GO with
precise failed clauses; if source (identifiability) fails or auditor
cannot verify chronology/report, it is RD04_ENGINEERING_INVALID. Never
tune to source outcomes, rerun consumed rows as a fresh trial, change
thresholds after seeing results or claim scientific superiority.
For a new hypothesis after RD04, require an independently frozen,
never-before-consumed source family.

## Custody / owner fences

Original CAP04 `prereg.json` blob
`1d79e222685ea1a6889bff49e5bf405a9aed9580`,
RD02 frozen protocol blob
`aac12e09ff4ea6729693c1fac41d8aa0dfb82a4f`,
RD03 frozen diagnostic blob
`bc1fd6fa7ec83d62b6140fe4915ede33e023443a`,
and historical RD02 NO_GO / RD03 identical dual-OS receipts must remain.
Original-world first use under issue #426 is not authorized. Do not touch
accepted main, active owner source/ledger, learned checkpoints, PR #1278,
Amalgam training, or create a competing learner lineage.
