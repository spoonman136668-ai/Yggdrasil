TITLE: DG-1A-P0-STAB-17 — MATURE-VIS-ANCHOR-R1 Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
CANDIDATE: MATURE-VIS-ANCHOR-R1 + FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
EVIDENCE CLASS: MEASURED_SANDBOX

SCIENTIFIC SOURCE REVISION
23263694d9bd2188d7c6bc40fdc2a920754901e2

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false

PRE-EXECUTION REGRESSION
226 passed
0 failed

ENVIRONMENT
Python 3.13.5
PyTorch 2.10.0+cpu
device: CPU
precision: float32

PREREGISTERED QUESTION
Can STAB-16's viable decoupled hidden-life substrate improve formation occupancy, visible morphology, and lesion salience if mature hidden life is required to remain within one cell of the organism's own current visible-alpha phenotype, without using target geometry?

EXECUTED MECHANISM
MATURE-VIS-ANCHOR-R1:
- hard hidden life = channel 4 >0.1;
- hard visible support = current channel 3 >0.1;
- exact R1 / 3x3 Chebyshev visible neighborhood;
- mature only at hidden-life count >=113;
- forward error = fraction of mature hard life lacking any visible-alpha neighbor;
- straight-through gradient only through hard-alive unanchored hidden-life cells;
- no target tensor in anchor computation;
- zero direct gradient into visible alpha, RGB, dead life, anchored life, or other hidden channels;
- endpoint only;
- coefficient 1.0;
- FRONTIER-FLOOR-113, CEIL-800, ATTRACT-16, hidden L2, thresholds, and all canonical gates preserved unchanged.

EXECUTION
Exactly one fresh seed-0 candidate.
200 / 200 training iterations completed.
Deterministic single-writer atomic resumable checkpoints were used.

Canonical config SHA-256:
546d9053cdeb975b979096c312511c3ea39dfdc565f767cb8cf79e3f4be6b0ee

Final checkpoint SHA-256:
5b20f9b694c57d321069240e8df45f222ebfa668e59852acca9d504e538c03a5

Full evaluation SHA-256:
877ff069cecba36de4f955d6bba1c192091132f770c6229582033cced8f0190a

TRAINING RESULT
initial recorded loss:                    1.4307032824
minimum recorded loss:                    0.5240716934
final recorded loss:                      0.5387070775
final global visible MSE:                  0.0645075962
final foreground morphology MSE:           0.1509581357
final background alpha MSE:                0.0341420956
final ATTRACT-16 trajectory loss:           0.2855977714
final mature samples:                       8 / 8
final CEIL-800 loss:                        0.0001156250
final hidden-life mean:                   708.0
final hidden-life max:                    824
final FRONTIER-FLOOR-113 loss:              0.0
final MATURE-VIS-ANCHOR-R1 loss:            0.0033855534
final unanchored-life fraction:             0.0033855534
final unanchored-life cells mean:           2.25
non-finite state:                          NO

ANCHOR DYNAMICS
The new anchor was usually already satisfied.

Representative checkpoints:
- iteration 10:
  anchor loss 0.0;
  unanchored mature life 0;
- iteration 30:
  anchor loss 0.0;
  unanchored mature life 0;
- iteration 50:
  anchor loss 0.0;
  unanchored mature life 0;
- iteration 90:
  anchor loss 0.0;
  unanchored mature life 0;
- iteration 110:
  anchor fraction 0.0024048;
  mean unanchored mature life 1 cell;
- iteration 130:
  anchor fraction 0.0016191;
  mean unanchored mature life 0.86 cells;
- iteration 150:
  transient anchor activation 0.0864302;
  mean unanchored mature life 69.67 cells;
- iteration 170:
  anchor loss returned to 0.0;
- iteration 190:
  anchor loss 0.0;
- iteration 200:
  anchor fraction 0.0033856;
  mean unanchored mature life 2.25 cells.

The dominant mature regime therefore already had hidden life locally adjacent to visible alpha.

GROWTH / DAMAGE / RECOVERY
pre-damage hidden-life cells:             1038
post-damage hidden-life cells:             650
final recovery hidden-life cells:          681

pre-lesion global visible MSE:              0.0655461326
post-lesion global visible MSE:             0.0575213321
final recovery global visible MSE:          0.0569460019

DamageEffect:                               -0.0080248006
RelativeDamageEffect:                       -0.1224298101
ActiveCellRemovalFraction:                   0.3737957611

RecoveryFraction:                           undefined
stable T50:                                 not attained

The lesion again improved visible morphology.
Regeneration inference remains invalid.

PERSISTENCE / HOMEOSTASIS
initial hidden-life cells:                  919
maximum hidden-life cells:                 1043
final hidden-life cells:                    690
final active-cell drift:                   -229

initial global visible MSE:                 0.0591669381
maximum global visible MSE:                 0.0770485774
final global visible MSE:                   0.0668581352
maximum MSE degradation:                    0.0178816393
visible-state drift MSE:                    0.0190954842

GATE RESULTS
FAIL  113 <= pre-damage active <= 800
PASS  113 <= final recovery active <= 800
PASS  113 <= final persistence active <= 800
FAIL  maximum persistence active <= 800
PASS  final persistence active-cell drift <= 0
FAIL  DamageEffect > 0
FAIL  RelativeDamageEffect >= 0.10
PASS  ActiveCellRemovalFraction >= 0.10
FAIL  stable T50 attained
FAIL  final RecoveryFraction > 0.4230230485
FAIL  pre-lesion global MSE <= 0.0361635
FAIL  final persistence global MSE <= 0.0361635
PASS  maximum persistence MSE <= 2x initial persistence MSE
PASS  no non-finite state

FAILED GATES
8 / 14

CLASSIFICATION
LOCAL VISIBLE PROXIMITY MOSTLY ALREADY SATISFIED;
FUNCTIONAL MORPHOLOGY COUPLING REMAINS UNRESOLVED

CANDIDATE WORTH WIDENING
NO

COMPARISON TO STAB-16
STAB-17 modestly reduced some occupancy measures:
- pre-damage: 1082 -> 1038;
- persistence initial: 1047 -> 919;
- persistence peak: 1049 -> 1043;
- persistence final: 750 -> 690.

But visible morphology regressed:
- pre-lesion MSE: 0.06731 -> 0.06555 only slightly better;
- final persistence MSE: 0.04885 -> 0.06686, substantially worse;
- DamageEffect remained negative and became more negative.

The anchor was too often zero for these changes to support the hypothesis that simple R1 spatial disconnection was the dominant defect.

MECHANISTIC INTERPRETATION
STAB-17 falsifies simple local visible proximity as the missing functional-coupling mechanism.

Most mature hidden-life cells were already within one cell of visible alpha, yet:
- the organism remained overgrown at canonical formation;
- lesion removal improved visible morphology;
- visible morphology remained above the frozen thresholds;
- recovery remained invalid.

Therefore the important distinction is not merely:
"Is hidden life near visible form?"

The next seam is:
"Does a hidden-life cell causally contribute to maintaining or restoring useful visible morphology?"

Spatial adjacency is not sufficient evidence of functional usefulness.

DO NOT TUNE INSIDE STAB-17
Do not:
- widen anchor radius;
- increase anchor coefficient;
- change visible threshold;
- move the anchor onto ATTRACT future states;
- switch to target-mask anchoring;
- alter FRONTIER-FLOOR-113;
- tighten CEIL-800;
- alter hidden L2;
- alter ATTRACT-16;
- weaken scientific gates.

RETURN REFERENCES
STAB-12 remains the best overall canonical phenotype by gate count.

STAB-16 remains the key architectural result establishing that decoupled hidden life can be kept viable without exact target-mask equality.

STAB-17 establishes that R1 spatial proximity between hidden life and visible alpha is mostly already present and is not enough.

NEXT SCIENTIFIC SEAM
CAUSAL CONTRIBUTION OF LATENT SUPPORT TO VISIBLE MORPHOLOGY.

A future mechanism should distinguish useful hidden support from redundant support by measurable effect on visible morphology, rather than by:
- raw count;
- target-mask equality;
- or geometric proximity.

DURABLE MACHINE EVIDENCE
evidence/dg1a/p0_stab17_sandbox.json

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this result.
