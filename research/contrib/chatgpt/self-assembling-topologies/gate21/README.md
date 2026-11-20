# Gate 21 — Repeated-evidence causal graph rewiring under sensor remapping

**Contributor synthetic scientific NO-GO.** Nothing here is accepted Yggdrasil native learning or Amalgam checkpoint integration.

## Frozen trial chronology

1. Prior [Gate20](../gate20/README.md) qualified head `90515a68cc0ffb00a6063600e9a7c2500c92702b`.
2. [Frozen preregistration](./prereg.json) `834c26e40562e52581997b040d6a39d3f947d337`.
3. [Executable source](./run.cjs) committed **before initial scoring** at `4b9483ba5d8a7cf487682fb0ae9c0bace90bffb0`.
4. [First sealed result](./result.json) `107ce2a011376a399581280e38b51c4ac532be92`.
5. [Receipt arithmetic and source separation audit](./audit.cjs) verifies classifications without reimplementing the full learner; [provenance](./provenance.json) gives runtime and first-use limits.

## Falsifiable question

Can repeated action-consequence witnesses avoid the Gate20 31/32 spurious topology changes on noise **without sacrificing useful causal adaptation** or losing to a fully trained fixed selector?

Six binary physical inputs. 192 new synthetic seeds across four related causal families (pair XOR, MUX3, essential3, unary), one unrelated essential3 function, and independent random noise (32 seeds each). Every source A has 64 training experiences. Target B has 32 new action IDs each repeated three times =96 training outcomes; eight of these action IDs (24 observations) are reserved as *training-only witnesses* for validating proposed rewires. Another 16 unique action IDs and outcomes are strictly held for evaluation, and 16 unique are unused. The mapping and true parents are hidden from all learners.

Online gated and ungated arms take the same action sequence, start from the same A-selected mask, and assess local connection additions/removals/swaps at B steps 32, 64 and 96. The gated arm requires fit-only leave-one-out improvement >=0.008 **and** witness prediction Brier improvement >=0.012 plus two positive interleaved witness halves. Ungated needs fit-only improvement alone. Strong controls: an independently implemented all-96-outcome globally fitted static selector, a Beta-binomial Bayesian subset mixture, source graph frozen-A, label-shuffled static and null .5. Every arm sees the same observations and adheres to a 384-byte persistent evidence ceiling; repeated computation and transient scratch are not equalized.

## Held-out Brier (lower is better)

| World | Gated | Ungated | Fully fit fixed | Bayesian | Frozen A |
|---|---:|---:|---:|---:|---:|
| XOR pair | 0.125991 | 0.128263 | **0.060811** | 0.060944 | 0.279339 |
| MUX3 | 0.084221 | **0.047469** | **0.041243** | 0.041265 | 0.238744 |
| Essential3 | 0.090338 | **0.066325** | **0.052693** | 0.054343 | 0.237818 |
| Unary | **0.057212** | **0.057212** | **0.057212** | 0.057365 | 0.272456 |
| Unrelated3 | 0.081103 | 0.055877 | **0.051011** | 0.052067 | 0.227311 |
| Independent noise | 0.259920 | 0.260122 | 0.261614 | **0.254806** | 0.254388 |

**Frozen thresholds failed:**
- Independent random noise: gated changed final topology in **13/32** trials; ungated **30/32**. Noise change rate dropped, but gated exceeds the <=20% frozen maximum (13/32=40.625%).
- Related pooled gated loss to ungated: **+0.0146231769** Brier, paired normal 95% CI **[+0.0041152456,+0.0251311082]**. Both maximum +0.01 and CI upper <=+0.02 **FAIL**.
- Fully fitted fixed minus gated: **-0.0364509289**, CI **[-0.0500767765,-0.0228250813]**. The fixed model wins, failing the >=+0.01 structural gain condition.
- Worst related Bayes advantage over gated: **+0.0650471093**, above maximum +0.015.
- Benefit versus old A topology: **+0.1676489865**, CI **[+0.1504178886,+0.1848800843]**, but this is not an advantage over a strong freshly fitted comparator.
- **192/192** synthetic in-process mid-training B64→B96 byte-state continuation, old-A preservation, held-action disjointness and 384-byte record checks PASS. This does *not* prove cross-process durable cognition.

## Reproduction

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate21/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate21/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate21/audit.cjs
```

**Engineering:** Frozen source and results committed. Full final exact-head dual-OS regression and source-pinned atlas must pass before engineering PASS; source audit is narrower than independent reproduction.

**Science:** **NO-GO** for useful evidence-gated self-assembly. Suppressing false rewires alone did not compensate for delayed adaptation; a fitted conventional model remains stronger. Further experiments should test explicit uncertainty-dependent change-point detection and calibration, but must not tune on these 192 evaluated trials.

**Deployment:** NONE. PR #1340 stays draft/unmerged; accepted main, canonical Amalgam learner, native checkpoints, runners and controllers are not changed.
