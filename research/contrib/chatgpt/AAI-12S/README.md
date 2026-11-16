# AAI-12S — Compositional relationship construction, source-only falsification

**Outcome: `DEV_NO_GO_NO_SCIENCE`.** The tokenless program-synthesis learner achieved an important but bounded in-grammar transfer gain. It **failed** preregistered out-of-grammar non-regression and minimum-per-world consistency. No native Yggdrasil integration is justified.

## Frozen source chain

- Independent predecessor AAI-12P draft PR #1074, immutable parent `abd374e7dc433981df991e103d8ebdff0b5eb093`. AAI-12R #1123 and AAI-12Q #1076 negatives are background, **not imported or modified**.
- Frozen AAI-12S preregistration first commit **`edc51091e55d1f55a3b6007f10f1c5662ce7aa94`**, blob `d9a434c40278fad3942eec80981e13b0e66ad1a1`, before writing model, tests, or inspecting experiment outcome.
- New source exact Git blob `049fcfb46c084c0b4f8a7b460a17644a55ca31ff`, exact SHA256 `d9179898ef038becb83e7225dd946d701df25ffe781d45ff938218b851156cf9`; first implementation commit `b6f418a7862333f0a4fa668c5e67a7cbb2b24d2d`.
- Focused tests exact Git blob `ce20ba13174c946c3b7014e94790931dd87c3a5f`, commit `a20b46ad92781642d235a6637480c2731683d3df`.

## What is being learned?

The target is a previously unknown relationship assembled from **three primitive gates** XOR, AND, OR, four distinct variable bindings (from six public input bits), and optional output negation. The target graph is **never delivered to any learner**. The candidate searches the fixed typed compositional grammar and infers a circuit from public input/output consequences. No transformer, token prediction, large donor, hidden source labels, or paid model. Controls are trained deterministically on exactly the same 16 public examples: a depth-6 ID3 decision tree, 500-epoch full-batch degree-3 logistic regression, Hamming kNN-5, a table learner, plus a same-data single-gate ablation.

For every named source fixture and world, eight genuine one-bit interventions generate **16 unique public input/output observations**, and evaluation excludes all seen inputs (**48 held-out combinations per world**). The source-only screen consists of 12 unfamiliar expression worlds × 2 fixtures × 48 = **1,152 unfamiliar judgments per model**, plus 384 familiar and 384 out-of-grammar negatives. All relationships and exact fixed source sampling protocol were frozen before code.

Crucial scientific limit: the grammar already permits the compositional form of every unfamiliar source-world target. The candidate learns *which* combination to use, **not** an unrestricted new primitive operation, and is not an AGI or native-model claim.

## Corrected local-source outcome; all metrics are from the exact Git source blob

| Learner | Unfamiliar heldout | Familiar heldout | Out-of-grammar negative |
|---|---:|---:|---:|
| Compositional synthesis | **0.916667** | **0.895833** | **0.554688** |
| Best conventional unfamiliar (full-depth ID3) | 0.689236 | 0.770833 | 0.578125 |
| Best conventional out-of-grammar (Hamming kNN) | 0.638889 | 0.622396 | **0.778646** |
| Single-gate equal-data ablation | 0.679688 | 0.804688 | 0.596354 |

- Unfamiliar mean accuracy gain vs strongest conventional = **+0.227431**; frozen requirement ≥+0.05: **PASS**.
- Relative to single-gate ablation = **+0.236979**; requirement ≥+0.10: **PASS**.
- Per-world consistency: **8/12** of the transfer worlds reached ≥85% accuracy pooled over the two fixtures; requirement ≥10/12: **FAIL**.
- Out-of-grammar 0.554688 vs strongest conventional 0.778646 = **−0.223958**; maximum allowed regression 0.02: **FAIL**.
- Familiar return nonregression: **PASS**.
- Full-process cost: **UNVERIFIED**. Diagnostic stopwatch in the source script measures each fitted model + prediction but excludes the compositional grammar's one-time source-free compilation, so its time-ratio boolean must **not** be treated as a fully qualified cost gate.

Deterministic original action/prediction trace SHA256 `1979a4dee547685c87208194d3fc1c0d87f886428b52dc737f6a9eababd52cce`. A second identical local screen reproduced scores, classification, gates and trace exactly. Locally run focused **10/10 tests PASS**, including all four out-of-grammar functions provably absent from the synthesis grammar, real do transitions, equal public observations, preregistered world count and first-use denial.

The source script had a pre-outcome unpacking bug detected by the first execution (no metrics produced). This was mechanically corrected **before** the first completed source screen and frozen source upload. No after-result model, fixture, threshold or policy edits followed.

## Reproduce (independent source-only development, not primary science)

From `research/contrib/chatgpt/AAI-12S` on Python 3.13:

```sh
python -m unittest -v test_dev.py
python dev.py --source-dev
python dev.py --primary # intentionally denied
```

Exact results, full conventional scores, SHA provenance and classification are in `result.json`. The local execution environment was an isolated assistant Linux container, **not** a named Yggdrasil project owner/runner; native full cross-platform regression and GitHub-independent original scientific qualification **NOT RUN**.

**Stop / authority:** Development hypothesis did not meet all its prespecified gates. Preserve failure without repairing the result via tuning. Main/accepted refs, native models, independent research loops, other project architectures, owner/runner/scheduler/queue, and first-use cohorts are untouched. Draft is research evidence, not merge or deployment authority.
