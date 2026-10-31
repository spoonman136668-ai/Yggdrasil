# MR32 — prospective admission boundary for learned causal-belief formation

Date: 2026-10-31
Classification: RESEARCH CONTINUITY / DESIGN BOUNDARY ONLY.
This document is NOT a preregistration, candidate admission, source-family birth receipt, first-use authorization, workflow dispatch, or scientific acceptance.

## Verified prior frontier

- MR29 PR #382 is OPEN/DRAFT/UNMERGED, exact head `cc55f042adce8da6faa68d16611f0b39a73e9c57`. It found a narrow development signal on 18 correlated naturally reached full-input causal-alias pairs: learned 45-slot innovation-state Brier 0.27099 vs same-weight state-erasure 0.28137 and recurrent 0.30525. It failed the precommitted Empty nonregression criterion (0.14624 vs recurrent 0.13963 and stateless 0.13858); resource parity and source atlas qualification were not complete.
- MR30A PR #383 is OPEN/DRAFT/UNMERGED, exact head `7f2b66165dd4dc27dcd801a2acb168c6363b15a1`. It used fresh development seeds and found **zero** strict full-input natural causal-alias pairs among 1,763 matched alias context groups. The absence of qualifying pairs is a data-acquisition/contrast-availability result, not proof such contrasts cannot exist. The learned-state candidate still failed Empty nonregression.
- MR31 PR #384 is OPEN/DRAFT/UNMERGED, exact head `bcb40f3ed66ba1e1ed8eb0bd3b1842094140dc1e`, base `7f2b66165dd4dc27dcd801a2acb168c6363b15a1`. Its frozen protocol `research/mr31/frozen_protocol.json`, blob `86e979372e9e0e9fdea1b1bd9caa8a9a67b117fd`, predates its acquisition code and execution. The experiment ran 128 original-source development episodes with equal fixed actor-state layouts and matched-prefix action counts. It increased DoorKey seed clusters with strict naturally occurring causal aliases from 1 (MR26 baseline) to 5 (MR31 challenger), and visible key-pickup-then-unlock episodes from 2 to 8. However it is an acquisition mechanism only: no Yggdrasil learner was trained or modified. Total CPU time was higher on both OS; total resource parity is not qualified.
- At MR31 exact head, Windows/Linux focused producer, observation and acquisition workflows passed, while G29 Atlas Acceptance run #39694885199 failed. Mandatory atlas/full integration qualification remains unresolved. Original Farama licensing metadata conflict remains unresolved for redistribution.

## Scientific interpretation

MR31 improves the availability of some naturally observed causal contrasts without expanding the fixed typed actor-state layout. This is useful experimental infrastructure/evidence acquisition. It is not a cognitive-learning result.

MR29's rare positive pairwise state signal did not independently replicate in MR30A, and it did not meet the frozen overall nonregression threshold. MR31 must not be used to retroactively relabel those old cohorts as positive, nor may its acquired observations be treated as independent trials when multiple streams share a reset-seed cluster.

## The only worthwhile next learning question

Can a bounded, architecture-native belief update use *naturally acquired, public-only, full-input causal contrasts* to improve prospective consequence prediction after a genuinely new source family or independent task regime, without degrading ordinary non-aliased prediction?

Candidate mechanism class to investigate (not yet admitted): **prediction-residual-driven selective state formation**. The learner should retain only a compact state component when two histories with identical current public input/action produce systematically divergent observed consequences; it should revise or evict that component when subsequent evidence contradicts it. The retained state must be learned from prior outcomes, not assigned by evaluator labels, source object semantics, or a hand-coded novelty score. No assumption that exact-key history lookup is sufficient.

## Mandatory MR32 prerequisites before any experiment admission

1. Independent FSA authority is deployed and qualified: separate-failure-domain monotonic CAS/archive head, authenticated per-candidate grant, durable one-shot intent/terminal receipts, all-lane cohort ledger, crash/indeterminate-start no-redispatch, and independent witness. FSA-04 issue #83 remains OPEN; this prerequisite is currently BLOCKED.
2. Genuine new source-family birth/rights custody and authentic public action→consequence interface are independently admitted. No hidden parent truth, world/task IDs, generator metadata, evaluator labels or post-outcome signals may reach learner or policy.
3. A fresh immutable preregistration defines disjoint FIT/CHECK/TRANSFER source cohorts, seed clusters, run limits, budgets, stopping rules and negative preservation before implementation freeze and before first use. CHECK is veto-only; TRANSFER cannot tune the candidate.
4. Compare separately trained native candidate, same-information memoryless learner, equal-total-state recurrent/state-space learner, and capable Bayesian/model-based learner. Include same-weight state erasure and native-component ablations. Exact architecture independence across Yggdrasil and Wingless must be preserved.
5. Primary endpoints: pre-outcome predictive loss on naturally observed conflicting consequences and actual task reward/success. Secondary: causal correction after intervention reversal, cold restart retention under distractors, transfer without target-family fit, and calibration on ordinary non-aliased inputs.
6. Charge total resources, not just the named actor arrays: active and retained state, checkpoint bytes, learner/training memory, CPU/wall, peak RSS, source interface, inference and communication. Candidate must meet the preregistered nonregression bound on both causal-conflict prediction and ordinary task inputs.
7. Complete source-bound provenance, Linux/Windows focused interfaces, exact G29 atlas, restart/fault tests and mandatory final full regression. Preserve every negative and harness failure separately.

## Current gate disposition

`MR29_NARROW_PAIRWISE_SIGNAL=DEVELOPMENT_ONLY`
`MR29_EMPTY_NONREGRESSION=FAIL`
`MR30A_FRESH_PAIR_REPLICATION=ZERO_QUALIFYING_PAIRS`
`MR31_CAUSAL_CONTRAST_ACQUISITION=POSITIVE_DEV_INFORMATION_YIELD`
`MR31_LEARNED_COGNITIVE_GAIN=NOT_TESTED`
`MR31_EQUAL_TOTAL_RESOURCE_NONREGRESSION=FAIL/UNQUALIFIED`
`MR31_G29_ATLAS=FAIL`
`FSA_04_INDEPENDENT_FIRST_USE_AUTHORITY=BLOCKED`
`MR32_EXPERIMENT_ADMISSION=NOT_GRANTED`

## What can proceed before admission

Only non-original engineering that does not consume source cohorts: repair MR31's legitimate source-atlas/provenance qualification under its existing owner and exact rules; develop source-only unit/fault/restart tests for a bounded belief-state component; audit total-state and resource accounting interfaces. Do not mutate MR29/MR30/MR31 model results, frozen source cohorts, or existing controller/queue. Do not dispatch an original environment or call the design an executed scientific experiment.

This record is a continuity boundary only. It creates no new controller, worker, workflow, authority, branch protection change, acceptance or promotion.
