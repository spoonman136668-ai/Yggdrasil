TITLE: DG-1A-P0-STAB-15 — LIFE4-DECOUPLE Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
CANDIDATE: LIFE4-DECOUPLE + CEIL-800 + ATTRACT-16
EVIDENCE CLASS: MEASURED_SANDBOX

SCIENTIFIC SOURCE REVISION
5e3d52602ff38fbc2285cff9d495b79cfeb5826e

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false

The scientific source was semantically reconstructed from independently verified connected-GitHub readbacks because native GitHub checkout remained unavailable.

PRE-EXECUTION REGRESSION
192 passed
0 failed

ENVIRONMENT
Python 3.13.5
PyTorch 2.10.0+cpu
device: CPU
precision: float32

PREREGISTERED QUESTION
Can canonical P0 preserve the near-bounded STAB-12 regime while improving visible morphology and lesion salience if organism liveness is moved off visible alpha channel 3 and onto hidden channel 4?

EXECUTED MECHANISM
LIFE4-DECOUPLE:
- visible RGBA morphology remained channels 0..3;
- visible alpha remained channel 3;
- hidden liveness moved to channel 4;
- alive threshold remained 0.1;
- target channel 4 remained zero;
- seed initialized only channel 4 at the center;
- morphology losses remained visible-only;
- active-cell counts, maturity, damage geometry, persistence, and recovery used channel 4;
- target foreground cardinality remained visible-alpha derived: 113;
- CEIL-800 counted channel-4 life but protected target foreground using visible-alpha geometry;
- ATTRACT-16 remained mature-only and visible-morphology-only;
- hidden L2 remained unchanged at 0.00001 and therefore included channel 4;
- no STAB-13 TRACE-CEIL;
- no STAB-14 support-allocation term;
- no hidden-life target or survival reward.

EXECUTION
Exactly one fresh seed-0 candidate.
200 / 200 training iterations completed.
Deterministic single-writer resumable checkpoints were used.

Final checkpoint SHA-256:
ca1eba1fbbcbc8ee5f28f53817bb9d1f721cb213015f59116a846beff87e6f45

Canonical config SHA-256:
20b6407423a815d9b2beb6576f08923cf0e1e26433c502fee5dcb5b5db964237

Full evaluation SHA-256:
89b20e28cd097deb31574ba16e544408d94b5bb03b9d8199a6bc5aa45599195d

TRAINING RESULT
initial recorded loss:                    0.4483242035
minimum recorded loss:                    0.4188809395
final recorded loss:                      0.4351223707
final global visible MSE:                 0.0287033431
final foreground morphology MSE:          0.4064190388
final background alpha MSE:               0.0
final ATTRACT-16 trajectory loss:          0.0
final mature samples:                      0 / 8
final life CEIL-800 loss:                 0.0
final batch mean hidden-life cells:        0.375
final batch max hidden-life cells:         1
final hidden penalty:                      0.0001847324
non-finite state:                         NO

TRAINING DYNAMICS
Hidden life never reached the 113-cell maturity floor at any recorded checkpoint.

Representative occupancy records:
- iteration 20: mean 1.125, max 4;
- iteration 30: mean 15.375, max 94;
- iteration 40: mean 0.375, max 1;
- iteration 60: mean 0.125, max 1;
- iteration 90: mean 1.875, max 12;
- iteration 100: mean 9.375, max 63;
- iteration 110: mean 0.5, max 1;
- iteration 150: mean 1.5, max 10;
- iteration 170: mean 3.125, max 13;
- iteration 200: mean 0.375, max 1.

ATTRACT-16 therefore remained correctly inactive for the entire training run.

The hidden-life channel repeatedly produced small local expansions and then collapsed back toward seed/dead occupancy.

GROWTH / DAMAGE / RECOVERY
pre-damage life cells:             1
post-damage life cells:            0
final recovery life cells:         0

pre-lesion visible MSE:             0.0272321105
post-lesion visible MSE:            0.0274932720
final recovery visible MSE:         0.0295742173

DamageEffect:                       +0.0002611615
RelativeDamageEffect:                0.0095902033
ActiveCellRemovalFraction:           1.0

RecoveryFraction:                    0.0
stable T50:                         not attained
stable T90:                         not attained

PERSISTENCE / HOMEOSTASIS
initial life cells:                 1
maximum life cells:                 1
final life cells:                   0
final active-cell drift:           -1

initial visible MSE:                0.0272324514
maximum visible MSE:                0.0295742173
final visible MSE:                  0.0295742173
maximum MSE degradation:            0.0023417659
visible-state drift MSE:            0.0022353614

GATE RESULTS
FAIL  113 <= pre-damage active <= 800
FAIL  113 <= final recovery active <= 800
FAIL  113 <= final persistence active <= 800
PASS  maximum persistence active <= 800
PASS  final persistence active-cell drift <= 0
PASS  DamageEffect > 0
FAIL  RelativeDamageEffect >= 0.10
PASS  ActiveCellRemovalFraction >= 0.10
FAIL  stable T50 attained
FAIL  final RecoveryFraction > 0.4230230485
PASS  pre-lesion global visible MSE <= 0.0361635
PASS  final persistence global visible MSE <= 0.0361635
PASS  maximum persistence MSE <= 2x initial persistence MSE
PASS  no non-finite state

FAILED GATES
6 / 14

CLASSIFICATION
DECOUPLED HIDDEN LIFE COLLAPSED
VISIBLE SPARSE-OUTPUT LOSS REMAINED LOW
ORGANISM VIABILITY DISAPPEARED

CANDIDATE WORTH WIDENING
NO

MECHANISTIC INTERPRETATION
LIFE4-DECOUPLE cleanly demonstrates that visible-alpha/liveness conflation was providing an incidental survival constraint.

Once liveness moved to an unsupervised hidden channel:
- visible morphology loss no longer rewarded maintaining the life signal;
- the hidden life channel remained subject to the unchanged hidden-state L2 penalty;
- CEIL-800 supplied only an upper bound and was always inactive;
- ATTRACT-16 never activated because maturity was never reached;
- training repeatedly selected near-dead hidden-life states.

The low global visible MSE is not evidence of successful morphology.
It is the same sparse-target pathology observed early in P0:
a mostly blank visible output can score well on global MSE while failing foreground morphology and organism viability.

This result narrows the architecture question.

The problem is not simply that visible alpha and life must be the same channel.
A decoupled life channel is viable as an architecture class, but the present objective contains no positive coupling that makes maintaining hidden life useful to the visible developmental task.

The foreground morphology MSE remained ~0.406 despite global visible MSE ~0.029, confirming the blank-output degeneracy.

CONCLUSION
Do not:
- exempt channel 4 from hidden L2 inside STAB-15;
- reduce hidden L2 after observing collapse;
- seed visible alpha in addition to hidden life;
- add a direct hidden-life target mask inside STAB-15;
- lower the maturity threshold;
- weaken viability gates;
- re-conflate visible alpha and life merely to make this packet pass.

The next scientific seam should test an explicit POSITIVE VIABILITY-TO-MORPHOLOGY COUPLING for a decoupled life channel.

That coupling should reward sufficient organism viability only when it supports visible target development, rather than directly forcing life to equal the visible target mask or adding another raw upper-bound penalty.

A future packet may test a target-derived one-sided viability floor or other morphology-conditioned survival mechanism, but that mechanism must be separately researched and preregistered.

DURABLE MACHINE EVIDENCE
evidence/dg1a/p0_stab15_sandbox.json

BOUNDARY
P0 remains morphology/developmental-substrate research only.
This result does not establish cognition, intelligence, specialization, inheritance, or AGI.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this result.
