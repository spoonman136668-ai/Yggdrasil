TITLE: DG-1A-P0-STAB-18-R1 — Wound-Memory Robustness Boundary Audit
DATE: 2026-09-18
STATUS: EXPLORATORY SYNTHETIC STRESS AUDIT — NEGATIVE ROBUSTNESS BOUNDARY
TRACK: DG-1A
PARENT: SYNTHETIC WOUND-MEMORY REPAIR ROLLOUT POC

PURPOSE
Stress-test the promising temporal wound-memory repair toy against perturbations of the MEMORY STATE ITSELF rather than only binary LIFE4 dropout.

The prior POC showed:
- strong clean central-wound repair;
- no clean exterior growth;
- a strong-injury gate sharply reduced false growth under 1% independent LIFE4 turnover.

The remaining question is whether a raw analog support-memory channel is robust to the kind of structured hidden-state variability reported in recent GNCA analysis.

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- measure real Yggdrasil hidden-state fluctuation amplitude;
- select a memory amplitude, noise tolerance, trigger threshold, component size, or repair candidate;
- establish that Yggdrasil hidden noise follows Gaussian statistics;
- authorize a named hidden channel.

LITERATURE MOTIVATION
Recent 2026 GNCA self-maintenance work reports that hidden-channel fluctuations are:
- temporally persistent enough to participate in collective dynamics;
- spatially structured;
- functionally involved in repair.

Therefore IID binary dropout alone is an insufficient robustness control for a proposed hidden-memory mechanism.

SYNTHETIC STRESS SETUP
Stable undamaged body:
- 40x40 grid;
- radius-15 disk;
- 709 live cells.

Base SupportMemory:
pre-existing normalized 3x3 support density.

Perturbation:
Gaussian additive noise applied to SupportMemory on live cells.

Spatial correlation conditions:
- correlation scale 0: independent field;
- Gaussian smoothing sigma 1;
- Gaussian smoothing sigma 2.

After smoothing, fields were rescaled so the live-cell standard deviation matched the requested memory-noise sigma.

The life mask itself remained undamaged.

Repair mechanism:
- same frozen synthetic local frontier classifier from the preceding POC;
- strong support-loss injury gate;
- local signal propagation;
- up to 8 repair steps.

This is a deliberately harsh control:
the perturbed memory field is static over the rollout rather than transiently resampled each step.

RESULT — LOW MEMORY NOISE
At normalized SupportMemory sigma = 0.05:

For correlation scales 0, 1, and 2:
- 0 / 200 trials produced external expansion;
- mean external expansion = 0;
- maximum = 0.

The toy is therefore stable to small persistent memory perturbations in this synthetic body.

RESULT — MODERATE MEMORY NOISE
At normalized SupportMemory sigma = 0.10:

Independent field:
- mean strong-trigger sites: approximately 0.295;
- trials with external expansion: 5 / 200;
- mean external expansion: 1.515 cells;
- p95 external expansion: 0;
- p99: approximately 62;
- maximum: 71.

Correlation scale 1:
- mean strong-trigger sites: approximately 0.315;
- trials with external expansion: 7 / 200;
- mean external expansion: 2.57;
- p95: 0;
- p99: approximately 77;
- maximum: 88.

Correlation scale 2:
- mean strong-trigger sites: approximately 0.320;
- trials with external expansion: 7 / 200;
- mean external expansion: 3.295;
- p95: 0;
- p99: approximately 99;
- maximum: 128.

Interpretation:
moderate memory noise produces a LOW-FREQUENCY / HIGH-SEVERITY failure mode.

Most trials are stable.
Rare false injury seeds can nevertheless bootstrap large outward cascades.

This is precisely the kind of tail behavior that clean central-lesion tests would miss.

RESULT — HIGHER MEMORY NOISE
At normalized SupportMemory sigma = 0.15:

Independent:
- mean strong-trigger sites: approximately 9.36;
- external-expansion trials: 123 / 200;
- mean external expansion: 67.91;
- maximum: 290.

Correlation scale 1:
- mean strong-trigger sites: approximately 9.58;
- external-expansion trials: 129 / 200;
- mean external expansion: 91.57;
- maximum: 383.

Correlation scale 2:
- mean strong-trigger sites: approximately 9.58;
- external-expansion trials: 94 / 200;
- mean external expansion: 63.58;
- maximum: 406.

The raw analog-memory mechanism is therefore NOT robust to persistent perturbations of this magnitude.

SPATIAL-CONSENSUS CONTROL
A diagnostic refinement retained initial injury seeds only when they belonged to a connected 8-neighbor trigger component with minimum size k.

Canonical clean lesion:
- strong-trigger ring contained 36 seed sites;
- minimum-component values 1 through 8 preserved the 120/121 repair result;
- no exterior expansion;
- component size 12 suppressed the repair entirely.

This shows that local spatial consensus can discriminate large wound evidence from some small trigger noise.

However, it is NOT a complete robustness solution.

Examples at memory sigma 0.10, correlation scale 2:
- k=3: 4 / 200 false-expansion trials; max 110;
- k=4: 1 / 200; max 75;
- k=5: 1 / 200; max 81;
- k=8: 1 / 200; max 107.

At memory sigma 0.15, spatial consensus remains insufficient.
For correlated noise, false repair cascades remain common even at larger component thresholds.

Therefore:
SPATIAL CONSENSUS HELPS,
BUT DOES NOT FIX A NOISY PERSISTENT ANALOG MEMORY REPRESENTATION.

IMPORTANT SCIENTIFIC CONSEQUENCE
The clean wound-memory result should NOT be promoted directly into a Yggdrasil candidate.

A repair state must satisfy both:
1. sensitivity to true acute injury;
2. stability against the organism's own latent fluctuations.

The second requirement is now experimentally first-class.

WHY THIS MATTERS FOR YGGDRASIL
The architecture is intentionally developmental and recurrent.

A hidden repair signal that occasionally self-excites during ordinary maintenance would recreate the exact failure class the stabilization series is trying to eliminate:
- unnecessary support creation;
- outward growth;
- poor lesion salience;
- occupancy instability.

Therefore repair intelligence cannot simply mean:
"detect a large hidden-state difference and grow."

It requires a robust state transition.

NEXT MECHANISTIC DIRECTIONS
These are research directions only, not selected candidates.

A. TEMPORAL HYSTERESIS / PERSISTENCE
Require injury evidence to persist or accumulate across multiple local updates before repair is licensed.

Rationale:
true structural injury persists;
high-frequency hidden fluctuations may not.

B. PREDICTIVE-ERROR STATE
Rather than storing raw previous support magnitude, learn a bounded expectation / prediction-error representation.

Rationale:
the signal should represent violation of expected local dynamics, not absolute analog memory noise.

C. MULTI-CUE LOCAL AGREEMENT
Require agreement between:
- LIFE4 support change;
- visible-state change;
- possibly latent cell-type context.

Rationale:
a real wound zeros multiple state dimensions coherently.

D. EXCITABLE TRANSIENT REPAIR STATE
Use a bounded transient state with:
- activation threshold;
- refractory/decay behavior;
- local propagation;
rather than an unbounded analog memory difference.

This is structurally closer to calcium-wave / excitable-media wound signaling and may naturally suppress low-amplitude noise.

NO PARAMETER SELECTION
The synthetic sigma values, component thresholds, trigger thresholds, and decay constants are diagnostics only.

Do not use them as frozen STAB-19 values.

PREREQUISITE BEFORE REAL REPAIR CANDIDATE
Measure real trained Yggdrasil maintenance dynamics after the R1 branch is resolved:
- per-channel hidden RMS / variance;
- temporal autocorrelation;
- spatial correlation length;
- LIFE4 turnover;
- visible-alpha turnover;
- distribution of local state changes during undamaged persistence;
- same quantities immediately after lesion.

Only then should a wound-signal threshold or state representation be preregistered.

RELATION TO STAB-18-R1
R1 remains frozen and prior.

The current repair research is contingency work.

If R1 does not establish useful maintenance-stage substrate, repair-signal design is premature.

If R1 improves maintenance but leaves recovery weak, this robustness audit prevents the project from jumping directly to an unsafe raw-memory implementation.

CONCLUSION
The current research now supports BOTH sides of the wound-memory hypothesis:

POSITIVE:
local temporal information can make wound frontier distinguishable and can drive selective layer-by-layer synthetic repair using the existing perception/MLP capacity.

NEGATIVE:
a naive persistent analog memory representation can convert latent noise into rare or frequent runaway repair.

The next meaningful advance is therefore not another threshold sweep.

It is:
ROBUST LOCAL INJURY-STATE REPRESENTATION.

PROVENANCE
evidence_class = EXPLORATORY_SYNTHETIC_ROBUSTNESS_AUDIT
canonical_scientific_execution = false
new_yggdrasil_training_run = false
memory_noise_trials_per_condition = 200
synthetic_seed_family = 20260918
