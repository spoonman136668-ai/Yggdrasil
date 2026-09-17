TITLE: DG-1A-P0-STAB-08 — Graded Immutable Target-Distance Occupancy Control Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
EVIDENCE CLASS: MEASURED SANDBOX

QUESTION
Can canonical P0 preserve meaningful target viability while bounding excess support if target-background occupancy pressure is graded continuously by immutable distance from the target instead of applied uniformly or exempted by a binary halo?

PREREGISTERED CANDIDATE
DIST-1

For each target-background cell, let d be Chebyshev distance to the nearest immutable target-foreground cell.

DistanceWeight(d) = d / (d + 1)

GradedBackgroundAlphaMSE =
    mean(DistanceWeight(d) * state_alpha^2 over target-background cells)

TrainingMorphologyLoss =
    GlobalVisibleMSE
    + ForegroundVisibleMSE
    + GradedBackgroundAlphaMSE

No distance cap, halo radius, coefficient schedule, coefficient sweep, threshold sweep, or post-result tuning was permitted.

FROZEN DISTANCE GEOMETRY
40 x 40 radius-6 target:
- foreground cells: 113
- background cells: 1487
- maximum Chebyshev distance: 16
- mean background distance weight: 0.8635463277

Ring cardinalities:
d=1: 56
d=2: 64
d=3: 72
d=4: 80
d=5: 88
d=6: 96
d=7: 104
d=8: 112
d=9: 120
d=10: 128
d=11: 136
d=12: 144
d=13: 152
d=14: 102
d=15: 28
d=16: 5

PREREGISTRATION
research/experiments/dg1a/dg1a-p0-stab08-spec.ice

SOURCE / PROVENANCE
Implementation-and-test source revision used as semantic reconstruction basis:

5b67f6a6f2f748ee2da9a8208739173b8d4232cb

Sandbox execution was not a native byte-identical checkout.

Therefore:
- source_revision_verified_checkout: NO
- sandbox_source_byte_identity: NO
- scientific status: MEASURED SANDBOX, not commit-bound confirmatory acceptance

TEST SURFACE
The complete reconstructed test surface was exercised without skipping tests:

95 non-runner tests: PASS
STAB-04 + STAB-05 subprocess runner tests: 2 PASS
STAB-06 + STAB-07 subprocess runner tests: 2 PASS
STAB-08 subprocess runner test: 1 PASS

TOTAL:
100 passed
0 failed
all bounded batches returned pytest code 0

Environment:
Python 3.13.5
PyTorch 2.10.0+cpu

The additive DIST-1 tests covered:
- exact immutable Chebyshev distance rings;
- fail-closed missing foreground/background behavior;
- exact radius-6 ring cardinalities;
- frozen mean background weight;
- exact graded alpha formula;
- exact composite training objective;
- all-dead loss sanity;
- frozen config validation;
- normal training telemetry;
- resumable training telemetry;
- runner evidence mode/telemetry.

No assertion was weakened, skipped, disabled, or modified merely to obtain a passing result.

EXECUTION CONTRACT
Exactly one fresh seed-0 DIST-1 candidate completed 200 / 200 training iterations.

The run used:
- one writer;
- deterministic resumable checkpoints;
- bounded 10-iteration segments;
- frozen H96/M16 regeneration envelope;
- no second candidate;
- no alternate seed;
- no distance-function change;
- no coefficient change;
- no threshold/gate change.

MEASURED TRAINING RESULT
training iterations:       200 / 200
initial recorded loss:     0.4459555447
minimum recorded loss:     0.2007718384
final recorded loss:       0.2026043236
training elapsed:          271.8185413 s
non-finite state:          NO

Final recorded components:
- global morphology MSE:       0.0611362085
- foreground morphology MSE:   0.0863720179
- graded background alpha MSE: 0.0550952032
- morphology loss:             0.2026034296
- hidden penalty:              0.0886766464
- gradient norm:               1.0809142590

MEASURED EVALUATION RESULT
pre-lesion global MSE:     0.1016835570
post-lesion global MSE:    0.0743995309
final recovery global MSE: 0.0601313077

DamageEffect:              -0.0272840261
RelativeDamageEffect:      -0.2683228925

pre-damage active cells:   1440 / 1600
post-damage active cells:   864 / 1600
active-cell removal:       0.4000000000
final recovery active:     1095 / 1600

bounded RecoveryFraction:  undefined
raw RecoveryFraction:      undefined
stable T50:                NOT ATTAINED / undefined
stable T90:                NOT ATTAINED / undefined
normalized recovery AUC:   undefined

PERSISTENCE OBSERVATION
initial persistence error: 0.0879649892
maximum degradation:       0.0458279923
final persistence error:   0.0973186269
initial active cells:      1348
final active cells:        1102
active-cell drift:         -246
visible-state drift MSE:   0.0375958979
mean step update magnitude:0.0055083151

The phenotype contracted in active-cell count over the persistence window but remained far above the 800-cell ceiling and retained poor morphology. This contraction is not evidence of stabilization.

PREREGISTERED GATE APPLICATION
PASS  pre-damage active cells >= 113
FAIL  pre-damage active cells <= 800
FAIL  DamageEffect > 0
FAIL  RelativeDamageEffect >= 0.10
PASS  ActiveCellRemovalFraction >= 0.10
FAIL  stable T50 attained
FAIL  final RecoveryFraction > 0.4230230485
FAIL  pre-lesion global MSE <= 0.0361635
PASS  final recovery active cells >= 113
FAIL  final recovery active cells <= 800
PASS  persistence final active cells >= 113
FAIL  persistence final active cells <= 800
FAIL  persistence final global MSE <= 0.0361635
PASS  persistence maximum MSE <= 2x initial persistence MSE
PASS  no non-finite state

CANDIDATE WORTH WIDENING: NO

PRIMARY FAILURE MODE
VIABLE BUT SEVERE OVERGROWTH WITH INVALID LESION.

The evaluation lesion removed 576 active cells, exactly 40% of the active phenotype, yet global morphology MSE improved from 0.1016836 to 0.0743995.

Therefore the mature phenotype contained substantial harmful/excess structure before lesion. There was no valid morphology-damage event from which to infer regeneration.

COMPARISON WITH STAB-05
STAB-05 OCC-A1:
- pre-damage active: 1206
- pre-lesion MSE: 0.0701904967
- final recovery active: 1329
- persistence final active: 1378

STAB-08 DIST-1:
- pre-damage active: 1440
- pre-lesion MSE: 0.1016835570
- final recovery active: 1095
- persistence final active: 1102

Relative to STAB-05:
- pre-damage activity increased by 234, approximately 19.40%;
- pre-lesion MSE worsened by approximately 44.87%.

Later activity contracted more strongly than STAB-05, but that did not produce valid morphology, bounded occupancy, or a valid lesion.

COMPARISON WITH STAB-07
STAB-07 HALO-1:
- pre-damage active: 1094
- pre-lesion MSE: 0.0625592172
- final recovery active: 1232
- persistence final active: 1276

STAB-08 DIST-1:
- pre-damage active: 1440
- pre-lesion MSE: 0.1016835570
- final recovery active: 1095
- persistence final active: 1102

Relative to STAB-07:
- pre-damage activity increased by 346, approximately 31.63%;
- pre-lesion MSE worsened by approximately 62.54%;
- final recovery activity was approximately 11.12% lower;
- persistence final activity was approximately 13.64% lower.

The lower later active-cell counts do not offset the failed morphology/occupancy/lesion gates.

SCIENTIFIC INTERPRETATION
The STAB-05/06/07/08 bracket now rejects another simple mechanism class:

1. uniform continuous background alpha pressure is insufficient;
2. strong threshold-aligned pressure can collapse viability;
3. binary one-cell support exemption restores viability but remains overgrown;
4. smooth monotonic distance discount d/(d+1) worsens the mature overgrowth phenotype rather than locating bounded viable support.

The result indicates that static spatial weighting of background alpha energy, whether uniform, binary-halo, or this fixed monotonic distance gradient, is not sufficient to control the dynamic support process under the frozen envelope.

The remaining problem is increasingly dynamic rather than merely spatial:
- excessive support emerges during development;
- lesions can remove harmful structure;
- active support can later contract while morphology remains poor;
- mature occupancy and morphology are not being held near a stable attractor.

NEGATIVE KNOWLEDGE RETAINED
1. DIST-1 is not worth widening.
2. Do not tune the d/(d+1) function inside STAB-08.
3. Do not reinterpret later contraction as successful bounded support.
4. Static target-distance weighting alone is insufficient under H96/M16.
5. The next discriminating mechanism should target dynamic excess-support creation or maintenance rather than another static spatial-weight interpolation.
6. Global morphology MSE must continue to be interpreted jointly with viability, occupancy, persistence, and lesion-validity telemetry.

DECISION
- CLOSE STAB-08 as negative.
- DO NOT widen DIST-1 to additional seeds.
- DO NOT tune distance weights, coefficients, thresholds, or gates inside STAB-08.
- Preserve all seven historical training-loss modes for reproducibility.
- Preserve the target-derived 113-cell viability floor and existing absolute gates.
- Keep global visible-channel morphology MSE as the common evaluation metric.
- Do not reopen STAB-01 through STAB-08 with post-result parameter insertion.

NEXT RESEARCH ACTION
Remain inside canonical DG-1A P0.

Open a new preregistered packet, provisionally DG-1A-P0-STAB-09, before further scientific execution.

STAB-09 should discriminate a dynamic support-control mechanism rather than another static coefficient, margin, halo-radius, or distance-weight sweep.

Plausible design classes include:
- an explicit penalty on excess active-support creation between developmental states;
- a persistence/homeostasis objective that penalizes post-growth expansion;
- a coupled morphology-plus-support-change objective tied to immutable target viability.

NO STAB-09 mechanism is selected by this result record.

MACHINE EVIDENCE
evidence/dg1a/p0_stab08_sandbox.json

The durable GitHub evidence is a compact summary of the full sandbox evidence.

Full local sandbox evidence SHA-256:
8c4a0c21319cdb06dc2d806faec2d593cb9233d6320d29bbc77e14b651b6532e

SCIENTIFIC BOUNDARY
This remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, or Fibonacci scheduling from this result.
