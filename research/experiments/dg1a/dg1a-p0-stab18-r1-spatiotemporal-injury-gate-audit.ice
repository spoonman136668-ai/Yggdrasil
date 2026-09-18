TITLE: DG-1A-P0-STAB-18-R1 — Spatiotemporal Injury-Gate Audit
DATE: 2026-09-18
STATUS: EXPLORATORY SYNTHETIC DETECTOR AUDIT — NO CANDIDATE SELECTED
TRACK: DG-1A
PARENT: WOUND-MEMORY ROBUSTNESS BOUNDARY

PURPOSE
Test whether combining LOCAL temporal persistence with LOCAL spatial consensus can make a wound-memory injury detector robust to structured hidden-state noise without destroying true wound sensitivity.

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- select a future injury threshold, persistence length, component size, or repair mechanism;
- measure real Yggdrasil hidden noise;
- establish an accepted wound detector.

SYNTHETIC REFERENCE
Body:
- 40x40;
- radius-15 disk;
- 709 cells.

True lesion:
- centered 35% bounding-box lesion.

Memory perturbation:
- normalized SupportMemory noise sigma = 0.10;
- spatial correlation scale = 2 lattice cells;
- temporal AR(1)-style correlation rho in:
  0.0, 0.5, 0.9, 0.99.

Each time step:
- evaluate strong local support-loss evidence;
- require K consecutive trigger steps at a cell;
- then require the confirmed sites to belong to an 8-neighbor connected component of at least M cells.

Window:
16 local updates.

Trials:
300 per diagnostic condition.

NOISE-ONLY RESULT — TEMPORAL PERSISTENCE ALONE
Probability of at least one false confirmed site during the 16-step window:

rho = 0.0
- K1: 77.67%
- K2: 0%
- K3: 0%
- K4: 0%

rho = 0.5
- K1: 68.67%
- K2: 3.67%
- K3: 0.33%
- K4: 0%

rho = 0.9
- K1: 52.67%
- K2: 21.0%
- K3: 6.0%
- K4: 2.33%

rho = 0.99
- K1: 45.33%
- K2: 22.67%
- K3: 12.33%
- K4: 6.33%

Interpretation:
temporal confirmation is highly effective against rapidly changing noise but loses discriminating power when the perturbation itself is persistent.

TRUE-LESION SENSITIVITY — TEMPORAL PERSISTENCE ALONE
Mean wound-boundary recall over the same noisy 16-step window:

rho = 0.0
- K1: 92.13%
- K2: 76.34%
- K3: 53.35%
- K4: 30.47%

rho = 0.5
- K1: 89.86%
- K2: 79.39%
- K3: 64.92%
- K4: 48.15%

rho = 0.9
- K1: 80.15%
- K2: 68.65%
- K3: 59.86%
- K4: 51.87%

rho = 0.99
- K1: 72.90%
- K2: 63.22%
- K3: 56.40%
- K4: 49.92%

Every trial through K4 still produced at least some wound detection in these tests, but spatial coverage of the wound ring falls as persistence requirements become stricter.

This demonstrates the expected sensitivity/specificity tradeoff rather than a free robustness gain.

SPATIOTEMPORAL CONSENSUS EXAMPLES
Confirmed trigger sites were additionally required to form a local connected component.

MODERATELY CORRELATED NOISE
rho = 0.5

K=2, component >=5:
- false-detection trials: 0 / 300;
- mean wound-boundary recall: 71.86%;
- 5th percentile wound recall: 50%;
- median first detection: step 2;
- no true-lesion detection misses.

K=3, component >=3:
- false-detection trials: 0 / 300;
- mean wound recall: 60.40%;
- median first detection: step 3;
- no true-lesion detection misses.

Thus a local spatiotemporal gate can cleanly separate this moderate-noise toy while retaining substantial lesion evidence.

HIGHLY CORRELATED NOISE
rho = 0.9

K=2, component >=4:
- false-detection trials: 5.33%;
- mean wound recall: 63.15%;
- median first detection: step 2.

K=3, component >=3:
- false-detection trials: 2.67%;
- mean wound recall: 57.40%;
- median first detection: step 3.

K=3, component >=4:
- false-detection trials: 2.0%;
- mean wound recall: 54.10%;
- median first detection: step 3.

Noise cannot be eliminated here merely by increasing local persistence/cluster requirements without progressively reducing wound coverage.

EXTREMELY PERSISTENT NOISE
rho = 0.99

Representative:
K=3, component >=5:
- false-detection trials: 1.0%;
- mean wound recall: 46.85%;
- some true-lesion trials failed to produce a confirmed component.

This is not a satisfactory detector.

KEY NEGATIVE RESULT
SPATIAL + TEMPORAL CONSENSUS IS NOT SUFFICIENT IN THE GENERAL CASE.

If hidden-state noise can create persistent coherent local deviations comparable to the wound-memory signal, a detector based only on:
- magnitude;
- duration;
- local cluster size

cannot reliably distinguish injury from endogenous latent dynamics.

This is an important stopping rule:
DO NOT convert the current synthetic success into a threshold/persistence/component sweep.

NEXT SCIENTIFIC SEAM
MULTI-CUE LOCAL PREDICTIVE ERROR.

A true canonical lesion coherently destroys:
- LIFE4;
- visible channels;
- all other hidden channels
inside the damaged region.

Ordinary latent fluctuation need not produce the same coherent multi-channel state-transition signature.

A more robust injury state should therefore be based on violation of expected LOCAL DYNAMICS rather than one raw support-memory magnitude.

Candidate research classes, not selected implementations:

1. MULTI-CHANNEL PREDICTION ERROR
Surviving cells learn an expectation for neighboring state evolution.
Acute coherent disappearance across several state dimensions generates injury evidence.

2. EXCITABLE / REFRACTORY INJURY STATE
Prediction error pushes a bounded latent variable across an activation threshold.
The state propagates transiently and then becomes refractory/decays.

3. AGREEMENT BETWEEN LIFE AND PHENOTYPE CHANGE
Require compatible evidence from LIFE4 and visible/other latent state rather than LIFE4 support alone.

4. LEARNED CHANGE DETECTOR
Use existing hidden recurrent state to represent expected local state and train the shared update rule to respond specifically to damage examples.
No explicit runtime lesion flag.

WHY THIS IS MORE PRINCIPLED
The current NCA already possesses:
- recurrent hidden state;
- local perception;
- damage examples during training;
- enough local MLP capacity.

The missing object may not be another loss coefficient.
It may be a learned LOCAL STATE-TRANSITION MODEL:
"what should my neighborhood look like next?"

Injury is then a prediction failure, not merely a low cell count.

LITERATURE CONSISTENCY
Recent GNCA work reports that self-repair involves:
- structured temporal hidden-state fluctuations;
- collective attractor displacement after damage;
- spatially differentiated information flow;
- recovery-associated changes in redundancy/synergy.

That picture is more compatible with state-transition / prediction-error signaling than with a static global occupancy threshold.

Biological wound systems likewise often use transient multi-signal responses to abrupt disruption rather than absolute cell-count sensing.

RELATION TO R1
R1 remains the immediate canonical maintenance experiment.

No repair detector should be implemented before R1 establishes whether the LIFE4 substrate can first become economically and causally useful.

If R1 later leaves repair recruitment absent, this audit narrows the next research direction:
do NOT sweep raw memory thresholds;
investigate learned multi-cue local predictive error.

PROVENANCE
evidence_class = EXPLORATORY_SYNTHETIC_SPATIOTEMPORAL_GATE_AUDIT
canonical_scientific_execution = false
new_yggdrasil_training_run = false
trials_per_condition = 300
