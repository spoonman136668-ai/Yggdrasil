# DWSA-01 — teacher-free direct structural assimilation (research-only)

## Question

Can a fixed-footprint native circuit be **compiled solely from frozen numerical
weights**, without executing the donor model? The target is useful structural
knowledge transfer, not distillation or imitation of model outputs.

**Scope:** This first gate is a synthetic, strictly restricted compiler-feasibility
experiment. It is not an authentic pretrained-model transfer experiment.

## Boundaries

- Accepted Yggdrasil main at start: \`5e74f8db85b2f5839c42148c0dfba69a88b1a2c9\`.
- Pre-score preregistration: \`6541fce463b8d6b868c1ccdef2ee01a557ad258b\`.
- First scored implementation/test exact branch head:
  \`f46122a5a2acb0c9dda4233a219e4c950abaeb7c\`.
- Changes only in this isolated contributor directory. No accepted learner,
  official owner loop, queue, scheduler, runner, native checkpoint, training,
  merges, protected first-use, or deployment is authorized.
- \`yggdrasil/public_causal_cells.py::PublicCausalCells.observe\` is **not** an
  assimilation API. It must not be used to forge witnessed action/outcome counts.
  The only potential future seam is an external read-only structural candidate
  consumed by the unified Amalgam coordinator following independent evaluation.

## Mechanism

The donor source is a **numerical artifact**, with 12 restricted ReLU-like
hidden conjunction units on 8 binary input coordinates and two linear score
channels. No donor network forward routine is implemented. For the restricted
family only, every hidden weight row has 2 or 3 nonzero entries of identical
absolute magnitude, with a bias admitting an exact binary conjunction, and
readout weights carrying exact integer scores after positive-scale reduction.

\`compile_weight_only(donor)\` receives only numerical \`hidden\`, \`bias\`, and
\`readout\` tensors. It does not receive the independent law specification,
labeled examples, donor outputs, or activation data. It validates the restricted
family, recovers signed binary masks and score routes, and emits an immutable
101-byte, SHA-256-checked, 16-slot native router. Supported hidden permutations
and positive diagonal rescalings leave behavior invariant. Unsupported shapes,
motifs, biases, routes, forged counts and tampered checkpoints reject.

## Local development outcome (NOT confirmatory science)

- 3 synthetic source seeds, 768 distinct input/world pairs, 3 gauge variants
  per source plus original = **3,072/3,072 score and action matches**.
- 3/3 cold checkpoint restores; **8/8 focused unit tests PASS** locally.
- Donor forward passes: **zero**.
- Numeric donor float64 serialization: **1,056 bytes** versus **101 bytes**
  native checkpoint (**10.455x** reduction). This is **not** a fair advantage
  over optimized/quantized conventional compression.
- Route-shuffled sham: **279/626** correct non-tie decisions on the original
  768-case cohort. Independent exact symbolic evaluator: **exact tie**.
- Environment: Linux Python 3.13.5, standard library only.
- Read \`result.json\` and \`provenance.json\` for exact metrics and hashes.

**Protocol deviation:** The preregistration's input SHA-256 field was left
null; only deterministic seed specification and source code were pinned before
scoring. Post-run donor hashes are recorded for reproducibility, but cannot be
retroactively treated as precommitted. Python 3.12, mandatory Linux/Windows full
regression and independent G29 qualification have not run. Evidence is therefore
**LOCAL_MECHANICAL_DEV_PASS, UNPREREGISTERED_FOR_CONFIRMATORY_USE**.

This cannot support SCIENTIFIC_PASS, generic pretrained checkpoint transfer,
unfamiliar causal reasoning, native integration or learned intelligence.

## Reproduce

At repository root, using a compatible Python interpreter:

\`\`\`sh
python -m unittest discover -s research/contrib/chatgpt/DWSA-01 -p test_dwsa.py -v
python research/contrib/chatgpt/DWSA-01/dwsa.py
\`\`\`

## Next independently frozen gate

DWSA-02 must use an **already-trained, appropriately licensed third-party
donor artifact**, fixed input/output alignment, precommitted source bytes and
hash, and independent ground-truth cases. Precommit the entire datum,
interface mapping, negative controls, output metrics and matched resource
accounting before running. Compare against exact structural compilers,
optimized quantization/SVD or model-specific compression, and fully trained
same-capacity conventional controls. Include permutation/gauge corruption,
unfamiliar-input transfer, cold restoration, retained prior capabilities,
and all-in wall time/memory. Reject models outside the identifiable structural
family rather than claiming their motifs are semantically decoded.

Submit any future useful result as a **proposal only** to the Unified Causal
Intelligence Amalgam Work coordinator; no separate canonical learner.
