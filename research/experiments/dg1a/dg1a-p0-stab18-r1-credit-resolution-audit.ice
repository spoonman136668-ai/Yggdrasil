TITLE: DG-1A-P0-STAB-18-R1 — Pre-Execution Group-Credit Resolution Audit
DATE: 2026-09-18
STATUS: PRE-EXECUTION INTERPRETATION AUDIT — NOT A SCIENTIFIC RESULT
TRACK: DG-1A
CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Quantify the expected resolution and collateral-pruning behavior of the already-preregistered fixed 25% group-level causal probe before the single canonical seed-0 execution.

THIS RECORD DOES NOT
- change the frozen STAB-18-R1 candidate;
- change probe fraction, horizon, floor, ceiling, coefficient, hidden L2, fire rate, or any scientific gate;
- qualify the repository regression suite;
- execute the canonical seed-0 candidate;
- establish cellwise causal attribution.

FROZEN SCIENTIFIC SOURCE
e7710a29768ebc852a19796ea42eba4c10629412

RNG DOMAIN-SEPARATION RECHECK
Existing R1 standalone audit was rerun under:
- Python 3.13.5 family
- PyTorch 2.10.0+cpu
- CPU

Across main seeds 0..999 and a 16-step horizon:
- mean probe fraction: 0.2502843758
- maximum absolute mean overlap deviation from fire-rate 0.5: 0.0013472252
- maximum absolute mean phi correlation: 0.0013104913

Interpretation:
The R1 probe/main-stream relationship is consistent with practical pseudorandom domain separation for this experiment. This is not a proof of formal independence.

ORIGINAL ALIAS CONTROL
The frozen original STAB-18 defect is specifically same-random-field reuse:
- ProbeDrop = U < 0.25
- FirstFireMask = U <= 0.50
for the same U field after main-generator state restore.

Direct same-field control:
- P(FirstFireMask | ProbeDrop) = 1.0
- phi approximately 0.578

A same-generator/different-draw control does not reproduce this severe alias. Therefore the original confound was identical-field reuse, not generator identity alone.

STRUCTURAL PROBE CHECK
For a radius-6 113-cell disk over 5000 deterministic probe trials:
- mean selected cells: 28.3664
- selected SD: 4.56593
- structurally removed fraction after local eligibility check: 0.000958881
- trials with any structural removal: 0.0252
- mean structurally removed sites: 0.0272

Interpretation:
At minimum viable occupancy, ordinary 25% probe selection itself almost never eliminates local update eligibility. Any canonical effect should primarily reflect latent-state ablation rather than immediate topological isolation.

GROUP-CREDIT TOY
Diagnostic only:
- equal-magnitude additive cell contributions;
- harmful contribution = -1;
- beneficial contribution = +1;
- fixed probe p = 0.25;
- group classified non-beneficial when selected-group sum <= 0;
- no parameter from this toy feeds back into STAB-18-R1.

At q_harmful = 0.5:
- n=113: harmful-vs-beneficial prune probability gap approximately 0.148
- n=300: gap approximately 0.091
- n=500: gap approximately 0.068
- n=705: gap approximately 0.060
- n=800: gap approximately 0.057

At strongly skewed q_harmful = 0.25 or 0.75, the group decision rapidly saturates toward keep-all or prune-all as n grows.

CELLWISE COLLATERAL AUDIT
At q_harmful = 0.5 with 50,000 trials:
- n=113: harmful precision among pruned selected cells approximately 0.570; beneficial collateral approximately 0.430
- n=300: harmful precision approximately 0.544; collateral approximately 0.456
- n=705: harmful precision approximately 0.529; collateral approximately 0.471
- n=800: harmful precision approximately 0.528; collateral approximately 0.472

STAB-16 OCCUPANCY CONTEXT
Historical STAB-16 final formation active-cell mean:
704.75

At approximately 705 live cells:
- expected 25% probe size is approximately 176 cells/sample;
- equal-effect toy group resolution is coarse;
- a non-beneficial group decision applies one-sided prune pressure to every probed hard-live LIFE4 site in that sample.

DIRECT GRADIENT SCALE
Frozen causal_latent_prune_terms gives each pruned LIFE4 site direct derivative:
1 / (HardLifeCount * mature_batch_count)

For mature batch count 8:
- n=705: approximately 1.773e-4 per pruned LIFE4 site
- n=800: approximately 1.563e-4

Frozen occupancy-ceiling surrogate is inactive below 800.
At n=824 its per-site direct derivative is approximately 9.375e-6, making the causal term roughly 16.2x larger on a selected pruned site.
At n=984 occupancy derivative is approximately 7.188e-5 and causal derivative approximately 1.270e-4, ratio approximately 1.77.

CEILING-EXCESS SCALE CHECK
Historical evaluation overgrowth relative to the fixed ceiling 800:
- STAB-16 pre-damage: 1082 -> requires removal of 282 cells = 26.0628%
- STAB-17 pre-damage: 1038 -> requires removal of 238 cells = 22.9287%
- STAB-16 persistence maximum: 1049 -> requires removal of 249 cells = 23.7369%
- STAB-17 persistence maximum: 1043 -> requires removal of 243 cells = 23.2982%

Relative to the frozen 25% causal probe:
- STAB-16 pre-damage excess / 25% = 1.0425
- STAB-17 pre-damage excess / 25% = 0.9171
- STAB-16 persistence-max excess / 25% = 0.9495
- STAB-17 persistence-max excess / 25% = 0.9319

Interpretation:
The preregistered 25% probe fraction is on the same order as one full historical ceiling-excess correction. This supports the intervention as materially capable of changing occupancy, while reinforcing the need to interpret collateral pruning carefully. It does not justify changing the frozen fraction.

INTERPRETATION BOUNDARY
R1 remains scientifically worth executing because:
- STAB-16 restored hidden-life viability but remained overgrown and morphologically weak;
- STAB-17 showed simple visible proximity was already mostly satisfied and did not resolve the same failure pattern;
- R1 tests functional dependence rather than geometric proximity.

However, a negative R1 result will NOT by itself establish that latent support lacks causal value.

A negative result may instead indicate that fixed 25% group credit is too coarse:
- beneficial and harmful cells can be co-selected;
- group classification can generate substantial collateral prune pressure;
- resolution degrades approximately with larger selected-group size under the equal-effect diagnostic.

CANONICAL RESULT INTERPRETATION
Use frozen telemetry after execution:
- causal_delta_mean/min/max
- causal_probe_nonbeneficial_fraction
- causal_probe_actual_drop_fraction_mean
- causal_latent_prune_loss
- formation occupancy
- morphology and all 14 gates

Interpretation patterns:
1. Mostly positive causal deltas + little prune pressure:
   latent substrate appears broadly useful under this intervention; failure would not support redundant-support pruning as the solution.
2. Mostly non-positive deltas + strong prune pressure + hidden-life collapse/morphology regression:
   group-credit pruning is likely too indiscriminate under the fixed probe.
3. Mixed deltas + occupancy reduction + morphology improvement:
   supports the intended redundant-support hypothesis.
4. Occupancy improvement without morphology/recovery improvement:
   redundancy was present but was not the dominant missing coupling mechanism.

NO POST-HOC TUNING
The canonical candidate remains exactly as preregistered.
Exactly one fresh seed-0, 200-iteration STAB-18-R1 execution remains permitted only after all mandatory historical acceptance is green.

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false
evidence_class = ANALYTIC_RUNTIME_EQUIVALENT
canonical_scientific_execution = false
