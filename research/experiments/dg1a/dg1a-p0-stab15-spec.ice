TITLE: DG-1A-P0-STAB-15 — LIFE4-DECOUPLE Hidden-Liveness / Visible-Morphology Separation Preregistration
DATE: 2026-09-17
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
CONFIDENCE: ARCHITECTURALLY MOTIVATED / SINGLE-CANDIDATE TEST

QUESTION
Can canonical P0 recover the near-bounded STAB-12 regime while improving morphology and lesion salience if organism liveness is no longer encoded by the same visible alpha channel that is directly supervised as target morphology?

SCIENTIFIC BASELINE
STAB-12 is the baseline:
- visible alpha channel 3 also served as liveness;
- CEIL-800 + ATTRACT-16;
- pre-damage active 857;
- persistence 799 -> 1015 -> 623;
- final recovery active 655;
- positive DamageEffect;
- stable T50 59;
- 5 / 14 gates failed.

STAB-13 and STAB-14 are closed negative and are NOT inherited:
- no TRACE-CEIL-800;
- no BALANCED-HARD-ALLOC.

STAB-14 showed that forcing exact hard living-support overlap with visible target foreground is harmful:
- target TP coverage reached 112.125 / 113;
- FP support rate reached 0.694687;
- pre-damage active 1097;
- persistence 1014 -> 1477 peak -> 1112;
- lesion invalid;
- 11 / 14 gates failed.

EXTERNAL RESEARCH BASIS
Growing Neural Cellular Automata defines visible RGBA channels and uses alpha as a special liveness signal, while hidden channels are free latent signaling state.

Goal-Guided Neural Cellular Automata describes NCA state as target channels, a living channel, and hidden memory channels, demonstrating that a dedicated living channel is a valid NCA formulation rather than a requirement that visible morphology itself encode viability.

Self-Organising Textures reports that hidden channels organize structural and signaling information that is not directly constrained by the visible loss.

Recent developmental-dynamics work likewise reports differentiated hidden-channel organization during GNCA development.

These references motivate the architectural separation only.
They do not determine gates or establish that LIFE4-DECOUPLE will succeed.

SELECTED MECHANISM
LIFE4-DECOUPLE

Exactly one architectural scientific factor is changed:

OLD
visible alpha channel 3 = morphology alpha AND liveness channel.

NEW
visible alpha channel 3 = morphology alpha only.
hidden state channel 4 = liveness channel only.

All remaining state channels retain learned latent semantics.

CHANNEL CONTRACT
state channels: 16

visible morphology channels:
0 = R
1 = G
2 = B
3 = visible alpha

liveness channel:
4 = hidden life

other hidden channels:
5..15

MODEL CONFIG
alive_channel = 4
alive_threshold = 0.1

VISIBLE TARGET
The target remains unchanged.

Target RGBA remains stored only in channels 0..3.
Target channel 4 remains zero and is NOT a liveness target.

Static morphology losses remain restricted to visible channels 0..3.

SEED
The canonical seed remains one center cell.

make_seed_state must initialize the configured alive_channel only:
channel 4 at center = 1.0.

Visible alpha channel 3 begins at 0.0.

Do not separately seed visible alpha.
Do not seed additional hidden channels.

LIVING MASK
NeuralCellularAutomaton.alive_mask must use configured alive_channel = 4.

The existing pre-alive AND post-alive neighborhood masking semantics remain unchanged.

ACTIVE-CELL METRIC
All canonical active-cell counts must use:
state channel 4 > 0.1.

This includes:
- training damage eligibility;
- pre-damage active count;
- post-damage active count;
- recovery active trajectory;
- persistence active trajectory;
- occupancy gates;
- resource active-cell estimate.

TARGET CARDINALITY
The immutable target foreground cardinality remains derived from visible target alpha channel 3:

target foreground = target alpha > 0.1
canonical target foreground cardinality = 113.

This is a morphology cardinality, not a target life-mask requirement.

ATTRACT-16 MATURITY
A sample is mature when:

hard life-channel active count >= target visible-foreground cardinality

i.e.
count(result channel 4 > 0.1) >= 113.

Do not derive maturity from visible alpha in STAB-15.

ATTRACT-16 FUTURE LOSS
Preserve STAB-11 exactly:
- exactly 16 sequential RNG-neutral future steps;
- mature samples only;
- arithmetic mean over future states 1..16;
- future StaticMorphologyLoss =
  GlobalVisibleMSE
  + ForegroundVisibleMSE
  + BackgroundAlphaMSE;
- coefficient = 1.0;
- visible channels only;
- no life-channel target loss.

CEIL-800
Preserve the STAB-12 conceptual constraint:
hard organism occupancy must remain <=800.

But hard occupancy now means:
count(channel 4 > 0.1).

The zero-forward straight-through ceiling correction must:
- count hard life from channel 4;
- derive protected target foreground spatial mask from target visible alpha channel 3;
- supply downward gradient only through currently hard-active life-channel cells located on target-background pixels when hard life count >800;
- supply zero CEIL gradient through target-foreground life cells;
- supply zero CEIL gradient when count <=800.

ceiling = 800
normalization = 800
square excess
coefficient = 1.0

This is the direct semantic translation of CEIL-800 into the decoupled architecture, not a new tuned mechanism.

STATIC ENDPOINT OBJECTIVE
StaticMorphologyLoss =
GlobalVisibleMSE(channels 0..3)
+ ForegroundVisibleMSE(target alpha channel 3)
+ BackgroundAlphaMSE(visible alpha channel 3)

FINAL TRAINING OBJECTIVE
TrainingMorphologyLoss =
StaticMorphologyLoss
+ AttractorTrajectoryLoss
+ FormationLifeOccupancyCeilingLoss

No BALANCED-HARD-ALLOC.
No TRACE-CEIL.

All coefficients remain 1.0.

HIDDEN L2
Preserve the existing hidden-state L2 implementation and coefficient 0.00001 unchanged.

Because channel 4 is now in the hidden slice, LIFE4 receives the same existing hidden L2 pressure as other hidden channels.
Do not exempt it inside STAB-15.

This consequence is preregistered and must not be changed after execution.

DAMAGE
Training and evaluation center lesions must derive their live bounding box from channel 4 > 0.1.

The lesion still zeros all channels inside the selected rectangle.

Training lesion:
center 0.50 x 0.50.

Evaluation lesion:
center 0.60 x 0.60.

VISIBLE MORPHOLOGY EVALUATION
All MSE morphology evaluation remains channels 0..3.

DamageEffect therefore continues to measure visible morphology degradation, while the lesion geometry is determined by organism liveness on channel 4.

NEW HISTORICAL TRAINING MODE
Add exactly one mode:

global_plus_foreground_bg_alpha_attractor_t16_life4_ceil800

Preserve all prior historical modes unchanged.

Do not reinterpret prior modes with channel 4 liveness.

CANONICAL FROZEN ENVELOPE
seed:                     0
variant:                  regeneration
grid:                     40 x 40
state channels:           16
hidden channels:          128
fire rate:                0.5
alive channel:            4
alive threshold:          0.1
training iterations:      200
learning rate:            0.001
development steps:        64..96
batch size:               8
pool size:                64
training damage prob:     0.50
training lesion:          center 0.50 x 0.50
damage minimum active:    16
gradient clip:            1.0
hidden L2:                0.00001
target:                   deterministic radius-6 disk
target visible foreground:113
evaluation growth:        96
persistence:              96
recovery:                 96
evaluation lesion:        center 0.60 x 0.60
model max steps:          256
precision:                float32
sandbox device:           CPU
common morphology metric: global visible-channel MSE

FIXED STAB-15 FACTORS
visible alpha channel:       3
liveness channel:            4
life threshold:              0.1
ATTRACT future horizon:      16
ATTRACT reduction:           arithmetic mean
ATTRACT coefficient:         1.0
life occupancy ceiling:      800
ceiling coefficient:         1.0
hidden L2 coefficient:       0.00001

No alternate life channel, threshold, seed semantics, ceiling, coefficient, hidden-L2 exemption, horizon, or reduction is permitted.

VIABILITY / OCCUPANCY GATES
All counts use life channel 4:
- 113 <= pre-damage active cells <= 800;
- 113 <= final recovery active cells <= 800;
- 113 <= final persistence active cells <= 800;
- maximum active cells anywhere in persistence <= 800;
- final persistence active-cell drift <= 0.

LESION VALIDITY GATES
All morphology terms remain visible RGBA:
- DamageEffect > 0;
- RelativeDamageEffect >= 0.10;
- ActiveCellRemovalFraction >= 0.10.

RECOVERY GATES
- stable T50 attained;
- final bounded RecoveryFraction > 0.4230230485.

MORPHOLOGY GATES
- pre-lesion global visible MSE <= 0.0361635;
- final persistence global visible MSE <= 0.0361635;
- maximum persistence MSE <= 2.0 * initial persistence MSE.

FINITE-STATE GATE
- no non-finite state during training, virtual persistence, growth, damage, recovery, or persistence.

IMPROVEMENT RULE
LIFE4-DECOUPLE is worth widening only if every preregistered gate passes.

Exactly one fresh seed-0 candidate.
No second seed.
No second candidate.
No alternate life channel.
No visible-alpha seeding variant.
No hidden-L2 exemption.
No ceiling or ATTRACT tuning.

IMPLEMENTATION REQUIREMENTS
Before scientific execution:
- add a decoupled maturity helper or equivalent with state life channel separate from target alpha channel;
- add a decoupled life CEIL-800 helper or equivalent with state life channel 4 and target visible alpha channel 3;
- ensure training damage uses model.config.alive_channel;
- ensure evaluation damage and active counts use model.config.alive_channel;
- preserve visible morphology losses on channels 0..3;
- implement exactly one STAB-15 training mode in normal and resumable training;
- preserve original-rollout-only pool updates;
- preserve RNG-neutral ATTRACT trajectory;
- preserve all historical modes unchanged;
- add additive tests for:
  * seed initializes channel 4 and not visible alpha;
  * alive mask uses channel 4;
  * active-cell metric uses channel 4;
  * maturity count uses channel 4 against target-alpha cardinality;
  * CEIL forward count uses channel 4;
  * CEIL target-background mask derives from visible alpha channel 3;
  * CEIL gradient scope matches preregistration;
  * visible morphology loss ignores channel 4 directly;
  * target channel 4 remains zero;
  * lesion geometry follows channel 4;
  * full objective formula;
  * normal telemetry;
  * resumable telemetry;
  * pool isolation;
  * frozen config;
  * runner evidence;
  * historical channel-3 modes remain compatible;
- run complete reconstructed regression with zero failures before scientific execution.

TEST DISCIPLINE
Never disable, skip, comment out, or weaken a failing test.
Fix root cause.
If repair requires changing the preregistered factor, stop and explicitly supersede or close STAB-15.

EXECUTION / PROVENANCE CONTRACT
Before scientific execution:
1. implementation and tests committed;
2. exact GitHub scientific source frozen;
3. complete reconstructed regression zero failures.

If native byte identity remains unavailable:
source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = MEASURED_SANDBOX

Use deterministic single-writer resumable checkpoints.
Never infer progress beyond latest durable checkpoint.

STOP RULES
Stop and record negative immediately if:
- any canonical active-cell path still silently uses visible alpha instead of configured life channel;
- any morphology loss begins supervising life channel 4 as target output;
- target channel 4 is populated;
- seed visible alpha is separately initialized;
- CEIL life count or gradient mask violates the frozen contract;
- non-finite state/loss appears;
- checkpoint/config integrity fails;
- RNG neutrality or pool isolation fails;
- tests cannot be repaired without changing the scientific factor.

DISCRIMINATING INTERPRETATION
If LIFE4-DECOUPLE restores bounded occupancy while materially improving visible morphology and lesion salience, that supports the hypothesis that visible-alpha/liveness conflation was a major structural cause of the P0 bracket.

If liveness collapses while visible morphology cannot persist, hidden life is not adequately sustained under the unchanged objective and hidden L2; do not exempt LIFE4 or tune hidden L2 inside STAB-15.

If life becomes bounded but visible morphology remains poor, liveness conflation was not the dominant morphology seam.

If overgrowth persists on the hidden life channel while visible alpha improves, the occupancy-control problem remains independent of visible morphology and requires a new packet.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling.

Fibonacci remains separate DG-1A-FIB1.

EXECUTION STATE
PREREGISTERED ONLY.
Do not execute until this exact spec is independently read back and branch HEAD independently verified.
