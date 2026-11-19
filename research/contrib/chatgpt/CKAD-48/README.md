# CKAD48 — Learning state-dependent, non-XOR action effects from public interventions

This is **isolated Yggdrasil native-representation research**, stacked on [CKAD47 draft PR #1312](https://github.com/spoonman136668-ai/Yggdrasil/pull/1312) at `a29b6e668fe1435bd9345664d5b9d2db87b46b7a`. It does **not** modify the accepted binary `NativeEpisodeExperience` / `PublicCausalCells` code or reset any official trained weights.

Frozen preregistration `dba16e4e3a1c7f51ea18b45b15da84761de9e5ba` was committed **before implementation** and before any original CKAD48 scored DEV event.

## Why a different causal-representation mechanism

CKAD47 successfully learned four action effects but assumed that an action adds a fixed 2-bit XOR delta *independent of starting state*. Its separate negative fixture proved that a truly state-dependent action can violate that invariance, and its original scientific DEV failed to beat the fully fitted tabular baseline by the required 0.010.

Here the simulated physical action operator is explicitly **state-dependent**: for each action, the latent XOR delta depends on a binary grouping of the *public* starting state. World 0 uses the higher state bit; world 1 uses the XOR parity of both state bits. The two class-specific four-action mappings are hidden bijections with no fixed action preserving the same effect across state classes. The learner never receives the private state partition or the hidden mappings. Its genuine observed source episodes each contain `s0,a1,s1,a2,s2,y`, where both transitions are observed and one terminal reward is observed. Physical transition noise is .9 intended next state and .1/3 for each other next state; terminal outcome noise is .9/.1.

The data schedule is **80 real episodes with actions 0/1, 112 with truly new primitive action IDs 2/3, and 64 with old actions 0/1 again**, per world, with no reset or source replay. Separate new DEV 48111/48112 each contain two independently hidden worlds. All trainable policies see the **same** public action IDs, state transitions and stochastic rewards. No evaluator/private class label, source row from future episodes, counterfactual outcome or hidden true mapping is passed into `observe`.

## Direct native learned representation

One new research-only `NativeStateEffects` model retains four independent candidate **publicly computable** state partitions: invariant, low state bit, high state bit and state parity. Each candidate has four 4-outcome action-delta count banks with Dirichlet(.25) smoothing for observed XOR delta `s XOR s'`. Every real transition updates each partition's source counts and the **prequential Bayesian model evidence** over those four partitions. A shared 4×2 Beta(1,1) terminal outcome bank learns every actual observed reward.

The candidate predicts using evidence-weighted causal partitions, but **hard-selects the most supported structural partition only when source posterior ≥.90**. It then composes two interventions by marginalizing intermediate/final states under one hypothesis, rather than multiplying independently marginalized action-effects or imagining a hidden state. All partitions and past source remain in a single exact cold-restorable checkpoint; no trained knowledge is erased.

This is genuine source-trained **context-dependent action effect** learning, not a binary relabel. The set of possible partitions and four-state group arithmetic are *predeclared structural priors*; this cannot prove discovery of unrestricted state-dependent physical rules.

## Strong independent comparators

- **Exact structure BMA:** A distinct fully trained model maintains exactly the same four candidate structural hypotheses, Dirichlet counts and *all* observed transition likelihood evidence, but performs the full Bayesian model average **without hard selection**. Joint two-action computation shares the same structure identity across both interventions, conditioning on possible intermediate states. It is not an oracle and never knows the true state class.
- **Fully fitted unconstrained tabular:** Dirichlet(.25) next-state distributions for all 16 `(state,action)` cells, plus the same independently source-trained state-reward Beta posterior, composed through two transitions. This conventional control can learn effects outside the candidate's XOR-partition model class.
- **False XOR-invariant:** Same source-trained Dirichlet action delta counts pooled over all states, no state dependence. This is the directly falsified predecessor mechanism.
- **Uniform sham:** 0.5 reward and uniform next-state predictions, negative control only.

The old/invariant and tabular controls use separate trained weights; neither is inferred from the candidate after scoring. All receive equal real actions/information, but the structural candidate and exact BMA use extra processing. **Compute is not matched. No efficiency claim.**

## Independent common examiner and frozen scientific stop

Before observations at episodes `80,96,112,128,144,160,176,192,208,224,240`, the evaluator reads **64 shared two-action state combinations** (4 initial states × 4 first actions × 4 second actions), for every model and hidden world. The private world computes the actual two-transition terminal reward Bernoulli probability; reported expected Brier is `(p-q)^2 + q(1-q)`. These truths **never** train the models and readouts may not mutate source memories.

Two fresh original DEV seeds **48111/48112**, with 2 hidden worlds each. Registered pilots **48211/48212** and primaries **48311/48312/48313** are inaccessible to the DEV runner and remain untouched. Previously consumed CKAD41–47 original cohorts are not scored.

Precommitted **both-seed** DEV acceptance requires pooled late-novel + old-action-return Brier ≤.190, gain ≥.010 over fully trained unconstrained tabular and ≥.025 over the false XOR-invariance control, gap to exact structural Bayes ≤.004, early unseen-worsening ≤.015 and cold-return worsening ≤.008 relative to exact BMA. All four action IDs must be genuinely witnessed, and byte-exact source/cold/duplicate/conflict controls and dual-platform metrics/checkpoint hashes must pass. Any failure is **DEV_NO_GO** and a mandatory research stop. If all pass, this is only **DEV_FEASIBLE_NOT_SCIENTIFIC** until truly disjoint physics, matched compute, independent owner-scoped first-use and full final required-platform regression.

Separate engineer-only negative fixtures test a changing high-state-bit mechanism against the false invariant model. This fixture is **not** a scored scientific cohort and its outcomes cannot be used to tune original DEV thresholds.

## Reproduce safely, development scope only

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-48 -p test_ckad48.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-48/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-48/screen_dev.py
```

GitHub Actions runs the exact qualified source on Ubuntu and Windows only after source-only fixture tests. It preserves complete original numbers, source/checkpoint hashes, time/cost and frozen negative results in this repo, not a chat attachment or Library artifact. No full final repo regression, accepted Yggdrasil native merge, autonomous FORGE/owner training, scheduled task, paid API, independent first-use, deployment or new controller is authorized here.
