TITLE: DG-1A-P0-STAB-18-R1 — Auxiliary Latent Injury-Information Diagnostic Preregistration
DATE: 2026-09-18
STATUS: AUXILIARY OBSERVATIONAL PREREGISTRATION — NON-GATING
TRACK: DG-1A
PARENT: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Freeze a non-gating latent-state measurement protocol BEFORE the canonical STAB-18-R1 result exists.

The canonical scientific decision remains determined ONLY by the already frozen 14 gates.

This auxiliary protocol exists to answer a different question after execution:
what latent information organization accompanies maintenance and injury in the trained R1 organism?

THIS RECORD DOES NOT
- alter R1 training;
- alter R1 evaluation;
- add or remove any scientific gate;
- change pass/fail classification;
- change source, seed, coefficient, horizon, floor, ceiling, lesion, or loss;
- authorize a second training run;
- permit post-hoc parameter tuning.

ORDER OF OPERATIONS
After and only after:
1. mandatory historical acceptance is fully green;
2. the single canonical seed-0 R1 candidate is trained;
3. the frozen canonical evaluation is completed;
4. all 14 preregistered gates are applied and recorded;

then the saved R1 model/checkpoint may receive this additional read-only observational evaluation.

The auxiliary diagnostic cannot retroactively change the canonical classification.

FROZEN OBSERVATION ENVELOPE
Use the canonical trained R1 checkpoint.

Device:
CPU

Precision:
float32

Grid:
40 x 40

State channels:
16

Visible:
0..3

LIFE4:
4

Other hidden:
5..15

Observation trajectories:

A. UNDAMAGED MAINTENANCE
- grow from seed for 96 canonical steps;
- continue for 96 additional persistence steps;
- record the complete state at every step.

B. CANONICAL DAMAGE / RECOVERY
- grow from seed for 96 canonical steps using the canonical evaluation seed/RNG contract;
- apply the frozen canonical 0.6 x 0.6 center lesion;
- record pre-lesion and immediate post-lesion state;
- continue exactly 96 recovery steps;
- record complete state at every step.

No new damage geometry is introduced in this diagnostic.

RNG DISCIPLINE
The auxiliary trajectories must use explicit fresh deterministic generators.

They must not mutate or replace the canonical scientific evidence.

Record exact generator seeds used.

The observational analysis may be repeated deterministically on the same saved checkpoint because it does not consume a new training candidate.

PRIMARY RAW TELEMETRY
For every recorded step and state channel:

1. state mean;
2. state RMS;
3. state standard deviation;
4. update RMS:
   RMS(X_t - X_{t-1});
5. fraction of cells with absolute update above:
   1e-4,
   1e-3,
   1e-2;
6. lag-1 temporal autocorrelation where defined;
7. horizontal/vertical nearest-neighbor spatial correlation where defined.

For LIFE4 additionally:
- hard alive count;
- hard birth count from t-1 to t;
- hard death count from t-1 to t;
- turnover = births + deaths;
- births and deaths localized by distance to lesion boundary in recovery.

VISIBLE TELEMETRY
For alpha channel 3:
- hard alpha-active count at threshold 0.1;
- birth/death/turnover;
- update RMS;
- spatial correlation.

Maintain LIFE4 and visible-alpha telemetry separately.

LESION RESPONSE Z-SCORES
Construct maintenance reference distributions from the final 64 steps of undamaged persistence.

For each channel and raw scalar telemetry above:
MaintenanceMean
MaintenanceStd

For each post-lesion recovery step:
Z =
(value - MaintenanceMean)
/
max(MaintenanceStd, epsilon)

epsilon must be fixed only for numerical divide-by-zero handling and must not be tuned to results.

Use:
epsilon = 1e-12

This is descriptive, not a gate.

LOCAL REGION PARTITION
Using the canonical lesion rectangle only for ANALYSIS, partition surviving/recovery cells by Chebyshev distance from the lesion rectangle:

R0:
inside lesion footprint

R1:
distance 1

R2:
distance 2

R3_4:
distance 3..4

R5PLUS:
distance >=5

This geometry is analysis metadata only and is not supplied to the NCA.

Record per-channel update RMS and mean state by region and recovery step.

The purpose is to detect whether injury produces:
- local correction;
- distal perturbation propagation;
- or no differentiated response.

INJURY DISCRIMINABILITY
Define two labeled observational sample classes:

MAINTENANCE samples:
local state/perception observations drawn from the final 64 undamaged persistence steps.

INJURY samples:
local state/perception observations drawn from recovery steps 1..16.

Do not rebalance by deleting hard examples.

For each state channel individually:
estimate a simple scalar injury discriminability using ROC AUC from that channel's local update magnitude and local state-change magnitude.

Report:
- every channel AUC;
- mean hidden-channel AUC;
- best hidden-channel AUC;
- LIFE4 AUC;
- visible-alpha AUC.

Do not select a "best repair channel" as a new candidate from this one model.

POOLED MULTI-CHANNEL DISCRIMINABILITY
Fit a linear discriminant using ONLY the observational samples:

features:
per-channel local state-change magnitudes for channels 0..15.

Validation:
deterministic temporal block split:
- earlier half of eligible time blocks for fitting;
- later half for held-out scoring.

Use a shrinkage covariance estimator or equivalent numerically stable linear discriminant.

Report held-out pooled ROC AUC.

Primary ensemble diagnostic:
EnsembleGain =
PooledAUC - BestSingleChannelAUC

Interpretation:
large positive EnsembleGain means several channels contain useful injury information not captured by the single best channel.

It does NOT by itself prove PID redundancy.

NOISE-COVARIANCE DIAGNOSTIC
From maintenance samples only:
compute the 12x12 hidden-state-change correlation matrix for channels 4..15.

Also report:
- eigenvalues of covariance;
- participation ratio:
  (sum lambda)^2 / sum(lambda^2);
- equal-weight effective cue count diagnostic:
  N_eff =
  K^2 / sum_{i,j} Corr(i,j)
  where defined and positive.

IMPORTANT:
N_eff is a NOISE-correlation diagnostic.
It is not sufficient evidence of injury redundancy.

SYNTHETIC VALIDATION OF THE METRIC SET
Before this preregistration, the measurement combination was validated on four known synthetic information structures using 12 channels.

All synthetic channels used equal unit-noise scale and injury signal shift = 1 where applicable.

REGIME A — INDEPENDENT REDUNDANT CUES
Every channel carries the same injury signal.
Channel noises independent.

Observed:
- mean single-channel AUC ~0.7601
- best single-channel AUC ~0.7708
- pooled AUC ~0.9932
- ensemble gain ~+0.2224
- covariance N_eff ~12.14

Correct reading:
many individually informative cues + large pooling gain + independent noise.

REGIME B — DUPLICATED SIGNAL AND DUPLICATED NOISE
Every channel carries the same injury signal and the same noise realization.

Observed:
- mean single AUC ~0.7612
- best single AUC ~0.7612
- pooled AUC ~0.7612
- ensemble gain 0
- N_eff = 1

Correct reading:
raw duplication without reliability gain.

REGIME C — ONE USEFUL CHANNEL + ELEVEN IRRELEVANT CHANNELS
Only one channel carries injury signal.
Other channels are independent noise.

Observed:
- mean single AUC ~0.5208
- best single AUC ~0.7592
- pooled AUC ~0.7594
- ensemble gain ~+0.00017
- N_eff ~11.91

CRITICAL RESULT:
N_eff alone would falsely look "high-dimensional" here.

Therefore no future interpretation may claim robust redundant injury evidence from covariance/effective-rank alone.

REGIME D — THREE CORRELATED MODULES
12 channels in 3 modules of 4.
Within-module noise correlation approximately 0.8.
Modules retain largely independent noise.
Every channel carries injury signal.

Observed:
- mean single AUC ~0.7628
- best single AUC ~0.7667
- pooled AUC ~0.9095
- ensemble gain ~+0.1429
- N_eff ~3.53

Correct reading:
modular redundant evidence with meaningful but not maximal reliability gain.

REQUIRED INTERPRETATION COMBINATION
A future R1 latent result may be described as redundancy-like injury evidence only if the pattern includes BOTH:

1. multiple channels individually above chance on injury discrimination;
AND
2. positive held-out ensemble gain over the best individual channel.

Noise covariance/effective rank is then used to interpret whether the evidence has diverse error modes.

Do not use one metric alone.

MAINTENANCE-TO-REPAIR REGIME COMPARISON
Compare the same metrics between:
- final 64 undamaged maintenance steps;
- recovery steps 1..16;
- recovery steps 17..48;
- recovery steps 49..96.

Questions:
A. Does latent update magnitude leave maintenance baseline after lesion?
B. Is response spatially concentrated near lesion or distributed?
C. Does injury discriminability recruit more channels early in repair?
D. Does pooled ensemble gain increase during early recovery?
E. Does the response return toward maintenance statistics by late recovery?

These are observational questions, not pass/fail gates.

HYPOTHESIS BRANCHES
H1:
R1 passes maintenance-related gates and early recovery shows multi-channel injury information with positive ensemble gain.
Interpretation:
repair information exists; recruitment failure may lie downstream of injury detection.

H2:
R1 improves maintenance but early recovery shows little channel-level injury discriminability.
Interpretation:
injury-state representation is likely absent or weak.

H3:
many channels respond but EnsembleGain ~0 and maintenance noise is highly correlated.
Interpretation:
duplicated/noisy shared mode rather than robust distributed injury evidence.

H4:
several channels individually informative and EnsembleGain materially positive.
Interpretation:
supports a distributed multi-cue injury representation.

H5:
strong early response that does not return toward maintenance.
Interpretation:
possible failure of repair-state termination/homeostasis.

None changes canonical R1 classification.

NO PID CLAIM
Do not call this protocol a direct measurement of:
- synergy;
- redundancy;
- unique information
in the formal partial-information-decomposition sense.

Those require a separately justified estimator and sample-size analysis.

This protocol measures:
- discrimination;
- ensemble gain;
- covariance structure;
- spatial/temporal response.

LITERATURE RELATION
The protocol is motivated by 2026 GNCA reports of:
- structured hidden fluctuations;
- distributed repair information flow;
- a resting-to-repair change in information organization.

The Yggdrasil analysis remains independent and must report its own measurements.

DURABLE OUTPUT
After the canonical R1 run exists, if this diagnostic is executed, create:
research/experiments/dg1a/dg1a-p0-stab18-r1-latent-injury-diagnostic-result.ice

and machine evidence containing:
- exact checkpoint hash;
- exact analysis code revision;
- full scalar tables;
- covariance/eigenvalue arrays;
- all AUCs;
- temporal-region summaries.

No result file exists yet.

PROVENANCE
evidence_class = AUXILIARY_OBSERVATIONAL_PREREGISTRATION
canonical_scientific_gate = false
new_training_run = false
written_before_canonical_r1_result = true
