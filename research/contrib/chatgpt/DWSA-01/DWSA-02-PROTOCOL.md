# DWSA-02 — authentic archived trained-head structural assimilation (frozen DEV protocol)

Status: **PREREGISTERED SOURCE-ONLY DEVELOPMENT; NOT A SCIENTIFIC TRIAL**.
Research contributor to Yggdrasil only. No canonical learner, training owner, scheduler, runner, protected source action, merge, or promotion changes.

## Why this successor exists

DWSA-01 demonstrated only restricted synthetic exact circuit reconstruction and
did not precommit an input SHA. DWSA-02 uses an *authentic already-trained*
Yggdrasil experimental research checkpoint, without executing that donor.
It does **not** meet the separate third-party-donor / multiple independently
trained donor / independent-outcome requirements of a confirmatory science gate.

## Frozen custody before any DWSA-02 scoring

Repository accepted baseline: `spoonman136668-ai/Yggdrasil@5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`.
Donor originating research: Amalgam PR #1278, producing run 44499793023,
candidate `40471f649364c0829c61e28d92a575e9351056f`.
Existing custody receipt: LINEAGE01 draft PR #1322,
`research/contrib/chatgpt/YGG-LINEAGE01/recovered_research_archive.json`
(blob `bf43b222edcdce3437fd15d4754e4c763ea84c10`).

Allowed historical artifact only: Linux artifact ID **14517860401**.
ZIP byte SHA-256:
`b8504c3a9f0e44185380687f7ce3f0a7ad0347c5be03c1cd51dc3aa1bbc1051d`.
Archive member `amalgam-joint-state.json`: length **2921047** bytes;
SHA-256:
`576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8`.
Other archive members MUST NOT be used as teacher-output labels or targets.
Native-state `native_ascii` MUST NOT be restored, mutated, or treated as this
experiment's recipient. No current canonical owner/accepted-state inference.

Observed read-only schema before this prereg:
`yggdrasil.ckad.native-causal-amalgam.v1`, 2 action heads and 2 temporal
heads; each has 8 hidden units and 2 readout channels; input dimensions in
locked order [3,5,43,45]; all four record 2109 gradient steps. Recheck
from exact file bytes before any compiling. Authenticity = original research
custody and recorded gradient counts, NOT source-equivalent cold restoration,
independent learned competence, or scientific qualification.

## Hypothesis, representation, and exact interface

Question: can the static encoder-to-readout *routing motif* of each trained
two-layer head be transferred from stored weight tensors into one compact
fixed-footprint tokenless native **structural candidate** without a donor
forward pass, donor activation, teacher output, training step, or task oracle?

Each head has encoder matrix E (8×d), encoder bias b (8), predictor matrix P
(2×8), predictor bias q (2). Compile only the weight-algebra products
`M = P @ E` (2×d) and `u = P @ b + q` (2), in canonical head order.
**This is NOT a Jacobian and NOT a reconstruction of tanh(P,E) inference**;
it intentionally discards hidden nonlinearity and cannot establish equivalent
behavior, transfer, reasoning, or policy quality.

For d in [3,5,43,45], 2*(sum(d)+4)=200 real coefficients. Per head,
quantize its coefficients using ONE symmetric positive float64 scale
`max(abs(coefficient))/127` (or 1.0 for all-zero); nearest-even rounding,
clamp to signed int8 [-127,127]. Locked checkpoint length = **320 bytes**:
4-byte `DWS2` magic; 1-byte version=1; 4 exact input dimensions; four
big-endian float64 scales (32 bytes); 200 signed coefficient bytes in head
order (each head outputs row0 d coefficients, row1 d, then u0/u1);
47 zero padding bytes; trailing 32-byte SHA-256 of preceding 288 bytes.
Dequantize strictly from stored bytes only. Fail closed on header, dimensions,
size, nonfinite/nonpositive scale, reserved padding, checksum or unsupported
source tensors. Uncompressed float64 donor **parameter-only** budget is
872 floats = 6976 bytes; the 21.8× comparison is NOT a model-equivalent
compression or a victory over optimized quantization.

Recipient interface proposed: a read-only external candidate carrying
2×d affine routing coefficients per head; no `PublicCausalCells.observe`
calls or model-state changes. Independent Unified Causal Intelligence Amalgam
Work chat owns any future review or integration decision.

## Frozen local DEV protocol

- Single pinned, pre-existing donor; no data access outside the archived ZIP.
- Python standard library only, CPU, deterministic ordering, no network and
  no model imports; ZIP/raw checksum before parsing; avoid consuming all
  `native_ascii` content beyond JSON decoding.
- Verify schema, exact 4-head order, dimensions, steps, numeric finite fields,
  nonzero trained weights, and shape. Reject all deviations.
- Calculate independent direct matrix-product reference from the serialized
  donor weights (static algebra only), not via donor inference or its source
  prediction methods; measure max absolute coefficient error and normalized
  `L2` error for the 200 dequantized coefficients.
- Compare (A) fixed-320-byte quantized structural candidate, (B) exact
  unquantized algebraic route oracle (should be the upper bound), (C)
  same-320-byte independently implemented ordinary uniform int8 product
  quantization (expected tie), (D) cross-hidden-column shuffled readout
  sham, and (E) zero coefficients. Strong conventional baselines cannot
  be declared beaten by any tie. Only C is a matched-footprint control.
- Deterministic 3 hidden-unit permutation/sign-gauge transformations per
  head: jointly permute corresponding E rows/b, P columns, and optionally
  invert both E row + b and the matching P column sign. For this *linear
  algebraic projection*, products are invariant; report coefficients'
  maximum difference, and whether 320-byte restores match within
  quantization tolerance. This symmetry applies to tanh networks too, but
  equivalence of their full predictions is NOT tested.
- Corrupt checksum, alter pinned archive byte, tamper head shapes/steps,
  create nonfinite tensor, truncate native checkpoint, and alter padding.
  All must reject. No donor import/forward invocation is permitted.
- Three cold deserialize/rehash cycles, deterministic duplicate compilation.
- Primary metrics: exact verified source hashes; 4 accepted head shapes;
  200 reconstructed coefficients; 320 checkpoint bytes; coefficient max/L2
  errors vs exact weight algebra; sham/zero error; 12 valid signed-gauge
  cases (3 per head); invalid artifact rejection; measured source-only
  CPU seconds and memory; calls to donor = 0.
- Fixed engineering pass: exact source matches, all 4 heads accepted,
  320-byte checkpoint and restores, 12 invariant gauge cases to <=1e-12
  coefficient error, and valid quantization max error <= scale/2 + 1e-12
  per coefficient, all corruptions rejected, zero donor calls. The exact
  algebraic oracle and ordinary product quantization must be reported even
  if they tie. Any breach is a DEV NO_GO/INVALID, with preserved negatives.
- No output selection, threshold adjustment, or new hidden evaluation
  data after this protocol. A separately frozen protocol and owner permission
  are required for future witness-based functional scoring, cold retention,
  interference, unfamiliar transfer, or a third-party independently trained
  donor. **SCIENTIFIC_PASS impossible in DWSA-02.**

## Explicit result classification

- Engineering LOCAL_DEV_PASS is at most a static *structural* transfer and
  checkpoint-integrity finding, not demonstrated useful learned behavior.
- SCIENCE: UNVERIFIED irrespective of local algebraic metrics; no new
  original-environment use, trained conventional control, held-out action
  outcome, or measurable retention/transfer is authorized here.
- Deployment: NONE. No model promotion, learner restart, or accepted ref edit.
- CI: Mandatory candidate-SHA Linux/Windows full regression and G29 atlas
  qualification remain separate from the static local DEV analysis.
