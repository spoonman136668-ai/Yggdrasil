# FKP18-CB7 — Causal intervention value after variable probe costs

**Decision: direct one-step intervention learning beats weak controls but loses to equally informed full-horizon exact Bayesian planning. SCIENTIFIC NO-GO. Research-only, no native promotion.**

## Frozen-first source and experiment

- Accepted Yggdrasil `main` at fork: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; isolated CB6 parent `b7e9fac479b4547e8825fed79ee0f69bcbeff7cf`.
- Preregistered source/arms/budgets/gates **before implementation and original scores** at commit `8cd229e5342d72eecfb1fffea5cbd0dc2f32d973`. Exact GitHub source/test implementation frozen by `7b12af769f6a0dd0b5ee115fde68bfeff8b73444`.
- 32 new PUBLIC synthetic worlds `82600..82631`, each with six possible source-private causal sensor identities, varying source-known probability distributions and unequal charged intervention costs. 8 worlds per four source regimes. Hidden identity is never passed to a learner or planner. Public per-channel cost and prior are **equally given to both**.
- Every policy may stop and name the sensor at any point, earning **+1** for correct or **0** for wrong, **minus every actual paid intervention cost**. Testing channel `j` produces an actual public positive/negative causal-effect observation; previously tested channels cannot be repeated. Source's hidden identity is evaluator-private.
- For each world and arm, the evaluator runs six separately instantiated actual charged source trajectories—one for each hidden channel—with no counterfactual answers supplied *to the policy*. Then it weights their earned terminal net values by the frozen public prior for an exact, noise-free estimate of *expected* net decision reward. **32 × 6 × 5 = 960 executed source trajectories**, yielding **2,159 real synthetic charged probe actions** across all five arms. This is a source-owner diagnostic, not a real-world field experiment or independently held first-use.

## Candidate, strong comparator, negative controls

The **direct-written one-step policy** stores a six-bit public posterior support mask and updates it from observed outcomes. At each decision it computes the improvement in **immediate terminal correctness** from one next paid probe; if no single probe is worth its charged cost, it stops. It cannot look ahead through a sequence of experiments.

The **independently implemented exact Bayesian full-horizon dynamic program** knows only the same source prior, costs, public observations and exactly-one structure. It recursively considers STOP and each remaining probe, including the value of later experiments conditional on a negative. It is an **expected-decision-value upper bound under these specified known source assumptions**; no correctly implemented same-information policy can improve on its expectation. Controls include CB5-like ascending fixed-order probe-until-certain, seeded random-order probing, and no-probe maximum-prior guessing. **No arm receives a hidden outcome, source feature index or after-the-fact oracle signal as an input.**

## Original prospective public development results

| Arm | Mean expected net decision reward (higher is better) | Mean correct probability | Mean charged intervention cost |
| --- | ---: | ---: | ---: |
| Exact optimal Bayesian full-horizon | **0.573830** | 90.63% | 0.332426 |
| Direct one-step intervention policy | **0.530553** | 77.79% | 0.247326 |
| No probe | 0.347271 | 34.73% | 0 |
| Fixed ascending confirmation | 0.334277 | 100.00% | 0.665723 |
| Random ascending-style probing | 0.316756 | 100.00% | 0.683244 |

The direct learner pays **less** than Bayes but also stops **too early** when a sequence of experiments has positive value despite an individual first probe appearing unprofitable. Direct minus exact Bayes **−0.0432770 net reward/world**, paired 1,000 world-bootstrap 95% interval **[−0.068184, −0.021482]**. Full-horizon Bayes is strictly higher on **13/32** source distributions and tied on **19/32**. The frozen direct-versus-Bayes near-optimality (gap ≤0.02) and unique-superiority gates both **FAIL**; the direct-versus-fixed ≥0.02 and direct-versus-no-probe ≥0.01 gates **PASS**.

This is a **mechanism-specific falsification** of a myopic direct-weight exploration strategy, not evidence of general intelligence. A stronger native architecture would need reliable planning over the delayed value of a sequence of interventions and persistent learning from retained outcomes; changing the direct policy to call the Bayesian DP would merely reproduce the conventional solution, not a new algorithmic gain.

## Engineering custody, reproducibility, and limits

- Exact local-tested and GitHub-retrieved file blobs:
  - `public_world.py=c0b6c2ad5a874162f1963833f3261e360c57ee46`
  - `policies.py=af0809fd61a51bdfdd504aedf611449f55b572f1`
  - `study.py=ac4f62c0faa31c2d50ba838529b917d4b7acfc8b`
  - `test_cb7.py=3dbc66cbda90bedcd686f37db2aa8adbdce68591`
- Linux CPython 3.13 local compile PASS, **8/8 frozen focused tests PASS before original public score**. An independent full rerun reproduced the same complete non-timing world and result records, digest `2a296ecd8c48cdb1b05c2b42801d82bc6b9c85d9c8f126e1ddf8bb401bbf37d2`.
- Independently verified that the Bayesian DP value equals actual six-hidden-identity source weighted terminal-rollout reward to within a maximum numerical discrepancy **2.22×10⁻¹⁶** across the 32 worlds. This confirms the strong comparator actually optimizes the charged source's expected outcome, not a mis-specified objective.
- Original complete 960-trajectory development result file **412,907 bytes**, SHA-256 `77feea318515f636ddc1f76fe02666ffba509268716957f7f922b951ddad0a40`; that large temporary file is not posted in chat or copied into the user library. Compact all-32-world results and frozen predicates are committed in `result.json`, with exact script/seed replay regenerating all 960 source trajectories. Provenance and absolute source receipts in `provenance.json`.

```bash
cd research/contrib/chatgpt/FKP18-CB7
python -m unittest -q test_cb7.py
python -m compileall -q .
python study.py > result.reproduced.json
```

**Important scope limits:** No across-world training or cold retention; public prior and cost model are supplied to both models. Six identities are enumerated in the evaluator to estimate expected utility, not 192 independent physically observed worlds. No noisy source, external natural-world consequence, trained GRU/SSM or model-to-model whole-process compute parity is demonstrated. Main native interface, G29 and mandatory full final Linux/Windows root regression are **UNVERIFIED**. Previous FKP17 protected DEV `978500..978531` and TRANSFER `978600..978663` remain unopened, as do all owner-private science. Accepted Yggdrasil `main`, FKP-18 PR #1114, WSP-120 #1113, DG1, ITD-02 and other model owners untouched. No new PR/workflow, paid API, runner/controller/scheduler, merge or deployment.

**Decision / research pivot:** Stop iterating this fixed six-sensor family. It proves that *short-horizon inference is insufficient*, and full-horizon exact Bayesian action-value computation is already the ceiling for the source class. The next independent, genuinely novel substrate test should learn reusable approximations of long-horizon intervention value in unfamiliar dynamics with **resource limits, retained causal consequences, fully trained conventional controls, disjoint owner-held source families and full lifecycle cost**. That is distinct from replaying the same synthetic known-source family with a new heuristic. **SCIENTIFIC_PASS=false; native promotion prohibited.**
