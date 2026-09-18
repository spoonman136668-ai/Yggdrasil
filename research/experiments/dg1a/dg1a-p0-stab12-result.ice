TITLE: DG-1A-P0-STAB-12 — CEIL-800 + ATTRACT-16 Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
CANDIDATE: CEIL-800 + ATTRACT-16
EVIDENCE CLASS: MEASURED_SANDBOX

SCIENTIFIC SOURCE REVISION
19c758e7d006b3a4da46ee5d5c15ce01acf5fba4

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false

The scientific source was semantically reconstructed from independently verified connected-GitHub readbacks because a native byte-identical checkout could not be established.

PRE-EXECUTION REGRESSION
148 passed
0 failed

ENVIRONMENT
Python 3.13.5
PyTorch 2.10.0+cpu
device: CPU
precision: float32

PREREGISTERED QUESTION
Could the contractive persistence behavior discovered in STAB-11 be retained while preventing severe formation-stage overgrowth by adding a one-sided hard occupancy ceiling at the already frozen 800-cell canonical gate?

EXECUTED MECHANISM
STAB-11 ATTRACT-16 remained unchanged:
- maturity threshold 113 hard-active cells;
- exactly 16 RNG-neutral virtual future steps;
- full future target-state objective;
- arithmetic-mean reduction;
- coefficient 1.0;
- virtual states excluded from pool authority.

Exactly one new factor was added:
CEIL-800 formation occupancy control.

Forward semantics:
- exact hard alpha > 0.1 active-cell count;
- zero ceiling loss for hard count <= 800;
- normalized squared excess above 800.

Backward surrogate:
- straight-through only through currently active target-background alpha cells;
- no gradient to target foreground;
- no gradient to inactive background.

No ceiling, coefficient, STE, horizon, or reduction sweep was performed.

EXECUTION
Exactly one fresh seed-0 candidate.
200 / 200 training iterations completed.
Deterministic single-writer resumable checkpoints were used.

Final checkpoint SHA-256:
d599dee7a8634e459c00b3979768dbf81261b3b124551362d5967f4f8c09cdb7

Canonical config SHA-256:
9282a481baeadb4035f5cdbe65c1d7870c208ff994c6f210e125d315e09faaa0

Full evaluation SHA-256:
9b0a0a0a44752bc2b57642f3c9aa66558910742bf8326eea6c1a065d615e5064

TRAINING RESULT
initial recorded loss:                  0.4459555447
minimum recorded loss:                  0.4229927361
final recorded loss:                    0.4229927361
final global morphology MSE:            0.0345974788
final foreground morphology MSE:        0.1625714153
final background alpha MSE:             0.0184523389
final ATTRACT-16 trajectory loss:        0.2073710412
final formation ceiling loss:            0.0
final formation active mean:             588.375
final formation active max:              780
final mature samples:                    8 / 8
non-finite state:                        NO

GROWTH / DAMAGE / RECOVERY
pre-damage active cells:                 857 / 1600
post-damage active cells:                435
final recovery active cells:             655

pre-lesion global MSE:                   0.0456747562
post-lesion global MSE:                  0.0457243808
final recovery global MSE:               0.0318049565

DamageEffect:                            0.0000496246
RelativeDamageEffect:                    0.0010864774
ActiveCellRemovalFraction:               0.4924154026

RecoveryFraction:                        1.0
stable T50:                              59
stable T90:                              59
normalized recovery AUC:                 0.390625

The lesion finally worsened morphology rather than improving it, so the sign of lesion validity was restored.
However the relative effect was far below the required 0.10 threshold.

PERSISTENCE / HOMEOSTASIS
initial active cells:                    799
final active cells:                      623
maximum active cells:                    1015
final active-cell drift:                 -176

initial global MSE:                      0.0444691367
final global MSE:                        0.0434814841
maximum global MSE:                      0.0736930072
maximum MSE degradation:                 0.0292238705
visible-state drift MSE:                 0.0166738257

GATE RESULTS
FAIL  113 <= pre-damage active <= 800
PASS  113 <= final recovery active <= 800
PASS  113 <= final persistence active <= 800
FAIL  maximum persistence active <= 800
PASS  final persistence active-cell drift <= 0
PASS  DamageEffect > 0
FAIL  RelativeDamageEffect >= 0.10
PASS  ActiveCellRemovalFraction >= 0.10
PASS  stable T50 attained
PASS  final RecoveryFraction > 0.4230230485
FAIL  pre-lesion global MSE <= 0.0361635
FAIL  final persistence global MSE <= 0.0361635
PASS  maximum persistence MSE <= 2x initial persistence MSE
PASS  no non-finite state

FAILED GATES
5 / 14

CLASSIFICATION
NEAR-BOUND FORMATION WITH TRANSIENT PERSISTENCE OVERSHOOT
LESION SIGN RESTORED BUT TOO WEAK
MORPHOLOGY THRESHOLDS STILL MISSED

CANDIDATE WORTH WIDENING
NO

MECHANISTIC INTERPRETATION
STAB-12 materially narrowed the canonical P0 failure.

Compared with STAB-11:
- pre-damage active cells improved from 1252 to 857;
- persistence initial active cells improved from 1160 to 799;
- persistence final active cells remained bounded at 623;
- persistence drift remained contractive at -176;
- final recovery active cells entered the accepted range at 655;
- lesion DamageEffect changed from negative to positive.

The new formation ceiling therefore did what it was designed to do directionally:
it moved the organism much closer to the accepted occupancy regime without destroying the contractive ATTRACT-16 persistence behavior.

But the remaining failures are not removable by simply tightening the same ceiling after observing the result.

Formation still overshot the occupancy ceiling:
857 pre-damage active cells.

Persistence began inside the accepted range but transiently expanded to:
1015 active cells.

The lesion became directionally valid but remained nearly morphology-neutral:
RelativeDamageEffect = 0.0010864774.

Morphology remained above the frozen target:
pre-lesion MSE 0.0456747562;
final persistence MSE 0.0434814841;
required <= 0.0361635.

The persistence trajectory is especially informative:
799 -> peak 1015 -> 623.

This indicates that raw endpoint cardinality control is now close, while the remaining defect includes transient support allocation and target morphology quality.

CONCLUSION
The combined evidence from STAB-11 and STAB-12 supports retaining direct future target-state supervision and a formation occupancy constraint as established directional components.

Do not:
- lower the 800 ceiling after seeing this result;
- increase the CEIL-800 coefficient;
- alter the STE mask;
- change ATTRACT-16 horizon or coefficient;
- weaken any scientific gate.

Those would be post-result parameter ratchets rather than a new discriminating mechanism.

NEXT SCIENTIFIC SEAM
STAB-13 should target support allocation / transient persistence morphology rather than raw endpoint cardinality alone.

The strongest current clue is that:
- endpoint occupancy can be acceptable;
- the trajectory still overshoots in active support;
- morphology error rises substantially before contracting;
- lesion salience remains extremely small.

A useful next mechanism should therefore distinguish target-support structure from excess living support over the persistence trajectory without reintroducing STAB-06's broad threshold pressure.

No STAB-13 mechanism is selected by this result.

DURABLE MACHINE EVIDENCE
evidence/dg1a/p0_stab12_sandbox.json

BOUNDARY
P0 remains morphology/developmental-substrate research only.
This result does not establish cognition, intelligence, specialization, inheritance, or AGI.

Do not begin:
- DG-1B functional computation;
- ancestor inheritance;
- structural growth;
- developmental adapters;
- Fibonacci scheduling.

Fibonacci remains separate DG-1A-FIB1.
