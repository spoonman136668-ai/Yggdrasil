# AAI-12T — novelty-gated primitive induction from witnessed actions

**Status:** `DEV_NO_GO_NO_SCIENCE`, source-only local development result. **No native model integration, first-use science, merge, or deployment.** An initial checkpoint omission was repaired **after** the first local source screen; this chronology is disclosed and the result is not represented as independent sealed science.

## Exact provenance

- Independently based on **AAI-12P draft PR #1074**, commit `abd374e7dc433981df991e103d8ebdff0b5eb093`. AAI-12Q/#1076, AAI-12R/#1123 and AAI-12S/#1124 are preserved negative background, not a source/code dependency.
- Frozen source prereg **BEFORE** code or measured outcomes: commit `58b415219373484864bcf63189a7c18f3eeea711`, blob `29f79f0d6368840c76c39443ffaefaf5607a6f5f`.
- First implementation commit `a6464185a9ab1e3c91a7b946c8b2b7297eb0bf46`, exact-blob `295f0624b39f3603530c285c07b62db0dc66cb5e`. First test commit `6c2d15e4bf82b9f25085c43921de106baed0a8d6`.
- **After the first source-only run** the cold checkpoint was found to omit the explicitly learned 8-bit ternary primitive. Mechanical custody fix commit `f0f0e7084c3e0e47378446f62df211dd9a60cba5`, separate tampering-negative test commit `2cb45a83c099a412fcc83a33a8f34fc2c95ced65`. The final committed source blob is `b8bf17029cb20147042f386251192ace8928097f`, test blob `0111f2c74a5b7edd6b2a460c12cc64b298e55b12`. Each was read back from GitHub and matched to the exact local file bytes. **No change to model predictions, hypothesis, world IDs, gate, data, or thresholds.**
- The initial pre-repair cold-format result is **not** claimed as a protocol-clean confirmation. Two post-repair local source-only runs reproduced the same scores, gate decisions, and trace. They also reproduced the initial *outcome* (not the serialization format). This is mechanical development, **not independent science**.

## What the experiment can and cannot show

The source generator creates a six-input/one-output relation. Known prior grammar = exactly three XOR/AND/OR gates operating on four distinct inputs. New-source hidden targets compose an unknown 3-input 8-bit Boolean primitive (256 possible truth tables) XOR one other input. Learners receive only 32 public x/y examples from 16 genuine one-bit source interventions and cannot inspect the hidden primitive or withheld outputs. They predict the other 32 input assignments.

The candidate uses 24 public examples to fit a fixed-grammar learner, an inferred ternary primitive, and kNN. It selects the ternary expansion only if it reduces errors on eight public validation examples by at least two relative to both alternatives, then refits the selected mode to all 32. The learned primitive is now explicitly serialized and verified on cold restoration. Controls receive identical public evidence: fixed three-gate synthesis, **always-expanded with the identical 256-primitive vocabulary**, kNN5, ID3, and a selector without expansion. No role/state tokens or transformers.

The 12 novel hidden-source masks were mechanically verified **absent from the fixed grammar**, before scoring. Four familiar known-grammar worlds and four unrelated six-input tasks (parity, majority, exactly-two, hashed truth table) are mandatory retention/negative controls. Across two deterministic mechanical fixtures this is **768 novel / 256 familiar / 256 negative** held-out predictions **per arm**; **240 successful cold restored checks** across six arms.

This is bounded induction of a 3-input Boolean truth table from explicit public data. It is **not** unrestricted invention of a new relation type and does not prove cumulative knowledge retention across independent worlds.

## Exact local source-only mechanical result

| Arm | Novel transfer | Familiar retention | Unrelated negative |
|---|---:|---:|---:|
| Novelty-gated primitive induction | **0.808594** | **1.000000** | **0.570313** |
| Equally expressive always-expanded | **0.947917** | 0.734375 | 0.363281 |
| No-vocabulary-growth ablation | 0.657552 | **1.000000** | 0.570313 |
| Fixed three-gate vocabulary | 0.682292 | **1.000000** | 0.515625 |
| Fully fitted ID3 | 0.731771 | 0.859375 | 0.460938 |
| kNN5 | 0.518229 | 0.753906 | 0.582031 |

**Frozen mandatory gates (all required):**
- Novel accuracy at least +0.03 over **best** full-capacity control: **FAIL**, −0.139323 vs always expanded.
- Novel accuracy at least +0.06 vs no-growth: **PASS**, +0.151042.
- At least 9/12 novel worlds at ≥0.80: **FAIL**, only **7/12**.
- At least 8/12 novel worlds select expansion in **both** source fixtures: **FAIL**, only **3/12**.
- No more than one familiar world falsely triggers expansion in either fixture: **PASS**, zero.
- Familiar and unrelated negative non-regression within 0.03 of best eligible generic comparator: **PASS**.
- Entire source-specific model build/fitting, selection, restoration and inference ≤50× the fastest generic control: **PASS** on this one local CPU only; observed candidate 0.169666s and fastest generic kNN 0.009406s (source-free grammar compilation charged to applicable arms). This does **not** qualify cross-platform native or real-world all-process efficiency.

**Conclusion:** The proposed novelty trigger is too conservative: it does not engage the more powerful vocabulary on most novel worlds. Preserving old relationships improves substantially relative to always expanding, but this does not compensate for missed novel learning. Frozen classification **`DEV_NO_GO_NO_SCIENCE`**. Do **not** tune this candidate after seeing results, promote, merge, or consume independent science cohorts.

## Reproduction

From this directory on Python 3.13:

```sh
python -m unittest -v test_dev.py
python dev.py --source-dev
python dev.py --primary # explicitly denied
```

Final local **11/11 focused tests PASS**. Two corrected runs produced identical aggregate accuracies, gate dispositions, and deterministic action/prediction trace SHA256 `bae2cd2b1842b7115b09bd53f8884476a6484aa0fc3834aa8d6ffebd06ab6aae`. Local tool environment was isolated Linux x86_64 CPython 3.13.5, **not an authorized native Yggdrasil project runner**. No official Windows/Ubuntu exact-final regression, scientific heldout first-use, or deployment qualification performed.

All custody, metrics, and limits are in `result.json`. Native main, FORGE, Wingless, Hybrid, owners/controllers/runners/queues/schedulers, source-science first-use, and accepted refs are unchanged. Retain negative results in this unmerged research lane.
