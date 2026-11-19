# CKAD47 — Native four-action, four-state compositional causal learning

**Independent development research, not a change to accepted Yggdrasil native API.** Original `NativeEpisodeExperience` and `PublicCausalCells` support only binary intervention IDs, so CKAD46's unfamiliar actuator symbols could be learned only through a binary-alias bridge. CKAD46 [draft PR #1309](https://github.com/spoonman136668-ai/Yggdrasil/pull/1309) was a scientific `DEV_NO_GO` relative to exact balanced mapping. CKAD47 builds a genuinely 4-way *experimental* native causal representation without altering the binary source memory and without silently claiming production integration.

**Pre-code frozen protocol:** commit `b0d71e48848a92d10ed78019d40dffb7af0f505c`, before source code and all science cohorts. Parent is `754e7fd1daf4e99f4949fa649eccd26863622a7b`.

## Hypothesis and real learned state

Each source episode contains actual public `s0,a1,s1,a2,s2,y` with `s0/s1/s2 ∈ {0,1,2,3}`, two action IDs 0..3 and a binary terminal outcome. Each intervention stochastically changes the two-bit state; the outcome noise is fixed **0.9 for the intended XOR transition, 0.1/3 for each other state**; the terminal Bernoulli reward has independent **0.9/0.1** noise. The causal world assigns *all four action IDs* to four **distinct** two-bit XOR effects through a hidden randomly shuffled bijection. World 0 has a parity reward law; World 1 has an OR reward law. The private permutation and reward law never enter trained models.

The new experimental model accumulates a **4×4 action-by-state-delta count bank** with Dirichlet(.25) predictive smoothing. It learns the independent distribution of effect `delta=s XOR s'` from each genuinely observed intervention, rather than mapping every action into two binary equivalents. It also learns genuine terminal outcomes in a separate 4×2 state–reward Beta bank. After authentic source training, a two-action terminal reward prediction is composed by marginalizing possible intermediate and final state transitions under the two separately trained effects and the learned reward-state distribution. Every actual source episode supplies **two observed state transitions and one reward**, updates the model exactly once and preserves raw IDs in an append-only ledger. There is no replay, unobserved counterfactual source, hidden mapping, language-token model or weight reset.

A separate exact cold-restorable checkpoint contains all integer effect counts, terminal reward counts, source receipts and a SHA-256 of the first 96 original episodes. Idempotent duplicates and conflicting source identities fail closed without changing weights.

## Full-fit matched-source comparators

The strongest structural control is an **exact 24-permutation Bayesian posterior** over which action ID produces which XOR delta, using the task's correct fixed 0.9/0.1 transition noise, uniform prior and authentic source transitions. Its two-action readout correctly uses **one shared hidden hypothesis jointly across both actions**, not a weaker product of independent action marginals. The exact control also trains a Beta reward bank from the same real terminal consequences.

The conventional control is fully fitted, unrestricted **state×action → four-way next-state Dirichlet(.25)** counts (16 action/state cells), trained on both transitions and exactly the same Beta reward bank. This is a viable alternative on non-XOR worlds and does not receive privileged causal information. A uniform 0.5-reward sham is shown as a negative, not as the strongest baseline.

Every trainable arm receives precisely the same 240 genuine witnessed source episodes per world and the same actual action IDs, contexts, state transitions, reward outcomes and exogenous source noise. Action 0/1 occur for the first 96 episodes, newly introduced *primitive* effects 2/3 for 96 episodes, and familiar actions return for 48. The candidate learns from these experiences cumulatively, without prior-memory reset. **Known XOR group structure remains a prior:** this is *not* arbitrary unknown nonlinear physical mechanism discovery.

## Independent evaluator and registered DEV stop

Before observations at episodes 96,112,128,144,160,176,192,208,224, read each model against the **same 64 action-independent two-step composition probes** (four initial states × four first actions × four second actions). The evaluator privately computes the true stochastic terminal-reward probability under both transitions and reward noise and reports exact expected Bernoulli Brier. These counterfactual truths are for read-only comparison **only**; they are not source data or a model teaching signal.

Phases: **novel-early** probes 96/112, **novel-late** 144/160/176, **old-action cold return** 192/208/224, and the pooled six late/return probes. Every seed has two different hidden worlds. **DEV 47111 and 47112** may run once per platform for source-qualified reproduction; pilots **47211/47212** and primaries **47311/47312/47313** stay untouched.

Both DEV seeds must simultaneously satisfy: pooled late+return expected Brier ≤0.170; improve by ≥0.010 over the **fully fitted tabular** control; be worse than exact structural Bayes by no more than 0.006; early novel-state/action transfer no more than 0.015 worse than Bayes; return-to-old no more than 0.008 worse than Bayes; exact source, four-action coverage, cold and cross-platform SHA custody. Any failure is `DEV_NO_GO`; do not tune on consumed seeds, score held first-use, merge or promote. Even a favorable DEV is only `DEV_FEASIBLE_NOT_SCIENTIFIC`.

Separate **non-XOR negative control:** a deterministic action whose effect depends on the current state must make the fully fitted tabular model outperform the invariant XOR-based model. This is an explicit representation limitation rather than a science result. No unseen physical mechanics beyond XOR or genuine real-world intelligence is claimed.

## Engineering qualification and boundaries

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-47 -p test_ckad47.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-47/campaign.py --mode preflight
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-47/screen_dev.py
```

The isolated GitHub workflow runs only on its exact source-qualification commit, on Ubuntu and Windows with Python 3.12. Source custody and actual developer-only science scoring run after fixture negative controls. Results, measured CPU/wall/checkpoint bytes and any frozen failure are retained as in-repo evidence. The current experiment creates no new controller, scheduled task, paid API use, authoritative training owner, acceptance ref change, merge, deployment or file-library artifact. Its measured costs do **not** establish matched compute or runtime efficiency. Mandatory full final repository regression remains a separate gate only for a scientifically promotable candidate under verified owner authority.
