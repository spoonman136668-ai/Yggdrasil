TITLE: DG-1A-P0-STAB-14 — BALANCED-HARD-ALLOC Result
DATE: 2026-09-17
STATUS: CLOSED NEGATIVE
TRACK: DG-1A
CANDIDATE: BALANCED-HARD-ALLOC + CEIL-800 + ATTRACT-16
EVIDENCE CLASS: MEASURED_SANDBOX

SCIENTIFIC SOURCE REVISION
81d70262fe2f3e66d83def3fa800fdef90f3fea0

PROVENANCE
source_revision_verified_checkout = false
sandbox_source_byte_identity = false

The scientific source was semantically reconstructed from independently verified connected-GitHub readbacks.

PRE-EXECUTION REGRESSION
176 passed
0 failed

ENVIRONMENT
Python 3.13.5
PyTorch 2.10.0+cpu
device: CPU
precision: float32

PREREGISTERED QUESTION
Can the STAB-12 near-bound/contractive regime be preserved while improving morphology and lesion salience by directly aligning the exact hard living-support mask with the target foreground?

EXECUTED MECHANISM
BALANCED-HARD-ALLOC:
- exact hard alpha > 0.1 support classification;
- target foreground = target alpha > 0.1;
- forward loss = 0.5 * false-positive rate + 0.5 * false-negative rate;
- false-positive and false-negative rates normalized by their own target classes;
- zero-forward straight-through gradient restricted to hard FP and hard FN alpha cells;
- endpoint only;
- CEIL-800 preserved exactly from STAB-12;
- ATTRACT-16 preserved exactly from STAB-11;
- no STAB-13 TRACE-CEIL term;
- no weight, coefficient, threshold, temporal-scope, ceiling, or horizon sweep.

EXECUTION
Exactly one fresh seed-0 candidate.
200 / 200 training iterations completed.
Deterministic single-writer resumable checkpoints were used.

Final checkpoint SHA-256:
7c935be3015774e8eaf78e2a0e2032f77ee8ed8d99a036731ffb7935f544f4c6

Canonical config SHA-256:
263351a199f6c7757517e7d27c53743c3c601113b2976f6d1a6ebc4f2ac7211c

Full evaluation SHA-256:
81e16e4bfd5110d147b5d7fe72c7240bb8a71fb3cdf867cd3890c7daccda02af

TRAINING RESULT
initial recorded loss:                    0.9415307641
minimum recorded loss:                    0.6897137761
final recorded loss:                      0.9957820177
final global morphology MSE:              0.0589801818
final foreground morphology MSE:          0.1177192703
final background alpha MSE:               0.0376449861
final ATTRACT-16 trajectory loss:          0.2149733454
final CEIL-800 loss:                      0.2152482271
final support-allocation loss:             0.3512153029
final false-positive rate:                 0.6946872473
final false-negative rate:                 0.0077433628
final true-positive target cells mean:   112.125 / 113
final batch mean active cells:          1145.125
final batch max active cells:           1331
final mature samples:                      8 / 8
non-finite state:                         NO

TRAINING DYNAMICS
The allocation loss did not settle to a stable balanced support regime.

Representative records:
- iteration 100:
  FP rate 0.7025, FN rate 0.0077, max active 1435;
- iteration 120:
  FP rate 0.2841, FN rate 0.4558, max active 824;
- iteration 140:
  FP rate 0.4960, FN rate 0.1582, max active 1238;
- iteration 160:
  FP rate 0.3375, FN rate 0.2644, max active 915;
- iteration 180:
  FP rate 0.4380, FN rate 0.2954, max active 1164;
- iteration 200:
  FP rate 0.6947, FN rate 0.0077, max active 1331.

The model repeatedly traded false positives against false negatives rather than finding the STAB-12 near-bound allocation regime.

GROWTH / DAMAGE / RECOVERY
pre-damage active cells:          1097 / 1600
post-damage active cells:          613
final recovery active cells:      1078

pre-lesion global MSE:             0.0587935299
post-lesion global MSE:            0.0537803695
final recovery global MSE:         0.0624851994

DamageEffect:                      -0.0050131604
RelativeDamageEffect:              -0.0852672125
ActiveCellRemovalFraction:          0.4412032817

RecoveryFraction:                  undefined
stable T50:                        not attained
stable T90:                        not attained

The lesion again improved morphology.
Regeneration inference is invalid.

PERSISTENCE / HOMEOSTASIS
initial active cells:              1014
final active cells:                1112
maximum active cells:              1477
final active-cell drift:             +98

initial global MSE:                0.0554905981
final global MSE:                  0.0712424740
maximum global MSE:                0.0873765945
maximum MSE degradation:           0.0318859965
visible-state drift MSE:           0.0189572610

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
HARD SUPPORT ALLOCATION SATURATED TARGET FOREGROUND
BUT REINTRODUCED WIDESPREAD FALSE-POSITIVE SUPPORT
AND UNBOUNDED PERSISTENCE

CANDIDATE WORTH WIDENING
NO

MECHANISTIC INTERPRETATION
BALANCED-HARD-ALLOC did not preserve the STAB-12 near-bound regime.

The final training record covered almost all target foreground:
112.125 / 113 true-positive target cells on average,
with false-negative rate only 0.00774.

However, it simultaneously accepted very large false-positive living support:
false-positive rate 0.69469,
batch mean active 1145.125,
batch max active 1331.

The scientific evaluation confirmed that this was not a harmless training-batch artifact:
- pre-damage active: 1097;
- persistence: 1014 -> 1112;
- persistence peak: 1477;
- lesion invalid;
- stable recovery absent.

The class-normalized 0.5 / 0.5 construction creates much larger per-cell straight-through magnitude for a missed foreground cell than for an extra background cell because the target foreground contains 113 cells while target background contains 1487.

That property was preregistered and must not be retuned after observing this result.

STAB-14 therefore does not establish that exact hard target-mask overlap is the correct remaining morphology seam.

CONCLUSION
Return to STAB-12 as the useful directional baseline.

Do not:
- tune FP/FN class weights;
- tune allocation coefficient;
- move BALANCED-HARD-ALLOC onto future ATTRACT states;
- change alpha threshold;
- tighten CEIL-800;
- alter ATTRACT-16.

The next scientific seam should represent morphologically useful support without forcing exact equality between the hard living-support mask and the visible target mask.

Candidate directions should distinguish:
- target-visible morphology,
- hidden/auxiliary living support,
- redundant exterior support,
rather than assuming every living cell must coincide with target-visible foreground.

DURABLE MACHINE EVIDENCE
evidence/dg1a/p0_stab14_sandbox.json

BOUNDARY
P0 remains morphology/developmental-substrate research only.
This result does not establish cognition, intelligence, specialization, inheritance, or AGI.
Do not begin DG-1B, ancestor inheritance, structural growth, developmental adapters, or Fibonacci scheduling from this result.
