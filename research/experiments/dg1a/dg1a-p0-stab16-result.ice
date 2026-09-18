TITLE: DG-1A-P0-STAB-16 — FRONTIER-FLOOR-113 Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
CANDIDATE: FRONTIER-FLOOR-113 + LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
EVIDENCE CLASS: MEASURED_SANDBOX

SCIENTIFIC SOURCE REVISION
986e3953365a2aa47682a3147cc6ae56a64c9485

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false

PRE-EXECUTION REGRESSION
209 passed
0 failed

ENVIRONMENT
Python 3.13.5
PyTorch 2.10.0+cpu
device: CPU
precision: float32

PREREGISTERED QUESTION
Can decoupled hidden life avoid STAB-15 collapse if it receives only a local positive minimum-viability signal on the mechanically reachable 3x3 growth frontier, while preserving the existing 113..800 occupancy band and ATTRACT-16 visible-morphology supervision?

EXECUTED MECHANISM
FRONTIER-FLOOR-113:
- hidden life channel 4;
- visible morphology channels 0..3;
- one-sided hard hidden-life lower bound at 113;
- straight-through gradient only through currently dead cells in the immediate 3x3 hard-life neighborhood;
- zero floor gradient on already-live cells;
- zero floor gradient on remote dead cells;
- zero direct gradient on visible channels;
- no target geometry in the floor;
- floor exactly zero at hidden-life count >=113;
- CEIL-800 preserved from STAB-15;
- ATTRACT-16 preserved from STAB-15;
- hidden L2 preserved at 0.00001;
- no coefficient, radius, threshold, floor, ceiling, hidden-L2, or horizon sweep.

EXECUTION
Exactly one fresh seed-0 candidate.
200 / 200 training iterations completed.
Deterministic single-writer atomic resumable checkpoints were used.

Canonical config SHA-256:
bf5c35409f1b0b06e0a90a1473d0a82f293f8140c433f66d49cbf6ff190df6d2

Final checkpoint SHA-256:
94004a0d0ee3400f0b20daad3415d042309b28f3b27b9262c1ffdc656f709f63

Full evaluation SHA-256:
b72746e9fc657639cae489703cb74b737db394dfff3c4d70b1470409313c4a55

TRAINING RESULT
initial recorded loss:                   1.4307032824
minimum recorded loss:                   0.3706562817
final recorded loss:                     0.6650499701
final global visible MSE:                 0.0423287600
final foreground morphology MSE:          0.2503173947
final background alpha MSE:               0.0188140422
final ATTRACT-16 trajectory loss:          0.3450603187
final mature samples:                      8 / 8
final CEIL-800 loss:                       0.0085267583
final hidden-life mean:                  704.75
final hidden-life max:                   984
final FRONTIER-FLOOR-113 loss:             0.0
final frontier cells mean:               678.5
non-finite state:                         NO

DYNAMIC TRAINING INTERPRETATION
FRONTIER-FLOOR-113 eliminated the STAB-15 absorbing hidden-life collapse.

The floor and ceiling behaved as a genuine deadband rather than a fixed-count target:
- iteration 10: all 8 mature, mean active 818.375, max 1600, ceiling active;
- iteration 30: mean active 264.25, max 771, floor active on under-113 samples;
- iteration 50: all 8 mature, mean active 536, max 769, both band losses zero;
- iteration 90: all 8 mature, mean active 564.625, max 669, both band losses zero;
- iteration 110: mean active 676.125, max 906, mild ceiling activation;
- iteration 130: mean active 304.375, max 462, one under-floor sample and mild floor activation;
- iteration 150: all 8 mature, mean active 459.25, max 639, both band losses zero;
- iteration 200: all 8 mature, mean active 704.75, max 984, ceiling active.

The candidate therefore demonstrates that hidden liveness can be sustained without a direct life target mask.

GROWTH / DAMAGE / RECOVERY
pre-damage hidden-life cells:            1082
post-damage hidden-life cells:            795
final recovery hidden-life cells:         797

pre-lesion global visible MSE:             0.0673088878
post-lesion global visible MSE:            0.0621344075
final recovery global visible MSE:         0.0442852266

DamageEffect:                              -0.0051744804
RelativeDamageEffect:                      -0.0768766287
ActiveCellRemovalFraction:                  0.2652495379

RecoveryFraction:                          undefined
stable T50:                                not attained

The lesion again improved visible morphology.
Regeneration inference is invalid.

PERSISTENCE / HOMEOSTASIS
initial hidden-life cells:                1047
maximum hidden-life cells:                1049
final hidden-life cells:                   750
final active-cell drift:                  -297

initial global visible MSE:                0.0645831600
maximum global visible MSE:                0.0682063028
final global visible MSE:                  0.0488450378
maximum MSE degradation:                   0.0036231428
visible-state drift MSE:                   0.0220685005

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
VIABILITY RESTORED,
BUT FORMATION OVERGROWTH AND VISIBLE-MORPHOLOGY COUPLING REMAIN

CANDIDATE WORTH WIDENING
NO

MECHANISTIC INTERPRETATION
STAB-16 establishes a useful positive result inside an overall negative candidate:

1. Decoupled hidden liveness does not inherently require visible-alpha/liveness conflation.
2. A minimal locally reachable positive viability signal is sufficient to prevent hidden-life collapse.
3. The FRONTIER-FLOOR / CEIL deadband can repeatedly allow hidden life to enter the accepted 113..800 range without specifying which cells must live.
4. ATTRACT-16 can remain active once viability is restored.

However, restoring hidden-life viability did not restore target-critical visible morphology.

The canonical evaluation still starts overgrown:
1082 active before lesion;
1047 active at persistence start;
peak 1049.

More importantly, removing 26.5% of hidden life improves visible morphology rather than damaging it.

This means a substantial fraction of the sustained latent support is still morphologically redundant or negatively coupled to the visible phenotype.

STAB-16 therefore narrows the unresolved seam from:
"how to keep decoupled life alive"
to:
"how to make viable latent support causally useful to visible morphology."

DO NOT TUNE INSIDE STAB-16
Do not:
- increase FRONTIER-FLOOR coefficient;
- change viability floor 113;
- change frontier radius or definition;
- change hidden-life threshold;
- tighten CEIL-800;
- change its STE mask;
- alter hidden L2;
- alter ATTRACT-16 horizon/coefficient/reduction;
- add a direct target life mask;
- weaken scientific gates.

RETURN BASELINES
STAB-12 remains the best overall canonical phenotype by gate count: 5 / 14 failed.

STAB-16 is the best evidence that decoupled hidden liveness can be made viable without exact target-mask equality.

NEXT SCIENTIFIC SEAM
FUNCTIONAL COUPLING BETWEEN LATENT SUPPORT AND VISIBLE MORPHOLOGY.

A future mechanism should reward or preserve hidden support according to its contribution to visible target morphology, rather than:
- raw cardinality;
- exact spatial life-mask equality;
- or life existence alone.

The mechanism must remain local/developmental and must not open DG-1B cognition.

DURABLE MACHINE EVIDENCE
evidence/dg1a/p0_stab16_sandbox.json

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this result.
