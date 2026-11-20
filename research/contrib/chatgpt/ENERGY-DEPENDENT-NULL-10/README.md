# ENERGY-DEPENDENT-NULL-10 — Exact false causal-effect risk with correlated delayed outcomes

**2026-11-20 · Independent source-free analytical contribution · ENGINEERING: EXACT ARITHMETIC PASS · SCIENCE: NO NEW LEARNING GAIN · DEPLOYMENT: NONE**

## Question and predecessor

In [ENERGY-DELAY-07](../ENERGY-DELAY-07/README.md), a threshold-only lagged intervention detector identified genuine delayed direction/sign on 24/24 non-null synthetic worlds but falsely declared action effects on 4/12 NULL worlds. [ENERGY-NULL-ALLOC-09](../ENERGY-NULL-ALLOC-09/README.md) proved that its one-lag false-effect rate under the original randomized source model was 12.920102%, and that its three-lag family-wise false-effect probability lay within **12.920102%–38.760307%**. Those were bounds, not a point estimate, because all lag outcomes within an episode share hidden nuisance U.

This gate computes the **exact** three-lag false-alarm risk under that same generator—not a new neural learner, not a trained model and not a replay of the consumed scientific primary seeds. It stays exclusively on the independent contributor [draft PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346); the central cumulative Yggdrasil learner remains under its own [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).

## Frozen source and mathematical model

- Frozen original source: [ENERGY-DELAY-07/experiment.mjs](../ENERGY-DELAY-07/experiment.mjs) commit `299f728e0fb6b397300286c935350cbdc7736193`, exact Git blob `b6b282dfea714bc22b709058534e4bec49c9cc78`.
- [Preregistration](prereg.json) committed **before** the mathematical code at `2ad34543c842ac249bf333220bbf652152041cc1`.
- [First exact BigInt certificate](certificate.mjs) committed `aaa7e3277696dc61da1cb46200d2d7936f42224e`, Git blob `5b5957fdf861250bb3f1da288190e61f4708ed2e`, fetched from GitHub and verified byte-for-byte **before computing**.
- The original [exact result](result.json) committed `9b26898b7d5ef2d359ed9dfc9745ff2e9c075a58`, Git blob `3f91f2a8769a828d1897ea14a3558b446c107e00`.
- An [independently implemented mathematical audit](audit.mjs), committed `eccfd03340c55f2e7a9174308f513f006145570c`, Git blob `03eaedeb171dcfdafca0635f84e8515f603ea3b4`, re-enumerated the same exact probability using a distinct closed-form combinatorial implementation, **without any original-world or original experiment replay**. **PASS**.

Under the original NEW/NULL synthetic generator, each of 24 intervention episodes has randomized binary A, independent nuisance U~Bernoulli(.5), and three binary lag outcomes conditionally independent **given U**. For every lag, the outcome success probability is 0.8 if U=1 and 0.2 if U=0; A has no true causal effect. Because U is shared among that episode's three outcomes, the lagged outcomes are correlated marginally. The public proxy Z plays no role in the original intervention-only action contrast.

For a latent profile with n0 observed action0 episodes, n1=24−n0, u0 and u1 episodes containing U=1 in each arm:

```
P(n0,u0,u1) = C(24,n0) C(n0,u0) C(n1,u1) / 4^24.

Conditional on (n,u), the numerator polynomial for the number
of outcome successes at one lag is
    (1 + 4z)^u (4 + z)^(n-u),
with denominator 5^n.

Given the latent profile, successes are independent across
action groups AND across the three lags.

Let p_g be the exact one-lag false declaration probability
under this latent profile. Then
    P(any false among 3 | profile) = 1 − (1 − p_g)^3.
The exact unconditional FWER is this expression averaged
over all latent profiles—not 1−(1−E[p_g])^3.
```

The original contrast declares an effect if the maximum across the three lags of the absolute Beta(1/2)-smoothed action effect exceeds or equals 0.30. The conventional comparator uses exact two-sided Fisher tests per lag with Bonferroni significance threshold 1/60, under the randomized sharp no-effect null.

## Exact answer

| Frozen null-risk measurement | Exact probability |
| --- | ---: |
| Old heuristic false effect, **one** lag | **12.9201022081%** |
| Old heuristic false effect, **at least one of three correlated lags** | **31.5992849472%** |
| Fisher + Bonferroni false effect, **one** lag | **0.8451061956%** |
| Fisher + Bonferroni false effect, **at least one of three correlated lags** | **2.4234377418%** |

The source and independent audit both checked **2,925 latent nuisance/action profiles** and **396,045 conditional outcome-count pairs**, with integer probability mass conservation and exact one-lag parity to ENERGY-NULL-ALLOC-09. Full exact numerator/denominator values—not just rounded display decimals—are in [result.json](result.json).

The earlier three-lag interval **12.920102%–38.760307%** legitimately contained the exact 31.599285% value. The conventional Fisher risk of 2.423438% is within its earlier exact union bound of 2.535319% and the general 5% familywise guarantee.

## Interpretation and limits

This is decisive **only for the known synthetic NEW/NULL model**, which by construction has no causal action effect. It does **not** establish what fraction of false positives Yggdrasil's accepted native learner would make in real environments. It does **not** prove a generic intelligence improvement. It does provide a formal explanation for why the previous simple threshold frequently confused noise with delayed causal evidence.

The correct science verdict for ENERGY-DELAY-07 remains **MIXED_NO_GO**: its old 4/12 NULL false declarations are historical observations and **must not be erased, reclassified, rerun or used to retune the original 0.30 threshold**.

A routine Fisher/Bonferroni guard is **conventional statistics**. It is not a newly discovered energy-based intelligence mechanism. To move toward the user's scientific objective, the next independently frozen research trial should target unfamiliar action-consequence mechanism classes and intervention value under calibrated null control, fully matched flexible conventional baselines, functional historical retention across a real process restart, and an objective unknown-source test. Do not use already-consumed scientific seeds or promote experimental snapshots into the sole cumulative model.

## Engineering / scientific / deployment classification

- **ENGINEERING — PASS for exact arithmetic and independent implementation:** source custody, matched 1-lag marginals, correlated-lag exact integration and a second BigInt combinatorial audit. Dual-OS G29 atlas CI qualification of the research draft remains separate and failed on added indexed paths.
- **SCIENTIFIC — no new empirical/native intelligence gain:** mathematically identified and quantified a previously uncalibrated null false-effect risk. No training, unfamiliar-world transfer, cumulative cognition or protected first-use was performed.
- **DEPLOYMENT — NONE:** accepted `main`, central Amalgam PR #1278, native checkpoint, runner, controller, scheduler, and model integration are unchanged.

## Reproduce arithmetic only

After checking out this exact research branch:

```bash
node --input-type=module -e "import('./research/contrib/chatgpt/ENERGY-DEPENDENT-NULL-10/certificate.mjs').then(m=>console.log(JSON.stringify(m.exactDependentLagNull().exact_three_lag_original_fwer)))"
node --input-type=module -e "import('node:fs').then(async fs=>{const m=await import('./research/contrib/chatgpt/ENERGY-DEPENDENT-NULL-10/audit.mjs');console.log(m.auditDependentLagNull(JSON.parse(fs.readFileSync('./research/contrib/chatgpt/ENERGY-DEPENDENT-NULL-10/result.json','utf8'))))})"
```

No GitHub Actions workflow, owner-controlled scientific first-use, original experimental seeds or model are needed for this mathematical verification.
