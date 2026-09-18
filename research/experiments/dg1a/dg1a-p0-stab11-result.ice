TITLE: DG-1A-P0-STAB-11 — ATTRACT-16 Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
CANDIDATE: ATTRACT-16
EVIDENCE CLASS: MEASURED_SANDBOX

SCIENTIFIC SOURCE REVISION
6db241bce7ba21c51baedb80152f0e031bf233de

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false

The scientific source was semantically reconstructed from independently verified connected-GitHub readbacks because a native byte-identical checkout could not be established.

PRE-EXECUTION REGRESSION
135 passed
0 failed

ENVIRONMENT
Python 3.13.5
PyTorch 2.10.0+cpu
device: CPU
precision: float32

PREREGISTERED QUESTION
Would direct target supervision across a fixed 16-step mature virtual persistence trajectory produce a bounded target attractor where one-step and 16-step local velocity control failed?

EXECUTED MECHANISM
ATTRACT-16:
- maturity threshold = immutable target foreground cardinality 113;
- exactly 16 sequential mature-only virtual NCA steps;
- RNG state restored after the complete virtual trajectory;
- virtual states excluded from persistent state-pool authority;
- each future state receives the full static morphology objective:
  GlobalVisibleMSE + ForegroundVisibleMSE + BackgroundAlphaMSE;
- the 16 future target losses are arithmetic-mean reduced;
- the auxiliary coefficient is 1.0;
- the normal rollout endpoint keeps its original static loss;
- no horizon, coefficient, or reduction sweep.

EXECUTION
Exactly one fresh seed-0 candidate.
200 / 200 training iterations completed.
Deterministic single-writer resumable checkpoints were used.

Final checkpoint SHA-256:
daf4c43152dfbf13e7781ed458cebdbfb5bca2f555e5a332d0ffdf5374a1f0c4

Canonical config SHA-256:
90879b9c8a8c7cadde77db23fc1c2f63df7ca354b3b52d602f6f870c08d7b05c

TRAINING RESULT
initial recorded loss:               0.4459555447
minimum recorded loss:               0.3962120116
final recorded loss:                 0.3962120116
final global morphology MSE:         0.0424258895
final foreground morphology MSE:     0.1203744709
final background alpha MSE:          0.0351579934
final ATTRACT-16 trajectory loss:     0.1982530355
final mature samples:                8 / 8
non-finite state:                    NO

GROWTH / DAMAGE / RECOVERY
pre-damage active cells:          1252 / 1600
post-damage active cells:         701
final recovery active cells:      882

pre-lesion global MSE:             0.0665020347
post-lesion global MSE:            0.0562916957
final recovery global MSE:         0.0404028222

DamageEffect:                      -0.0102103390
RelativeDamageEffect:              -0.1535342344
ActiveCellRemovalFraction:          0.4400958466

RecoveryFraction:                  undefined
stable T50:                        not attained
stable T90:                        not attained

The lesion again improved morphology.
Therefore regeneration inference is invalid.

PERSISTENCE / HOMEOSTASIS
initial active cells:              1160
final active cells:                592
maximum active cells:              1335
final active-cell drift:           -568

initial global MSE:                0.0616273582
final global MSE:                  0.0547853708
maximum global MSE:                0.0852470100
maximum MSE degradation:           0.0236196518
visible-state drift MSE:           0.0300126895

GATE RESULTS
FAIL  113 <= pre-damage active <= 800
FAIL  113 <= final recovery active <= 800
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
9 / 14

CLASSIFICATION
OVERGROWN INITIAL PHENOTYPE WITH STRONG CONTRACTIVE PERSISTENCE
TARGET-TRAJECTORY SUPERVISION IMPROVED ATTRACTOR DIRECTION
CANONICAL HOMEOSTASIS AND LESION VALIDITY STILL FAILED

CANDIDATE WORTH WIDENING
NO

MECHANISTIC INTERPRETATION
ATTRACT-16 produced the clearest long-horizon directional improvement in the current stabilization series.

Unlike HOME-1 and HOME-T16, persistence did not continue expanding:
- STAB-09 drift: +465;
- STAB-10 drift: -7;
- STAB-11 drift: -568.

The STAB-11 persistence trajectory also moved into the preregistered final occupancy range:
- persistence initial active: 1160;
- persistence peak active: 1335;
- persistence final active: 592.

Persistence morphology improved over the 96-step trajectory:
- initial MSE: 0.0616273582;
- final MSE: 0.0547853708.

This supports the hypothesis that direct future target-state supervision is more effective at shaping the long-horizon attractor than local positive-alpha velocity suppression alone.

However, ATTRACT-16 does not satisfy the canonical question because the system reaches the persistence regime already severely overgrown:
- pre-damage active: 1252;
- persistence initial active: 1160;
- persistence peak active: 1335.

The lesion removed about 44.01% of active cells and improved morphology by about 15.35% relative to pre-lesion MSE, so substantial harmful/excess structure remained in the nominal mature phenotype.

The final persistence state is bounded in occupancy but still misses the morphology gate:
0.0547853708 > 0.0361635.

CONCLUSION
Direct future target supervision changes the attractor in the desired direction, but it acts too late relative to phenotype formation and does not prevent the model from first entering a severely overgrown mature state.

Do not ratchet ATTRACT-16 horizon length.
Do not tune its coefficient or reduction after observing this result.
Do not weaken occupancy, morphology, lesion-validity, or recovery gates.

NEXT SCIENTIFIC SEAM
The next mechanism should change how viable support occupancy is represented or controlled during formation, while preserving the directional benefit of trajectory-level target supervision.

A promising class is a target-derived differentiable occupancy-setpoint mechanism that penalizes excess living support relative to the target cardinality without applying the broad threshold pressure that caused STAB-06 collapse.

This is a design direction only.
No STAB-12 mechanism is selected or executed by this result.

DURABLE MACHINE EVIDENCE
evidence/dg1a/p0_stab11_sandbox.json

BOUNDARY
P0 remains morphology/developmental-substrate research only.
This result does not establish cognition, intelligence, specialization, inheritance, or AGI.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this result.
