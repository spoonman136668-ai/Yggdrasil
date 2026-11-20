# Gate 20 — Online topology rewiring with independent fixed control

**Scientific classification: NEGATIVE DEVELOPMENT for structural superiority.** This is an isolated synthetic contributor experiment on [draft PR #1340](https://github.com/spoonman136668-ai/Yggdrasil/pull/1340), not accepted native Yggdrasil training.

## Frozen chronology

- Parent Gate19 candidate: `98b99c959509db614d751962e68f75c454d0ce66` (Gate19's supposed fixed control used the same predictor path).
- Preregistration: `c1ff29dbbdbd54444fe339982356a4913a7d0789`, before primary run.
- Frozen executable: `819f72e50d5838f6a1f33ad0fe060b5ba08ac956`, Git blob `6b9a4117ac02a32019f79ede483c33ee3649d63b`, committed before primary scoring.
- Sealed first result: `e490d56eda859b774efa1f550b09949f9ba552cc`, blob `a96019df9236abffd72d9484a13608b985d76667`.
- `audit.cjs` checks receipt arithmetic, failure thresholds and static-selector code separation; it is not an independent full learner implementation. `provenance.json` records runtime, custody and qualification limits.

## Design

160 fresh deterministic seeds: 32 each of pair XOR, 3-parent MUX, random essential 3-parent Boolean, unary, and independent-noise. Six binary physical sensors, 64 A training consequences, then a B environment with changed true parents and 32 training actions; B has 16 strictly withheld action IDs and another 16 unused IDs. Mapping, true parent indices, function family and held consequences are not learner inputs.

The active graph starts from A's selected 1–3 parent connections. Every four B observations it evaluates local add, remove and replace-one-edge neighbors on **B-training-only** leave-one-out Brier, with complexity penalty and frozen minimum improvement 0.008. A maximum of three graph edges and 260 bytes of packed A/B evidence and actual graph state are enforced.

The separately written fixed selector globally fits a 1–3-parent topology using B's full 32 fit observations. Other matched-information controls are frozen-A connections fitted to B outcomes, a Bayesian fixed-subset mixture, independently shuffled B training labels, and a p=.5 null. The Bayesian and dynamic arms share projection primitives; do not claim total implementation independence.

## Held Brier (lower is better)

| Family | Dynamic | Fully fitted static | Frozen A | Bayesian |
|---|---:|---:|---:|---:|
| XOR pair | 0.1215383305 | **0.0648435884** | 0.2792539857 | **0.0644136208** |
| MUX3 | **0.1004297429** | **0.1004297429** | 0.2544468486 | 0.1186298377 |
| Essential3 | 0.0937269964 | **0.0772226119** | 0.2307308220 | 0.0982245869 |
| Unary | **0.0559752866** | **0.0559752866** | 0.2665000805 | **0.0552272805** |
| Random labels | 0.2977779889 | 0.3035372650 | 0.2771195703 | **0.2717427941** |

- Real graph mutations: 128/128 related trials updated edges, and 128/128 ended with a graph different from source A.
- Versus frozen A: related pooled mean **+0.1648153451** Brier, paired normal 95% CI **[+0.1495229727,+0.1801077175]**.
- Versus independent fully fitted static: mean fixed-minus-dynamic **-0.0182997817**, 95% CI **[-0.0298282562,-0.0067713071]**; frozen >= +0.010 and positive-CI superiority rules **FAIL**.
- Worst related-family adaptive deficit to Bayes: **+0.0571247097** (frozen max +0.010): **FAIL**.
- Noise negative: 31/32 unrelated random-label worlds still rewired. This is structural false-positive behavior, not reliable causal discovery.
- 160/160 deterministic same-process 260-byte restoration, mid-B continuation, unchanged source A predictions and disjoint held-action checks passed. Do not infer cross-process checkpoint durability.
- Dynamic rescans local alternatives repeatedly while fixed fitted selector uses one global scan. Matched computation, time and energy are **not proven**. Held full action IDs may overlap with training in their lower-order parent patterns.

## Reproduction from exact repository source

```sh
node research/contrib/chatgpt/self-assembling-topologies/gate20/run.cjs --verify research/contrib/chatgpt/self-assembling-topologies/gate20/result.json
node research/contrib/chatgpt/self-assembling-topologies/gate20/audit.cjs
```

## Qualification and ownership

**ENGINEERING:** Git custody for protocol/source/result verified; initial result executed using isolated JavaScript V8. On head `e490d56...`, existing [CI #44766545479](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44766545479) **FAILED** on both platforms at G29 stale atlas; following Python unit tests and Node replays were skipped. Full exact-head CI is NOT PASS until atlas repair and subsequent qualification.

**SCIENTIFIC:** **NO-GO** for unique self-assembling benefit: fixed fit-end beats active learner, strong Bayesian better on critical cohorts and random noise induces spurious rewiring. No real-environment or accepted autonomous intelligence gain.

**DEPLOYMENT:** NONE. Keep contributor PR draft, do not merge, advance the canonical Amalgam checkpoint, alter main, promote science, run native first-use or control the autonomous loop.
