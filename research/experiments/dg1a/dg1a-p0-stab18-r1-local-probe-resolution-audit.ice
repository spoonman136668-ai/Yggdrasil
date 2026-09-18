TITLE: DG-1A-P0-STAB-18-R1 — Local Counterfactual Probe Resolution Audit
DATE: 2026-09-18
STATUS: PRE-EXECUTION ANALYTIC AUDIT — NOT A SCIENTIFIC RESULT
TRACK: DG-1A
PARENT_CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Test whether the known credit-resolution weakness of the frozen 25% global Bernoulli causal probe is fundamentally caused by group size and spatial mixing, and identify a justified contingency direction if STAB-18-R1 is negative.

THIS RECORD DOES NOT
- alter the frozen STAB-18-R1 candidate;
- change any canonical gate, coefficient, horizon, fire rate, occupancy target, or seed;
- execute the canonical seed-0 candidate;
- establish that real Yggdrasil LIFE4 causal roles are spatially clustered;
- preregister STAB-19.

FROZEN SCIENTIFIC SOURCE
e7710a29768ebc852a19796ea42eba4c10629412

BACKGROUND
The prior credit-resolution audit showed that, around the STAB-16 formation occupancy of approximately 705 live cells, the frozen 25% global probe selects approximately 176 cells. Under a balanced equal-effect additive toy, harmful-vs-beneficial group-credit separation is only about 0.06 and beneficial collateral among pruned selected cells is about 47%.

The question here is whether a smaller spatially-local intervention can improve cellwise credit resolution without making the causal perturbation too weak to measure.

LITERATURE MOTIVATION
Two 2026 results make the spatial hypothesis worth testing:
- Sato, Masumori, Ikegami, arXiv:2607.15726 report hidden-channel modularization and mature spatially coherent cell-type communities during GNCA development.
- Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata, arXiv:2607.12403, frames hidden-state organization during maintenance/repair in terms of redundancy and synergy.

These works motivate, but do not prove, the assumption that Yggdrasil latent causal roles may have local spatial correlation.

AUDIT A — GLOBAL GROUP-SIZE TRADEOFF
Synthetic balanced cell contributions:
- harmful = -1
- beneficial = +1
- q_harmful = 0.5
- n = 705
- a selected group is classified non-beneficial when selected contribution sum <= 0

Monte Carlo results:
probe_fraction | expected_group | harmful_precision | beneficial_collateral | mean_abs_group_sum
0.02           | 14.10          | 0.5955            | 0.4045                | 2.9674
0.05           | 35.25          | 0.5632            | 0.4368                | 4.7195
0.10           | 70.50          | 0.5460            | 0.4540                | 6.6918
0.15           | 105.75         | 0.5374            | 0.4626                | 8.1911
0.20           | 141.00         | 0.5326            | 0.4674                | 9.4826
0.25           | 176.25         | 0.5292            | 0.4708                | 10.5806
0.35           | 246.75         | 0.5247            | 0.4753                | 12.5244
0.50           | 352.50         | 0.5207            | 0.4793                | 14.9853

Interpretation:
Smaller random groups improve attribution because the focal cell contributes a larger fraction of the intervention effect, but pure random downsizing trades away perturbation magnitude.

AUDIT B — 709-CELL BODY WITH SPATIALLY CORRELATED CAUSAL ROLES
Geometry:
- circular active body
- radius = 15 lattice cells
- active cells = 709, closely matching STAB-16 formation occupancy

Contribution fields:
- Gaussian random field over the body
- thresholded at the median to maintain approximately balanced harmful and beneficial cell counts
- spatial correlation controlled by Gaussian sigma
- sigma = 0 gives effectively independent roles
- larger sigma gives increasingly coherent causal regions

Probe families:
1. GLOBAL25
   independent Bernoulli p=0.25 across active cells
2. LOCAL05
   one circular local probe targeting approximately 5% of active-body area, intersected with the body

Representative results:
sigma | GLOBAL25 harmful precision | LOCAL05 harmful precision | GLOBAL25 mean |sum| | LOCAL05 mean |sum|
0     | 0.5254                     | 0.5654                    | 9.1866              | 4.4383
1     | 0.5255                     | 0.6687                    | 9.2551              | 11.3549
2     | 0.5252                     | 0.7730                    | 9.2223              | 18.2944
4     | 0.5255                     | 0.8572                    | 9.2777              | 23.9120
6     | 0.5256                     | 0.8891                    | 9.2185              | 25.9762

At sigma=2:
- GLOBAL25 beneficial collateral approximately 47.5%
- LOCAL05 beneficial collateral approximately 22.7%

At sigma=4:
- GLOBAL25 beneficial collateral approximately 47.5%
- LOCAL05 beneficial collateral approximately 14.3%

KEY RESULT
LOCAL05 becomes a Pareto improvement over GLOBAL25 once spatial correlation is modest:
- harmful precision is higher across every tested sigma;
- causal-signal magnitude crosses GLOBAL25 at approximately sigma=0.9 lattice cell;
- above that crossover, LOCAL05 uses roughly one-fifth the ablation budget while producing both cleaner credit and larger absolute intervention signal.

CROSSOVER SWEEP
sigma | LOCAL05 precision gain over GLOBAL25 | LOCAL05/GLOBAL25 signal ratio
0.0   | +0.0394                              | 0.4904
0.5   | +0.0618                              | 0.6551
0.7   | +0.0965                              | 0.8909
0.8   | +0.1103                              | 0.9958
0.9   | +0.1277                              | 1.1238
1.0   | +0.1467                              | 1.2212
1.2   | +0.1624                              | 1.3848
1.5   | +0.2002                              | 1.6419

AUDIT C — REPEATED SMALL LOCAL PROBES
A repeated-probe diagnostic used LOCAL05 with M independent probe locations per synthetic body.

At sigma=2:
M | mean unique body coverage | harmful precision | beneficial collateral
1 | 0.0469                    | 0.7665            | 0.2335
2 | 0.0919                    | 0.7737            | 0.2263
4 | 0.1750                    | 0.7685            | 0.2315
8 | 0.3199                    | 0.7709            | 0.2291

At sigma=4:
M | mean unique body coverage | harmful precision | beneficial collateral
1 | 0.0471                    | 0.8571            | 0.1429
2 | 0.0921                    | 0.8581            | 0.1419
4 | 0.1757                    | 0.8579            | 0.1421
8 | 0.3199                    | 0.8584            | 0.1416

Interpretation:
Repeated local probes increase spatial coverage without materially degrading attribution precision in the clustered-role toy. However, multiple probes per sample increase causal-rollout compute and are NOT proposed for the frozen R1 candidate.

MECHANISTIC IMPLICATION
If Yggdrasil's latent LIFE4 roles are spatially coherent at approximately one-cell scale or larger, global random 25% dropout is a poor causal-credit geometry:
- it mixes distinct local roles into one scalar group decision;
- useful and redundant regions cancel;
- every selected hard-live site receives the same one-sided decision;
- collateral pressure remains high.

A small localized probe can instead act as a coarse regional intervention. Under clustered-role assumptions it simultaneously:
- improves causal attribution precision;
- reduces useful-cell collateral;
- increases effect magnitude by avoiding cancellation across distant regions;
- samples different latent modules over training by moving the probe center.

BOUNDARY OF EVIDENCE
This is a synthetic causal-resolution audit, not an empirical Yggdrasil morphology result.
The result depends on spatial correlation of real causal roles.
STAB-17 established that latent cells are mostly spatially adjacent to visible structure, but did NOT establish causal-role clustering.
The canonical STAB-18-R1 execution must remain unchanged.

CONTINGENCY HYPOTHESIS
If frozen R1 fails with:
- mixed or predominantly non-positive causal deltas,
- substantial prune pressure,
- occupancy reduction accompanied by morphology/recovery regression,

then a high-value next experiment is to test LOCAL causal credit rather than immediately changing coefficients or probe thresholds.

A prospective post-R1 candidate should begin with one small domain-separated local probe per mature sample, not a parameter sweep. Exact fraction, geometry, and gates must be preregistered from measured R1 telemetry before execution.

If R1 instead shows mostly positive causal deltas with little prune pressure, localized pruning is not automatically justified; the stronger hypothesis becomes damage-conditioned latent reserve rather than redundant-cell elimination.

NO POST-HOC TUNING
No result in this audit authorizes alteration of STAB-18-R1.
The single fresh seed-0, 200-iteration STAB-18-R1 execution remains governed by the existing acceptance and no-tuning rules.

PROVENANCE
source_revision_verified_checkout = false
canonical_scientific_execution = false
evidence_class = SYNTHETIC_MECHANISTIC_AUDIT
random_seed_family = deterministic audit seeds derived from 20260918
