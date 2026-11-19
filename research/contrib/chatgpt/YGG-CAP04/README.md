# YGG-CAP04 — Native cumulative predictive-state splitting

**Status:** preregistration frozen; engineering fixture checks only; registered development source UNUSED; scientific result UNVERIFIED. Isolated tokenless native research candidate, not accepted-model integration.

## Why a distinct mechanism

CAP03's matched intervention contrast passed its exact-source two-OS engineering regression but failed frozen DEV scientific comparison against strong conventional controls. CKAD49 only discovered operators within a preenumerated grammar and tied full structural Bayesian averaging. Retuning those consumed cohorts is prohibited.

CAP04 instead asks whether source-observed past action/consequence history can induce a useful predictive state when the current public three-bit input alone cannot explain outcomes. Feature families are finite and disclosed; arbitrary physical-law invention is not claimed.

## Implemented

- Frozen prospective prereg.json committed separately before implementation or registered source scoring.
- yggdrasil/native_predictive_state_split.py: source-only pooled/conditional estimates, fixed prequential evidence penalty, two-stage clock, cold replay, misaligned history sham.
- tests/test_native_predictive_state_split.py: fixture-only checks for learnability, stage clock, duplicate/tamper rejection, cold restore and import of legacy independent native sensor views.
- Prior native checkpoint and six JEPA heads remain immutable and are not retrained or reset by the fixture.

## Evidence boundaries

Known fixture dependence on the preceding actual action is an ENGINEERING test, not a registered DEV result. The prospective registered synthetic source, independent scientific scoring audit and fresh development cohorts have NOT run. Conventional controls and engineering-only source fixtures are implemented but require source-exact CI qualification. No first-use, accepted main, merge, deployment, Forge integration, or controller/scheduler change.

Fixture-only invocation: PYTHONPATH=. python -B -m unittest discover -s tests -p 'test_native_predictive_state_split.py' -v

Lineage: draft CAP03 PR #1318 and exact sealed parent a594a6c5273345687544ddc31e698498bda41d2c.

## CAP04 matched-control implementation (engineering only)

The additive `yggdrasil/native_predictive_state_controls.py` implements six independently evaluated readouts on the same witnessed history: exact state/action Beta, order-1 and order-2 history-conditioned Beta, Bayesian context-tree mixture with fixed prior and prequential evidence, regularized full-history linear ridge, and a source-ID-hashed random-history sham. The comparator models direct terminal reward conditioned on the genuinely witnessed s2, rather than inheriting the candidate's XOR-residual restriction. Both stages score before target outcome admission. Numeric dependencies are pinned for CI; compute parity and scientific advantage are not claimed.

`research/contrib/chatgpt/YGG-CAP04/source_fixture.py` exposes only two hardcoded engineering fixture IDs and rejects every registered DEV/pilot/primary seed. It checks deterministic, actual action/consequence chronology and an A/B/A fixture shift; these are *not* scored science. `tests/test_native_predictive_state_controls.py` and `tests/test_native_predictive_state_source_fixture.py` cover source identity, sham, no future-label leakage, original model read purity, cold replay and direct stage-2 conditional baselines. `tests/test_native_predictive_state_cumulative.py` is a CI-only integration test that cold-restores the exact original 1118/1093-event CAP03 native and six-head checkpoints separately per OS; it may only read original history and must preserve native byte/checkpoint/readout identity while fitting candidate and all controls. The frozen `prereg.json` remains unchanged.

No prospective source generator, registered cohort scoring, native train continuation, merge, owner controller, scheduled task or accepted main mutation occurs in this engineering gate.

### Six-field historical native records and missingness

The original native ledger contains six fields per witnessed episode, lacking a full public post-state triple; the newest segmented continuation stores seven fields, including an actually witnessed post. This is a source-data format distinction, **not** a 1,118-event loss of original training. Both candidate and fully fitted conventional controls now import the full 1,118/1,093-event historical chronology, with `post=None` for older observations where no post triple was witnessed. It is never fabricated from the next sensor view. Missingness is explicit in ridge features, source-only conditional keys, and cold-replay receipts. The source-exact integration test must verify both original learned checkpoints and all archived readouts are unchanged. These checks are engineering, not scientific efficacy.


## Engineering-fixture identifiability repair (2026-11-19)

**Finding:** The earlier four-action fixture used a fixed four-step cyclic
action order. For every novel-stage observation after the first, the current
action identified the preceding action exactly. Thus the purported
"previous-action-dependent" transition/reward could be learned as a
current-action-only function. The original engineering fixture did *not* test
independent historical causal-state discovery.

**Source-free correction:** The two existing **engineering-only** fixtures
now use a fixed 16-symbol de Bruijn action cycle over the same four actions.
For each current action, *all four possible previous actions* appear within
each 16 observations. Both the 32-observation familiar acquisition stage,
40-observation novel stage, and 24-observation familiar-return stage cover
all 16 ordered prior/current action pairs. The action schedule is fixed
before outcomes, independent of the labels, and remains public-action only.
This supplies a necessary variation for history identifiability, not proof
of causal discovery or statistical sufficiency conditional on all sensors.
A focused negative test explicitly rejects the old four-pair confound.

The original `prereg.json`, registered seeds, original CAP03 native model
checkpoint/JEPA heads and scientific source-first-use prohibition remain
unchanged. Previous two fixture identities now generate new *engineering*
rows; do not relabel earlier fixture scores as fresh science. The source
actor and registered DEV/pilot/primary cohorts are still absent.


## Next bounded gate: causal-history matched-control engineering diagnostic

With the identified current-action alias removed, the existing immutable
fixture auditor now emits `CAP04_ENGINEERING_DIAGNOSTIC=` JSON for **both**
already known 96-observation engineering sources. Each result binds the
independently audited source and prequential score receipt, reports all seven
candidate/control Brier scores and the best control in the frozen novel
(48–71), familiar-return (72–95), and pooled (48–95) intervals. Positive
`candidate_minus_best` means the learner **lost** to that matched control.

It also reports the distinct ordered previous/current actions (expected
16 of 16) and how often the same observable current public views and action
can follow multiple previously witnessed actions. This is **necessary but
insufficient** to establish identifiable causal dependencies: public context
could contain other predictive information and the code only performs
observational prequential scoring. There is no new registered source birth,
no protected cohort, no first-use lease, no action-selection evaluation and
no claim of scientific advantage even if a known fixture scores well.

An exact frozen-source and dual-OS full test workflow emits the diagnostic
to the GitHub Actions run. The archived engineering fixture metrics are
exploratory and may motivate a distinct preregistered follow-up but must
not be used to tune the existing reserved CAP04 scientific thresholds.

## Structural expressivity falsifier — frozen reward XOR readout (2026-11-19)

The CAP04 candidate's already-disclosed `residual=y XOR s2` design
imposes a **hard anti-symmetry constraint**. For any *fixed* current public
views/action and actual past history, it has a single fitted residual
probability `p`, then forecasts `P(y=1|s2=0)=p` and
`P(y=1|s2=1)=1-p`. It **cannot** express a genuine rule
`y=0` (or `y=1`) regardless of witnessed `s2`, even if sufficient
past data has established this fact.

With balanced `s2=0/1`, the candidate's average stage-2 Brier for either
constant reward obeys `(p²+(1-p)²)/2 >= 0.25` (same lower bound
for always-one labels). An exact matched-information control already
implemented in `MatchedHistoryControls` conditions direct terminal reward
on the *witnessed* current `s2` and is **not** subject to this bound.

The existing `tests/test_native_predictive_state_controls.py` now includes
a pure engineering negative control with **128 actual chronological synthetic
witnesses**, 64 for each sensor value, for both constant-zero and
constant-one reward. It verifies the mathematical floor, fits the already
available direct Beta control (expected stage-2 `P(y=1)` equal to
`1/66` or `65/66` for each sensor, respectively), checks read-only
forecasts and exact source-free cold replays. This case is deliberately
outside CAP04's expected causal family and its original registered DEV
source; **it is not a replacement scientific cohort, a change to
preregistered thresholds, or an accepted-model training update**.

**Research interpretation:** finite history-feature induction alone cannot
resolve a misspecified terminal-reward factorization. If real novel
relationships need sensor-independent or asymmetric direct reward, reuse the
existing direct terminal-reward representation as a comparison/reference;
do not add another learner or retrofit CAP04 to post hoc fit this example.
A future different hypothesis must be prospectively preregistered, evaluated
on genuinely fresh owner-qualified sources, and integrated only by the central
Amalgam coordinator after independent scientific qualification.

## CAP04-RD01 opt-in direct-reward shadow (frozen before implementation)

**Preregistered source-free engineering protocol first:** `RD01-FROZEN-ENGINEERING.md`
in commit `94791622ccb28ffca50b61a42b7b016e8670dc23`. The original
`YGG-CAP04/prereg.json` remains unchanged; no original-science seeds
`99917/99931` or owner-protected source are opened.

The existing `PredictiveStateSplit` class now exposes a strictly optional
`reward_mode="direct"`. Its original default `"xor"` behavior, imported
witness handling, evidence selection and checkpoint v1 bytes remain unchanged.
The new mode fits the **actual witnessed terminal reward** conditional on
current revealed public `s2`, rather than predicting `y XOR s2` and then
inverting the prediction when `s2=1`. It uses the same fixed, bounded
history-feature selection, mutation-free prequential readout and source-ID
controls, **not a competing model-owner/learner process**.

A distinct `SCHEMA_DIRECT` stores the selected reward-mode identity.
The direct schema and XOR v1 schema can each cold-restore exactly, but
cross-schema reinterpretation fails closed. The existing direct-reward
matched-history Beta remains an independently fitted strong control, not
a reference model to claim superiority over.

The separately frozen RD01 engineering test uses two **128-observation**
known synthetic series, constant terminal reward 0 or 1, balanced observed
`s2` and identical public action/view. It requires the direct head's
balanced stage-two Brier below 0.05 for *both* constructions while retaining
the XOR model's known ≥0.25 structural lower bound. It verifies the full
source-clock, closed readouts, exact mode-specific restore and tamper refusal.

**Limitations:** a mechanism class that can represent a known counterexample
is not demonstrated to discover a new real causal law, retain an older native
skill, beat exact controls, or improve whole-process efficiency. No claim of
qualified scientific benefit or permission to integrate into the accepted
single Yggdrasil learner follows from this opt-in engineering PASS.


## RD02 independent A→B→A source-free engineering falsifier

Protocol frozen in commit \`157a52827b8898b33bc2de58d9eb031f429b8e67\`
at \`RD02-FROZEN-ENGINEERING.md\`, **before** generating or scoring any
RD02 outcomes. This does **not** alter the original CAP04 preregistration.

The read-only scientific-method test driver \`rd02_engineering.py\` uses
two predetermined synthetic, unregistered-source identities, 256 real
chronological observed public interventions each, and one fixed
A (reward=s2) → B (reward=previous action bit 0 AND s2) → A schedule.
It compares the opt-in direct-reward history candidate, old XOR
candidate, misaligned-history direct sham and six existing independently
fitted conventional controls, all with identical public actions and
consequences. Scores are computed **prequentially** at both stages;
the unknown B law and phase labels are not supplied to predictors.

The frozen test records familiar A anchor, B endpoint and A-return
fixed A-readout probes, each exact-cold-restored without overwriting the
original model, and separately reports novel, return and pooled Brier.
Its one-shot output lines \`CAP04_RD02_ENGINEERING=...\` carry the two
source identities, receipt/source hashes, each strongest named
conventional control, candidate-minus-control and every failed gate
criterion. Both registered source IDs must satisfy every preset
gain/retention/sham condition to classify as
\`RD02_ENGINEERING_FEASIBLE\`; otherwise preserve
\`RD02_ENGINEERING_NO_GO\` and its exact negative clauses.
The code supports no alternative registered scientific seeds.

This **cannot** by itself prove native cumulative intelligence or
admit a new checkpoint into the accepted owner. Zero original-world
first-use, zero fresh protected CAP04 scientific cohort, zero model
owner/runner/queue/Forge involvement. Central Amalgam chat is the only
candidate integration coordinator.


## RD03 read-only history feature diagnostic

The source and analysis contract are frozen in `RD03-RETROSPECTIVE-DIAGNOSTIC.md`
at commit `632039c1ac480cd05012c94ffda5e395722cf026` **before
implementing the instrument**. `rd03_diagnostic.py` only replays the already
evaluated RD02 engineering sources; no fresh source identity, scientific
cohort, owner action or new learner is introduced.

The instrument records `selected_feature("residual")`, per-stage
selection counts, existing unmodified cumulative selector evidence, and
read-only pooled and forced previous-pair reward forecasts prior to each
actual synthetic event. It compares historical A/B/A windows and checks
that the prior published B-terminal Brier is reproduced at its original
exact fixed source SHA. Existing opt-in `direct` and sham models receive
identical witnesses. The forced-feature counterfactual is **only a
retrospective diagnostic, not a trained new arm or evidence of gain**.
The independent replay auditor checks source, score, selected-feature,
evidence and tampering. Preserve RD02 NO_GO and all old experimental
negative findings regardless of new diagnostic observations.

A feature not being selected is a mechanism hypothesis, not proof that
the learner can never capture previous-action history. Fitted controls,
fixed-feature representation, and model/observation context confounds
remain possible. Under the current sole-coordinator boundary, no
canonical Yggdrasil integration or model-owner action is authorized.
