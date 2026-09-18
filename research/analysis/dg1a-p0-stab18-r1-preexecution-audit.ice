TITLE: DG-1A-P0-STAB-18-R1 — Pre-Execution Mechanism Audit
DATE: 2026-09-18
STATUS: ANALYTICAL AUDIT — CANONICAL SEED-0 STILL UNEXECUTED
TRACK: DG-1A
BASELINE: STAB-16
FROZEN SCIENTIFIC SOURCE: e7710a29768ebc852a19796ea42eba4c10629412
EVIDENCE CLASS: SOURCE AUDIT + DETERMINISTIC ANALYTICAL SIMULATION + LITERATURE CROSS-CHECK

PURPOSE
Record pre-execution findings that sharpen interpretation of STAB-18-R1 without modifying its preregistered candidate, hyperparameters, scientific gates, or execution budget.

NON-MUTATION RULE
This audit does NOT modify:
- the STAB-18-R1 loss mode;
- probe fraction 0.25;
- T16 causal horizon;
- seed 0;
- the 200-iteration canonical envelope;
- STAB-16 baseline architecture;
- any of the 14 scientific gates.

The canonical seed-0 STAB-18-R1 run remains forbidden until the required compatibility/regression acceptance surface is green.

FROZEN-CONFIG ISOLATION
Direct line-by-line comparison between:
- p0_stab16_life4_band113_800.yaml
- p0_stab18_r1_life4_band113_800_causal_latent_dropout25_prune_t16_domainsep.yaml

found exactly one configuration difference:
    training.loss_mode

Seed, architecture, dimensions, fire rate, LIFE4 channel, training envelope, damage geometry, evaluation horizon, optimizer parameters, resource limits, and reporting cadence are unchanged.

NORMAL / RESUMABLE PARITY
The STAB-18-R1 normal-training and resumable-training loss-mode branches were extracted from the frozen source and normalized only for receiver naming and indentation.

Normalized branch length:
    normal:    4043 characters
    resumable: 4043 characters

Result:
    byte-identical after normalization.

No resume-only semantic drift was found.

DOMAIN-SEPARATED RNG AUDIT
The fixed domain-separated probe seed construction reproduces the preregistered reference seed for main manual_seed(1):
    3494006018084941813

Independent audit:
- 1000 main RNG seeds;
- all 16 future stochastic fire fields;
- canonical fire probability 0.5.

Observed maximum absolute deviation of mean probe-conditioned fire overlap from 0.5:
    0.0013472252

Observed maximum absolute mean Bernoulli correlation across the T16 horizon:
    0.00131049135

Interpretation:
No residual probe/fire schedule coupling was detected across the full T16 horizon.
The original STAB-18 first-step RNG aliasing confound is not present in R1.

INTERVENTION SEMANTICS
The intervention zeros latent channels 4..15 at selected hard-live sites while preserving visible RGBA 0..3.

The NCA alive mask is not pointwise LIFE4.
It is:
    max_pool_3x3(LIFE4) > 0.1

Therefore a selected site's LIFE4 can be zeroed while that lattice location remains eligible for the next NCA update because a neighboring LIFE4 site remains alive.

Minimal canonical support simulation:
- 40x40 grid;
- radius-6 disk;
- 113 hard-live sites;
- dropout fraction 0.25;
- 5000 independent main RNG states;
- exact R1 domain-separated mask construction.

Results:
    mean selected sites: 28.3664
    SD:                 4.56593
    min/max:            11 / 47

Among selected sites:
    retained next-step NCA update eligibility: 0.999041119
    structurally removed from local alive support: 0.000958881

Trials containing at least one structurally removed selected site:
    0.0252

Mean structurally removed selected sites per trial:
    0.0272

INTERPRETATION BOUNDARY
STAB-18-R1 is primarily a transient local latent-packet ablation under regenerative neighborhood support.
It is not a permanent cell-deletion assay.

A negative R1 result therefore must NOT be interpreted as proof that persistent structural cell presence is causally irrelevant.

TRAINING-CURRICULUM EXPOSURE
R1 uses variant:
    regeneration

The frozen CPU scheduling stream at seed 0 was replayed for the 200 training iterations using the exact operation order:
1. randperm(64) pool sample;
2. one damage-probability draw;
3. one randint(64,96) rollout-length draw.

Results:
    lesion-mode requests: 101 / 200 = 50.5%
    mean rollout length:  79.945
    rollout min/max:      64 / 96

On a lesion-mode iteration, samples 1..7 are lesion candidates when each has at least 16 LIFE4-active cells.
Sample 0 is always replaced by the fresh seed and is never pre-lesioned.

Maximum lesion-candidate opportunities under the schedule:
    101 * 7 = 707

Actual lesion applications remain phenotype-dependent because the >=16-life condition is evaluated at runtime.

The causal probe runs after the 64..96-step rollout.
Consequently its mature sample population can contain both ordinary developmental states and post-lesion recovery states.

MATURE-SAMPLE AVAILABILITY FROM BASELINES
Final STAB-16 training checkpoint:
    attractor_mature_samples = 8 / 8

Final STAB-17 training checkpoint:
    attractor_mature_samples = 8 / 8

The mature-sample gate is therefore not expected to starve the R1 probe late in training.

NEGATIVE-RESULT MECHANISM SIGNAL
STAB-12:
    pre LIFE/alpha-active: 857
    post-lesion active:    435
    removed:               422
    damage effect:         +0.0000496246
    visible-MSE improvement per removed cell:
        approximately -1.18e-7
    interpretation:
        lesion is essentially neutral/slightly harmful to visible morphology.

STAB-16:
    pre LIFE4 active:      1082
    post-lesion active:    795
    removed:               287
    damage effect:         -0.0051744804
    visible-MSE improvement per removed cell:
        approximately +1.803e-5

STAB-17:
    pre LIFE4 active:      1038
    post-lesion active:    650
    removed:               388
    damage effect:         -0.0080248006
    visible-MSE improvement per removed cell:
        approximately +2.068e-5

The similar per-removed-cell morphology improvement in STAB-16 and STAB-17, contrasted with STAB-12, is consistent with LIFE4 decoupling creating a reproducible population of morphologically costly support rather than simple count excess alone.

This is correlational evidence from the lesion assay.
STAB-18-R1 remains the causal test.

R1 BURDEN RELATIVE TO STAB-16
To satisfy the frozen gates from the STAB-16 endpoint, R1 must accomplish approximately:
- pre-damage active count:
    1082 -> <=800
    reduction >=282 = 26.06%
- persistence peak:
    1049 -> <=800
    reduction >=249 = 23.74%
- pre-lesion visible MSE:
    0.0673088878 -> <=0.0361635
    reduction >=46.27%
- final persistence visible MSE:
    0.0488450378 -> <=0.0361635
    reduction >=25.96%
- relative damage effect:
    -0.07687663 -> >=+0.10
    absolute swing >=0.17687663

Thus occupancy correction alone cannot produce a scientific pass.
R1 must simultaneously improve morphology and reverse lesion semantics.

DROPOUT SCALE
A literal 25% structural trim of STAB-16 counts would imply:
    pre-damage:       1082 * 0.75 = 811.5
    persistence peak: 1049 * 0.75 = 786.75
    recovery final:   797  * 0.75 = 597.75
    persistence final:750  * 0.75 = 562.5

This is only a scale comparison; R1 is not literal permanent deletion.
The fixed 0.25 probe is nonetheless the correct order of magnitude to interrogate the observed occupancy excess without approaching the 113 viability floor.

CAUSAL SCORE SCOPE
CausalDelta compares the exact per-sample ATTRACT-16 visible future objective:
    global visible MSE
  + foreground visible MSE
  + background alpha MSE
averaged over 16 future states.

CausalDelta does NOT include:
- CEIL-800 occupancy pressure;
- FRONTIER-FLOOR-113;
- hidden-state L2.

This preserves the intended separation:
- causal classifier asks whether latent removal helps/hurts visible morphology;
- independent LIFE4 terms enforce count/viability constraints.

GROUP-CREDIT LIMITATION
The causal decision is per sample, not per selected cell.

For each mature sample:
- approximately 25% of hard-live sites are selected as one probe group;
- one aggregate CausalDelta labels the entire group;
- if CausalDelta <= 0, every selected LIFE4 site receives the one-sided downward actuator gradient;
- if CausalDelta > 0, none of the selected sites receives that gradient.

At STAB-16's final mean formation count 704.75, the expected selected group is roughly:
    176 hard-live sites per mature sample.

A synthetic equal-effect group-testing diagnostic at N=704, p=0.25 shows:
- when harmful and beneficial sites are balanced, the conditional prune-probability separation between an included harmful versus beneficial site is only about 0.06;
- when one class strongly dominates, the aggregate classifier tends toward prune-almost-all or prune-almost-none.

This synthetic calculation is NOT a model prediction.
The real NCA is nonlinear and cell effects are neither independent nor equal.
It establishes only that a failed R1 cannot by itself falsify finer-grained causal pruning: the fixed group probe may have limited localization power.

EXISTING TELEMETRY IS SUFFICIENT
The runner stores the complete TrainingSummary.history.

R1 already records:
- causal_probe_mature_samples;
- causal_probe_classified_samples;
- causal_probe_nonbeneficial_samples;
- causal_probe_nonbeneficial_fraction;
- causal_probe_dropped_cells_mean;
- causal_probe_actual_drop_fraction_mean;
- causal_delta_mean/min/max;
- causal_intact_future_loss_mean;
- causal_counterfactual_future_loss_mean;
- occupancy/frontier/attractor metrics.

No telemetry change is required before the canonical run.

PRE-REGISTERED INTERPRETATION OF R1 TELEMETRY
These are interpretation aids, NOT new scientific gates.

Signature A — causal redundancy signal:
- nonbeneficial classifications occur materially;
- occupancy falls;
- visible loss stays stable or improves;
- lesion damage effect becomes positive.
Interpretation:
    supports removal of morphologically redundant/harmful latent support.

Signature B — beneficial latent substrate:
- CausalDelta is predominantly positive;
- nonbeneficial fraction remains low;
- causal actuator is mostly inactive.
Interpretation:
    random latent packets are functionally useful under T16.
    If overgrowth persists, redundancy-removal hypothesis is weakened.

Signature C — group-label saturation:
- nonbeneficial fraction remains near 0 or near 1 for long stretches;
- delta distribution is one-sided;
- morphology/count response is weak or indiscriminate.
Interpretation:
    fixed 25% group credit may be too coarse to localize mixed beneficial/harmful support.
    Do not generalize to cell-level causal irrelevance.

Signature D — occupancy improves but morphology worsens:
Interpretation:
    hidden support is heterogeneous and the group actuator is deleting useful packets together with costly packets.

Signature E — delta near zero with weak occupancy response:
Interpretation:
    T16 local regenerative compensation may make transient packet ablation insensitive to persistent structural dependence.

LITERATURE CROSS-CHECK
Mordvintsev et al., Growing Neural Cellular Automata, Distill (2020), establishes the 64..96-step stochastic-update, 3x3 alive-neighborhood, damage-trained NCA regime and treats hidden channels as learned communication/state variables.

Niklasson et al., Self-Organising Textures, Distill (2021), explicitly notes that hidden channels are unconstrained latent communication variables and may contain redundancy/correlation.

Masumori, Sato, and Ikegami, Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural Cellular Automata, arXiv:2607.12403 / Entropy 28(8):893 (2026), reports that distributed hidden-state fluctuations can be functionally involved in self-repair and that repair can involve increased redundant coordination.

This literature strengthens the need to distinguish:
- redundant state;
- synergistic/distributed latent computation;
- transient recoverability;
- permanent structural dependence.

It does NOT change the frozen R1 experiment.

ACCEPTANCE STATE
Previous MEASURED_SANDBOX targeted STAB-18-R1 acceptance:
    21 passed / 0 failed
after exact restoration of the frozen runner.

Historical compatibility replay and final combined regression remain mandatory before canonical seed-0 execution.

DECISION
KEEP STAB-18-R1 FROZEN.

Do not tune the dropout fraction, causal horizon, loss weights, gates, or seed before the single canonical run.

The new audit findings improve interpretation but do not justify replacing the preregistered experiment before execution.

NEXT AUTHORIZED SCIENTIFIC ACTION
1. Complete exact historical compatibility acceptance against frozen source e7710a2.
2. Require zero failures.
3. Execute exactly one canonical seed-0 STAB-18-R1 run.
4. Apply all 14 preregistered gates unchanged.
5. Use existing telemetry plus the interpretation signatures above to classify the mechanism.
6. No parameter sweep after failure.
