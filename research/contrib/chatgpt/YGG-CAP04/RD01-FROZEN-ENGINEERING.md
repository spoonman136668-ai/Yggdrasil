# CAP04-RD01 — opt-in direct-reward history head: frozen engineering protocol

**Status:** source-free engineering hypothesis; NOT the original CAP04 registered
DEV trial, owner-qualified source, main-model update, or scientific acceptance.
**Freeze:** repository prereg commit must precede code/test implementation.
**Parent:** CAP04 draft PR #1324 at `6f1622f4d18869b3ade0c0101a4db5c7efe89370`. No new model lineage or
experiment owner. Central integration coordinator: Unified Causal Intelligence
Amalgam Work chat; this contributor does not merge or promote it.

## Falsifiable hypothesis

The previously verified CAP04 `residual = y XOR s2` factorization enforces
`P(y=1|s2=0) + P(y=1|s2=1) = 1` for any fixed current public views,
action, and actual preceding witnessed history. This prevents faithful
prediction of both `y≡0` and `y≡1` when both sensor values occur.

**RD01 alternative, isolated from the frozen original:** provide a selectable
`reward_mode="direct"` on the existing `PredictiveStateSplit` class, in
which the stage-two target is witnessed `y` and the `s2` bit is included
as an explicit condition in both pooled and history-split reward keys. The
existing candidate remains `reward_mode="xor"` by default, byte-identical
v1 checkpoint format, original frozen prereg and all original fixtures unchanged.
A distinct, schema-marked direct-mode checkpoint must reject tampering/cross-mode
reinterpretation.

## Fixed structural engineering witnesses and checks

- Source: in-memory manually constructed events only, independent of
  `YGG-CAP04/source_fixture.py`; no private entropy or reserved scientific
  seeds. Use two patterns `reward=0` and `reward=1`, **128 chronological
  witnessed events per pattern**, `s2=i%2`, fixed public `views=((0,0),(0,0))`,
  `action=(0,0)`, `post=(0,s2,0)`, deterministic unique synthetic IDs.
  Each model sees the same actually taken action and sensor/outcome per event.
- After 128 observations, evaluate read-only stage-two forecasts at both
  *possible public sensor values*, conditional on the *same* history.
  This is a representational probe, not a scored causal-action trial.
- **Preset success:** for each of the two patterns, the direct mode's balanced
  average stage-two reward Brier **<0.05**, while the original XOR mode
  retains its previously proved floor **≥0.25**. The existing fitted
  direct-reward `full_history_exact_state_action_Beta` is included as a
  strong control with expected `1/66` (all-zero) or `65/66`
  (all-one) per sensor, and is NOT required to lose to the new candidate.
  No scientific gain is inferred from this analytical engineering setup.
- Verify stage-one forecasts cannot see unrevealed `s2`, reads do not
  mutate checkpoints, duplicate/conflicting IDs fail, old XOR v1 source
  checkpoint is byte-identical and restores exactly, direct-mode schema
  and exact cold-replay survive, and cross-schema/tamper attempts fail.
- Fail-closed if any condition is false; keep the failure and report **NO_GO**
  without tuning this registered engineering probe.

## Scope, cost and decision

No original-world first-use, CAP04 registered `99917/99931` DEV,
pilot/primary, archived Amalgam learning, trained JEPA heads or owner
checkpoint are read/modified. No new scheduler, runner, controller, source
actor, alternative accepted model or policy activation. Keep no additional
model in a live owner process. Only a bounded research-side alternative
algorithm is implemented; stronger conventional controls remain untouched.

Required engineering qualification: existing source-first pinned atlas and
full Linux/Windows test suites at exact final candidate SHA/tree; record
test counts, source and final parent, protocol integrity, runtime and
a deterministic negative control. **Scientific status remains UNVERIFIED
even if engineering passes.** A future scientifically meaningful test of
direct-reward generalization would need a *different*, independently
preregistered and owner-authorized prospective source family, old-model
retention and matched-control/action/compute budget. Do not rewrite the
original CAP04 prereg or post-hoc re-score consumed fixtures as new science.
