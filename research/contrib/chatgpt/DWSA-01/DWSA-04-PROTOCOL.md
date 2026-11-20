# DWSA-04: constrained nonlinear-preserving structural assimilation

**Status:** prospective engineering-fixture DEV protocol, not SCIENTIFIC_PASS.
No original-world first use, donor inference, independent validation, owner
model integration, training continuation, or accepted main mutation.

**Parent negative:** DWSA-03 frozen NO-GO at PR #1335. Its exact loss and
all previous negative controls remain untouched. This is a different
mechanism/next experiment, never a post-result rescue of DWSA-03.

## Unchanged source

Read-only archived engineering fixture: Amalgam run #44499793023, artifact
14517860401, ZIP SHA-256
b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d,
member amalgam-joint-state.json SHA-256
576370a1963158f7dc43099360f491eb6a1e49355448922943b6dbe374d484c8.
Require engineering_fixture_only; 1,025 already-consumed rows, previous
DWSA-03 chronology, 820 fit-prefix and final 205 late-training rechecks.
The trained donor has already seen ALL the rows; no honest donor-heldout
science or unfamiliar-family transfer is being evaluated.

## Frozen representation — 320 bytes, nonlinear recipient

Preserve eight hidden tanh units per each of four trained heads (dimensions
3,5,43,45), instead of the failed P@E affine collapse. Use only frozen
stored donor weights/biases and mathematical quantization to produce a
student-native immutable 320-byte checkpoint; the original donor model is
never imported, restored, or forward-executed. The *recipient* executes a
native tanh reconstruction after decoding its own 320-byte structure.

Exact binary layout, 320 bytes total, ordered:
- 8-byte header: 4-byte ASCII DWN4, one-byte version 1, three zero reserved.
- 16 scale bytes: four pairs of binary16 big-endian scales (E, P) per head.
- 192 bytes: 768 E coefficients, four 2-bit indices per byte, high bits
  first; signed level set (-3,-1,+1,+3), scaled by head E scale.
- 32 bytes: 64 predictor P coefficients, two signed four-bit values per
  byte, high nibble first; signed range [-7,7], 15 invalid; per-head P scale.
- 32 bytes: 32 encoder biases, signed int8, same per-head E scale.
- 8 bytes: eight predictor biases, signed int8, same P scale.
- 32 bytes: full SHA-256 checksum over all first 288 bytes.

Per head E scale is max absolute encoder weight divided by 3, P scale is
max absolute predictor weight divided by 7; store each using IEEE-754
binary16 and quantize all values with **stored decoded scale**, not its
higher-precision progenitor. All-zero scale replaced by 1.0. E coefficients
use nearest among (-3,-1,1,3), ties by smaller absolute level then lower
index; P and biases use nearest-even signed integer rounding, clamped into
their supported bounds. No post-observation choice of scales, offsets,
bit-width, outliers, pruning, thresholds, or prefix. Input/head order is
fixed, not tuned.

Decoder fails closed for checksum, size, header, zero/nonfinite scales,
unsupported P encoding, invalid source tensor shape and stale archive
bytes. Three cold restores and duplicate deterministic checkpoint bytes.
Valid hidden-unit permutation and joint sign inversions of E row,
encoder bias, and corresponding P column must leave reconstructed
recipient probabilities equal within absolute tolerance 1e-10.
Tanh is an odd activation; this symmetry is meaningful without executing
the donor. No comparisons to donor output/activations are permitted.

## Frozen evaluation and controls

Exactly reuse DWSA-03 public fixture feature mapping and task labels,
chronology, splits and no-leakage tests; no original-world actions.
Evaluate Brier on 205 late-training rechecks separately for action
transition, action reward, temporal transition and temporal reward.
Evaluate directly from compact student weights by averaging the two
view-wise logit differences and sigmoid as frozen in DWSA-03.

Compare at minimum (1) 320B nonlinear student, (2) frozen DWSA-03 320B
affine, (3) same-320B independently fitted prefix-only logistic,
(4) untrained initializer, (5) 0.5 prediction, (6) prefix prevalence,
(7) permutation/sign-gauge versions, (8) byte corruption.
The original nonlinear donor is **not** a control because that would
require a forbidden teacher forward pass. Do not infer faithful
teacher distillation from fixed storage alone.

Falsifiable DEV signal threshold: nonlinear student must improve Brier
over BOTH 320B affine and fitted logistic by at least **0.0100 absolute
on each of the four tasks**, while preserving the 320-byte footprint,
deterministic serialisation, and 12 valid symmetries. Any failure =>
DWSA04_DEV_NO_GO. Never call a DEV pass SCIENTIFIC_PASS.

No new source first-use, training data, neural donor inference, policy
promotion, live-model modifications, integration, model rerun or API cost.
Engineering Linux-focused tests plus source hashes and full result
receipt are permitted. Separate exact-SHA cross-platform full regression,
generated atlas re-anchor, and native owner review remain required.
