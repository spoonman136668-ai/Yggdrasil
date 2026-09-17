TITLE: DG-1A-P0-STAB-10 — HOME-T16 Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
CANDIDATE: HOME-T16
EVIDENCE CLASS: MEASURED_SANDBOX

SCIENTIFIC SOURCE REVISION
7d19c34cb59d96d2d94e2d8e5b92fcf4c7255e77

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false

The scientific source was semantically reconstructed from independently verified connected-GitHub readbacks because a native byte-identical checkout could not be established.

PRE-EXECUTION REGRESSION
123 passed
0 failed

ENVIRONMENT
Python 3.13.5
PyTorch 2.10.0+cpu
device: CPU
precision: float32

PREREGISTERED QUESTION
Would extending HOME-1 from one mature-only virtual step to one fixed 16-step virtual persistence trajectory produce bounded long-horizon support without changing the static objective, maturity rule, normalization, coefficient, canonical envelope, or gates?

EXECUTED MECHANISM
HOME-T16:
- mature when hard active cells >= target foreground cardinality 113;
- exactly 16 sequential virtual NCA steps;
- RNG state restored after the entire virtual trajectory;
- virtual states excluded from state-pool authority;
- per-transition positive target-background alpha velocity divided by 0.1;
- arithmetic mean across the 16 transition losses;
- coefficient 1.0;
- no horizon or coefficient sweep.

EXECUTION
Exactly one fresh seed-0 candidate.
200 / 200 training iterations completed.
Deterministic single-writer resumable checkpoints were used.
Final checkpoint SHA-256:
166b6bf06a1596b81b82a2120562db1a18e9f98f9dd9d248cda2b87595292a4e

Canonical config SHA-256:
670c74a939e64635ab4f8490a25810626a40c466e83962e5b16d229f9a7b465f

TRAINING RESULT
initial recorded loss:                    0.4459555447
minimum recorded loss:                    0.2100088596
final recorded loss:                      0.2100088596
final global morphology MSE:              0.0618761294
final foreground morphology MSE:          0.0798158646
final background alpha MSE:               0.0504219234
final HOME-T16 trajectory velocity loss:  0.0178935546
final mature samples:                     8 / 8
non-finite state:                         NO

GROWTH / DAMAGE / RECOVERY
pre-damage active cells:          1407 / 1600
post-damage active cells:         831
final recovery active cells:      1339

pre-lesion global MSE:             0.0883897096
post-lesion global MSE:            0.0698274300
final recovery global MSE:         0.0683572218

DamageEffect:                      -0.0185622796
RelativeDamageEffect:              -0.2100049851
ActiveCellRemovalFraction:          0.4093816631

RecoveryFraction:                  undefined
stable T50:                        not attained
stable T90:                        not attained

The lesion again improved morphology.
Therefore regeneration inference is invalid.

PERSISTENCE / HOMEOSTASIS
initial active cells:              1360
final active cells:                1353
maximum active cells:              1501
final active-cell drift:           -7

initial global MSE:                0.0818152428
final global MSE:                  0.0922317058
maximum global MSE:                0.1109334379
maximum MSE degradation:           0.0291181952
visible-state drift MSE:           0.0228087734

GATE RESULTS
FAIL  113 <= pre-damage active <= 800
FAIL  113 <= final recovery active <= 800
FAIL  113 <= final persistence active <= 800
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
10 / 14

CLASSIFICATION
VIABLE BUT SEVERELY OVERGROWN
MULTI-STEP LOCAL HOMEOSTASIS DID NOT PRODUCE BOUNDED SUPPORT
INVALID LESION

CANDIDATE WORTH WIDENING
NO

MECHANISTIC INTERPRETATION
HOME-T16 does not solve the canonical P0 homeostasis problem.

The longer virtual horizon changed the trajectory shape relative to HOME-1: final persistence drift was slightly negative rather than strongly positive. However, this occurred around a grossly overgrown state:
- 1360 active cells at persistence start;
- transient peak 1501;
- 1353 active cells at persistence end.

Therefore the preregistered occupancy question still fails directly.

The nominal growth snapshot also degraded substantially relative to HOME-1:
- STAB-09 pre-damage active: 993
- STAB-10 pre-damage active: 1407
- STAB-09 pre-lesion MSE: 0.0524558015
- STAB-10 pre-lesion MSE: 0.0883897096

The lesion removed about 40.94% of active cells and improved morphology by about 21.00% relative to pre-lesion MSE. This is strong evidence that the mature phenotype still contains substantial harmful/excess support.

CONCLUSION
The failure is not adequately explained by HOME-1 having only a one-step probe.

Extending the same local positive-background velocity mechanism to a fixed 16-step virtual trajectory did not establish a bounded target attractor and worsened the nominal mature phenotype.

Do not ratchet nearby virtual horizons.
Do not tune the HOME-T16 coefficient.
Do not weaken occupancy, morphology, lesion-validity, or recovery gates.

The next discriminating packet should reconsider the objective architecture rather than another local velocity-horizon variant.

NEXT SCIENTIFIC SEAM
Prefer an explicit persistence / attractor-state training mechanism, such as a bounded persistence curriculum term coupled to target-derived viability, with one preregistered construction and no parameter sweep.

This is a design direction only.
No STAB-11 mechanism is selected or executed by this result.

DURABLE MACHINE EVIDENCE
evidence/dg1a/p0_stab10_sandbox.json

BOUNDARY
P0 remains morphology/developmental-substrate research only.
This result does not establish cognition, intelligence, specialization, inheritance, or AGI.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this result.
