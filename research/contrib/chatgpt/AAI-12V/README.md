# AAI-12V — Actual causal disambiguation under equal action budgets

**Final source-development classification: `DEV_NO_GO_NO_SCIENCE`.** A fresh experiment from qualified AAI-12P source, not a retuning of negative AAI-12U PR #1127. No accepted native Yggdrasil changes, no first-use scientific worlds, no merge, no new scheduler or controller.

## Provenance and source lockdown

Preregistration was committed before implementation/outcomes at `ddd0b9de703bb20346c02d6d91b5327a796dfb90` (Git blob `0bdbd50e01dd3bd7851901d1d3b887a79c30eab0`). Exact independent parent: AAI-12P `abd374e7dc433981df991e103d8ebdff0b5eb093`; observed main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. All source code and the 11 focused tests were committed **before** the first measured source screen. The final pre-outcome immutable branch commit was `dc645bf65f0728baf877c7c87076ccbf17ba0f10`. Exact byte-level original source/test Git blobs:

| File | Git blob |
|---|---|
| `world.py` | `c50bb7118e6632c74a123ec6c37bbeddfe9a3ca9` |
| `learner.py` | `c1b0272564a3def80902fd83d4b9701d90eb6a00` |
| `dev.py` | `8276271c17ab701b1671a0ab942ce1b649d07f03` |
| `test_dev.py` | `c6281214af8e0e3716c76296142b42d03e756c0a` |

A first *unit test* exposed missing checkpoint-integrity authentication. This was repaired with a canonical SHA256 envelope, and the corruption-negative test updated **before any developmental source-screen outcome**. All **11/11** pre-screen focused tests then passed, with exact committed blobs matching the locally executed bytes. The implementation was not changed after the first result.

## Distinct question and information budget

Does a tokenless causal learner choose *more diagnostically useful actions* by maximizing expected information gain over three latent hypotheses (donor relationship, interfering relationship, unknown relationship), compared with conventional Bayesian predictive-entropy exploration under **identical prior, posterior updates, stored two-slot relationship capacity, public evidence and real intervention budget**?

A synthetic 8-bit public input world uses a hidden 3-input Boolean relation and publicly reported input-port mappings. Donor and interfering worlds each supply eight actual one-bit-do pairs (16 public rows) and full observed 8-bit truth tables. The recipient exposes exactly two actual do pairs (four public rows) before the model selects **one additional real diagnostic do** (two more public rows). Four action policies probe a genuinely new ternary-code input, while a sham control probes an already-known code (same real action count but no new relationship information). All five arms have the **same known priors and the same outcome-update/prediction rules**. Only action selection varies. No model imports the privileged world generator or receives hidden true operator, world family/class, oracle, or withheld labels.

Twenty preregistered world groups × two independent mechanical fixture IDs × 128 evaluation inputs = **5,120 held-out inputs per arm**, with classes `reuse=8`, `changed=4`, `novel=4`, `familiar=4` world groups. Test inputs use nuisance contexts 8–15, while ALL exposure (donor/interference/receiver/probe) uses nuisance contexts 0–7. There is no input-level train/test overlap for any candidate or control.

All 200 bounded public checkpoints were cold restored. Reserved independent scientific first-use remains disarmed.

## Frozen source-only results

| Arm | Overall | Reuse | Changed | Novel | Familiar |
|---|---:|---:|---:|---:|---:|
| **Information gain (candidate)** | **0.875000** | **1.000000** | 0.734375 | 0.640625 | **1.000000** |
| Bayesian predictive entropy | **0.878125** | **1.000000** | 0.734375 | 0.656250 | **1.000000** |
| Random new probe | 0.871875 | 0.976563 | 0.734375 | **0.671875** | **1.000000** |
| Fixed new probe | 0.871875 | 0.984375 | 0.734375 | 0.656250 | **1.000000** |
| Redundant sham do | 0.796875 | 0.953125 | 0.640625 | 0.562500 | 0.875000 |

All preregistration gates are mandatory. **Six of ten fail**: overall improvement over Bayesian entropy at least +0.02 (**observed −0.003125**); changed improvement +0.06 (**0**); novel improvement +0.04 (**−0.015625**); improvement over random +0.03 (**+0.003125**); improvement over fixed +0.03 (**+0.003125**); novel-task non-inferiority within −0.02 against best other control (**candidate −0.031250 versus random**). Reuse/familiar lower bounds, changed non-inferiority, and local measured model-cost ratio ≤2× passed. This is **`DEV_NO_GO_NO_SCIENCE`**, not an infrastructure failure.

**Mechanism diagnosis:** The candidate and strongest Bayesian policy chose the *same intervention in 37 of 40* source group/fixture cases, so the proposed information-gain formulation changed actual action selection in only three cases. Its 7.8125-point overall improvement over the redundant sham arm supports the usefulness of probing new evidence, **not superiority of this particular selection policy**. Also, perfect score on known reusable/familiar structures does not prove discovery of new relationship types.

Predicted-action-and-outcome trace SHA256: `a45838d1b1e2434e9b3eed565113938d7b1755daa372882304fe462e850d2c5a`. Two executions with the same source reproduced **exactly** the trace, full accuracy table, gate decisions and classification; Python 3.13.5 Linux x86_64, local isolated container, not official project runner. Timings are diagnostics for source-specific model operation only, not independent cross-platform regression or end-to-end native integration.

## Reproduction

Run in this directory with Python 3.13:

```sh
python -m unittest -v test_dev.py
python dev.py --source-dev
python dev.py --primary    # must be denied
```

See `result.json` for exact original commit IDs, blobs, source SHA256s, timings, accuracy and reproducibility. The code and results are **in the GitHub research branch**; no ChatGPT Library artifact was created. No manual edits to `.ice/code-atlas.*` or official native source. The original G29 atlas, whole-native Windows/Linux regression, first-use independent scientific evaluation and qualified model promotion were **not run**; do not infer accepted engineering or science from focused local PASS.

### Decision / next distinct hypothesis

Preserve the negative and **do not retune** the fixed source/threshold/action mechanism. A meaningful successor would need unfamiliar structural uncertainty that creates different candidate-versus-Bayesian action choices, plus independently qualified true retention and transfer tests; it must be preregistered on new disjoint worlds. No new draft PR is needed solely to store another development NO-GO. The repository branch is intentionally isolated and unmerged.
