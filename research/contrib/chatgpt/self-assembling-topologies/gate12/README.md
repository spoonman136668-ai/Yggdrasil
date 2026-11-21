# Gate 12 — Hierarchical zero/one/two-parent causal model order

**Research-only, fresh-seed synthetic developmental MIXED result. Structural self-assembly superiority NOT established.** Keep this contributor evidence separate from accepted Yggdrasil, the Amalgam learner, first-use custody and checkpoint continuation.

## Experiment custody and reproduction

- [Frozen preregistration](./prereg.json), original commit `d6a8e401530029018e54571219b62b8187649b36`, before any run.
- [Committed JavaScript experiment](./run.cjs), original source commit `14d9f29088dcf1f22702b2434cd17baa54437946`; **no post-result code or protocol change**.
- [Sealed primary observations](./result.json), result commit `55e0decd0981ad83ad9b62c4c33eb88c6274bf02`.
- [Independent model-order/receipt audit](./audit.cjs), committed later at `b09318d6915a5777a72754477ec378e0efdb3c8c`. The audit independently checks the 3-way parity impossibility for a 2-input truth table and result arithmetic, not a new fully independent experimental learner.
- [Provenance](./provenance.json), including exact original source object and scope/compute limitations.

From repo root with Node (no external packages):

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate12/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate12/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate12/audit.cjs
```

## Frozen test design

Six independent binary intervention inputs, one observed noisy binary consequence, two context-tagged worlds per seed. The learner never receives true causal parent IDs, operator label, truth table, or test labels. It retains the last **64 fit observations per context**, with 48 used to select the simplest predictive structure and a separate 16 used only to test the evidence for the chosen claim; no held outcome is used for updating.

Test families (new, disjoint from Gates 10/11): genuine two-parent truth tables (`16000..16063`), single-parent unary functions (`19000..19031`), three-parent parity (`18000..18031`), random independent labels (`17000..17031`), and independent Bernoulli(0.8) labels (`20000..20031`). Each seed exposes 128 fit and 32 held interventions per world. Total **192 seeds**, **384 worlds**, **49,152 fit** and **12,288 held observations** across the five families.

All three compact learners use **260 persistent serialized bytes**, including 128 last-fit action/label pairs + two bytes per context for a zero-, one-, or two-parent route. The new hierarchical dynamic chooses among 1 marginal, 6 unary and 15 pair structures, compares against an otherwise identical **fit-end fixed** learner, Gate 11's calibrated two-parent baseline on the *same new data*, a marginal null, and a **2,640 nominal-byte** 0/1/2-hypothesis Bayesian posterior model. The Bayesian comparator assumes the 5% sensor noise and is **memory unmatched**.

## Primary development outcomes (held Brier lower is better)

| World type | Hierarchical dynamic | Same-state hierarchical fixed | Gate11-style pair-only | 2,640-byte Bayes |
|---|---:|---:|---:|---:|
| Two-parent causal | 0.0670314458 | 0.0670314458 | 0.0678962120 | **0.0471044922** |
| Unary causal | **0.0536923322** | 0.0536923322 | 0.2542640539 | **0.0517187500** |
| Unrepresentable parity3 | 0.2529803540 | 0.2529803540 | 0.2529803540 | **0.2500000000** |
| Independent random | 0.2529773007 | 0.2529773007 | 0.2538817393 | **0.2500000000** |
| Biased independent | **0.1644866635** | 0.1644866635 | 0.1644866635 | 0.1994759440 |

**One major bounded gain:** 64/64 unary parent relationships were correctly identified and preserved, versus the predecessor pair-only fallback which lost their predictive information. Unary held Brier improved **0.2005717216** absolute (paired 95% approximate CI [0.1921458265, 0.2089976168]). Macro across all four negative/out-of-two-parent test families gained **0.0503690401** absolute Brier (descriptive family-stratified 95% approximate CI **[0.0482277340, 0.0525103462]**), exceeding the prespecified 0.045 minimum.

**One falsifying failure:** true two-parent parent-set recovery reached **115/128**, missing preregistered **116/128** by one. In-family Brier was modestly **better** than Gate11-style pair baseline by 0.0008647662 (no causal-gain claim; paired 95% CI for improvement contains zero). The dynamic and fixed hierarchical learners **tied exactly** on final predictions across all five families. Dynamic pair/candidate comparison work was **937,984** vs fixed **280,576** over in-family seeds (~3.34× more); do not claim compute/energy savings or self-assembly advantage.

Unsupported causal claims correctly rejected with order-zero predictions: **parity3 64/64**, **independent random 63/64**, **biased-independent 64/64**. Cold prediction restore was deterministic on **64/64** in-family seeds and **32/32** per other family, but continuing training after restore was NOT examined. This is not model-level cold retention or independent native scientific first-use.

## Disposition

- **ENGINEERING:** Source and preregistration committed before primary outcomes. Deterministic synthetic execution and local cold prediction parity observed. Dual-OS exact-head CI and repository regression require a separate authoritative run receipt.
- **SCIENTIFIC:** **MIXED DEVELOPMENT, NO scientific qualification or superiority.** Hierarchical model order repairs the unary prediction failure from Gate11 but misses its exact two-parent recovery threshold; tie with matched fixed disproves a special advantage from repeated structural rewiring. Bayesian control remains better on actual pair causal prediction.
- **DEPLOYMENT:** None. No canonical model, checkpoint, owner-runner or production refs altered. Keep [PR #1340](https://github.com/spoonman136668-ai/Yggdrasil/pull/1340) draft and unmerged.

Follow-on: do not retune this Gate12 on its seed cohorts. A separate preregistered native-compatible experiment should test causally informative *action choice*, cold training continuation, and transfer to unfamiliar compositional operators, against matched fully trained conventional and Bayesian controls before central Amalgam review.
