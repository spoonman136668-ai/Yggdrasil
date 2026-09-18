TITLE: DG-1A-P0-STAB-13 — TRACE-CEIL-800 Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
CANDIDATE: TRACE-CEIL-800 + CEIL-800 + ATTRACT-16
EVIDENCE CLASS: MEASURED_SANDBOX

SCIENTIFIC SOURCE REVISION
422b8eec20f8089a40bb83b66f8452e0bf1b525e

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false

PRE-EXECUTION REGRESSION
163 passed
0 failed

ENVIRONMENT
Python 3.13.5
PyTorch 2.10.0+cpu
device: CPU
precision: float32

PREREGISTERED QUESTION
Could STAB-12's remaining transient persistence occupancy overshoot be removed by applying the already-frozen CEIL-800 constraint to each of ATTRACT-16's same 16 virtual future states?

EXECUTED MECHANISM
STAB-12 remained intact:
- static morphology objective unchanged;
- ATTRACT-16 unchanged;
- endpoint CEIL-800 unchanged.

Exactly one new factor:
TRACE-CEIL-800.

For each of the same 16 mature virtual future states:
- reuse exact CEIL-800 hard forward count;
- reuse exact target-background-only STE gradient mask;
- reuse 800 normalization and squared excess;
- arithmetic-mean the 16 future ceiling losses;
- coefficient 1.0.

No new horizon.
No lower ceiling.
No coefficient change.
No reduction sweep.
No STE change.

EXECUTION
Exactly one fresh seed-0 candidate.
200 / 200 training iterations completed.
No non-finite state.

Final checkpoint SHA-256:
9d14cd00abe55e61a927e243a8c1827680f17cc5ffe32e9269814e90515cf204

Canonical config SHA-256:
0eaafecf239a2e33aeb82494887a46a41f9f138682f1737c667fc115588c5fbd

Full evaluation SHA-256:
df8fa4e2123f51942308b8f89ebc0deb0c7cbfb3df581cd4e7cc59c402b742da

TRAINING RESULT
initial recorded loss:                  0.4459555447
minimum recorded loss:                  0.4079751670
final recorded loss:                    0.9951227307
final global morphology MSE:            0.0609447956
final foreground morphology MSE:        0.1257571280
final background alpha MSE:             0.0410929359
final ATTRACT-16 trajectory loss:        0.2293405533
final endpoint CEIL-800 loss:            0.2437195480
final formation active mean:             1167.75
final formation active max:              1434
final TRACE-CEIL-800 loss:               0.2942671478
final trace active mean:                 1215.046875
final trace active max:                  1446
mature samples:                          8 / 8

GROWTH / DAMAGE / RECOVERY
pre-damage active cells:                 1193
post-damage active cells:                641
final recovery active cells:             1439

pre-lesion global MSE:                   0.0645737201
post-lesion global MSE:                  0.0561438613
final recovery global MSE:               0.0883831903

DamageEffect:                            -0.0084298588
RelativeDamageEffect:                    -0.1305462783
ActiveCellRemovalFraction:               0.4626990780

RecoveryFraction:                        undefined
stable T50:                              not attained
stable T90:                              not attained

The lesion again improved morphology.
Regeneration inference is therefore invalid.

PERSISTENCE / HOMEOSTASIS
initial active cells:                    1130
final active cells:                      1456
maximum active cells:                    1517
final active-cell drift:                 +326

initial global MSE:                      0.0614977255
final global MSE:                        0.0938185528
maximum global MSE:                      0.0998317450
maximum MSE degradation:                 0.0383340195
visible-state drift MSE:                 0.0213837996

GATE RESULTS
FAIL  113 <= pre-damage active <= 800
FAIL  113 <= final recovery active <= 800
FAIL  113 <= final persistence active <= 800
FAIL  maximum persistence active <= 800
FAIL  final persistence active-cell drift <= 0
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
11 / 14

CLASSIFICATION
TRACE-WIDE OCCUPANCY PRESSURE DESTABILIZED THE STAB-12 NEAR-BOUND REGIME
GROSS OVERGROWTH RETURNED
LESION VALIDITY AND RECOVERY COLLAPSED

CANDIDATE WORTH WIDENING
NO

MECHANISTIC INTERPRETATION
STAB-13 directly rejects the hypothesis that STAB-12's remaining transient overshoot can be solved by extending the same raw-cardinality ceiling across the existing 16-step future trajectory.

Relative to STAB-12:
- pre-damage active worsened 857 -> 1193;
- persistence initial worsened 799 -> 1130;
- persistence peak worsened 1015 -> 1517;
- persistence final worsened 623 -> 1456;
- drift changed -176 -> +326;
- lesion DamageEffect changed positive -> negative;
- stable recovery was lost;
- pre-lesion MSE worsened 0.04567 -> 0.06457;
- final persistence MSE worsened 0.04348 -> 0.09382;
- failed gates increased 5 -> 11.

The additional trajectory-wide ceiling generated strong occupancy pressure during training, but that pressure did not produce bounded evaluation dynamics.

This is evidence that more repeated raw cardinality pressure is not the right seam.

Do not:
- lengthen TRACE-CEIL horizon;
- lower its ceiling;
- increase its coefficient;
- change mean to max;
- alter its STE mask;
- weaken gates.

NEXT SCIENTIFIC SEAM
Return to the STAB-12 directional baseline, not STAB-13.

The next packet should target spatial/morphological allocation of living support rather than raw active-cell count.

The core unresolved observation from STAB-12 remains:
- a near-bounded organism can have 799 active cells yet still poor morphology;
- removing nearly half of living support barely changes morphology;
- therefore support is morphologically redundant / poorly concentrated.

A discriminating next mechanism should make living support overlap target-relevant structure without blanket suppression and without changing the frozen 800-cell ceiling.

No STAB-14 mechanism is selected by this result.

DURABLE MACHINE EVIDENCE
evidence/dg1a/p0_stab13_sandbox.json

BOUNDARY
P0 remains morphology/developmental-substrate research only.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling.
