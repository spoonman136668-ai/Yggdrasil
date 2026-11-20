# CAP04-RD07 — exact old-A query conditioning audit (retrospective)

**Freeze chronology:** this one-file protocol commit precedes any RD07
implementation or source-specific diagnostic result calculation.
**Research role:** independent CAP04 contributor in existing draft #1324;
central cumulative learner/checkpoint coordination belongs solely to the
Unified Causal Intelligence Amalgam Work chat.
**Frozen parent SHA:** `8efe64da4fc1d193d32c80ca47c458119a4c565e`.
**Classification:** SOURCE-ONLY RETROSPECTIVE ENGINEERING, not a fresh
scientific trial or new trained mechanism. Original RD04 NO_GO remains.

## Falsifiable question

RD06 established that previous `old_skill_queries` froze only
`(views, action, observed_s2)`, while `PredictiveStateSplit.forecast`
uses its most recently witnessed history for the hidden feature values.
This means its forecast inputs at A anchor (64 events), B end (192),
and A return (256) did not include the same prior action, post or
reward. Quantify how much of previously reported old-A readout drift is
explained by that query-history mismatch, **without** altering the
trained model, source, thresholds, or retrospective labels.

The test must NOT claim that eliminating query-context drift proves
absence of forgetting. The same exact public historical input can be
scored differently because learned pooled counts, selected features,
shrinkage and evidence have changed. Retention is about *fixed-input
functional output*, which is distinct from immutable checkpoint bytes,
parameter deletion and online phase selection.

## Fixed source, model and inquiry budget

Exactly two original, already-consumed RD04 engineered public sequences:
- `cap04-rd04-source-a`, SHA256
  `a3a06178c1bc0955bb7e5258284aaaa90691c556cd832310d146373f703339be`.
- `cap04-rd04-source-b`, SHA256
  `4ed6c8044fa88c4667c3b6194c93f74480ed18462e9720b0e1dba9a718a7cdf3`.

Identical existing A→B→A 256 actually witnessed public actions/consequences
per source, no new source identity, no private phase labels fed to learners
and no counterfactual outcome. Existing only readouts:
`PredictiveStateSplit(reward_mode="direct", routing_mode="recent32")`,
`PredictiveStateSplit(reward_mode="direct")`, and original XOR mode.
No other new trained model, trained conventional control, native
checkpoint alteration, owner action or SCIENTIFIC_PASS.

Replay each original public witness into these three independent
research-side shadows solely to recreate the **same historical RD04
three model states at t=64/192/256**. The models receive actual
observations identically and exactly once. For each state and each
of the **first 16 old-A actually witnessed source queries** compute:
1. **Legacy readout**: standard `forecast(views,action,"residual",s2)`,
   which reads learner's **latest** historical event, and mean
   familiar-A reward Brier versus witnessed A label `y=s2`.
   Require legacy values replicate the exact published RD04
   `old_a_probe` means, from a fresh read-only validation of
   `rd04_engineering.run` on identical consumed sources, within
   `1e-12`.
2. **Frozen full input**: the same query `(views,action,s2)`
   with its **original source-public previous event at index i-1**
   (or at i-3 for the explicitly sham readout, which is not run here).
   For query i=0 the historical feature value is `None` under
   the original prequential clock. When available, use **exact
   original public prior pair/post/reward** in
   `previous_pair`, `previous_post`, `previous_reward` and
   `previous_pair_post`. Execute the *same* existing
   `_winner("residual",values)`, `_conditioned_state`, `_estimate`
   and XOR output inversion *without modifying any model state*.
   Each source index, public ID and previous witnessed ID must be
   checked against the learner's own exact append-only event ledger
   at that checkpoint and against the source SHA.
3. **Current conditional/context comparison**: how many of the 16
   frozen query contexts differ from the live learner's last-episode
   history at each stage; frozen and legacy Brier, fixed-input
   Brier drift relative to A anchor and legacy delta. Report whether
   **the frozen full-input drift passes or fails the previously
   registered RD04 threshold +0.020** at B endpoint and A-return;
   label this a **RETROSPECTIVE DIAGNOSTIC ONLY**, never a
   post-result change to original RD04 `NO_GO` verdict.
4. At each stage record model checkpoint SHA/bytes and exact cold
   `PredictiveStateSplit.restore` parity for all 16 frozen readouts.
   Negative tests: reject source identifier mismatch; source order or
   past actual reward tampering; future event used as historical context;
   forged old-A label, sham wrong lag; all forecasts leave current
   checkpoint untouched; independent report audit recomputes full
   fixed source/query diagnostic and rejects forged Brier/count/identity.

The frozen summary must explicitly distinguish:
- **input-context mismatch rate** (descriptive, not forgetting);
- **same-input retrospective old-A functional drift** (can indicate
  inability to preserve old behavior; not proof of deletion);
- **legacy published RD04 old-A drift** (old preregistered failure
  criterion, never revised);
- **phase-blind active environment identification** (NOT tested);
- **new-world improvement vs matched controls** (NOT tested).

## Decision rule and evidence class

Classify `RD07_RETROSPECTIVE_VALID` if all original source SHA,
historical IDs, old legacy Brier readbacks, exact cold restores,
finite probabilities, source-order/negative controls, complete
read-only inspection and Linux+Windows cross-platform full
regression pass. Otherwise `RD07_DIAGNOSTIC_INVALID`;
do not tweak predictions or source data after seeing the results.
Do not declare a scientific win on a smaller old-A delta, because
these are previously scored in-sample synthetic probes.

No protected original-world first use (#426), new approved training
owner, queue/scheduler, paid API, merge, deployment, official
learner/checkpoint promotion or restart. Preserve and submit the
diagnostic to #1324 and the existing central review #1327 only after
engineering qualification. Avoid overlapping Quine #1329's
checkpoint-retention guard and LR-92AR #1330's archived/recent
posterior learner: this is an **input-provenance audit**, not a
new retention gate or a competing learner.
