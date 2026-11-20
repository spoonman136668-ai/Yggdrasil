# Gate 15 — Prequential residual model-adequacy guard

**SCIENTIFIC DEVELOPMENT: MIXED / NO-GO. No native Yggdrasil first-use, accepted intelligence gain, or checkpoint promotion.**

This independent contributor experiment asks whether a *prequential excess-Brier calibration signal* is a better out-of-model guard than Gate 14's arbitrary count of surprising responses. It uses 160 fresh synthetic seeds and retains exact source custody.

## Custody and reproducibility

Preregistration committed **before experiment source** at `d0d372ea1e0f0f9683a115fbdc04b72b0fc21470`; [protocol](./prereg.json). Executable [source](./run.cjs) committed and frozen at `14d4cae57c419671155f21eef1c87e6e38f12dc8`, Git blob `dc8e9d160269f4446f68924fcb7a019771bab9e1`. [Results](./result.json) sealed after first primary experiment and independent exact recomputation at `20d03144afda823ad48ad1b15dadf89ac323f8dc`, Git blob `68ed056164044908f72db7c949e3c9c869d5b174`. [Independent mathematical and receipt audit](./audit.cjs) and [provenance](./provenance.json) were committed after result sealing. No post-result source or threshold tuning.

Reproduce from repo root with built-in Node.js:

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate15/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate15/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate15/audit.cjs
```

The audit independently verifies threshold arithmetic, cohort sizes, Brier deltas, equal counted posterior candidate evaluations, checkpoint size and model-family mathematics. It is **not** an independent second numerical learner.

## Design

New seed families: genuine two-parent Boolean causes `41000..41063` (64 seeds), unary `42000..42031`, unrepresentable 3-parent parity `43000..43031`, independent fair labels `44000..44031` (32 seeds each). Two contexts A/B per seed, 5 controllable binary inputs, **12 intervention-consequence observations and 32 held actions per world**. Held labels are common to all policies, generated with a disjoint noise domain, and never used for training, policy selection, or calibration.

All five policies share Gate 13's exact **113-hypothesis Bayesian prior**: 3 constant/fair null, 10 unary and 100 genuinely two-parent Boolean functions, assumed 5% noise. The original active intervention policy maximizes posterior predictive entropy; balanced and random schedules are unchanged; *fixed damp* shrinks held predictions by 30% toward 0.5. The new **residual guard** uses each observed action's *pre-update* prediction `p` and consequence `y`, accumulating excess-Brier `(p-y)^2-p(1-p)`. After 6 events, if its mean exceeds **0.06**, a sticky alarm switches subsequent actions to balanced and shrinks held predictions by 45% toward 0.5. It receives no hidden causal labels.

Every policy uses the same 12-action training budget per context, the same possible interventions and source feedback function; models may observe different consequences because their chosen actions differ. The source intentionally runs all 32 posterior candidate predictions for every arm at each action to equalize counted work; **real balanced/random implementations need much less work**. Each arm serializes exactly **1,892 bytes**, including posterior, visit counts, step, accumulated residual and alarm state for both contexts. Temporary arrays, code, process memory and hardware energy are excluded from this size.

## Frozen held outcomes — Brier (lower is better)

| World family | Residual guard | Original active | Balanced | Random | Fixed 30% null damping |
|---|---:|---:|---:|---:|---:|
| Two-parent causal | 0.0763368246 | **0.0621335370** | 0.0934772979 | 0.1158381401 | 0.0861570514 |
| Unary causal | 0.0621946285 | **0.0533105629** | 0.0564567398 | 0.0692194177 | 0.0734011821 |
| Three-parent parity | 0.3302599910 | 0.3480448764 | 0.2983303456 | **0.2809626262** | 0.2976671268 |
| Random independent | 0.2920860006 | 0.3296156818 | 0.2964462392 | **0.2831405441** | 0.2899519103 |

**Positive diagnostics:** The residual guard improves on balanced by **0.0171404734 Brier** on genuine two-parent causes (paired ~95% CI **[0.0035641567, 0.0307167900]**), clearing the minimum +0.010 and positive-CI criteria. It also improves over unguarded active on parity3 (**0.0177848854**) and random (**0.0375296812**). The random-family conservative-loss requirement passes; cold action/learner-state continuation and matched counted work pass.

**Prespecified failures:**
1. Genuine pair-world held error worsens relative to original active by **0.0142032876 Brier**, exceeding the allowed +0.010. The paired active-minus-guard interval is **[-0.0204339073,-0.0079726678]**. The guard incorrectly alarms in **33/128** real pair contexts (25.8%).
2. Unfamiliar three-parent parity retains **+0.0492973648** extra Brier above the best conservative random control (0.3302599910 vs 0.2809626262), exceeding allowed +0.015.

The guard alarms in **13/64 unary**, **40/64 parity3**, and **47/64 random** contexts. Even when unfamiliar worlds are often flagged, action selection and posterior confidence under the wrong model remain problematic. An unconditional fixed 30% shrink comparator does not establish structural superiority either; macro guard-minus-damp excess is +0.0034250435, within its frozen ceiling +0.005 but **not** an improvement.

All **160/160** seed trials passed synthetic same-process checkpoint restorations, dormant-A immutability after B training and exact four-step A action/update/prediction continuation. This is **not** native Yggdrasil training retention or external-process cold restore.

## Important correction: entropy versus mutual information

For this specific 113-hypothesis posterior, all deterministic hypotheses predict p=0.05 or p=0.95, with the same conditional entropy `h(0.05)`; the only p=0.5 hypothesis is the fair null. Its posterior weight is independent of candidate action. Therefore the expected conditional entropy term in `I(H;Y | do(x)) = h(predictive(x)) - E_H[h(p(Y|H,x))]` is **identical for all candidate actions**, so maximizing posterior predictive entropy and maximizing mutual information produce the **same action choices** (up to tie handling). This does not generalize to arbitrary heteroscedastic models. An 'MI' arm here would be a misleading duplicate.

## Disposition

- **ENGINEERING:** Frozen source and sealed results reproduced in an isolated V8 execution. Separate exact-SHA Linux/Windows CI and full repository regression required for final closure.
- **SCIENTIFIC:** **MIXED/NO-GO.** No decisive advantage over strong active plus conservative random controls on all families. Do not tune residual threshold against these tested seeds or claim native causal intelligence.
- **DEPLOYMENT:** None. Accepted `main`, central Unified Causal Intelligence Amalgam owner, checkpoint lineage and training source untouched. Keep PR #1340 draft and unmerged.

Next science candidate should directly test **model-structure adequacy** or out-of-class hypothesis construction—not another fixed threshold adjustment to a short prequential window. A native owner-controlled experiment would be separately authorized and qualified.
