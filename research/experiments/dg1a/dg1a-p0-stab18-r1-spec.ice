TITLE: DG-1A-P0-STAB-18-R1 — CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP Preregistration
DATE: 2026-09-18
STATUS: PREREGISTERED — NOT YET EXECUTED
TRACK: DG-1A
CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP + FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
CONFIDENCE: MECHANISTICALLY MOTIVATED / SINGLE-CANDIDATE TEST

SUPERSEDES BEFORE EXECUTION
This preregistration supersedes the unexecuted DG-1A-P0-STAB-18 preregistration:
research/experiments/dg1a/dg1a-p0-stab18-spec.ice
preregistration commit:
e6cb795c0bfa7de96400214bb0978878658368c3

The original STAB-18 candidate was NEVER scientifically executed.
It is not a scientific negative.

PRE-EXECUTION DEFECT FOUND DURING ACCEPTANCE REVIEW
The original causal probe helper saved the main torch.Generator state, sampled:
    torch.rand([B,1,H,W], generator=main_generator)
then restored the generator state.

The canonical NCA first future step also samples:
    torch.rand([B,1,H,W], generator=main_generator)
from that restored state for its stochastic fire mask.

Canonical thresholds:
    causal probe: random < 0.25
    NCA fire mask: random <= 0.50

Therefore the original probe field and the first future fire field are the same random field.
Every probed cell is necessarily included in the first-step fire mask.
The causal intervention is consequently correlated with the immediate stochastic update schedule.

Saving/restoring durable RNG state is necessary but not sufficient for a scientifically neutral intervention.
The probe needs a separate pseudorandom domain.

CLASSIFICATION OF ORIGINAL STAB-18
CLOSED UNEXECUTED — ACCEPTANCE-DISCOVERED RNG STREAM ALIASING CONFOUND.

No original scientific result exists.
Do not classify it as success or failure.

QUESTION
Can canonical P0 preserve STAB-16's viable decoupled hidden-life substrate while reducing morphologically redundant support when the causal latent-ablation probe is pseudorandomly domain-separated from the future NCA update schedule?

SCIENTIFIC BASELINE
STAB-16 remains the architectural baseline.

Preserve unchanged:
- visible morphology channels 0..3;
- visible alpha channel 3;
- hidden life channel 4;
- life threshold 0.1;
- FRONTIER-FLOOR-113;
- CEIL-800;
- ATTRACT-16;
- hidden L2 = 0.00001;
- canonical seed-0 envelope;
- all 14 scientific gates.

STAB-17 remains historical compatibility only.
Do NOT carry MATURE-VIS-ANCHOR-R1 into STAB-18-R1.

SCIENTIFIC INTERPRETATION BOUNDARY
The intervention measures dependence of future visible morphology on the removed latent state under the fixed group-level probe.

It does NOT establish:
- uniquely localized causal responsibility for an individual cell;
- a complete mechanistic decomposition of latent computation;
- counterfactual independence outside this fixed intervention.

FIXED CAUSAL MECHANISM
CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

Maturity:
    HardLifeCount >= 113

Probe scope:
    currently hard-live LIFE4 cells only

Fixed probe fraction:
    0.25

Intervention:
- preserve visible RGBA channels 0..3 exactly;
- zero latent channels 4..15 only at probed cells;
- leave unprobed cells unchanged.

Future horizon:
    exactly 16 NCA steps

Visible future loss:
    exact ATTRACT-16 per-sample loss
    = global visible MSE
    + foreground visible MSE
    + background alpha MSE
averaged across exactly 16 future states.

CausalDelta[i] =
    stop_gradient(
        CounterfactualFutureLoss[i]
        - IntactFutureLoss[i]
    )

Classification:
- CausalDelta > 0:
  removal worsened future visible morphology;
  classify probed group as beneficial;
  causal-prune gradient = ZERO.

- CausalDelta <= 0:
  removal did not worsen future visible morphology;
  classify probed group as non-beneficial under this probe;
  apply one-sided straight-through downward gradient only to LIFE4 at probed hard-live cells.

No gradient may flow through CausalDelta itself.

DOMAIN-SEPARATED PROBE RNG — FROZEN CONSTRUCTION
The main training/trajectory torch.Generator is READ ONLY during probe-mask construction.

Let:
    MainStateBytes =
        bytes(main_generator.get_state().cpu().tolist())

Let the fixed ASCII domain tag be exactly:
    DG1A_P0_STAB18_R1_CAUSAL_PROBE_V1

Compute:
    Digest =
        SHA256(
            MainStateBytes
            || ASCII("DG1A_P0_STAB18_R1_CAUSAL_PROBE_V1")
        )

Compute:
    ProbeSeed64 =
        unsigned big-endian integer from Digest[0:8]

Compute:
    ProbeSeed =
        ProbeSeed64 AND 0x7FFFFFFFFFFFFFFF

Construct a temporary torch.Generator on state.device.

Set:
    probe_generator.manual_seed(ProbeSeed)

Then sample exactly:
    ProbeRandom =
        torch.rand(
            [B,1,H,W],
            dtype=state.dtype,
            device=state.device,
            generator=probe_generator
        )

Then:
    ProbeDrop =
        HardAliveLIFE4
        AND ProbeRandom < 0.25

The temporary probe generator is discarded after mask generation.

MANDATORY RNG PROPERTIES
1. main_generator state is bit-identical before and after probe generation;
2. same main_generator state + same tensor shape/device/dtype produces the same ProbeDrop mask;
3. changing main_generator state changes the derived probe pseudorandom domain in deterministic contract fixtures;
4. probe random values are NOT drawn directly from main_generator;
5. probe selection is not constrained to be a subset of the immediate future NCA fire mask;
6. intact and counterfactual future trajectories still use the SAME main-generator starting state and therefore the same stochastic update sequence as each other.

REFERENCE DOMAIN-SEPARATION CONTRACT FIXTURE
CPU torch.Generator manual_seed(1)
probe field shape:
    [1,1,9,9]

Under the frozen derivation above:
    ProbeSeed = 3494006018084941813

For this fixture:
- at least one cell selected by ProbeDrop must have the corresponding first-main-stream fire random value > 0.50;
- ProbeDrop must not equal (FirstMainStreamRandom < 0.25).

This fixture directly prevents regression to the original aliased-stream construction.

NO DURABLE RNG CONSUMPTION
Probe generation consumes ZERO durable state from main_generator.

It may consume arbitrary state from the temporary probe_generator because that generator is local to the probe and discarded.

MATCHED FUTURE TRAJECTORIES
IntactTrajectory:
    16 RNG-neutral future steps from MatureResult
    using main_generator starting state S

CounterfactualTrajectory:
    16 RNG-neutral future steps from CounterfactualStart
    using the same main_generator starting state S

The existing RNG-neutral trajectory helper may be reused if it restores main_generator to S after each trajectory.

No main-generator consuming operation may occur between those matched virtual trajectories.

ONE-SIDED PRUNE GRADIENT
For mature samples with at least one probed hard-live cell and CausalDelta <= 0:

Forward term:
    HardProbeFraction =
        ProbedHardLiveCount / HardLifeCount

Straight-through correction:
- direct gradient only through LIFE4;
- only at probed hard-live cells;
- positive derivative so gradient descent pushes LIFE4 downward;
- no direct gradient to visible channels 0..3;
- no direct gradient to latent channels 5..15;
- no direct gradient to unprobed LIFE4 cells.

For beneficial groups:
    exact zero causal-prune gradient.

For immature samples:
    exact differentiable zero contribution.

For mature samples that draw zero probed cells:
    exact differentiable zero contribution.

FULL STAB-18-R1 OBJECTIVE
Static visible morphology
+ ATTRACT-16
+ CEIL-800
+ FRONTIER-FLOOR-113
+ CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP
+ unchanged hidden L2 regularization.

All coefficients remain 1 except the already-frozen hidden L2 coefficient.

NO TARGET-GEOMETRY CELL SELECTION
Target geometry may be used by the frozen visible morphology loss and ATTRACT-16.

Target geometry must NOT select causal probe cells.

VIRTUAL-STATE ISOLATION
Neither intact nor counterfactual virtual future states may enter the state pool.

Only the normal training result may update the pool.

FROZEN LOSS MODE
global_plus_foreground_bg_alpha_attractor_t16_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep

CANONICAL ENVELOPE
seed: 0
device: cpu
precision: float32
phenotype: 40 x 40
target: radius-6 disk
target foreground cells: 113
state channels: 16
hidden channels: 128
fire rate: 0.5
alive channel: 4
alive threshold: 0.1
max NCA steps: 256

training:
- regeneration
- iterations: 200
- learning rate: 0.001
- development steps: 64..96
- batch size: 8
- pool size: 64
- damage probability: 0.5
- training lesion: 0.5 x 0.5
- damage minimum active cells: 16
- gradient clip norm: 1.0
- hidden L2: 0.00001

evaluation:
- growth steps: 96
- persistence steps: 96
- recovery steps: 96
- evaluation lesion: 0.6 x 0.6

SCIENTIFIC GATES — UNCHANGED
Viability / occupancy:
- 113 <= pre-damage active cells <= 800
- 113 <= final recovery active cells <= 800
- 113 <= final persistence active cells <= 800
- max persistence active cells <= 800
- final persistence active-cell drift <= 0

Lesion validity:
- DamageEffect > 0
- RelativeDamageEffect >= 0.10
- ActiveCellRemovalFraction >= 0.10

Recovery:
- stable T50 attained
- final bounded RecoveryFraction > 0.4230230485

Morphology:
- pre-lesion global visible MSE <= 0.0361635
- final persistence global visible MSE <= 0.0361635
- max persistence MSE <= 2 x initial persistence MSE

Finite:
- no nonfinite state during training, intact virtual trajectory, counterfactual virtual trajectory, growth, damage, recovery, or persistence.

MANDATORY IMPLEMENTATION CONTRACTS BEFORE EXECUTION
- preserve the original unexecuted STAB-18 mode unchanged for repository history/compatibility;
- add the R1 loss mode separately;
- domain tag exact;
- SHA256 construction exact;
- first 8 digest bytes interpreted unsigned big-endian;
- 63-bit mask exact;
- reference ProbeSeed contract = 3494006018084941813;
- main RNG state unchanged by probe generation;
- same main RNG state reproduces same probe mask;
- changed main RNG state changes probe mask in fixed test fixture;
- only hard-live LIFE4 cells may be probed;
- fixed fraction = 0.25;
- reference fixture proves at least one probed cell lies outside first fire mask;
- intervention preserves channels 0..3 exactly;
- intervention zeros channels 4..15 only at probed cells;
- unprobed cells unchanged;
- intact/counterfactual future trajectories use identical stochastic update sequences;
- per-sample causal delta detached;
- positive delta produces zero prune gradient;
- zero/negative delta prunes only probed hard-live LIFE4;
- no causal-prune gradient to RGBA or hidden5..15;
- immature batch produces differentiable zero;
- zero-probed mature sample produces differentiable zero;
- normal and resumable implementations remain semantically identical;
- virtual intact/counterfactual states never enter pool;
- frozen config validates;
- runner evidence exposes R1 mode and causal telemetry;
- all historical contracts remain green.

MANDATORY HISTORICAL ACCEPTANCE BEFORE EXECUTION
The pre-existing acceptance closeout remains mandatory:
- STAB-04 / STAB-05 executable replay;
- repaired STAB-15 executable replay;
- STAB-16 / STAB-17 executable replay;
- full combined regression;
- R1 targeted contracts.

No scientific seed-0 execution until all required acceptance is green.

NO POST-HOC TUNING
Do not after observing the canonical result:
- change probe fraction;
- change domain tag or seed derivation;
- change causal delta threshold;
- change prune coefficient;
- change horizon;
- change floor 113;
- change ceiling 800;
- change ATTRACT-16;
- change hidden L2;
- change fire rate;
- weaken gates.

DECISION RULE
Exactly one fresh seed-0 canonical R1 candidate is permitted after acceptance.

Worth widening:
YES only if all 14 preregistered gates pass.

Otherwise:
close negative and classify the observed failure mechanistically without parameter sweep.

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this packet.
