# YGG-RET03 — staged two-action public forecasting

**Source-only engineering candidate** stacked on exact qualified [RET02 PR #1291](https://github.com/spoonman136668-ai/Yggdrasil/pull/1291)
at `0e4c9b32cd3a037f10b5d441ec9fb2c8c92f54eb`.
Original RET02 retained trained native+six-head checkpoint, readout, source,
prereg and scored original evidence are not modified.

**Frozen protocol before source implementation:** Git commit
`2fc425b1a52ff3f29aa094e06076bbd8fea8905e`.
This is an engineering freeze, not a new scientific first-use lease.

## The precise temporal boundary

The original RET01 `forecast(views, full_row)` computes
`P(s2 | prior views,x1)` and then
`P(y | prior views,x1, witnessed s2, chosen x2)` inside one call.
That was valid as a **post-first-stage forecast**, not as an unconditional
prediction of both outcomes *before* the first action. Consequently,
a retrospectively scored two-output Brier must not be presented as
fully pre-action prediction unless the two steps are separately timed.

RET03 introduces an **opt-in timing adapter**, without changing original
RET02 or native learning:

1. `begin(source_id, prior_public_views, chosen_x1)` returns only
   a forecast of the first transition **before knowing s2 or x2 or y**;
2. `record_transition(source_id, witnessed_s2)` receives the first-stage
   observed consequence. **No original model or learned readout update**;
3. `choose_second(source_id, chosen_x2)` returns
   `P(y | prior views, chosen x1, observed s2, chosen x2)` **without y**;
4. `complete(source_id, witnessed_y)` calls the existing
   `NativeTemporalContextReadout.observe` EXACTLY ONCE for a complete
   source-witnessed action/consequence row. Only this stage updates
   the original continuously trained native model, its four active
   specialists and the bounded RET02 temporal readout.

The adapter has at most one unresolved source event, deterministic numeric
floats, exact original checkpoint/prefix preservation, fail-closed phase
ordering and no implicit cancellation. It supports **cold restore of the
full native+readout state at each phase**, with re-execution of the
pending public stage to verify predictions and source custody. It has no
actor or interface for actually sending interventions. Source hashes are
identities, not proof of independently authorized external observations.

The original downstream RET02 readout may use an observed `s2` when
`complete` learns. That is appropriate **after** the first transition
has actually been witnessed, and is explicitly contrasted with the
pre-transition probability that cannot depend on that observation.
The two public views in the RET01 synthetic generator are constructed
from the preceding `u,v,w` state before the event's actions, not future
outcomes. This provides a chronology smoke check for the API; it is not
independent physical-source validation.

Seven hand-authored source-free mechanical tests check pre-outcome
isolation, phase order, repeated/out-of-order rejection, exact original
native source progression, cold replay at each stage, forged rehash
rejection and history continuation. No scored old RET01 development
cohort is replayed; the tests use existing frozen model state only.

## Qualification and research separation

- **ENGINEERING:** original GH Actions Linux and Windows focused + mandatory
  full root/native/inherited causal suites and strict source-pinned G29,
  all on exact final candidate SHA.
- **SCIENTIFIC:** no new original-world first-use, matched prospective
  comparison, unfamiliar transfer, true causal mechanism discovery or
  whole-process gain. `SCIENTIFIC_PASS=false`.
- **DEPLOYMENT:** none. No accepted main/Forge/controller/queue/scheduler,
  model promotion or merge. Keep isolated draft.

A future science-qualified test requires genuine sequential source
`action1 -> s2 -> action2 -> y` with actor/effects journal and
independently owner-approved new source lease, and separate scoring at
the first and second observation clocks. Compare against matched
fully trained history-aware Bayesian/symbolic/recurrent controls,
cold old-context retention and resources, plus shuffled temporal-history
negatives and unfamiliar families, preregistered before first-use.
[Source owner #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426)
currently blocks new protected original-world first-use.
