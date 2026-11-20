# Yggdrasil P0 — learn, retain, compare, repeat

**Operating decision (2026-11-19):** Retention-first, one cumulative learner, smallest useful experiment. This is the working plan for isolated Amalgam [PR #1329](https://github.com/spoonman136668-ai/Yggdrasil/pull/1329); it is **not** a training-start command, new execution authority, or promotion. Engineering guard is ready; scientific improvement remains unproved.

## Pinned start, not a model restart

- Existing Amalgam source: `86264b41a08d49f558418c0fba367f3a2636befa` ([PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278)).
- Exact archived **experimental** P0 joint-state content SHA-256: `576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`, with **1,025** original witnesses, native state and **four** trained JEPA heads. The native checkpoint hash is `5720151e18b52f7219763027c2ad9c7c37476e099b4334e42417615adb7f959d`.
- Original frozen transfer protocol content SHA-256: `22edfde67e981c561ade96b988e4ae9ba1f0d8cf2fb3ae6c9560b6f421b8a60e`.
- Accepted `main` (unmodified): `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
- Donor/starting-state artifact byte integrity was independently checked and recorded in [PR #1329 custody comment](https://github.com/spoonman136668-ai/Yggdrasil/pull/1329#issuecomment-7021464968). **Downloaded-byte checks are not a successful native owner cold restore.** The state flags `accepted_native=false`, `scientific_pass=false`, and `engineering_fixture_only`; do not present P0 as an official accepted continually trained model.

## The minimal research loop

1. **Restore once and reuse.** At the independently qualified native owner, restore P0 through the existing `selection_trial.restore` mechanism, verify the complete original ledger, all four heads and checkpoint hash, and record one cold-restore receipt. Reuse this verified checkpoint and existing evidence until the source, contract, or owner changes. No restart from empty weights, no competing learner, no new scheduler.
2. **Protect retained competence.** Identify genuine previously mastered regimes from independent, provenance-grounded evidence *before* selecting Quines; select 5–10 charged transition anchors per regime (eight by default), freeze their indices and manifest hash. The existing opt-in `quine_retention.guarded_observe` checks each prospective **single shared-witness update**. If any Quine transition/reward Brier or complete old-regime/old-prefix Brier rises by more than **+0.02** against P0, reject that shared-state overwrite; retain the **last admitted** state. Log the rejected candidate and continue only with authorized fresh evidence. This guard currently uses retrospective anchor surprise and binary reward as a signed proxy: do **not** claim prequential surprise, measured action cost or independently certified mastery from the implementation itself.
3. **Learn and measure.** One bounded, independently authorized *fresh* acquisition batch at a time. Keep the original source, seeds/splits, public actions, charged outcomes, learning budget, matched information, compute and controls frozen **before** the first new outcome. Compare unchanged P0, unguarded native continuation, Quine-veto native continuation, and the strongest fully fitted relevant conventional/exact controls on matched data. Check **retained familiar transition/reward Brier, genuinely withheld unfamiliar transfer Brier, and full-process cost**; include cold replay and tampering negatives. Never tune on the old consumed transfer cohort.
4. **Keep only earned gains.** A research improvement requires every familiar/Quine retention delta `<= +0.02`, a clean separately withheld familiar check, and lower new-cohort withheld Brier than the **same-cohort** strongest control, with deterministic reconstruction and budget parity. If the result fails, preserve the negative and the last good checkpoint; change one causal hypothesis, not the machinery. If it succeeds, retain the candidate for separately authorized qualification. Report hashes, metrics, cost, PASS/FAIL and the next eligible test in **one** consolidated receipt.

**Historic failure stays a failure:** `transfer-curve-dev-01` yielded familiar Brier `0.091801 → 0.189425` (drift **+0.097624**) and withheld `0.210820` against the historical strongest-control mean `0.195822`; **DEV_NO_GO**. The historical control is a reference, **not** the threshold for a new distribution. Freeze further JEPA gating heuristics and unconditional blending until native retention and transfer are demonstrated.

## Keep development light; keep science honest

- No extra PR, harness, controller, research track or repeated regression for an unchanged exact source. Use the existing Quine tests and [qualified exact-source CI #44586135646](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44586135646) (Ubuntu/Windows PASS, **403 tests per OS**) as the engineering baseline. Re-run the **mandatory full final regression** only for a changed candidate SHA, interface, protocol, dependency or custody key.
- Development fixture smoke checks can be simple and cheap; they are **not** scientific first-use. The independent owner/runner, real cold restore, certified mastered-regime windows and new-cohort preregistration are the limited essential gates before any protected experiment.
- No owner process, queue, schedule, research source, existing data, accepted ref, active learner, or trial state may be overwritten as a shortcut. Existing P0 is an archived experimental fixture. Preserve expiring artifacts under legitimate owner custody rather than designing another storage system.
- **Not now:** context-specialist speciation, nullspace projection, action-ID-free role binding (P3, PR #1327), and SCDR/H1 variable minting (CKAD41–49, PR #1320). Read-only diagnosis can proceed independently, but do not promote these before basic functional retention.

**Status (2026-11-19):** Engineering PASS at pinned candidate `d0f1b0a382f16ee119c464a434f79f18e2603cc9`; experimental checkpoint artifact integrity PASS; owner cold restore UNVERIFIED; real mastered Quines UNVERIFIED; functional retention/transfer scientific gain UNVERIFIED; accepted deployment NONE.


## Source-interface correction (2026-11-19; engineering candidate only)

The P0 guard now checks **the effective selected policy** when all three
inputs are the same active-selector type. For a native-only path it retains
its original native forecasting behavior. Mixed native/selector inputs fail
closed: a caller cannot pass an active policy in one position and raw native
weights in another to bypass the policy-level veto.

The selector checkpoint receipt separately binds the complete joint-state
digest, frozen selector configuration, and all matched prequential routing
evidence. A candidate cannot silently change that configuration during one
witness update. The read-only \`verify_selector_replay(expected, restored)\`
checks the complete active-policy custody and old historical functional
forecasts after the existing native + JEPA cold-restore/selector-replay route.
It does **not** itself instantiate a fresh operating-system process, authenticate
an owner runner, or qualify the archived P0 as accepted science.

Synthetic negative controls cover selector-only degradation with unchanged
native probabilities, selector/native bypass, config drift, routing-state
cold-replay divergence, and single shared-witness admission. Exact changed-
candidate dual-platform full regression is still required; no real mastered
regime, owner cold restore, or protected new source use is claimed.

## Charged-veto receipt contract (engineering only)

A vetoed witness is absent from the admitted active checkpoint. The optional
`on_veto(receipt_bytes, receipt_sha256)` callback on `guarded_observe` must
acknowledge the canonical witnessed-event receipt with source packet,
original actions/outcomes, and rejected proposal/active checkpoint pins.
If the callback is missing or does not acknowledge the expected SHA-256, the
guard **raises instead of returning a silent veto**. The qualified independent
owner must ensure its storage is append-only, durable, crash-safe and
idempotent for identical event identities; a SHA-256 acknowledgement by itself
does **not** establish those properties. `assess_update` is a proposal-only
checker, **not** the owner witness-ingestion interface.

This changes no native state, accepted model, research source, owner,
controller or scheduler. Rejected evidence is externally retained for later
qualified learning but not trained into the current checkpoint. The source-free
test covers successful acknowledgement, missing/false acknowledgement,
unchanged active state, and repeated identical receipt. Actual owner durable
custody and scientific learning benefit remain UNVERIFIED.

## Frozen-input validation on idempotent replay (2026-11-19)

The opt-in `guarded_observe` now checks the unchanged frozen Quine manifest
pin, the fixed +0.02 drift contract, active-policy configuration, P0 anchor
checkpoint and ledger digests, and the original ledger prefix **before**
calling the existing observe route. An idempotent existing-witness replay
therefore cannot bypass those input checks. The same preflight is shared
with a proposed new-witness gate so the two paths cannot diverge.

A source-free negative test supplies a wrong manifest pin, altered manifest,
changed tolerance, and stale anchor to the idempotent route. This is only
research-branch integrity hardening: owner custody, fresh learning,
scientific benefit, and accepted deployment remain UNVERIFIED.

## Historical-score reuse for the bounded Quine guard (engineering only)

The guard now computes anchor-versus-proposal transition and reward losses
**once per retained witness for each policy**. It reuses those same exact
integer loss numerators for all selected Quines, certified-regime averages,
and the complete original historical prefix. This removes redundant forecast
calls without changing source admission, the fixed +0.02 tolerance, accepted
versus vetoed candidate state, current-versus-anchor custody, or the outside
owner receipt obligation. The proposed active native model remains one shared
cumulative state; this is not a new learner or selector.

The source-free negative test enforces precisely **one evaluation per policy
per historical witness** on the existing 24-witness/two-regime fixture:
24 anchor calls + 24 candidate calls versus 64 + 64 before this change.
That is a **2.667× reduction in forecast calls on this fixture**, not a
measured end-to-end speedup, training improvement, or scientific gain.
Existing admission/veto, replay, selector, source-pin and Linux/Windows full
regression must also pass on the exact final candidate. No archived P0
scientific source was reused as a new trial and no owner first-use occurred.

## Integrated continuation envelope (research candidate, November 19, 2026)

The pure cumulative_checkpoint.py codec bundles the exact pre-existing native+four-JEPA-head checkpoint bytes with a separately pinned Quine manifest, trained selector routing configuration and evidence, rejected charged-witness receipts, historical functional readout hashes, and an explicit owner-supplied continuation cursor. Anchor and active core bytes are preserved without mutation, retraining or conversion. Identical veto receipts deduplicate; conflicting IDs, accepted/veto overlap, altered packets, forged weights and selector evidence fail closed on restore.

The caller must use the existing source-pinned native/Jepa restore route and reconstruct the policy from its saved evidence. This research-only bundle does not modify NativeCausalAmalgam v1, authorize scientific first-use, or prove durable owner custody. An independently authorized owner must atomically save this envelope together with its full charged receipt store, verify readback and crash recovery, and authenticate the cursor and lease before using it for cumulative training. The separate six-head JEPA2 research architecture is not implicitly fused into this four-head Amalgam.

Synthetic integration tests alone cannot prove original learned-model cold restore or scientific efficacy.
