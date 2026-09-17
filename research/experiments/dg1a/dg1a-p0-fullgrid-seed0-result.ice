TITLE: DG-1A-P0 Full-Grid Seed 0 Exploratory Result
DATE: 2026-09-17
STATUS: EXPLORATORY MEASURED RESULT — PARTIAL REGENERATION / FULLGRID CONTROL REPRODUCED
TRACK: DG-1A
CONFIDENCE: PLAUSIBLE / SINGLE-SEED FULL-GRID

QUESTION
Does the qualitative small-grid separation between growth-only collapse and maturity-gated regeneration persist when P0 is expanded to the original 40 x 40, 16-channel, 128-hidden-channel envelope?

EVIDENCE CLASS
MEASURED SANDBOX RESULT.

PROVENANCE LIMIT
Execution occurred in the isolated reconstructed ChatGPT CPU workspace rather than an authenticated repository checkout. This result is exploratory and cannot satisfy the commit-bound confirmatory gate.

MACHINE-READABLE EVIDENCE
evidence/dg1a/p0_fullgrid_seed0_sandbox.json

TEST SURFACE
47 tests passed.
0 failed.
The test pass includes the explicit separation of regeneration-training damage geometry from evaluation damage geometry.

PROTOCOL
Seed: 0
Grid: 40 x 40
State channels: 16
Hidden channels: 128
Model/update-rule parameters: 8,320
Training iterations: 200
Training development horizon: 64..96 steps
Batch size: 8
Pool size: 64 for regeneration
Target: deterministic disk, radius 6
Regeneration training lesion: center 0.50 x 0.50
Regeneration damage probability: 0.50
Regeneration maturity threshold: 16 active cells
Evaluation lesion: center 0.60 x 0.60
Evaluation growth horizon: 96
Recovery horizon: 96
Device: CPU
Precision: float32

RESOURCE CONTEXT
Prior full-grid cost probe measured approximately:
- 64-step forward/backward: 0.962 s total, observed max RSS about 1.01 GB;
- 96-step forward/backward: 1.396 s total, observed max RSS about 1.40 GB.

These are sandbox process measurements, not home-hardware guarantees.

GROWTH-ONLY RESULT
Training initial loss: 0.02941797
Training final loss: 0.00642034
Training minimum loss: 0.00602521
Accumulated training time: 145.92 s

Pre-lesion error: 0.02026492
Post-lesion error: 0.03979737
RelativeDamageEffect: 0.96386
Active-cell removal fraction: 0.42785

Final recovery error: 0.33155453
Bounded RecoveryFraction: 0.0
Raw RecoveryFraction: -14.93705
Stable T50: NOT ATTAINED
Stable T90: NOT ATTAINED
Recovery AUC: 0.0
Final active cells: 1517 / 1600
Final grid occupancy: 94.81%

INTERPRETATION — GROWTH ONLY
The full-grid growth-only model learns the target morphology well before damage, but after a meaningful lesion its developmental dynamics diverge from repair. Activity expands through nearly the entire available grid while morphology error becomes much worse.

This reproduces the small-grid negative-control failure mode at the full P0 envelope.

REGENERATION RESULT
Training initial loss: 0.02941797
Training final loss: 0.02671962
Training minimum loss: 0.02664715
Accumulated training time: 151.48 s
State-pool checkpoint size: approximately 6.67 MB

Pre-lesion error: 0.02410901
Post-lesion error: 0.02671267
RelativeDamageEffect: 0.107996
Active-cell removal fraction: 0.43077
Lesion validity under the frozen 10% relative functional-loss rule: VALID, but only narrowly above threshold.

Final recovery error: 0.02561126
Bounded RecoveryFraction: 0.42302
Raw RecoveryFraction: 0.42302
First T50 crossing: step 15
First T90 crossing: step 31
Stable T50: NOT ATTAINED
Stable T90: NOT ATTAINED
Recovery AUC: 0.71037
Final active cells: 502 / 1600
Final grid occupancy: 31.38%

INTERPRETATION — REGENERATION
The regeneration-trained organism responds much better than growth-only after lesion and uses far fewer active cells at the end of the recovery horizon.

However, its recovery is not stable enough to meet T50 by the end of the 96-step recovery window. The trajectory initially improves past the first T50 and T90 crossings, then gradually relapses, ending at approximately 42.3% recovered lost morphology quality.

This is partial repair with relapse, not successful stable regeneration under the current full-grid protocol.

MATCHED DIFFERENCE
DeltaRecovery: +0.42302 in favor of regeneration
DeltaRecoveryAUC: +0.71037 in favor of regeneration
Final active cells regeneration minus growth-only: -1015 cells

The active-cell difference is descriptive resource telemetry only. It is not evidence of realized sparse compute or memory savings because the current dense tensor implementation still stores/updates the fixed grid.

KEY FINDING
Scaling the canonical mechanism from the 20 x 20 probe to 40 x 40 does not preserve the same strong stable-recovery behavior without further mechanism or curriculum work.

The result therefore identifies a real scale/stability problem rather than a simple implementation failure:
- growth-only instability generalizes;
- damage-trained dynamics remain materially better;
- stable regeneration weakens at the larger envelope.

HYPOTHESIS STATUS
H-P0-3 at 20 x 20:
Numerical sandbox support rule met previously; confirmatory provenance still open.

H-P0-3 at 40 x 40:
UNKNOWN / NOT YET SUPPORTED.
Single seed shows partial recovery but fails stable T50.

FAILURE DISCIPLINE
Do not:
- lower the stable T50 requirement;
- shorten the recovery window to capture the transient crossing;
- claim success from recovery AUC alone;
- increase damage or training complexity without a new bounded experiment specification;
- alter the growth-only control to make the comparison easier.

DIAGNOSTIC HYPOTHESES
D1 — RECOVERY RELAPSE
The regeneration curriculum trains local repair but not sufficiently persistent post-repair stabilization over the larger developmental horizon.

D2 — POOL MATURITY / DAMAGE DISTRIBUTION
The 16-cell maturity threshold may be too weak relative to the 40 x 40 phenotype scale; many damaged training examples may not represent mature full-grid structures.

D3 — TRAINING HORIZON DISTRIBUTION
Training at 64..96 developmental steps may not adequately constrain behavior during an additional 96-step post-damage repair trajectory.

D4 — TARGET / ALIVE-DYNAMICS SCALE
The radius-6 target is relatively compact inside a 40 x 40 grid, leaving a large inactive spatial reservoir that can support uncontrolled expansion after perturbation.

D5 — RESOURCE PRESSURE ABSENT
P0 currently measures active-cell growth but does not penalize excess activation. The growth-only collapse and regeneration relapse may partly reflect the absence of an active-population cost.

These are hypotheses, not conclusions.

DECISION
1. Preserve this result as a partial/negative full-grid finding.
2. Do not widen to multiple full-grid seeds yet; first run one bounded discriminating stabilization experiment.
3. Keep the canonical P0 control unchanged.
4. Test a mechanism that targets repair persistence without introducing P1 functionality, structural replication, or Fibonacci scheduling into P0.
5. Preserve DG-1A-FIB1 separately; Fibonacci repair scheduling may later use this relapse phenotype as a useful ablation target, but only after the canonical stabilization question is characterized.

NEXT EXPERIMENT
DG-1A-P0-STAB-01.

Preregister a small full-grid stabilization ablation that changes one repair-training factor at a time. Recommended first factor: maturity threshold scaled to the developed phenotype rather than the fixed 16-cell threshold.

Candidate thresholds should be chosen before results and compared against the existing threshold-16 control using seed 0 first. If one candidate removes relapse without degrading pre-lesion morphology or causing resource explosion, then widen to multiple seeds.
