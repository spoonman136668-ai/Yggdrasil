# YGG-DB01 — Development-only sensory feedback feasibility

Parent source: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`
Branch: `research/ygg-db01-development-only`
Status: EXPLORATORY; NO SCIENTIFIC RESULT; NO NATIVE LEARNING CLAIM.

## Frozen question
Can a fixed-capacity shared local developmental update receive temporally patterned sensory signals, and can future controlled training establish a causal behavioral benefit from predictable success feedback versus irregular failure feedback?

## Boundaries
The repository currently contains an accepted DG-1 NCA *design* but no verified executable native DG-1 update in its source atlas. PublicCausalCells is a conventional comparator and must not be reported as DG-1 cognition. No accepted research refs, schedulers, production paths, or autonomous loops are modified.

## Proposed first stages
1. Implement a standalone deterministic, fixed-capacity 2D Moore-neighborhood developmental update and structural tests, without claiming trained capability.
2. Add a pure feedback encoder: success => regular beat train; failure => irregular noise. Feed temporal samples only through explicit local input; do not expose outcome bits or hidden labels.
3. Validate deterministic replay, input locality, no hidden capacity growth, reverse/no-feedback/sham controls and equal compute/data budgets.
4. Freeze a separate complete preregistration (seeds, split, task, data hashes, thresholds, budgets and evaluator) **before** primary learning runs. No primary run is authorized by this note.

## Scientific interpretation
Adapter unit-test PASS is not learning improvement. Even if trained behavior improves, distinguish predictable structure, noise amplitude, valence, information leakage, and reward equivalence through controls. Report negative results unchanged.

## Authority
Research-only source branch. No production, promotion, scheduler, queue, owner, or protected first-use authority.

## Development-only negative-control interface (G32)

`feedback_control(outcome, condition, length, seed)` is environment-side and exposes *only* temporal samples to `LocalDevelopment.step`. Conditions are `mapped` (success beats/failure noise), `reversed` (mapping swapped), `sham` (seed parity selects beats/noise independent of outcome; use identical seeds for paired outcomes), and `no_feedback` (all-zero samples). All conditions use the same frame count and the same fixed-capacity local-update call budget. The sham parity scheme is a provisional diagnostic, not independently randomized task data. No feedback condition grants the learner a direct outcome-bit input.

Focused tests exercise exact mapping, inverse mapping, outcome-blind sham, zero input, guard rejections, locality, fixed dimensions, and repeatability. These are structural development checks only; they do not establish improved learning, matched signal energy, scientific transfer, or DG-1 native integration.

**Native interface audit:** The executable here is `LocalDevelopment.step(state, sensory)`, a provisional fixed-capacity 2D fixture; the accepted DG-1 substrate still requires separately verified native integration. `PublicCausalCells` is a conventional comparator. Do not represent either as an accepted DG-1 cognitive result. A prospective primary experiment still requires an independently frozen task/evaluator, balanced paired seeds, signal-amplitude and valence controls, complete compute accounting, source custody, thresholds and authorization. No primary or held-out evaluation is enabled by this change.


## G33: isolated shared-neural-rule DG-1A candidate and native interface

The bounded `native_dg1a.py` is a **new development-only prototype** with 16 state channels per cell, a 3x3 Moore neighborhood, one shared 398-parameter neural genome, local sensory input, residual developmental updates, and a transparent supervised *toy* gradient step. Its task and alive channels are immutable in this prototype. Fixed cells, bounded weights, bounded sensory, and no model calls prevent implicit architecture/capacity growth. Neither `LocalDevelopment` nor `PublicCausalCells` is relabeled as accepted DG-1 cognition.

The focused tests verify identical-seed byte-level deterministic structure, local-only influence, fixed shapes, finite hard input guards, and a one-step supervised reduction on a declared synthetic DEV target (with unchanged parameter count). That proves a trainable interface exists in a bounded prototype; it does **not** prove autonomous acquired cognition, valid beat/noise training benefit, integration into the accepted native DG-1 lineage, or reproducible primary science.

`g33_prereg_draft.json` documents the still-missing primary source/cohort/evaluator/custody/threshold identities and exact required controls. `primary_execution_allowed=false`; it is *not* a frozen or admitted preregistration. A separately authorized authentic primary run requires source custody, real task definition, primary thresholds, input dataset hashes, independent evaluator and matched signal amplitude/resource controls. No held-out use, production activation, or accepted-state update is permitted.


## G34: equal-marginal, equal-energy temporal and polarity controls (development only)

`matched_feedback.py` provides separately bounded **development-only** alternatives to the earlier unequal-energy beat/noise encoder. With the same frozen length and seed, the periodic sequence and deterministic shuffled sequence have an *identical multiset* of signed values (+1, -1, 0), zero mean, identical L1 norm and L2 energy, identical peak amplitude and identical developmental frame count. The periodic schedule is (+1, 0, 0, -1) repeated; the irregular sequence is a pinned xorshift/Fisher-Yates permutation of those same values with an explicit nonperiodic fallback. This is a structural test of temporal pattern rather than an experimental result.

In addition to mapped/reversed and outcome-blind paired-seed sham, `polarity_flip` reverses every sign while preserving the amplitude histogram, and `phase_shift` rotates each waveform by one frame. These are **diagnostics** for phase/polarity confounds; they do not by themselves isolate reward valence in a trained system. `no_feedback` intentionally retains the number of update calls but has zero input energy; **do not include it in equal-energy comparisons**. The earlier `feedback()`/`feedback_control()` functions remain unchanged for historical comparability and are not claimed energy matched.

G34 tests verify signed-histogram/energy parity, temporal nonperiodicity, pairwise inversions, independent sham, invalid input failure, identical update counts/local channels for both bounded developmental fixtures, and unmodified research authority. Resource accounting and scientific evaluation remain outside these unit tests.

The `g33_prereg_draft.json` status stays `INCOMPLETE_NOT_FROZEN`, with explicit missing source/custodian/task/evaluator/cohort/threshold fields and `primary_execution_allowed=false`. Authentic first-use still needs a frozen task, dataset/labels, independent source custody, matched conventional controls and complete all-in compute/energy accounting, acceptance rules and separate authorized research execution.


## G35: prospective task/custody admission preflight — still NO-GO

`g35_candidate.json` and `g35_preflight.py` specify a *proposed*, not frozen, deterministic 4×4/16-channel DG-1A diagnostic design. Its two disjoint planned seed groups (eight seeds each) and paired-outcome intention are scheduling constraints **not authentic FIT/TRANSFER task cohorts or labels**. Every feedback condition receives exactly 16 frames, 256 cell updates, zero primary training updates, and the same fixed 398-parameter shared genome. The energy-matched comparison explicitly excludes zero-energy `no_feedback`.

The validator emits a content digest, missing evidence list and fixed analytic resource proxy: 256 cell updates, 1,600 neighborhood visits and 25,600 neighborhood-channel reads per case, plus 2,048 logical state and 3,184 logical genome float bytes. These are **algorithmic proxies**, not observed wall time, FLOPs, actual Python resident memory, total energy cost or scientific equal-resource proof. All-in runtime accounting and proper matched conventional baselines remain missing.

The preflight **fails closed** for schema, cohort overlap, condition/budget, external hash, authority or threshold drift. Even if every external evidence field is populated with correctly formatted declarations, it returns `STRUCTURE_ONLY_EXTERNAL_AUTHENTICITY_UNVERIFIED` and `primary_execution_allowed=false`: a manifest cannot authenticate itself or become an independent scientific custodian. The G33/G34 preregistration is unchanged and `INCOMPLETE_NOT_FROZEN`.

Required before first-use: original independent task source/license and immutable digest, separately sourced evaluator and frozen label/task cohort manifests, external prediction-seal and label-release receipts, predeclared thresholds, actual compute/resource evidence, independent authority review and explicit primary execution authorization. No protected data were used to create this planning-only candidate; this is *not* primary qualification.
