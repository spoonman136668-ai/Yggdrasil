# CKAD49 — Source discovery of an unlisted state exception and action operator

**Research-only Yggdrasil source learner; accepted native binary API unchanged.** Stacked on the previous negative [CKAD48 draft PR #1316](https://github.com/spoonman136668-ai/Yggdrasil/pull/1316) at commit `5949204f743f113891efe18d0ba81c690151acce`. The original protocol is permanently frozen at `63d9ff3b5cabbe932f70ad5452c86d24cfb74c7f`, **before candidate code or any original DEV scored seed**. This is a first-principles research test, not acceptance, merge, a training restart or a new controller.

## Hypothesis distinct from CKAD48

CKAD48 hard-selected among the *four named* action-effect context partitions: invariant, low bit, high bit, parity, all with XOR transition effects. Both private generating worlds were among its prelisted partitions; hard selection produced identical scoring to an exact Bayesian average, with no scientific improvement over the fully fitted tabular control.

This successor adds **two distinct physical transition operators** (XOR effect and modular-addition effect) and a *source-driven binary partition search*. Four-state partitions include all seven unique two-class partitions and a pooled alternative. One hidden world depends on whether its initial state is **exactly 0** and uses additive (modulo-four) action effects; the other depends on whether its initial state is **exactly 3** and uses XOR effects. Neither singleton partition was in CKAD48's four named partitions, and CKAD48 did not represent modular-addition action physics.

Crucial scientific limitation: the new expanded **16-hypothesis** grammar **does include the true structure**. This tests discovering an initially unknown relation **inside a new finite operator grammar**, NOT inventing arbitrary unanticipated physical laws or intelligent open-world state features. The candidate searches and updates all hypotheses from witnessed outcomes, never receives private feature labels, action mappings, world structure, future outcomes or evaluator counterfactual targets.

Each real source episode is `s0,a1,s1,a2,s2,y`: two genuine publicly witnessed state transitions and one terminal reward. Both action identities and the state space have four values. Each action's true state effect depends on the hidden state class and an independently private action→operator-delta permutation. Transition is correct with probability 0.90 and otherwise yields one of the other three states, probability 0.10/3 each. Reward noise is 0.90/0.10 under two distinct terminal-state laws. All models independently learn exactly the same public source episodes.

The first **80 episodes** use familiar actions 0/1, the next **112** introduce genuinely different physical actuator actions 2/3, and the last **64** return to the familiar actions. The source contains no high-level feature label, no binary alias of new actions and no scripted replay or reset of learned weights.

## Persistent native causal representation and controls

The new research model trains 16 alternative action-conditioned Dirichlet(.25) distributions of **state effect deltas** under each candidate structure, with a fixed 2:1 pooled versus partitioned simplicity prior. Each observed state transition updates both actual source counts and **prequential** posterior structure evidence. All four genuine final-state Bernoulli reward relations are learned separately with Beta(1,1). Before the most-supported source hypothesis reaches frozen posterior mass 0.80, the candidate averages its hypotheses; afterward it selects the learned operator and exception relation. Both action transitions are composed using **one and the same** learned structure, not independently selected unknown structures. All source, posterior weights and reward evidence survive an exact-byte canonical cold restoration.

**Strong independent source-trained comparisons:**
- **Full exact Bayesian structural BMA** over the same 16 hypothesis/Dirichlet banks and same prior, but never hard-selects a winner. It jointly composes two actual intervention effects and fits observed terminal reward probabilities. Strong probabilistic matched-grammar control, not oracle.
- **Unrestricted state–action tabular** four-way next-state Dirichlet(.25) for all 16 state/action conditional cells and state reward Beta(1,1), fully fit on every witnessed source event. No proposed operator prior or pooling advantage; strong conventional alternative outside this grammar.
- **Old CKAD48 restricted XOR class**, independently fitted on only invariant, lowbit, highbit and parity partitions, to measure whether adding an unlisted exception feature and modular addition matters.
- **Uniform 0.5 terminal sham**, an intentionally weak negative only.

Every arm trains on identical observed rows, actual interventions, information and episode budgets. The new structure search uses more computation; **compute efficiency is unqualified and must not be claimed**.

## Frozen independent examiner and negative controls

Before source episodes 80,96,112,128,144,160,176,192,208,224,240, the evaluator scores **all 64 possible two-action combinations** (4 initial states × 4 first actions × 4 second actions) using a private exact two-transition terminal reward expectation. The score is expected Bernoulli Brier `(p−q)^2+q(1−q)`. Evaluator truth is **read-only** and never added as source evidence. Both policies are tested on precisely the same unknown physical combinations, not only convenient on-policy observations.

The engineer-only fixtures (seed 0) must show: no privileged mapping reachability, all source actions and outcomes update exactly once, cold restoration/checkpoint source custody, duplicate idempotence/conflict atomicity, same latent structure across both actions, the new addition operator helps relative to old XOR-only, and **a genuinely arbitrary state-action lookup outside the 16-hypothesis grammar is better learned by the unrestricted tabular model**. Fixture evaluation does not score a registered scientific seed.

Fresh **DEV 49111/49112**, two worlds per seed, 256 genuine source episodes/world and 3 genuinely observed consequences/episode. Pilots **49211/49212** and primaries **49311/49312/49313** are reserved and are **inaccessible** to source-scoring CLI. All prior development seed cohorts are excluded.

Precommitted **both-seed scientific DEV gates:** pooled novel-late + familiar-cold-return expected Brier ≤0.190; gain ≥0.010 over unrestricted fully fitted tabular; gain ≥0.025 over old XOR-only; no worse than full 16-hypothesis BMA by more than 0.004, no early-novel worsening above 0.015 or old-return worsening above 0.008 relative to BMA; true structural feature and operator inferred by the **last scored probe**, full action coverage and original source retained; exact full checkpoint SHA and all phase means agree Ubuntu/Windows. **ANY failure: DEV_NO_GO**, no tuning or replay on original consumed seeds. Even favorable DEV is `DEV_FEASIBLE_NOT_SCIENTIFIC`, not independent SCIENTIFIC_PASS.

## Engineering-first workflow

The GitHub Action has a fixture-only trigger and a separate frozen-development trigger. Fixture-only commits qualify source and negative cases before any registered DEV first use; only a later exact-SHA trigger executes the new cohort once on each operating system. This prevents a fix to broken fixture code from silently consuming scientific data.

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-49 -p test_ckad49.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-49/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-49/screen_dev.py
```

All measured original scientific results, Linux/Windows checkpoint hashes, source/tree provenance, wall and CPU, and frozen negative findings belong in an in-repo evidence receipt. No ChatGPT File Library outputs, scheduled tasks, paid models, new runner or controller, accepted `main` change, Forge integration, merge or deployment. Required-platform full final repository regression and independent owner first-use are separate gates only for a candidate that passes scientific qualification.
