TITLE: DG-1A-P0 Exploratory Probe 01 — Curriculum and Regeneration Stability
DATE: 2026-09-17
STATUS: EXPLORATORY MEASURED RESULT — NOT CONFIRMATORY
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE / SINGLE-SEED

QUESTION
Does the bounded P0 implementation produce distinguishable post-lesion behavior between growth-only, persistence, and maturity-gated regeneration curricula under a matched small CPU probe?

HYPOTHESIS
Regeneration training applied only to sufficiently mature pooled phenotypes will produce more stable post-lesion recovery than growth-only training, while a persistence-only curriculum may remain difficult to interpret if the lesion does not cause meaningful loss.

EVIDENCE CLASS
MEASURED RESULT in an isolated ChatGPT CPU reconstruction of the repository interfaces.

IMPORTANT PROVENANCE LIMIT
The execution workspace was reconstructed from connected-GitHub source contents and did not contain the repository .git database. The runner therefore recorded source_revision = UNKNOWN in the generated machine-readable sandbox evidence.

These measurements are exploratory implementation evidence only. They do not satisfy the DG-1 reproducibility requirement for commit-bound confirmatory evidence.

ENVIRONMENT
Python: container Python 3
PyTorch: 2.10.0+cpu
Device: CPU
Seed: 0
Precision: float32

MATCHED PROBE CONFIGURATION
Repository-native configs created for reproduction:
- experiments/dg1a/configs/p0_probe_growth.yaml
- experiments/dg1a/configs/p0_probe_persistence.yaml
- experiments/dg1a/configs/p0_probe_regeneration.yaml

Shared envelope:
- state channels: 16
- hidden channels: 32
- fixed grid: 20 x 20
- target: deterministic disk, radius 4
- training iterations: 200
- development horizon per update: 8..12
- batch size: 4
- pool size: 16 where applicable
- evaluation growth steps: 12
- recovery steps: 16
- center lesion: 50% x 50% of active bounding box
- maturity gate for regeneration damage: at least 16 active cells

MEASUREMENT NOTE
RecoveryFraction is now reported both as:
- bounded normalized recovery_fraction in [0,1];
- recovery_fraction_raw for detecting overshoot or catastrophic negative recovery.

T50/T90 now distinguish first crossing from stable crossing. A stable crossing is counted only if the threshold remains satisfied for the rest of the declared recovery window.

MEASURED RESULTS

VARIANT: GROWTH ONLY
initial recorded loss: 0.0506718792
final recorded training loss: 0.0412252434
minimum recorded training loss: 0.0202803630
pre-lesion error: 0.0362425596
post-lesion error: 0.0653115734
damage effect: +0.0290690139
final recovery error: 1.3128582239
bounded recovery fraction: 0.0
raw recovery fraction: -42.9167172659
stable T50: NOT ATTAINED
stable T90: NOT ATTAINED
normalized recovery AUC: 0.0
final active cells: 400 / 400

INTERPRETATION
The growth-only control can reduce morphology loss during training, but after a meaningful lesion its developmental dynamics become catastrophically unstable and expand activity across the full fixed grid. This is negative evidence for untrained repair, not evidence against the developmental thesis.

VARIANT: PERSISTENCE
initial recorded loss: 0.0506718792
final recorded training loss: 0.0422349274
minimum recorded training loss: 0.0376902409
pre-lesion error: 0.0453899577
post-lesion error: 0.0463556200
damage effect: +0.0009656623
final recovery error: 0.0354418792
bounded recovery fraction: 1.0
raw recovery fraction: 11.3018193181
stable T50: 1 step
stable T90: 2 steps
normalized recovery AUC: 0.9478031040
final active cells: 73 / 400

INTERPRETATION
The persistence curriculum is stable, but the matched lesion causes only a very small immediate loss. Under the preregistered F3 rule this is not strong regeneration evidence: apparent recovery is confounded by weak damage sensitivity / robustness.

VARIANT: REGENERATION — MATURITY GATED
initial recorded loss: 0.0506718792
final recorded training loss: 0.0418235511
minimum recorded training loss: 0.0321079157
pre-lesion error: 0.0386763699
post-lesion error: 0.0449767970
damage effect: +0.0063004270
final recovery error: 0.0376846939
bounded recovery fraction: 1.0
raw recovery fraction: 1.1573982207
stable T50: 3 steps
stable T90: 5 steps
normalized recovery AUC: 0.8568749933
final active cells: 254 / 400

INTERPRETATION
The regeneration curriculum experiences a materially larger lesion effect than the persistence variant and then reaches stable T50 and stable T90 within the 16-step recovery window. Its final error is slightly lower than its own pre-lesion error, hence raw recovery above 1 while bounded recovery remains 1.

This is the first exploratory result in Yggdrasil showing the intended qualitative separation:
- growth-only: meaningful damage followed by collapse;
- persistence: stability but weak measurable damage;
- regeneration curriculum: meaningful damage followed by stable recovery.

It remains single-seed, small-grid, morphology-only evidence and does not establish cognition or general regenerative intelligence.

FAILURE / DESIGN FINDING
An earlier regeneration probe damaged every pooled state regardless of maturity. It produced transient threshold crossings but no stable T50/T90 at the end of the recovery window.

That observation motivated damage_min_active_cells. The maturity gate prevents seed-like / undeveloped states from being treated as repair examples.

DECISION
SUPPORTED AS AN IMPLEMENTATION MECHANISM:
Retain maturity-gated damage in P0 exploratory regeneration training.

NOT YET SUPPORTED AS A SCIENTIFIC CLAIM:
Do not declare H-P0-3 supported until commit-bound multi-seed runs reproduce a meaningful lesion effect and stable recovery advantage over the growth-only control.

NEXT EXPERIMENT
1. Re-run all three repository-native probe configs from an actual repository checkout so evidence records a real source_revision.
2. Run multiple seeds without changing thresholds after inspection.
3. Establish a numeric minimum damage-effect criterion before confirmatory H-P0-3 evaluation.
4. If stable regeneration replicates, move to the full 40 x 40 P0 family.
5. Do not begin DG-1B until P0 reproduction/regeneration is adequately characterized.
