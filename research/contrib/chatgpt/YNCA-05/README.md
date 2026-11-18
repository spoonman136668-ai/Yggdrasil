# YNCA-05 — an exact identifiability ceiling for causal probes

**Verdict: ANALYTIC_BOUND_SUPPORTED; NATIVE_SCIENCE_UNVERIFIED.** This is a source-free *exhaustive mathematical audit*, not Yggdrasil model training or a native intelligence gain.

## Why this gate exists

YNCA-04's cost-sensitive native probing lost to simpler controls, despite exact-source cross-platform qualification (draft PR #1222). Before adding more learned probe heuristics, this experiment asks a more fundamental question: **can the permitted evidence distinguish the causal relationships in the first place?**

The experiment was preregistered, source-locked and executed once on each OS at the same source. The original result is committed unchanged as `result.json`.

## Full-law-space identifiability proof

Enumerate all 256 truth tables of three binary inputs and one binary output. Condition on two observed diagonal outcomes `f(000)=0`, `f(111)=1`, leaving exactly 64 distinct Boolean laws. The six other truth bits are free and mutually independent under a uniform prior. With only noiseless observations at these two diagonal actions, **all 64 laws are observationally equivalent**, regardless of how many times those diagonal actions are repeated.

Each new **distinct, noiseless, off-diagonal intervention** reveals at most one free bit. In this construction all 64 truth tables are present, so after `k` such interventions exactly `2^(6-k)` laws remain consistent. Two distinct probes leave 16 laws. To uniquely identify the entire truth table one must observe all six off-diagonal actions noiselessly. With 14% measurement noise, even six single-shot interventions need not suffice.

This result is a bound **for this Boolean-function family and observation setup**. It is not a theorem about every causal model or every Yggdrasil environment.

## Expected downstream intervention value with costs

For all 15 unordered terminal-decision pairs among actions 1–6, compare stopping, one two-sample query, all six fixed probes, random probing, cheapest terminal-action probing, an entropy-per-cost heuristic and exact Bayesian decision-value selection. Interventions are noisy with error `0.14`, cost `0.018 + 0.012×popcount(action)`, while terminal action utility is true outcome less `0.08×popcount(action)`.

| One-probe policy | Exact mean terminal regret plus probe cost ↓ |
| --- | ---: |
| Exact Bayesian expected decision value | **0.1086208** |
| Cheap terminal-action probe | **0.1086208** |
| Best fixed action | 0.2140736 |
| Random action among 1–6 | 0.2200736 |
| No intervention | 0.2380000 |

All 15 terminal pairs have some positive-cost-adjusted probe value. Because the six unobserved truth bits are independent under the *specified uniform prior*, querying an action **outside the offered terminal pair has exactly zero expected terminal-decision information value** and strictly negative net value after paying probe cost. That special independence assumption matters: the conclusion does **not** generalize to structured rule families where probing one action informs other actions.

A cheap terminal-action query ties the more elaborate exact Bayesian probe selector. This is a case where added arbitration complexity has **no demonstrated advantage**.

## Verification and receipt

- Parent accepted baseline `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, not mutated.
- Preregistration committed before result at `570716f08d4297d7db68c342a99aae94e839b47d`.
- Frozen source commit `f582a375500636148e7ec31f43668f3866e94b5f`, SHA-256 `cd3a455caad032f534f1ae04ac190f19e053c1a038b7030ee1067b40099569bb`.
- Original GitHub-hosted [dual-OS analytic run #44284548414](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44284548414) **PASS**, focused 9/9 Linux and 9/9 Windows. Original result bytes matched exactly, SHA-256 `e4e7e689dbcdb21009d927731ee2175ef8c4763408ce34b0c6919fbcca3ab110`.
- Reproduction (Python 3.12+ stdlib): `python -B research/contrib/chatgpt/YNCA-05/experiment.py --run`; unit test: `python -B -m unittest discover -s research/contrib/chatgpt/YNCA-05 -p 'test_*.py' -v`.

## Scientific implication

No adaptive algorithm can infer arbitrary unobserved Boolean truth bits from evidence which cannot distinguish them, regardless of how clever its referee is. Before asking Yggdrasil to discover unknown laws reliably, its **action policy must acquire sufficient discriminating interventions**, and its **world representation must permit the novel relationships to be expressed**. The next development test should focus on *learned representation extension and measured identifiability gain*, not another weighting or threshold tweak.

This result is a rigorous mathematical bound but **does not demonstrate native cumulative learning, autonomous discovery, cold retention or transfer**. Engineering qualification of a contributor research branch never grants owner, science, or deployment authority. Keep this negative/limit proof independent of CKAD, Weight Programming, Wingless, and TTT-Hybrid.
