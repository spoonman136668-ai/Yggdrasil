# ENERGY-REMAP-GATE-12 — Proof the local repair was unreachable

**20 November 2026 · Exact analytic correction to ENERGY-REMAP-11 · Engineering arithmetic PASS · Scientific mechanism FAIL · Deployment NONE**

The previous [ENERGY-REMAP-11 study](../ENERGY-REMAP-11/README.md) reported zero activated local repairs across 36 synthetic worlds. At the time that was treated as an observed negative. This follow-up strengthens the conclusion: **under the frozen experimental sample quota, the repair probability cannot possibly reach its implementation threshold**. The failure was structural rather than a random draw.

This is a source-free read-only mathematical certificate, not a new learning algorithm, new primary experiment, or permission to change a frozen threshold after seeing outcomes. The central cumulative Yggdrasil learner remains the independently owned [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).

## Original, source-verified interface

Frozen original experiment source: [ENERGY-REMAP-11/experiment.mjs](../ENERGY-REMAP-11/experiment.mjs) commit `ab203a45bd1e42a11a043055e4541d26e1676ced`, Git blob `8a5fbfa908edad48bb23804517c06bb645b5fda8`, preserved unchanged.

The original row-level mechanism used six labels, symmetric Dirichlet pseudocount **0.5**, exactly **six OLD action-conditioned categorical observations per row** and **two NEW per row**. It calculated:
- `stay = logDM(NEW_counts, OLD_counts + 0.5)`
- `reset = logDM(NEW_counts, 0.5)`
- `P(reset | NEW, OLD) = exp(log(0.25)+reset)/[exp(log(0.25)+reset)+exp(log(0.75)+stay)]`.

It would reset the row only when `P(reset | NEW, OLD) >= 0.80`. No selector, hidden world label, or learned structural alignment changes the number of observations per mapped row. This identity was checked against the original executable and [unchanged primary result](../ENERGY-REMAP-11/result.json).

## Proof — exact upper bound, not a simulation

Denote the six OLD category counts `c_0,...,c_5`, with nonnegative integers summing to six. Two NEW categorical observations either have distinct category labels `i != j` or repeat the same label `i=j`. Under the frozen symmetric Dirichlet model, the likelihood ratio favoring reset (Bayes factor `BF`) over pooling is:

**Two different labels:**

```
BF = (15/2) / [(2*c_i+1)(2*c_j+1)] <= 15/2.
```

**Two observations of the same label:**

```
BF = (45/2) / [(2*c_i+1)(2*c_i+3)] <= 15/2.
```

Both upper bounds are attainable when the NEW-observed categories received zero OLD observations. Since the frozen reset/stay prior odds are **1:3**, the largest possible reset posterior is:

```
P(reset | observations) = BF/(BF+3)
                         <= (15/2)/(15/2+3)
                         = 5/7
                         = 0.7142857142857.

Required for reset: P >= 4/5 = 0.80
                  => BF >= 12.

But BF can never exceed 7.5.
Therefore: NO eligible row can trigger the reset.
```

This is a general statement about **every** possible world subject to the exact frozen per-row data budget and prior, not a probability estimated from 36 sampled worlds.

## Two independently structured exact enumerations

1. The [precommitted mathematical specification](prereg.json), commit `48ecdd4f01fa625529a53702af98ed188bf8aa49`, was frozen before the [first exact verifier](certificate.mjs), commit `2e59fabca32ec13f2d64c4d36efedebd01136600`, Git blob `7ae8dae5d5a0388b3b57132b62c908099e5846a2`. After byte-for-byte source readback and checking the frozen original's source/results identity, it exhaustively evaluated **462** possible OLD count vectors × **21** possible unordered NEW outcome pairs = **9,702** cases. The exact maximum BF was **15/2** and exact maximum posterior **5/7**. **0/9,702** met the gate. The frozen receipt was committed to [result.json](result.json), commit `7845843f06d1c75788538bad0662559e745aa522`.
2. A distinct [ordered-outcome auditor](audit.mjs), commit `2db1c9a0b1300a5c4a8c14af4613cb0eef685938`, Git blob `5cf7035ba90f93ba1ebdf5bbe3a0db3ada7192c5`, instead directly multiplies **sequential Dirichlet predictive probabilities** (not the first implementation's Bayes-factor formulas). It exhaustively checked **462×36 = 16,632 ordered possibilities**, individually verified normalization of reset and stay predictive masses, and again found **zero** threshold crossings, maximum posterior **5/7**. The second audit result is preserved in [audit-result.json](audit-result.json) at `0c117e78c676f6dc79569fbf6ac8c73d40eb169a`. **Independent arithmetic PASS**.

No ENERGY-REMAP-11 primary seeds were rerun, no original data changed, and no new experimental science first-use is implied.

For analytical reproduction only:

```bash
node --input-type=module -e "import('./research/contrib/chatgpt/ENERGY-REMAP-GATE-12/certificate.mjs').then(x=>console.log(x.proveFrozenResetGate()))"
node --input-type=module -e "import('node:fs').then(async fs=>{const x=await import('./research/contrib/chatgpt/ENERGY-REMAP-GATE-12/audit.mjs');const r=JSON.parse(fs.readFileSync('./research/contrib/chatgpt/ENERGY-REMAP-GATE-12/result.json','utf8'));console.log(x.auditGate12(r));})"
```

## Correction and scientific decision

**The experimental candidate did not have an operative local-repair mechanism under its own protocol.** Its 36-world predictions matched a conventional MAP alignment plus pooled Dirichlet control because *the hard change gate was mathematically impossible to activate*. The observed positive difference against NEW-only tabular learning is a normal transfer benefit from mapping learned observations between labels. It is not evidence of self-directed topology repair or novel causal adaptation.

Retain ENERGY-REMAP-11's original result, consumed-seed status and frozen classification **MIXED_NO_GO**. Do not retrospectively tune the threshold from 0.80, change sample sizes on the same primary cohort, or present this mathematical proof as a scientific gain.

This closes the local hard-reset proposal as currently specified. A future substantive study would need **a distinct mechanism**, such as continuous posterior-supported causal hypothesis updates, actual decision-making interventions and genuinely unfamiliar law families, with a calibrated abstention rule and matched conventional controls. The central Amalgam research program already has overlapping context, retention and intervention experiments; do not duplicate its canonical learner or research ownership.

**ENGINEERING — PASS:** frozen source/result identity plus two different exact-integer proofs. **SCIENTIFIC — FAIL for the original adaptive local-repair claim, and no new native gain.** **DEPLOYMENT — NONE:** no accepted main, owner checkpoint, runner, scheduling or native model changes. The draft PR's original G29 source-atlas indexing CI block is independent and remains unresolved.
