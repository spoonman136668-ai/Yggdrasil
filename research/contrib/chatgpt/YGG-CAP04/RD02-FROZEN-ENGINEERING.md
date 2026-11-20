# CAP04-RD02 — freeze source-free A→B→A causal-learning falsifier

**Freeze before generating/scoring any RD02 world** — 2026-11-19.
**Independent contributor:** CAP04 research PR #1324; central Yggdrasil model
integration remains solely with Unified Causal Intelligence Amalgam Work.
**Frozen parent:** `bb13611a78044cb9e5fd78c7da795483aa717646`.
**Classification:** SYNTHETIC_ENGINEERING_ONLY. These are constructed toy
worlds, not protected original-world first-use, registered CAP04 scientific
DEV seeds or proof of cumulative autonomous intelligence.

## Predeclared hypothesis and hard negative alternatives

Hypothesis: opt-in `PredictiveStateSplit(reward_mode="direct")` can exploit
a genuinely witnessed prior action to represent a reward relation that the
original CAP04 XOR-residual head cannot, *while retaining* old A competence
across the A→B→A intervention history. A positive result requires an advantage
over independently trained matched-information conventional readouts as
well as A-return retention, not merely a better fit than XOR.

Alternative explanations include source-clock/source-view confounding, simple
tabular history lookup, inability of the selector to identify past action,
catastrophic interference after a hidden rule switch, or random-history sham
matching the candidate. Record all negative results; no post-hoc retuning.

## Fixed engineering source and chronological budget

Two and only two source names:
`cap04-rd02-source-a`, `cap04-rd02-source-b`. These are *not* numerical
registered first-use seeds. Each source has **256** witnessed public
action/consequence episodes, 512 total across source identities.
Each source begins at public three-bit state selected by SHA256 bits of
`cap04/rd02/<source>/start/<index>`.
At every t, public `views=((u,v),(v,w))`. Public intervention pair
`action=ARMS[ACTION_CYCLE[(t+shift)%16]]` with
`ARMS=((0,0),(0,1),(1,0),(1,1))`,
`ACTION_CYCLE=(0,0,1,0,2,0,3,1,1,2,1,3,2,2,3,3)`,
`shift=0` for source-a and `shift=1` for source-b.
Only outcomes of actually chosen actions exist; no off-policy oracle.
Intermediate sensor `s2` is SHA256 low bit of
`cap04/rd02/<source>/<t>/public-intermediate`, independent of current
model forecasts. The source's *private* A/B mode is determined by t, not
passed to models or predictions.

**A familiar:** t=0..63, terminal reward `y=s2`.
**B unfamiliar:** t=64..191, terminal reward
`y=previous_actual_action[0] & s2` (previous action initially (0,0)).
**A return:** t=192..255, terminal reward `y=s2` again.
Each actual witnessed `post=(v XOR action[0], s2, w XOR action[1])`;
next public `(u,v,w)=post`. Identifier is SHA256 of
`cap04/rd02/<source>/witness/<t>`.
No phase label, prior private law, future `s2` or future reward is given to
learners. Candidate only sees prior observed source events, current public
views/action, then actual current `s2` at stage two.

## Already implemented controls, no new model

Fit from **identical witnessed public sequences**:
- Existing `PredictiveStateSplit(reward_mode="direct")` (candidate).
- Existing `PredictiveStateSplit()` XOR-residual, same finite-history
  source and parameters (structural negative).
- Existing `PredictiveStateSplit(reward_mode="direct", sham=True)` with
  misaligned historical event (negative).
- All six existing `MatchedHistoryControls`: full direct-state/action Beta,
  order-1 history Beta, order-2 history Beta, Bayesian context-tree mixture,
  fixed regularized linear history, random-history split sham. Same witnesses
  and clock. No private source or phase hint in their inputs.

On each t, score transition `P(s2)` *before* revealing s2; score terminal
`P(y)` after revealing public s2 but *before* revealing y; then all nine
readouts ingest the same real public episode. No reward-action optimization
or source-dependent intervention policy.

## Frozen metrics and stop criteria

For each source independently compute mean equally weighted stage-one
transition and stage-two reward prequential Brier on:
- **novel B:** t=96..191 (96 observations; t=64..95 B adaptation);
- **A return:** t=192..255 (64 observations);
- **pooled:** t=96..255 (160 observations).
Also report separate terminal Brier for each interval, all nine readouts,
source digest, final snapshot hashes, and cold exact restore.
Select strongest conventional comparator from all six for each interval
after engineering scoring; comparisons are descriptive engineering (not
held science).

At **t=64 before learning B** freeze the first 16 actual familiar A
public (views,action,s2) queries as old-knowledge probes. On that fixed
list measure candidate and XOR stage-two `y=s2` Brier:
1. A anchor checkpoint immediately after 64 A witnesses;
2. B endpoint checkpoint after 192 total witnesses;
3. A-return endpoint after 256 total witnesses.
No probe labels are trained; probes are read-only. Check identical
original A prefix, source-ID uniqueness, trained event count and
byte-exact cold restoration at each snapshot.

**RD02_ENGINEERING_FEASIBLE** only if, on BOTH source identities:
- Direct candidate improves pooled equally weighted Brier by **≥0.005**
  against the best of six fully fitted conventional controls;
- Its novel and A-return equal-weight Brier each are no worse than the
  strongest respective conventional control by **0.010**;
- Its old-A probe Brier at B endpoint and at return endpoint both worsen
  by **≤0.020** relative to its pinned A anchor;
- Candidate beats the misaligned-history direct sham by **≥0.005** in
  B-stage terminal Brier; and
- Source, prequential clocks, cold pinning, no future leakage, no checkpoint
  mutation and cross-platform qualified regression all PASS.

Any failure gives **RD02_ENGINEERING_NO_GO** (with exact failed clauses),
not an ad hoc adjusted threshold or score. No synthetic engineering score
is a SCIENTIFIC_PASS, no model integration or first-use permission follows.

## Budgets and owner fence

Only **512 new synthetic public fixture events** in two deliberately
constructed internal worlds. This is a finite engineering falsifier.
Maximum 9 readouts per source, 256 steps/source, no original source
actions, no protected CAP04 registered DEV/pilot/primary use, no archived
Amalgam checkpoint/admission, no owner-host modification, no scheduled tasks,
no paid API, no competing model process, no merge/promotion/deployment.

The RD02 source, runner, metrics, independent audit and precise negative
finding must be committed in #1324; use the existing isolated G29 atlas and
complete Linux/Windows regression workflow, preserving this exact prereg
blob unchanged. If scientific evaluation later becomes authorized, create
a *different* independently frozen original/novel-world protocol with
authentic owner custody, fully trained controls, retention and action value.
