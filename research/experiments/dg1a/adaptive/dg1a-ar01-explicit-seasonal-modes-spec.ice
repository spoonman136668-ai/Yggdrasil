TITLE: DG-1A-AR-01 — Explicit Seasonal Modes
DATE: 2026-09-18
STATUS: PREREGISTERED — UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT_SYNTHETIC_CONTROL: dg1a-ar01-seasonal-context-synthetic-control.ice
PARENT_ENCODING_AUDIT: dg1a-ar01-context-encoding-ablation.ice

QUESTION
Can one compact shared local developmental engine express distinct organismal regimes when given only a two-scalar environmental season signal, while an exactly parameter-count-matched fixed-rule control cannot?

PRIMARY CLAIM UNDER TEST
A single fixed set of shared local weights can support multiple context-dependent developmental policies without assigning a separate neural network to each cell and without changing globally stored weights during the organism lifetime.

THIS EXPERIMENT DOES NOT TEST
- endogenous mode inference;
- heritable per-cell micro-genomes;
- role switching;
- adversarial ecology;
- lifetime weight plasticity;
- meta-learning;
- STAB-18-R1 causal pruning.

R1 ISOLATION
STAB-18-R1 remains frozen, unexecuted, and scientifically prior.

AR-01:
- must not modify R1 source/specification;
- must not execute the canonical R1 seed-0 / 200-iteration run;
- must not consume or relabel R1 scientific gates;
- must not use AR-01 outcomes to alter R1 before R1 is independently resolved.

ARCHITECTURAL BASE
Preserve the compact Yggdrasil local-developmental design:

state channels:
16

visible channels:
0..3

LIFE4:
channel 4

shared local neural rule:
one network shared by all cells

hidden width:
128

fire rate:
0.5

alive threshold:
0.1

No cell receives a private neural network.

AR-01 adds only:
two exogenous environmental context scalars.

The two scalars are broadcast identically to every cell and concatenated into the shared local update rule's input after the existing local perception representation.

No persistent state channel is reserved exclusively for the external mode signal.

No globally stored network weight may change during evaluation/lifetime rollout.

FROZEN SEASON ENCODING
Use six discrete phase points separated by 60 degrees.

EXPANSION:
phi = 0 degrees

CONSOLIDATION:
phi = 60 degrees

MAINTENANCE:
phi = 120 degrees

REPAIR:
phi = 180 degrees

DORMANCY:
phi = 240 degrees

REACTIVATION:
phi = 300 degrees

Broadcast context:
C0 = cos(phi)
C1 = sin(phi)

No interpolation claim is permitted in AR-01.

No alternate context encoding may be substituted after the first real AR-01 training run.

PARAMETER-COUNT-MATCHED CONTROL
Both candidate and control use the exact same network architecture including the two additional context input columns.

CONTEXT candidate:
receives the correct CIRCLE-2 phase signal.

FIXED control:
receives:
C0 = 0
C1 = 0
for all cells and all steps.

Therefore:
trainable parameter count is exactly identical.

The fixed control is not allowed to remove the two input columns or reclaim those parameters elsewhere.

SECONDARY NON-GATING CONTROL
If implementation cost is trivial, a scrambled-phase diagnostic may be run with the same architecture and marginal context distribution but phase labels independently permuted from the actual mode.

This diagnostic is NON-GATING.
It cannot replace the fixed zero-context control.

PAIRING / RANDOMNESS
Run paired candidate/control seeds:

0
1
2
3
4

Within each seed pair:
- identical weight initialization before context-dependent learning diverges;
- identical state-pool initialization;
- identical training minibatch order;
- identical damage schedule;
- identical NCA stochastic fire schedule;
- identical mode/scenario schedule;
- identical evaluation RNG streams.

Mode/scenario sampling must use a pseudorandom domain separate from NCA fire-mask randomness.

The candidate/control pair differs only in whether the correct CIRCLE-2 context is exposed to the local update rule.

TRAINING ENVELOPE
Fresh AR-01 models.
Do not initialize from a scientifically executed R1 model.

device:
cpu

precision:
float32

phenotype:
40 x 40

target:
radius-6 disk

target foreground cells:
113

state channels:
16

hidden width:
128

fire rate:
0.5

max NCA steps:
256

iterations:
200

learning rate:
0.001

batch size:
8

pool size:
64

gradient clip norm:
1.0

hidden L2:
0.00001

The exact same envelope applies to candidate and control.

MODE TRAINING PRINCIPLE
AR-01 must contain genuine matched-state policy conflicts.

It is not sufficient to assign a unique state distribution to every mode, because a fixed rule could then infer mode from state alone.

At least the following cloned-state pairs must occur during training:

PAIR A — UNDERGROWN
same undergrown snapshot:
EXPANSION branch should continue target-directed development;
DORMANCY branch should preserve/quiesce.

PAIR B — DAMAGED
same lesioned mature snapshot:
REPAIR branch should restore target-directed structure;
DORMANCY branch should remain quiescent rather than entering an active repair program.

PAIR C — DORMANT INCOMPLETE
same dormant incomplete snapshot:
REACTIVATION branch should resume target-directed development/recovery;
continued DORMANCY branch should remain quiescent.

This makes external context causally necessary for perfect policy selection.

MODE OBJECTIVES

EXPANSION
Starting state:
seed or undergrown clone.

Desired regime:
rapid target-directed development.

Primary objective:
reduce visible target loss.

CONSOLIDATION
Starting state:
late-development or deliberately rough/overgrown-but-finite clone.

Desired regime:
reduce target error and unnecessary turnover without uncontrolled new expansion.

Primary objectives:
reduce visible target loss;
reduce active-cell turnover relative to EXPANSION.

Do not introduce a new fixed occupancy target.

MAINTENANCE
Starting state:
mature intact clone.

Desired regime:
preserve morphology and viability with low drift.

Primary objectives:
low visible drift;
bounded LIFE4 occupancy;
low turnover.

REPAIR
Starting state:
mature clone after the declared lesion.

Desired regime:
target-directed recovery.

Primary objectives:
bounded recovery fraction;
visible target recovery;
finite state;
bounded occupancy.

DORMANCY
Starting state:
cloned undergrown, mature, or damaged state.

Desired regime:
suppress active developmental change while preserving the current state sufficiently for later reactivation.

Primary objective:
trajectory state-preservation / quiescence.

Dormancy is not allowed to be implemented as:
- stopping the simulator externally;
- setting fire rate to zero externally;
- bypassing the local neural rule;
- freezing tensors outside the shared update rule.

The organism must receive ordinary NCA updates and learn to emit near-quiescent local updates under DORMANCY context.

REACTIVATION
Starting state:
a state that has spent a declared interval in DORMANCY.

Desired regime:
resume target-directed development or repair.

Primary objectives:
recover from incomplete/damaged dormant state;
return to a viable target morphology;
demonstrate that dormancy did not permanently destroy developmental competence.

TRAINING LOSS BOUNDARY
Mode-specific supervision may select among:
- visible target morphology loss;
- current-state preservation loss;
- existing viability-band penalties;
- turnover/update-magnitude penalties.

No loss may:
- encode absolute target coordinates into the local rule;
- provide per-cell target labels;
- provide a different network per mode;
- directly write hidden state;
- change globally stored network weights during evaluation.

Before first real training execution, the implementation must freeze exact coefficients and normalization for every active loss term in this file or a child implementation-contract .ice committed on dg1a-ar.

No coefficient may be tuned after seeing seed-0 AR-01 results.

PRIMARY EVALUATION — LIFECYCLE
For each paired seed:

1. EXPANSION
96 steps from canonical seed.

2. CONSOLIDATION
64 additional steps.

3. MAINTENANCE
96 additional steps.

4. FIRST LESION
apply the standard 0.6 x 0.6 evaluation lesion.

5. REPAIR
96 steps.

6. DORMANCY
96 intact steps after repair.

7. DORMANT DAMAGE
while still in DORMANCY, apply a second fixed 0.4 x 0.4 lesion.

8. CONTINUED DORMANCY
32 steps.

9. REACTIVATION
96 steps from that damaged dormant state.

This schedule is held fixed across candidate/control pairs.

MATCHED-STATE COUNTERFACTUAL EVALUATION
Use cloned snapshots and identical future stochastic update streams.

TEST A — EXPANSION VS DORMANCY
same undergrown snapshot
32 steps

TEST B — REPAIR VS DORMANCY
same lesioned mature snapshot
32 steps

TEST C — REACTIVATION VS CONTINUED DORMANCY
same damaged dormant snapshot
32 steps

For each clone compute target-loss improvement:

Improvement =
    (InitialVisibleLoss - FinalVisibleLoss)
    / max(InitialVisibleLoss, 1e-8)

Define contextual contrast:

Contrast(mode, dormancy) =
    Improvement_mode
    - Improvement_dormancy

A fixed zero-context control presented with the same cloned state and identical stochastic stream has no mode information and should therefore have near-zero contrast except numerical nondeterminism.

PRIMARY AR-01 DISCRIMINATION GATES
The AR-01 candidate is classified POSITIVE only if ALL are true.

GATE 1 — PARAMETER MATCH
candidate trainable parameter count
==
fixed-control trainable parameter count

GATE 2 — EXPANSION CONTEXT CONTRAST
Across seeds 0..4:

median candidate
Contrast(EXPANSION, DORMANCY)
>= 0.25

and at least 4/5 seeds are positive.

GATE 3 — REPAIR CONTEXT CONTRAST
Across seeds 0..4:

median candidate
Contrast(REPAIR, DORMANCY)
>= 0.25

and at least 4/5 seeds are positive.

GATE 4 — REACTIVATION CONTEXT CONTRAST
Across seeds 0..4:

median candidate
Contrast(REACTIVATION, DORMANCY)
>= 0.25

and at least 4/5 seeds are positive.

GATE 5 — CONTROL NON-SEPARATION
For each of the three matched-state tests:

absolute median fixed-control contextual contrast
<= 0.05

The control receives zero context in both cloned branches.

GATE 6 — DORMANCY QUIESCENCE
During the 96-step intact DORMANCY phase:

candidate median per-step mean absolute state update
<= 0.50 x
candidate median per-step mean absolute state update during MAINTENANCE

and visible morphology must not catastrophically drift.

GATE 7 — DORMANCY IS REVERSIBLE
After dormant damage and 32 steps of continued DORMANCY:

switching to REACTIVATION must produce a positive target-loss improvement in at least 4/5 seeds.

At 96 reactivation steps:
final bounded RecoveryFraction
> 0.4230230485
in at least 4/5 seeds.

GATE 8 — VIABILITY / OCCUPANCY SAFETY
Where the organism is expected to be mature:

113 <= LIFE4 hard-live count <= 800

No new narrower occupancy target is introduced.

GATE 9 — MORPHOLOGY SAFETY
At end of MAINTENANCE and end of REACTIVATION:

global visible MSE
<= 0.0361635
in at least 4/5 candidate seeds.

GATE 10 — FINITE
No nonfinite state in training or evaluation for any candidate/control run used in classification.

FALSE MODE LEAKAGE DIAGNOSTICS
Measure, do not hide:

- REPAIR context on an intact mature organism;
- EXPANSION context on an already mature organism;
- DORMANCY context on a damaged organism;
- MAINTENANCE context on an undergrown organism.

Record:
- visible loss;
- LIFE4 occupancy;
- turnover;
- update magnitude;
- births/deaths;
- runaway growth;
- collapse.

A candidate that merely maps each mode signal to indiscriminate growth/suppression is not a successful adaptive rule.

MEASUREMENTS
Record per phase and per seed:

- visible morphology MSE;
- LIFE4 hard-live occupancy;
- births;
- deaths;
- total turnover;
- mean absolute state update;
- persistence drift;
- damage effect;
- bounded RecoveryFraction;
- stable T50 where applicable;
- switching latency;
- contextual contrast;
- false mode leakage;
- reactivation success.

SWITCHING LATENCY
For a declared mode switch, define switching latency as the first step at which the destination-mode diagnostic remains inside its destination criterion for 8 consecutive steps.

Destination criteria must be frozen in the implementation-contract .ice before execution.

INTERPRETATION RULE
A positive AR-01 result supports:

one shared local rule
+
tiny explicit environmental context
->
multiple learned developmental regimes

It does NOT support:
- endogenous adaptive intelligence;
- autonomous repair-mode inference;
- evolution;
- heritable specialization;
- meta-learning.

A negative AR-01 result means the present architecture/training scheme did not exploit the explicit mode signal under the frozen test.

Do not rescue a negative result by tuning context encoding, gates, or coefficients post hoc.

LITERATURE ANCHOR
Prior work establishes that NCA behavior can be conditioned by compact goals or signals.

AR-01 differs by requiring:
- explicit parameter-count matching;
- developmental regime switching rather than only target identity;
- dormancy/reactivation;
- matched-state policy conflicts;
- repair-versus-dormancy discrimination.

PRIOR SYNTHETIC EVIDENCE
The preceding synthetic control was positive.

That evidence is only:
SYNTHETIC

It justifies execution of AR-01.
It is not part of AR-01 scientific classification.

STATUS
PREREGISTERED
UNEXECUTED

NEXT IMPLEMENTATION STEP
Implement the minimum two-scalar context path and exact dummy-context control on dg1a-ar.

Before any real AR-01 training run:
1. add deterministic acceptance tests for context plumbing and parameter equality;
2. freeze exact mode-specific loss coefficients;
3. freeze switching-latency destination criteria;
4. verify identical candidate/control RNG schedules;
5. verify R1 files and canonical dg1a-p0 head remain unchanged.

PROVENANCE
evidence_class = PREREGISTRATION
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
adaptive_rule_mode = explicit_seasonal_context
context_encoding = circle_2
context_dimensions = 2
paired_seeds = 5
