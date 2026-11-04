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


## G36 — original-source custody inspection boundary (NO-GO)

A read-only search of the current original Yggdrasil PR #719 and repository records found no authenticated G36 original task source, evaluator, independently admitted FIT/TRANSFER cohort manifests, prospective custodian, prediction seal, label release, or frozen scientific thresholds. The nine slots in `g36_evidence_index.json` remain **null** rather than invented or retroactively asserted.

`g36_originals.py` is a bounded offline **metadata-receipt integrity verifier**, not a scientific authority. It checks that externally supplied original receipt files exist under an isolated `originals/` directory, match declared SHA-256 bytes, have pinned source references and strictly claimed chronological seal/release order, and reference the exact G35 plan hash. It reads *receipts only*, not protected task labels, and never trains or launches inference. Partial/missing receipts result in `MISSING_ORIGINAL_RECEIPTS`; complete matching bytes would still return `HASHES_MATCH_AUTHENTICITY_UNVERIFIED` because file hashes, source URLs, actor strings, and timestamps cannot independently authenticate their own custody.

Its regression tests use ephemeral **synthetic negative fixtures** under temporary directories solely to exercise tampering, unpinned sources, invalid chronology, authority escalation, and missing evidence. No synthetic fixtures are durable research evidence or replacement historical receipts.

**Current G36 outcome:** engineering hardening may be qualified; independent source and custody admission remains `NO-GO`. The prior G35 plan and G33 draft remain unmodified; neither primary execution nor scientific acceptance is granted. Recovery requires independently original, authorized research-custodian evidence and external adjudication, not another development-only code artifact.

## G38 — synthetic closed-loop native action-learning diagnostic (NOT PRIMARY SCIENCE)

`g38_native_learning.py` is separate from G35 protected task/cohort planning. The 4×4 16-channel, 398-parameter G33 shared neural rule chooses a binary action from a local cell response. A synthetic world reveals ONLY the G34 temporal sensory waveform after the chosen action; no hidden correct-action target, outcome bit, or task labels are passed to the learning update. A FIXED, EXTERNALLY ENGINEERED four-frame periodicity detector operates on fresh local native neural responses to each of the 16 feedback samples; the disclosed G33 supervised-gradient plasticity rule then reinforces or discourages the model's own action. The decoder is NOT learned, and the rule is NOT yet an independent self-organizing learning system.

Development fixture: 16 rounds, 2 synthetic training cues, 16 feedback frames and 8 G33 gradient calls per interaction. The shared genome is retained across interactions; evaluation is made after training on the same cue signs at smaller, unused amplitudes (±0.5). This is simple within-task synthetic interpolation, NOT independently sourced held-out transfer. Controls are mapped/reversed/sham (matched signed histograms, energy and fixed update budget) and zero-energy no_feedback (explicit ablation, not energy-matched). Both the outcome mapping and synthetic fixtures are self-authored and never primary science. No additional autonomous runner, model inference API, new controller or paid service is used.

The code-level result, if qualified, shows only that a tiny cellular policy can update its shared weights using an engineered sensory-reward adapter on a fixed toy binary task. It does NOT prove learned valence, persistent recurrent memory, language, open-world causal intelligence, genuine task transfer, or acceptance of the North Star. All G35/G36 originals and frozen primary requirements remain untouched; G36's nine receipt slots stay null and primary/protected execution remains NO-GO. Preserve both positive and negative control results and exact-HEAD Linux/Windows focused and mandatory full regression.

## G40 — task-rule reversal with adaptation (synthetic diagnostic only)

The source-trained G38 genome is reused or replaced with a fresh seeded genome,
then exposed to a **reversed** binary cue-action relationship. The world alone
knows the correct action. Learner updates receive only selected action,
local cue, and G34 feedback waveform; the decoder remains hand-engineered.
Matched/reversed/sham conditions have the same signed waveform energy and
update budgets. No-feedback and decoder-ablation are zero-energy ablations,
not matched-energy controls.

The test records deterministic before/after target-rule scores for warm/cold
starts without a success threshold or scientific acceptance. Cue magnitudes
remain in the original task family; adaptation is a toy diagnostic, **not
independent held-out transfer**. Primary source admission, G36 original
custody, frozen scientific thresholds and protected evaluation remain NO-GO.

## G41 — deterministic synthetic development score receipt

`g41_score_report.py` produces a JSON receipt for all ten G40
warm/cold by mapped/reversed/sham/no-feedback/decoder-ablation conditions.
It records before/after target-rule accuracy, score changes, fixed adaptation
budgets and a purely descriptive warm-start diagnostic. The test prints
`YGG_G41_DEV_REPORT_JSON=` to both platform qualification logs.
Negative outcomes are reported, **not** treated as engineering failures.
Warm-start has additional earlier source-training cost, so the matched
adaptation-call budgets do not establish matched total training compute.
Original custody, truly independent transfer, learned reward interpretation,
protected first use, and scientific acceptance remain NO-GO/UNVERIFIED.

## G42 — synthetic task-reversal interference trace

`g42_interference.py` replays the existing G40 adaptation mechanics at
round checkpoints 0, 1, 2, 4, 8, 12 and 16 for every condition and both
warm/cold starts. It records source and reversed-target accuracy, Euclidean
genome weight drift, and exact interaction/frame/gradient-call counts. The
independent G40 endpoint comparison rejects implementation drift. A full
machine-readable `YGG_G42_DEV_TRACE_JSON=` receipt is printed by Linux
and Windows focused tests. Negative results do not fail qualification.

The synthetic setup has two cues, a fixed externally engineered periodicity
decoder and **unmatched additional warm-start source training**; it is
neither independent transfer nor learned native reward interpretation.
Protected first use, original custody, and scientific acceptance remain
NO-GO/UNVERIFIED. No production, controller, model API or accepted state changes.

## G43 — bounded synthetic plasticity reset comparison

G43 compares the unchanged G40 warm-start baseline against **two frozen
interventions**, blending 25% or 50% of the original seeded genome into the
source-trained genome before target-rule reversal. This is a deliberately
simple weight-reset mechanism, not a new model architecture. All arms
retain 398 parameters, identical 32 adaptation interactions, 512 waveform
frames, and 256 gradient calls; blend arithmetic is additional overhead
and all arms incur the earlier G38 source pretraining. Controls are mapped,
outcome-blind sham and zero-energy no-feedback, with both source and target
accuracy recorded before/after adaptation.

The `YGG_G43_DEV_PLASTICITY_JSON=` receipt reports all arms including
negative ones. This development-only comparison cannot demonstrate genuine
held-out transfer, independently learned reward interpretation, or a
general cognitive mechanism. G36 custody and protected first-use remain
NO-GO; no acceptance/promotion or controller changes are authorized.

## G44 — context-dependent conflicting rules (synthetic, NOT primary science)

G44 presents two independent local signals to a single, fixed-capacity
398-parameter shared genome: immutable channel-0 task context (+1/-1)
and local sensory cue (+1/-1). The toy world's correct action depends
on the combination; neither individual signal suffices. The action
target stays inside the environment. Learner updates receive chosen
action, local signals, and temporal feedback decoded by the SAME
externally engineered G38 periodicity decoder.

Matched-feedback, sham-feedback, and zero-energy no-feedback conditions
are crossed with visible/masked context. Both context groups and cue signs
have paired frame/update budgets; masked context makes the two conflicting
rules information-theoretically indistinguishable. All arms start from
the same G38-trained genome, with no parameter growth or context-specific
genome copies. The receipt reports both task accuracies and their joint
accuracy; engineering tests DO NOT enforce a positive result.

This is an explicit synthetic context/retention interface test, not
held-out transfer, open-world cognition, learned reward understanding,
or independent scientific evidence. G36 custody remains NO-GO and
production/primary use remains blocked.

## G45 — representation-capacity witness versus supervised optimization

G45 tests the precise G44 conflicting-rule input/output interface without
modifying G33's 398-parameter shared-cell architecture or G44's feedback
learning. A transparent, **hand-constructed, not learned** four-hidden-unit
genome demonstrates a possible context/cue conjunction if it satisfies the
four balanced sign pairs. A separate, limited supervised training probe
starts from seeded or G38-trained genomes and trains visible/masked context
on the same four explicitly synthetic answer labels for 16 rounds and
8 gradient calls per pair. Masked context cannot distinguish opposing rules.
Novel cue magnitudes of 0.5 are *within-family interpolation only*.

The independent report `YGG_G45_DEV_REPRESENTATION_JSON=` includes all
positive and negative results without elevating supervised labels into
native reward comprehension. A hand-built witness is evidence of possible
*representation*, not acquisition or autonomous learning. Frozen G36
custody, independent transfer and scientific acceptance remain NO-GO.

## G46 — bounded optimization diagnostic (synthetic only)

G46 holds the G45 398-parameter architecture, four task/context pairs,
16 training rounds, eight gradient calls per pair and synthetic target
labels fixed. It compares three predeclared arms: the exact G45 baseline
(learning rate 0.5, alternating forward/reversed order); interleaving
context per cue at the same rate; and baseline order at learning rate
0.1. Seeded and G38-pretrained starts and visible/masked context remain
crossed. It records balanced task accuracy, within-family interpolation,
and mean squared synthetic-target error at rounds 0,4,8,16, plus local
one-update response coupling across opposing contexts. Neither a
hand-built witness nor a change to G44 reward learning is used to train.

The unchanged G45 baseline genome must replay exactly. Negative results
are reported without a performance PASS threshold. Every arm has the
same gradient-call count, but not necessarily the same computational
cost. `YGG_G46_DEV_OPTIMIZATION_JSON=` publishes the complete diagnostic
in both OS logs. G36 custody, primary science, authentic transfer,
and native reward comprehension remain NO-GO/UNVERIFIED.

## G47 — opposing-context gradient projection (synthetic engineering diagnostic)

G47 adds an **externally engineered** projection of the supervised
gradient update against its conflicting opposite-context gradient. The
projection acts on the existing 398-parameter shared genome; it does not
create context-specific genomes, neurons, or answer tables. Baseline and
projection evaluate both synthetic context gradients per update (same
256 gradient evaluations for 128 updates). Both warm/seeded starts
and visible/masked context controls are included. The baseline must
reproduce the G46 four-round checkpoint. Scores, loss, projection
activation counts, and all failures are retained in
`YGG_G47_DEV_PROJECTION_JSON=`.

Targets for both counterfactual gradients are explicit **synthetic
supervised labels**, and are *not* available in the original feedback
environment. Success would therefore be a diagnostic of update
geometry only, not independent native learning, memory, or genuine
held-out transfer. No primary cohort, model API, controller or
production activation; G36 custody remains NO-GO.
