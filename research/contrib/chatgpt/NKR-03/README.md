# NKR-03 — Native causal evidence and deliberate uncertainty

## Original reason for this gate

[Native bridge NKR01 PR #1092](https://github.com/spoonman136668-ai/Yggdrasil/pull/1092) passed source-verified dual-OS regression and enabled non-gradient context-sensitive decisions with no duplicate facts. [NKR02 PR #1094](https://github.com/spoonman136668-ai/Yggdrasil/pull/1094) then independently showed an important **MIXED / NO-PROMOTION** result: direct numeric weights worked perfectly on the 16-slot affine family but made **128 confidently incorrect outcomes among 352 unseen quadratic heldout effects** after only singleton interventions. That failure is scientifically real. No source changes or replay of that cohort are allowed.

First NKR03 commit `257a37a0e5c6c962191da5c247a2fc133eb9ba42` froze this new hypothesis, scale, budgets and control comparison **before implementation or newly sourced data**. The independent source uses NEW NKR03 SHA256 worlds, visible public synthetic causal laws, not NKR02's evaluated original or WSP114/115 protected-world answers.

## What changes in native Yggdrasil

The same original `NativeRelationMemory` now optionally accepts **genuine new public observations contradicting its limited affine feature family** via `observe_public_verified`, without overwriting old numeric weights or duplicate storage for the same (native address, context, action). Only incompatible *new evidence* is stored in a bounded address-specific exception slot; an identical source alias never increases counts, and conflicting facts for an already observed key always reject atomically.

Legacy `observe_public`, ordinary `choose` and the old snapshot remain as before. Existing NKR01 version-1 relation checkpoints are **byte-identical when no incompatible new evidence exists**; those can cold-restore. When verified exceptions exist, a separate canonical version-2 SHA256 envelope includes the original v1 program only once plus only its exceptions; integrity and exact cold replay are mandatory. The original 16-slot YPC1 state still has a 164-byte checkpoint, unchanged.

The **new opt-in readout** `PublicCausalCells.choose_verified_contextual` acts only when **both observed public action outcomes for the exact native address/context exist** and differ. Otherwise it returns the unchanged context-free incumbent decision. A fitted affine numeric weight prediction on an unseen composition is **not evidence that a higher-order relation is absent**. This policy cannot guarantee an unknown environment outcome; it prevents *unsupported confident effect assertions*. Source labels are provenance labels, not a certificate that an arbitrary caller told the truth. No live source connections or automatic accepted-state promotion were enabled.

## Frozen scientific-development check

Six genuine two-bit action contrasts per slot, actions 0 and 1, are added at a maximum **12** additional interventions (on top of 10 singletons) per slot; audit budgets **12,8,4,0**. This reaches 16 native slots and 16 newly generated novel-world laws in each of two families (unknown quadratic pair; unknown cubic triple), 11 heldout composite contexts per slot, **176 decisions per family/budget**.

At the highest 12 intervention budget each family must achieve all **96/96** directly evidenced pair-context decisions, no unsupported confident claims on the other **80/80** unobserved contexts, and >=15 percentage points improvement vs its own identical-public-data incumbent. The direct evidence-only lookup control should **tie** on supported decisions, not be treated as an inferior baseline. Independently authored complete quadratic symbolic and actually trained gradient 32-hidden tanh/Adam with 2000 updates each are evaluated on the **same public events**. All controls and the old native decision path are compared over each frozen budget, including cold retention, no-duplication and cost diagnostics.

This is a **scientific-development capability/safety study only**, not evidence that Yggdrasil has learned open-domain language, outside-family causal transfer or reliable autonomous generalization. The directly observed six pairs are supported because they were actually probed; unseen triples remain outside the earned evidence. Recording observed higher-order exceptions is genuine direct knowledge intake, not evidence of generalized world understanding.

**No automatic merge or trained-knowledge import** is authorized by this proposal. No Yggdrasil accepted main state, Wingless, Hybrid, FORGE, native controllers, schedulers, paid APIs, self-hosted runners or hidden WSP/NKR prior worlds are changed.

## Fabricated qualification checkpoint before frozen public DEV

[Run #43718149966](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43718149966) **SUCCESS** Linux and Windows on candidate `985260821ca2ed31fe14eebfd6016f2729dddc72`: new NKR03 native exception/guard tests, legacy NKR01 relationship tests and incumbent cell tests PASS. Frozen prereg SHA `257a37a0e5c6c962191da5c247a2fc133eb9ba42` is an ancestor; no protected WSP114/115/NKR02 data or accepted model writes. This is only fabricated fixture qualification, **not** independently qualified original public DEV or scientific acceptance.
